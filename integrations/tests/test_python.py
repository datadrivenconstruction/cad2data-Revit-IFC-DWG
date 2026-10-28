from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import threading
import zipfile
from pathlib import Path

import pytest

import ddc_converter
from ddc_converter import ConverterError, convert, download_cli, find_cli, read_elements, summarize
from ddc_converter import cli as cli_mod

pytestmark = pytest.mark.timeout(900)


# ---------- real converter on real models ----------

def test_keywest_xlsx(converted_keywest):
    r = converted_keywest
    assert r.ok and r.exit_code in (0, 2)
    assert r.status
    assert r.xlsx and r.xlsx.is_file() and "glb" in r.files
    assert (r.output_dir / "summary.json").is_file()
    assert r.to_dict()["ok"] is True


def test_keywest_read_elements_and_summary(converted_keywest):
    rows = read_elements(converted_keywest.xlsx, limit=5)
    assert 0 < len(rows) <= 5
    assert read_elements(converted_keywest.xlsx, "zzz-no-such-category") == []
    s = summarize(converted_keywest.output_dir)
    assert s.get("status") == converted_keywest.status


def test_house_converts(real_cli, house, tmp_path):
    r = convert(house, ["xlsx"], tmp_path / "h", cli=real_cli, timeout=900)
    assert r.ok and r.xlsx


def test_missing_file(real_cli, tmp_path):
    with pytest.raises(ConverterError, match="not found"):
        convert(tmp_path / "nope.rvt", cli=real_cli)


def test_directory_as_input(real_cli, tmp_path):
    with pytest.raises(ConverterError):
        convert(tmp_path, cli=real_cli)


def test_empty_file(real_cli, tmp_path):
    p = tmp_path / "empty.rvt"
    p.write_bytes(b"")
    r = convert(p, cli=real_cli, out=tmp_path / "o", timeout=120)
    assert not r.ok and r.status == "FAILED"


def test_garbage_file(real_cli, tmp_path):
    p = tmp_path / "junk.rvt"
    p.write_bytes(os.urandom(200_000))
    r = convert(p, cli=real_cli, out=tmp_path / "o", timeout=120)
    assert not r.ok and r.exit_code != 0


def test_truncated_model(real_cli, keywest, tmp_path):
    p = tmp_path / "trunc.rvt"
    p.write_bytes(keywest.read_bytes()[:300_000])
    r = convert(p, cli=real_cli, out=tmp_path / "o", timeout=300)
    assert not r.ok or r.status  # either rejected cleanly or reported with a status; never a crash/hang


def test_unicode_and_space_paths(real_cli, keywest, tmp_path):
    d = tmp_path / "Проект дом 日本 with spaces"
    d.mkdir()
    p = d / "модель №1 (копия).rvt"
    shutil.copyfile(keywest, p)
    r = convert(p, ["xlsx"], d / "результат", cli=real_cli, timeout=600)
    assert r.ok and r.xlsx and r.xlsx.is_file()
    assert "результат" in str(r.output_dir)


def test_default_output_beside_input_is_unique(stub_cli, stub_models):
    a = convert(stub_models / "a.rvt", cli=stub_cli)
    b = convert(stub_models / "a.rvt", cli=stub_cli)
    assert a.output_dir != b.output_dir and a.output_dir.exists() and b.output_dir.exists()


def test_long_path(real_cli, keywest, tmp_path):
    d = tmp_path
    while len(str(d)) < 300:
        d = d / ("segment_" + "x" * 30)
    try:
        d.mkdir(parents=True)
    except OSError:
        pytest.skip("long paths unsupported on this system")
    p = d / "long.rvt"
    shutil.copyfile(keywest, p)
    r = convert(p, ["xlsx"], d / "out", cli=real_cli, timeout=600)
    assert r.ok and r.xlsx


def test_unknown_format(stub_cli, stub_models):
    with pytest.raises(ConverterError, match="unknown format"):
        convert(stub_models / "a.rvt", ["docx"], cli=stub_cli)


def test_timeout(stub_cli, stub_models, monkeypatch):
    monkeypatch.setenv("STUB_SLEEP", "5")
    with pytest.raises(ConverterError, match="timed out"):
        convert(stub_models / "a.rvt", cli=stub_cli, timeout=1)


def test_bad_cli_path(stub_models, tmp_path):
    with pytest.raises(ConverterError):
        convert(stub_models / "a.rvt", cli=tmp_path / "does-not-exist.exe")


def test_corrupt_summary_json_tolerated(tmp_path):
    (tmp_path / "summary.json").write_text("{not json")
    with pytest.raises(ValueError):
        summarize(tmp_path)  # surfaced, not silently wrong


def test_summarize_missing(tmp_path):
    with pytest.raises(ConverterError):
        summarize(tmp_path / "nothing")


def test_read_elements_not_xlsx(tmp_path):
    p = tmp_path / "x.xlsx"
    p.write_bytes(b"not a zip")
    with pytest.raises(Exception):
        read_elements(p)


