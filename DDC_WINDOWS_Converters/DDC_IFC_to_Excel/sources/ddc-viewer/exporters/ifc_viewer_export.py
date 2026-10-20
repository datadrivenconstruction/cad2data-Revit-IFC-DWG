"""DDC Viewer package from an IFC file (Python stdlib + the own DDC IFC reader).

Reads the file with ``sources/ifc-independent/model.py`` (own STEP/EXPRESS
reader; no third-party IFC library) and writes ``ddc-viewer-package/1``:

* spatial tree (IfcRelAggregates + IfcRelContainedInSpatialStructure),
* per element: attributes, property sets (occurrence and type), quantities with
  units, materials (layer sets, constituents, lists),
* triangulated geometry from the own shared module
  ``sources/ifc-independent/geometry.py`` (``Tessellator``: implemented item
  subset, advanced B-rep faces, opening subtraction and boolean differences by
  exact convex clipping or the own mesh boolean, curved profiles); every refusal
  is counted per reason and IFC type, an element with a refused item or
  opening is ``PARTIAL``.

The RVT path uses the same exporter on the IFC written by our RVT converter
(``--format RVT --rvt-report report.json``).
"""
import argparse
import base64
import gzip
import hashlib
import json
import math
import struct
import sys
from array import array
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA = 'ddc-viewer-package/1'
PRODUCER = 'ddc-viewer/exporters/ifc_viewer_export'
HERE = Path(__file__).resolve().parent
DEFAULT_READER = HERE.parent.parent / 'ifc-independent'
MAX_VERTICES_PER_MESH = 1_000_000
SPATIAL = ('IfcProject', 'IfcSite', 'IfcBuilding', 'IfcBuildingStorey', 'IfcSpace', 'IfcFacility', 'IfcFacilityPart',
           'IfcBridge', 'IfcRoad', 'IfcRailway', 'IfcMarineFacility')
CLASS_COLOURS = {
    'IfcWall': '#d8dde3', 'IfcWallStandardCase': '#d8dde3', 'IfcCurtainWall': '#9cc3e6', 'IfcSlab': '#c4c9cf',
    'IfcRoof': '#b06c4f', 'IfcBeam': '#8fa3b8', 'IfcColumn': '#8fa3b8', 'IfcMember': '#9aaabb',
    'IfcPlate': '#9cc3e6', 'IfcWindow': '#8ec5ff', 'IfcDoor': '#b88b5c', 'IfcStair': '#c9b79c',
    'IfcStairFlight': '#c9b79c', 'IfcRailing': '#6f7c8a', 'IfcFooting': '#a7a29a', 'IfcPile': '#a7a29a',
    'IfcSpace': '#7fd1ae', 'IfcFurnishingElement': '#d9a86c', 'IfcFurniture': '#d9a86c',
    'IfcBuildingElementProxy': '#c3b4d6', 'IfcCovering': '#e6dccb', 'IfcFlowSegment': '#6cb2a8',
    'IfcFlowTerminal': '#6cb2a8', 'IfcFlowFitting': '#6cb2a8', 'IfcOpeningElement': '#ff6b6b',
}
TRANSPARENT_CLASSES = {'IfcWindow': 0.45, 'IfcSpace': 0.18, 'IfcOpeningElement': 0.15, 'IfcCurtainWall': 0.55,
                       'IfcPlate': 0.6}


# Geometry (tessellation, openings, curves) lives in sources/ifc-independent/geometry.py.


# ----------------------------------------------------------------------- semantics

def value_of(v):
    if v is None:
        return None
    if hasattr(v, 'wrappedValue'):
        return value_of(v.wrappedValue)
    if isinstance(v, (list, tuple)):
        return [value_of(x) for x in v]
    if hasattr(v, 'is_a'):
        return '#%d %s' % (v.id(), v.is_a())
    return v


