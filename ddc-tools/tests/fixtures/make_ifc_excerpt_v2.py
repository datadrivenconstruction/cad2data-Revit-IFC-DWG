"""Make "version 2" of the committed IFC excerpt, a realistic edit of the real converter output.

    python make_ifc_excerpt_v2.py ifc_duplex_excerpt ifc_duplex_excerpt_v2

Only data.jsonl is written. Every record that is not touched stays byte-for-byte as the converter wrote
it; the edits are what a designer does between two issues of a model:

* removed:  door 8169 and cabinet 13331 (with their properties, links and opening 13340)
* added:    wall 90001 (a copy of wall 4598 with a new GlobalId) and door 90002 (copy of door 6652)
* modified: wall 4131 (FireRating added to the wall set, Length/Area/Volume re-measured, Top Offset),
            window 6531 (renamed), slab 5165 (thicker: Thickness/Volume, Room Bounding), space 514 (Area/Volume)
* id churn: roof 22475 and beam 36686 get new STEP ids but keep their GlobalId (a re-export), so the
            comparison must use GlobalId, not the STEP id.
"""
import copy
import json
import sys
from pathlib import Path

NEW_GUID = {"90001": "3Zk0a1dXj9ZwB2Q7Ls4tDx", "90002": "1hOSvn6df7F8_7GcBWlNEW"}
RENUMBER = {"22475": "122475", "36686": "136686"}


def main(src, dst):
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    recs = [json.loads(l) for l in open(src / "data.jsonl", encoding="utf-8")]
    objs = {r["record"]["ID"]: r["record"] for r in recs if r["table"] == "Objects"}
    gone = {"8169", "13331", "13340"}          # door, cabinet and the opening named ...157950:1
    out = []
    for r in recs:
        t, rec = r["table"], r["record"]
        if t == "Objects" and rec["ID"] in gone:
            continue
        if t in ("Properties", "Quantities") and rec["owner_step_id"] in gone:
            continue
        if t == "SpatialLinks" and (rec["child_step_id"] in gone or rec["parent_step_id"] in gone):
            continue
        if t == "TypeLinks" and rec["owner_step_id"] in gone:
            continue
        out.append(r)

    def edit(owner, set_name, prop, value, table="Properties"):
        for r in out:
            x = r["record"]
            if r["table"] == table and x["owner_step_id"] == owner and x["set_name"] == set_name and x["property_name"] == prop:
                nv = x["value"]
                if "NominalValue" in nv:
                    nv["NominalValue"]["value"] = value
                    if isinstance(x.get("attributes", {}).get("NominalValue"), dict):
                        x["attributes"]["NominalValue"]["value"] = value
                else:
                    k = next(iter(nv))
                    nv[k] = value
                    if k in x.get("attributes", {}):
                        x["attributes"][k] = value
                return
        raise KeyError((owner, set_name, prop))

    # modified: wall 4131
    edit("4131", "PSet_Revit_Dimensions", "Length", 4.2915)
    edit("4131", "PSet_Revit_Dimensions", "Area", 11.9955)
    edit("4131", "PSet_Revit_Dimensions", "Volume", 1.48743)
    edit("4131", "PSet_Revit_Constraints", "Top Offset", -0.25)
    edit("4131", "Pset_WallCommon", "IsExternal", True)
    fr = copy.deepcopy(next(r for r in out if r["table"] == "Properties" and r["record"]["owner_step_id"] == "4131"
                            and r["record"]["property_name"] == "LoadBearing"))
    fr["record"]["property_name"] = "FireRating"
    fr["record"]["path"] = ["Pset_WallCommon", "FireRating"]
    fr["record"]["value"] = {"NominalValue": {"ifc_type": "IfcLabel", "value": "EI 60"}}
    fr["record"]["attributes"]["Name"] = "FireRating"
    fr["record"]["attributes"]["NominalValue"] = {"ifc_type": "IfcLabel", "value": "EI 60"}
    fr["record"]["property_step_id"] = "9990001"
    out.append(fr)
    # modified: window renamed
    for r in out:
        if r["table"] == "Objects" and r["record"]["ID"] == "6531":
            r["record"]["Name"] = r["record"]["Name"].replace("4835mm x 2420mm:4835mm x 2420mm:146016", "4835mm x 2420mm:4835mm x 2420mm:146016 (rev B)")
    # modified: a room gets bigger
    edit("514", "PSet_Revit_Dimensions", "Area", 19.25)
    edit("514", "PSet_Revit_Dimensions", "Volume", 50.05)
    # modified: slab gets thicker
    edit("5165", "PSet_Revit_Dimensions", "Thickness", 0.15)
    edit("5165", "PSet_Revit_Dimensions", "Volume", 9.71698920)
    edit("5165", "PSet_Revit_Constraints", "Room Bounding", False)

    # added: copies with new ids and GlobalIds
    def clone(old, new, name_suffix):
        o = copy.deepcopy(objs[old])
        o["ID"], o["GlobalId"] = new, NEW_GUID[new]
        o["StableKey"] = o["StableKey"].rsplit("#", 1)[0] + "#" + new
        o["Name"] = o["Name"].rsplit(":", 1)[0] + ":" + name_suffix
        o["Attributes"]["GlobalId"], o["Attributes"]["Name"] = o["GlobalId"], o["Name"]
        add = [{"table": "Objects", "ordinal": 999, "record": o}]
        for r in out:
            x = r["record"]
            if r["table"] in ("Properties", "Quantities") and x["owner_step_id"] == old:
                y = copy.deepcopy(r)
                y["record"]["owner_step_id"] = new
                add.append(y)
            elif r["table"] == "SpatialLinks" and x["child_step_id"] == old:
                y = copy.deepcopy(r)
                y["record"]["child_step_id"] = new
                add.append(y)
            elif r["table"] == "TypeLinks" and x["owner_step_id"] == old:
                y = copy.deepcopy(r)
                y["record"]["owner_step_id"] = new
                add.append(y)
        return add
    out += clone("4598", "90001", "209001")
    out += clone("6652", "90002", "209002")

    # id churn: new STEP id, same GlobalId
    for r in out:
        x = r["record"]
        for k in ("ID", "owner_step_id", "child_step_id", "parent_step_id", "type_step_id"):
            if x.get(k) in RENUMBER:
                x[k] = RENUMBER[x[k]]
    # sequence numbers
    n = {}
    for r in out:
        n[r["table"]] = n.get(r["table"], 0) + 1
        r["ordinal"] = n[r["table"]]
    with open(dst / "data.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:3])
