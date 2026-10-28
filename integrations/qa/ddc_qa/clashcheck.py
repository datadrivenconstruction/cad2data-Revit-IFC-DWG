"""Independent check of clash results: surface sampling + ray-parity point-in-mesh test.

Different algorithm from the triangle-triangle test in clash.py: a pair is confirmed when sampled
surface points of one element lie inside the other element's closed volume.
"""
from __future__ import annotations
import random
import numpy as np

from .clash import points_inside
from .model import eid

def sample_surface(mesh, n, region=None, rng=None):
    rng = rng or np.random.default_rng(1)
    t = mesh.verts[mesh.tris]
    if region is not None:
        lo, hi = region
        t = t[(t.max(1) >= lo).all(1) & (t.min(1) <= hi).all(1)]
    if not len(t):
        return np.zeros((0, 3))
    area = np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1)
    if area.sum() == 0:
        return np.zeros((0, 3))
    idx = rng.choice(len(t), n, p=area / area.sum())
    u, v = rng.random((2, n))
    f = u + v > 1
    u[f], v[f] = 1 - u[f], 1 - v[f]
    T = t[idx]
    p = T[:, 0] + (T[:, 1] - T[:, 0]) * u[:, None] + (T[:, 2] - T[:, 0]) * v[:, None]
    if region is not None:
        p = p[(p >= region[0]).all(1) & (p <= region[1]).all(1)]
    return p


ORACLE_RAYS = np.array([[0.1234, -0.9321, 0.3412], [-0.8123, 0.1311, 0.5678], [0.3001, 0.4412, -0.8432], [0.6, 0.6, 0.52], [-0.4, 0.2, 0.9]])


def inside(mesh, pts):
    return points_inside(mesh, pts, ORACLE_RAYS)


def interpenetration(ma, mb, tol=0.0, n=3000):
    """Fraction-free count of sampled surface points of each mesh lying inside the other (restricted to the bbox overlap)."""
    lo = np.maximum(ma.bbox()[0], mb.bbox()[0])
    hi = np.minimum(ma.bbox()[1], mb.bbox()[1])
    reg = (lo - 1e-6, hi + 1e-6)
    pa, pb = sample_surface(ma, n, reg), sample_surface(mb, n, reg)
    ia = int(inside(mb, pa).sum()) if len(pa) else 0
    ib = int(inside(ma, pb).sum()) if len(pb) else 0
    return ia, ib, len(pa), len(pb)


def validate(model, findings, sample=20, seed=7):
    """Returns rows (finding, inside_a_in_b, inside_b_in_a, confirmed) for a random sample of findings."""
    rnd = random.Random(seed)
    pick = rnd.sample(findings, min(sample, len(findings)))
    rows = []
    for f in pick:
        ia, ib, na, nb = interpenetration(model.meshes[eid(f.element)], model.meshes[eid(f.other)])
        rows.append((f, ia, ib, na, nb, (ia + ib) > 0))
    return rows
