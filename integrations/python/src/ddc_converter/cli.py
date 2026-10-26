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

DEFAULT_VERSION = "2.0.5"
RELEASE_URL = "https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/download/v{v}/{name}"
EXE_NAMES = ("RVTconverter.exe", "RVTconverter", "rvt-decode")
# glb is always written by the converter
FORMAT_FLAGS = {
    "xlsx": "--xlsx", "csv": "--csv", "ifc": "--ifc", "gltf": "--gltf", "obj": "--obj",
    "sqlite": "--sqlite", "properties": "--properties", "all": "--all",
}
OUTPUT_SUFFIXES = (".xlsx", ".glb", ".gltf", ".ifc", ".obj", ".csv", ".sqlite", ".jsonl")


class ConverterError(RuntimeError):
    pass


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


def download_cli(version: str = DEFAULT_VERSION, dest: Path | None = None) -> Path:
    """Download the release package, verify SHA256SUMS.txt, unpack into the cache."""
    name = _asset(version)
    dest = Path(dest) if dest else cache_dir() / version
    tmp = Path(tempfile.mkdtemp(prefix="ddc-dl-"))
    try:
        archive = tmp / name
        urllib.request.urlretrieve(RELEASE_URL.format(v=version, name=name), archive)
        sums = urllib.request.urlopen(RELEASE_URL.format(v=version, name="SHA256SUMS.txt")).read().decode()
        want = next((ln.split()[0] for ln in sums.splitlines() if ln.strip().endswith(name)), None)
        if not want:
            raise ConverterError(f"{name} is not listed in SHA256SUMS.txt")
        h = hashlib.sha256()
        with open(archive, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        if h.hexdigest().lower() != want.lower():
            raise ConverterError(f"checksum mismatch for {name}")
        dest.mkdir(parents=True, exist_ok=True)
        if name.endswith(".zip"):
            with zipfile.ZipFile(archive) as z:
                z.extractall(dest)
        else:
            with tarfile.open(archive) as t:
                if hasattr(tarfile, "data_filter"):
                    t.extractall(dest, filter="data")
                else:
                    t.extractall(dest)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    exe = _find_exe(dest)
    if exe is None:
        raise ConverterError("converter executable not found in the downloaded package")
    if sys.platform != "win32":
        exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
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

    @property
    def ok(self) -> bool:
        return self.exit_code in (0, 2)  # 2 = written with reported gaps

    @property
    def xlsx(self) -> Path | None:
        return self.files.get("xlsx")

    def to_dict(self) -> dict:
        return {"ok": self.ok, "exit_code": self.exit_code, "status": self.status,
                "input": str(self.input), "output_dir": str(self.output_dir),
                "files": {k: str(v) for k, v in self.files.items()}}


def _unique(p: Path) -> Path:
    q, i = p, 1
    while q.exists():
        i += 1
        q = p.with_name(f"{p.name}-{i}")
    return q


def convert(path, formats=("xlsx", "glb"), out=None, cli=None, timeout: float | None = None,
            extra_args=()) -> Result:
    """Convert one .rvt/.rfa into a new folder (default <name>.converted beside the input)."""
    src = Path(path).resolve()
    if not src.is_file():
        raise ConverterError(f"input not found: {src}")
    exe = Path(cli) if cli else ensure_cli()
    out_dir = _unique(Path(out)) if out else _unique(src.with_name(src.stem + ".converted"))
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
    summary = {}
    sj = out_dir / "summary.json"
    if sj.exists():
        summary = json.loads(sj.read_text(encoding="utf-8"))
    files = {}
    if out_dir.exists():
        for f in sorted(out_dir.iterdir()):
            if f.suffix.lower() in OUTPUT_SUFFIXES:
                files.setdefault(f.suffix.lower().lstrip("."), f)
    status = summary.get("status") or ("" if p.returncode in (0, 2) else "FAILED")
    return Result(src, out_dir, p.returncode, status, summary, files, (p.stdout or "") + (p.stderr or ""))


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
