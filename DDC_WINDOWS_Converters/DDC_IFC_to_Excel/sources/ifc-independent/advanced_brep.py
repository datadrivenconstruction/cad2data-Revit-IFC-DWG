"""Own tessellation of IFC4 advanced boundary representations (stdlib only).

IfcAdvancedBrep / IfcAdvancedBrepWithVoids (outer shell) and IfcFaceSurface /
IfcAdvancedFace bounded by IfcEdgeLoop or IfcPolyLoop:

* edges: IfcEdgeCurve over IfcLine, IfcPolyline, IfcCircle, IfcEllipse,
  IfcTrimmedCurve of those, IfcBSplineCurveWithKnots and its rational form,
  IfcCompositeCurve; the edge runs between its vertex points (SameSense and the
  oriented-edge flag are honoured);
* faces: IfcPlane (exact polygon with holes), IfcCylindricalSurface,
  IfcConicalSurface, IfcSphericalSurface, IfcToroidalSurface,
  IfcSurfaceOfRevolution, IfcSurfaceOfLinearExtrusion,
  IfcBSplineSurfaceWithKnots and IfcRationalBSplineSurfaceWithKnots.  A curved
  face is trimmed by its loops in the surface parameter plane, triangulated
  there piece by piece after cutting it along a grid of one tessellation step
  per curved direction (shared cut points, no cracks), then mapped onto the surface.
  A face whose loops wrap a periodic direction (a full pipe band) is meshed as
  a band between its two boundary loops.

Faces that cannot be meshed are skipped and counted in ``stats``
('approx:advanced_face_skipped:<reason>'); an item none of whose faces meshes
raises ``Refused``.
"""
import math

import geometry as G

TWO_PI = 2 * math.pi
MAX_FACE_TRIANGLES = 20000
BSPLINE_GRID = 16


# ----------------------------------------------------------------------- small helpers

def inv_rigid(m):
    """Inverse of an orthonormal placement matrix (rotation + translation)."""
    r = (m[0], m[4], m[8], m[1], m[5], m[9], m[2], m[6], m[10])
    t = (m[3], m[7], m[11])
    tx = -(r[0] * t[0] + r[1] * t[1] + r[2] * t[2])
    ty = -(r[3] * t[0] + r[4] * t[1] + r[5] * t[2])
    tz = -(r[6] * t[0] + r[7] * t[1] + r[8] * t[2])
    return (r[0], r[1], r[2], tx, r[3], r[4], r[5], ty, r[6], r[7], r[8], tz, 0.0, 0.0, 0.0, 1.0)


def _lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _flag(v):
    """IFC boolean/logical value -> bool (unknown/None -> True)."""
    if v is None:
        return True
    if isinstance(v, bool):
        return v
    s = str(v).strip('.').upper()
    return s not in ('F', 'FALSE')


def _num(v):
    return float(v.wrappedValue if hasattr(v, 'wrappedValue') else v)


# ----------------------------------------------------------------------- NURBS (own de Boor)

def expand_knots(mults, knots):
    out = []
    for k, n in zip(knots, mults):
        out.extend([_num(k)] * int(n))
    return out


def _deboor(deg, P, U, t):
    """Point of a (homogeneous) B-spline with control tuples P and full knot vector U."""
    n = len(P) - 1
    lo, hi = U[deg], U[n + 1]
    t = min(max(t, lo), hi)
    k = deg
    while k < n and U[k + 1] <= t:
        k += 1
    d = [list(P[j]) for j in range(k - deg, k + 1)]
    for r in range(1, deg + 1):
        for j in range(deg, r - 1, -1):
            i = j + k - deg
            den = U[i + deg - r + 1] - U[i]
            a = (t - U[i]) / den if den else 0.0
            d[j] = [(1 - a) * x + a * y for x, y in zip(d[j - 1], d[j])]
    return d[deg]


