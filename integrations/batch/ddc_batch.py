#!/usr/bin/env python3
"""Convert every .rvt/.rfa in a folder (or watch it) and keep a JSON-lines log.

  python ddc_batch.py IN_DIR OUT_DIR --formats xlsx,gltf,ifc [--recursive] [--watch --interval 10]

Each model goes to OUT_DIR/<name>.converted; models already converted (same size and mtime) are skipped.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "python", "src"))
from ddc_converter import ConverterError, convert, ensure_cli  # noqa: E402


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
        return json.loads(state.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def run_once(a, exe, done: dict, state: Path) -> int:
    fails = 0
    for m in models(Path(a.input), a.recursive):
        st = m.stat()
        key = str(m.resolve())
        sig = [st.st_size, int(st.st_mtime)]
        if done.get(key) == sig:
            continue
        if a.watch and time.time() - st.st_mtime < a.settle:  # file may still be copying
            continue
        rel = m.relative_to(a.input).with_suffix("")
        out = Path(a.output) / (rel.as_posix().replace("/", "__") + ".converted")
        t0 = time.time()
        try:
            r = convert(m, a.formats.split(","), out, cli=exe, timeout=a.timeout)
            log(a.log, event="model_done" if r.ok else "model_failed", input=str(m), output=str(r.output_dir),
                exit_code=r.exit_code, status=r.status, files=sorted(r.files), seconds=round(time.time() - t0, 1))
            ok = r.ok
        except ConverterError as e:
            log(a.log, event="model_failed", input=str(m), error=str(e))
            ok = False
        if ok:
            done[key] = sig
            state.write_text(json.dumps(done), encoding="utf-8")
        else:
            fails += 1
    return fails


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--formats", default="xlsx,gltf", help="comma list: glb,xlsx,csv,ifc,gltf,obj,sqlite,all")
    ap.add_argument("--recursive", action="store_true")
    ap.add_argument("--watch", action="store_true", help="keep running and convert new or changed files")
    ap.add_argument("--interval", type=float, default=10)
    ap.add_argument("--settle", type=float, default=5, help="watch: ignore files modified in the last N seconds")
    ap.add_argument("--timeout", type=float, default=1800)
    ap.add_argument("--cli", help="converter executable (default: DDC_CLI, PATH, or auto-download)")
    ap.add_argument("--log", default=None, help="JSON-lines log (default OUTPUT/ddc_batch.log.jsonl)")
    a = ap.parse_args(argv)
    if not Path(a.input).is_dir():
        ap.error("input must be a folder")
    Path(a.output).mkdir(parents=True, exist_ok=True)
    a.log = a.log or str(Path(a.output) / "ddc_batch.log.jsonl")
    exe = a.cli or ensure_cli()
    state = Path(a.output) / ".ddc_batch_state.json"
    done = load_done(state)
    log(a.log, event="start", input=a.input, formats=a.formats, watch=a.watch)
    try:
        while True:
            fails = run_once(a, exe, done, state)
            if not a.watch:
                log(a.log, event="done", failed=fails)
                return 1 if fails else 0
            time.sleep(a.interval)
    except KeyboardInterrupt:
        log(a.log, event="stopped")
        return 0


if __name__ == "__main__":
    sys.exit(main())
