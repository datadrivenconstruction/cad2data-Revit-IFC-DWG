# ddc-converter (Python)

Pure-Python wrapper around the DDC RVT converter command line. No required dependencies.

```bash
pip install ./integrations/python            # from a checkout; add [pandas] for to_pandas()
```

```python
import ddc_converter as ddc

r = ddc.convert("House.rvt", formats=["xlsx", "gltf", "ifc"])   # glb is always written
print(r.ok, r.status, r.output_dir, r.files)                     # exit code 2 = written with reported gaps

rows = ddc.read_elements(r.xlsx, category="Walls", limit=100)   # list of dicts, stdlib only
df = ddc.to_pandas(r, category="Walls")                          # needs pandas + openpyxl
```

Finding the CLI, in order: `DDC_CLI` (file or folder), `RVTconverter` / `rvt-decode` on `PATH`,
`~/.ddc-converter/<version>/` (override with `DDC_HOME`). If none is found, `convert()` downloads the 2.0.5
release package for your platform from GitHub and verifies it against the release `SHA256SUMS.txt`.
Call `ddc.download_cli()` to do it explicitly, or `ddc-convert --download` from a shell.

CLI: `ddc-convert House.rvt -f xlsx,ifc -o out_dir` prints the result as JSON.

Formats: `glb` (always), `xlsx`, `csv`, `ifc`, `gltf`, `obj`, `sqlite`, `properties`, `all`.
Output goes to a new folder (`<name>.converted` beside the input by default; `-2`, `-3` ... if it exists).
Not published to PyPI.