class BSplineCurve:
    def __init__(self, c):
        self.deg = int(c.Attr1 if not hasattr(c, 'Degree') else c.Degree)
        pts = [G.coords(p) for p in c.ControlPointsList]
        w = [_num(x) for x in c.WeightsData] if getattr(c, 'WeightsData', None) else [1.0] * len(pts)
        self.P = [(p[0] * wi, p[1] * wi, p[2] * wi, wi) for p, wi in zip(pts, w)]
        self.U = expand_knots(c.KnotMultiplicities, c.Knots)
        if len(self.U) != len(self.P) + self.deg + 1:
            raise G.Refused('IFC_BSPLINE_KNOTS_INCONSISTENT:' + c.is_a())
        self.lo, self.hi = self.U[self.deg], self.U[len(self.P)]

    def point(self, t):
        x, y, z, w = _deboor(self.deg, self.P, self.U, t)
        return (x / w, y / w, z / w)

    def samples(self):
        n = max(8, min(96, 4 * len(self.P)))
        return [self.point(self.lo + (self.hi - self.lo) * i / n) for i in range(n + 1)]


class BSplineSurface:
    def __init__(self, s):
        self.du, self.dv = int(s.UDegree), int(s.VDegree)
        rows = [[G.coords(p) for p in row] for row in s.ControlPointsList]
        if getattr(s, 'WeightsData', None):
            W = [[_num(x) for x in row] for row in s.WeightsData]
        else:
            W = [[1.0] * len(r) for r in rows]
        self.P = [[(p[0] * w, p[1] * w, p[2] * w, w) for p, w in zip(r, wr)] for r, wr in zip(rows, W)]
        self.U = expand_knots(s.UMultiplicities, s.UKnots)
        self.V = expand_knots(s.VMultiplicities, s.VKnots)
        if len(self.U) != len(self.P) + self.du + 1 or len(self.V) != len(self.P[0]) + self.dv + 1:
            raise G.Refused('IFC_BSPLINE_KNOTS_INCONSISTENT:' + s.is_a())
        self.u0, self.u1 = self.U[self.du], self.U[len(self.P)]
        self.v0, self.v1 = self.V[self.dv], self.V[len(self.P[0])]
        self.periodic = (False, False)
        self.step = ((self.u1 - self.u0) / BSPLINE_GRID, (self.v1 - self.v0) / BSPLINE_GRID)
        n = BSPLINE_GRID
        self.grid = [((self.u0 + (self.u1 - self.u0) * i / n, self.v0 + (self.v1 - self.v0) * j / n), None)
                     for i in range(n + 1) for j in range(n + 1)]
        self.grid = [(uv, self.eval(*uv)) for uv, _ in self.grid]

    def eval(self, u, v):
        rows = [_deboor(self.dv, row, self.V, v) for row in self.P]
        x, y, z, w = _deboor(self.du, rows, self.U, u)
        return (x / w, y / w, z / w)

    def inv(self, p):
        best = min(self.grid, key=lambda g: (g[1][0] - p[0]) ** 2 + (g[1][1] - p[1]) ** 2 + (g[1][2] - p[2]) ** 2)
        (u, v), q = best
        hu, hv = self.step
        d = math.dist(q, p)
        for _ in range(12):                      # pattern search refinement
            improved = False
            for du, dv in ((hu, 0), (-hu, 0), (0, hv), (0, -hv)):
                uu = min(max(u + du, self.u0), self.u1); vv = min(max(v + dv, self.v0), self.v1)
                dd = math.dist(self.eval(uu, vv), p)
                if dd < d:
                    u, v, d = uu, vv, dd; improved = True
            if not improved:
                hu /= 2; hv /= 2
        return (u, v)


# ----------------------------------------------------------------------- analytic surfaces

class _Placed:
    def __init__(self, position):
        self.m = G.axis2placement(position)
        self.mi = inv_rigid(self.m)

    def local(self, p):
        return G.apply(self.mi, p)


class Cylinder(_Placed):
    periodic = (True, False)

    def __init__(self, s):
        super().__init__(s.Position)
        self.r = float(s.Radius)
        self.step = (G.ARC_STEP, math.inf)

    def eval(self, u, v):
        return G.apply(self.m, (self.r * math.cos(u), self.r * math.sin(u), v))

    def inv(self, p):
        x, y, z = self.local(p)
        return (math.atan2(y, x), z)


class Cone(_Placed):
    periodic = (True, False)

    def __init__(self, s, angle_scale):
        super().__init__(s.Position)
        self.r = float(s.Radius)
        self.t = math.tan(float(s.SemiAngle) * angle_scale)
        self.step = (G.ARC_STEP, math.inf)

    def eval(self, u, v):
        r = self.r + v * self.t
        return G.apply(self.m, (r * math.cos(u), r * math.sin(u), v))

    def inv(self, p):
        x, y, z = self.local(p)
        return (math.atan2(y, x), z)


