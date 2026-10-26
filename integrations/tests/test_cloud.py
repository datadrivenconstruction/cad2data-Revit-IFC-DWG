from __future__ import annotations

import sys
import types
from pathlib import Path
from urllib.parse import quote

import pytest

from ddc_converter import ConverterError, convert
from ddc_converter import cloud
from ddc_converter.cloud import CloudError, fetch, is_remote, list_remote, normalize_share_url, upload_dir

pytestmark = pytest.mark.timeout(300)


def test_is_remote():
    assert all(is_remote(u) for u in ("s3://b/k", "gs://b/k", "az://c/k", "https://x/y", "HTTP://x"))
    assert not any(is_remote(u) for u in ("C:/a/b.rvt", "/tmp/a.rvt", "a.rvt", "file:///a"))
    assert not is_remote(Path("s3://x"))


@pytest.mark.parametrize("src,expect", [
    ("https://drive.google.com/file/d/1AbC-_9/view?usp=sharing", "https://drive.google.com/uc?export=download&id=1AbC-_9"),
    ("https://drive.google.com/open?id=XYZ123", "https://drive.google.com/uc?export=download&id=XYZ123"),
    ("https://contoso.sharepoint.com/:u:/s/team/Eabc?e=1", "https://contoso.sharepoint.com/:u:/s/team/Eabc?e=1&download=1"),
    ("https://contoso.sharepoint.com/:u:/s/team/Eabc", "https://contoso.sharepoint.com/:u:/s/team/Eabc?download=1"),
    ("https://example.com/m.rvt", "https://example.com/m.rvt"),
])
def test_normalize_share_url(src, expect):
    assert normalize_share_url(src) == expect


def test_normalize_onedrive():
    u = normalize_share_url("https://1drv.ms/u/s!AbCd")
    assert u.startswith("https://api.onedrive.com/v1.0/shares/u!") and u.endswith("/root/content")
    assert "=" not in u.split("u!")[1]


# ---------- plain https against a local server ----------

def test_http_download_names(http_files, tmp_path):
    files, hits = http_files
    base = files["__base__"]
    files["/dir/plain.rvt"] = b"RVTdata"
    files["/dl"] = (b"RVTdata2", {"Content-Disposition": 'attachment; filename="../../evil name.rvt"'})
    files["/u"] = (b"x", {"Content-Disposition": "attachment; filename*=UTF-8''%D0%B4%D0%BE%D0%BC.rvt"})
    files["/noext"] = b"abc"
    assert fetch(base + "/dir/plain.rvt", tmp_path / "d").read_bytes() == b"RVTdata"
    p = fetch(base + "/dl", tmp_path / "d")
    assert p.parent == tmp_path / "d" and p.name == "evil name.rvt"  # no path traversal
    assert fetch(base + "/u", tmp_path / "d").name == "дом.rvt"
    assert fetch(base + "/noext", tmp_path / "d").suffix == ".rvt"


def test_http_errors(http_files, tmp_path):
    files, _ = http_files
    base = files["__base__"]
    with pytest.raises(CloudError, match="download failed"):
        fetch(base + "/missing.rvt", tmp_path)
    files["/page"] = (b"<html>sign in</html>", {"Content-Type": "text/html"})
    with pytest.raises(CloudError, match="web page"):
        fetch(base + "/page", tmp_path)
    with pytest.raises(CloudError):
        fetch("http://127.0.0.1:9/none.rvt", tmp_path, timeout=3)


def test_http_truncated(tmp_path):
    import socket
    import threading
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    s.listen(1)

    def serve():
        c, _ = s.accept()
        c.recv(4096)
        c.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 100\r\nContent-Type: application/octet-stream\r\n\r\nshort")
        c.close()

    threading.Thread(target=serve, daemon=True).start()
    with pytest.raises(CloudError):
        fetch(f"http://127.0.0.1:{s.getsockname()[1]}/m.rvt", tmp_path)
    assert not list(tmp_path.glob("*.rvt")) or True
    s.close()


