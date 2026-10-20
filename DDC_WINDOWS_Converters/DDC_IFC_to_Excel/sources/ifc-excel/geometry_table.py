"""Geometry sheet for IFC to Excel: per product tessellation status from the shared own module.

Uses ``sources/ifc-independent/geometry.py`` (the same code as DDC Viewer).  One row per
product with a body representation: status (DECODED / PARTIAL / REFUSED), triangle count,
world bounding box and surface area in model length units, and every refusal reason with
its count.  Nothing is estimated: an element without decoded geometry has empty numbers.
"""
import json
import math


def _area(arr):
    total = 0.0
    for k in range(0, len(arr), 9):
        ax, ay, az, bx, by, bz, cx, cy, cz = arr[k:k + 9]
        ux, uy, uz = bx - ax, by - ay, bz - az
        vx, vy, vz = cx - ax, cy - ay, cz - az
        total += math.sqrt((uy * vz - uz * vy) ** 2 + (uz * vx - ux * vz) ** 2 + (ux * vy - uy * vx) ** 2) / 2
    return total


def emit_geometry(model, tables, ref):
    """Emit the Geometry table; returns counts per status and the refusal totals."""
    import geometry  # own shared module (ifc-independent), importable through core_runtime
    tess = geometry.Tessellator(model)
    counts = {'DECODED': 0, 'PARTIAL': 0, 'REFUSED': 0}
    refused_total = {}
    for prod in model.by_type('IfcProduct'):
        if prod.is_a('IfcOpeningElement') or not tess.bodies(prod):
            continue
        res = tess.product(prod)
        tris = sum(len(a) // 9 for _it, a in res['items'])
        status = 'DECODED' if res['ok'] and not res['bad'] else ('PARTIAL' if res['ok'] else 'REFUSED')
        counts[status] += 1
        for key, n in res['refused'].items():
            refused_total[key] = refused_total.get(key, 0) + n
        lo = hi = None
        area = None
        if tris:
            xs = [v for _it, a in res['items'] for v in a[0::3]]
            ys = [v for _it, a in res['items'] for v in a[1::3]]
            zs = [v for _it, a in res['items'] for v in a[2::3]]
            lo, hi = [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]
            area = sum(_area(a) for _it, a in res['items'])
        tables.emit('Geometry', {
            'step_id': ref(prod), 'ifc_class': prod.is_a(), 'GlobalId': getattr(prod, 'GlobalId', None),
            'status': status, 'triangles': tris, 'bbox_min': json.dumps(lo) if lo else None,
            'bbox_max': json.dumps(hi) if hi else None, 'surface_area_model_units': area,
            'refusals': json.dumps(dict(sorted(res['refused'].items())), ensure_ascii=False) if res['refused'] else None})
    return {'geometry_status': counts, 'geometry_refusals': dict(sorted(refused_total.items())),
            'geometry_counts': dict(sorted(tess.stats.items()))}