class Sphere(_Placed):
    periodic = (True, False)

    def __init__(self, s):
        super().__init__(s.Position)
        self.r = float(s.Radius)
        self.step = (G.ARC_STEP, G.ARC_STEP)

    def eval(self, u, v):
        c = math.cos(v)
        return G.apply(self.m, (self.r * c * math.cos(u), self.r * c * math.sin(u), self.r * math.sin(v)))

    def inv(self, p):
        x, y, z = self.local(p)
        return (math.atan2(y, x), math.asin(max(-1.0, min(1.0, z / self.r))))


class Torus(_Placed):
    periodic = (True, True)

    def __init__(self, s):
        super().__init__(s.Position)
        self.R = float(s.MajorRadius); self.r = float(s.MinorRadius)
        self.step = (G.ARC_STEP, G.ARC_STEP)

    def eval(self, u, v):
        rr = self.R + self.r * math.cos(v)
        return G.apply(self.m, (rr * math.cos(u), rr * math.sin(u), self.r * math.sin(v)))

    def inv(self, p):
        x, y, z = self.local(p)
        return (math.atan2(y, x), math.atan2(z, math.hypot(x, y) - self.R))


def _polyline_param(pts):
    """Cumulative chord parameter (0..n-1 by vertex index) helpers for a sampled profile."""
    return pts


class Revolution(_Placed):
    """Profile polyline (sampled, Position coordinates) revolved about an axis; v = vertex index."""
    periodic = (True, False)

    def __init__(self, s, geo):
        super().__init__(getattr(s, 'Position', None))
        prof = s.SweptCurve
        curve = getattr(prof, 'Curve', None)
        if curve is None:
            raise G.Refused('IFC_REVOLUTION_PROFILE_NOT_IMPLEMENTED:' + prof.is_a())
        pts = curve_points3d(curve, geo)
        if len(pts) < 2:
            raise G.Refused('IFC_REVOLUTION_PROFILE_DEGENERATE')
        ax = s.AxisPosition
        self.a = G.coords(ax.Location)
        self.d = G.direction(getattr(ax, 'Axis', None), (0.0, 0.0, 1.0))
        # reference radial direction from the profile point farthest from the axis
        far = max(pts, key=lambda q: self._rho(q))
        w = self._radial(far)
        if G.dot(w, w) < 1e-24:
            raise G.Refused('IFC_REVOLUTION_PROFILE_ON_AXIS')
        self.e1 = G.norm(w)
        self.e2 = G.cross(self.d, self.e1)
        # profile in the (h, rho) half plane, angle of every profile point recorded
        self.hr = []
        for q in pts:
            r = self._radial(q)
            self.hr.append((G.dot(_sub(q, self.a), self.d), math.sqrt(G.dot(r, r)),
                            math.atan2(G.dot(r, self.e2), G.dot(r, self.e1))))
        self.step = (G.ARC_STEP, 1.0)
        self.n = len(self.hr)

    def _radial(self, q):
        v = _sub(q, self.a)
        h = G.dot(v, self.d)
        return (v[0] - h * self.d[0], v[1] - h * self.d[1], v[2] - h * self.d[2])

    def _rho(self, q):
        r = self._radial(q)
        return G.dot(r, r)

    def eval(self, u, v):
        v = min(max(v, 0.0), self.n - 1.0)
        i = min(int(v), self.n - 2); t = v - i
        h0, r0, a0 = self.hr[i]; h1, r1, a1 = self.hr[i + 1]
        h = h0 + (h1 - h0) * t; r = r0 + (r1 - r0) * t; ang = u + a0 + (a1 - a0) * t
        c, s = math.cos(ang), math.sin(ang)
        p = tuple(self.a[k] + h * self.d[k] + r * (c * self.e1[k] + s * self.e2[k]) for k in range(3))
        return G.apply(self.m, p)

    def inv(self, p):
        q = self.local(p)
        r = self._radial(q)
        h = G.dot(_sub(q, self.a), self.d); rho = math.sqrt(G.dot(r, r))
        best = (math.inf, 0.0, 0.0)
        for i in range(self.n - 1):
            h0, r0, a0 = self.hr[i]; h1, r1, a1 = self.hr[i + 1]
            dh, dr = h1 - h0, r1 - r0
            L = dh * dh + dr * dr
            t = 0.0 if L == 0 else min(1.0, max(0.0, ((h - h0) * dh + (rho - r0) * dr) / L))
            d = (h0 + dh * t - h) ** 2 + (r0 + dr * t - rho) ** 2
            if d < best[0]:
                best = (d, i + t, a0 + (a1 - a0) * t)
        ang = math.atan2(G.dot(r, self.e2), G.dot(r, self.e1)) if rho > 0 else 0.0
        return (ang - best[2], best[1])