UNIT_SYMBOLS = {('LENGTHUNIT', None, 'METRE'): 'm', ('LENGTHUNIT', 'MILLI', 'METRE'): 'mm',
                ('LENGTHUNIT', 'CENTI', 'METRE'): 'cm', ('AREAUNIT', None, 'SQUARE_METRE'): 'm²',
                ('AREAUNIT', 'MILLI', 'SQUARE_METRE'): 'mm²', ('VOLUMEUNIT', None, 'CUBIC_METRE'): 'm³',
                ('VOLUMEUNIT', 'MILLI', 'CUBIC_METRE'): 'mm³', ('MASSUNIT', 'KILO', 'GRAM'): 'kg',
                ('PLANEANGLEUNIT', None, 'RADIAN'): 'rad', ('TIMEUNIT', None, 'SECOND'): 's'}


def unit_table(model):
    units = {}
    for ua in model.by_type('IfcUnitAssignment'):
        for u in ua.Units or []:
            try:
                if u.is_a('IfcSIUnit'):
                    key = (u.UnitType, u.Prefix, u.Name)
                    units[u.UnitType] = UNIT_SYMBOLS.get(key, ((u.Prefix or '') + ' ' + str(u.Name)).strip().lower())
                elif u.is_a('IfcConversionBasedUnit'):
                    units[u.UnitType] = str(u.Name).lower()
            except AttributeError:
                continue
    return units


QUANTITY_KIND = {'IfcQuantityLength': ('LengthValue', 'LENGTHUNIT'), 'IfcQuantityArea': ('AreaValue', 'AREAUNIT'),
                 'IfcQuantityVolume': ('VolumeValue', 'VOLUMEUNIT'), 'IfcQuantityCount': ('CountValue', None),
                 'IfcQuantityWeight': ('WeightValue', 'MASSUNIT'), 'IfcQuantityTime': ('TimeValue', 'TIMEUNIT'),
                 'IfcQuantityNumber': ('NumberValue', None)}


def pset_values(pdef, units):
    out = {}
    t = pdef.is_a()
    if t == 'IfcElementQuantity':
        for q in pdef.Quantities or []:
            kind = QUANTITY_KIND.get(q.is_a())
            if not kind:
                out[q.Name] = '(%s)' % q.is_a(); continue
            v = getattr(q, kind[0], None)
            unit = units.get(kind[1]) if kind[1] else None
            out[q.Name] = {'value': v, 'unit': unit} if unit else v
        return out
    if t in ('IfcPropertySet',):
        for p in pdef.HasProperties or []:
            pt = p.is_a()
            try:
                if pt == 'IfcPropertySingleValue':
                    out[p.Name] = value_of(p.NominalValue)
                elif pt == 'IfcPropertyEnumeratedValue':
                    out[p.Name] = ', '.join(str(value_of(v)) for v in (p.EnumerationValues or []))
                elif pt == 'IfcPropertyListValue':
                    out[p.Name] = ', '.join(str(value_of(v)) for v in (p.ListValues or []))
                elif pt == 'IfcPropertyBoundedValue':
                    out[p.Name] = '%s … %s' % (value_of(p.LowerBoundValue), value_of(p.UpperBoundValue))
                else:
                    out[p.Name] = '(%s)' % pt
            except AttributeError:
                out[getattr(p, 'Name', '?')] = '(unreadable %s)' % pt
        return out
    return {'(definition)': t}


def material_names(mat):
    t = mat.is_a()
    if t == 'IfcMaterial':
        return [mat.Name]
    if t == 'IfcMaterialLayerSetUsage':
        return material_names(mat.ForLayerSet)
    if t == 'IfcMaterialLayerSet':
        return ['%s (%s)' % (l.Material.Name if l.Material else '?', l.LayerThickness) for l in mat.MaterialLayers]
    if t == 'IfcMaterialList':
        return [m.Name for m in mat.Materials]
    if t == 'IfcMaterialConstituentSet':
        return [c.Material.Name if c.Material else (c.Name or '?') for c in (mat.MaterialConstituents or [])]
    if t == 'IfcMaterialProfileSetUsage':
        return material_names(mat.ForProfileSet)
    if t == 'IfcMaterialProfileSet':
        return [p.Material.Name if p.Material else '?' for p in (mat.MaterialProfiles or [])]
    if t == 'IfcMaterialLayer':
        return [mat.Material.Name if mat.Material else '?']
    return ['(%s)' % t]


