"""Clash detection: bbox overlap with tolerance, refined by triangle-mesh intersection (numpy)."""
from __future__ import annotations
import numpy as np

from .model import eid

EPS = 1e-9


def _segment_on_plane(V, d, n_dir, o_pt):
    """Per triangle (N,3,3) with signed plane distances d (N,3): min/max of the triangle's
    intersection with the plane projected on direction n_dir (N,3). Returns lo, hi, ok."""
    N = len(V)
    big = np.inf
    lo = np.full(N, big)
    hi = np.full(N, -big)
    cnt = np.zeros(N, int)
    for i, j in ((0, 1), (1, 2), (2, 0)):
        di, dj = d[:, i], d[:, j]
        cross = (di * dj) < 0
        t = np.where(cross, di / np.where(cross, di - dj, 1.0), 0.0)
        p = V[:, i] + (V[:, j] - V[:, i]) * t[:, None]
        s = np.einsum("ij,ij->i", p - o_pt, n_dir)
        lo = np.where(cross, np.minimum(lo, s), lo)
        hi = np.where(cross, np.maximum(hi, s), hi)
        cnt += cross
    for i in range(3):
        on = np.abs(d[:, i]) <= EPS
        s = np.einsum("ij,ij->i", V[:, i] - o_pt, n_dir)
        lo = np.where(on, np.minimum(lo, s), lo)
        hi = np.where(on, np.maximum(hi, s), hi)
        cnt += on
    return lo, hi, cnt >= 2


def tri_tri_intersect(A, B, eps=1e-7):
    """A,B: (N,3,3) triangle pairs. True where the triangles cross with a segment of positive length
    (coplanar and grazing contacts are not counted)."""
    n1 = np.cross(A[:, 1] - A[:, 0], A[:, 2] - A[:, 0])
    n2 = np.cross(B[:, 1] - B[:, 0], B[:, 2] - B[:, 0])
    l1 = np.linalg.norm(n1, axis=1)
    l2 = np.linalg.norm(n2, axis=1)
    ok = (l1 > 1e-12) & (l2 > 1e-12)
    n1 = n1 / np.where(l1 > 0, l1, 1)[:, None]
    n2 = n2 / np.where(l2 > 0, l2, 1)[:, None]
    dB = np.einsum("nj,nkj->nk", n1, B - A[:, :1])      # B verts to plane A
    dA = np.einsum("nj,nkj->nk", n2, A - B[:, :1])      # A verts to plane B
    dB[np.abs(dB) < eps] = 0.0
    dA[np.abs(dA) < eps] = 0.0
    ok &= ~((dB > 0).all(1) | (dB < 0).all(1) | (dA > 0).all(1) | (dA < 0).all(1))
    ok &= ~((dA == 0).all(1) | (dB == 0).all(1))      # coplanar
    L = np.cross(n1, n2)
    ll = np.linalg.norm(L, axis=1)
    ok &= ll > 1e-12
    L = L / np.where(ll > 0, ll, 1)[:, None]
    o = A[:, 0]
    loA, hiA, okA = _segment_on_plane(A, dA, L, o)
    loB, hiB, okB = _segment_on_plane(B, dB, L, o)
    ok &= okA & okB
    ov = np.minimum(hiA, hiB) - np.maximum(loA, loB)
    return ok & (ov > eps)


def mesh_intersect(ma, mb, region=None, max_pairs=4_000_000, chunk=512):
    """Number of intersecting triangle pairs between two meshes (restricted to a region box)."""
    ta, tb = ma.verts[ma.tris], mb.verts[mb.tris]
    if region is not None:
        lo, hi = region
        ta = ta[(ta.max(1) >= lo).all(1) & (ta.min(1) <= hi).all(1)]
        tb = tb[(tb.max(1) >= lo).all(1) & (tb.min(1) <= hi).all(1)]
    if not len(ta) or not len(tb):
        return 0
    amin, amax, bmin, bmax = ta.min(1), ta.max(1), tb.min(1), tb.max(1)
    hits, seen = 0, 0
    for s in range(0, len(ta), chunk):
        sl = slice(s, s + chunk)
        m = ((amin[sl, None] <= bmax[None]) & (amax[sl, None] >= bmin[None])).all(-1)
        ia, ib = np.nonzero(m)
        seen += len(ia)
        if seen > max_pairs:
            break
        if len(ia):
            hits += int(tri_tri_intersect(ta[sl][ia], tb[ib]).sum())
    return hits


