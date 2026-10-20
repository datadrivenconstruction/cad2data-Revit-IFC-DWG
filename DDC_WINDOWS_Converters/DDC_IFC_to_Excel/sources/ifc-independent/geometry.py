"""Own IFC geometry: tessellation of representation items into world triangles (stdlib only).

Works on entities of the own reader (``model.py``).  Implemented subset:
IfcTriangulatedFaceSet, IfcPolygonalFaceSet, IfcFacetedBrep (+WithVoids outer
shell), IfcShellBasedSurfaceModel / IfcFaceBasedSurfaceModel of poly loops,
IfcExtrudedAreaSolid with rectangle, hollow rectangle, circle, hollow circle,
ellipse, I / L / T / U / C / Z shape (without fillets, counted) and arbitrary closed / with-voids profiles whose curves are polylines,
indexed poly curves (line and arc segments), circles, ellipses, trimmed
circles / ellipses / lines and composite curves of those; IfcMappedItem,
IfcLocalPlacement chains, IfcRevolvedAreaSolid, IfcRoundedRectangleProfileDef,
IfcAdvancedBrep / IfcFaceSurface faces (``advanced_brep``: planes, cylinders,
cones, spheres, tori, surfaces of revolution / linear extrusion, B-spline
surfaces, edge loops of lines, conics and B-spline curves), IfcBooleanResult
UNION, DIFFERENCE with an IfcHalfSpaceSolid / IfcBoxedHalfSpace or an
IfcPolygonalBoundedHalfSpace with a convex boundary (exact convex clipping, the
cut is capped when the outline closes), DIFFERENCE with a non-convex bounded
half-space or with any solid second operand by the own BSP mesh boolean
(``mesh_csg``; above its work budget the first operand is kept and counted).

Openings (IfcRelVoidsElement), see ``Tessellator``: an opening whose body is
convex (an extrusion with a convex profile or a convex closed mesh) is subtracted
from every triangle of a host that is a convex extrusion, and the opening faces
clipped to the host are added as reveals; any other opening, and every opening of
any other host, is subtracted by the mesh boolean (reveals from the opening body).
Every refusal raises ``Refused('<CODE>:<IFC type>')``.
"""
import math
from array import array
from collections import Counter, defaultdict

CIRCLE_SEGMENTS = 32
ARC_STEP = 2 * math.pi / CIRCLE_SEGMENTS
EPS = 1e-9

class Refused(ValueError):
    pass


# ----------------------------------------------------------------------- linear algebra (4x4 row-major)

IDENTITY = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)


def mul(a, b):
    return tuple(sum(a[r * 4 + k] * b[k * 4 + c] for k in range(4)) for r in range(4) for c in range(4))


def apply(m, p):
    x, y, z = p
    return (m[0] * x + m[1] * y + m[2] * z + m[3], m[4] * x + m[5] * y + m[6] * z + m[7],
            m[8] * x + m[9] * y + m[10] * z + m[11])


def norm(v):
    L = math.sqrt(sum(c * c for c in v))
    if L == 0:
        raise Refused('ZERO_LENGTH_DIRECTION')
    return tuple(c / L for c in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def coords(point):
    c = list(point.Coordinates)
    while len(c) < 3:
        c.append(0.0)
    return tuple(float(v) for v in c[:3])


def direction(d, default):
    if d is None:
        return default
    r = list(d.DirectionRatios)
    while len(r) < 3:
        r.append(0.0)
    return norm(tuple(float(v) for v in r[:3]))


def axis2placement(p):
    """Matrix of IfcAxis2Placement3D / IfcAxis2Placement2D."""
    if p is None:
        return IDENTITY
    o = coords(p.Location)
    if p.is_a('IfcAxis2Placement2D'):
        x = direction(p.RefDirection, (1.0, 0.0, 0.0))
        z = (0.0, 0.0, 1.0)
    else:
        z = direction(p.Axis, (0.0, 0.0, 1.0))
        x = direction(p.RefDirection, (1.0, 0.0, 0.0))
    # orthonormalise x against z
    x = tuple(a - dot(x, z) * b for a, b in zip(x, z))
    try:
        x = norm(x)
    except Refused:
        x = norm(cross((0.0, 1.0, 0.0) if abs(z[1]) < 0.9 else (1.0, 0.0, 0.0), z))
    y = cross(z, x)
    return (x[0], y[0], z[0], o[0], x[1], y[1], z[1], o[1], x[2], y[2], z[2], o[2], 0.0, 0.0, 0.0, 1.0)


def transform_operator(t):
    """IfcCartesianTransformationOperator3D(nonUniform) matrix."""
    if t is None:
        return IDENTITY
    o = coords(t.LocalOrigin)
    x = direction(getattr(t, 'Axis1', None), (1.0, 0.0, 0.0))
    y = direction(getattr(t, 'Axis2', None), (0.0, 1.0, 0.0))
    try:
        z = direction(getattr(t, 'Axis3', None), (0.0, 0.0, 1.0))
    except AttributeError:
        z = (0.0, 0.0, 1.0)
    s = t.Scale if getattr(t, 'Scale', None) is not None else 1.0
    s2 = getattr(t, 'Scale2', None) or s
    s3 = getattr(t, 'Scale3', None) or s
    return (x[0] * s, y[0] * s2, z[0] * s3, o[0], x[1] * s, y[1] * s2, z[1] * s3, o[1],
            x[2] * s, y[2] * s2, z[2] * s3, o[2], 0.0, 0.0, 0.0, 1.0)


# ----------------------------------------------------------------------- polygon triangulation

def _area2(pts):
    return sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts))) / 2


