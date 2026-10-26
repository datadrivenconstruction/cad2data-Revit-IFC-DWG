import zipfile
from pathlib import Path

import numpy as np
import pytest

from ddc_qa import bcf, ids as idsmod
from ddc_qa.clash import tri_tri_intersect
from ddc_qa.diff import diff_models
from ddc_qa.diffreport import write_all
from ddc_qa.glb import write_colored_glb
from ddc_qa.rules import run_rule
from synth import box, model, row

XSD = Path(r"C:\tmp\modern\xsd")


def test_diff_exact():
    old = model([row(1, "Walls", Mark="A"), row(2, "Walls", Mark="B"), row(3, "Doors")],
                {1: box((0, 0, 0), (1, 1, 1)), 2: box((5, 0, 0), (6, 1, 1)), 3: box((9, 9, 9), (10, 10, 10))})
    new = model([row(1, "Walls", Mark="A2"), row(2, "Walls", Mark="B"), row(4, "Doors")],
                {1: box((0, 0, 0), (1, 1, 1)), 2: box((5, 0.5, 0), (6, 1.5, 2)), 4: box((0, 0, 0), (1, 1, 1))})
    d = diff_models(old, new)
    assert d.summary() == {"added": 1, "removed": 1, "changed": 2, "unchanged": 0}
    assert d.param_edits() == {("1", "Mark", "A2")}
    g = {c.new["ElementId"]: c.geom for c in d.changed}
    assert g[1] is None and g[2].moved and g[2].resized and abs(g[2].volume_delta - 1.0) < 1e-9
    assert g[2].tris_old == g[2].tris_new == 12


def test_diff_fallback_to_elementid_and_noise_free():
    old = model([row(1, "Walls", Width=0.2)], {1: box((0, 0, 0), (1, 1, 1))})
    r = row(1, "Walls", Width=0.2 + 1e-9)
    r["UniqueId"] = None
    new = model([r], {1: box((0, 0, 0), (1, 1, 1))})
    d = diff_models(old, new)
    assert d.summary()["changed"] == 0 and d.matched_by_id == 1


def test_glb_roundtrip_and_reports(tmp_path):
    p = tmp_path / "a.glb"
    write_colored_glb(p, [("changed:7", box((0, 0, 0), (2, 1, 1)), (1, 1, 0, 1))])
    from ddc_qa.glb import read_glb
    j, _ = read_glb(p)
    assert j["nodes"][0]["name"] == "changed:7"
    old = model([row(1, "Walls", Mark="A")], {1: box((0, 0, 0), (1, 1, 1))})
    new = model([row(1, "Walls", Mark="B"), row(2, "Doors")], {1: box((0, 0, 0), (1, 1, 1)), 2: box((3, 0, 0), (4, 1, 1))})
    out = write_all(diff_models(old, new), old, new, tmp_path / "o", "old", "new")
    for f in ("diff.xlsx", "diff.html", "diff.glb", "viewer.html"):
        assert (out / f).stat().st_size > 100
    v = (out / "viewer.html").read_text(encoding="utf-8")
    assert "cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" in v and "added:2" not in v  # GLB is base64


def test_tri_tri():
    A = np.array([[[0, 0, 0], [2, 0, 0], [0, 2, 0]]], float)
    B = np.array([[[0.5, 0.5, -1], [0.5, 0.5, 1], [1.5, 0.5, 0]]], float)   # pierces A
    assert tri_tri_intersect(A, B)[0]
    C = B + np.array([0, 0, 3.0])
    assert not tri_tri_intersect(A, C)[0]
    D = np.array([[[0, 0, 0], [2, 0, 0], [0, 2, 0]]], float) + np.array([5, 0, 0.0])
    assert not tri_tri_intersect(A, D)[0]


def _clash_model():
    rows = [row(1, "Walls"), row(2, "Pipes"), row(3, "Pipes"), row(4, "Pipes")]
    meshes = {1: box((0, 0, 0), (4, 0.3, 3)),
              2: box((1, -1, 1), (1.2, 1, 1.2)),      # crosses the wall: hard clash
              3: box((1, 0.1, 1), (1.2, 0.2, 1.2)),   # fully inside: no surface crossing
              4: box((1, 0.5, 1), (1.2, 1.5, 1.2))}   # bbox clear of wall in y
    return model(rows, meshes)


def test_clash_bbox_then_mesh():
    m = _clash_model()
    f = run_rule({"type": "clash", "a": ["Walls"], "b": ["Pipes"], "tolerance": 0.01}, m)
    assert {x.other["ElementId"] for x in f} == {2, 3}   # 3 lies fully inside the wall (containment)
    assert {x.other["ElementId"] for x in run_rule({"type": "clash", "a": ["Walls"], "b": ["Pipes"], "containment": False}, m)} == {2}
    f2 = run_rule({"type": "clash", "a": ["Walls"], "b": ["Pipes"], "tolerance": 0.01, "refine": False}, m)
    assert {x.other["ElementId"] for x in f2} == {2, 3}
    f3 = run_rule({"type": "clash", "a": ["Walls"], "b": ["Pipes"], "tolerance": 0.25}, m)
    assert f3 == []   # overlap 0.2 in x/z is below the tolerance


