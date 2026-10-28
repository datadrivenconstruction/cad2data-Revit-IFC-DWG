import zipfile
from pathlib import Path

import pytest

import realdata as R
from ddc_qa import bcf, cli
from ddc_qa.clashcheck import validate
from ddc_qa.ids import run_ids
from ddc_qa.model import eid, load_model
from ddc_qa.rules import load_rules, run_rule, run_rules

pytestmark = [pytest.mark.real, pytest.mark.skipif(not R.have_cli(), reason="DDC CLI not available")]
MEP = Path(r"C:\Users\Artem\Desktop\CC Projects\rvt_export\corpus_downloads\holdout_20260911\daniel_installations.rvt")
RULES = Path(__file__).parent.parent / "ddc_qa" / "rules"
XSD = Path(r"C:\tmp\modern\xsd")


@pytest.fixture(scope="module")
def mep():
    if not MEP.exists():
        pytest.skip("sample missing")
    return load_model(MEP)


def test_mep_clashes_are_confirmed_by_independent_sampling(mep):
    for a, b, expect in ((["Pipes"], ["Walls"], 30), (["Conduits"], ["Walls"], 180)):
        f = run_rule({"type": "clash", "a": a, "b": b, "tolerance": 0.01}, mep)
        assert len(f) == expect                                    # every bbox candidate is a real penetration
        rows = validate(mep, f, 20)
        assert len(rows) == 20 and all(r[5] for r in rows)         # 0 / 20 false positives
        nb = run_rule({"type": "clash", "a": a, "b": b, "tolerance": 0.01, "refine": False}, mep)
        assert len(nb) == len(f)


def test_bbox_only_candidates_are_rejected_when_surfaces_do_not_meet():
    p = R.RME
    if not Path(p).exists():
        pytest.skip("sample missing")
    m = load_model(p)
    rule = {"type": "clash", "a": ["Walls"], "b": ["Floors"], "tolerance": 0.01}
    f = run_rule(rule, m)
    nb = run_rule({**rule, "refine": False}, m)
    assert len(f) < len(nb)
    keys = {(eid(x.element), eid(x.other)) for x in f}
    rej = [x for x in nb if (eid(x.element), eid(x.other)) not in keys]
    assert not any(r[5] for r in validate(m, rej, 20, seed=3))     # rejected pairs do not interpenetrate (no false negatives)
    assert all(r[5] for r in validate(m, f, 20))


@pytest.mark.parametrize("name", ["architecture", "mep", "data_quality"])
def test_bundled_rule_sets_run_and_export_valid_bcf(mep, name, tmp_path):
    f = run_rules(load_rules(RULES / (name + ".yaml")), mep)
    out = tmp_path / "x.bcfzip"
    n = bcf.write_bcf(f, out, MEP.name, meshes=mep.meshes, max_topics=200)
    assert n == min(len(f), 200)
    et = pytest.importorskip("lxml.etree")
    if not (XSD / "markup.xsd").exists():
        pytest.skip("xsd missing")
    sch = {k: et.XMLSchema(et.parse(str(XSD / v))) for k, v in (("bcf", "markup.xsd"), ("bcfv", "visinfo.xsd"))}
    z = zipfile.ZipFile(out)
    for nm in z.namelist():
        k = nm.rsplit(".", 1)[-1]
        if k in sch:
            assert sch[k].validate(et.fromstring(z.read(nm))), (nm, sch[k].error_log)


def test_ids_example_on_real_model(mep):
    p = Path(__file__).parent.parent / "examples" / "doors_windows.ids"
    title, f, notes = run_ids(p, mep)
    assert title == "Doors and windows handover" and not notes
    assert all(x.element["Category"] in ("Doors", "Windows") for x in f)


def test_cli_end_to_end(tmp_path):
    out = tmp_path / "o"
    rc = cli.main(["check", str(MEP), "--rules", "mep", "data_quality", str(Path(__file__).parent.parent / "examples" / "doors_windows.ids"), "-o", str(out)])
    assert rc == 0
    for f in ("check.xlsx", "check.html", "issues.bcfzip"):
        assert (out / f).stat().st_size > 500
