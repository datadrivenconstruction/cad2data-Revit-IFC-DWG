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
