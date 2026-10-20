"""IFC to Excel simplified-mode runtime: the own schema-free reader (no buildingSMART schema data).

Same interface as ``ifc_runtime`` (``model``, ``Entity``, ``model_from_file``, ``VERSION``,
``source_paths``) but backed by ``sources/ifc-independent/core_model.py``: a generic
positional STEP reader plus a small hand-written table of the core entities.  Entities
outside that table are exported generically (file type name, STEP id, raw attributes
``Attr1..AttrN``).  See LEGAL_NOTE.md.  Compiled builds embed core_model directly.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1] / "ifc-independent"
try:
    import core_model as model  # compiled in, or already importable
except ImportError:
    if (ROOT / "core_model.py").is_file() and str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import core_model as model

Entity = (model.Entity, model.TypedValue)
model_from_file = model.model_from_file
VERSION = "2.0.0"
MODE = model.MODE


def source_paths():
    """Code only: this runtime loads no schema data files."""
    import geometry
    return [Path(__file__).resolve(), *model.source_paths(), Path(geometry.__file__).resolve()]
