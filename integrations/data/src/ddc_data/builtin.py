"""Built-in report templates (same schema as custom YAML/JSON templates)."""
from __future__ import annotations


def _cat(*names):
    return [{"column": "CategoryEn", "in": list(names)}]


_QTY = [{"column": "Length", "fn": "sum", "as": "Length"},
        {"column": "Area", "fn": "sum", "as": "Area"},
        {"column": "Volume", "fn": "sum", "as": "Volume"}]
_COUNT = {"fn": "count", "as": "Count"}


def _qty(title, group_by):
    return {"title": title, "group_by": group_by, "aggregates": [_COUNT] + _QTY, "sort": group_by}


_SCHED_COLS = ["ElementId", "Mark", "Family", "Type Name", "Level", "Width", "Height", "Width (type)",
               "Height (type)", "Width (parameter)", "Height (parameter)", "Fire Rating", "Area", "Volume"]
# older saves keep sizes only in feet (internal units); show them in metres
_SCHED_CONV = {"Width (type)": "m", "Height (type)": "m", "Width (parameter)": "m", "Height (parameter)": "m"}

BUILTIN = {
    "quantity_takeoff": {
        "name": "Quantity takeoff",
        "description": "Length, area and volume totals by category, level and type.",
        "sections": [
            _qty("By category", ["Category"]),
            _qty("By level", ["Level"]),
            _qty("By category and level", ["Category", "Level"]),
            _qty("By type", ["Category", "Family", "Type Name"]),
        ],
    },
    "room_schedule": {
        "name": "Room schedule",
        "description": "Rooms with level and measured area, perimeter and volume.",
        "filters": _cat("Rooms"),
        "sections": [{
            "title": "Rooms",
            "columns": ["ElementId", "Number", "Name", "Type Name", "Level", "Area", "Perimeter", "Volume",
                        "Height", "Department", "Occupancy"],
            "sort": ["Level", "Number", "Name"],
        }, {
            "title": "Area by level",
            "group_by": ["Level"],
            "aggregates": [_COUNT, {"column": "Area", "fn": "sum", "as": "Area"}],
            "sort": ["Level"],
        }],
    },
    "door_window_schedule": {
        "name": "Door and window schedule",
        "description": "Door and window lists and counts per type and level.",
        "sections": [
            {"title": "Doors", "filters": _cat("Doors"), "columns": _SCHED_COLS, "convert": _SCHED_CONV, "sort": ["Level", "Type Name"]},
            {"title": "Doors by type", "filters": _cat("Doors"), "group_by": ["Family", "Type Name", "Level"],
             "aggregates": [_COUNT]},
            {"title": "Windows", "filters": _cat("Windows"), "columns": _SCHED_COLS, "convert": _SCHED_CONV, "sort": ["Level", "Type Name"]},
            {"title": "Windows by type", "filters": _cat("Windows"), "group_by": ["Family", "Type Name", "Level"],
             "aggregates": [_COUNT]},
        ],
    },
    "wall_types_summary": {
        "name": "Wall types summary",
        "description": "Walls grouped by family and type with count, length, area and volume.",
        "filters": _cat("Walls"),
        "sections": [{
            "title": "Wall types",
            "group_by": ["Family", "Type Name"],
            "aggregates": [_COUNT, {"column": "Width", "fn": "mean", "as": "Avg width"}] + _QTY,
            "sort": ["-Volume"],
        }, {
            "title": "Wall types by level",
            "group_by": ["Level", "Type Name"],
            "aggregates": [_COUNT] + _QTY,
            "sort": ["Level", "-Volume"],
        }],
    },
    "parameter_fill_rate": {
        "name": "Parameter fill rate",
        "description": "Share of elements with a non-empty value per parameter, by category.",
        "kind": "fill_rate",
        "group_by": ["Category"],
    },
}
