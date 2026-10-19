"""Load the suite's own IFC implementation; no external parser fallback."""
from pathlib import Path
import hashlib
import importlib.util
import os
import sys
import types

ROOT = Path(__file__).resolve().parents[1] / "ifc-independent"
PACKAGE = "_ddc_own_ifc_" + hashlib.sha256(os.path.normcase(str(ROOT.resolve())).encode("utf-8")).hexdigest()


def _load():
    expected = {PACKAGE + ".reader": ROOT / "reader.py", PACKAGE + ".model": ROOT / "model.py"}
    for name in tuple(sys.modules):
        if not (name == PACKAGE or name.startswith(PACKAGE + ".")):
            continue
        cached = sys.modules[name]
        if name == PACKAGE:
            if [Path(p).resolve() for p in getattr(cached, "__path__", ())] != [ROOT.resolve()]:
                raise ImportError("Conflicting DDC IFC package search path")
        elif name not in expected or Path(getattr(cached, "__file__", "")).resolve() != expected[name].resolve():
            raise ImportError("Conflicting cached DDC IFC module: " + name)
    before = set(sys.modules)
    try:
        if PACKAGE not in sys.modules:
            package = types.ModuleType(PACKAGE)
            package.__path__ = [str(ROOT)]
            sys.modules[PACKAGE] = package
        for name, path in expected.items():
            if name in sys.modules:
                continue
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None or spec.loader is None:
                raise ImportError("DDC IFC implementation is unavailable")
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        return sys.modules[PACKAGE + ".model"]
    except Exception:
        for name in tuple(sys.modules):
            if name not in before and (name == PACKAGE or name.startswith(PACKAGE + ".")):
                sys.modules.pop(name, None)
        raise


model = _load()
Entity = (model.Entity, model.TypedValue) if hasattr(model, "TypedValue") else model.Entity
model_from_file = model.model_from_file
VERSION = "0.3.0-preview"


def source_paths():
    """Receipt includes every schema, so its verifier need not trust input metadata."""
    return [Path(__file__).resolve(), *model.source_paths()]
