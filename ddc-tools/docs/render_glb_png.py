"""Render a GLB to a PNG with a tiny software rasteriser (flat shading, orthographic isometric view,
painter's algorithm, alpha from the material) for the README. Dev helper only (needs Pillow); it is a
drawing of the geometry and the material colours, not a viewer screenshot.

    python render_glb_png.py diff.glb out.png [width] [height]
"""
import math
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ddc_tools.glbdiff import _local, _mul, IDENT, read_glb  # noqa: E402


def accessor(g, blob, i):
    a = g["accessors"][i]
    bv = g["bufferViews"][a["bufferView"]]
    start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    ct = {5126: ("f", 4), 5125: ("I", 4), 5123: ("H", 2), 5121: ("B", 1)}[a["componentType"]]
    nc = {"SCALAR": 1, "VEC3": 3}[a["type"]]
    stride = bv.get("byteStride") or ct[1] * nc
    return [struct.unpack_from("<" + ct[0] * nc, blob, start + k * stride) for k in range(a["count"])]


def triangles(path):
    g, blob = read_glb(path)
    out = []                                           # (points, rgba, node name)
    nodes = g["nodes"]
    roots = g["scenes"][g.get("scene", 0)]["nodes"]

    def walk(i, parent):
        n = nodes[i]
        w = _mul(parent, _local(n))
        if "mesh" in n:
            for p in g["meshes"][n["mesh"]]["primitives"]:
                mat = g.get("materials", [{}])[p.get("material", 0)] if g.get("materials") else {}
                col = mat.get("pbrMetallicRoughness", {}).get("baseColorFactor", [0.7, 0.7, 0.7, 1])
                pos = [(w[0] * x + w[4] * y + w[8] * z + w[12], w[1] * x + w[5] * y + w[9] * z + w[13],
                        w[2] * x + w[6] * y + w[10] * z + w[14]) for x, y, z in accessor(g, blob, p["attributes"]["POSITION"])]
                idx = [t[0] for t in accessor(g, blob, p["indices"])] if "indices" in p else list(range(len(pos)))
                for t in range(0, len(idx) - 2, 3):
                    out.append(([pos[idx[t]], pos[idx[t + 1]], pos[idx[t + 2]]], col))
        for c in n.get("children", []):
            walk(c, w)

    for r in roots:
        walk(r, IDENT)
    return out


def render(glb, out, W=1100, H=700, legend=None):
    tris = triangles(glb)
    az, el = math.radians(-215), math.radians(32)
    ca, sa, ce, se = math.cos(az), math.sin(az), math.cos(el), math.sin(el)

    def proj(p):                                       # glTF Y-up -> screen
        x, y, z = p
        xr, zr = x * ca - z * sa, x * sa + z * ca
        return xr, y * ce - zr * se, zr * ce + y * se  # screen x, screen y (up), depth

    pts = [[proj(p) for p in t[0]] for t in tris]
    xs = [q[0] for t in pts for q in t]
    ys = [q[1] for t in pts for q in t]
    s = min((W - 160) / (max(xs) - min(xs)), (H - 160) / (max(ys) - min(ys)))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    SS = 2
    im = Image.new("RGB", (W * SS, H * SS), "#F7F8FA")
    d = ImageDraw.Draw(im, "RGBA")
    order = sorted(range(len(tris)), key=lambda i: sum(q[2] for q in pts[i]))
    light = (0.4, 0.8, 0.45)
    for i in order:
        a, b, c = tris[i][0]
        u, v = [b[k] - a[k] for k in range(3)], [c[k] - a[k] for k in range(3)]
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        ln = math.sqrt(sum(x * x for x in n)) or 1
        shade = 0.55 + 0.45 * abs(sum(n[k] / ln * light[k] for k in range(3)))
        col = tris[i][1]
        rgb = tuple(int(255 * min(1, col[k] * shade)) for k in range(3))
        poly = [((q[0] - cx) * s * SS + W * SS / 2, H * SS / 2 - (q[1] - cy) * s * SS) for q in pts[i]]
        d.polygon(poly, fill=rgb + (int(255 * col[3]),), outline=tuple(int(c * 0.6) for c in rgb) + (int(120 * col[3]),))
    im = im.resize((W, H), Image.LANCZOS)
    if legend:
        d2 = ImageDraw.Draw(im)
        try:
            f = ImageFont.truetype("segoeui.ttf", 18)
        except OSError:
            f = ImageFont.load_default()
        y = 24
        for label, color in legend:
            d2.rectangle([24, y, 46, y + 20], fill=color, outline="#555")
            d2.text((56, y), label, fill="#222", font=f)
            y += 30
    im.save(out)


if __name__ == "__main__":
    a = sys.argv
    render(a[1], a[2], int(a[3]) if len(a) > 3 else 1100, int(a[4]) if len(a) > 4 else 700,
           legend=[("added", "#2EB84D"), ("removed", "#DB3232"), ("modified", "#FA9E1A"), ("unchanged (ghost)", "#BEBEBE")])
