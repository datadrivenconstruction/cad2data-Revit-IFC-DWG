# Folder batch mode

```bash
python ddc_batch.py IN_DIR OUT_DIR --formats xlsx,gltf,ifc            # convert once
python ddc_batch.py IN_DIR OUT_DIR --formats xlsx --recursive --watch  # keep watching
```

- Each `.rvt`/`.rfa` goes to `OUT_DIR/<name>.converted` (subfolders become `sub__name.converted`).
- A JSON-lines log is printed and written to `OUT_DIR/ddc_batch.log.jsonl`: events `start`, `model_done`, `model_failed`, `done`.
- Models already converted (same size and modification time) are skipped; state is in `OUT_DIR/.ddc_batch_state.json`. Delete it to force a re-run.
- `--watch` polls every `--interval` seconds and ignores files changed in the last `--settle` seconds, so a file still being copied is not read.
- Exit code 1 if any model failed. Output "written with reported gaps" (converter exit code 2) counts as done.
- CLI lookup and download as in `../python/README.md`; `--cli PATH` overrides.

Formats: `glb` (always), `xlsx`, `csv`, `ifc`, `gltf`, `obj`, `sqlite`, `properties`, `all`.
The converter also has a native `--input-dir DIR --recursive --json-log` mode; this script adds skip-if-done and watching.
