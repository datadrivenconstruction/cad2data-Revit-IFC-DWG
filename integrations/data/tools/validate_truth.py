"""Compare report-template totals against Revit truth dumps (truth.json.gz).

usage: python validate_truth.py OUT.json NAME=XLSX=TRUTH_JSON_GZ [NAME=XLSX=TRUTH_JSON_GZ ...]

Per element, our Length/Area/Volume must be within 1 % of the Revit parameter values
(CURVE_ELEM_LENGTH, HOST_AREA_COMPUTED / RBS_CURVE_SURFACE_AREA, HOST_VOLUME_COMPUTED, feet converted to metres).
Category totals come from the quantity_takeoff template, so the check covers the report path end to end.
"""
import gzip
import json
import sys

from ddc_data.builtin import BUILTIN
from ddc_data.frame import load
from ddc_data.report import run_template

FT, FT2, FT3 = 0.3048, 0.09290304, 0.028316846592
HOSTS = {"Walls", "Floors", "Ceilings", "Roofs"}
Q = {"Length": (("CURVE_ELEM_LENGTH",), FT), "Area": (("HOST_AREA_COMPUTED", "RBS_CURVE_SURFACE_AREA"), FT2),
     "NetArea": (("HOST_AREA_COMPUTED",), FT2), "Volume": (("HOST_VOLUME_COMPUTED",), FT3)}


def truth_values(path):
    d = json.load(gzip.open(path))
    out = {}
    for e in d["elements"]:
        for q, (bips, f) in Q.items():
            for p in e.get("params", []):
                if p.get("bip_name") in bips and isinstance(p.get("raw"), (int, float)) and p["raw"] > 0:
                    out.setdefault(q, {})[e["id"]] = p["raw"] * f
                    break
    return out, d["element_count"]


def check(name, xlsx, truth):
    fr = load(xlsx)
    df = fr.df.set_index("ElementId")
    tv, n_truth = truth_values(truth)
    rep = run_template(BUILTIN["quantity_takeoff"], fr)
    bycat = rep.sections[0]
    res = {"model": name, "elements_ours": len(df), "elements_truth": n_truth, "quantities": {}}
    cats = {}
    for q, vals in tv.items():
        if q not in df.columns:
            res["quantities"][q] = {"error": "column missing"}
            continue
        ours = df[q]
        n = ok = both = 0
        h_n = h_ok = 0
        h_t = h_o = 0.0
        t_sum = o_sum = 0.0
        for i, t in vals.items():
            n += 1
            o = ours.get(i)
            if o is None or o != o:
                continue
            both += 1
            t_sum += t
            o_sum += float(o)
            if abs(float(o) - t) <= 0.01 * t + 1e-9:
                ok += 1
            c = df.at[i, "Category"]
            if df.at[i, "CategoryEn"] in HOSTS:
                h_n += 1
                h_t += t
                h_o += float(o)
                h_ok += abs(float(o) - t) <= 0.01 * t + 1e-9
            a = cats.setdefault(c, {}).setdefault(q, [0.0, 0.0])
            a[0] += t
            a[1] += float(o)
        tot_tpl = float(bycat.totals.get(q, 0.0))
        res["quantities"][q] = {
            "truth_elements": n, "matched": both, "within_1pct": ok,
            "within_1pct_of_matched": round(100 * ok / both, 2) if both else None,
            "truth_total": round(t_sum, 3), "ours_total_same_ids": round(o_sum, 3),
            "total_diff_pct": round(100 * (o_sum - t_sum) / t_sum, 3) if t_sum else None,
            "template_total_all_elements": round(tot_tpl, 3),
            "hosts_matched": h_n, "hosts_within_1pct": int(h_ok),
            "hosts_total_diff_pct": round(100 * (h_o - h_t) / h_t, 3) if h_t else None}
    worst = []
    for c, qs in cats.items():
        for q, (t, o) in qs.items():
            worst.append((abs(o - t) / t if t else 0, c, q, round(t, 2), round(o, 2)))
    res["worst_categories"] = [dict(zip(("rel_diff", "category", "quantity", "truth", "ours"), w))
                               for w in sorted(worst, reverse=True)[:5]]
    return res


if __name__ == "__main__":
    out = sys.argv[1]
    results = [check(*a.split("=", 2)) for a in sys.argv[2:]]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, ensure_ascii=False)
    for r in results:
        print(r["model"], {q: (v.get("within_1pct_of_matched"), v.get("total_diff_pct")) for q, v in r["quantities"].items()})
