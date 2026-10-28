# Docker and CI (Linux)

## Image

```bash
docker build -t ddc-rvt-converter integrations/docker
docker run --rm -v "$PWD:/data" ddc-rvt-converter /data/House.rvt --xlsx --gltf --out /data/out
docker run --rm -v "$PWD:/data" ddc-rvt-converter --input-dir /data/models --recursive --out /data/out --xlsx --json-log
```
The build downloads the Linux x86-64 release package (glibc 2.35+, so Ubuntu 22.04 or newer) and checks it against the release `SHA256SUMS.txt`.
`--build-arg DDC_VERSION=2.0.6` selects the release. `--out` must name a folder that does not exist yet.

## GitHub Action

`action.yml` is a composite action; `convert-rvt.yml` is a ready workflow (copy it to `.github/workflows/`):

```yaml
- uses: datadrivenconstruction/cad2data-Revit-IFC-DWG/integrations/docker@main
  with:
    input: models            # folder with .rvt/.rfa
    output: converted        # new folder, one <model>.converted per model
    formats: "--xlsx --gltf --ifc"
    version: "2.0.6"
- uses: actions/upload-artifact@v4
  with: { name: converted, path: converted }
```
The step fails only on real errors; converter exit code 2 (written with reported gaps) passes. A per-model JSON-lines log is saved as `<output>.ndjson`.

Status: the Linux package and the exact command lines were run on Ubuntu 22.04 (WSL); the Dockerfile and the Action have not been executed (no Docker on the test machine).
