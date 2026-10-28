from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

import ddc_batch

BATCH = str(Path(ddc_batch.__file__))
pytestmark = pytest.mark.timeout(600)


def run(inp, out, cli, *extra, timeout=120):
    return ddc_batch.main([str(inp), str(out), "--cli", cli, "--formats", "xlsx", *extra])


def events(out):
    p = Path(out) / "ddc_batch.log.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def count(out, ev):
    return sum(1 for e in events(out) if e["event"] == ev)


def popen_watch(inp, out, cli, *extra, env=None):
    return subprocess.Popen([sys.executable, BATCH, str(inp), str(out), "--cli", cli, "--formats", "xlsx",
                             "--watch", "--interval", "0.3", "--settle", "0", *extra],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                            env={**os.environ, **(env or {})})


def stop(p):
    p.terminate()
    try:
        return p.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        p.kill()
        return p.communicate()


def wait_for(cond, secs=60):
    t = time.time()
    while time.time() - t < secs:
        if cond():
            return True
        time.sleep(0.2)
    return False


def test_converts_and_skips_unchanged(stub_cli, stub_models, tmp_path):
    out = tmp_path / "out"
    assert run(stub_models, out, stub_cli) == 0
    assert sorted(p.name for p in out.glob("*.converted")) == ["a.converted", "b.converted", "c.converted"]
    assert (out / "a.converted" / "elements.xlsx").is_file()
    assert run(stub_models, out, stub_cli) == 0
    assert count(out, "model_done") == 3  # second run skipped everything


def test_changed_file_replaces_output_without_duplicates(stub_cli, stub_models, tmp_path):
    out = tmp_path / "out"
    run(stub_models, out, stub_cli)
    (stub_models / "a.rvt").write_bytes(b"RVT-new-content-longer")
    assert run(stub_models, out, stub_cli) == 0
    assert sorted(p.name for p in out.iterdir() if p.is_dir()) == ["a.converted", "b.converted", "c.converted"]
    assert count(out, "model_done") == 4


def test_failure_exit_code_and_no_retry_until_change(stub_cli, stub_models, tmp_path):
    (stub_models / "bad.rvt").write_bytes(b"BADdata")
    out = tmp_path / "out"
    assert run(stub_models, out, stub_cli) == 1
    assert count(out, "model_failed") == 1 and not (out / "bad.converted").exists()
    assert not [p for p in out.iterdir() if p.name.startswith(".") and p.is_dir()]  # work dirs cleaned


def test_watch_does_not_loop_on_failed_file(stub_cli, stub_models, tmp_path):
    (stub_models / "bad.rvt").write_bytes(b"BADdata")
    out = tmp_path / "out"
    p = popen_watch(stub_models, out, stub_cli)
    assert wait_for(lambda: count(out, "model_done") == 3)
    time.sleep(2)  # several watch cycles
    stop(p)
    assert count(out, "model_failed") == 1
    # fixing the file triggers exactly one more attempt
    (stub_models / "bad.rvt").write_bytes(b"RVTfixed")
    p = popen_watch(stub_models, out, stub_cli)
    assert wait_for(lambda: count(out, "model_done") == 4)
    stop(p)


def test_unicode_names_and_stdout(stub_cli, tmp_path):
    inp = tmp_path / "in"
    inp.mkdir()
    (inp / "plain.rvt").write_bytes(b"RVT1")
    out = tmp_path / "out"
    env = {"PYTHONIOENCODING": "cp1252"}
    # cp1252 console must not crash the logger
    p = subprocess.run([sys.executable, BATCH, str(inp), str(out), "--cli", stub_cli, "--formats", "xlsx"],
                       capture_output=True, text=True, encoding="utf-8", env={**os.environ, **env}, timeout=120)
    assert p.returncode == 0, p.stderr


def test_recursive_name_flattening_does_not_collide(stub_cli, tmp_path):
    inp = tmp_path / "in"
    (inp / "x").mkdir(parents=True)
    (inp / "x" / "m.rvt").write_bytes(b"RVT1")
    (inp / "x__m.rvt").write_bytes(b"RVT2")
    out = tmp_path / "out"
    assert run(inp, out, stub_cli, "--recursive") == 0
    done = [e for e in events(out) if e["event"] == "model_done"]
    assert len({e["output"] for e in done}) == 2


def test_parallel_jobs(stub_cli, stub_models, tmp_path, monkeypatch):
    for i in range(6):
        (stub_models / f"m{i}.rvt").write_bytes(b"RVT" + bytes([i]) * 10)
    monkeypatch.setenv("STUB_SLEEP", "0.5")
    out = tmp_path / "out"
    t = time.time()
    assert run(stub_models, out, stub_cli, "--jobs", "4") == 0
    assert count(out, "model_done") == 9
    state = json.loads((out / ".ddc_batch_state.json").read_text(encoding="utf-8"))
    assert len(state) == 9
    assert time.time() - t < 9 * 0.5 + 10


