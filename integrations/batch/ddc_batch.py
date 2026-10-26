#!/usr/bin/env python3
"""Convert every .rvt/.rfa in a folder or cloud location (or watch it) and keep a JSON-lines log.

  python ddc_batch.py IN OUT_DIR --formats xlsx,gltf,ifc [--recursive] [--watch --interval 10] [--jobs 4]
                      [--upload s3://bucket/results/]

IN is a folder, an s3://, gs:// or az:// prefix, or a OneDrive / SharePoint / Google Drive share link.
Each model goes to OUT_DIR/<name>.converted; models already converted (same size and mtime) are skipped.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "python", "src"))
from ddc_converter import ConverterError, convert, ensure_cli  # noqa: E402
from ddc_converter.cloud import fetch, is_remote, list_remote, upload_dir  # noqa: E402


def models(root: Path, recursive: bool):
    it = root.rglob("*") if recursive else root.glob("*")
    return sorted(p for p in it if p.is_file() and p.suffix.lower() in (".rvt", ".rfa"))


def log(fp, **kw):
    kw["time"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    line = json.dumps(kw, ensure_ascii=False)
    print(line, flush=True)
    if fp:
        with open(fp, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def load_done(state: Path) -> dict:
    try:
        d = json.loads(state.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save_done(state: Path, done: dict) -> None:
    tmp = state.with_name(f"{state.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(done), encoding="utf-8")
    os.replace(tmp, state)  # atomic: a crash never leaves a truncated state file


class Lock:
    """One batch instance per output folder (OS file lock, released automatically when the process dies)."""

    def __init__(self, path: Path):
        self.path, self.fh = path, None

    def acquire(self) -> bool:
        self.fh = open(self.path, "a+b")
        try:
            if os.name == "nt":
                import msvcrt
                self.fh.seek(0)
                msvcrt.locking(self.fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.fh.close()
            self.fh = None
            return False
        return True

    def release(self) -> None:
        if self.fh:
            self.fh.close()
            self.fh = None


def _out_name(rel: Path) -> str:
    return rel.as_posix().replace("/", "__") + ".converted"


def sync_remote(a, staging: Path, seen: dict) -> int:
    """Download new or changed remote models into the staging folder. Returns the number of failures."""
    try:
        items = list_remote(a.input)
    except ConverterError as e:
        log(a.log, event="source_failed", input=a.input, error=str(e))
        return 1
    fails = 0
    for r in items:
        sig = [r.size, r.etag, r.mtime]
        if seen.get(r.url) == sig:
            continue
        try:
            local = fetch(r.url, staging, rel_to=a.input if r.size is not None else None)
        except ConverterError as e:
            log(a.log, event="download_failed", input=r.url, error=str(e))
            fails += 1
            continue
        t = r.mtime or (time.time() - 3600)
        os.utime(local, (t, t))  # stable mtime so change detection and --settle work on the staged copy
        seen[r.url] = sig
        log(a.log, event="downloaded", input=r.url, bytes=local.stat().st_size)
    return fails


def out_names(root: Path, files) -> dict:
    """Output folder name per model. Nested files flatten to a__b.converted; a hash is added on a clash."""
    flat = {m: _out_name(m.relative_to(root).with_suffix("")) for m in files}
    seen: dict = {}
    for n in flat.values():
        seen[n] = seen.get(n, 0) + 1
    for m, n in list(flat.items()):
        if seen[n] > 1 and len(m.relative_to(root).parts) > 1:
            h = hashlib.sha1(m.relative_to(root).as_posix().encode("utf-8")).hexdigest()[:6]
            flat[m] = n[: -len(".converted")] + f"~{h}.converted"
    return flat


def convert_one(a, exe, m: Path, root: Path, key: str, sig: list, name: str):
    out = Path(a.output) / name
    work = out.with_name(f".{out.name}.{os.getpid()}.work")
    shutil.rmtree(work, ignore_errors=True)
    t0 = time.time()
    try:
        r = convert(m, a.formats.split(","), work, cli=exe, timeout=a.timeout)
        ok = r.ok
        if ok:  # swap in the finished folder only after success, so a re-conversion never leaves -2 copies
            old = out.with_name(f".{out.name}.{os.getpid()}.old")
            if out.exists():
                os.replace(out, old)
            os.replace(r.output_dir, out)
            shutil.rmtree(old, ignore_errors=True)
            r.output_dir = out
            r.files = {k: out / v.name for k, v in r.files.items()}
            if a.upload:
                r.uploaded = upload_dir(out, a.upload.rstrip("/") + "/" + out.name)
        log(a.log, event="model_done" if ok else "model_failed", input=str(m), output=str(r.output_dir),
            exit_code=r.exit_code, status=r.status, files=sorted(v.name for v in r.files.values()),
            uploaded=len(r.uploaded), seconds=round(time.time() - t0, 1))
    except ConverterError as e:
        log(a.log, event="model_failed", input=str(m), error=str(e))
        ok = False
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return key, sig, ok


def run_once(a, exe, done: dict, state: Path, failed: dict, root: Path) -> int:
    todo = []
    files = models(root, a.recursive)
    names = out_names(root, files)
    for m in files:
        try:
            st = m.stat()
        except OSError:
            continue
        key = str(m.resolve())
        sig = [st.st_size, int(st.st_mtime)]
        if done.get(key) == sig or failed.get(key) == sig:  # failed files retry only after they change
            continue
        if a.watch and time.time() - st.st_mtime < a.settle:  # file may still be copying
            continue
        todo.append((m, key, sig, names[m]))
    fails = 0
    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        for key, sig, ok in ex.map(lambda t: convert_one(a, exe, t[0], root, t[1], t[2], t[3]), todo):
            if ok:
                done[key] = sig
                failed.pop(key, None)
                save_done(state, done)
            else:
                failed[key] = sig
                fails += 1
    return fails


def main(argv=None) -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="folder, s3://bucket/prefix/, gs://..., az://container/prefix/, or a share link")
    ap.add_argument("output")
    ap.add_argument("--formats", default="xlsx,gltf", help="comma list: glb,xlsx,csv,ifc,gltf,obj,sqlite,all")
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--watch", action="store_true", help="keep running and convert new or changed files")
    ap.add_argument("--interval", type=float, default=10)
    ap.add_argument("--settle", type=float, default=5, help="watch: ignore files modified in the last N seconds")
    ap.add_argument("--timeout", type=float, default=1800)
    ap.add_argument("--jobs", type=int, default=1, help="models converted in parallel")
    ap.add_argument("--upload", help="s3://, gs:// or az:// prefix that receives each <name>.converted folder")
    ap.add_argument("--cli", help="converter executable (default: DDC_CLI, PATH, or auto-download)")
    ap.add_argument("--log", default=None, help="JSON-lines log (default OUTPUT/ddc_batch.log.jsonl)")
    a = ap.parse_args(argv)
    remote = is_remote(a.input)
    if not remote and not Path(a.input).is_dir():
        ap.error("input must be a folder or a cloud URL")
    Path(a.output).mkdir(parents=True, exist_ok=True)
    a.log = a.log or str(Path(a.output) / "ddc_batch.log.jsonl")
    lock = Lock(Path(a.output) / ".ddc_batch.lock")
    if not lock.acquire():
        print(f"error: another ddc_batch already uses {a.output}", file=sys.stderr)
        return 3
    try:
        try:
            exe = a.cli or ensure_cli()
        except ConverterError as e:
            print(f"error: {e}", file=sys.stderr)
            return 4
        state = Path(a.output) / ".ddc_batch_state.json"
        done = load_done(state)
        seen: dict = {}
        failed: dict = {}
        root = Path(a.input)
        if remote:
            root = Path(a.output) / ".ddc_staging" / hashlib.sha1(a.input.encode()).hexdigest()[:12]
            root.mkdir(parents=True, exist_ok=True)
            a.recursive = True
        log(a.log, event="start", input=a.input, formats=a.formats, watch=a.watch)
        try:
            while True:
                fails = sync_remote(a, root, seen) if remote else 0
                fails += run_once(a, exe, done, state, failed, root)
                if not a.watch:
                    log(a.log, event="done", failed=fails)
                    return 1 if fails else 0
                time.sleep(a.interval)
        except KeyboardInterrupt:
            log(a.log, event="stopped")
            return 0
    finally:
        lock.release()


if __name__ == "__main__":
    sys.exit(main())
