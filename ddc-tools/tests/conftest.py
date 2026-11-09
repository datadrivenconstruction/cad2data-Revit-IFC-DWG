import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

import make_sample  # noqa: E402


@pytest.fixture()
def export_dir(tmp_path):
    d = tmp_path / "export"
    make_sample.write_all(d)
    return d


@pytest.fixture()
def rows():
    h = make_sample.HEADER
    return [dict(zip(h, r)) for r in make_sample.rows()]


@pytest.fixture()
def rules_basic():
    return ROOT / "examples" / "rules_basic.yaml"


# ---------------------------------------------------------------------------- BCF schemas
# The buildingSMART BCF XSD files are licensed CC BY-ND 4.0 (not a permissive licence), so they are not
# kept in this repository. Tests that validate against them download them once into a cache folder
# (env DDC_BCF_XSD_DIR, default: the pytest cache) and skip when lxml or the network is not available.
XSD_BASE = "https://raw.githubusercontent.com/buildingSMART/BCF-XML/{branch}/Schemas/{name}.xsd"
XSD_BRANCH = {"2.1": "release_2_1", "3.0": "release_3_0"}
XSD_FILES = {"2.1": ["markup", "visinfo", "version", "project"],
             "3.0": ["markup", "visinfo", "version", "project", "extensions", "shared-types", "documents"]}


@pytest.fixture(scope="session")
def bcf_validator(tmp_path_factory):
    etree = pytest.importorskip("lxml.etree")
    import os
    import urllib.request

    base = Path(os.environ.get("DDC_BCF_XSD_DIR") or tmp_path_factory.mktemp("bcf_xsd"))
    schemas = {}
    for ver, names in XSD_FILES.items():
        d = base / ver
        d.mkdir(parents=True, exist_ok=True)
        for n in names:
            f = d / f"{n}.xsd"
            if not f.exists():
                try:
                    with urllib.request.urlopen(XSD_BASE.format(branch=XSD_BRANCH[ver], name=n), timeout=30) as r:
                        f.write_bytes(r.read())
                except OSError as e:
                    pytest.skip(f"BCF XSD not available (offline?): {e}")
        schemas[ver] = {n: etree.XMLSchema(etree.parse(str(d / f"{n}.xsd")))
                        for n in names if n not in ("shared-types", "documents")}

    def validate(path, version):
        import zipfile
        z = zipfile.ZipFile(path)
        errors, seen = [], set()
        kinds = {"markup.bcf": "markup", "bcf.version": "version", "project.bcfp": "project", "extensions.xml": "extensions"}
        for n in z.namelist():
            base_name = n.rsplit("/", 1)[-1]
            kind = kinds.get(base_name) or ("visinfo" if base_name.endswith(".bcfv") else None)
            if not kind:
                errors.append(f"{n}: unexpected file")
                continue
            seen.add(kind)
            sch = schemas[version][kind]
            doc = etree.fromstring(z.read(n))
            if not sch.validate(doc):
                errors.append(f"{n}: {sch.error_log.last_error}")
        return errors, seen

    return validate


# ---------------------------------------------------------------------------- optional IFC fixtures
# The IFC-derived fixtures (ifc_excel, ifc_duplex_excerpt*) are not shipped in the public tree; tests that
# need them are skipped when the folders are absent. Drop your own IFC to Excel output into them to run.
_OPTIONAL = {
    "ifc_excel": Path(__file__).parent / "data" / "ifc_excel",
    "ifc_duplex_excerpt": Path(__file__).parent / "fixtures" / "ifc_duplex_excerpt",
}


def pytest_collection_modifyitems(config, items):
    import re
    missing = [k for k, p in _OPTIONAL.items() if not p.exists()]
    if not missing:
        return
    skip = pytest.mark.skip(reason="IFC-derived fixture not shipped: " + ", ".join(missing))
    cache = {}

    def tainted_defs(path):
        # top-level blocks of a test module; a block is tainted when it names a missing fixture folder
        # (directly or through a module constant / helper that does)
        if path in cache:
            return cache[path]
        text = Path(path).read_text(encoding="utf-8")
        blocks = re.split(r"(?m)(?<!\)\n)^(?=def |@pytest|[A-Za-z_]\w* = |[A-Za-z_]\w*, \w+ = )", text)
        named = {}
        for b in blocks:
            m = re.search(r"(?m)^(?:def (\w+)|(\w+)(?:, (\w+))? = )", b)
            if m:
                for n in m.groups():
                    if n:
                        named[n] = b
        bad = {n for n, b in named.items() if any(k in b for k in missing)}
        changed = True
        while changed:
            changed = False
            for n, b in named.items():
                if n not in bad and any(re.search(r"(?<![\w\"'])" + re.escape(x) + r"(?![\w\"'])", b) for x in bad):
                    bad.add(n)
                    changed = True
        cache[path] = bad
        return bad

    for item in items:
        bad = tainted_defs(item.path)
        names = {item.function.__name__}
        for defs in item._fixtureinfo.name2fixturedefs.values():
            names |= {d.func.__name__ for d in defs}
        if names & bad:
            item.add_marker(skip)