class LinearExtrusion(_Placed):
    periodic = (False, False)

    def __init__(self, s, geo):
        super().__init__(getattr(s, 'Position', None))
        curve = getattr(s.SweptCurve, 'Curve', None)
        if curve is None:
            raise G.Refused('IFC_EXTRUSION_SURFACE_PROFILE_NOT_IMPLEMENTED:' + s.SweptCurve.is_a())
        self.pts = curve_points3d(curve, geo)
        if len(self.pts) < 2:
            raise G.Refused('IFC_EXTRUSION_SURFACE_PROFILE_DEGENERATE')
        self.d = G.direction(s.ExtrudedDirection, (0.0, 0.0, 1.0))
        self.step = (1.0, math.inf)
        self.n = len(self.pts)

    def _curve(self, u):
        u = min(max(u, 0.0), self.n - 1.0)
        i = min(int(u), self.n - 2)
        return _lerp(self.pts[i], self.pts[i + 1], u - i)

    def eval(self, u, v):
        c = self._curve(u)
        return G.apply(self.m, tuple(c[k] + v * self.d[k] for k in range(3)))

    def inv(self, p):
        q = self.local(p)
        best = (math.inf, 0.0, 0.0)
        for i in range(self.n - 1):
            a, b = self.pts[i], self.pts[i + 1]
            # closest points between the line q + s*d and the segment a..b
            e = _sub(b, a); w = _sub(q, a)
            ee, ed, dd = G.dot(e, e), G.dot(e, self.d), 1.0
            den = ee * dd - ed * ed
            if abs(den) < 1e-18:
                t = 0.0
            else:
                t = (G.dot(w, e) * dd - G.dot(w, self.d) * ed) / den
            t = min(1.0, max(0.0, t))
            c = _lerp(a, b, t)
            s = G.dot(_sub(q, c), self.d)
            r = tuple(q[k] - c[k] - s * self.d[k] for k in range(3))
            dist = G.dot(r, r)
            if dist < best[0]:
                best = (dist, i + t, s)
        return (best[1], best[2])


def surface_of(s, geo):
    t = s.is_a().upper()
    if t == 'IFCCYLINDRICALSURFACE':
        return Cylinder(s)
    if t == 'IFCCONICALSURFACE':
        return Cone(s, geo.angle_scale)
    if t == 'IFCSPHERICALSURFACE':
        return Sphere(s)
    if t == 'IFCTOROIDALSURFACE':
        return Torus(s)
    if t == 'IFCSURFACEOFREVOLUTION':
        return Revolution(s, geo)
    if t == 'IFCSURFACEOFLINEAREXTRUSION':
        return LinearExtrusion(s, geo)
    if t in ('IFCBSPLINESURFACEWITHKNOTS', 'IFCRATIONALBSPLINESURFACEWITHKNOTS'):
        return BSplineSurface(s)
    raise G.Refused('IFC_FACE_SURFACE_NOT_IMPLEMENTED:' + s.is_a())


# ----------------------------------------------------------------------- 3D curves and edges

def _conic3d(c):
    m = G.axis2placement(c.Position)
    if c.is_a().upper() == 'IFCCIRCLE':
        r1 = r2 = float(c.Radius)
    else:
        r1, r2 = float(c.SemiAxis1), float(c.SemiAxis2)
    return m, r1, r2


def _conic_param(m, r1, r2, p):
    x, y, _z = G.apply(inv_rigid(m), p)
    return math.atan2(y / r2, x / r1)


