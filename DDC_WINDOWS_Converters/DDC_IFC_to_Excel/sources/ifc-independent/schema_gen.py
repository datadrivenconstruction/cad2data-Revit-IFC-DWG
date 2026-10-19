"""Generate compact entity/type metadata from pinned official buildingSMART EXPRESS.

This is a deliberately small extractor for EXPRESS declarations, not a general
EXPRESS compiler. It fails closed when entity inheritance/attribute extraction
is ambiguous. Runtime mapping consumes the generated JSON only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
OFFICIAL = HERE / "schemas" / "official"
OUT = HERE / "schemas" / "generated"
SCHEMAS = {
    "IFC2X3": ("IFC2X3_TC1.exp", "2.3.0.1", "https://github.com/buildingSMART/Standards-builds/blob/main/IFC/RELEASE/IFC2x3/TC1/EXPRESS/IFC2X3_TC1.exp"),
    "IFC4": ("IFC4_ADD2_TC1.exp", "4.0.2.1", "https://github.com/buildingSMART/Standards-builds/blob/main/IFC/RELEASE/IFC4/ADD2_TC1/EXPRESS/IFC4.exp"),
    "IFC4X3": ("IFC4X3_ADD2.exp", "4.3.2.0", "https://github.com/buildingSMART/Standards-builds/blob/main/IFC/RELEASE/IFC4_3/HTML/IFC4X3_ADD2.exp"),
}


class SchemaExtractError(ValueError):
    pass


def extract(path: Path) -> dict:
    raw = path.read_bytes()
    source_hash = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8-sig")
    text = re.sub(r"\(\*.*?\*\)", " ", text, flags=re.S)
    entities: dict[str, dict] = {}
    for match in re.finditer(r"\bENTITY\s+([A-Za-z][A-Za-z0-9_]*)\b(.*?)\bEND_ENTITY\s*;", text, flags=re.I | re.S):
        name, body = match.group(1), match.group(2)
        if name in entities:
            raise SchemaExtractError(f"duplicate entity declaration {name}")
        header_end = body.find(";")
        if header_end < 0:
            raise SchemaExtractError(f"missing entity header terminator in {name}")
        header, declaration = body[:header_end], body[header_end + 1:]
        section = re.search(r"^\s*(DERIVE|INVERSE|UNIQUE|WHERE)\b", declaration, flags=re.I | re.M)
        if section:
            declaration = declaration[:section.start()]
        parents_match = re.search(r"\bSUBTYPE\s+OF\s*\((.*?)\)", header, flags=re.I | re.S)
        parents = re.findall(r"[A-Za-z][A-Za-z0-9_]*", parents_match.group(1)) if parents_match else []
        fields = []
        for statement in declaration.split(";"):
            statement = statement.strip()
            if not statement:
                continue
            field = re.match(r"(?:SELF\\[A-Za-z][A-Za-z0-9_]*\.)?([A-Za-z][A-Za-z0-9_]*)\s*:\s*", statement, flags=re.I)
            if field:
                fields.append(field.group(1))
            elif re.search(r"\b(?:SUBTYPE|SUPERTYPE|ABSTRACT)\b", statement, flags=re.I):
                continue
            else:
                raise SchemaExtractError(f"unrecognized declaration in {name}: {statement[:90]!r}")
        derived = []
        derive_match = re.search(r"^\s*DERIVE\b(.*?)(?=^\s*(?:INVERSE|UNIQUE|WHERE)\b|\Z)", body, flags=re.I | re.M | re.S)
        if derive_match:
            for statement in derive_match.group(1).split(";"):
                field = re.match(r"\s*(?:SELF\\([A-Za-z][A-Za-z0-9_]*)\.)?([A-Za-z][A-Za-z0-9_]*)\s*:", statement, flags=re.I)
                if field:
                    qualified = re.match(r"\s*SELF\\([A-Za-z][A-Za-z0-9_]*)\.([A-Za-z][A-Za-z0-9_]*)\s*:", statement, flags=re.I)
                    derived.append({"name": field.group(1), "redefines": qualified.group(2) if qualified else None})
                elif statement.strip():
                    raise SchemaExtractError(f"unrecognized DERIVE declaration in {name}: {statement[:90]!r}")
        entities[name] = {"parents": parents, "declared": fields, "derived": derived}

    if not entities:
        raise SchemaExtractError(f"no entities found in {path}")
    for name, info in entities.items():
        for parent in info["parents"]:
            if parent not in entities:
                raise SchemaExtractError(f"{name} has unknown parent {parent}")

    visiting: set[str] = set()
    done: set[str] = set()

    def resolve(name: str) -> None:
        if name in done:
            return
        if name in visiting:
            raise SchemaExtractError(f"inheritance cycle at {name}")
        visiting.add(name)
        info = entities[name]
        inherited: list[str] = []
        ancestors: list[str] = []
        inherited_derived: list[str] = []
        for parent in info["parents"]:
            resolve(parent)
            parent_info = entities[parent]
            for ancestor in parent_info["ancestors"] + [parent]:
                if ancestor not in ancestors:
                    ancestors.append(ancestor)
            for attr in parent_info["attributes"]:
                if attr not in inherited:
                    inherited.append(attr)
            for index in parent_info["derived_slots"]:
                attr = parent_info["attributes"][index]
                if attr not in inherited_derived:
                    inherited_derived.append(attr)
        # Duplicate declarations would make position mapping ambiguous.
        if set(info["declared"]) & set(inherited):
            raise SchemaExtractError(f"attribute redeclaration requires explicit handling in {name}")
        attributes = inherited + info["declared"]
        derived = list(inherited_derived)
        for item in info["derived"]:
            attr_name, redefines = item["name"], item["redefines"]
            if redefines:
                if redefines not in attributes:
                    raise SchemaExtractError(f"{attr_name} redefines absent inherited attribute {redefines} in {name}")
                index = attributes.index(redefines)
                attributes[index] = redefines
                derived.append(redefines)
            elif attr_name in attributes:
                # EXPRESS can restate an inherited derived attribute without a
                # qualified redeclaration; the slot remains where inherited.
                derived.append(attr_name)
            else:
                # A fresh derived attribute is not serialized as an argument
                # slot. Keep its declaration metadata, but never shift slots.
                pass
        info["attributes"] = attributes
        info["derived_slots"] = [i for i, attr in enumerate(attributes) if attr in derived]
        info["ancestors"] = ancestors
        visiting.remove(name)
        done.add(name)

    for name in entities:
        resolve(name)
    types = {}
    for match in re.finditer(r"\bTYPE\s+([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.*?)\bEND_TYPE\s*;", text, flags=re.I | re.S):
        name, body = match.group(1), match.group(2).strip()
        select = re.search(r"\bSELECT\s*\((.*?)\)", body, flags=re.I | re.S)
        enumeration = re.search(r"\bENUMERATION\s+OF\s*\((.*?)\)", body, flags=re.I | re.S)
        types[name.casefold()] = {"name": name,
                       "select": re.findall(r"[A-Za-z][A-Za-z0-9_]*", select.group(1)) if select else None,
                       "enumeration": re.findall(r"[A-Za-z][A-Za-z0-9_]*", enumeration.group(1)) if enumeration else None}
    return {"schema": path.stem, "source": {"filename": path.name, "sha256": source_hash, "bytes": len(raw)},
            "entities": entities, "types": types}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for normalized, (filename, version, url) in SCHEMAS.items():
        data = extract(OFFICIAL / filename)
        data["schema"] = normalized
        data["version"] = version
        data["official_source_url"] = url
        target = OUT / f"{normalized}.json"
        target.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"{normalized}: {len(data['entities'])} entities, {len(data['types'])} types -> {target.name}")


if __name__ == "__main__":
    main()
