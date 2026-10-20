"""Own mesh boolean difference by binary space partitioning (stdlib only).

``subtract(a, b, ...)`` returns the triangles of solid A minus solid B, both given
as flat sequences of 9 floats per triangle.  The method is the classic BSP-tree
polygon clipping: every polygon of A inside B is removed, every polygon of B
inside A is kept with its orientation reversed (the walls of the cut).  The
trees are built and walked iteratively (no recursion limit).  A work budget
bounds the time spent; when it is exceeded ``CsgBudget`` is raised and the
caller keeps A unchanged and counts the case.

Inputs are expected to be closed, consistently oriented meshes (outward
normals); open or inconsistent meshes give a result that is still bounded by A
but may keep or drop extra faces.
"""
import math
from array import array

COPLANAR, FRONT, BACK, SPANNING = 0, 1, 2, 3
DEFAULT_BUDGET = 3_000_000


class CsgBudget(RuntimeError):
    pass


class _Ctx:
    __slots__ = ('eps', 'work', 'budget')

    def __init__(self, eps, budget):
        self.eps = eps; self.work = 0; self.budget = budget

    def tick(self, n=1):
        self.work += n
        if self.work > self.budget:
            raise CsgBudget('CSG_WORK_BUDGET_EXCEEDED')


def _plane(pts):
    # Newell normal: robust for slightly non-planar polygons
    nx = ny = nz = 0.0
    k = len(pts)
    for i in range(k):
        c = pts[i]; d = pts[(i + 1) % k]
        nx += (c[1] - d[1]) * (c[2] + d[2]); ny += (c[2] - d[2]) * (c[0] + d[0]); nz += (c[0] - d[0]) * (c[1] + d[1])
    L = math.sqrt(nx * nx + ny * ny + nz * nz)
    if L == 0:
        return None
    n = (nx / L, ny / L, nz / L)
    w = sum(n[0] * p[0] + n[1] * p[1] + n[2] * p[2] for p in pts) / k
    return (n, w)


class _Poly:
    __slots__ = ('pts', 'plane')

    def __init__(self, pts, plane):
        self.pts = pts; self.plane = plane

    def flipped(self):
        n, w = self.plane
        return _Poly(self.pts[::-1], ((-n[0], -n[1], -n[2]), -w))


def _split(plane, poly, cf, cb, front, back, ctx):
    n, w = plane
    eps = ctx.eps
    types = []
    ptype = 0
    for p in poly.pts:
        t = n[0] * p[0] + n[1] * p[1] + n[2] * p[2] - w
        ty = BACK if t < -eps else FRONT if t > eps else COPLANAR
        ptype |= ty
        types.append((ty, t))
    ctx.tick(len(poly.pts))
    if ptype == COPLANAR:
        pn = poly.plane[0]
        (cf if n[0] * pn[0] + n[1] * pn[1] + n[2] * pn[2] > 0 else cb).append(poly)
    elif ptype == FRONT:
        front.append(poly)
    elif ptype == BACK:
        back.append(poly)
    else:
        f = []; b = []
        pts = poly.pts; k = len(pts)
        for i in range(k):
            j = (i + 1) % k
            ti, di = types[i]; tj, dj = types[j]
            vi = pts[i]
            if ti != BACK:
                f.append(vi)
            if ti != FRONT:
                b.append(vi)
            if (ti | tj) == SPANNING:
                t = di / (di - dj)
                vj = pts[j]
                v = (vi[0] + (vj[0] - vi[0]) * t, vi[1] + (vj[1] - vi[1]) * t, vi[2] + (vj[2] - vi[2]) * t)
                f.append(v); b.append(v)
        if len(f) >= 3:
            front.append(_Poly(f, poly.plane))
        if len(b) >= 3:
            back.append(_Poly(b, poly.plane))


