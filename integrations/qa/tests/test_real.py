"""Real model pairs. Skipped when the DDC CLI or the local sample files are missing."""
import csv
import gzip
import json
from collections import Counter
from pathlib import Path

import pytest

import realdata as R
from ddc_qa.diff import diff_models
from ddc_qa.model import load_model

pytestmark = [pytest.mark.real, pytest.mark.skipif(not R.have_cli(), reason="DDC CLI not available")]
HOUSE = R.CHECK / "house_ORIGINAL.rvt"
VILLA = R.CHECK / "villa_ORIGINAL.rvt"


def need(*paths):
    for p in paths:
        if not Path(p).exists():
            pytest.skip("missing %s" % p)


def ids(rows):
    return {int(r["ElementId"]) for r in rows}


@pytest.fixture(scope="module")
def house():
    need(HOUSE)
    return load_model(HOUSE)


# ---- Excel -> RVT writer outputs vs originals: diff must be exactly the edited cells ----
@pytest.mark.parametrize("tag,src", [("rme", R.RME), ("villa", str(VILLA))])
def test_writer_output_diff_is_exactly_the_edits(tag, src):
    need(src)
    if not R.WRITER:
        pytest.skip("rvt-write not available")
    s, o, exp = R.edit_pair(src, tag)
    d = diff_models(load_model(s), load_model(o))
    assert d.param_edits() == exp
    assert not d.added and not d.removed and not any(c.geom for c in d.changed)


def _journal(p):
    return [(r["element"], r["column"], r["old"], r["new"]) for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="	")]


@pytest.mark.parametrize("a,b,j", [
    ("excel_to_rvt/villa_original.rvt", "excel_to_rvt/villa_updated.rvt", "excel_to_rvt/changes.tsv"),
    ("house_ORIGINAL.rvt", "mark_20261024/house_M1long.rvt", "mark_20261024/house_M1long.rvt.changes.tsv"),
    ("house_ORIGINAL.rvt", "mark_20261024/house_M1same.rvt", "mark_20261024/house_M1same.rvt.changes.tsv"),
    ("villa_ORIGINAL.rvt", "mark_20261024/villa_M1long.rvt", "mark_20261024/villa_M1long.rvt.changes.tsv"),
])
def test_journal_pairs(a, b, j):
    """A journal edit is visible only if the 2.0.5 table carries that cell with the journal's old value in the
    original; the diff must equal exactly that visible subset (the rest are elements/cells outside the table)."""
    need(R.CHECK / a, R.CHECK / b, R.CHECK / j)
    ma, mb = load_model(R.CHECK / a), load_model(R.CHECK / b)
    d = diff_models(ma, mb)
    cell = {(str(r["ElementId"]), c): v for r in ma.rows for c, v in r.items()}
    visible = {(e, c, n) for e, c, o, n in _journal(R.CHECK / j) if str(cell.get((e, c))) == o}
    assert d.param_edits() == visible
    assert not d.added and not d.removed


@pytest.mark.parametrize("a,b", [("house_ORIGINAL.rvt", "house_W0_repack.rvt"), ("house_ORIGINAL.rvt", "house_W1_recompress.rvt"),
                                 ("villa_ORIGINAL.rvt", "villa_W2b_comments.rvt"), ("villa_ORIGINAL.rvt", "villa_W3a_longer.rvt")])
def test_repack_outputs_have_no_diff(a, b):
    need(R.CHECK / a, R.CHECK / b)
    d = diff_models(load_model(R.CHECK / a), load_model(R.CHECK / b))
    assert d.summary()["added"] == d.summary()["removed"] == d.summary()["changed"] == 0


def test_type_rename_is_one_door(house):
    need(R.CHECK / "house_W2_typename.rvt")
    d = diff_models(house, load_model(R.CHECK / "house_W2_typename.rvt"))
    assert d.param_edits() == {("318057", "Type Name", "1810x2119mm")}
    assert d.changed[0].old["Type Name"] == "1810x2110mm" and not d.added and not d.removed


# ---- Revit twin pairs: Revit opened house_ORIGINAL, applied an operation and saved ----
def _created(job):
    r = json.load(open(R.JOBS / job / "result.json"))
    out = set()
    for a in r["actions"]:
        i = a.get("info", {})
        out |= {x["id"] for x in i.get("new_ids", [])}
        if a["op"] in ("create_wall", "create_door"):
            out.add(i["id"])
    return out


def _saved(job):
    return next(p for p in (R.JOBS / job).iterdir() if p.suffix == ".rvt")


@pytest.mark.parametrize("job,added,changed", [
    ("clone__t0a", set(), set()),
    ("clone__t2_wall", {324080}, set()),
    ("clone__t3_door", {324080, 324081}, set()),
    ("clone__t4_two", {324080, 324081}, set()),
    ("gen__tw_floor", {324083}, set()),
    ("gen__tw_door", {324082}, {314628}),    # the new door cuts an opening in its host wall
    ("gen__tw_win", {324082}, {314360}),
])
def test_revit_twin_exact(house, job, added, changed):
    need(R.JOBS / job / "result.json")
    assert added <= _created(job) | added
    d = diff_models(house, load_model(_saved(job)))
    assert ids(d.added) == added and not d.removed
    assert {int(c.new["ElementId"]) for c in d.changed} == changed
    for c in d.changed:       # opening cut: volume and area shrink, triangle count differs, bbox unchanged
        assert c.geom and not c.geom.moved and not c.geom.resized and c.geom.volume_delta < 0
        assert c.geom.tris_new != c.geom.tris_old and {p for p, _, _ in c.params} >= {"Area (m²)", "Volume (m³)"}


def test_copy_of_wall_brings_its_hosted_inserts(house):
    need(R.JOBS / "clone__t1_copy")
    d = diff_models(house, load_model(_saved("clone__t1_copy")))
    assert ids(d.added) == set(range(324081, 324087)) and not d.changed
    assert Counter(r["Category"] for r in d.added)["Walls"] == 1


@pytest.mark.parametrize("job,base", [("a4", "a4"), ("a5", "a5"), ("a6", "a6"), ("a7", "a7"), ("c10", "c10"), ("c5_r2", "c5")])
def test_resaved_rvtgen_clones_match_revit_truth(house, job, base):
    """rvt-gen clone outputs re-saved by Revit: added elements == Revit's own element list difference."""
    d0 = R.JOBS / ("clone__" + job)
    need(d0 / "truth.json.gz", R.JOBS / "gen__tw_base" / "truth.json.gz")
    tn = {e["id"] for e in json.load(gzip.open(d0 / "truth.json.gz"))["elements"]}
    tb = {e["id"] for e in json.load(gzip.open(R.JOBS / "gen__tw_base" / "truth.json.gz"))["elements"]}
    d = diff_models(house, load_model(d0 / (base + "_resaved.rvt")))
    assert ids(d.added) == tn - tb and not d.removed and not d.changed


def test_raw_rvtgen_output_is_not_decodable_by_205():
    """Raw rvt-gen files (g10 = 30 clones) are written for Revit; DDC 2.0.5 refuses them cleanly, so no diff is possible."""
    need(R.GEN / "g10.rvt")
    with pytest.raises(RuntimeError, match="could not be decoded"):
        load_model(R.GEN / "g10.rvt")