def test_rule_types():
    rows = [row(1, "Walls", Mark="M1", Width=0.1, **{"Type Name": "W_Ext"}), row(2, "Walls", Mark="M1", Width=0.5),
            row(3, "Doors", Mark="", Level=None, Fire="1HR"), row(4, "Doors", Mark="D4", Fire="9HR", **{"Type Name": "bad name"})]
    m = model(rows)
    assert [x.element_id for x in run_rule({"type": "required_params", "category": "Doors", "params": ["Mark"]}, m)] == [3]
    assert [x.element_id for x in run_rule({"type": "range", "category": "Walls", "param": "Width", "min": 0.15, "max": 0.4}, m)] == [1, 2]
    assert [x.element_id for x in run_rule({"type": "enum", "param": "Fire", "values": ["1HR", "2HR"]}, m)] == [4]
    assert [x.element_id for x in run_rule({"type": "regex", "param": "Mark", "pattern": "[A-Z]\\d"}, m)] == []
    assert [x.element_id for x in run_rule({"type": "naming", "category": "Doors", "pattern": "[A-Za-z0-9_]+"}, m)] == [4]
    assert [x.element_id for x in run_rule({"type": "duplicate", "param": "Mark"}, m)] == [1, 2]
    assert [x.element_id for x in run_rule({"type": "no_level"}, m)] == [3]


IDS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ids xmlns="http://standards.buildingsmart.org/IDS" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://standards.buildingsmart.org/IDS http://standards.buildingsmart.org/IDS/1.0/ids.xsd">
 <info><title>t</title></info>
 <specifications>
  <specification name="walls" ifcVersion="IFC4">
   <applicability minOccurs="0" maxOccurs="unbounded"><entity><name><simpleValue>IFCWALL</simpleValue></name></entity></applicability>
   <requirements>
    <property dataType="IFCLABEL" cardinality="required"><propertySet><simpleValue>Pset_WallCommon</simpleValue></propertySet>
      <baseName><simpleValue>Fire</simpleValue></baseName>
      <value><xs:restriction base="xs:string"><xs:enumeration value="1HR"/><xs:enumeration value="2HR"/></xs:restriction></value></property>
    <attribute cardinality="required"><name><simpleValue>Name</simpleValue></name><value><xs:restriction base="xs:string"><xs:pattern value="W_.*"/></xs:restriction></value></attribute>
   </requirements>
  </specification>
  <specification name="mat" ifcVersion="IFC4">
   <applicability minOccurs="0" maxOccurs="unbounded"><entity><name><simpleValue>IFCDOOR</simpleValue></name></entity></applicability>
   <requirements><material cardinality="required"/></requirements>
  </specification>
 </specifications>
</ids>"""


def test_ids(tmp_path):
    p = tmp_path / "t.ids"
    p.write_text(IDS_XML, encoding="utf-8")
    W = {"IfcClass": "IFCWALL"}
    m = model([row(1, "Walls", Fire="1HR", **{"Type Name": "W_a"}, **W), row(2, "Walls", Fire="3HR", **{"Type Name": "W_b"}, **W),
               row(3, "Walls", **{"Type Name": "X"}, **W), row(4, "Doors", IfcClass="IFCDOOR")])
    title, f, notes = idsmod.run_ids(p, m)
    assert [x.element_id for x in f] == [2, 3, 3]
    assert len(notes) == 1 and "material" in notes[0]
    xsd = XSD / "ids.xsd"
    if xsd.exists():
        lxml = pytest.importorskip("lxml.etree")
        sch = lxml.XMLSchema(lxml.parse(str(xsd)))
        assert sch.validate(lxml.parse(str(p))), sch.error_log


def test_bcf_structure_and_xsd(tmp_path):
    from ddc_qa.rules import Finding
    f = [Finding("R1", "Missing mark", "error", "empty Mark", row(1, "Doors")),
         Finding("CL", "Clash", "error", "x clashes y", row(1, "Walls"), row(2, "Pipes"), (1.0, 2.0, 3.0))]
    out = tmp_path / "x.bcfzip"
    assert bcf.write_bcf(f, out, "m.rvt", meshes={1: box((0, 0, 0), (1, 1, 1))}) == 2
    z = zipfile.ZipFile(out)
    names = z.namelist()
    assert "bcf.version" in names and sum(n.endswith("/markup.bcf") for n in names) == 2
    xsds = {n: XSD / n for n in ("markup.xsd", "visinfo.xsd", "version.xsd")}
    if not all(p.exists() for p in xsds.values()):
        pytest.skip("BCF XSDs not fetched into %s" % XSD)
    et = pytest.importorskip("lxml.etree")
    sch = {n: et.XMLSchema(et.parse(str(p))) for n, p in xsds.items()}
    for n in names:
        key = {"markup.bcf": "markup.xsd", "viewpoint.bcfv": "visinfo.xsd", "bcf.version": "version.xsd"}.get(n.split("/")[-1])
        if key:
            doc = et.fromstring(z.read(n))
            assert sch[key].validate(doc), (n, sch[key].error_log)
    vp = [n for n in names if n.endswith(".bcfv")][0]
    assert b'IfcGuid="G000000000000000000001"' in z.read(vp)


def test_example_ids_validates_against_schema():
    xsd = XSD / "ids.xsd"
    if not xsd.exists():
        pytest.skip("ids.xsd not fetched")
    et = pytest.importorskip("lxml.etree")
    ex = Path(__file__).parent.parent / "examples" / "doors_windows.ids"
    sch = et.XMLSchema(et.parse(str(xsd)))
    assert sch.validate(et.parse(str(ex))), sch.error_log
