"""Locate, download and run the DDC RVT converter command line."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from .cloud import ConverterError, fetch, is_remote, upload_dir

DEFAULT_VERSION = "2.0.5"
RELEASE_URL = "https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v{v}/{name}"
DOWNLOAD_TIMEOUT = 120
EXE_NAMES = ("RVTconverter.exe", "RVTconverter", "rvt-decode")
# glb is always written by the converter
FORMAT_FLAGS = {
    "xlsx": "--xlsx", "csv": "--csv", "ifc": "--ifc", "gltf": "--gltf", "obj": "--obj",
    "sqlite": "--sqlite", "properties": "--properties", "all": "--all",
}
OUTPUT_SUFFIXES = (".xlsx", ".glb", ".gltf", ".ifc", ".obj", ".csv", ".sqlite", ".jsonl")


def cache_dir() -> Path:
    return Path(os.environ.get("DDC_HOME") or os.path.join(os.path.expanduser("~"), ".ddc-converter"))


def _find_exe(root: Path) -> Path | None:
    if root.is_file():
        return root
    for name in EXE_NAMES:
        for p in sorted(root.rglob(name)):
            if p.is_file():
                return p
    return None


def find_cli(version: str = DEFAULT_VERSION) -> Path | None:
    """DDC_CLI env var (file or folder), then PATH, then the download cache. None when not found."""
    env = os.environ.get("DDC_CLI")
    if env and Path(env).exists():
        return _find_exe(Path(env))
    for name in EXE_NAMES:
        p = shutil.which(name)
        if p:
            return Path(p)
    d = cache_dir() / version
    return _find_exe(d) if d.exists() else None


def _asset(version: str) -> str:
    if sys.platform == "win32":
        return f"DDC-RVT-Converter-{version}-portable.zip"
    if sys.platform.startswith("linux") and platform.machine() in ("x86_64", "AMD64"):
        return f"DDC-RVT-Converter-{version}-linux-x64.tar.gz"
    raise ConverterError("No converter build for this platform (Windows x64 and Linux x86-64 only).")


def _fetch(url: str, timeout: float = DOWNLOAD_TIMEOUT) -> urllib.request.addinfourl:
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ddc-converter"}), timeout=timeout)


def download_cli(version: str = DEFAULT_VERSION, dest: Path | None = None) -> Path:
    """Download the release package, verify SHA256SUMS.txt, unpack into the cache.

    DDC_RELEASE_URL (a template with {v} and {name}) overrides the download location.
    """
    name = _asset(version)
    dest = Path(dest) if dest else cache_dir() / version
    base = os.environ.get("DDC_RELEASE_URL") or RELEASE_URL
    tmp = Path(tempfile.mkdtemp(prefix="ddc-dl-"))
    try:
        archive = tmp / name
        h = hashlib.sha256()
        try:
            with _fetch(base.format(v=version, name=name)) as r, open(archive, "wb") as f:
                for chunk in iter(lambda: r.read(1 << 20), b""):
                    f.write(chunk)
                    h.update(chunk)
            with _fetch(base.format(v=version, name="SHA256SUMS.txt")) as r:
                sums = r.read().decode("utf-8", "replace")
        except OSError as e:
            raise ConverterError(f"download failed: {e}") from e
        want = None
        for ln in sums.splitlines():
            parts = ln.split()
            if len(parts) >= 2 and parts[-1].lstrip("*") == name:
                want = parts[0]
                break
        if not want:
            raise ConverterError(f"{name} is not listed in SHA256SUMS.txt")
        if h.hexdigest().lower() != want.lower():
            raise ConverterError(f"checksum mismatch for {name}")
        stage = tmp / "unpacked"
        stage.mkdir()
        try:
            if name.endswith(".zip"):
                with zipfile.ZipFile(archive) as z:
                    z.extractall(stage)
            else:
                with tarfile.open(archive) as t:
                    if hasattr(tarfile, "data_filter"):
                        t.extractall(stage, filter="data")
                    else:
                        t.extractall(stage)
        except (zipfile.BadZipFile, tarfile.TarError) as e:
            raise ConverterError(f"unreadable package {name}: {e}") from e
        if _find_exe(stage) is None:
            raise ConverterError("converter executable not found in the downloaded package")
        # publish atomically so a failed or concurrent download never leaves a half-unpacked cache
        dest.parent.mkdir(parents=True, exist_ok=True)
        if _find_exe(dest) is None:  # a concurrent download may already have installed a working copy
            if dest.exists():
                shutil.rmtree(dest, ignore_errors=True)
            try:
                os.replace(stage, dest)
            except OSError:
                if _find_exe(dest) is None:
                    raise
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    exe = _find_exe(dest)
    if exe is None:
        raise ConverterError("converter executable not found in the downloaded package")
    if sys.platform != "win32":
        for p in dest.rglob("*"):
            if p.is_file() and p.name in EXE_NAMES:
                p.chmod(p.stat().st_mode | stat.S_IXUSR)
    return exe


def ensure_cli(version: str = DEFAULT_VERSION, download: bool = True) -> Path:
    exe = find_cli(version)
    if exe is None and download:
        exe = download_cli(version)
    if exe is None:
        raise ConverterError("Converter CLI not found. Set DDC_CLI, add it to PATH, or call download_cli().")
    return exe


@dataclass
class Result:
    input: Path
    output_dir: Path
    exit_code: int
    status: str
    summary: dict = field(default_factory=dict)
    files: dict = field(default_factory=dict)
    log: str = ""
    uploaded: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.exit_code in (0, 2)  # 2 = written with reported gaps

    @property
    def xlsx(self) -> Path | None:
        return self.files.get("xlsx")

    def to_dict(self) -> dict:
        return {"ok": self.ok, "exit_code": self.exit_code, "status": self.status,
                "input": str(self.input), "output_dir": str(self.output_dir),
                "files": {k: str(v) for k, v in self.files.items()}, "uploaded": list(self.uploaded)}


def _unique(p: Path) -> Path:
    q, i = p, 1
    while q.exists():
        i += 1
        q = p.with_name(f"{p.name}-{i}")
    return q


def convert(path, formats=("xlsx", "glb"), out=None, cli=None, timeout: float | None = None,
            extra_args=(), upload: str | None = None) -> Result:
    """Convert one .rvt/.rfa into a new folder (default <name>.converted beside the input).

    path may be an s3://, gs://, az:// or https:// URL (including OneDrive, SharePoint and Google Drive
    share links); it is downloaded to a temp folder and the result goes to ./<name>.converted unless out
    is given. upload: s3://, gs:// or az:// prefix that receives the output folder.
    """
    if is_remote(str(path)):
        tmp = Path(tempfile.mkdtemp(prefix="ddc-src-"))
        try:
            local = fetch(str(path), tmp)
            dest = out if out else Path.cwd() / (local.stem + ".converted")
            return convert(local, formats, dest, cli, timeout, extra_args, upload)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    src = Path(path).resolve()
    if not src.is_file():
        raise ConverterError(f"input not found: {src}")
    exe = Path(cli) if cli else ensure_cli()
    out_dir = _unique(Path(out).resolve()) if out else _unique(src.with_name(src.stem + ".converted"))
    args = [str(exe), str(src), "--out", str(out_dir)]
    for f in formats:
        f = f.strip().lower().lstrip(".")
        if f == "glb" or not f:
            continue
        if f not in FORMAT_FLAGS:
            raise ConverterError(f"unknown format {f!r}; use glb, {', '.join(FORMAT_FLAGS)}")
        args.append(FORMAT_FLAGS[f])
    args += list(extra_args)
    try:
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise ConverterError(f"conversion timed out after {timeout}s") from e
    except OSError as e:
        raise ConverterError(f"cannot run converter {exe}: {e}") from e
    summary = {}
    sj = out_dir / "summary.json"
    if sj.exists():
        try:
            summary = json.loads(sj.read_text(encoding="utf-8"))
        except ValueError:
            summary = {}
    files = {}
    if out_dir.exists():
        for f in sorted(out_dir.iterdir()):
            if f.suffix.lower() in OUTPUT_SUFFIXES:
                files.setdefault(f.suffix.lower().lstrip("."), f)
    status = summary.get("status") or ("" if p.returncode in (0, 2) else "FAILED")
    res = Result(src, out_dir, p.returncode, status, summary, files, (p.stdout or "") + (p.stderr or ""))
    if upload and res.ok:
        target = upload.rstrip("/") + "/" + out_dir.name
        res.uploaded = upload_dir(out_dir, target)
    return res


def read_elements(xlsx, category: str | None = None, limit: int | None = None) -> list[dict]:
    """Element table rows as dicts; category is a case-insensitive substring filter."""
    from .xlsx import read_xlsx
    header, rows = read_xlsx(xlsx, "Elements")
    ci = header.index("Category") if "Category" in header else None
    out = []
    for r in rows:
        if category and (ci is None or category.lower() not in str(r[ci] or "").lower()):
            continue
        out.append({h: v for h, v in zip(header, r) if v is not None})
        if limit and len(out) >= limit:
            break
    return out


def to_pandas(source, category: str | None = None):
    """DataFrame of the element table. source: .xlsx path or a Result."""
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError("to_pandas needs pandas: pip install ddc-converter[pandas]") from e
    x = source.xlsx if isinstance(source, Result) else source
    if x is None:
        raise ConverterError("no xlsx in result; convert with formats=('xlsx',)")
    df = pd.read_excel(x, sheet_name="Elements")
    if category:
        df = df[df["Category"].astype(str).str.contains(category, case=False, na=False)]
    return df


def summarize(path) -> dict:
    """summary.json of a result folder, of a model's <name>.converted folder, or the file itself."""
    p = Path(path)
    if p.is_file() and p.name != "summary.json":
        p = p.with_name(p.stem + ".converted")
    sj = p if p.name == "summary.json" else p / "summary.json"
    if not sj.exists():
        raise ConverterError(f"summary.json not found in {p}")
    return json.loads(sj.read_text(encoding="utf-8"))