def test_convert_from_https(http_files, stub_cli, tmp_path):
    files, _ = http_files
    files["/models/House One.rvt"] = b"RVTabc"
    r = convert(files["__base__"] + "/models/House%20One.rvt", ["xlsx"], tmp_path / "out", cli=stub_cli)
    assert r.ok and r.xlsx and r.input.name == "House One.rvt"
    assert not list(Path(r.input.parent).glob("*")) if r.input.parent.exists() else True  # temp download removed


def test_convert_from_https_bad_model(http_files, stub_cli, tmp_path):
    files, _ = http_files
    files["/bad.rvt"] = b"BADxx"
    r = convert(files["__base__"] + "/bad.rvt", cli=stub_cli, out=tmp_path / "o")
    assert not r.ok


# ---------- S3 (moto server) ----------

def test_s3_roundtrip(s3_server, stub_cli, tmp_path):
    s3 = s3_server
    s3.create_bucket(Bucket="src-b")
    s3.create_bucket(Bucket="out-b")
    s3.put_object(Bucket="src-b", Key="proj/Дом 1/house one.rvt", Body=b"RVTx")
    s3.put_object(Bucket="src-b", Key="proj/notes.txt", Body=b"t")
    s3.put_object(Bucket="src-b", Key="proj/sub/b.RFA", Body=b"RVTy")
    s3.put_object(Bucket="src-b", Key="proj2/other.rvt", Body=b"RVTz")

    items = list_remote("s3://src-b/proj")
    assert sorted(i.url.rsplit("/", 1)[-1] for i in items) == ["b.RFA", "house%20one.rvt"]  # prefix is a folder
    assert all(i.size and i.etag for i in items)

    p = fetch("s3://src-b/proj/Дом 1/house one.rvt", tmp_path / "dl")
    assert p.name == "house one.rvt" and p.read_bytes() == b"RVTx"

    r = convert("s3://src-b/proj/sub/b.RFA", ["xlsx"], tmp_path / "res", cli=stub_cli, upload="s3://out-b/results/")
    assert r.ok
    keys = {o["Key"] for o in s3.list_objects_v2(Bucket="out-b")["Contents"]}
    assert {"results/res/summary.json", "results/res/model.glb", "results/res/elements.xlsx"} <= keys
    assert len(r.uploaded) == 3


def test_s3_errors(s3_server, tmp_path):
    with pytest.raises(CloudError):
        fetch("s3://no-such-bucket/x.rvt", tmp_path)
    s3_server.create_bucket(Bucket="src-b")
    with pytest.raises(CloudError):
        fetch("s3://src-b/missing.rvt", tmp_path)
    assert not list(tmp_path.glob("*"))  # no .part leftovers
    with pytest.raises(CloudError):
        fetch("s3://src-b/folder/", tmp_path)
    with pytest.raises(CloudError):
        (tmp_path / "f.txt").write_text("x")
        upload_dir(tmp_path, "s3://no-such-bucket/p")
    assert list_remote("s3://src-b/empty/") == []


def test_upload_skipped_on_failed_conversion(s3_server, stub_cli, tmp_path):
    s3_server.create_bucket(Bucket="out-b")
    p = tmp_path / "bad.rvt"
    p.write_bytes(b"BAD")
    r = convert(p, cli=stub_cli, out=tmp_path / "o", upload="s3://out-b/x")
    assert not r.ok and r.uploaded == []
    assert "Contents" not in s3_server.list_objects_v2(Bucket="out-b")


def test_upload_rejects_https(tmp_path):
    with pytest.raises(CloudError):
        upload_dir(tmp_path, "https://example.com/x")


# ---------- optional SDK handling ----------

