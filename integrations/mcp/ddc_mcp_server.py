"""MCP server exposing the DDC RVT converter CLI to AI assistants (stdio transport).

Tools: convert_rvt(path, formats), list_elements(xlsx, category, limit), summary(path).
Needs the `mcp` package and the ddc-converter package (../python) or PYTHONPATH pointing at its src folder.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "python", "src"))

from ddc_converter import convert, read_elements, summarize  # noqa: E402

try:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

mcp = _Server("ddc-rvt-converter")


@mcp.tool()
def convert_rvt(path: str, formats: list[str] | None = None, out: str | None = None) -> dict:
    """Convert a Revit .rvt/.rfa file. formats: any of glb (always written), xlsx, csv, ifc, gltf, obj,
    sqlite, properties, all. Default xlsx. Returns output folder, written files and the converter status."""
    r = convert(path, formats or ["xlsx"], out, timeout=1800)
    d = r.to_dict()
    t = r.summary.get("totals", {})
    d["active_elements"] = t.get("active_elements")
    d["log_tail"] = r.log[-1500:]
    return d


@mcp.tool()
def list_elements(xlsx: str, category: str | None = None, limit: int = 50) -> dict:
    """Read the element table (elements.xlsx) written by convert_rvt. category is a case-insensitive
    substring filter (for example Walls). Returns up to limit rows and the number returned."""
    rows = read_elements(xlsx, category, max(1, min(limit, 500)))
    return {"count": len(rows), "elements": rows}


@mcp.tool()
def summary(path: str) -> dict:
    """Return summary.json (status, element counts, quality notes) for a result folder, a summary.json
    path, or a model path whose <name>.converted folder exists."""
    return summarize(path)


if __name__ == "__main__":
    mcp.run()
