"""Unit factors (values in DDC output are metric; 'internal units' are feet)."""
from __future__ import annotations

_LEN = {"m": 1.0, "mm": 1000.0, "cm": 100.0, "ft": 1 / 0.3048, "in": 1 / 0.0254, "yd": 1 / 0.9144}
_ALIAS = {"m2": "m²", "m^2": "m²", "m3": "m³", "m^3": "m³", "ft2": "ft²", "ft^2": "ft²", "ft3": "ft³",
          "ft^3": "ft³", "in2": "in²", "in3": "in³", "yd2": "yd²", "yd3": "yd³", "cm2": "cm²", "cm3": "cm³",
          "mm2": "mm²", "mm3": "mm³", "l": "L", "liter": "L", "litre": "L", "internal units": "ft",
          "internal": "ft", "feet": "ft", "inch": "in", "meter": "m", "metre": "m"}


def norm(u: str) -> str:
    u = (u or "").strip()
    return _ALIAS.get(u.lower(), u)


def _scale(u: str) -> tuple[int, float] | None:
    """(power, units per metre**power)."""
    u = norm(u)
    if u == "L":
        return 3, 1000.0
    for sup, p in (("²", 2), ("³", 3)):
        if u.endswith(sup) and u[:-1] in _LEN:
            return p, _LEN[u[:-1]] ** p
    return (1, _LEN[u]) if u in _LEN else None


def factor(src: str, dst: str) -> float:
    """Multiplier turning a value in `src` into `dst`; ValueError if incompatible."""
    s, d = _scale(src), _scale(dst)
    if s is None or d is None or s[0] != d[0]:
        raise ValueError(f"cannot convert {src!r} to {dst!r}")
    return d[1] / s[1]
