"""Rule engine: YAML rule sets evaluated on the element table (+ clash on GLB geometry)."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from .model import Model, eid

GUID_COLS = ("GlobalId", "IfcGUID", "IfcGuid")
SEV_ORDER = {"error": 0, "warning": 1, "info": 2}


@dataclass
class Finding:
    rule_id: str
    title: str
    severity: str
    message: str
    element: dict
    other: dict | None = None
    point: tuple | None = None       # scene coordinates (Y-up, metres)
    extra: dict = field(default_factory=dict)

    @property
    def element_id(self):
        return self.element.get("ElementId")

    @staticmethod
    def guid_of(r):
        for c in GUID_COLS:
            if r and r.get(c):
                return r[c]
        return None


def empty(v):
    return v is None or (isinstance(v, str) and v.strip() in ("", "<None>", "None"))


def cats(spec):
    if spec in (None, "*", ["*"]):
        return None
    if isinstance(spec, str):
        spec = [spec]
    return {s.lower() for s in spec}


def in_cats(r, cs, excl=None):
    c = str(r.get("Category") or "").lower()
    if excl and c in excl:
        return False
    return cs is None or c in cs


def num(v):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", ".").strip())
    except ValueError:
        return None


def load_rules(path):
    d = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(d, dict) or "rules" not in d:
        raise ValueError("rule file needs a top-level 'rules' list: %s" % path)
    return d


def _f(rule, r, msg, **kw):
    return Finding(rule.get("id", rule["type"]), rule.get("title", rule["type"]), rule.get("severity", "warning"), msg, r, **kw)


def run_rule(rule, model: Model):
    t = rule["type"]
    cs = cats(rule.get("category"))
    ex = cats(rule.get("exclude_categories"))
    rows = [r for r in model.rows if in_cats(r, cs, ex)]
    out = []
    if t == "required_params":
        for r in rows:
            miss = [p for p in rule["params"] if empty(r.get(p))]
            if miss:
                out.append(_f(rule, r, "empty required parameter(s): %s" % ", ".join(miss), extra={"params": miss}))
    elif t in ("regex", "naming"):
        p = rule.get("param", "Type Name")
        rx = re.compile(rule["pattern"])
        for r in rows:
            v = r.get(p)
            if empty(v):
                if rule.get("require_value"):
                    out.append(_f(rule, r, "%s is empty" % p))
                continue
            if not rx.fullmatch(str(v)):
                out.append(_f(rule, r, "%s = %r does not match %s" % (p, v, rule["pattern"])))
    elif t == "enum":
        p = rule["param"]
        vals = [str(x) for x in rule["values"]]
        cmp = (lambda x: x) if rule.get("case_sensitive", True) else (lambda x: x.lower())
        allowed = {cmp(x) for x in vals}
        for r in rows:
            v = r.get(p)
            if empty(v):
                if rule.get("require_value"):
                    out.append(_f(rule, r, "%s is empty" % p))
                continue
            if cmp(str(v)) not in allowed:
                out.append(_f(rule, r, "%s = %r not in %s" % (p, v, vals)))
    elif t == "range":
        p = rule["param"]
        lo, hi = rule.get("min"), rule.get("max")
        for r in rows:
            v = num(r.get(p))
            if v is None:
                if rule.get("require_value") and empty(r.get(p)):
                    out.append(_f(rule, r, "%s is empty" % p))
                continue
            if (lo is not None and v < lo) or (hi is not None and v > hi):
                out.append(_f(rule, r, "%s = %g outside [%s, %s]" % (p, v, lo, hi)))
    elif t == "duplicate":
        p = rule.get("param", "Mark")
        by = rule.get("scope", "model")
        groups: dict = {}
        for r in rows:
            v = r.get(p)
            if empty(v):
                continue
            k = (str(v), r.get("Category") if by == "category" else None)
            groups.setdefault(k, []).append(r)
        for (v, _), g in groups.items():
            if len(g) > 1:
                for r in g:
                    out.append(_f(rule, r, "duplicate %s %r (%d elements)" % (p, v, len(g)), extra={"value": v, "count": len(g)}))
    elif t == "no_level":
        col = rule.get("param", "Level")
        for r in rows:
            if empty(r.get(col)):
                out.append(_f(rule, r, "element has no %s" % col))
    elif t == "clash":
        from .clash import find_clashes
        out += find_clashes(rule, model)
    else:
        raise ValueError("unknown rule type %r (rule %s)" % (t, rule.get("id")))
    return out


def run_rules(ruleset: dict, model: Model):
    res = []
    for rule in ruleset["rules"]:
        res += run_rule(rule, model)
    res.sort(key=lambda f: (SEV_ORDER.get(f.severity, 9), f.rule_id, eid(f.element) or 0))
    return res
