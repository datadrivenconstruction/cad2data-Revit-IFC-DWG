"""IDS 1.0 (buildingSMART Information Delivery Specification) reader.

Supported facets: entity, attribute, property. Property sets are ignored because the element table is
flat: a property baseName is mapped to the column of the same name (exact, case-insensitive, or with a
unit suffix such as "Width (m)"). Attribute names map through ATTR_MAP. classification, material and
partOf facets are reported as unsupported (the specification is skipped, not failed).
"""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET

from .model import Model
from .rules import Finding, empty, num

ATTR_MAP = {"Name": "Type Name", "Tag": "ElementId", "GlobalId": "GlobalId", "ObjectType": "Family",
            "Description": "Description", "LongName": "Type Name"}
UNSUPPORTED = {"classification", "material", "partOf"}


def _ln(tag):
    return tag.rsplit("}", 1)[-1]


def _child(e, name):
    for c in e:
        if _ln(c.tag) == name:
            return c
    return None


def _children(e, name):
    return [c for c in e if _ln(c.tag) == name]


class Value:
    """simpleValue or xs:restriction."""

    def __init__(self, el):
        self.simple = None
        self.enum, self.pats, self.lo, self.hi, self.length = [], [], None, None, {}
        if el is None:
            self.any = True
            return
        self.any = False
        sv = _child(el, "simpleValue")
        if sv is not None:
            self.simple = sv.text or ""
            return
        r = _child(el, "restriction")
        if r is None:
            self.any = True
            return
        for c in r:
            n, v = _ln(c.tag), c.get("value")
            if n == "enumeration":
                self.enum.append(v)
            elif n == "pattern":
                self.pats.append(re.compile(v))
            elif n in ("minInclusive", "minExclusive", "maxInclusive", "maxExclusive"):
                self.length[n] = float(v)
            elif n in ("length", "minLength", "maxLength"):
                self.length[n] = int(v)

    def match(self, v):
        if self.any:
            return True
        s = _s(v)
        if self.simple is not None:
            a, b = num(v), num(self.simple)
            return (a is not None and b is not None and abs(a - b) < 1e-9) or s == _s(self.simple)
        if self.enum and s not in {_s(x) for x in self.enum}:
            return False
        if self.pats and not any(p.fullmatch(s) for p in self.pats):
            return False
        L = self.length
        x = num(v)
        if any(k in L for k in ("minInclusive", "minExclusive", "maxInclusive", "maxExclusive")):
            if x is None:
                return False
            if "minInclusive" in L and x < L["minInclusive"] or "minExclusive" in L and x <= L["minExclusive"]:
                return False
            if "maxInclusive" in L and x > L["maxInclusive"] or "maxExclusive" in L and x >= L["maxExclusive"]:
                return False
        if "length" in L and len(s) != L["length"] or "minLength" in L and len(s) < L["minLength"] \
                or "maxLength" in L and len(s) > L["maxLength"]:
            return False
        return True

    def text(self):
        if self.any:
            return "any"
        if self.simple is not None:
            return repr(self.simple)
        return "restriction(%s)" % ", ".join(
            [("enum " + "|".join(self.enum))] * bool(self.enum) + [("pattern " + "|".join(p.pattern for p in self.pats))] * bool(self.pats)
            + ["%s=%s" % kv for kv in self.length.items()])


def _s(v):
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    t = str(v)
    return {"Yes": "TRUE", "No": "FALSE"}.get(t, t)


class Facet:
    def __init__(self, el, requirement=False):
        self.kind = _ln(el.tag)
        self.card = el.get("cardinality", "required") if requirement else "required"
        if self.kind == "entity":
            self.name = Value(_child(el, "name"))
        elif self.kind == "attribute":
            self.name, self.value = Value(_child(el, "name")), Value(_child(el, "value"))
        elif self.kind == "property":
            self.name, self.value = Value(_child(el, "baseName")), Value(_child(el, "value"))
        self.unsupported = self.kind in UNSUPPORTED

    def label(self):
        if self.kind == "entity":
            return "entity %s" % self.name.text()
        return "%s %s %s" % (self.kind, self.name.text(), "" if self.value.any else "= " + self.value.text())

    def columns(self, headers):
        want = self.name.simple if self.name.simple is not None else None
        if want is None:
            return [h for h in headers if h and self.name.match(h)]
        if self.kind == "attribute" and want in ATTR_MAP:
            return [ATTR_MAP[want]]
        low = want.lower()
        c = [h for h in headers if h == want] or [h for h in headers if h.lower() == low] \
            or [h for h in headers if h.lower().startswith(low + " (")]
        return c[:1] if c else [want]


class Spec:
    def __init__(self, el):
        self.name = el.get("name", "specification")
        self.description = el.get("description", "")
        a, rq = _child(el, "applicability"), _child(el, "requirements")
        self.min_occurs = int(a.get("minOccurs", "0")) if a is not None else 0
        self.applic = [Facet(f) for f in (a if a is not None else [])]
        self.reqs = [Facet(f, True) for f in (rq if rq is not None else [])]


def parse_ids(path):
    root = ET.parse(path).getroot()
    if _ln(root.tag) != "ids":
        raise ValueError("not an IDS file")
    info = _child(root, "info")
    title = (_child(info, "title").text if info is not None and _child(info, "title") is not None else "IDS")
    specs = [Spec(s) for s in _children(_child(root, "specifications"), "specification")]
    return title, specs


def is_ids(path):
    try:
        return _ln(ET.parse(path).getroot().tag) == "ids"
    except ET.ParseError:
        return False


def _match_applic(f: Facet, r, headers):
    if f.kind == "entity":
        return f.name.match(str(r.get("IfcClass") or "").upper()) or f.name.match(str(r.get("IfcClass") or ""))
    for c in f.columns(headers):
        v = r.get(c)
        if not empty(v) and f.value.match(v):
            return True
    return False


def run_ids(path, model: Model):
    title, specs = parse_ids(path)
    findings, notes = [], []
    for i, sp in enumerate(specs, 1):
        rid = "IDS-%d" % i
        if any(f.unsupported for f in sp.applic + sp.reqs):
            notes.append("%s %r skipped: unsupported facet (%s)" % (rid, sp.name, ", ".join(
                sorted({f.kind for f in sp.applic + sp.reqs if f.unsupported}))))
            continue
        app = [r for r in model.rows if sp.applic and all(_match_applic(f, r, model.headers) for f in sp.applic)]
        if len(app) < sp.min_occurs:
            findings.append(Finding(rid, sp.name, "error", "no element satisfies the applicability (minOccurs=%d)" % sp.min_occurs, {}))
        for r in app:
            for f in sp.reqs:
                cols = f.columns(model.headers)
                if f.kind == "entity":
                    ok = f.name.match(str(r.get("IfcClass") or "").upper())
                    bad = None if ok else "entity is %r, required %s" % (r.get("IfcClass"), f.name.text())
                else:
                    vals = [(c, r.get(c)) for c in cols if not empty(r.get(c))]
                    if f.card == "prohibited":
                        bad = "%s must not be set" % f.label() if any(f.value.match(v) for _, v in vals) else None
                    elif not vals:
                        bad = None if f.card == "optional" else "%s is missing or empty" % f.label()
                    elif not any(f.value.match(v) for _, v in vals):
                        bad = "%s: value %r does not match %s" % (cols[0], vals[0][1], f.value.text())
                    else:
                        bad = None
                if bad:
                    findings.append(Finding(rid, sp.name, "error", bad, r))
    return title, findings, notes