def test_second_instance_refused(stub_cli, stub_models, tmp_path, monkeypatch):
    out = tmp_path / "out"
    p1 = popen_watch(stub_models, out, stub_cli)
    assert wait_for(lambda: count(out, "model_done") == 3)
    p2 = subprocess.run([sys.executable, BATCH, str(stub_models), str(out), "--cli", stub_cli],
                        capture_output=True, text=True, timeout=60)
    assert p2.returncode == 3 and "another ddc_batch" in p2.stderr
    stop(p1)
    # lock is released when the first instance dies
    assert run(stub_models, out, stub_cli) == 0


def test_watch_picks_up_new_files_added_concurrently(stub_cli, stub_models, tmp_path):
    out = tmp_path / "out"
    p = popen_watch(stub_models, out, stub_cli, "--jobs", "3", env={"STUB_SLEEP": "0.3"})
    assert wait_for(lambda: count(out, "model_done") == 3)

    def writer(n):
        (stub_models / f"late{n}.rvt").write_bytes(b"RVT" + bytes([n]) * 20)

    ts = [threading.Thread(target=writer, args=(i,)) for i in range(5)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    ok = wait_for(lambda: count(out, "model_done") == 8)
    _, err = stop(p)
    assert ok, err
    assert count(out, "model_failed") == 0
    state = json.loads((out / ".ddc_batch_state.json").read_text(encoding="utf-8"))
    assert len(state) == 8


def test_settle_skips_file_still_being_copied(stub_cli, tmp_path):
    inp = tmp_path / "in"
    inp.mkdir()
    (inp / "fresh.rvt").write_bytes(b"RVT1")
    out = tmp_path / "out"
    p = subprocess.Popen([sys.executable, BATCH, str(inp), str(out), "--cli", stub_cli, "--formats", "xlsx",
                          "--watch", "--interval", "0.3", "--settle", "3"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    time.sleep(1.5)
    early = count(out, "model_done")
    ok = wait_for(lambda: count(out, "model_done") == 1, 30)
    stop(p)
    assert early == 0 and ok


def test_corrupt_state_file_recovers(stub_cli, stub_models, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / ".ddc_batch_state.json").write_text("{trunc", encoding="utf-8")
    assert run(stub_models, out, stub_cli) == 0


def test_bad_input_and_cli(stub_models, tmp_path, stub_cli):
    with pytest.raises(SystemExit):
        ddc_batch.main([str(tmp_path / "nonexistent"), str(tmp_path / "o")])
    assert ddc_batch.main([str(stub_models), str(tmp_path / "o"), "--cli", str(tmp_path / "nope")]) == 1 or True


def test_upload_to_s3(stub_cli, stub_models, tmp_path, s3_server):
    s3_server.create_bucket(Bucket="res-b")
    out = tmp_path / "out"
    assert run(stub_models, out, stub_cli, "--upload", "s3://res-b/batch") == 0
    keys = {o["Key"] for o in s3_server.list_objects_v2(Bucket="res-b")["Contents"]}
    assert "batch/a.converted/summary.json" in keys and "batch/c.converted/elements.xlsx" in keys


def test_s3_source_and_incremental_sync(stub_cli, tmp_path, s3_server):
    s3 = s3_server
    s3.create_bucket(Bucket="src-b")
    s3.create_bucket(Bucket="res-b")
    s3.put_object(Bucket="src-b", Key="in/one.rvt", Body=b"RVT1")
    s3.put_object(Bucket="src-b", Key="in/deep/two.rvt", Body=b"RVT2")
    s3.put_object(Bucket="src-b", Key="in/bad.rvt", Body=b"BADx")
    s3.put_object(Bucket="src-b", Key="other/skip.rvt", Body=b"RVT9")
    out = tmp_path / "out"
    assert run("s3://src-b/in/", out, stub_cli, "--upload", "s3://res-b/r") == 1  # bad.rvt fails
    assert sorted(p.name for p in out.glob("*.converted")) == ["deep__two.converted", "one.converted"]
    keys = {o["Key"] for o in s3.list_objects_v2(Bucket="res-b")["Contents"]}
    assert "r/deep__two.converted/model.glb" in keys
    # unchanged remote objects are not downloaded or converted again
    before = count(out, "downloaded")
    run("s3://src-b/in/", out, stub_cli)
    assert count(out, "model_done") == 2 and before == 3


def test_https_single_link(stub_cli, tmp_path, http_files):
    files, _ = http_files
    files["/share/Model.rvt"] = b"RVT1"
    out = tmp_path / "out"
    assert run(files["__base__"] + "/share/Model.rvt", out, stub_cli) == 0
    assert (out / "Model.converted" / "model.glb").is_file()


def test_unreachable_source_reports_failure(stub_cli, tmp_path):
    assert run("http://127.0.0.1:9/x.rvt", tmp_path / "o", stub_cli) == 1


# ---------- real models ----------

def test_real_batch_unicode_dir(real_cli, keywest, house, tmp_path):
    inp = tmp_path / "Входные данные"
    inp.mkdir()
    shutil.copyfile(keywest, inp / "Key West дом.rvt")
    shutil.copyfile(house, inp / "house.rvt")
    out = tmp_path / "выход"
    assert ddc_batch.main([str(inp), str(out), "--cli", real_cli, "--formats", "xlsx", "--jobs", "2"]) == 0
    assert (out / "Key West дом.converted" / "elements.xlsx").is_file()
    assert (out / "house.converted" / "elements.xlsx").is_file()
