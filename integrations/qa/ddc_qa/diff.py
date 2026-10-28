"""Model diff: match by UniqueId (fallback ElementId), report added / removed / changed."""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

from .model import Model, ID_COLS, eid

POS_TOL = 1e-3     # metres; GLB positions are float32
VOL_REL_TOL = 1e-3
NUM_TOL = 1e-6


def _norm(v):
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return None
    if isinstance(v, bool):
        return int(v)
    return v


def values_equal(a, b):
    a, b = _norm(a), _norm(b)
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= NUM_TOL + 1e-9 * max(abs(a), abs(b))
    return str(a) == str(b)


@dataclass
class GeomChange:
    moved: bool = False
    resized: bool = False
    shift: tuple = (0.0, 0.0, 0.0)       # centre shift, metres (scene axes)
    size_old: tuple = ()
    size_new: tuple = ()
    volume_old: float = 0.0
    volume_new: float = 0.0
    tris_old: int = 0
    tris_new: int = 0
    note: str = ""

    @property
    def volume_delta(self):
        return self.volume_new - self.volume_old


@dataclass
class Change:
    old: dict
    new: dict
    params: list = field(default_factory=list)   # (column, old, new)
    geom: GeomChange | None = None


@dataclass
class DiffResult:
    added: list
    removed: list
    changed: list
    unchanged: int
    matched_by_id: int = 0

    def summary(self):
        return {"added": len(self.added), "removed": len(self.removed), "changed": len(self.changed),
                "unchanged": self.unchanged}

    def param_edits(self):
        """Set of (ElementId, column, new value as str) for easy exact assertions."""
        return {(str(c.new.get("ElementId")), p, None if n is None else str(n)) for c in self.changed for p, o, n in c.params}


def _geom(mo, mn):
    if mo is None and mn is None:
        return None
    g = GeomChange()
    if mo is None or mn is None:
        g.note = "geometry added" if mo is None else "geometry removed"
        m = mn if mo is None else mo
        g.tris_old = 0 if mo is None else len(mo.tris)
        g.tris_new = 0 if mn is None else len(mn.tris)
        g.volume_old = 0.0 if mo is None else mo.volume()
        g.volume_new = 0.0 if mn is None else mn.volume()
        s = tuple((m.bbox()[1] - m.bbox()[0]).round(4))
        g.size_old, g.size_new = (s, s)
        return g
    (lo0, hi0), (lo1, hi1) = mo.bbox(), mn.bbox()
    s0, s1 = hi0 - lo0, hi1 - lo1
    c0, c1 = (lo0 + hi0) / 2, (lo1 + hi1) / 2
    g.size_old, g.size_new = tuple(s0.round(4)), tuple(s1.round(4))
    g.shift = tuple((c1 - c0).round(4))
    g.resized = bool(np.any(np.abs(s1 - s0) > POS_TOL))
    g.moved = bool(np.any(np.abs(c1 - c0) > POS_TOL))
    g.tris_old, g.tris_new = len(mo.tris), len(mn.tris)
    g.volume_old, g.volume_new = mo.volume(), mn.volume()
    vd = abs(g.volume_new - g.volume_old)
    vol_changed = vd > VOL_REL_TOL * max(g.volume_old, g.volume_new, 1e-9) and vd > 1e-6
    if not (g.moved or g.resized or vol_changed or g.tris_old != g.tris_new):
        return None
    return g


def diff_models(old: Model, new: Model) -> DiffResult:
    cols = [h for h in dict.fromkeys(list(old.headers) + list(new.headers)) if h and h not in ID_COLS]
    ouid = {r["UniqueId"]: r for r in old.rows if r.get("UniqueId")}
    nuid = {r["UniqueId"]: r for r in new.rows if r.get("UniqueId")}
    pairs, used_o, used_n, by_id = [], set(), set(), 0
    for u, r in nuid.items():
        if u in ouid:
            pairs.append((ouid[u], r))
            used_o.add(id(ouid[u]))
            used_n.add(id(r))
    oid = {str(r.get("ElementId")): r for r in old.rows if id(r) not in used_o and r.get("ElementId") is not None}
    for r in new.rows:
        if id(r) in used_n or r.get("ElementId") is None:
            continue
        o = oid.get(str(r["ElementId"]))
        if o is not None and (not o.get("UniqueId") or not r.get("UniqueId")):
            pairs.append((o, r))
            used_o.add(id(o))
            used_n.add(id(r))
            by_id += 1
    added = [r for r in new.rows if id(r) not in used_n]
    removed = [r for r in old.rows if id(r) not in used_o]
    changed, same = [], 0
    for o, n in pairs:
        ps = [(c, o.get(c), n.get(c)) for c in cols if not values_equal(o.get(c), n.get(c))]
        g = _geom(old.meshes.get(eid(o)), new.meshes.get(eid(n)))
        if ps or g:
            changed.append(Change(o, n, ps, g))
        else:
            same += 1
    return DiffResult(added, removed, changed, same, by_id)
