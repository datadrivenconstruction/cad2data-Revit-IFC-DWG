"""``ddc convert`` with the converters replaced by a stub that copies the trimmed real output."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from ddc_tools import cli, convert

DATA = Path(__file__).parent / "data"


@pytest.fixture()
def conv(tmp_path):
    c = tmp_path / "DDC_WINDOWS_Converters"
    for rel in ("DDC_RVT_Converter/cli/RVTconverter.exe",
                "DDC_IFC_to_Excel/runtime/python.exe",
                "DDC_IFC_to_Excel/sources/ifc-excel/converter.py",
                "DDC_CAD_Drawing_to_Excel/cli/dwg2excel.exe"):
        f = c / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("stub")
    return c


@pytest.fixture()
def calls(monkeypatch):
    seen = []

    def fake_run(cmd, capture_output=True, text=True, **kw):
        seen.append(cmd)
        exe = Path(cmd[0]).name.lower()
        if exe == "rvtconverter.exe":
            out = Path(cmd[cmd.index("-o") + 1])
            assert not out.exists(), "the RVT converter refuses an existing folder"
            shutil.copytree(DATA / "rvt_converted", out)
            return subprocess.CompletedProcess(cmd, 2, "", "")
        out = Path(cmd[cmd.index("--output") + 1])
        if exe == "python.exe":
            shutil.copytree(DATA / "ifc_excel", out / "Model-0123456789ab")
        else:
            shutil.copytree(DATA / "dwg", out / "plan")
        return subprocess.CompletedProcess(cmd, 0, "{}", "")

    monkeypatch.setattr(convert.subprocess, "run", fake_run)
    return seen


def test_rvt_command_line_and_default_names(tmp_path, conv, calls):
    m = tmp_path / "Project.rvt"
    m.write_bytes(b"x")
    res = convert.convert(str(m), converters=str(conv))
    cmd = calls[0]
    assert cmd[1] == str(m.resolve()) and cmd[2] == "-o" and cmd[3].endswith("Project.converted")
    assert cmd[4:] == ["--properties", "--ifc"]
    assert Path(res["xlsx"]).name == "Project_rvt.xlsx" and Path(res["xlsx"]).exists()
    assert res["conversion"] == "done" and res["converter_exit"] == 2 and res["elements"] >= 3


def test_no_ifc_option_drops_the_flag(tmp_path, conv, calls):
    m = tmp_path / "P.rvt"
    m.write_bytes(b"x")
    convert.convert(str(m), converters=str(conv), ifc=False)
    assert calls[0][4:] == ["--properties"]


def test_ifc_and_dwg_command_lines(tmp_path, conv, calls):
    i = tmp_path / "Model.ifc"
    i.write_bytes(b"x")
    r = convert.convert(str(i), converters=str(conv))
    assert calls[0][1].endswith("converter.py") and calls[0][3] == "--output"
    assert Path(r["xlsx"]).name == "Model_ifc.xlsx" and r["elements"] == 10
    d = tmp_path / "plan.dwg"
    d.write_bytes(b"x")
    r = convert.convert(str(d), converters=str(conv))
    assert calls[1][2:] == ["--output", str(tmp_path / "plan.converted"), "--json", "--no-svg", "--no-dxf", "--no-xlsx"]
    assert Path(r["xlsx"]).name == "plan_dwg.xlsx"


def test_finished_output_is_reused_and_force_moves_it_aside(tmp_path, conv, calls):
    m = tmp_path / "P.rvt"
    m.write_bytes(b"x")
    os.utime(m, (1_000_000, 1_000_000))          # the model is older than any converter output
    convert.convert(str(m), converters=str(conv))
    r = convert.convert(str(m), converters=str(conv))
    assert r["conversion"] == "reused" and len(calls) == 1
    r = convert.convert(str(m), converters=str(conv), force=True)
    assert r["conversion"] == "done" and len(calls) == 2
    assert Path(r["moved_aside"]).exists()                     # nothing is deleted


def test_errors(tmp_path, conv, monkeypatch, tmp_path_factory):
    with pytest.raises(convert.ConvertError):
        convert.convert(str(tmp_path / "missing.rvt"), converters=str(conv))
    t = tmp_path / "a.txt"
    t.write_text("x")
    with pytest.raises(convert.ConvertError):
        convert.convert(str(t), converters=str(conv))
    m = tmp_path / "P.rvt"
    m.write_bytes(b"x")
    monkeypatch.setattr(convert.subprocess, "run",
                        lambda cmd, capture_output=True, text=True, **kw: subprocess.CompletedProcess(cmd, 1, "", "boom"))
    with pytest.raises(convert.ConvertError, match="exit 1"):
        convert.convert(str(m), converters=str(conv))
    monkeypatch.delenv("DDC_CONVERTERS", raising=False)
    monkeypatch.setattr(convert, "__file__", str(tmp_path / "a" / "b" / "c" / "d" / "convert.py"))
    monkeypatch.chdir(tmp_path_factory.mktemp("elsewhere"))
    with pytest.raises(convert.ConvertError, match="converters folder"):
        convert.find_converters(str(tmp_path / "nope"))


def test_cli_json_line_for_scripts(tmp_path, conv, calls, capsys):
    m = tmp_path / "P.rvt"
    m.write_bytes(b"x")
    assert cli.main(["convert", str(m), "--converters", str(conv), "--json"]) == 0
    res = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert res["kind"] == "rvt" and res["xlsx"].endswith("P_rvt.xlsx")


def test_dwg_converter_found_under_old_and_new_folder_name(tmp_path):
    new = tmp_path / "new"
    old = tmp_path / "old"
    for root, name in ((new, "DDC_CAD_Drawing_to_Excel"), (old, "DDC_DWG_to_Excel")):
        exe = root / name / "cli" / "dwg2excel.exe"
        exe.parent.mkdir(parents=True)
        exe.write_text("stub")
    m = tmp_path / "plan.dwg"
    assert convert.command_for("dwg", m, tmp_path / "w", new)[0] == str(new / "DDC_CAD_Drawing_to_Excel/cli/dwg2excel.exe".replace("/", os.sep))
    assert convert.command_for("dwg", m, tmp_path / "w", old)[0] == str(old / "DDC_DWG_to_Excel/cli/dwg2excel.exe".replace("/", os.sep))
    assert convert.find_converters(str(old)) == old
