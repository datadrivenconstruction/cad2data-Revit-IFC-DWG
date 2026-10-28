# Integrations for the DDC RVT converter

Glue code that makes the 2.0.5 command line easy to use from AI agents, Python, CI and folder pipelines.
The integrations only call the released converter; they do not change it. This folder is MIT licensed
(see `LICENSE`); the converter itself keeps its own license.

| Folder | What | Use it for |
|---|---|---|
| [`python/`](python) | `ddc-converter` package: `convert()`, `read_elements()`, `to_pandas()` | notebooks, scripts, ETL |
| [`mcp/`](mcp) | MCP server: `convert_rvt`, `list_elements`, `summary` | AI assistants and agents |
| [`batch/`](batch) | `ddc_batch.py`: convert or watch a folder, JSON-lines log | file drops, shared drives |
| [`docker/`](docker) | Linux `Dockerfile`, composite GitHub Action, example workflow | CI and servers |

No-code: the existing `DDC_n8n_Workflows&Pipelines` folder covers n8n; the batch script and the Docker
image work as an "execute command" step in other automation tools.

Cloud storage (S3, Google Cloud Storage, Azure Blob, OneDrive / SharePoint / Google Drive links) works as input
and output in the Python package, the MCP server and the batch script. Tests live in `tests/`; the CI workflow is
`.github/workflows/integrations-tests.yml` (Windows and Ubuntu).

Tested on Windows 10/11 x64 (portable package) and Ubuntu 22.04 (Linux x86-64 package) with the 2.0.5 release.
The Docker image and the GitHub Action were written against the same Linux package but not run in Docker.