def _conic_arc(m, r1, r2, a0, a1):
    n = max(2, int(math.ceil(abs(a1 - a0) / G.ARC_STEP)) + 1)
    return [G.apply(m, (r1 * math.cos(a0 + (a1 - a0) * i / (n - 1)), r2 * math.sin(a0 + (a1 - a0) * i / (n - 1)), 0.0))
            for i in range(n)]


def _sweep(a0, a1, ccw, full_if_equal=True):
    if ccw:
        while a1 <= a0 + 1e-12:
            a1 += TWO_PI
        if not full_if_equal and a1 - a0 > TWO_PI - 1e-9:
            a1 -= TWO_PI
    else:
        while a1 >= a0 - 1e-12:
            a1 -= TWO_PI
        if not full_if_equal and a0 - a1 > TWO_PI - 1e-9:
            a1 += TWO_PI
    return a1


def curve_points3d(c, geo, start=None, end=None, sense=True):
    """3D points of a bounded curve; with *start*/*end* the curve is cut between those points."""
    t = c.is_a().upper()
    if t == 'IFCLINE':
        if start is None or end is None:
            raise G.Refused('IFC_UNBOUNDED_LINE')
        return [start, end]
    if t == 'IFCPOLYLINE':
        pts = [G.coords(p) for p in c.Points]
        if not sense:
            pts.reverse()
        if start is not None:
            pts[0] = start
        if end is not None:
            pts[-1] = end
        return pts
    if t in ('IFCCIRCLE', 'IFCELLIPSE'):
        m, r1, r2 = _conic3d(c)
        if start is None:
            return _conic_arc(m, r1, r2, 0.0, TWO_PI)
        a0 = _conic_param(m, r1, r2, start)
        a1 = _conic_param(m, r1, r2, end)
        closed = math.dist(start, end) <= 1e-9 * max(1.0, r1)
        a1 = _sweep(a0, a1, sense) if closed else _sweep(a0, a1, sense, full_if_equal=False)
        pts = _conic_arc(m, r1, r2, a0, a1)
        pts[0] = start; pts[-1] = end
        return pts
    if t == 'IFCTRIMMEDCURVE':
        basis = c.BasisCurve
        if start is None:
            p0 = _trim_point(c.Trim1, basis, geo); p1 = _trim_point(c.Trim2, basis, geo)
            agree = _flag(c.SenseAgreement)
            return curve_points3d(basis, geo, p0, p1, agree)
        agree = _flag(c.SenseAgreement)
        return curve_points3d(basis, geo, start, end, sense == agree)
    if t in ('IFCBSPLINECURVEWITHKNOTS', 'IFCRATIONALBSPLINECURVEWITHKNOTS'):
        pts = BSplineCurve(c).samples()
        if not sense:
            pts.reverse()
        if start is not None:
            pts[0] = start
        if end is not None:
            pts[-1] = end
        return pts
    if t == 'IFCCOMPOSITECURVE':
        pts = []
        for seg in c.Segments:
            piece = curve_points3d(seg.ParentCurve, geo)
            if not _flag(seg.SameSense):
                piece.reverse()
            for p in piece:
                if not pts or math.dist(pts[-1], p) > 1e-12:
                    pts.append(p)
        if not sense:
            pts.reverse()
        if start is not None:
            pts[0] = start
        if end is not None:
            pts[-1] = end
        return pts
    raise G.Refused('IFC_EDGE_CURVE_NOT_IMPLEMENTED:' + c.is_a())


def _trim_point(trims, basis, geo):
    point = param = None
    for v in trims or []:
        if hasattr(v, 'is_a') and v.is_a('IfcCartesianPoint'):
            point = G.coords(v)
        elif hasattr(v, 'wrappedValue') or (isinstance(v, (int, float)) and not isinstance(v, bool)):
            param = _num(v)
    if point is not None:
        return point
    if param is None:
        raise G.Refused('IFC_TRIM_UNRESOLVED:' + basis.is_a())
    bt = basis.is_a().upper()
    if bt in ('IFCCIRCLE', 'IFCELLIPSE'):
        m, r1, r2 = _conic3d(basis)
        a = param * geo.angle_scale
        return G.apply(m, (r1 * math.cos(a), r2 * math.sin(a), 0.0))
    if bt == 'IFCLINE':
        o = G.coords(basis.Pnt); v = basis.Dir
        d = G.direction(v.Orientation, (1.0, 0.0, 0.0)); mag = float(v.Magnitude)
        return tuple(o[k] + d[k] * mag * param for k in range(3))
    raise G.Refused('IFC_TRIM_UNRESOLVED:' + basis.is_a())