def surface_colour(style_owner):
    """(hex, opacity) of an IfcStyledItem's surface style, or None."""
    styles = list(style_owner.Styles or [])
    flat = []
    for s in styles:
        if s.is_a('IfcPresentationStyleAssignment'):
            flat.extend(s.Styles or [])
        else:
            flat.append(s)
    for s in flat:
        if not s.is_a('IfcSurfaceStyle'):
            continue
        for e in s.Styles or []:
            if e.is_a('IfcSurfaceStyleShading'):
                c = e.SurfaceColour
                rgb = '#%02x%02x%02x' % tuple(max(0, min(255, round(float(v) * 255))) for v in (c.Red, c.Green, c.Blue))
                tr = getattr(e, 'Transparency', None)
                return rgb, 1.0 - float(tr) if tr is not None else 1.0
    return None


# ----------------------------------------------------------------------- export

class Buffers:
    def __init__(self):
        self.items = []

    def add(self, typecode, values):
        data = values if isinstance(values, array) else array(typecode, values)
        if sys.byteorder != 'little':
            data = array(typecode, data); data.byteswap()
        self.items.append({'id': len(self.items), 'dtype': {'f': 'f32', 'I': 'u32'}[typecode], 'count': len(data),
                           'data': base64.b64encode(data.tobytes()).decode('ascii')})
        return len(self.items) - 1


def load_reader(reader_dir):
    reader_dir = Path(reader_dir).resolve()
    if not (reader_dir / 'core_model.py').is_file():
        raise SystemExit('DDC IFC reader not found: %s' % reader_dir)
    sys.path.insert(0, str(reader_dir))
    import core_model as ifc_model  # own schema-free reader (no buildingSMART schema data loaded)
    import geometry as ifc_geometry  # own tessellation (shared with IFC to Excel)
    return ifc_model, ifc_geometry


