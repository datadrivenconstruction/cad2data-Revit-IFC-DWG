"""Template-driven reports: filters, group-by, aggregates, columns, sort, unit conversion."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import pandas as pd

from . import units as U
from .frame import Frame

AGG = {"sum", "mean", "min", "max", "count", "nunique", "median", "first"}
NUMERIC_AGG = {"sum", "mean", "min", "max", "median"}
OPS = {"eq", "ne", "in", "not_in", "gt", "ge", "lt", "le", "contains", "matches", "notnull", "isnull"}


class TemplateError(ValueError):
    pass


@dataclass
class Section:
    title: str
    df: pd.DataFrame
    units: dict = field(default_factory=dict)
    formats: dict = field(default_factory=dict)
    totals: dict = field(default_factory=dict)
    note: str = ""


@dataclass
class Report:
    name: str
    description: str
    source: str
    sections: list


def load_template(path_or_name: str) -> dict:
    from .builtin import BUILTIN

    if path_or_name in BUILTIN:
        return BUILTIN[path_or_name]
    with open(path_or_name, encoding="utf-8") as f:
        text = f.read()
    if path_or_name.lower().endswith(".json"):
        t = json.loads(text)
    else:
        import yaml

        t = yaml.safe_load(text)
    if not isinstance(t, dict):
        raise TemplateError("template must be a mapping")
    return t


def _mask(df: pd.DataFrame, f: dict) -> pd.Series:
    col = f.get("column")
    ops = [k for k in f if k in OPS]
    if len(ops) != 1:
        raise TemplateError(f"filter on {col!r} needs exactly one operator from {sorted(OPS)}")
    op, v = ops[0], f[ops[0]]
    if col not in df.columns:
        # missing column: only negative tests can pass
        keep = op in ("ne", "not_in") or (op == "isnull" and v) or (op == "notnull" and not v)
        return pd.Series(keep, index=df.index)
    s = df[col]
    if op == "eq":
        return (s == v).fillna(False)
    if op == "ne":
        return (s != v).fillna(True)
    if op == "in":
        return s.isin(v)
    if op == "not_in":
        return ~s.isin(v)
    if op == "notnull":
        return s.notna() if v else s.isna()
    if op == "isnull":
        return s.isna() if v else s.notna()
    if op in ("contains", "matches"):
        st = s.astype("string")
        m = st.str.contains(str(v), case=False, regex=False) if op == "contains" \
            else st.str.contains(str(v), flags=re.I, regex=True)
        return m.fillna(False).astype(bool)
    num = pd.to_numeric(s, errors="coerce")
    return {"gt": num > v, "ge": num >= v, "lt": num < v, "le": num <= v}[op].fillna(False)


def apply_filters(df: pd.DataFrame, filters) -> pd.DataFrame:
    for f in filters or []:
        df = df[_mask(df, f)]
    return df


def _convert(df, units, conv):
    for col, dst in (conv or {}).items():
        if col in df.columns and col in units:
            df[col] = pd.to_numeric(df[col], errors="coerce") * U.factor(units[col], dst)
            units[col] = U.norm(dst)


def _sort(df, spec):
    keys, asc = [], []
    for s in spec or []:
        if isinstance(s, dict):
            by, desc = s["by"], bool(s.get("desc"))
        else:
            by, desc = (str(s)[1:], True) if str(s).startswith("-") else (str(s), False)
        if by in df.columns:
            keys.append(by)
            asc.append(not desc)
    return df.sort_values(keys, ascending=asc, kind="stable") if keys else df


def _fill_rate(df: pd.DataFrame, sec: dict) -> list:
    df = df.drop(columns=["CategoryEn"], errors="ignore")
    grp = (sec.get("group_by") or ["Category"])[0]
    keys = df[grp].astype("object").where(df[grp].notna(), "(none)")
    params = [c for c in df.columns if c != grp]
    filled = pd.DataFrame({c: df[c].notna() & (df[c].astype("string").str.strip() != "").fillna(False)
                           for c in params})
    rows = []
    for key, idx in filled.groupby(keys).groups.items():
        n = len(idx)
        sums = filled.loc[idx].sum()
        for c in params:
            k = int(sums[c])
            if k or sec.get("include_empty"):
                rows.append((key, c, k, n, k / n))
    by_cat = pd.DataFrame(rows, columns=[grp, "Parameter", "Filled", "Total", "Fill rate"])
    by_cat = _sort(by_cat, sec.get("sort") or [grp, "-Fill rate"]).reset_index(drop=True)
    tot = len(df)
    overall = pd.DataFrame({"Parameter": params, "Filled": [int(filled[c].sum()) for c in params]})
    overall["Total"] = tot
    overall["Fill rate"] = overall["Filled"] / tot if tot else 0.0
    overall = overall.sort_values("Fill rate", ascending=False, kind="stable").reset_index(drop=True)
    fm = {"Fill rate": "pct", "Filled": "int", "Total": "int"}
    return [Section(sec.get("title", "Fill rate by category"), by_cat, formats=fm),
            Section("Fill rate overall", overall, formats=fm)]


def run_section(fr: Frame, sec: dict, base_filters=None) -> list:
    title = sec.get("title") or "Report"
    df = apply_filters(fr.df, list(base_filters or []) + list(sec.get("filters") or []))
    units = dict(fr.units)
    if sec.get("kind") == "fill_rate":
        return _fill_rate(df, sec)
    wanted_gb = list(sec.get("group_by") or [])
    gb = [c for c in wanted_gb if c in df.columns]
    missing = [c for c in wanted_gb if c not in df.columns]
    aggs = sec.get("aggregates") or []
    fmts: dict = {}
    if gb or aggs:
        df = df.copy()
        spec, out_units = {}, {}
        for a in aggs:
            fn, col = a.get("fn", "sum"), a.get("column")
            if fn not in AGG:
                raise TemplateError(f"unknown aggregate {fn!r}; use one of {sorted(AGG)}")
            name = a.get("as") or (f"{fn}_{col}" if col else "Count")
            if fn == "count" and not col:
                df["__one"] = 1
                spec[name] = ("__one", "count")
                fmts[name] = "int"
            elif col in df.columns:
                if fn in NUMERIC_AGG:
                    df[f"__n_{col}"] = pd.to_numeric(df[col], errors="coerce")
                    spec[name] = (f"__n_{col}", fn)
                    if col in units:
                        out_units[name] = units[col]
                else:
                    spec[name] = (col, fn)
                    if fn in ("count", "nunique"):
                        fmts[name] = "int"
            else:
                missing.append(col)
        for g in gb:
            df[g] = df[g].astype("object").where(df[g].notna(), "(none)")
        if gb:
            out = df.groupby(gb, sort=True).agg(**spec).reset_index() if spec \
                else df[gb].drop_duplicates().reset_index(drop=True)
        else:
            df["__g"] = 0
            out = df.groupby("__g").agg(**spec).reset_index(drop=True) if len(df) else \
                pd.DataFrame({k: [0 if f in ("sum", "count", "nunique") else None] for k, (_, f) in spec.items()})
        units = out_units
    else:
        out = df.drop(columns=[c for c in df.columns if c.startswith("__")])
        cols = sec.get("columns")
        if cols:
            sel, ren = [], {}
            for c in cols:
                src, as_ = (c, c) if isinstance(c, str) else (c["column"], c.get("as", c["column"]))
                if src in out.columns:
                    sel.append(src)
                    ren[src] = as_
                else:
                    missing.append(src)
            out = out[sel].rename(columns=ren)
            units = {ren[k]: v for k, v in units.items() if k in ren}
        else:
            out = out.drop(columns=["CategoryEn"], errors="ignore")
    out = out.copy()
    _convert(out, units, sec.get("convert"))
    out = apply_filters(out, sec.get("having"))
    out = _sort(out, sec.get("sort"))
    if sec.get("columns") and (gb or aggs):
        keep = [c if isinstance(c, str) else c.get("as", c["column"]) for c in sec["columns"]]
        out = out[[c for c in keep if c in out.columns]]
    if sec.get("limit"):
        out = out.head(int(sec["limit"]))
    out = out.reset_index(drop=True)
    totals = {}
    if sec.get("totals", bool(gb)) and len(out):
        for c in out.columns:
            if c in units or fmts.get(c) == "int":
                totals[c] = float(pd.to_numeric(out[c], errors="coerce").sum())
    note = f"Missing columns ignored: {', '.join(sorted(set(map(str, missing))))}" if missing else ""
    return [Section(title, out, units, fmts, totals, note)]


def run_template(tpl: dict, fr: Frame) -> Report:
    secs = tpl.get("sections")
    out: list = []
    if secs:
        for s in secs:
            out += run_section(fr, s, tpl.get("filters"))
    else:
        out += run_section(fr, tpl)
    return Report(tpl.get("name", "Report"), tpl.get("description", ""), fr.source, out)
