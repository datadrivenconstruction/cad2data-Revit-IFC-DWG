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

## Cloud sources

`convert()` and `ddc-convert` accept a URL instead of a path: `s3://bucket/key.rvt`, `gs://bucket/key.rvt`,
`az://container/blob.rvt`, or an `https://` link, including OneDrive, SharePoint and Google Drive share links
(rewritten to direct-download URLs; the link must be readable without signing in). The model is downloaded to a
temp folder that is removed afterwards; output goes to `-o` or `./<name>.converted`.
`--upload s3://bucket/results/` (or `upload=` in Python) copies the output folder there after a successful conversion.

```
pip install "ddc-converter[s3]"      # boto3, Apache-2.0
pip install "ddc-converter[gcs]"     # google-cloud-storage, Apache-2.0
pip install "ddc-converter[azure]"   # azure-storage-blob, MIT
```
Credentials come from each SDK's normal chain (environment, profile, `AWS_ENDPOINT_URL` for S3-compatible stores).
Azure reads `AZURE_STORAGE_CONNECTION_STRING`, or `AZURE_STORAGE_ACCOUNT` with `AZURE_STORAGE_KEY` / `AZURE_STORAGE_SAS_TOKEN`.
Share links need no SDK. `DDC_RELEASE_URL` (template with `{v}` and `{name}`) points the converter download at a mirror.

## Tests

`pip install -e "integrations/python[test]"`, then `python -m pytest` in `integrations/`. Set `DDC_CLI` (converter)
and `DDC_TEST_MODELS` (folder containing `house.rvt` and `KeyWest.rvt`) to include the real-model tests;
without them those tests skip. S3 is tested against a local moto server, share links against a local HTTP server.
