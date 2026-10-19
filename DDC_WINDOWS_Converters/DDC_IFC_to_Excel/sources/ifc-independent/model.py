"""First-party IFC model adapter over :mod:`reader` and official EXPRESS metadata.

This provides the subset of IfcOpenShell's Python model API used by the current
IFC-to-Excel semantic mapper. It is not an EXPRESS validator and does not
interpret geometry, units, WHERE rules, or effective properties.
"""
from __future__ import annotations

import json
from copy import deepcopy
import importlib.util
import math
from decimal import Decimal
from pathlib import Path
import sys
from typing import Any, Iterator

HERE = Path(__file__).resolve().parent

if __package__:
    from . import reader
else:  # direct import fallback is explicitly pinned to this directory
    _reader_name = "_ddc_independent_reader"
    _reader_path = HERE / "reader.py"
    _reader_spec = importlib.util.spec_from_file_location(_reader_name, _reader_path)
    if _reader_spec is None or _reader_spec.loader is None:
        raise ImportError(f"Cannot load first-party reader from {_reader_path}")
    reader = importlib.util.module_from_spec(_reader_spec)
    sys.modules[_reader_name] = reader
    _reader_spec.loader.exec_module(reader)


GENERATED = HERE / "schemas" / "generated"
_SCHEMA_FILES = {
    "IFC2X3": "IFC2X3.json",
    "IFC4": "IFC4.json",
    "IFC4X3": "IFC4X3.json",
}
_SCHEMA_HEADER_ALIASES = {
    "IFC2X3": "IFC2X3", "IFC2X3_TC1": "IFC2X3", "IFC2X3_TC1_ADD1": "IFC2X3",
    "IFC4": "IFC4", "IFC4_ADD1": "IFC4", "IFC4_ADD2": "IFC4",
    "IFC4_ADD2_TC1": "IFC4",
    "IFC4X3": "IFC4X3", "IFC4X3_ADD1": "IFC4X3", "IFC4X3_ADD2": "IFC4X3",
    "IFC4X3_ADD2_TC1": "IFC4X3",
}


class ModelError(ValueError):
    """Input cannot be represented by the supported EXPRESS metadata."""


def _metadata(schema: str, schema_dir: str | Path | None = None) -> dict:
    path = Path(schema_dir) / _SCHEMA_FILES[schema] if schema_dir else GENERATED / _SCHEMA_FILES[schema]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModelError(f"Cannot load pinned schema metadata {path}: {exc}") from exc
    if data.get("schema") != schema or not isinstance(data.get("entities"), dict):
        raise ModelError(f"Schema metadata identity/content mismatch: {path}")
    return data


def _schema_name(rows: list[dict]) -> str:
    records = [row for row in rows if row.get("record_type") == "header" and row.get("name", "").upper() == "FILE_SCHEMA"]
    if len(records) != 1:
        raise ModelError(f"Expected exactly one FILE_SCHEMA header record; found {len(records)}")
    attrs = records[0].get("attributes")
    if not isinstance(attrs, list) or len(attrs) != 1 or not isinstance(attrs[0], list) or not attrs[0]:
        raise ModelError("FILE_SCHEMA must contain one non-empty schema identifier list")
    names = attrs[0]
    if not all(isinstance(name, str) for name in names):
        raise ModelError("FILE_SCHEMA contains a non-string schema identifier")
    normalized = set()
    for name in names:
        target = _SCHEMA_HEADER_ALIASES.get(name.upper())
        if target is None:
            raise ModelError(f"Unqualified IFC schema identifier {name!r}")
        normalized.add(target)
    if len(normalized) != 1:
        raise ModelError(f"Ambiguous FILE_SCHEMA identifiers: {sorted(names)!r}")
    return normalized.pop()


class TypedValue:
    """An EXPRESS defined-type/select wrapper; entity id is zero like IfcOpenShell."""

    __slots__ = ("_type", "wrappedValue")

    def __init__(self, type_name: str, wrapped_value: Any):
        self._type = type_name
        self.wrappedValue = wrapped_value

    def id(self) -> int:
        return 0

    def is_a(self, type_name: str | None = None) -> str | bool:
        if type_name is None:
            return self._type
        return self._type.casefold() == type_name.casefold()

    def __repr__(self) -> str:
        return f"TypedValue({self._type!r}, {self.wrappedValue!r})"


