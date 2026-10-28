"""Synthetic models for unit tests."""
import numpy as np

from ddc_qa.glb import Mesh
from ddc_qa.model import Model


def box(lo, hi):
    lo, hi = np.array(lo, float), np.array(hi, float)
    c = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    # vertex index = 4*ix + 2*iy + iz
    q = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    t = []
    for a, b, cc, d in q:
        t += [(a, b, cc), (a, cc, d)]
    t = np.array(t)
    m = Mesh(c, t)
    if m.volume() == 0:
        raise AssertionError
    return m


def row(i, cat, **kw):
    r = {"ElementId": i, "GlobalId": "G%021d" % i, "UniqueId": "u-%d" % i, "Category": cat, "Family": "F", "Type Name": "T",
         "Level": "L1", "IfcClass": "IFC" + cat.upper()}
    r.update(kw)
    return r


def model(rows, meshes=None):
    hdr = list(dict.fromkeys(k for r in rows for k in r))
    return Model("synthetic", hdr, rows, meshes or {})
