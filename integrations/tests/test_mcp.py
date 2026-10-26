from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("mcp")
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

SERVER = str(Path(__file__).resolve().parent.parent / "mcp" / "ddc_mcp_server.py")
pytestmark = pytest.mark.timeout(900)


def run_session(cli, fn):
    async def go():
        params = StdioServerParameters(command=sys.executable, args=[SERVER],
                                       env={**os.environ, "DDC_CLI": str(cli)})
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                return await fn(s)
    return asyncio.run(go())


def schema(t):
    return getattr(t, "input_schema", None) or t.inputSchema


def is_err(res):
    return bool(getattr(res, "is_error", getattr(res, "isError", False)))


def payload(res):
    sc = getattr(res, "structured_content", None) or getattr(res, "structuredContent", None)
    if sc:
        return sc.get("result", sc) if isinstance(sc, dict) else sc
    return json.loads(res.content[0].text)


def test_tool_schemas(stub_cli):
    async def fn(s):
        return (await s.list_tools()).tools

    tools = {t.name: t for t in run_session(stub_cli, fn)}
    assert set(tools) == {"convert_rvt", "list_elements", "summary"}
    c = schema(tools["convert_rvt"])
    assert c["type"] == "object" and c["required"] == ["path"]
    assert set(c["properties"]) == {"path", "formats", "out", "upload"}
    assert c["properties"]["path"]["type"] == "string"
    fmts = c["properties"]["formats"]
    assert "array" in json.dumps(fmts)
    le = schema(tools["list_elements"])
    assert le["required"] == ["xlsx"] and le["properties"]["limit"]["type"] == "integer"
    assert schema(tools["summary"])["required"] == ["path"]
    assert all(t.description for t in tools.values())


def test_convert_error_is_tool_error(stub_cli, tmp_path):
    async def fn(s):
        return await s.call_tool("convert_rvt", {"path": str(tmp_path / "missing.rvt")})

    res = run_session(stub_cli, fn)
    assert is_err(res) and "not found" in res.content[0].text


def test_invalid_arguments_rejected(stub_cli):
    async def fn(s):
        try:
            return await s.call_tool("convert_rvt", {"formats": ["xlsx"]})
        except Exception as e:  # noqa: BLE001
            return e

    res = run_session(stub_cli, fn)
    assert isinstance(res, Exception) or is_err(res)


def test_stub_convert_and_summary(stub_cli, stub_models, tmp_path):
    out = tmp_path / "o"

    async def fn(s):
        a = await s.call_tool("convert_rvt", {"path": str(stub_models / "a.rvt"), "out": str(out)})
        b = await s.call_tool("summary", {"path": str(out)})
        c = await s.call_tool("summary", {"path": str(tmp_path / "nothing")})
        return a, b, c

    a, b, c = run_session(stub_cli, fn)
    assert not is_err(a) and payload(a)["ok"] is True and payload(a)["active_elements"] == 3
    assert payload(b)["status"] == "OK"
    assert is_err(c)


def test_list_elements_limit_clamped_and_missing(stub_cli, tmp_path):
    async def fn(s):
        return await s.call_tool("list_elements", {"xlsx": str(tmp_path / "no.xlsx")})

    assert is_err(run_session(stub_cli, fn))


def test_real_model_through_stdio(real_cli, keywest, tmp_path):
    out = tmp_path / "kw"

    async def fn(s):
        a = await s.call_tool("convert_rvt", {"path": str(keywest), "formats": ["xlsx"], "out": str(out)})
        x = payload(a)["files"]["xlsx"]
        b = await s.call_tool("list_elements", {"xlsx": x, "limit": 3})
        c = await s.call_tool("summary", {"path": str(out)})
        return a, b, c

    a, b, c = run_session(real_cli, fn)
    assert not is_err(a) and payload(a)["ok"]
    rows = payload(b)
    assert 0 < rows["count"] <= 3
    assert payload(c)["status"]