def _point_in_tri(p, a, b, c):
    d1 = (p[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (p[1] - b[1])
    d2 = (p[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (p[1] - c[1])
    d3 = (p[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (p[1] - a[1])
    neg = d1 < 0 or d2 < 0 or d3 < 0
    pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)


def triangulate2d(outer, holes=()):
    """Ear clipping with hole bridging; returns index triples into outer+holes (concatenated)."""
    pts = list(outer); idx = list(range(len(outer)))
    if _area2(outer) < 0:
        idx.reverse()
    base = len(outer)
    for hole in sorted(holes, key=lambda h: -max(p[0] for p in h)):
        h_idx = list(range(base, base + len(hole))); pts.extend(hole); base += len(hole)
        if _area2(hole) > 0:
            h_idx.reverse()
        # bridge from the hole's rightmost vertex to the nearest visible outer vertex (approximate visibility)
        hi = max(range(len(h_idx)), key=lambda i: pts[h_idx[i]][0])
        hp = pts[h_idx[hi]]
        cands = sorted(range(len(idx)), key=lambda i: (pts[idx[i]][0] - hp[0]) ** 2 + (pts[idx[i]][1] - hp[1]) ** 2)
        oi = cands[0]
        for i in cands[:16]:
            if pts[idx[i]][0] >= hp[0]:
                oi = i; break
        ring = h_idx[hi:] + h_idx[:hi] + [h_idx[hi]]
        idx = idx[:oi + 1] + ring + [idx[oi]] + idx[oi + 1:]
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 100000:
        guard += 1
        n = len(idx); found = False
        for i in range(n):
            a, b, c = idx[i - 1], idx[i], idx[(i + 1) % n]
            pa, pb, pc = pts[a], pts[b], pts[c]
            if (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0]) <= 0:
                continue
            if any(_point_in_tri(pts[j], pa, pb, pc) for j in idx if j not in (a, b, c) and pts[j] not in (pa, pb, pc)):
                continue
            tris.append((a, b, c)); del idx[i]; found = True
            break
        if not found:
            break
    if len(idx) == 3:
        tris.append(tuple(idx))
    elif len(idx) > 3:   # degenerate remainder: fan (counted by caller via return flag)
        for i in range(1, len(idx) - 1):
            tris.append((idx[0], idx[i], idx[i + 1]))
    return tris


def triangulate3d(loop, holes=()):
    """Triangles (as point triples) of a planar 3D polygon with optional holes."""
    if len(loop) < 3:
        return []
    if len(loop) == 3 and not holes:
        return [tuple(loop)]
    # Newell normal
    n = [0.0, 0.0, 0.0]
    for i in range(len(loop)):
        c = loop[i]; d = loop[(i + 1) % len(loop)]
        n[0] += (c[1] - d[1]) * (c[2] + d[2]); n[1] += (c[2] - d[2]) * (c[0] + d[0]); n[2] += (c[0] - d[0]) * (c[1] + d[1])
    ax = max(range(3), key=lambda k: abs(n[k]))
    u, v = [(1, 2), (2, 0), (0, 1)][ax]
    sign = 1 if n[ax] >= 0 else -1
    proj = lambda pts: [(p[u], p[v] * sign) for p in pts]
    all3 = list(loop) + [p for h in holes for p in h]
    tris = triangulate2d(proj(loop), [proj(h) for h in holes])
    return [(all3[a], all3[b], all3[c]) for a, b, c in tris]


# ----------------------------------------------------------------------- parameterised steel profiles
# Outlines centred on the bounding box (IFC4 placement rule), counter-clockwise, without
# fillet/edge radii and flange slopes (counted by the caller).

def _f(v):
    return float(v.wrappedValue if hasattr(v, 'wrappedValue') else v)


def _i_shape(p):
    w, d, tw, tf = _f(p.OverallWidth) / 2, _f(p.OverallDepth) / 2, _f(p.WebThickness) / 2, _f(p.FlangeThickness)
    return [(-w, -d), (w, -d), (w, -d + tf), (tw, -d + tf), (tw, d - tf), (w, d - tf), (w, d), (-w, d),
            (-w, d - tf), (-tw, d - tf), (-tw, -d + tf), (-w, -d + tf)]


def _l_shape(p):
    d = _f(p.Depth); b = _f(p.Width) if getattr(p, 'Width', None) is not None else d; t = _f(p.Thickness)
    x, y = b / 2, d / 2
    return [(-x, -y), (x, -y), (x, -y + t), (-x + t, -y + t), (-x + t, y), (-x, y)]


def _t_shape(p):
    y = _f(p.Depth) / 2; bf = _f(p.FlangeWidth) / 2; tw = _f(p.WebThickness) / 2; tf = _f(p.FlangeThickness)
    return [(-tw, -y), (tw, -y), (tw, y - tf), (bf, y - tf), (bf, y), (-bf, y), (-bf, y - tf), (-tw, y - tf)]


def _u_shape(p):
    y = _f(p.Depth) / 2; x = _f(p.FlangeWidth) / 2; tw = _f(p.WebThickness); tf = _f(p.FlangeThickness)
    return [(-x, -y), (x, -y), (x, -y + tf), (-x + tw, -y + tf), (-x + tw, y - tf), (x, y - tf), (x, y), (-x, y)]


def _c_shape(p):
    y = _f(p.Depth) / 2; x = _f(p.Width) / 2; t = _f(p.WallThickness)
    g = _f(p.Girth) if getattr(p, 'Girth', None) is not None else t
    return [(-x, -y), (x, -y), (x, -y + g), (x - t, -y + g), (x - t, -y + t), (-x + t, -y + t), (-x + t, y - t),
            (x - t, y - t), (x - t, y - g), (x, y - g), (x, y), (-x, y)]


def _z_shape(p):
    y = _f(p.Depth) / 2; bf = _f(p.FlangeWidth); tw = _f(p.WebThickness); tf = _f(p.FlangeThickness)
    x = bf - tw / 2; h = tw / 2
    return [(-h, -y), (x, -y), (x, -y + tf), (h, -y + tf), (h, y), (-x, y), (-x, y - tf), (-h, y - tf)]


SHAPE_PROFILES = {'IfcIShapeProfileDef': _i_shape, 'IfcLShapeProfileDef': _l_shape, 'IfcTShapeProfileDef': _t_shape,
                  'IfcUShapeProfileDef': _u_shape, 'IfcCShapeProfileDef': _c_shape, 'IfcZShapeProfileDef': _z_shape}


# ----------------------------------------------------------------------- geometry of representation items

class Geometry:
    def __init__(self, stats=None, angle_scale=1.0):
        self.stats = stats if stats is not None else Counter()
        self.angle_scale = angle_scale       # plane angle unit -> radians

    def item(self, it, m, out):
        """Append world triangles of *it* under matrix *m* to *out* (list of floats, 9 per tri)."""
        t = it.is_a()
        fn = getattr(self, 'g_' + t, None)
        if fn is None:
            raise Refused('IFC_GEOMETRY_ITEM_NOT_IMPLEMENTED:' + t)
        fn(it, m, out)
        self.stats['item:' + t] += 1

    def _emit(self, tri, m, out):
        for p in tri:
            out.extend(apply(m, p))

    def g_IfcTriangulatedFaceSet(self, it, m, out):
        pts = [tuple(float(c) for c in (list(p) + [0.0, 0.0])[:3]) for p in it.Coordinates.CoordList]
        pn = list(it.PnIndex) if getattr(it, 'PnIndex', None) else None
        for f in it.CoordIndex:
            ids = [pn[i - 1] if pn else i for i in f]
            self._emit([pts[i - 1] for i in ids], m, out)

    def g_IfcTriangulatedIrregularNetwork(self, it, m, out):
        self.g_IfcTriangulatedFaceSet(it, m, out)

    def g_IfcPolygonalFaceSet(self, it, m, out):
        pts = [tuple(float(c) for c in (list(p) + [0.0, 0.0])[:3]) for p in it.Coordinates.CoordList]
        pn = list(it.PnIndex) if getattr(it, 'PnIndex', None) else None
        get = lambda i: pts[(pn[i - 1] if pn else i) - 1]
        for face in it.Faces:
            loop = [get(i) for i in face.CoordIndex]
            holes = []
            if face.is_a('IfcIndexedPolygonalFaceWithVoids'):
                holes = [[get(i) for i in inner] for inner in face.InnerCoordIndices]
            for tri in triangulate3d(loop, holes):
                self._emit(tri, m, out)

    def _faces(self, faces, m, out):
        faces = list(faces)
        if any(f.is_a('IfcFaceSurface') or any(not b.Bound.is_a('IfcPolyLoop') for b in f.Bounds) for f in faces):
            import advanced_brep
            advanced_brep.faces(self, faces, m, out)
            return
        for face in faces:
            outer = None; holes = []
            for bound in face.Bounds:
                loop = bound.Bound
                if not loop.is_a('IfcPolyLoop'):
                    raise Refused('IFC_FACE_BOUND_NOT_POLYLOOP:' + loop.is_a())
                pts = [coords(p) for p in loop.Polygon]
                if not bound.Orientation:
                    pts.reverse()
                if bound.is_a('IfcFaceOuterBound') and outer is None:
                    outer = pts
                else:
                    holes.append(pts)
            if outer is None and holes:
                outer = max(holes, key=len); holes.remove(outer)
            if outer is None:
                continue
            for tri in triangulate3d(outer, holes):
                self._emit(tri, m, out)

    def g_IfcFacetedBrep(self, it, m, out):
        self._faces(it.Outer.CfsFaces, m, out)

    def g_IfcFacetedBrepWithVoids(self, it, m, out):
        self._faces(it.Outer.CfsFaces, m, out)
        self.stats['approx:brep_voids_not_subtracted'] += 1

    def g_IfcAdvancedBrep(self, it, m, out):
        import advanced_brep
        advanced_brep.faces(self, it.Outer.CfsFaces, m, out)

    def g_IfcAdvancedBrepWithVoids(self, it, m, out):
        self.g_IfcAdvancedBrep(it, m, out)
        self.stats['approx:brep_voids_not_subtracted'] += 1

    def g_IfcRevolvedAreaSolid(self, it, m, out):
        outer, holes = self.profile(it.SweptArea)
        if len(outer) < 3:
            raise Refused('IFC_PROFILE_DEGENERATE')
        mm = mul(m, axis2placement(it.Position))
        ax = it.Axis
        a = coords(ax.Location); d = direction(getattr(ax, 'Axis', None), (0.0, 0.0, 1.0))
        angle = float(it.Angle) * self.angle_scale
        if abs(angle) < 1e-12:
            raise Refused('IFC_REVOLUTION_ANGLE_ZERO')
        full = abs(abs(angle) - 2 * math.pi) < 1e-9
        n = max(2, int(math.ceil(abs(angle) / ARC_STEP)))
        if _area2(outer) < 0:
            outer = outer[::-1]
        holes = [h if _area2(h) < 0 else h[::-1] for h in holes]

        def rot(p, t):
            v = (p[0] - a[0], p[1] - a[1], p[2] - a[2])
            c, s_ = math.cos(t), math.sin(t)
            k = dot(d, v); cr = cross(d, v)
            return tuple(a[i] + v[i] * c + cr[i] * s_ + d[i] * k * (1 - c) for i in range(3))
        for loop in [outer] + holes:
            ring = [(x, y, 0.0) for x, y in loop]
            rows = [[rot(p, angle * j / n) for p in ring] for j in range(n + 1)]
            for j in range(n):
                r0, r1 = rows[j], rows[j + 1]
                for i in range(len(ring)):
                    p, q = r0[i - 1], r0[i]; pt, qt = r1[i - 1], r1[i]
                    self._emit((p, q, qt), mm, out); self._emit((p, qt, pt), mm, out)
        if not full:
            bottom = [(x, y, 0.0) for x, y in outer]; hb = [[(x, y, 0.0) for x, y in h] for h in holes]
            for tri in triangulate3d(bottom, hb):
                self._emit(tri, mm, out)
                self._emit(tuple(rot(p, angle) for p in (tri[0], tri[2], tri[1])), mm, out)
        self.stats['solid:revolved'] += 1

    def g_IfcShellBasedSurfaceModel(self, it, m, out):
        for shell in it.SbsmBoundary:
            self._faces(shell.CfsFaces, m, out)

    def g_IfcFaceBasedSurfaceModel(self, it, m, out):
        for shell in it.FbsmFaces:
            self._faces(shell.CfsFaces, m, out)

    def g_IfcMappedItem(self, it, m, out):
        src = it.MappingSource
        mm = mul(m, mul(transform_operator(it.MappingTarget), axis2placement(src.MappingOrigin)))
        for sub in src.MappedRepresentation.Items:
            self.item(sub, mm, out)

    def g_IfcBooleanClippingResult(self, it, m, out):
        second = it.SecondOperand
        op = str(it.Operator).strip('.').upper()
        if op == 'UNION':
            self.item(it.FirstOperand, m, out); self.item(second, m, out)
            return
        if op != 'DIFFERENCE':
            self.stats['approx:boolean_second_operand_ignored'] += 1
            self.item(it.FirstOperand, m, out)
            return
        if not second.is_a('IfcHalfSpaceSolid'):
            self._solid_difference(it, m, out)
            return
        first = array('d')
        self.item(it.FirstOperand, m, first)
        if first and second.is_a('IfcPolygonalBoundedHalfSpace'):
            res = self._nonconvex_halfspace_csg(second, m, first)
            if res is not None:
                out.extend(res)
                return
        try:
            regions = self._halfspace_regions(second, m)
        except Refused as error:
            self.stats['approx:boolean_second_operand_ignored'] += 1
            self.stats['approx:halfspace_refused:' + str(error)] += 1
            out.extend(first)
            return
        if not first:
            return
        lo = min(first); hi = max(first)
        eps = 1e-9 * max(1.0, abs(lo), abs(hi))
        kept = first; changed = False
        for planes, _sides in regions:
            kept, ch = subtract_convex(kept, planes, eps)
            changed = changed or ch
        out.extend(kept)
        if not changed:
            self.stats['boolean:halfspace_no_effect'] += 1
            return
        self.stats['boolean:halfspace_clipped'] += 1
        closed = True
        for planes, sides in regions:
            caps = halfspace_caps(first, planes[0], sides, eps)
            if caps is None:
                closed = False
            else:
                out.extend(caps)
        if not closed:
            self.stats['approx:halfspace_cap_not_closed'] += 1

    def _solid_difference(self, it, m, out):
        """DIFFERENCE with a solid second operand: own BSP mesh boolean (mesh_csg)."""
        import mesh_csg
        first = array('d')
        self.item(it.FirstOperand, m, first)
        second = array('d')
        try:
            self.item(it.SecondOperand, m, second)
        except Refused as error:
            self.stats['approx:boolean_second_operand_ignored'] += 1
            self.stats['approx:boolean_second_operand_refused:' + str(error)] += 1
            out.extend(first)
            return
        if not first or not second:
            out.extend(first)
            return
        try:
            res = mesh_csg.subtract(orient_outward(first), orient_outward(second))
        except mesh_csg.CsgBudget:
            self.stats['approx:boolean_second_operand_ignored'] += 1
            self.stats['approx:boolean_csg_budget_exceeded'] += 1
            out.extend(first)
            return
        self.stats['boolean:csg_difference'] += 1
        out.extend(res)

    def _nonconvex_halfspace_csg(self, hs, m, first):
        """First operand minus a polygonal bounded half-space with a non-convex boundary, by the
        mesh boolean against a closed cutter (boundary prism clipped by the base plane, capped).
        None when the boundary is convex (exact convex path) or the boolean is not possible."""
        import mesh_csg
        try:
            poly = self.curve_points(hs.PolygonalBoundary)
        except Refused:
            return None
        if len(poly) < 3 or is_convex2d(poly) or abs(_area2(poly)) <= 0:
            return None
        if _area2(poly) < 0:
            poly = poly[::-1]
        try:
            plane = self._halfspace_region(hs, m, [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])[0][0]
        except Refused:
            return None
        lo, hi = mesh_csg.bbox(first)
        qm = mul(m, axis2placement(hs.Position))
        centre = [(a + b) / 2 for a, b in zip(lo, hi)]
        diag = math.dist(lo, hi)
        L = 2 * (diag + math.dist(centre, (qm[3], qm[7], qm[11]))) + 1.0
        prism = array('d')
        bottom = [(x, y, -L) for x, y in poly]; top = [(x, y, L) for x, y in poly]
        for a, b, c in triangulate2d(poly):
            self._emit((bottom[a], bottom[c], bottom[b]), qm, prism)
            self._emit((top[a], top[b], top[c]), qm, prism)
        for i in range(len(poly)):
            a, b = bottom[i - 1], bottom[i]; at, bt = top[i - 1], top[i]
            self._emit((a, b, bt), qm, prism); self._emit((a, bt, at), qm, prism)
        n, d = plane
        keep_side = (tuple(-c for c in n), -d)        # remove the prism part on the material side
        eps = 1e-9 * max(1.0, max(abs(v) for v in lo + hi), L)
        cutter, changed = subtract_convex(prism, [keep_side], eps)
        caps = halfspace_caps(prism, keep_side, [], eps) if changed else array('d')
        if caps is None:
            return None
        cutter.extend(caps)
        try:
            res = mesh_csg.subtract(orient_outward(first), orient_outward(cutter))
        except mesh_csg.CsgBudget:
            self.stats['approx:halfspace_csg_budget_exceeded'] += 1
            return None
        self.stats['boolean:polygonal_bounded_halfspace_nonconvex_csg'] += 1
        return res

    def _halfspace_regions(self, hs, m):
        """[(planes, sides)] convex regions whose union is removed by a half-space solid.

        A non-convex polygonal boundary is split into triangles, one region each."""
        if hs.is_a('IfcPolygonalBoundedHalfSpace'):
            poly = self.curve_points(hs.PolygonalBoundary)
            if len(poly) >= 3 and not is_convex2d(poly):
                if _area2(poly) < 0:
                    poly = poly[::-1]
                pieces = [[poly[i], poly[j], poly[k]] for i, j, k in triangulate2d(poly)]
                pieces = [q for q in pieces if abs(_area2(q)) > 0]
                if not pieces:
                    raise Refused('IFC_HALFSPACE_BOUNDARY_DEGENERATE')
                self.stats['boolean:polygonal_bounded_halfspace_nonconvex'] += 1
                return [self._halfspace_region(hs, m, q) for q in pieces]
        return [self._halfspace_region(hs, m)]

    def _halfspace_region(self, hs, m, poly=None):
        """Convex region removed by a half-space solid as planes (n, d), n.p <= d inside.

        Returns (planes, side_planes): planes[0] is the material side of the base plane;
        side_planes bound an IfcPolygonalBoundedHalfSpace (convex boundary only)."""
        base = hs.BaseSurface
        if not base.is_a('IfcPlane'):
            raise Refused('IFC_HALFSPACE_BASE_NOT_PLANE:' + base.is_a())
        pm = mul(m, axis2placement(base.Position))
        n = norm((pm[2], pm[6], pm[10]))
        o = (pm[3], pm[7], pm[11])
        # AgreementFlag TRUE: the plane normal points away from the half-space material.
        if hs.AgreementFlag is False or str(hs.AgreementFlag) in ('F', '.F.', 'False'):
            plane = (tuple(-c for c in n), -dot(n, o))
        else:
            plane = (n, dot(n, o))
        sides = []
        if hs.is_a('IfcPolygonalBoundedHalfSpace'):
            if poly is None:
                poly = self.curve_points(hs.PolygonalBoundary)
            if len(poly) < 3 or not is_convex2d(poly):
                raise Refused('IFC_HALFSPACE_BOUNDARY_NOT_CONVEX')
            if _area2(poly) < 0:
                poly = poly[::-1]
            qm = mul(m, axis2placement(hs.Position))
            for i in range(len(poly)):
                a = poly[i - 1]; b = poly[i]
                nl = (b[1] - a[1], a[0] - b[0], 0.0)          # outward normal of a CCW edge
                nw = norm((qm[0] * nl[0] + qm[1] * nl[1], qm[4] * nl[0] + qm[5] * nl[1],
                           qm[8] * nl[0] + qm[9] * nl[1]))
                sides.append((nw, dot(nw, apply(qm, (a[0], a[1], 0.0)))))
            self.stats['boolean:polygonal_bounded_halfspace'] += 1
        return [plane] + sides, sides

    def g_IfcBooleanResult(self, it, m, out):
        self.g_IfcBooleanClippingResult(it, m, out)

    # -- profiles and extrusion
    # -- curves (2D, in the profile plane)
    def _arc(self, centre, r1, r2, rot, a0, a1):
        """Points of an elliptic arc from parameter a0 to a1 (radians, signed sweep), endpoints included."""
        n = max(2, int(math.ceil(abs(a1 - a0) / ARC_STEP)) + 1)
        c, s = math.cos(rot), math.sin(rot)
        out = []
        for i in range(n):
            t = a0 + (a1 - a0) * i / (n - 1)
            x, y = r1 * math.cos(t), r2 * math.sin(t)
            out.append((centre[0] + c * x - s * y, centre[1] + s * x + c * y))
        return out

    def _conic(self, c):
        """(centre, r1, r2, rotation) of IfcCircle / IfcEllipse in the profile plane."""
        mm = axis2placement(c.Position)
        if c.is_a('IfcCircle'):
            r1 = r2 = float(c.Radius)
        else:
            r1, r2 = float(c.SemiAxis1), float(c.SemiAxis2)
        return (mm[3], mm[7]), r1, r2, math.atan2(mm[4], mm[0])

    def _trim(self, trims, basis, prefer_param):
        point = param = None
        for t in trims or []:
            if hasattr(t, 'is_a') and t.is_a('IfcCartesianPoint'):
                point = coords(t)[:2]
            elif hasattr(t, 'wrappedValue'):
                param = float(t.wrappedValue)
            elif isinstance(t, (int, float)) and not isinstance(t, bool):
                param = float(t)
        if basis.is_a('IfcLine'):
            o = coords(basis.Pnt)[:2]
            v = basis.Dir
            d = direction(v.Orientation, (1.0, 0.0, 0.0)); mag = float(v.Magnitude)
            if param is not None and (prefer_param or point is None):
                return (o[0] + d[0] * mag * param, o[1] + d[1] * mag * param)
            if point is None:
                raise Refused('IFC_TRIM_UNRESOLVED:IfcLine')
            return point
        centre, r1, r2, rot = self._conic(basis)
        if param is not None and (prefer_param or point is None):
            return param * self.angle_scale
        if point is None:
            raise Refused('IFC_TRIM_UNRESOLVED:' + basis.is_a())
        c, s = math.cos(-rot), math.sin(-rot)
        x, y = point[0] - centre[0], point[1] - centre[1]
        return math.atan2((s * x + c * y) / r2, (c * x - s * y) / r1)

    def curve_points(self, c):
        """2D point list of a closed profile curve (closing duplicate removed)."""
        pts = self._curve(c)
        if len(pts) > 1 and math.dist(pts[0], pts[-1]) < 1e-12:
            pts = pts[:-1]
        return pts

    def _curve(self, c):
        t = c.is_a()
        if t == 'IfcPolyline':
            return [coords(p)[:2] for p in c.Points]
        if t == 'IfcIndexedPolyCurve':
            raw = [tuple(float(v) for v in p[:2]) for p in c.Points.CoordList]
            if not c.Segments:
                return raw
            pts = []
            for seg in c.Segments:
                ids = list(seg.wrappedValue if hasattr(seg, 'wrappedValue') else seg)
                if seg.is_a('IfcArcIndex'):
                    piece = arc_through(raw[ids[0] - 1], raw[ids[1] - 1], raw[ids[2] - 1])
                    self.stats['curve:indexed_arc'] += 1
                else:
                    piece = [raw[i - 1] for i in ids]
                for p in piece:
                    if not pts or math.dist(pts[-1], p) > 1e-12:
                        pts.append(p)
            return pts
        if t in ('IfcCircle', 'IfcEllipse'):
            centre, r1, r2, rot = self._conic(c)
            return self._arc(centre, r1, r2, rot, 0.0, 2 * math.pi)[:-1]
        if t == 'IfcTrimmedCurve':
            basis = c.BasisCurve
            bt = basis.is_a()
            if bt not in ('IfcCircle', 'IfcEllipse', 'IfcLine'):
                raise Refused('IFC_TRIMMED_BASIS_NOT_IMPLEMENTED:' + bt)
            prefer = str(c.MasterRepresentation) == 'PARAMETER'
            v1 = self._trim(c.Trim1, basis, prefer)
            v2 = self._trim(c.Trim2, basis, prefer)
            if bt == 'IfcLine':
                pts = [v1, v2] if c.SenseAgreement is not False else [v2, v1]
            else:
                centre, r1, r2, rot = self._conic(basis)
                a0, a1 = v1, v2
                if c.SenseAgreement:
                    while a1 <= a0 + 1e-12:
                        a1 += 2 * math.pi
                else:
                    while a1 >= a0 - 1e-12:
                        a1 -= 2 * math.pi
                pts = self._arc(centre, r1, r2, rot, a0, a1)
            self.stats['curve:trimmed_' + bt] += 1
            return pts
        if t == 'IfcCompositeCurve':
            pts = []
            for seg in c.Segments:
                if not seg.is_a('IfcCompositeCurveSegment'):
                    raise Refused('IFC_COMPOSITE_SEGMENT_NOT_IMPLEMENTED:' + seg.is_a())
                piece = self._curve(seg.ParentCurve)
                if not seg.SameSense:
                    piece = piece[::-1]
                for p in piece:
                    if not pts or math.dist(pts[-1], p) > 1e-9:
                        pts.append(p)
            self.stats['curve:composite'] += 1
            return pts
        raise Refused('IFC_PROFILE_CURVE_NOT_IMPLEMENTED:' + t)

    def profile(self, p):
        """(outer, holes) 2D loops of a profile definition."""
        t = p.is_a()
        pos = axis2placement(getattr(p, 'Position', None)) if getattr(p, 'Position', None) is not None else IDENTITY
        tr = lambda pts: [apply(pos, (x, y, 0.0))[:2] for x, y in pts]
        if t == 'IfcRectangleProfileDef':
            x = float(p.XDim) / 2; y = float(p.YDim) / 2
            return tr([(-x, -y), (x, -y), (x, y), (-x, y)]), []
        if t == 'IfcRoundedRectangleProfileDef':
            x = float(p.XDim) / 2; y = float(p.YDim) / 2
            r = min(float(p.RoundingRadius or 0.0), x, y)
            pts = []
            for cx, cy, a0 in ((x - r, y - r, 0.0), (-x + r, y - r, 90.0), (-x + r, -y + r, 180.0), (x - r, -y + r, 270.0)):
                for i in range(CIRCLE_SEGMENTS // 4 + 1):
                    a = math.radians(a0 + 90.0 * i / (CIRCLE_SEGMENTS // 4))
                    q = (cx + r * math.cos(a), cy + r * math.sin(a))
                    if not pts or math.dist(pts[-1], q) > 1e-12:
                        pts.append(q)
            if len(pts) > 1 and math.dist(pts[0], pts[-1]) <= 1e-12:
                pts.pop()
            self.stats['profile:IfcRoundedRectangleProfileDef'] += 1
            return tr(pts), []
        if t == 'IfcRectangleHollowProfileDef':
            x = float(p.XDim) / 2; y = float(p.YDim) / 2; w = float(p.WallThickness)
            return tr([(-x, -y), (x, -y), (x, y), (-x, y)]), [tr([(-x + w, -y + w), (x - w, -y + w), (x - w, y - w), (-x + w, y - w)])]
        if t == 'IfcCircleProfileDef':
            r = float(p.Radius)
            return tr([(r * math.cos(a), r * math.sin(a)) for a in (2 * math.pi * i / CIRCLE_SEGMENTS for i in range(CIRCLE_SEGMENTS))]), []
        if t == 'IfcCircleHollowProfileDef':
            r = float(p.Radius); w = float(p.WallThickness)
            ring = lambda rr: tr([(rr * math.cos(a), rr * math.sin(a)) for a in (2 * math.pi * i / CIRCLE_SEGMENTS for i in range(CIRCLE_SEGMENTS))])
            return ring(r), [ring(r - w)]
        if t == 'IfcEllipseProfileDef':
            a = float(p.SemiAxis1); b = float(p.SemiAxis2)
            return tr(self._arc((0.0, 0.0), a, b, 0.0, 0.0, 2 * math.pi)[:-1]), []
        if t in SHAPE_PROFILES:
            if any(getattr(p, a, None) for a in ('FilletRadius', 'EdgeRadius', 'InternalFilletRadius')):
                self.stats['approx:profile_fillets_ignored'] += 1
            self.stats['profile:' + t] += 1
            return tr(SHAPE_PROFILES[t](p)), []
        if t == 'IfcArbitraryClosedProfileDef':
            return self.curve_points(p.OuterCurve), []
        if t == 'IfcArbitraryProfileDefWithVoids':
            return self.curve_points(p.OuterCurve), [self.curve_points(c) for c in p.InnerCurves]
        raise Refused('IFC_PROFILE_NOT_IMPLEMENTED:' + t)

    def g_IfcExtrudedAreaSolid(self, it, m, out):
        outer, holes = self.profile(it.SweptArea)
        if len(outer) < 3:
            raise Refused('IFC_PROFILE_DEGENERATE')
        # outward orientation: outer loop counter-clockwise, holes clockwise
        if _area2(outer) < 0:
            outer = outer[::-1]
        holes = [h if _area2(h) <= 0 else h[::-1] for h in holes]
        mm = mul(m, axis2placement(it.Position))
        d = direction(it.ExtrudedDirection, (0.0, 0.0, 1.0)); depth = float(it.Depth)
        if d[2] * depth < 0:
            outer = outer[::-1]; holes = [h[::-1] for h in holes]
        off = tuple(c * depth for c in d)
        bottom = [(x, y, 0.0) for x, y in outer]; hb = [[(x, y, 0.0) for x, y in h] for h in holes]
        top = lambda pts: [(p[0] + off[0], p[1] + off[1], p[2] + off[2]) for p in pts]
        for tri in triangulate3d(bottom, hb):
            self._emit((tri[0], tri[2], tri[1]), mm, out)
            self._emit(tuple(top(list(tri))), mm, out)
        for loop in [bottom] + hb:
            for i in range(len(loop)):
                a = loop[i - 1]; b = loop[i]; at, bt = top([a, b])
                self._emit((a, b, bt), mm, out); self._emit((a, bt, at), mm, out)


# ----------------------------------------------------------------------- semantics

def arc_through(a, b, c):
    """2D points of the circular arc a -> b -> c (endpoints included); a straight polyline if collinear."""
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-15 * max(1.0, abs(ax) + abs(bx) + abs(cx)):
        return [a, b, c]
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    r = math.hypot(ax - ux, ay - uy)
    t0 = math.atan2(ay - uy, ax - ux); tm = math.atan2(by - uy, bx - ux); t1 = math.atan2(cy - uy, cx - ux)
    ccw = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) > 0
    norm_ = lambda x: x % (2 * math.pi)
    if ccw:
        sweep = norm_(t1 - t0)
    else:
        sweep = -norm_(t0 - t1)
    n = max(2, int(math.ceil(abs(sweep) / ARC_STEP)) + 1)
    pts = [(ux + r * math.cos(t0 + sweep * i / (n - 1)), uy + r * math.sin(t0 + sweep * i / (n - 1))) for i in range(n)]
    pts[0] = a; pts[-1] = c
    return pts


# ----------------------------------------------------------------------- convex polyhedra and clipping

def is_convex2d(pts):
    sign = 0
    n = len(pts)
    for i in range(n):
        ax, ay = pts[i - 1]; bx, by = pts[i]; cx, cy = pts[(i + 1) % n]
        z = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if abs(z) < 1e-15:
            continue
        s = 1 if z > 0 else -1
        if sign and s != sign:
            return False
        sign = s
    return sign != 0


def newell(poly):
    nx = ny = nz = 0.0
    for i in range(len(poly)):
        c = poly[i]; d = poly[(i + 1) % len(poly)]
        nx += (c[1] - d[1]) * (c[2] + d[2]); ny += (c[2] - d[2]) * (c[0] + d[0]); nz += (c[0] - d[0]) * (c[1] + d[1])
    L = math.sqrt(nx * nx + ny * ny + nz * nz)
    return None if L == 0 else (nx / L, ny / L, nz / L)


def planes_of(faces):
    """Outward planes (n, d) with n.p <= d inside, of a convex polyhedron given by its face polygons."""
    pts = [p for f in faces for p in f]
    cen = tuple(sum(p[k] for p in pts) / len(pts) for k in range(3))
    out = []
    for f in faces:
        n = newell(f)
        if n is None:
            continue
        d = dot(n, f[0])
        if dot(n, cen) > d:
            n = tuple(-v for v in n); d = -d
        out.append((n, d))
    return out


def split_polygon(poly, plane, eps):
    """(part with n.p <= d, part with n.p >= d) of a convex polygon."""
    n, d = plane
    dist = [dot(n, p) - d for p in poly]
    if max(dist) <= eps:          # inside or lying on the plane: all of it stays "inside"
        return poly, None
    if min(dist) >= -eps:
        return None, poly
    inside, outside = [], []
    k = len(poly)
    for i in range(k):
        p = poly[i]; q = poly[(i + 1) % k]
        sp = dot(n, p) - d; sq = dot(n, q) - d
        if sp <= eps:
            inside.append(p)
        if sp >= -eps:
            outside.append(p)
        if (sp < -eps and sq > eps) or (sp > eps and sq < -eps):
            t = sp / (sp - sq)
            x = tuple(p[j] + (q[j] - p[j]) * t for j in range(3))
            inside.append(x); outside.append(x)
    return (inside if len(inside) >= 3 else None), (outside if len(outside) >= 3 else None)


def _fan(poly, out):
    for i in range(1, len(poly) - 1):
        out.extend(poly[0]); out.extend(poly[i]); out.extend(poly[i + 1])


def subtract_convex(tris, planes, eps):
    """Triangles (flat array, 9 floats each) minus the inside of a convex polyhedron."""
    out = array('d')
    changed = False
    for k in range(0, len(tris), 9):
        tri = [tuple(tris[k + 3 * j:k + 3 * j + 3]) for j in range(3)]
        cur = tri; pieces = []
        for pl in planes:
            inside, outside = split_polygon(cur, pl, eps)
            if outside is not None:
                pieces.append(outside)
            cur = inside
            if cur is None:
                break
        if cur is None and len(pieces) == 1 and len(pieces[0]) == 3:
            out.extend(tris[k:k + 9])            # untouched triangle
            continue
        changed = True
        for poly in pieces:
            _fan(poly, out)
    return out, changed


def halfspace_caps(tris, plane, sides, eps):
    """Cap triangles closing a mesh cut by *plane* (kept side n.p >= d), clipped to *sides*.

    The cut outline is chained from the triangle/plane intersection segments; None when
    it does not form closed loops (open input mesh)."""
    n, d = plane
    segs = []
    for k in range(0, len(tris), 9):
        pts = [tuple(tris[k + 3 * j:k + 3 * j + 3]) for j in range(3)]
        s = [dot(n, p) - d for p in pts]
        cut = []
        for i in range(3):
            p, q = pts[i], pts[(i + 1) % 3]
            sp, sq = s[i], s[(i + 1) % 3]
            if abs(sp) <= eps and abs(sq) <= eps:
                continue                       # edge lying in the plane: shared by a cut face
            if abs(sp) <= eps:
                cut.append(p)
            elif (sp < -eps < eps < sq) or (sq < -eps < eps < sp):
                t = sp / (sp - sq)
                cut.append(tuple(p[j] + (q[j] - p[j]) * t for j in range(3)))
        uniq = []
        for p in cut:
            if all(math.dist(p, u) > 10 * eps for u in uniq):
                uniq.append(p)
        if len(uniq) == 2:
            segs.append(tuple(uniq))
    if not segs:
        return array('d')
    q = max(10 * eps, 1e-9)
    key = lambda p: tuple(round(c / (100 * q)) for c in p)
    adj = defaultdict(list)
    for i, (a, b) in enumerate(segs):
        adj[key(a)].append(i); adj[key(b)].append(i)
    if any(len(v) % 2 for v in adj.values()):
        return None
    used = [False] * len(segs)
    loops = []
    for i in range(len(segs)):
        if used[i]:
            continue
        used[i] = True
        a, b = segs[i]
        loop = [a, b]; start = key(a); cur = key(b)
        guard = 0
        while cur != start and guard <= len(segs):
            guard += 1
            nxt = next((j for j in adj[cur] if not used[j]), None)
            if nxt is None:
                return None
            used[nxt] = True
            x, y = segs[nxt]
            p = y if key(x) == cur else x
            loop.append(p); cur = key(p)
        if cur != start:
            return None
        loop.pop()
        if len(loop) >= 3:
            loops.append(loop)
    out = array('d')
    want = tuple(-c for c in n)                # cap faces the removed material
    for loop in loops:
        for tri in triangulate3d(loop):
            piece = clip_inside(list(tri), sides, eps) if sides else list(tri)
            if piece is None:
                continue
            nn = newell(piece)
            if nn is not None and dot(nn, want) < 0:
                piece = piece[::-1]
            _fan(piece, out)
    return out


def signed_volume(tris):
    v = 0.0
    for k in range(0, len(tris) - 8, 9):
        ax, ay, az, bx, by, bz, cx, cy, cz = tris[k:k + 9]
        v += ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)
    return v / 6


def orient_outward(tris):
    """The triangles with their order flipped when the enclosed signed volume is negative."""
    if signed_volume(tris) >= 0:
        return tris
    out = array('d')
    for k in range(0, len(tris) - 8, 9):
        out.extend(tris[k:k + 3]); out.extend(tris[k + 6:k + 9]); out.extend(tris[k + 3:k + 6])
    return out


def convex_mesh_planes(tris, eps):
    """Outward planes when the triangle mesh bounds a convex region, else None."""
    pts = [tuple(tris[k:k + 3]) for k in range(0, len(tris), 3)]
    if len(pts) < 12:
        return None
    cen = tuple(sum(p[i] for p in pts) / len(pts) for i in range(3))
    planes = []
    for k in range(0, len(tris) - 8, 9):
        tri = [tuple(tris[k + 3 * j:k + 3 * j + 3]) for j in range(3)]
        n = newell(tri)
        if n is None:
            continue
        d = dot(n, tri[0])
        if dot(n, cen) > d:
            n = tuple(-c for c in n); d = -d
        if any(abs(dot(n, pn) - 1) < 1e-9 and abs(d - pd) <= eps for pn, pd in planes):
            continue
        planes.append((n, d))
        if len(planes) > 64:
            return None
    for n, d in planes:
        if any(dot(n, p) - d > eps for p in pts):
            return None
    return planes if len(planes) >= 4 else None


def clip_inside(poly, planes, eps):
    cur = poly
    for pl in planes:
        cur, _ = split_polygon(cur, pl, eps)
        if cur is None:
            return None
    return cur


# ----------------------------------------------------------------------- product level

BODY_IDS = {'body', 'facetation', 'mesh', 'body-fallback', 'brep', 'surface'}
BODY_TYPES = {'Tessellation', 'Brep', 'SweptSolid', 'MappedRepresentation', 'SurfaceModel', 'AdvancedSweptSolid',
              'Clipping', 'CSG'}


def angle_scale_of(model, stats):
    for ua in model.by_type('IfcUnitAssignment'):
        for u in ua.Units or []:
            try:
                if getattr(u, 'UnitType', None) != 'PLANEANGLEUNIT':
                    continue
                if u.is_a('IfcSIUnit'):
                    return 1.0
                if u.is_a('IfcConversionBasedUnit'):
                    f = u.ConversionFactor.ValueComponent
                    f = float(f.wrappedValue if hasattr(f, 'wrappedValue') else f)
                    stats['angle_unit:' + str(u.Name).lower()] += 1
                    return f
            except (AttributeError, TypeError, ValueError):
                continue
    stats['angle_unit_assumed_radian'] += 1
    return 1.0


class Tessellator:
    """World triangles per product, with opening subtraction and per-reason refusal counting."""

    def __init__(self, model, stats=None):
        self.model = model
        self.stats = stats if stats is not None else Counter()
        self.geo = Geometry(self.stats, angle_scale_of(model, self.stats))
        self.pcache = {}
        self.voids = defaultdict(list)
        for r in model.by_type('IfcRelVoidsElement'):
            self.voids[r.RelatingBuildingElement.id()].append(r.RelatedOpeningElement)
        self._open_cache = {}

    def placement(self, p, depth=0):
        if p is None:
            return IDENTITY
        key = p.id()
        if key in self.pcache:
            return self.pcache[key]
        if depth > 64:
            raise Refused('IFC_PLACEMENT_DEPTH:' + p.is_a())
        if not p.is_a('IfcLocalPlacement'):
            raise Refused('IFC_PLACEMENT_NOT_IMPLEMENTED:' + p.is_a())
        m = mul(self.placement(p.PlacementRelTo, depth + 1), axis2placement(p.RelativePlacement))
        self.pcache[key] = m
        return m

    @staticmethod
    def bodies(prod):
        rep = getattr(prod, 'Representation', None)
        if rep is None:
            return []
        reps = list(rep.Representations or [])
        # Only shape representations carry body geometry; topology and other
        # representation subtypes (e.g. IfcTopologyRepresentation) are skipped.
        reps = [r for r in reps if r.is_a('IfcShapeRepresentation')]
        bodies = [r for r in reps if str(getattr(r, 'RepresentationIdentifier', None) or '').lower() in BODY_IDS]
        return bodies or [r for r in reps if str(getattr(r, 'RepresentationType', None) or '') in BODY_TYPES]

    def prism_faces(self, solid, m):
        """World face polygons of an IfcExtrudedAreaSolid with a convex hole-free profile, else None."""
        if not solid.is_a('IfcExtrudedAreaSolid'):
            return None
        outer, holes = self.geo.profile(solid.SweptArea)
        if holes or len(outer) < 3 or not is_convex2d(outer):
            return None
        mm = mul(m, axis2placement(solid.Position))
        d = direction(solid.ExtrudedDirection, (0.0, 0.0, 1.0)); depth = float(solid.Depth)
        o = tuple(c * depth for c in d)
        base = [apply(mm, (x, y, 0.0)) for x, y in outer]
        top = [apply(mm, (x + o[0], y + o[1], o[2])) for x, y in outer]
        faces = [base, top[::-1]]
        n = len(base)
        for i in range(n):
            j = (i + 1) % n
            faces.append([base[i], base[j], top[j], top[i]])
        return faces

    def opening_prisms(self, opening):
        """[(faces, planes, tris)] of an opening, or raises Refused.

        faces/planes describe a convex body (an extrusion with a convex profile or any
        convex closed mesh) and are None for a non-convex body, which is subtracted by
        the mesh boolean only; tris is the body mesh (built on demand for prisms)."""
        key = opening.id()
        if key in self._open_cache:
            return self._open_cache[key]
        m = self.placement(opening.ObjectPlacement)
        out = []
        for r in self.bodies(opening):
            for it in r.Items or []:
                faces = self.prism_faces(it, m)
                if faces is not None:
                    out.append([faces, planes_of(faces), None, it, m])
                    continue
                tris = array('d')
                self.geo.item(it, m, tris)
                if not tris:
                    raise Refused('IFC_OPENING_EMPTY_BODY:' + it.is_a())
                lo = min(tris); hi = max(tris)
                planes = convex_mesh_planes(tris, 1e-7 * max(1.0, abs(lo), abs(hi)))
                faces = None
                if planes is not None:
                    faces = [[tuple(tris[k + 3 * j:k + 3 * j + 3]) for j in range(3)] for k in range(0, len(tris), 9)]
                    self.stats['opening:convex_mesh'] += 1
                out.append([faces, planes, tris, it, m])
        if not out:
            raise Refused('IFC_OPENING_WITHOUT_BODY:' + opening.is_a())
        self._open_cache[key] = out
        return out

    def _opening_mesh(self, entry):
        if entry[2] is None:
            tris = array('d')
            self.geo.item(entry[3], entry[4], tris)
            entry[2] = tris
        return entry[2]

    def product(self, prod):
        """{'items': [(item, array of 9-float triangles)], 'refused': Counter, 'ok': n, 'bad': n}."""
        result = {'items': [], 'refused': Counter(), 'ok': 0, 'bad': 0}
        try:
            m = self.placement(prod.ObjectPlacement)
        except Refused as error:
            result['refused'][str(error)] += 1; result['bad'] += 1
            return result
        hosts = []
        for r in self.bodies(prod):
            for it in r.Items or []:
                out = array('d')
                try:
                    self.geo.item(it, m, out)
                except Refused as error:
                    result['refused'][str(error)] += 1; result['bad'] += 1; continue
                except (AttributeError, TypeError, IndexError, ValueError, ZeroDivisionError) as error:
                    result['refused']['IFC_GEOMETRY_ERROR:%s:%s' % (it.is_a(), type(error).__name__)] += 1
                    result['bad'] += 1; continue
                if out:
                    hosts.append([it, out, m]); result['ok'] += 1
        openings = self.voids.get(prod.id(), [])
        if openings and hosts:
            self._subtract(hosts, openings, result)
        result['items'] = [(it, out) for it, out, _m in hosts]
        return result

    def _subtract(self, hosts, openings, result):
        import mesh_csg
        prisms = []
        for op in openings:
            try:
                prisms.extend(self.opening_prisms(op))
            except Refused as error:
                result['refused'][str(error)] += 1; result['bad'] += 1
            except (AttributeError, TypeError, IndexError, ValueError, ZeroDivisionError) as error:
                result['refused']['IFC_OPENING_ERROR:%s' % type(error).__name__] += 1; result['bad'] += 1
        for host in hosts:
            it, tris, m = host
            lo = [min(tris[k::3]) for k in range(3)]; hi = [max(tris[k::3]) for k in range(3)]
            eps = 1e-9 * max(1.0, max(abs(v) for v in lo + hi))
            try:
                host_faces = self.prism_faces(it, m)
            except Refused:
                host_faces = None
            host_planes = planes_of(host_faces) if host_faces else None
            mesh_ops = []
            for entry in prisms:
                faces, planes = entry[0], entry[1]
                if planes is None or host_planes is None:
                    mesh_ops.append(entry)
                    continue
                tris, changed = subtract_convex(tris, planes, eps)
                if not changed:
                    continue
                self.stats['opening:subtracted'] += 1
                for f in faces:
                    n = newell(f)
                    if n is None:
                        continue
                    d = dot(n, f[0])
                    if any(abs(abs(dot(n, hn)) - 1) < 1e-9 and abs(d - dot(n, hn) * hd) <= 1e3 * eps for hn, hd in host_planes):
                        continue                  # coplanar with a host face: would close the hole
                    piece = clip_inside(f, host_planes, eps)
                    if piece is not None:
                        _fan(piece, tris)
                        self.stats['opening:reveal_faces'] += 1
            # non-convex openings, and any opening of a host that is not a convex extrusion:
            # own BSP mesh boolean (the cut walls come from the opening body)
            for entry in mesh_ops:
                try:
                    cutter = self._opening_mesh(entry)
                except Refused as error:
                    result['refused']['IFC_OPENING_NOT_MESHED:' + str(error)] += 1; result['bad'] += 1
                    continue
                if not mesh_csg.boxes_overlap(mesh_csg.bbox(tris), mesh_csg.bbox(cutter), 1e3 * eps):
                    continue
                try:
                    tris = mesh_csg.subtract(orient_outward(tris), orient_outward(cutter))
                    self.stats['opening:csg_subtracted'] += 1
                except mesh_csg.CsgBudget:
                    if entry[1] is not None:
                        tris, changed = subtract_convex(tris, entry[1], eps)
                        self.stats['opening:subtracted'] += int(changed)
                        self.stats['opening:reveals_not_generated_csg_budget'] += 1
                    else:
                        result['refused']['IFC_OPENING_CSG_BUDGET_EXCEEDED:' + entry[3].is_a()] += 1
                        result['bad'] += 1
            host[1] = tris