def build_package(source, *, reader_dir=DEFAULT_READER, fmt='IFC', rvt_report=None, cancel_event=None):
    ifc_model, geometry = load_reader(reader_dir)
    source = Path(source).resolve(strict=True)
    raw = source.read_bytes()
    model = ifc_model.model_from_file(source, cancel_event=cancel_event)
    stats = Counter(); tess = geometry.Tessellator(model, stats)
    units = unit_table(model)

    # styles: representation item id -> (colour, opacity)
    item_style = {}
    for si in model.by_type('IfcStyledItem'):
        if si.Item is not None:
            c = surface_colour(si)
            if c:
                item_style[si.Item.id()] = c
    material_style = {}
    for mdr in model.by_type('IfcMaterialDefinitionRepresentation'):
        for rep in mdr.Representations or []:
            for it in rep.Items or []:
                if it.is_a('IfcStyledItem'):
                    c = surface_colour(it)
                    if c:
                        material_style[mdr.RepresentedMaterial.id()] = c

    # relationships
    children = defaultdict(list)       # spatial/aggregate parent id -> [child]
    contained = defaultdict(list)
    parent_of = {}
    for r in model.by_type('IfcRelAggregates'):
        for o in r.RelatedObjects or []:
            children[r.RelatingObject.id()].append(o); parent_of[o.id()] = r.RelatingObject
    for r in model.by_type('IfcRelContainedInSpatialStructure'):
        for o in r.RelatedElements or []:
            contained[r.RelatingStructure.id()].append(o); parent_of.setdefault(o.id(), r.RelatingStructure)
    psets = defaultdict(dict)
    for r in model.by_type('IfcRelDefinesByProperties'):
        pdef = r.RelatingPropertyDefinition
        if pdef is None or not hasattr(pdef, 'is_a'):
            continue
        try:
            values = pset_values(pdef, units)
        except AttributeError:
            values = {'(error)': 'unreadable'}
        group = ('Qto: ' if pdef.is_a('IfcElementQuantity') else '') + (pdef.Name or pdef.is_a())
        for o in r.RelatedObjects or []:
            psets[o.id()][group] = values
    types = {}
    for r in model.by_type('IfcRelDefinesByType'):
        for o in r.RelatedObjects or []:
            types[o.id()] = r.RelatingType
    materials = defaultdict(list); first_material = {}
    for r in model.by_type('IfcRelAssociatesMaterial'):
        mat = r.RelatingMaterial
        try:
            names = material_names(mat)
        except AttributeError:
            names = ['(%s)' % mat.is_a()]
        base = mat
        while base is not None and not base.is_a('IfcMaterial'):
            nxt = None
            for attr in ('ForLayerSet', 'ForProfileSet'):
                if getattr(base, attr, None) is not None:
                    nxt = getattr(base, attr)
            if nxt is None:
                lst = getattr(base, 'MaterialLayers', None) or getattr(base, 'Materials', None) or getattr(base, 'MaterialConstituents', None)
                if lst:
                    first = lst[0]
                    nxt = first if first.is_a('IfcMaterial') else getattr(first, 'Material', None)
            base = nxt
        for o in r.RelatedObjects or []:
            materials[o.id()].extend(n for n in names if n)
            if base is not None:
                first_material.setdefault(o.id(), base.id())
    voids = Counter(r.RelatingBuildingElement.id() for r in model.by_type('IfcRelVoidsElement'))

    entities = []; ent_of = {}
    def entity(o, has_geometry=False):
        if o.id() in ent_of:
            return ent_of[o.id()]
        cls = o.is_a()
        attrs = {}
        for name in ('GlobalId', 'Name', 'Description', 'ObjectType', 'LongName', 'Tag', 'PredefinedType', 'Elevation'):
            try:
                v = getattr(o, name)
            except AttributeError:
                continue
            if v is not None:
                attrs[name] = value_of(v)
        attrs['IFC class'] = cls; attrs['STEP id'] = '#%d' % o.id()
        props = {'Attributes': attrs}
        for grp, vals in sorted(psets.get(o.id(), {}).items()):
            props[grp] = vals
        ty = types.get(o.id())
        if ty is not None:
            tattrs = {'Type class': ty.is_a(), 'Type name': ty.Name}
            props['Type'] = {k: value_of(v) for k, v in tattrs.items() if v is not None}
            for pd in getattr(ty, 'HasPropertySets', None) or []:
                try:
                    props['Type: ' + (pd.Name or pd.is_a())] = pset_values(pd, units)
                except AttributeError:
                    pass
        if materials.get(o.id()):
            props['Materials'] = {str(i + 1): n for i, n in enumerate(materials[o.id()])}
        storey = None
        p = parent_of.get(o.id()); guard = 0
        while p is not None and guard < 32:
            if p.is_a('IfcBuildingStorey'):
                storey = p.Name; break
            p = parent_of.get(p.id()); guard += 1
        e = {'id': len(entities), 'guid': attrs.get('GlobalId'), 'name': attrs.get('Name') or '', 'type': cls,
             'storey': storey, 'material': (materials.get(o.id()) or [None])[0], 'coverage': 'NO_GEOMETRY', 'props': props}
        if voids.get(o.id()):
            props['Attributes']['Openings'] = voids[o.id()]
        entities.append(e); ent_of[o.id()] = e['id']
        return e['id']

    # spatial tree
    def tree(o, depth=0):
        node = {'name': (getattr(o, 'Name', None) or getattr(o, 'LongName', None) or o.is_a()), 'type': o.is_a(),
                'entity': entity(o), 'children': []}
        if depth > 32:
            return node
        for c in children.get(o.id(), []):
            if any(c.is_a(s) for s in SPATIAL):
                node['children'].append(tree(c, depth + 1))
            else:
                node['children'].append({'name': c.Name or c.is_a(), 'type': c.is_a(), 'entity': entity(c), 'children': []})
        elems = contained.get(o.id(), [])
        if elems:
            node['elements'] = [entity(e) for e in elems]
            for e in elems:
                for sub in children.get(e.id(), []):
                    node['elements'].append(entity(sub))
        return node
    roots = [tree(p) for p in model.by_type('IfcProject')]

    # geometry
    materials_out = []; mat_index = {}
    def material_slot(colour, opacity):
        key = (colour, round(opacity, 3))
        if key not in mat_index:
            mat_index[key] = len(materials_out); materials_out.append({'colour': colour, 'opacity': round(opacity, 3)})
        return mat_index[key]

    per_entity = []   # (entity id, material slot, array('d') of tri coords)
    lo = [math.inf] * 3; hi = [-math.inf] * 3
    refused = Counter()
    for prod in model.by_type('IfcProduct'):
        if getattr(prod, 'Representation', None) is None:
            continue
        cls = prod.is_a()
        if cls == 'IfcOpeningElement':
            stats['skipped:IfcOpeningElement'] += 1
            continue
        eid = entity(prod)
        if not tess.bodies(prod):
            stats['no_body_representation'] += 1
            continue
        res = tess.product(prod)
        for key, n in res['refused'].items():
            refused[key] += n
        for it, out in res['items']:
            style = item_style.get(it.id())
            if style is None and first_material.get(prod.id()) in material_style:
                style = material_style[first_material[prod.id()]]
            if style is None:
                colour = CLASS_COLOURS.get(cls, '#c8ced6'); opacity = TRANSPARENT_CLASSES.get(cls, 1.0)
            else:
                colour, opacity = style
            for k in range(0, len(out), 3):
                for ax in range(3):
                    v = out[k + ax]
                    if v < lo[ax]: lo[ax] = v
                    if v > hi[ax]: hi[ax] = v
            per_entity.append((eid, material_slot(colour, opacity), out))
        ok, bad = res['ok'], res['bad']
        entities[eid]['coverage'] = 'DECODED' if ok and not bad else ('PARTIAL' if ok else 'REFUSED')
        if res['items']:
            entities[eid]['has_geometry'] = True

    if not per_entity:
        lo = [0.0] * 3; hi = [0.0] * 3
    origin = [(a + b) / 2 for a, b in zip(lo, hi)]
    buffers = Buffers()
    meshes = []
    pos = array('f'); idx = array('I'); ranges = array('I'); nv = 0
    def flush():
        nonlocal pos, idx, ranges, nv
        if nv:
            meshes.append({'positions': buffers.add('f', pos), 'indices': buffers.add('I', idx), 'ranges': buffers.add('I', ranges)})
        pos = array('f'); idx = array('I'); ranges = array('I'); nv = 0
    # merge consecutive items of the same entity+material into one range
    per_entity.sort(key=lambda t: (t[0], t[1]))
    i = 0
    while i < len(per_entity):
        eid, slot, _ = per_entity[i]
        group = []
        while i < len(per_entity) and per_entity[i][0] == eid and per_entity[i][1] == slot:
            group.append(per_entity[i][2]); i += 1
        count = sum(len(g) for g in group) // 3
        if nv + count > MAX_VERTICES_PER_MESH:
            flush()
        start = nv
        # weld identical vertices inside the range to shrink the package
        weld = {}
        for g in group:
            for k in range(0, len(g), 3):
                key = (round(g[k] - origin[0], 5), round(g[k + 1] - origin[1], 5), round(g[k + 2] - origin[2], 5))
                v = weld.get(key)
                if v is None:
                    v = weld[key] = nv; nv += 1
                    pos.extend(key)
                idx.append(v)
        ranges.extend((eid, start, nv - start, slot))
    flush()

    tri_count = sum(b['count'] for b in buffers.items[1::3]) // 3 if buffers.items else 0
    n_geo = sum(1 for e in entities if e.get('has_geometry'))
    cov = Counter(e['coverage'] for e in entities)
    report = None
    if rvt_report:
        try:
            report = json.loads(Path(rvt_report).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            report = None
    view = {'id': 'v0', 'name': '3D', 'kind': '3d', 'origin': origin,
            'extent': {'min': [a - o for a, o in zip(lo, origin)], 'max': [b - o for b, o in zip(hi, origin)]},
            'meshes': meshes}
    doc = {
        'schema': SCHEMA, 'format': fmt, 'title': source.name,
        'source': {'name': source.name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'ifc_schema': model.schema if hasattr(model, 'schema') else None},
        'producer': {'name': PRODUCER, 'reader': 'DDC IFC core reader (sources/ifc-independent/core_model.py, schema-free)'},
        'units': {'length': units.get('LENGTHUNIT'), 'area': units.get('AREAUNIT'), 'volume': units.get('VOLUMEUNIT'),
                  'status': 'FROM_IFCUNITASSIGNMENT' if units.get('LENGTHUNIT') else 'UNRESOLVED', 'scale_applied': False},
        'up_axis': 'Z',
        'coverage': {
            'state': 'PARTIAL' if refused or cov.get('PARTIAL') else 'COMPLETE_FOR_IMPLEMENTED_SUBSET',
            'can_convert': False,
            'elements': len(entities), 'elements_with_geometry': n_geo, 'triangles': tri_count,
            'counts': dict(sorted(cov.items())),
            'refused_items': dict(sorted(refused.items())),
            'scene_counts': dict(sorted(stats.items())),
            'approximations': [
                'Openings: convex openings in convex extruded hosts are cut exactly with reveals; every other opening is cut by the own mesh boolean (reveals from the opening body). Boolean DIFFERENCE: half-spaces clipped exactly (convex bounds) or by the mesh boolean (non-convex bounds, solid operands); above the work budget the first operand is kept and counted.',
                'Advanced B-rep faces (planes, cylinders, cones, spheres, tori, revolution / extrusion surfaces, B-spline surfaces) are trimmed in their parameter plane and tessellated per %d segments per turn; faces that cannot be meshed are skipped and counted.' % geometry.CIRCLE_SEGMENTS,
                'Curves (circles, ellipses, arcs, trimmed and composite curves) are tessellated with %d segments per full turn.' % geometry.CIRCLE_SEGMENTS,
                'Colours: IfcStyledItem surface colour, else material style, else a neutral colour per IFC class.',
                'Units are reported from IfcUnitAssignment; coordinates are not rescaled.'],
        },
        'materials': materials_out,
        'tree': {'spatial': roots},
        'views': [view],
        'entities': entities,
        'buffers': buffers.items,
    }
    if fmt == 'RVT':
        doc['coverage']['rvt_source'] = {'note': 'Geometry and properties come from the IFC written by our RVT converter.',
                                         'report': None if not isinstance(report, dict) else {
                                             'schema': report.get('schema'),
                                             'source_sha256': (report.get('source') or {}).get('sha256'),
                                             'engine_commit': (report.get('build') or {}).get('git_commit'),
                                             'engine_version': (report.get('build') or {}).get('package_version')}}
    return doc


def _container(kind, payload, header, compress):
    """One ``.js`` file: ``(window.<kind>=window.<kind>||[]).push(<container>);`` (ddc-viewer-container/1)."""
    text = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    box = {'schema': 'ddc-viewer-container/1'}
    box.update(header)
    if compress:
        raw = gzip.compress(text.encode('utf-8'), compresslevel=6, mtime=0)
        box.update(encoding='gzip+base64', bytes=len(text.encode('utf-8')), data=base64.b64encode(raw).decode('ascii'))
    else:
        box.update(encoding='json', data=payload)
    body = json.dumps(box, ensure_ascii=False, separators=(',', ':'))
    return '(window.%s=window.%s||[]).push(%s);' % (kind, kind, body) + chr(10)


def read_container(path):
    """The payload of a container ``.js`` file (for tests and tools)."""
    text = Path(path).read_text(encoding='utf-8')
    box = json.loads(text[text.index('push(') + 5:text.rindex(');')])
    if box.get('schema') != 'ddc-viewer-container/1':
        raise ValueError('VIEWER_CONTAINER_SCHEMA')
    if box['encoding'] == 'json':
        return box['data']
    if box['encoding'] != 'gzip+base64':
        raise ValueError('VIEWER_CONTAINER_ENCODING')
    return json.loads(gzip.decompress(base64.b64decode(box['data'])).decode('utf-8'))


def write_package(document, output_dir, *, chunk_size=4000, inline_limit=2000, compress=True):
    """Write a NEW package folder with ONE data copy: ``package.js`` (+ ``props/NNNN.js``).

    Each file is a ``ddc-viewer-container/1`` script that works from file:// without a
    server; the payload is gzip + base64 (the viewer inflates it with the browser's
    DecompressionStream) or, with ``compress=False``, plain JSON.  With more than
    *inline_limit* entities the per-entity ``props`` move to chunks of *chunk_size*
    entities loaded on demand (``properties.mode = "chunks"``)."""
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError('Fresh output folder required: %s' % output_dir)
    output_dir.mkdir(parents=True)
    entities = document.get('entities') or []
    sha = document['source']['sha256']
    total = 0
    if len(entities) > inline_limit:
        (output_dir / 'props').mkdir()
        files = []
        for start in range(0, len(entities), chunk_size):
            chunk = {'schema': 'ddc-viewer-props/1', 'package': sha, 'start': start,
                     'props': [e.pop('props', {}) for e in entities[start:start + chunk_size]]}
            name = 'props/%04d' % (start // chunk_size)
            text = _container('DDCV_PROPS', chunk, {'package': sha, 'start': start}, compress)
            (output_dir / (name + '.js')).write_text(text, encoding='utf-8')
            files.append(name)
            total += len(text.encode('utf-8'))
        document['properties'] = {'mode': 'chunks', 'chunk_size': chunk_size, 'files': files}
    else:
        document['properties'] = {'mode': 'inline'}
    text = _container('DDCV_PACKAGES', document, {'package': sha, 'package_schema': document['schema']}, compress)
    (output_dir / 'package.js').write_text(text, encoding='utf-8')
    total += len(text.encode('utf-8'))
    return {'js': str(output_dir / 'package.js'), 'bytes': total}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('input', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--reader', type=Path, default=DEFAULT_READER, help='folder of the own IFC reader (model.py)')
    ap.add_argument('--format', default='IFC', choices=('IFC', 'RVT'))
    ap.add_argument('--rvt-report', type=Path)
    ap.add_argument('--no-compress', action='store_true', help='plain JSON payload instead of gzip+base64')
    a = ap.parse_args(argv)
    doc = build_package(a.input, reader_dir=a.reader, fmt=a.format, rvt_report=a.rvt_report)
    size = write_package(doc, a.output, compress=not a.no_compress)['bytes']
    c = doc['coverage']
    print(json.dumps({'elements': c['elements'], 'with_geometry': c['elements_with_geometry'], 'triangles': c['triangles'],
                      'refused': sum(c['refused_items'].values()), 'bytes': size}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
