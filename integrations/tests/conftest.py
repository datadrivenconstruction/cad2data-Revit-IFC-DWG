"""Shared fixtures. Real-model tests need DDC_CLI (converter) and DDC_TEST_MODELS (folder with house.rvt,
KeyWest.rvt, found by name anywhere below it); they skip when those are missing."""
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "python" / "src"))
sys.path.insert(0, str(ROOT / "batch"))

STUB = r'''
import os, sys, time, json, pathlib
a = sys.argv[1:]
src = pathlib.Path(a[0]); out = pathlib.Path(a[a.index("--out") + 1])
time.sleep(float(os.environ.get("STUB_SLEEP", "0")))
if src.read_bytes()[:3] == b"BAD":
    sys.stderr.write("cannot read model\n"); sys.exit(1)
out.mkdir(parents=True, exist_ok=True)
(out / "summary.json").write_text(json.dumps({"status": "OK", "totals": {"active_elements": 3}}))
(out / "model.glb").write_bytes(b"glb")
if "--xlsx" in a: (out / "elements.xlsx").write_bytes(b"x")
print("ok")
'''


def _find(root: Path, name: str):
    for p in root.rglob(name):
        return p
    return None


@pytest.fixture(scope="session")
def real_cli():
    cli = os.environ.get("DDC_CLI")
    if not cli or not Path(cli).exists():
        pytest.skip("DDC_CLI not set")
    return cli


@pytest.fixture(scope="session")
def models_dir():
    d = os.environ.get("DDC_TEST_MODELS")
    if not d or not Path(d).is_dir():
        pytest.skip("DDC_TEST_MODELS not set")
    return Path(d)


@pytest.fixture(scope="session")
def keywest(models_dir):
    p = _find(models_dir, "KeyWest.rvt")
    if not p:
        pytest.skip("KeyWest.rvt not found")
    return p


@pytest.fixture(scope="session")
def house(models_dir):
    p = _find(models_dir, "house.rvt")
    if not p:
        pytest.skip("house.rvt not found")
    return p


@pytest.fixture(scope="session")
def converted_keywest(real_cli, keywest, tmp_path_factory):
    from ddc_converter import convert
    out = tmp_path_factory.mktemp("kw") / "kw.converted"
    return convert(keywest, ["xlsx"], out, cli=real_cli, timeout=600)


@pytest.fixture
def stub_cli(tmp_path):
    """A fake converter: writes summary.json/model.glb (+elements.xlsx); fails on files starting with BAD."""
    d = tmp_path / "stubbin"
    d.mkdir()
    (d / "stub.py").write_text(STUB, encoding="utf-8")
    if os.name == "nt":
        exe = d / "RVTconverter.cmd"
        exe.write_text(f'@"{sys.executable}" "%~dp0stub.py" %*\r\n')
    else:
        exe = d / "RVTconverter"
        exe.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{d}/stub.py" "$@"\n')
        exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
    return str(exe)


@pytest.fixture
def stub_models(tmp_path):
    d = tmp_path / "in"
    d.mkdir()
    for n in ("a", "b", "c"):
        (d / f"{n}.rvt").write_bytes(b"RVT" + n.encode() * 50)
    return d


@pytest.fixture
def s3_server(monkeypatch):
    """Local S3 API (moto server) with AWS_ENDPOINT_URL pointing at it."""
    pytest.importorskip("boto3")
    moto_server = pytest.importorskip("moto.server")
    import socket
    with socket.socket() as so:
        so.bind(("127.0.0.1", 0))
        port = so.getsockname()[1]
    srv = moto_server.ThreadedMotoServer(ip_address="127.0.0.1", port=port)
    srv.start()
    host, port = srv.get_host_and_port()
    monkeypatch.setenv("AWS_ENDPOINT_URL", f"http://{host}:{port}")
    for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(k, "test")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    import urllib.request
    urllib.request.urlopen(urllib.request.Request(f"http://{host}:{port}/moto-api/reset", method="POST"))  # moto state is process-global
    import boto3
    c = boto3.client("s3")
    yield c
    srv.stop()


@pytest.fixture
def http_files(tmp_path):
    """Serve a dict {path: bytes | (bytes, headers)} over a local http.server; yields (base_url, hits)."""
    import http.server
    import threading

    files: dict = {}
    hits: list = []

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            hits.append(self.path)
            from urllib.parse import unquote
            v = files.get(unquote(self.path.split("?")[0]))
            if v is None:
                self.send_error(404)
                return
            body, hdr = v if isinstance(v, tuple) else (v, {})
            self.send_response(200)
            hdr = {"Content-Type": "application/octet-stream", "Content-Length": str(len(body)), **hdr}
            for k, val in hdr.items():
                self.send_header(k, val)
            self.end_headers()
            try:
                self.wfile.write(body)
            except OSError:
                pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    files["__base__"] = f"http://127.0.0.1:{srv.server_address[1]}"
    yield files, hits
    srv.shutdown()


@pytest.fixture(autouse=True)
def _isolate_home(tmp_path, monkeypatch):
    monkeypatch.setenv("DDC_HOME", str(tmp_path / "ddc-home"))
    monkeypatch.delenv("DDC_RELEASE_URL", raising=False)
    # keep the real CLI reachable for tests that ask for it, but stop stray PATH/env pickup otherwise
    monkeypatch.delenv("DDC_CLI", raising=False)
    real = os.environ.get("_DDC_CLI_REAL")
    if real:
        monkeypatch.setenv("DDC_CLI", real)


def pytest_configure(config):
    # remember the user's DDC_CLI before the autouse fixture clears it
    if os.environ.get("DDC_CLI"):
        os.environ["_DDC_CLI_REAL"] = os.environ["DDC_CLI"]