ENGINE_RAYS = np.array([[0.5773, 0.3011, 0.7599], [-0.2113, 0.8123, -0.5431], [0.7071, -0.6013, 0.3691]])


def points_inside(mesh, pts, rays=ENGINE_RAYS, chunk=400):
    """Ray-parity point-in-mesh (Moller-Trumbore), majority vote over several oblique rays."""
    T = mesh.verts[mesh.tris]
    v0, e1, e2 = T[:, 0], T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
    votes = np.zeros(len(pts), int)
    for ray in rays / np.linalg.norm(rays, axis=1)[:, None]:
        h = np.cross(ray, e2)
        a = np.einsum("tj,tj->t", e1, h)
        ok = np.abs(a) > 1e-12
        sa = np.where(ok, a, 1)
        for s in range(0, len(pts), chunk):
            sv = pts[s:s + chunk, None, :] - v0[None]
            u = np.einsum("ptj,tj->pt", sv, h) / sa
            q = np.cross(sv, e1[None])
            v = np.einsum("j,ptj->pt", ray, q) / sa
            t = np.einsum("tj,ptj->pt", e2, q) / sa
            votes[s:s + chunk] += ((ok[None] & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-9)).sum(1) % 2 == 1)
    return votes * 2 > len(rays)


def contained(ma, mb, region, margin, max_pts=300):
    """True when vertices of one mesh (inside the overlap region) lie inside the other mesh by majority ray vote."""
    lo, hi = region
    for m, o in ((ma, mb), (mb, ma)):
        v = m.verts[(m.verts >= lo + margin).all(1) & (m.verts <= hi - margin).all(1)] if (hi - lo > 2 * margin).all() else m.verts[:0]
        if len(v) > max_pts:
            v = v[np.linspace(0, len(v) - 1, max_pts).astype(int)]
        if len(v) and points_inside(o, v).any():
            return True
    return False


def find_clashes(rule, model):
    from .rules import Finding, cats, in_cats
    ca, cb = cats(rule.get("a")), cats(rule.get("b"))
    tol = float(rule.get("tolerance", 0.01))
    refine = rule.get("refine", True)
    rows = {eid(r): r for r in model.rows if eid(r) in model.meshes}
    A = [(k, r) for k, r in rows.items() if in_cats(r, ca)]
    B = [(k, r) for k, r in rows.items() if in_cats(r, cb)]
    if not A or not B:
        return []
    bb = {k: model.meshes[k].bbox() for k, _ in A + B}
    loA = np.array([bb[k][0] for k, _ in A]); hiA = np.array([bb[k][1] for k, _ in A])
    loB = np.array([bb[k][0] for k, _ in B]); hiB = np.array([bb[k][1] for k, _ in B])
    same = ca == cb
    out = []
    for s in range(0, len(A), 256):
        ov = np.minimum(hiA[s:s + 256, None], hiB[None]) - np.maximum(loA[s:s + 256, None], loB[None])
        ia, ib = np.nonzero((ov > tol).all(-1))
        for i, j in zip(ia + s, ib):
            ka, kb = A[i][0], B[j][0]
            if ka == kb or (same and ka > kb):
                continue
            lo = np.maximum(loA[i], loB[j]); hi = np.minimum(hiA[i], hiB[j])
            hits = None
            if refine:
                hits = mesh_intersect(model.meshes[ka], model.meshes[kb], (lo - tol, hi + tol))
                if hits == 0:
                    if not (rule.get("containment", True) and contained(model.meshes[ka], model.meshes[kb], (lo, hi), 0.0)):
                        continue
                    hits = 0
            ra, rb = A[i][1], B[j][1]
            depth = tuple(float(x) for x in (hi - lo))
            msg = "%s %s clashes with %s %s (bbox overlap %.3f x %.3f x %.3f m%s)" % (
                ra.get("Category"), ka, rb.get("Category"), kb, *depth,
                (", %d triangle pairs intersect" % hits if hits else ", one element lies inside the other") if hits is not None else "")
            out.append(Finding(rule.get("id", "clash"), rule.get("title", "Clash"), rule.get("severity", "error"), msg,
                               ra, rb, tuple(((lo + hi) / 2).tolist()), {"overlap": depth, "tri_pairs": hits}))
    return out
