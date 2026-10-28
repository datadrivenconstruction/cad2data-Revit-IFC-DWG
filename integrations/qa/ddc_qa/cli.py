"""ddc-qa command line: diff and check."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

RULES_DIR = Path(__file__).parent / "rules"


def cmd_diff(a):
    from .diff import diff_models
    from .diffreport import write_all
    from .model import load_model
    old, new = load_model(a.old, a.cache), load_model(a.new, a.cache)
    d = diff_models(old, new)
    out = Path(a.out or "diff_%s_vs_%s" % (Path(a.old).stem, Path(a.new).stem))
    write_all(d, old, new, out, Path(a.old).name, Path(a.new).name)
    print("added %(added)d, removed %(removed)d, changed %(changed)d, unchanged %(unchanged)d -> %(o)s" % {**d.summary(), "o": out})
    return 0


def cmd_check(a):
    from . import bcf, checkreport
    from .ids import is_ids, run_ids
    from .model import load_model
    from .rules import SEV_ORDER, load_rules, run_rules
    model = load_model(a.model, a.cache)
    findings, notes = [], []
    for rp in a.rules:
        p = Path(rp)
        if not p.exists() and (RULES_DIR / (rp + ".yaml")).exists():
            p = RULES_DIR / (rp + ".yaml")
        if p.suffix.lower() in (".ids", ".xml") or is_ids(p):
            t, f, n = run_ids(p, model)
            findings += f
            notes += n
        else:
            findings += run_rules(load_rules(p), model)
    findings.sort(key=lambda f: (SEV_ORDER.get(f.severity, 9), f.rule_id))
    out = Path(a.out or "check_%s" % Path(a.model).stem)
    out.mkdir(parents=True, exist_ok=True)
    checkreport.write_xlsx(findings, out / "check.xlsx", notes)
    checkreport.write_html(findings, out / "check.html", Path(a.model).name, notes)
    nb = bcf.write_bcf(findings, out / "issues.bcfzip", Path(a.model).name, meshes=model.meshes, max_topics=a.bcf_max)
    print("%d findings (%d BCF topics) -> %s" % (len(findings), nb, out))
    for n in notes:
        print("note:", n)
    return 1 if (a.fail_on and any(SEV_ORDER.get(f.severity, 9) <= SEV_ORDER[a.fail_on] for f in findings)) else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="ddc-qa", description=__doc__)
    ap.add_argument("--cache", help="conversion cache folder (default: %%TEMP%%/ddc-qa-cache)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    d = sp.add_parser("diff", help="diff two models (.rvt, *.converted folder or elements.xlsx)")
    d.add_argument("old")
    d.add_argument("new")
    d.add_argument("-o", "--out")
    d.set_defaults(fn=cmd_diff)
    c = sp.add_parser("check", help="check a model against rule files (YAML or IDS 1.0 XML)")
    c.add_argument("model")
    c.add_argument("--rules", nargs="+", required=True, help="rules.yaml, ids file, or a bundled name: architecture, mep, data_quality")
    c.add_argument("-o", "--out")
    c.add_argument("--bcf-max", type=int, default=1000)
    c.add_argument("--fail-on", choices=["error", "warning", "info"], help="exit 1 when a finding of this severity or worse exists")
    c.set_defaults(fn=cmd_check)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
