"""Open IFC semantic tables. No geometry or effective-property fidelity claim."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import copy
from datetime import datetime, timezone
from decimal import Decimal
import json
import math
import os
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile
import uuid
import stat
import zipfile
from contextlib import suppress
from pathlib import PurePosixPath

try:
    import openpyxl
    from openpyxl.cell import WriteOnlyCell
    import semantics
    import ifc_runtime
    import file_pins
    RUNTIME_IMPORT_ERROR = None
except (ImportError, OSError) as error:
    RUNTIME_IMPORT_ERROR = str(error)

VERSION = "0.3.1-preview"
SCHEMA = "ddc_ifc_excel/1"
MAX_ROWS = 1_048_576
EXCEL_NUMERIC_COLUMNS = {"NormalizedMeasures": ["scale_to_si", "si_value"]}
INVALID_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]")


def pin(path):
    return file_pins.pin(path)


def value(v):
    """Preserve select type and references without expanding cyclic graphs."""
    if isinstance(v, ifc_runtime.Entity):
        if v.id():
            return {"ref": v.id(), "ifc_class": v.is_a()}
        return {"ifc_type": v.is_a(), "value": value(v.wrappedValue)}
    if isinstance(v, (list, tuple)):
        return [value(x) for x in v]
    return v


def dumps(v):
    return json.dumps(v, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def attributes(entity):
    return {entity.attribute_name(i): value(entity[i]) for i in range(len(entity))}


def ref(v):
    return str(v.id()) if isinstance(v, ifc_runtime.Entity) and v.id() else ""


def members(v):
    if isinstance(v, ifc_runtime.Entity):
        if v.id():
            yield v
        elif hasattr(v, "wrappedValue"):
            # IFC4 IfcPropertySetDefinitionSet is an id=0 aggregate select wrapper.
            yield from members(v.wrappedValue)
    elif isinstance(v, (list, tuple)):
        for item in v:
            yield from members(item)


def excel_safe_number(number):
    """Conservative Excel 15-significant-digit subset; never parse strings/IDs."""
    if isinstance(number, bool) or not isinstance(number, (int, float)):
        return False
    if abs(number) > 1e308 or not math.isfinite(number):
        return False
    if number and abs(number) < sys.float_info.min:
        return False
    digits = Decimal(str(number)).as_tuple().digits
    while len(digits) > 1 and digits[-1] == 0:
        digits = digits[:-1]
    return len(digits) <= 15


MAX_IFCZIP_MEMBERS = 4096
MAX_IFCZIP_COMPRESSION_RATIO = 500
IFCZIP_TEMP_DISK_RESERVE_BYTES = 512 * 1024 * 1024


def inspect_ifczip(source):
    """Validate an IFCZIP container before bounded extraction of its sole model."""
    with zipfile.ZipFile(source, "r") as archive:
        infos = archive.infolist()
        if not infos or len(infos) > MAX_IFCZIP_MEMBERS:
            raise ValueError("IFCZIP has no members or exceeds the 4096-member safety limit")
        expanded_bytes = sum(info.file_size for info in infos)
        free_bytes = shutil.disk_usage(tempfile.gettempdir()).free
        available_bytes = max(0, free_bytes - IFCZIP_TEMP_DISK_RESERVE_BYTES)
        if expanded_bytes > available_bytes:
            raise ValueError(
                f"IFCZIP uncompressed size ({expanded_bytes} bytes) exceeds temporary-disk budget "
                f"({available_bytes} bytes after a {IFCZIP_TEMP_DISK_RESERVE_BYTES}-byte reserve)"
            )
        names = set()
        for info in infos:
            name = info.filename
            normalized = name.casefold()
            if "\x00" in info.orig_filename:
                raise ValueError("IFCZIP member name contains an embedded NUL")
            if not name or normalized in names:
                raise ValueError("IFCZIP has an empty or duplicate member name")
            names.add(normalized)
            member_path = PurePosixPath(name)
            if "\\" in name or ":" in name or member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError("IFCZIP contains an unsafe member path")
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise ValueError("IFCZIP symbolic-link members are not accepted")
        models = [info for info in infos if not info.is_dir() and PurePosixPath(info.filename).suffix.lower() in (".ifc", ".ifcxml")]
        if len(models) != 1:
            raise ValueError("IFCZIP must contain exactly one IFC model member")
        model = models[0]
        if PurePosixPath(model.filename).suffix.lower() != ".ifc":
            raise ValueError("IFCZIP contains IFCXML, which the DDC IFC reader does not support")
        if model.flag_bits & 0x1:
            raise ValueError("Encrypted IFCZIP members are not supported")
        if model.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            raise ValueError("IFCZIP model compression must be STORED or DEFLATED")
        if model.file_size <= 0 or model.compress_size <= 0:
            raise ValueError("IFCZIP model member is empty or has invalid compressed size")
        if model.file_size / model.compress_size > MAX_IFCZIP_COMPRESSION_RATIO:
            raise ValueError("IFCZIP model exceeds the 500:1 expansion-ratio safety limit")
        ignored = [info.filename for info in infos if not info.is_dir() and info is not model]
        return {"container_format": "IFCZIP", "model_member": model.filename,
                "archive_member_count": len(infos), "ignored_non_model_members": ignored,
                "model_compressed_bytes": model.compress_size, "model_uncompressed_bytes": model.file_size}


def load_model(source, container=None):
    if container is None:
        return ifc_runtime.model_from_file(source)
    # Never extract archive paths. Stream only the selected member into a fixed
    # private path; enforce both the validated declared size and parser budget.
    declared = container["model_uncompressed_bytes"]
    if declared > 512 * 1024 * 1024:
        raise ValueError("IFCZIP model exceeds the 512 MiB reader input limit")
    with tempfile.TemporaryDirectory(prefix="ddc-ifc-") as folder:
        target = Path(folder) / "model.ifc"
        with zipfile.ZipFile(source) as archive:
            original = archive.getinfo(container["model_member"])
            if original.file_size != declared or original.compress_size != container["model_compressed_bytes"]:
                raise ValueError("IFCZIP member size does not match inspected metadata")
            if original.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise ValueError("IFCZIP model compression must be STORED or DEFLATED")
            # ZipExtFile normally truncates decompressor output at file_size.
            # An attacker can forge file_size AND CRC for a valid IFC prefix,
            # hiding a damaged tail. Give the reader one sentinel byte beyond
            # the untrusted declaration; preserve original CRC/header/overlap
            # validation and enforce the original size before writing a chunk.
            checked = copy(original)
            checked.file_size = declared + 1
            with archive.open(checked) as member, target.open("xb") as output:
                count = 0
                while chunk := member.read(min(1024 * 1024, declared - count + 1)):
                    count += len(chunk)
                    if count > declared:
                        raise ValueError("IFCZIP member exceeds its declared size")
                    output.write(chunk)
                # CPython ZipExtFile also treats exhausted compressed bytes as
                # EOF even when the DEFLATE end marker is absent, and ignores
                # bytes after that marker. Fail closed if the pinned runtime's
                # completion state is unavailable. No private state is changed.
                if getattr(member, "_compress_left", None) != 0:
                    raise ValueError("IFCZIP compressed member has unread trailing bytes")
                if original.compress_type == zipfile.ZIP_DEFLATED:
                    decoder = getattr(member, "_decompressor", None)
                    if not getattr(decoder, "eof", False):
                        raise ValueError("IFCZIP DEFLATE stream is incomplete")
                    if getattr(decoder, "unused_data", None) != b"" or getattr(decoder, "unconsumed_tail", None) != b"":
                        raise ValueError("IFCZIP DEFLATE stream has trailing compressed bytes")
        if count != declared:
            raise ValueError("IFCZIP member size does not match its declaration")
        return ifc_runtime.model_from_file(target)


def validate_row_limit(row_limit):
    """Reject nonintegral/nonfinite limits before any input or output work."""
    if type(row_limit) is not int or not 2 <= row_limit <= MAX_ROWS:
        raise ValueError("Invalid sheet row limit: expected an integer from 2 to MAX_ROWS")


class Tables:
    """SQLite/JSONL authoritative values, XLSX explicit text and bounded sheets."""
    def __init__(self, folder, row_limit=MAX_ROWS):
        validate_row_limit(row_limit)
        self.folder = folder
        self.limit = row_limit
        self.stream = None
        self.book = None
        self.db = sqlite3.connect(folder / "data.sqlite")
        try:
            self.db.execute("CREATE TABLE records(table_name TEXT NOT NULL, ordinal INTEGER NOT NULL, record_json TEXT NOT NULL, PRIMARY KEY(table_name,ordinal))")
            self.stream = (folder / "data.jsonl").open("w", encoding="utf-8", newline="\n")
            self.book = openpyxl.Workbook(write_only=True)
        except Exception:
            self.abort()
            raise
        self.sheets = {}
        self.counts = Counter()
        self.cell_limits = Counter()

    def emit(self, table, record):
        ordinal = self.counts[table] + 1
        serialized = dumps(record)
        self.db.execute("INSERT INTO records VALUES(?,?,?)", (table, ordinal, serialized))
        self.stream.write(dumps({"table": table, "ordinal": ordinal, "record": record}) + "\n")
        if table not in self.sheets or self.sheets[table][1] >= self.limit:
            part = (ordinal - 1) // (self.limit - 1) + 1
            ws = self.book.create_sheet(table if part == 1 else f"{table}_{part}")
            ws.freeze_panes = "A2"
            ws.append(list(record))
            self.sheets[table] = [ws, 1]
        ws = self.sheets[table][0]
        cells = []
        for key, original in record.items():
            if key in EXCEL_NUMERIC_COLUMNS.get(table, ()) and original is not None:
                if excel_safe_number(original):
                    cell = WriteOnlyCell(ws, value=original)
                    cell.number_format = "General"
                    cells.append(cell)
                    self.cell_limits["numeric_cells"] += 1
                    continue
                if isinstance(original, (int, float)) and not isinstance(original, bool):
                    original = f"[See data.jsonl: path={str((self.folder / 'data.jsonl').resolve())}; table={table} ordinal={ordinal} field={key}; numeric precision/range limit]"
                    self.cell_limits["numeric_precision_references"] += 1
            text = "" if original is None else (dumps(original) if isinstance(original, (dict, list, tuple)) else str(original))
            if "\r" in text or INVALID_XML.search(text) or len(text.encode("utf-16-le", errors="surrogatepass")) // 2 > 32767:
                text = f"[See data.jsonl: path={str((self.folder / 'data.jsonl').resolve())}; table={table} ordinal={ordinal} field={key}]"
                self.cell_limits["sidecar_cell_references"] += 1
            cell = WriteOnlyCell(ws, value=text)
            cell.data_type = "s"  # Never let '=...' become executable formula.
            cell.number_format = "@"  # IDs, large integers and leading zeroes remain exact.
            cells.append(cell)
        ws.append(cells)
        self.sheets[table][1] += 1
        self.counts[table] += 1

    def close(self):
        try:
            self.db.commit()
            self.db.close()
            self.stream.close()
            self.book.save(self.folder / "drawing.xlsx")
        finally:
            self.abort()

    def abort(self):
        """Release resources on every failure, preserving the original error.

        openpyxl 3.1.5 write-only sheets own temporary XML writers; closing the
        workbook alone does not close or remove these after an aborted save.
        """
        with suppress(Exception):
            self.db.close()
        if self.stream is not None:
            with suppress(Exception):
                self.stream.close()
        if self.book is not None:
            for sheet in self.book.worksheets:
                with suppress(Exception):
                    if not sheet.closed:
                        sheet.close()
                writer = sheet._writer
                if writer is not None and Path(writer.out).exists():
                    with suppress(Exception):
                        writer.cleanup()
            with suppress(Exception):
                self.book.close()


def property_rows(owner, pset, scope, relation_id="", path=(), seen=frozenset(), root_id=None):
    """Walk definitions in source order with branch-local iterative DFS."""
    root_id = root_id or ref(pset)
    active = set(seen)
    names = list(path)
    stack = [(pset, None)]
    while stack:
        pset, children = stack[-1]
        if children is None:
            if pset.id() in active:
                yield {"owner_step_id": ref(owner), "scope": scope, "relation_step_id": relation_id,
                       "root_set_step_id": root_id, "set_step_id": ref(pset), "set_name": getattr(pset, "Name", None), "property_step_id": ref(pset),
                       "path": list(names), "ifc_class": pset.is_a(), "property_name": getattr(pset, "Name", None),
                       "value": None, "unit_step_id": "", "attributes": attributes(pset),
                       "source_real_values": pset.source_real_values(), "status": "CYCLE_NOT_EXPANDED"}
                stack.pop()
                if stack:
                    names.pop()
                continue
            active.add(pset.id())
            values = getattr(pset, "HasProperties", None) or getattr(pset, "Quantities", None) or getattr(pset, "HasQuantities", None)
            children = iter(values or ())
            stack[-1] = (pset, children)
        try:
            prop = next(children)
        except StopIteration:
            active.remove(pset.id())
            stack.pop()
            if stack:
                names.pop()
            continue
        nested = getattr(prop, "HasProperties", None) or getattr(prop, "HasQuantities", None)
        if nested:
            names.append(getattr(pset, "Name", None))
            stack.append((prop, None))
        else:
            attrs = attributes(prop)
            # Keep value kind: lists/bounds/tables/references are not coerced to one scalar.
            payload = {k: v for k, v in attrs.items() if k not in ("Name", "Description", "Unit")}
            yield {"owner_step_id": ref(owner), "scope": scope, "relation_step_id": relation_id,
                   "root_set_step_id": root_id, "set_step_id": ref(pset), "set_name": getattr(pset, "Name", None), "property_step_id": ref(prop),
                   "path": list(names) + [getattr(pset, "Name", None), getattr(prop, "Name", None)],
                   "ifc_class": prop.is_a(), "property_name": getattr(prop, "Name", None),
                   "value": payload, "unit_step_id": ref(getattr(prop, "Unit", None)),
                   "attributes": attrs, "source_real_values": prop.source_real_values(), "status": "SOURCE_VALUE"}


def extract(model, tables, source_hash):
    ids = Counter()
    object_ids = set()
    for entity in model:
        for source_real in entity.source_real_values():
            # Source identity is bound by the job receipt/Metadata, like Entities.
            # Keep equivalent IFC/IFCZIP semantic rows independent of container hash.
            tables.emit("SourceReals", {"step_id": ref(entity), "ifc_class": entity.is_a(), **source_real})
        attrs = attributes(entity)
        tables.emit("Entities", {"step_id": ref(entity), "ifc_class": entity.is_a(), "attributes": attrs})
        if entity.is_a("IfcObjectDefinition"):
            object_ids.add(entity.id())
            guid = getattr(entity, "GlobalId", None)
            ids[guid] += 1
            tables.emit("Objects", {"ID": ref(entity), "GlobalId": guid,
                        "StableKey": f"sha256:{source_hash}#{entity.id()}", "Category": entity.is_a(),
                        "Name": getattr(entity, "Name", None), "Description": getattr(entity, "Description", None),
                        "IsType": entity.is_a("IfcTypeObject"), "Attributes": attrs})
            if entity.is_a("IfcTypeObject"):
                for definition in getattr(entity, "HasPropertySets", None) or ():
                    for row in property_rows(entity, definition, "TYPE_DEFINITION"):
                        tables.emit("Quantities" if row["ifc_class"].startswith("IfcQuantity") else "Properties", row)
        if entity.is_a("IfcRelationship"):
            tables.emit("Relations", {"step_id": ref(entity), "ifc_class": entity.is_a(), "GlobalId": getattr(entity, "GlobalId", None), "attributes": attrs})
        if entity.is_a("IfcUnitAssignment") or entity.is_a("IfcNamedUnit") or entity.is_a("IfcDerivedUnit") or entity.is_a("IfcMonetaryUnit"):
            tables.emit("Units", {"step_id": ref(entity), "ifc_class": entity.is_a(), "attributes": attrs})
        if entity.is_a("IfcRelDefinesByProperties"):
            for owner in entity.RelatedObjects or ():
                for definition in members(entity.RelatingPropertyDefinition):
                    for row in property_rows(owner, definition, "OCCURRENCE", ref(entity)):
                        tables.emit("Quantities" if row["ifc_class"].startswith("IfcQuantity") else "Properties", row)
        if entity.is_a("IfcRelDefinesByType"):
            for owner in entity.RelatedObjects or ():
                tables.emit("TypeLinks", {"owner_step_id": ref(owner), "type_step_id": ref(entity.RelatingType), "relation_step_id": ref(entity), "scope": "TYPE_ASSOCIATION_NOT_MERGED"})
        if entity.is_a("IfcRelContainedInSpatialStructure") or entity.is_a("IfcRelReferencedInSpatialStructure"):
            for owner in entity.RelatedElements or ():
                tables.emit("SpatialLinks", {"child_step_id": ref(owner), "parent_step_id": ref(entity.RelatingStructure), "relation_step_id": ref(entity), "kind": entity.is_a()})
        if entity.is_a("IfcRelAggregates") or entity.is_a("IfcRelNests"):
            for owner in entity.RelatedObjects or ():
                tables.emit("SpatialLinks", {"child_step_id": ref(owner), "parent_step_id": ref(entity.RelatingObject), "relation_step_id": ref(entity), "kind": entity.is_a()})
    duplicates = {str(k): v for k, v in ids.items() if k is None or v > 1}
    return {"object_count": len(object_ids), "duplicate_or_missing_global_ids": duplicates, **semantics.derive(model, tables)}


def write_result(job, result):
    """Publish only a complete flushed receipt; retain failed staging files."""
    destination = job / "result.json"
    staged = job / ("result.pending-" + uuid.uuid4().hex + ".json")
    with staged.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    if os.name == "nt":
        # Windows rename is atomic within the volume and refuses an existing target.
        os.rename(staged, destination)
    else:
        # os.rename replaces existing destinations on POSIX; hard-link publication
        # retains the no-overwrite contract for the same-directory staging file.
        os.link(staged, destination)
        with suppress(OSError):
                staged.unlink()


def failure_message(error):
    if isinstance(error, MemoryError):
        return "The file exceeded available conversion memory. No complete result was produced."
    return str(error) or type(error).__name__


def convert(source, output, *, row_limit=MAX_ROWS):
    validate_row_limit(row_limit)
    if RUNTIME_IMPORT_ERROR is not None:
        raise RuntimeError("Converter dependency unavailable; install the pinned requirements.txt dependencies: " + RUNTIME_IMPORT_ERROR)
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise ValueError("Expected an existing IFC file")
    source_format = source.suffix.lower()
    if source_format == ".ifcxml":
        raise ValueError("IFCXML is not supported by the DDC IFC reader; export IFC-SPF instead")
    if source_format not in (".ifc", ".ifczip"):
        raise ValueError("Expected .ifc or .ifczip input")
    source_pin = pin(source)
    output.mkdir(parents=True, exist_ok=True)
    job = output / (source.stem[:60] + "-" + uuid.uuid4().hex[:12])
    job.mkdir()
    started = datetime.now(timezone.utc).isoformat()
    result = {"schema": SCHEMA, "version": VERSION, "status": "FAILED", "folder": str(job), "started_utc": started,
              "source": source_pin, "engine": {"name": "DDC IFC Reader", "version": ifc_runtime.VERSION},
              "converter": pin(__file__), "modules": [pin(Path(__file__).with_name(name)) for name in ("semantics.py", "file_pins.py")] + [pin(p) for p in ifc_runtime.source_paths()], "errors": [], "full_fidelity_qualified": False,
              "excel_numeric_columns": EXCEL_NUMERIC_COLUMNS,
              "source_format": "IFCZIP" if source_format == ".ifczip" else "IFC-SPF",
              "limitations": ["No geometry/tessellation or calculated quantities", "Effective properties resolve only unique exact name paths; ambiguous candidates retained without selection", "SI normalization only scalar length/area/volume with unambiguous compatible SI/conversion units", "Legacy numeric values retain binary64 behavior; exact source REAL tokens are text in SourceReals and property provenance", "Exact SI decimal text is separate from approximate numeric cells; unsupported units/source provenance or decimal resource limits remain unresolved", "Structural and attribute-arity checks only; full EXPRESS validation not performed", "IFCZIP imports one unambiguous IFC-SPF member; auxiliary archive members are reported but not imported", "IFCXML is not supported by the DDC IFC reader", "Only declared SI measure columns may be numeric; precision/range/size/XML limits reference JSONL", "No comparison benchmark against cad2data performed"]}
    phase = "inspect_source"
    try:
        if source_format == ".ifc":
            with source.open("rb") as stream:
                if b"ISO-10303-21;" not in stream.read(4096):
                    raise ValueError("Missing STEP physical-file header in first 4096 bytes")
        else:
            result["source_container"] = inspect_ifczip(source)
        phase = "load_model"
        model = load_model(source, result.get("source_container"))
        result["ifc_schema"] = model.schema
        if model.schema not in ("IFC2X3", "IFC4", "IFC4X3"):
            raise ValueError(f"Unqualified IFC schema: {model.schema}")
        phase = "create_tables"
        tables = Tables(job, row_limit=row_limit)
        try:
            phase = "extract_tables"
            result["observations"] = extract(model, tables, source_pin["sha256"])
            tables.emit("Metadata", {"schema": SCHEMA, "source_sha256": source_pin["sha256"], "source_path": str(source), "source_format": result["source_format"], "source_container": result.get("source_container", {}), "ifc_schema": model.schema, "qualification": "SEMANTIC_TABLES_WITH_LIMITS", "limitations": result["limitations"], "excel_numeric_columns": EXCEL_NUMERIC_COLUMNS})
            phase = "finalize_tables"
            tables.close()
        except Exception:
            tables.abort()
            raise
        phase = "verify_source"
        if pin(source) != source_pin:
            raise RuntimeError("Source changed during conversion")
        result["tables"] = dict(tables.counts)
        result["cell_limits"] = dict(tables.cell_limits)
        phase = "hash_artifacts"
        result["artifacts"] = [pin(job / name) for name in ("drawing.xlsx", "data.sqlite", "data.jsonl")]
        result["data"] = str(job / "drawing.xlsx")
        result["status"] = "CONVERTED_WITH_LIMITS"
    except Exception as exc:
        result["status"] = "FAILED"
        result.pop("data", None)
        result.pop("artifacts", None)
        result["failure_phase"] = phase
        result["errors"].append({"type": type(exc).__name__, "message": failure_message(exc)})
    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    write_result(job, result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="DDC IFC to Excel: open semantic extraction")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = convert(args.source, args.output)
    except Exception as exc:
        result = {"schema": SCHEMA, "status": "FAILED", "errors": [{"type": type(exc).__name__, "message": failure_message(exc)}]}
    print(json.dumps({key: result[key] for key in ("schema", "status", "folder", "data", "errors") if key in result}, ensure_ascii=True))
    return 0 if result["status"] == "CONVERTED_WITH_LIMITS" else 1


if __name__ == "__main__":
    sys.exit(main())