class _Node:
    __slots__ = ('plane', 'front', 'back', 'polys')

    def __init__(self):
        self.plane = None; self.front = None; self.back = None; self.polys = []

    def nodes(self):
        stack = [self]
        while stack:
            nd = stack.pop()
            yield nd
            if nd.front is not None:
                stack.append(nd.front)
            if nd.back is not None:
                stack.append(nd.back)

    def build(self, polys, ctx):
        stack = [(self, polys)]
        while stack:
            nd, ps = stack.pop()
            if not ps:
                continue
            if nd.plane is None:
                nd.plane = ps[0].plane
            front = []; back = []
            for p in ps:
                _split(nd.plane, p, nd.polys, nd.polys, front, back, ctx)
            if front:
                if nd.front is None:
                    nd.front = _Node()
                stack.append((nd.front, front))
            if back:
                if nd.back is None:
                    nd.back = _Node()
                stack.append((nd.back, back))

    def invert(self):
        for nd in self.nodes():
            nd.polys = [p.flipped() for p in nd.polys]
            if nd.plane is not None:
                n, w = nd.plane
                nd.plane = ((-n[0], -n[1], -n[2]), -w)
            nd.front, nd.back = nd.back, nd.front

    def clip_polygons(self, polys, ctx):
        result = []
        stack = [(self, polys)]
        while stack:
            nd, ps = stack.pop()
            if nd.plane is None:
                result.extend(ps)
                continue
            front = []; back = []
            for p in ps:
                _split(nd.plane, p, front, back, front, back, ctx)
            if nd.front is not None:
                stack.append((nd.front, front))
            else:
                result.extend(front)
            if nd.back is not None:
                stack.append((nd.back, back))
        return result

    def clip_to(self, other, ctx):
        for nd in self.nodes():
            nd.polys = other.clip_polygons(nd.polys, ctx)

    def all_polygons(self):
        out = []
        for nd in self.nodes():
            out.extend(nd.polys)
        return out


def _polys(tris):
    out = []
    for k in range(0, len(tris) - 8, 9):
        pts = [(tris[k], tris[k + 1], tris[k + 2]), (tris[k + 3], tris[k + 4], tris[k + 5]),
               (tris[k + 6], tris[k + 7], tris[k + 8])]
        pl = _plane(pts)
        if pl is not None:
            out.append(_Poly(pts, pl))
    return out


def bbox(tris):
    return ([min(tris[k::3]) for k in range(3)], [max(tris[k::3]) for k in range(3)])


def boxes_overlap(a, b, eps=0.0):
    return all(a[0][k] <= b[1][k] + eps and b[0][k] <= a[1][k] + eps for k in range(3))


def subtract(a, b, eps=None, budget=DEFAULT_BUDGET):
    """Triangles of A minus B (flat float arrays); raises CsgBudget above the work budget."""
    if not a:
        return array('d')
    if not b:
        return array('d', a)
    ba, bb = bbox(a), bbox(b)
    if eps is None:
        size = max(max(abs(v) for v in ba[0] + ba[1]), max(bb[1][k] - bb[0][k] for k in range(3)), 1e-9)
        eps = 1e-9 * max(1.0, size) + 1e-7 * max(ba[1][k] - ba[0][k] for k in range(3))
    if not boxes_overlap(ba, bb, eps):
        return array('d', a)
    ctx = _Ctx(eps, budget)
    pa = _polys(a); pb = _polys(b)
    A = _Node(); A.build(pa, ctx)
    B = _Node(); B.build(pb, ctx)
    A.invert(); A.clip_to(B, ctx); B.clip_to(A, ctx); B.invert(); B.clip_to(A, ctx); B.invert()
    A.build(B.all_polygons(), ctx); A.invert()
    out = array('d')
    for p in A.all_polygons():
        pts = p.pts
        for i in range(1, len(pts) - 1):
            out.extend(pts[0]); out.extend(pts[i]); out.extend(pts[i + 1])
    return out