def _vertex(v):
    g = getattr(v, 'VertexGeometry', None)
    if g is None:
        raise G.Refused('IFC_VERTEX_NOT_IMPLEMENTED:' + v.is_a())
    return G.coords(g)


def edge_points(edge, geo, cache):
    """Points of an IfcEdgeCurve from its start to its end vertex."""
    key = edge.id()
    if key in cache:
        return cache[key]
    t = edge.is_a().upper()
    if t == 'IFCORIENTEDEDGE':
        pts = edge_points(edge.EdgeElement, geo, cache)
        return pts if _flag(edge.Orientation) else pts[::-1]
    a = _vertex(edge.EdgeStart); b = _vertex(edge.EdgeEnd)
    if t == 'IFCEDGECURVE':
        pts = curve_points3d(edge.EdgeGeometry, geo, a, b, _flag(edge.SameSense))
    elif t == 'IFCEDGE':
        pts = [a, b]
    else:
        raise G.Refused('IFC_EDGE_NOT_IMPLEMENTED:' + edge.is_a())
    cache[key] = pts
    return pts


def loop_points(loop, geo, cache):
    t = loop.is_a().upper()
    if t == 'IFCPOLYLOOP':
        return [G.coords(p) for p in loop.Polygon]
    if t != 'IFCEDGELOOP':
        raise G.Refused('IFC_FACE_BOUND_NOT_IMPLEMENTED:' + loop.is_a())
    pts = []
    for oe in loop.EdgeList:
        for p in edge_points(oe, geo, cache):
            if not pts or math.dist(pts[-1], p) > 1e-12:
                pts.append(p)
    if len(pts) > 1 and math.dist(pts[0], pts[-1]) <= 1e-9 * max(1.0, max(abs(c) for c in pts[0])):
        pts.pop()
    return pts


# ----------------------------------------------------------------------- parameter-plane meshing

def _unwrap(seq, period):
    out = [seq[0]]
    for x in seq[1:]:
        prev = out[-1]
        out.append(x + period * round((prev - x) / period))
    return out


def _bridge(outer, holes):
    """One polygon (point list) from an outer loop and its holes, joined by zero-width bridges."""
    poly = list(outer) if G._area2(outer) >= 0 else list(outer)[::-1]
    for hole in sorted(holes, key=lambda h: -max(q[0] for q in h)):
        h = list(hole) if G._area2(hole) <= 0 else list(hole)[::-1]
        hi = max(range(len(h)), key=lambda i: h[i][0])
        hp = h[hi]
        cands = sorted(range(len(poly)), key=lambda i: (poly[i][0] - hp[0]) ** 2 + (poly[i][1] - hp[1]) ** 2)
        oi = cands[0]
        for i in cands[:16]:
            if poly[i][0] >= hp[0]:
                oi = i
                break
        ring = h[hi:] + h[:hi] + [h[hi]]
        poly = poly[:oi + 1] + ring + [poly[oi]] + poly[oi + 1:]
    return poly


def _clip(poly, axis, c, keep_above):
    """Sutherland-Hodgman clip of a polygon by the line coordinate[axis] = c."""
    out = []
    n = len(poly)
    for i in range(n):
        p = poly[i - 1]; q = poly[i]
        pin = p[axis] >= c if keep_above else p[axis] <= c
        qin = q[axis] >= c if keep_above else q[axis] <= c
        if qin:
            if not pin:
                out.append(_cut(p, q, axis, c))
            out.append(q)
        elif pin:
            out.append(_cut(p, q, axis, c))
    return out


def _cut(p, q, axis, c):
    t = (c - p[axis]) / (q[axis] - p[axis])
    o = 1 - axis
    r = [0.0, 0.0]
    r[axis] = c
    r[o] = p[o] + (q[o] - p[o]) * t
    return (r[0], r[1])


