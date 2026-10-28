"""Localized Revit category names -> canonical English name (case-insensitive)."""
from __future__ import annotations

_RAW = {
    "Walls": "Walls Wände Murs Muros Pareti Стены Paredes Muren Ściany Zdi",
    "Doors": "Doors Türen Portes Puertas Porte Двери Portas Deuren Drzwi Dveře",
    "Windows": "Windows Fenster Fenêtres Ventanas Finestre Окна Janelas Ramen Okna",
    "Rooms": "Rooms Räume Pièces Habitaciones Locali Помещения Ambientes Ruimten Pomieszczenia Místnosti",
    "Floors": "Floors Geschossdecken Sols Suelos Pavimenti Перекрытия Pisos Vloeren Stropy",
    "Ceilings": "Ceilings Decken Plafonds Techos Controsoffitti Потолки Tetos Plafonds Sufity",
    "Roofs": "Roofs Dächer Toits Cubiertas Tetti Крыши Telhados Daken Dachy",
    "Columns": "Columns Stützen Poteaux Pilares Pilastri Колонны Kolommen Słupy",
    "Structural Columns": "Structural_Columns Tragwerksstützen Poteaux_porteurs Pilares_estructurales Колонны_несущие",
    "Structural Framing": "Structural_Framing Tragwerk Ossature Estructura Каркас",
    "Stairs": "Stairs Treppen Escaliers Escaleras Scale Лестницы Escadas Trappen Schody",
    "Levels": "Levels Ebenen Niveaux Niveles Livelli Уровни Níveis Niveaus Poziomy",
    "Furniture": "Furniture Möbel Mobilier Mobiliario Arredi Мебель Mobiliário Meubilair Meble",
}
_LOOKUP: dict[str, str] = {}
for _en, _names in _RAW.items():
    for _n in _names.split():
        _LOOKUP[_n.replace("_", " ").casefold()] = _en
    _LOOKUP[_en.casefold()] = _en
_LOOKUP.update({"geschosse": "Levels", "wandtypen": "Walls", "türen": "Doors", "tueren": "Doors"})


def canonical(name) -> str:
    if name is None:
        return "(none)"
    s = str(name)
    return _LOOKUP.get(s.strip().casefold(), s)


def canonical_series(series):
    cache: dict = {}
    return series.map(lambda v: cache.setdefault(v, canonical(v)))
