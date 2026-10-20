"""Worker process: build the DDC Viewer package of one IFC file into a NEW folder.

Usage: python viewer_worker.py MODEL.ifc NEW_FOLDER
Prints one JSON line: {"status": "VIEWER_PACKAGE_READY", "package": ".../package.js", ...} or FAILED.
The package is written to NEW_FOLDER.partial and renamed only when complete.
"""
import json
import os
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent


def _exporter():
    for folder in (HERE / "viewer" / "exporters", HERE.parent / "ddc-viewer" / "exporters"):
        if (folder / "ifc_viewer_export.py").is_file():
            sys.path.insert(0, str(folder))
            import ifc_viewer_export
            return ifc_viewer_export
    raise ImportError("DDC Viewer IFC exporter not found")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(json.dumps({"status": "FAILED", "message": "usage: viewer_worker.py MODEL.ifc NEW_FOLDER"}))
        return 2
    source, target = Path(argv[0]), Path(argv[1])
    try:
        if target.exists():
            raise FileExistsError("viewer package folder already exists")
        exporter = _exporter()
        reader = HERE.parent / "ifc-independent"
        document = exporter.build_package(source, reader_dir=reader)
        work = target.with_name(target.name + ".partial")
        shutil.rmtree(work, ignore_errors=True)
        info = exporter.write_package(document, work)
        os.replace(work, target)
        cov = document["coverage"]
        print(json.dumps({"status": "VIEWER_PACKAGE_READY", "package": str(target / "package.js"), "bytes": info["bytes"],
                          "elements": cov["elements"], "elements_with_geometry": cov["elements_with_geometry"],
                          "triangles": cov["triangles"]}, ensure_ascii=False))
        return 0
    except MemoryError:
        print(json.dumps({"status": "FAILED", "message": "Not enough memory to build the viewer package."}))
        return 7
    except Exception as exc:
        print(json.dumps({"status": "FAILED", "message": "%s: %s" % (type(exc).__name__, str(exc)[:300])}, ensure_ascii=False))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