def _cells(poly, step):
    """Pieces of the polygon cut by a grid of the given (u, v) step (math.inf: no cut)."""
    pieces = [poly]
    for axis in (0, 1):
        st = step[axis]
        if not math.isfinite(st):
            continue
        out = []
        for piece in pieces:
            lo = min(q[axis] for q in piece); hi = max(q[axis] for q in piece)
            n = int(math.ceil((hi - lo) / st - 1e-9))
            if n <= 1:
                out.append(piece)
                continue
            n = min(n, 256)
            w = (hi - lo) / n
            for k in range(n):
                part = piece
                if k > 0:
                    part = _clip(part, axis, lo + w * k, True)
                if k < n - 1 and len(part) >= 3:
                    part = _clip(part, axis, lo + w * (k + 1), False)
                if len(part) >= 3:
                    out.append(part)
        pieces = out
    clean = []
    for piece in pieces:
        q = []
        for pt in piece:
            if not q or abs(pt[0] - q[-1][0]) + abs(pt[1] - q[-1][1]) > 1e-15:
                q.append(pt)
        if len(q) > 1 and abs(q[0][0] - q[-1][0]) + abs(q[0][1] - q[-1][1]) <= 1e-15:
            q.pop()
        if len(q) >= 3 and abs(G._area2(q)) > 1e-24:
            clean.append(q)
    return clean


def _mesh_param(surface, loops3d, flip, out, m, emit, stats):
    per = surface.periodic
    uvl = []
    exact = {}
    for loop in loops3d:
        uv = [surface.inv(p) for p in loop]
        us = [q[0] for q in uv]; vs = [q[1] for q in uv]
        if per[0]:
            us = _unwrap(us, TWO_PI)
        if per[1]:
            vs = _unwrap(vs, TWO_PI)
        uvl.append(list(zip(us, vs)))
    # winding of each loop around a periodic direction
    wraps = []
    for loop in uvl:
        du = loop[0][0] - loop[-1][0]; dv = loop[0][1] - loop[-1][1]
        wraps.append((per[0] and abs(du) > math.pi) or (per[1] and abs(dv) > math.pi))
    if any(wraps):
        return _mesh_band(surface, uvl, wraps, loops3d, flip, out, m, emit, stats)
    outer_i = max(range(len(uvl)), key=lambda i: abs(G._area2(uvl[i])))
    outer = uvl[outer_i]
    holes = []
    ou = [q[0] for q in outer]
    for i, h in enumerate(uvl):
        if i == outer_i or len(h) < 3:
            continue
        shift = 0.0
        if per[0]:
            cu = sum(q[0] for q in h) / len(h)
            shift = round(((min(ou) + max(ou)) / 2 - cu) / TWO_PI) * TWO_PI
        h = [(q[0] + shift, q[1]) for q in h]
        holes.append(h)
        for q, p3 in zip(h, loops3d[i]):
            exact[q] = p3
    for q, p3 in zip(outer, loops3d[outer_i]):
        exact[q] = p3
    if len(outer) < 3 or abs(G._area2(outer)) < 1e-18:
        raise G.Refused('IFC_FACE_PARAMETER_LOOP_DEGENERATE')
    poly = _bridge(outer, holes)
    count = 0
    for piece in _cells(poly, surface.step):
        xyz = [exact.get(q) or surface.eval(q[0], q[1]) for q in piece]
        for a, b, c in G.triangulate2d(piece):
            pa, pb, pc = piece[a], piece[b], piece[c]
            ccw = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0]) >= 0
            tri = (xyz[a], xyz[b], xyz[c]) if ccw != flip else (xyz[a], xyz[c], xyz[b])
            emit(tri, m, out)
            count += 1
        if count > MAX_FACE_TRIANGLES:
            stats['approx:advanced_face_triangle_budget'] += 1
            break
    stats['advanced_face:param'] += 1


def _resample(loop, k, u0, n, period):
    """v (or u) of a wrapping loop at n+1 uniform values of the wrapping coordinate."""
    a = [(p[k], p[1 - k]) for p in loop]
    if a[-1][0] < a[0][0]:
        a.reverse()
    # periodic extension, then linear interpolation
    ext = [(x - period, y) for x, y in a] + a + [(x + period, y) for x, y in a]
    res = []
    j = 0
    for i in range(n + 1):
        x = u0 + period * i / n
        while j < len(ext) - 2 and ext[j + 1][0] < x:
            j += 1
        (x0, y0), (x1, y1) = ext[j], ext[j + 1]
        t = 0.0 if x1 == x0 else min(1.0, max(0.0, (x - x0) / (x1 - x0)))
        res.append(y0 + (y1 - y0) * t)
    return res