class Entity:
    """A source IFC instance exposing the semantic mapper's entity API."""

    __slots__ = ("_model", "_row", "_definition", "_values")

    def __init__(self, model: "Model", row: dict, definition: dict):
        self._model, self._row, self._definition = model, row, definition
        self._values = row["attributes"]
        expected = len(definition["attributes"])
        if len(self._values) != expected:
            raise ModelError(f"#{row['id']}={row['type']} has {len(self._values)} values; schema requires {expected} positional slots")

    def id(self) -> int:
        return int(self._row["id"])

    def is_a(self, type_name: str | None = None) -> str | bool:
        own = self._row["type"]
        if type_name is None:
            return own
        wanted = type_name.casefold()
        return own.casefold() == wanted or any(parent.casefold() == wanted for parent in self._definition["ancestors"])

    def attribute_name(self, index: int) -> str:
        try:
            return self._definition["attributes"][index]
        except (IndexError, TypeError) as exc:
            raise IndexError(index) from exc

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, index: int) -> Any:
        return self._model._value(self._values[index])

    def source_attribute(self, attribute: int | str) -> Any:
        """Return a detached structural value, retaining exact STEP REAL text.

        References remain source IDs; they are not expanded or unit-normalized.
        This additive API does not change legacy float/int attribute access.
        """
        if isinstance(attribute, str):
            try:
                attribute = self._definition['attributes'].index(attribute)
            except ValueError as exc:
                raise AttributeError(attribute) from exc
        return deepcopy(self._values[attribute])

    def source_real_values(self) -> list[dict]:
        """Identify every REAL token by source attribute and nested value path."""
        output = []

        def walk(node, index, path, types):
            if isinstance(node, list):
                for position, child in enumerate(node):
                    walk(child, index, path + [position], types)
            elif isinstance(node, dict):
                if 'step_real' in node:
                    lexeme = node['step_real']
                    exact = Decimal(lexeme)
                    number = float(exact)
                    if not math.isfinite(number):
                        status = 'OVERFLOW_REFUSED'
                    elif number == 0 and exact != 0:
                        status = 'UNDERFLOW_REFUSED'
                    elif number != 0 and exact == exact.to_integral_value() and exact != Decimal.from_float(number):
                        status = 'EXACT_INTEGER'
                    else:
                        status = 'EXACT_BINARY64' if exact == Decimal.from_float(number) else 'ROUNDED_BINARY64'
                    output.append({'attribute_index': index, 'attribute_name': self.attribute_name(index),
                                   'value_path': path, 'defined_types': types, 'step_real': lexeme,
                                   'model_precision': status})
                elif 'type' in node:
                    walk(node['value'], index, path + ['value'], types + [node['type']])

        for index, node in enumerate(self._values):
            walk(node, index, [], [])
        return output

    def __getattr__(self, name: str) -> Any:
        attrs = self._definition["attributes"]
        try:
            index = attrs.index(name)
        except ValueError as exc:
            raise AttributeError(name) from exc
        return self[index]

    def __repr__(self) -> str:
        return f"#{self.id()}={self._row['type']}"


