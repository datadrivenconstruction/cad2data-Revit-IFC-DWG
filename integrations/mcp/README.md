# DDC RVT converter MCP server

Lets an AI assistant convert Revit files and query the element table. stdio transport.

Tools
- `convert_rvt(path, formats, out)` - formats: `xlsx` (default), `csv`, `ifc`, `gltf`, `obj`, `sqlite`, `properties`, `all` (GLB is always written). Returns the output folder, files, status, element count.
- `list_elements(xlsx, category, limit)` - rows of `elements.xlsx`, filtered by category substring (for example `Walls`).
- `summary(path)` - `summary.json` for a result folder or a model that was already converted.

## Install

```bash
pip install mcp                    # official MCP SDK (MIT), Python 3.10+
```
The server imports the sibling `../python/src` package, so run it from a checkout. It finds the converter
as described in `../python/README.md` (set `DDC_CLI`, or let it download the release package on first use).

## Assistant configuration

Add to the assistant MCP settings (for example `claude_desktop_config.json` or `.mcp.json`):

```json
{
  "mcpServers": {
    "ddc-rvt-converter": {
      "command": "python",
      "args": ["/path/to/cad2data-Revit-IFC-DWG/integrations/mcp/ddc_mcp_server.py"],
      "env": { "DDC_CLI": "/path/to/RVTconverter.exe" }
    }
  }
}
```
`env` is optional. Then ask: "Convert C:\models\House.rvt to xlsx and list the first 20 walls."

`convert_rvt` also takes an `s3://`, `gs://`, `az://` or share-link `path` (set `out` to choose where the result goes)
and an optional `upload` prefix; see `../python/README.md` for the SDK extras and credentials.
Tests start the server over stdio with the real MCP client: `python -m pytest tests/test_mcp.py` in `integrations/`.
