"""MCP server exposing the DDC RVT converter CLI to AI assistants (stdio transport).

Tools: convert_rvt(path, formats), list_elements(xlsx, category, limit), summary(path).
Needs the `mcp` package and the ddc-converter package (../python) or PYTHONPATH pointing at its src folder.
"""
from __future__ import annotations

import os
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "python", "src"))

from ddc_converter import ConverterError, convert, read_elements, summarize  # noqa: E402

try:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer as _Server
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server
    from mcp.server.fastmcp.exceptions import ToolError

import functools

mcp = _Server("ddc-rvt-converter")


def readable_errors(fn):
    """Report expected failures to the assistant with their real message instead of a generic crash."""
    @functools.wraps(fn)
    def wrapper(*a, **kw):
        try:
            return fn(*a, **kw)
        except (ConverterError, OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
            raise ToolError(f"{type(e).__name__}: {e}") from e
    return wrapper


@mcp.tool()
@readable_errors
def convert_rvt(path: str, formats: list[str] | None = None, out: str | None = None,
                upload: str | None = None) -> dict:
    """Convert a Revit .rvt/.rfa file. formats: any of glb (always written), xlsx, csv, ifc, gltf, obj,
    sqlite, properties, all. Default xlsx. path may be an s3://, gs://, az:// or https share-link URL
    (downloaded first; then set out). upload: s3://, gs:// or az:// prefix for the results. Returns output folder, written files and the converter status."""
    r = convert(path, formats or ["xlsx"], out, timeout=1800, upload=upload)
    d = r.to_dict()
    t = r.summary.get("totals", {})
    d["active_elements"] = t.get("active_elements")
    d["log_tail"] = r.log[-1500:]
    return d


@mcp.tool()
@readable_errors
def list_elements(xlsx: str, category: str | None = None, limit: int = 50) -> dict:
    """Read the element table (elements.xlsx) written by convert_rvt. category is a case-insensitive
    substring filter (for example Walls). Returns up to limit rows and the number returned."""
    rows = read_elements(xlsx, category, max(1, min(limit, 500)))
    return {"count": len(rows), "elements": rows}


@mcp.tool()
@readable_errors
def summary(path: str) -> dict:
    """Return summary.json (status, element counts, quality notes) for a result folder, a summary.json
    path, or a model path whose <name>.converted folder exists."""
    return summarize(path)


if __name__ == "__main__":
    mcp.run()