# ---------- CLI entry ----------

def _run_cli(*args, env=None):
    e = {**os.environ, "PYTHONPATH": str(Path(ddc_converter.__file__).parent.parent), **(env or {})}
    return subprocess.run([sys.executable, "-m", "ddc_converter", *args], capture_output=True, text=True,
                          encoding="utf-8", env=e, timeout=300)


def test_cli_missing_input_exits_1(tmp_path):
    p = _run_cli(str(tmp_path / "missing.rvt"))
    assert p.returncode == 1 and "error:" in p.stderr and "Traceback" not in p.stderr


def test_cli_unicode_output(stub_cli, tmp_path):
    src = tmp_path / "дом.rvt"
    src.write_bytes(b"RVTx")
    p = _run_cli(str(src), "-o", str(tmp_path / "выход"), env={"DDC_CLI": stub_cli, "PYTHONIOENCODING": "cp1252"})
    assert p.returncode == 0, p.stderr
    assert "выход" in json.loads(p.stdout)["output_dir"]


# ---------- download + checksum ----------

def _asset_name(v="9.9.9"):
    return cli_mod._asset(v)


def _package(name: str) -> bytes:
    exe = "RVTconverter.exe" if sys.platform == "win32" else "RVTconverter"
    buf = io.BytesIO()
    if name.endswith(".zip"):
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("pkg/cli/" + exe, b"MZ fake")
    else:
        with tarfile.open(fileobj=buf, mode="w:gz") as t:
            data = b"#!/bin/sh\n"
            ti = tarfile.TarInfo("pkg/cli/" + exe)
            ti.size = len(data)
            ti.mode = 0o755
            t.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


@pytest.fixture
def release(http_files, monkeypatch):
    files, hits = http_files
    base = files["__base__"]
    monkeypatch.setenv("DDC_RELEASE_URL", base + "/{v}/{name}")
    name = _asset_name()
    pkg = _package(name)

    def publish(sha=None, sums_name=None, body=None):
        body = pkg if body is None else body
        files[f"/9.9.9/{name}"] = body
        sha = sha or hashlib.sha256(body).hexdigest()
        files["/9.9.9/SHA256SUMS.txt"] = f"{sha}  {sums_name or name}\n".encode()

    return publish, name, files


def test_download_ok_and_cached(release, tmp_path):
    publish, name, _ = release
    publish()
    exe = download_cli("9.9.9")
    assert exe.is_file() and exe.name.startswith("RVTconverter")
    assert exe.is_relative_to(cli_mod.cache_dir() / "9.9.9")


def test_download_sha_mismatch(release):
    publish, name, _ = release
    publish(sha="0" * 64)
    with pytest.raises(ConverterError, match="checksum mismatch"):
        download_cli("9.9.9")
    assert not (cli_mod.cache_dir() / "9.9.9").exists()


def test_download_not_listed(release):
    publish, name, _ = release
    publish(sums_name="other-file.zip")
    with pytest.raises(ConverterError, match="not listed"):
        download_cli("9.9.9")


def test_download_binary_marker_in_sums(release):
    publish, name, _ = release
    publish(sums_name="*" + name)  # `sha256sum -b` style
    assert download_cli("9.9.9").is_file()


def test_download_404(release):
    with pytest.raises(ConverterError, match="download failed"):
        download_cli("9.9.9")


def test_download_corrupt_archive(release):
    publish, name, _ = release
    publish(body=b"this is not an archive")
    with pytest.raises(ConverterError):
        download_cli("9.9.9")
    assert not (cli_mod.cache_dir() / "9.9.9").exists()


def test_download_archive_without_exe(release):
    publish, name, _ = release
    buf = io.BytesIO()
    if name.endswith(".zip"):
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("readme.txt", b"x")
    else:
        with tarfile.open(fileobj=buf, mode="w:gz") as t:
            ti = tarfile.TarInfo("readme.txt")
            ti.size = 1
            t.addfile(ti, io.BytesIO(b"x"))
    publish(body=buf.getvalue())
    with pytest.raises(ConverterError, match="executable not found"):
        download_cli("9.9.9")


def test_download_concurrent(release):
    publish, name, _ = release
    publish()
    res, errs = [], []

    def go():
        try:
            res.append(download_cli("9.9.9"))
        except Exception as e:  # noqa: BLE001
            errs.append(e)

    ts = [threading.Thread(target=go) for _ in range(4)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert not errs, errs
    assert len(set(res)) == 1 and res[0].is_file()


def test_find_cli_env_precedence(tmp_path, monkeypatch):
    exe = tmp_path / "RVTconverter.exe"
    exe.write_bytes(b"x")
    monkeypatch.setenv("DDC_CLI", str(tmp_path))
    assert find_cli() == exe
    monkeypatch.setenv("DDC_CLI", str(exe))
    assert find_cli() == exe


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="linux package")
def test_linux_package_executable_bit(release):
    publish, name, _ = release
    publish()
    assert os.access(download_cli("9.9.9"), os.X_OK)
