"""Small first-party ISO 10303-21 / IFC-SPF structural reader.

This is a syntax reader, not an EXPRESS/IFC semantic implementation. It keeps
source entity ids, type names, positional attributes, references, aggregate
shape, typed values, and explicit `$`/`*` markers. It does not assign schema
attribute names or interpret geometry, units, inheritance, or relationships.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import threading
from typing import Callable


MAX_INPUT_BYTES = 512 * 1024 * 1024
MAX_ENTITIES = 5_000_000
MAX_REFERENCES = 25_000_000
MAX_VALUES_PER_ENTITY = 100_000
# Bound the whole record, including aggregate containers, typed wrappers and
# scalar descendants; the outer positional-attribute list is not a value node.
MAX_TOTAL_VALUES_PER_RECORD = 1_000_000
# Large flat aggregates may use the existing record budget. Their own container
# consumes one node; nested/sibling values share the unchanged cumulative cap.
# Keep the separate positional-attribute limit above unchanged.
MAX_AGGREGATE_VALUES = MAX_TOTAL_VALUES_PER_RECORD - 1
MAX_NESTING_DEPTH = 128
MAX_STRING_CHARS = 1_048_576
MAX_ID = (1 << 64) - 1

_NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
_HEX = re.compile(r"[0-9A-Fa-f]+\Z")


class Part21Error(ValueError):
    """Malformed or unsupported Part 21 syntax with source offset context."""


@dataclass(frozen=True)
class ParseSummary:
    status: str
    input_bytes: int
    header_records: int
    entities: int
    references: int
    output: str | None
    schema_interpreted: bool = False
    geometry_interpreted: bool = False


@dataclass(frozen=True)
class _Token:
    kind: str
    value: object
    offset: int


class _Lexer:
    def __init__(self, text: str, *, cancel_event: threading.Event | None = None):
        self.text = text
        self.pos = 0
        self.lookahead: _Token | None = None
        self.cancel_event = cancel_event

    def _error(self, message: str, offset: int | None = None) -> Part21Error:
        at = self.pos if offset is None else offset
        line = self.text.count("\n", 0, at) + 1
        previous = self.text.rfind("\n", 0, at)
        column = at - previous
        return Part21Error(f"{message} at character {at} (line {line}, column {column})")

    def _skip(self) -> None:
        text, length = self.text, len(self.text)
        while self.pos < length:
            if self.cancel_event is not None and self.cancel_event.is_set():
                raise Part21Error("Cancelled during lexical scan")
            if text[self.pos].isspace():
                self.pos += 1
            elif text.startswith("/*", self.pos):
                end = text.find("*/", self.pos + 2)
                if end < 0:
                    raise self._error("Unterminated comment")
                self.pos = end + 2
            else:
                return

    def peek(self) -> _Token:
        if self.lookahead is None:
            self.lookahead = self._next()
        return self.lookahead

    def take(self) -> _Token:
        token = self.peek()
        self.lookahead = None
        return token

    def _string(self, start: int) -> _Token:
        text, size = self.text, len(self.text)
        self.pos += 1
        output: list[str] = []
        output_length = 0
        next_cancel_check = start + 4096

        def append(value: str) -> None:
            nonlocal output_length
            output_length += len(value)
            if output_length > MAX_STRING_CHARS:
                raise self._error(f"String literal exceeds {MAX_STRING_CHARS} decoded characters", start)
            output.append(value)

        while self.pos < size:
            # Escapes advance by more than one character and may never land on
            # an exact multiple of 4096 (e.g. repeated doubled apostrophes).
            if self.pos >= next_cancel_check:
                if self.cancel_event is not None and self.cancel_event.is_set():
                    raise self._error("Cancelled during string scan", self.pos)
                next_cancel_check = self.pos + 4096
            char = text[self.pos]
            if char == "'":
                if self.pos + 1 < size and text[self.pos + 1] == "'":
                    append("'")
                    self.pos += 2
                    continue
                self.pos += 1
                return _Token("STRING", "".join(output), start)
            if char in "\r\n":
                raise self._error("Raw line break inside string literal")
            if char != "\\":
                append(char)
                self.pos += 1
                continue

            if text.startswith("\\X2\\", self.pos):
                append(self._unicode_escape(start, digits=4))
                continue
            if text.startswith("\\X4\\", self.pos):
                append(self._unicode_escape(start, digits=8))
                continue
            if text.startswith("\\PA\\", self.pos):
                self.pos += 4
                continue
            if text.startswith("\\X\\", self.pos):
                hex_start = self.pos + 3
                payload = text[hex_start:hex_start + 2]
                if len(payload) != 2 or not _HEX.fullmatch(payload):
                    raise self._error("Malformed X escape byte", self.pos)
                append(chr(int(payload, 16)))
                self.pos = hex_start + 2
                continue
            if text.startswith("\\S\\", self.pos):
                char_index = self.pos + 3
                if char_index >= size:
                    raise self._error("Truncated S escape", self.pos)
                byte = ord(text[char_index])
                if byte < 0x20 or byte > 0x7E:
                    raise self._error("S escape requires a graphic ASCII character", self.pos)
                append(chr(byte + 0x80))
                self.pos = char_index + 1
                continue
            if text.startswith("\\\\", self.pos):
                append("\\")
                self.pos += 2
                continue
            raise self._error("Unsupported or malformed string escape", self.pos)
        raise self._error("Unterminated string literal", start)

    def _unicode_escape(self, start: int, *, digits: int) -> str:
        text = self.text
        prefix_size = 4
        data_start = self.pos + prefix_size
        terminator = "\\X0\\"
        maximum_payload = MAX_STRING_CHARS * 8
        search_limit = min(len(text), data_start + maximum_payload + len(terminator))
        cursor = data_start
        end = -1
        while cursor < search_limit:
            if self.cancel_event is not None and self.cancel_event.is_set():
                raise self._error("Cancelled during Unicode escape scan", cursor)
            chunk_end = min(search_limit, cursor + 65536)
            end = text.find(terminator, cursor, min(len(text), chunk_end + len(terminator) - 1))
            if end >= 0:
                break
            cursor = chunk_end
        if end < 0:
            if search_limit < len(text) and search_limit >= data_start + maximum_payload:
                raise self._error("Unicode escape payload exceeds configured limit", start)
            raise self._error("Unicode escape has no \\X0\\ terminator", start)
        payload = text[data_start:end]
        if not payload or len(payload) % digits or not _HEX.fullmatch(payload):
            raise self._error("Unicode escape has invalid hexadecimal payload", data_start)
        decoded: list[str] = []
        if digits == 4:
            raw = bytes.fromhex(payload)
            try:
                decoded.append(raw.decode("utf-16-be", errors="strict"))
            except UnicodeDecodeError as exc:
                raise self._error("Invalid UTF-16 code units in X2 escape", data_start + exc.start * 2) from exc
        else:
            for index in range(0, len(payload), 8):
                point = int(payload[index:index + 8], 16)
                if point > 0x10FFFF or 0xD800 <= point <= 0xDFFF:
                    raise self._error("Invalid Unicode scalar in X4 escape", data_start + index)
                decoded.append(chr(point))
        self.pos = end + 4
        return "".join(decoded)

    def _next(self) -> _Token:
        self._skip()
        text, size = self.text, len(self.text)
        if self.pos >= size:
            return _Token("EOF", None, self.pos)
        start = self.pos
        char = text[self.pos]
        if char == "'":
            return self._string(start)
        if char in "(),;=":
            self.pos += 1
            return _Token(char, char, start)
        if char in "$*":
            self.pos += 1
            return _Token("SPECIAL", char, start)
        if char == "#":
            self.pos += 1
            digits_start = self.pos
            while self.pos < size and '0' <= text[self.pos] <= '9':
                if self.pos - digits_start >= 20:
                    raise self._error("Invalid or oversized entity reference", start)
                self.pos += 1
            digits = text[digits_start:self.pos]
            if not digits or len(digits) > 20:
                raise self._error("Invalid or oversized entity reference", start)
            number = int(digits)
            if number <= 0 or number > MAX_ID:
                raise self._error("Entity reference is outside the positive 64-bit range", start)
            return _Token("REF", number, start)
        if char == "." and not (self.pos + 1 < size and text[self.pos + 1].isdigit()):
            end = text.find(".", self.pos + 1)
            if end < 0:
                raise self._error("Unterminated enumeration", start)
            body = text[self.pos + 1:end]
            if not body or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", body):
                raise self._error("Malformed enumeration", start)
            self.pos = end + 1
            return _Token("ENUM", text[start:self.pos], start)
        # One character beyond the accepted budget is enough to reject a long
        # numeric literal without scanning an arbitrarily large digit suffix.
        number_match = _NUMBER.match(text, self.pos, self.pos + 129)
        if number_match is not None:
            lexeme = number_match.group(0)
            if len(lexeme) > 128:
                raise self._error("Numeric literal exceeds 128 characters", start)
            self.pos = number_match.end()
            try:
                if any(marker in lexeme for marker in ".Ee"):
                    value = Decimal(lexeme)
                    as_float = float(value)
                    if not value.is_finite() or not math.isfinite(as_float):
                        raise self._error("Non-finite or overflowing real number", start)
                    return _Token("REAL", lexeme, start)
                return _Token("INTEGER", int(lexeme), start)
            except (InvalidOperation, OverflowError, ValueError) as exc:
                if isinstance(exc, Part21Error):
                    raise
                raise self._error("Invalid numeric literal", start) from exc
        name_match = _NAME.match(text, self.pos)
        if name_match is not None:
            self.pos = name_match.end()
            return _Token("NAME", name_match.group(0), start)
        raise self._error(f"Unexpected character {char!r}", start)


class _Parser:
    def __init__(self, text: str, *, cancel_event: threading.Event | None = None):
        self.lexer = _Lexer(text, cancel_event=cancel_event)
        self.cancel_event = cancel_event
        self.entity_ids: set[int] = set()
        self.references: list[tuple[int | None, int]] = []
        self.header_records = 0
        self.entities = 0
        self.current_entity: int | None = None
        self.record_value_nodes = 0

    def _check_cancel(self) -> None:
        if self.cancel_event is not None and self.cancel_event.is_set():
            raise Part21Error("Cancelled during parse")

    def _expect(self, kind: str, value: object | None = None) -> _Token:
        self._check_cancel()
        token = self.lexer.take()
        if token.kind != kind or (value is not None and token.value != value):
            raise Part21Error(f"Expected {value if value is not None else kind}, got {token.value!r} at character {token.offset}")
        return token

    def _keyword(self, value: str) -> None:
        token = self._expect("NAME")
        if str(token.value).upper() != value:
            raise Part21Error(f"Expected {value}, got {token.value!r} at character {token.offset}")

    def _value(self, depth: int = 0):
        if self.record_value_nodes >= MAX_TOTAL_VALUES_PER_RECORD:
            raise Part21Error(f"Record exceeds {MAX_TOTAL_VALUES_PER_RECORD} total value nodes")
        self.record_value_nodes += 1
        if depth > MAX_NESTING_DEPTH:
            token = self.lexer.peek()
            raise Part21Error(f"Aggregate nesting exceeds {MAX_NESTING_DEPTH} at character {token.offset}")
        self._check_cancel()
        token = self.lexer.peek()
        if token.kind == "REF":
            target = int(self.lexer.take().value)
            if len(self.references) >= MAX_REFERENCES:
                raise Part21Error(f"Reference count exceeds {MAX_REFERENCES}")
            self.references.append((self.current_entity, target))
            return {"ref": target}
        if token.kind == "SPECIAL":
            return {"step_special": self.lexer.take().value}
        if token.kind == "ENUM":
            return {"enum": self.lexer.take().value}
        if token.kind == "STRING":
            return self.lexer.take().value
        if token.kind == "INTEGER":
            return self.lexer.take().value
        if token.kind == "REAL":
            return {"step_real": self.lexer.take().value}
        if token.kind == "(":
            self.lexer.take()
            values = []
            if self.lexer.peek().kind == ")":
                self.lexer.take()
                return values
            while True:
                if len(values) >= MAX_AGGREGATE_VALUES:
                    raise Part21Error(f"Aggregate exceeds {MAX_AGGREGATE_VALUES} values")
                values.append(self._value(depth + 1))
                delimiter = self.lexer.peek()
                if delimiter.kind == ")":
                    self.lexer.take()
                    return values
                self._expect(",")
        if token.kind == "NAME":
            name = str(self.lexer.take().value)
            if self.lexer.peek().kind != "(":
                raise Part21Error(f"Bare identifier is not a Part 21 value at character {token.offset}")
            self.lexer.take()
            inner = self._value(depth + 1)
            self._expect(")")
            return {"type": name, "value": inner}
        raise Part21Error(f"Expected Part 21 value, got {token.value!r} at character {token.offset}")

    def _record_attributes(self) -> list:
        self.record_value_nodes = 0
        self._expect("(")
        values = []
        if self.lexer.peek().kind == ")":
            self.lexer.take()
            return values
        while True:
            if len(values) >= MAX_VALUES_PER_ENTITY:
                raise Part21Error(f"Record exceeds {MAX_VALUES_PER_ENTITY} positional values")
            values.append(self._value())
            if self.lexer.peek().kind == ")":
                self.lexer.take()
                return values
            self._expect(",")

    def parse(self, emit: Callable[[dict], None]) -> dict:
        self._keyword("ISO-10303-21")
        self._expect(";")
        self._keyword("HEADER")
        self._expect(";")
        while True:
            self._check_cancel()
            token = self.lexer.peek()
            if token.kind == "NAME" and str(token.value).upper() == "ENDSEC":
                self.lexer.take()
                self._expect(";")
                break
            name = str(self._expect("NAME").value)
            attributes = self._record_attributes()
            self._expect(";")
            emit({"record_type": "header", "name": name, "attributes": attributes})
            self.header_records += 1

        self._keyword("DATA")
        self._expect(";")
        while True:
            self._check_cancel()
            token = self.lexer.peek()
            if token.kind == "NAME" and str(token.value).upper() == "ENDSEC":
                self.lexer.take()
                self._expect(";")
                break
            if token.kind != "REF":
                raise Part21Error(f"Expected entity instance or DATA ENDSEC, got {token.value!r} at character {token.offset}")
            if self.entities >= MAX_ENTITIES:
                raise Part21Error(f"Entity count exceeds {MAX_ENTITIES}")
            entity_id = int(self._expect("REF").value)
            if entity_id in self.entity_ids:
                raise Part21Error(f"Duplicate entity id #{entity_id}")
            self._expect("=")
            name_token = self._expect("NAME")
            entity_type = str(name_token.value)
            self.current_entity = entity_id
            attributes = self._record_attributes()
            self._expect(";")
            self.current_entity = None
            self.entity_ids.add(entity_id)
            self.entities += 1
            emit({"record_type": "entity", "id": entity_id,
                  "type": entity_type, "attributes": attributes})

        self._keyword("END-ISO-10303-21")
        self._expect(";")
        token = self.lexer.peek()
        if token.kind != "EOF":
            raise Part21Error(f"Unexpected trailing content at character {token.offset}")
        for owner, target in self.references:
            if target not in self.entity_ids:
                source = f" in #{owner}" if owner is not None else " in header"
                raise Part21Error(f"Missing entity reference #{target}{source}")
        return {"header_records": self.header_records, "entities": self.entities,
                "references": len(self.references)}


def parse_text(text: str, *, cancel_event: threading.Event | None = None) -> list[dict]:
    """Parse a bounded test/control string into structural rows."""
    if not isinstance(text, str):
        raise Part21Error("Part 21 text must be a string")
    if len(text) > MAX_INPUT_BYTES:
        raise Part21Error(f"Input exceeds {MAX_INPUT_BYTES} byte limit")
    byte_count = 0
    # Match the file byte budget without allocating a second whole-file copy.
    try:
        for offset in range(0, len(text), 65536):
            if cancel_event is not None and cancel_event.is_set():
                raise Part21Error("Cancelled while checking text input")
            byte_count += len(text[offset:offset + 65536].encode('utf-8'))
            if byte_count > MAX_INPUT_BYTES:
                raise Part21Error(f"Input exceeds {MAX_INPUT_BYTES} byte limit")
    except UnicodeEncodeError as exc:
        raise Part21Error("Input text contains an invalid Unicode scalar") from exc
    rows: list[dict] = []
    _Parser(text, cancel_event=cancel_event).parse(rows.append)
    return rows


def _read_source(source: str | Path, *, cancel_event: threading.Event | None = None) -> tuple[str, int]:
    """Shared bounded UTF-8 snapshot read for structural and model consumers."""
    source = Path(source)
    if cancel_event is not None and cancel_event.is_set():
        raise Part21Error("Cancelled before file access")
    try:
        before = source.stat()
        size = before.st_size
        if size > MAX_INPUT_BYTES:
            raise Part21Error(f"Input exceeds {MAX_INPUT_BYTES} byte limit")
        with source.open("rb") as stream:
            payload = bytearray()
            while True:
                if cancel_event is not None and cancel_event.is_set():
                    raise Part21Error("Cancelled while reading input")
                chunk = stream.read(min(1024 * 1024, MAX_INPUT_BYTES - len(payload) + 1))
                if not chunk:
                    break
                payload.extend(chunk)
                if len(payload) > MAX_INPUT_BYTES:
                    raise Part21Error(f"Input grew beyond {MAX_INPUT_BYTES} byte limit while reading")
        after = source.stat()
        identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
        identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
        if len(payload) != size or identity_before != identity_after:
            raise Part21Error("Input changed or was truncated while reading")
        # Same-size writes can share timestamps on real filesystems. Compare a
        # bounded second read with the bytes we will parse, not just metadata.
        # This is a content check at read time, not a filesystem lock: later
        # writes remain possible after this observation.
        # Payload is no longer mutated after collection; expose only a read-only
        # view for comparison, without a second whole-file bytes allocation.
        view = memoryview(payload).toreadonly()
        with source.open("rb") as stream:
            offset = 0
            while offset < len(payload):
                if cancel_event is not None and cancel_event.is_set():
                    raise Part21Error("Cancelled while verifying input snapshot")
                chunk = stream.read(min(1024 * 1024, len(payload) - offset))
                if not chunk or chunk != view[offset:offset + len(chunk)]:
                    raise Part21Error("Input content changed while verifying snapshot")
                offset += len(chunk)
            if stream.read(1):
                raise Part21Error("Input grew while verifying snapshot")
        if cancel_event is not None and cancel_event.is_set():
            raise Part21Error("Cancelled while verifying input snapshot")
        final = source.stat()
        identity_final = (final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns, final.st_ctime_ns)
        if identity_final != identity_after:
            raise Part21Error("Input changed while verifying snapshot")
        text = payload.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise Part21Error(f"Input is not valid UTF-8 at byte {exc.start}") from exc
    return text, len(payload)


def parse_file(source: str | Path, output: str | Path, *,
               cancel_event: threading.Event | None = None) -> ParseSummary:
    """Parse one UTF-8 Part 21 file and atomically publish JSONL without overwrite."""
    source, destination = Path(source), Path(output)
    if source.resolve() == destination.resolve():
        raise ValueError("Input and JSONL output paths must differ")
    if destination.exists():
        raise FileExistsError(str(destination))
    text, input_bytes = _read_source(source, cancel_event=cancel_event)

    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, staging_name = tempfile.mkstemp(prefix=destination.name + ".", suffix=".pending",
                                         dir=destination.parent)
    staging = Path(staging_name)
    summary = None
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output_stream:
            def emit(row: dict) -> None:
                output_stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False,
                                               separators=(",", ":")) + "\n")
            counts = _Parser(text, cancel_event=cancel_event).parse(emit)
            output_stream.flush()
            os.fsync(output_stream.fileno())
        if cancel_event is not None and cancel_event.is_set():
            raise Part21Error("Cancelled before JSONL publication")
        os.link(staging, destination)
        staging.unlink()
        summary = ParseSummary("STRUCTURAL_PARSE_COMPLETE", input_bytes, counts["header_records"],
                               counts["entities"], counts["references"], str(destination.resolve()))
        return summary
    except Exception:
        try:
            staging.unlink()
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="First-party IFC-SPF structural reader; no EXPRESS/geometry interpretation")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="new JSONL path; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        result = parse_file(args.input, args.output)
    except (OSError, ValueError, Part21Error) as exc:
        print(json.dumps({"status": "FAILED", "can_convert": False,
                          "error_type": type(exc).__name__, "error": str(exc)},
                         ensure_ascii=True, separators=(",", ":")))
        return 2
    print(json.dumps(asdict(result), ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