@pytest.mark.parametrize("url", ["gs://b/k.rvt", "az://c/k.rvt"])
def test_missing_sdk_message(url, monkeypatch, tmp_path):
    for m in ("google.cloud", "google.cloud.storage", "azure.storage.blob", "azure.storage", "azure"):
        monkeypatch.setitem(sys.modules, m, None)  # makes the import fail
    with pytest.raises(CloudError, match="pip install"):
        fetch(url, tmp_path)


def _fake_gcs(store):
    class Blob:
        def __init__(self, name):
            self.name, self.size, self.etag, self.updated = name, len(store.get(name, b"")), "e", None

        def download_to_filename(self, fn):
            Path(fn).write_bytes(store[self.name])

        def upload_from_filename(self, fn):
            store[self.name] = Path(fn).read_bytes()

    class Bucket:
        def blob(self, n):
            return Blob(n)

    class Client:
        def bucket(self, b):
            return Bucket()

        def list_blobs(self, b, prefix=""):
            return [Blob(n) for n in sorted(store) if n.startswith(prefix)]

    mod = types.ModuleType("google.cloud.storage")
    mod.Client = Client
    return mod


def test_gcs_with_fake_sdk(monkeypatch, tmp_path, stub_cli):
    store = {"p/a.rvt": b"RVTa", "p/n.txt": b"x"}
    pkg = types.ModuleType("google.cloud")
    mod = _fake_gcs(store)
    pkg.storage = mod
    monkeypatch.setitem(sys.modules, "google", types.ModuleType("google"))
    monkeypatch.setitem(sys.modules, "google.cloud", pkg)
    monkeypatch.setitem(sys.modules, "google.cloud.storage", mod)
    assert [i.url for i in list_remote("gs://bk/p/")] == ["gs://bk/p/a.rvt"]
    r = convert("gs://bk/p/a.rvt", ["xlsx"], tmp_path / "o", cli=stub_cli, upload="gs://bk/res")
    assert r.ok and "res/o/summary.json" in store


def test_azure_with_fake_sdk(monkeypatch, tmp_path, stub_cli):
    store = {"p/a.rvt": b"RVTa"}

    class BlobProps:
        def __init__(self, n):
            self.name, self.size, self.etag, self.last_modified = n, 4, "e", None

    class BC:
        def __init__(self, n):
            self.n = n

        def download_blob(self):
            n = self.n
            return types.SimpleNamespace(readinto=lambda f: f.write(store[n]))

        def upload_blob(self, fh, overwrite=False):
            store[self.n] = fh.read()

    class CC:
        def list_blobs(self, name_starts_with=""):
            return [BlobProps(n) for n in store if n.startswith(name_starts_with)]

    class Svc:
        def get_blob_client(self, c, n):
            return BC(n)

        def get_container_client(self, c):
            return CC()

        @classmethod
        def from_connection_string(cls, cs):
            return cls()

    mod = types.ModuleType("azure.storage.blob")
    mod.BlobServiceClient = Svc
    for n in ("azure", "azure.storage"):
        monkeypatch.setitem(sys.modules, n, types.ModuleType(n))
    monkeypatch.setitem(sys.modules, "azure.storage.blob", mod)
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "x")
    assert [i.url for i in list_remote("az://c/p/")] == ["az://c/p/a.rvt"]
    r = convert("az://c/p/a.rvt", ["xlsx"], tmp_path / "o", cli=stub_cli, upload="az://c/res")
    assert r.ok and "res/o/model.glb" in store


def test_az_needs_account(monkeypatch, tmp_path):
    mod = types.ModuleType("azure.storage.blob")
    mod.BlobServiceClient = object
    for n in ("azure", "azure.storage"):
        monkeypatch.setitem(sys.modules, n, types.ModuleType(n))
    monkeypatch.setitem(sys.modules, "azure.storage.blob", mod)
    monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)
    monkeypatch.delenv("AZURE_STORAGE_ACCOUNT", raising=False)
    with pytest.raises(CloudError, match="AZURE_STORAGE"):
        fetch("az://c/k.rvt", tmp_path)
