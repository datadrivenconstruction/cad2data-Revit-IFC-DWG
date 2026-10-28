"""BCF 2.1 zip writer: one topic per finding, viewpoint selects the element GUIDs (IfcGuid)."""
from __future__ import annotations
import datetime as dt
import uuid
import zipfile
from xml.sax.saxutils import escape, quoteattr

import numpy as np

from .model import eid
from .rules import Finding

XML = '<?xml version="1.0" encoding="UTF-8"?>\n'


def _bcf_xyz(p):
    """Scene (Y-up) -> Z-up model coordinates."""
    return float(p[0]), float(-p[2]), float(p[1])


def _viewpoint(vguid, guids, point, size):
    cam = ""
    if point is not None:
        cx, cy, cz = _bcf_xyz(point)
        d = np.array([1.0, -1.0, 0.7])
        d /= np.linalg.norm(d)
        dist = max(size, 0.5) * 2.5
        pos = np.array([cx, cy, cz]) + d * dist
        f = -d
        cam = ("<PerspectiveCamera><CameraViewPoint><X>%.4f</X><Y>%.4f</Y><Z>%.4f</Z></CameraViewPoint>"
               "<CameraDirection><X>%.5f</X><Y>%.5f</Y><Z>%.5f</Z></CameraDirection>"
               "<CameraUpVector><X>0</X><Y>0</Y><Z>1</Z></CameraUpVector><FieldOfView>60</FieldOfView></PerspectiveCamera>"
               % (*pos, *f))
    comps = "".join('<Component IfcGuid=%s/>' % quoteattr(g) for g in guids)
    sel = "<Selection>%s</Selection>" % comps if guids else ""
    col = '<Coloring><Color Color="FFFF0000">%s</Color></Coloring>' % comps if guids else ""
    return (XML + '<VisualizationInfo Guid="%s"><Components>%s<Visibility DefaultVisibility="true"/>%s</Components>%s</VisualizationInfo>'
            % (vguid, sel, col, cam))


def _markup(tguid, vguid, f: Finding, model_name, author, now, snapshot):
    pri = {"error": "High", "warning": "Normal", "info": "Low"}.get(f.severity, "Normal")
    desc = f.message
    ids = [str(x.get("ElementId")) for x in (f.element, f.other) if x]
    if ids:
        desc += " [ElementId %s]" % ", ".join(ids)
    return (XML + '<Markup><Header><File isExternal="false"><Filename>%s</Filename><Date>%s</Date></File></Header>'
            '<Topic Guid="%s" TopicType="%s" TopicStatus="Open"><Title>%s</Title><Priority>%s</Priority>'
            "<CreationDate>%s</CreationDate><CreationAuthor>%s</CreationAuthor><Description>%s</Description></Topic>"
            '<Viewpoints Guid="%s"><Viewpoint>viewpoint.bcfv</Viewpoint>%s</Viewpoints></Markup>'
            % (escape(model_name), now, tguid, escape(f.severity.capitalize()),
               escape("%s: %s" % (f.rule_id, f.title)), pri, now, escape(author), escape(desc), vguid,
               "<Snapshot>snapshot.png</Snapshot>" if snapshot else ""))


def write_bcf(findings, path, model_name="model.rvt", author="ddc-qa", meshes=None, snapshot_fn=None, max_topics=1000):
    """snapshot_fn(finding) -> PNG bytes or None (optional)."""
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    n = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("bcf.version", XML + '<Version VersionId="2.1"><DetailedVersion>2.1</DetailedVersion></Version>')
        for f in findings:
            if n >= max_topics:
                break
            tg, vg = str(uuid.uuid4()), str(uuid.uuid4())
            guids = [g for g in (Finding.guid_of(f.element), Finding.guid_of(f.other)) if g]
            size = 1.0
            if meshes:
                bb = [meshes[eid(x)].bbox() for x in (f.element, f.other) if x and eid(x) in meshes]
                if bb:
                    lo = np.min([b[0] for b in bb], 0)
                    hi = np.max([b[1] for b in bb], 0)
                    size = float(np.linalg.norm(hi - lo))
                    if f.point is None:
                        f.point = tuple(((lo + hi) / 2).tolist())
            png = snapshot_fn(f) if snapshot_fn else None
            z.writestr("%s/markup.bcf" % tg, _markup(tg, vg, f, model_name, author, now, bool(png)))
            z.writestr("%s/viewpoint.bcfv" % tg, _viewpoint(vg, guids, f.point, size))
            if png:
                z.writestr("%s/snapshot.png" % tg, png)
            n += 1
    return n