class Model:
    """A parsed IFC model with source-order iteration and indexed lookup."""

    def __init__(self, rows: list[dict], schema: str, metadata: dict, filename: str | None = None, *, cancel_event=None):
        self.schema = schema
        self.filename = filename
        self._metadata = metadata
        self._definitions = metadata["entities"]
        self._type_lookup = {name.casefold(): name for name in self._definitions}
        self._by_id: dict[int, Entity] = {}
        self._entities: list[Entity] = []
        for row in rows:
            if cancel_event is not None and cancel_event.is_set():
                raise ModelError("Cancelled during model construction")
            if row.get("record_type") != "entity":
                continue
            original_type = row.get("type")
            entity_type = self._type_lookup.get(str(original_type).casefold())
            definition = self._definitions.get(entity_type) if entity_type else None
            if definition is None:
                raise ModelError(f"Unknown entity type {original_type!r} in {schema}")
            if original_type != entity_type:
                row = dict(row, type=entity_type)
            entity = Entity(self, row, definition)
            self._entities.append(entity)
            self._by_id[entity.id()] = entity

    def __iter__(self) -> Iterator[Entity]:
        return iter(self._entities)

    def iter(self) -> Iterator[Entity]:
        return iter(self._entities)

    def by_id(self, entity_id: int) -> Entity:
        try:
            return self._by_id[int(entity_id)]
        except (KeyError, TypeError, ValueError) as exc:
            raise KeyError(entity_id) from exc

    def by_type(self, type_name: str, include_subtypes: bool = True) -> list[Entity]:
        canonical = self._type_lookup.get(type_name.casefold())
        if canonical is None:
            raise ModelError(f"Unknown entity type filter {type_name!r} in {self.schema}")
        output = []
        for entity in self._entities:
            if entity.is_a(canonical) if include_subtypes else entity.is_a() == canonical:
                output.append(entity)
        return output

    def _value(self, value: Any) -> Any:
        if isinstance(value, list):
            return [self._value(item) for item in value]
        if not isinstance(value, dict):
            return value
        if "ref" in value:
            return self.by_id(value["ref"])
        if "step_special" in value:
            return None
        if "enum" in value:
            enum = value["enum"].strip(".")
            logical = {"T": True, "F": False, "U": "UNKNOWN"}
            return logical.get(enum.upper(), enum)
        if "step_real" in value:
            exact = Decimal(value["step_real"])
            number = float(exact)
            if not math.isfinite(number):
                raise ModelError("Non-finite real survived structural parse")
            if number == 0 and exact != 0:
                # The structural reader retains the exact lexeme. This adapter
                # uses binary64 values, so refuse silent loss of a nonzero value.
                raise ModelError("STEP real underflows binary64; nonzero source value cannot be represented")
            # A REAL lexeme can denote an exact integer beyond binary64's
            # precision (9007199254740993. or 9.007199254740993E15). Preserve
            # that source integer whenever float conversion would alter it.
            # Keep ordinary floats, signed zero and nonintegral values as-is;
            # typed wrappers still carry the original EXPRESS defined type.
            if number != 0 and exact == exact.to_integral_value():
                integer = int(exact)
                if integer != number:
                    return integer
            return number
        if "type" in value:
            raw_type = value["type"]
            canonical = self._metadata["types"].get(raw_type.casefold())
            type_name = canonical["name"] if canonical else raw_type
            return TypedValue(type_name, self._value(value.get("value")))
        raise ModelError(f"Unsupported structural value node: {value!r}")


def model_from_file(path: str | Path, schema_dir: str | Path | None = None, *, cancel_event=None) -> Model:
    """Read a UTF-8 IFC-SPF file and expose its schema-backed model interface.

    Parsing/metadata errors raise ``ModelError`` or ``reader.Part21Error``;
    no partially built model is returned. Only the structural grammar, selected
    entity slots, and reference resolution are checked, not EXPRESS WHERE rules.
    """
    source = Path(path)
    try:
        text, _ = reader._read_source(source, cancel_event=cancel_event)
    except (OSError, UnicodeError) as exc:
        raise ModelError(f"Cannot read IFC source {source}: {exc}") from exc
    rows = reader.parse_text(text, cancel_event=cancel_event)
    schema = _schema_name(rows)
    if cancel_event is not None and cancel_event.is_set():
        raise ModelError("Cancelled before schema metadata loading")
    metadata = _metadata(schema, schema_dir)
    return Model(rows, schema, metadata, str(source), cancel_event=cancel_event)


def schema_metadata() -> dict:
    """Return public schema release/source/hash metadata for all supported releases."""
    result = {}
    for schema in _SCHEMA_FILES:
        data = _metadata(schema)
        result[schema] = {key: data[key] for key in ("version", "official_source_url", "source")}
    return result


def source_paths(schema: str | None = None) -> list[Path]:
    """Return absolute first-party source/schema paths and SHA-256 pins.

    Passing a normalized schema limits official/generated data paths; code
    paths are always returned. Suitable for a conversion receipt's modules list.
    """
    paths = [HERE / "model.py", HERE / "reader.py", HERE / "schema_gen.py",
             HERE / "schemas" / "official" / "NOTICE.txt"]
    schemas = [schema.upper()] if schema else list(_SCHEMA_FILES)
    for name in schemas:
        if name not in _SCHEMA_FILES:
            raise ModelError(f"Unsupported schema {name!r}")
        data = _metadata(name)
        paths.extend((HERE / "schemas" / "official" / data["source"]["filename"], GENERATED / _SCHEMA_FILES[name]))
    return [path.resolve() for path in paths]


__all__ = ["Entity", "Model", "ModelError", "TypedValue", "model_from_file", "schema_metadata", "source_paths"]