def _mesh_band(surface, uvl, wraps, loops3d, flip, out, m, emit, stats):
    band = [l for l, w in zip(uvl, wraps) if w]
    if len(band) != 2:
        stats['approx:advanced_face_flat_fallback'] += 1
        outer = max(loops3d, key=len)
        for tri in G.triangulate3d(outer):
            emit(tri, m, out)
        return
    if sum(1 for w in wraps if not w):
        stats['approx:advanced_face_band_holes_ignored'] += 1
    k = 0 if surface.periodic[0] and abs(band[0][0][0] - band[0][-1][0]) > math.pi else 1
    n = max(int(math.ceil(TWO_PI / G.ARC_STEP)), 8)
    u0 = min(p[k] for p in band[0])
    rows = [_resample(l, k, u0, n, TWO_PI) for l in band]
    if sum(rows[0]) > sum(rows[1]):
        rows.reverse()
    pt = (lambda w, x: surface.eval(w, x)) if k == 0 else (lambda w, x: surface.eval(x, w))
    for i in range(n):
        w0 = u0 + TWO_PI * i / n; w1 = u0 + TWO_PI * (i + 1) / n
        a = pt(w0, rows[0][i]); b = pt(w1, rows[0][i + 1]); c = pt(w1, rows[1][i + 1]); d = pt(w0, rows[1][i])
        quad = [(a, b, c), (a, c, d)]
        if k == 1:
            quad = [(a, c, b), (a, d, c)]
        for tri in quad:
            emit(tri if not flip else (tri[0], tri[2], tri[1]), m, out)
    stats['advanced_face:band'] += 1


# ----------------------------------------------------------------------- faces

def face(geo, f, m, out, cache):
    """Append the triangles of one IfcFace / IfcFaceSurface / IfcAdvancedFace."""
    loops = []; outer_i = None
    for bound in f.Bounds:
        pts = loop_points(bound.Bound, geo, cache)
        if len(pts) < 2:
            continue
        if not _flag(bound.Orientation):
            pts.reverse()
        if bound.is_a('IfcFaceOuterBound') and outer_i is None:
            outer_i = len(loops)
        loops.append(pts)
    if not loops:
        return
    surf = getattr(f, 'FaceSurface', None)
    sense = _flag(getattr(f, 'SameSense', True))
    st = surf.is_a().upper() if surf is not None else 'IFCPLANE'
    if st == 'IFCPLANE' or surf is None:
        if outer_i is None:
            outer_i = max(range(len(loops)), key=lambda i: len(loops[i]))
        outer = loops[outer_i]
        holes = [l for i, l in enumerate(loops) if i != outer_i and len(l) >= 3]
        if len(outer) < 3:
            return
        n = None
        if surf is not None:
            pm = G.axis2placement(surf.Position)
            n = (pm[2], pm[6], pm[10]) if sense else (-pm[2], -pm[6], -pm[10])
        for tri in G.triangulate3d(outer, holes):
            if n is not None:
                tn = G.cross(_sub(tri[1], tri[0]), _sub(tri[2], tri[0]))
                if G.dot(tn, n) < 0:
                    tri = (tri[0], tri[2], tri[1])
            geo._emit(tri, m, out)
        geo.stats['advanced_face:plane'] += 1
        return
    surface = surface_of(surf, geo)
    loops = [l for l in loops if len(l) >= 2]
    _mesh_param(surface, loops, not sense, out, m, geo._emit, geo.stats)


def faces(geo, face_list, m, out):
    cache = {}
    done = 0; skipped = 0
    for f in face_list:
        before = len(out)
        try:
            face(geo, f, m, out, cache)
            done += 1
        except G.Refused as error:
            del out[before:]
            geo.stats['approx:advanced_face_skipped:' + str(error)] += 1
            skipped += 1
        except (AttributeError, TypeError, IndexError, ValueError, ZeroDivisionError, OverflowError) as error:
            del out[before:]
            geo.stats['approx:advanced_face_skipped:IFC_FACE_ERROR:%s' % type(error).__name__] += 1
            skipped += 1
    if not done and skipped:
        raise G.Refused('IFC_ADVANCED_BREP_NO_FACE_MESHED')
    return done, skipped
