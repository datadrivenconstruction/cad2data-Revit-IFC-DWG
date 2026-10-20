"""'Open in viewer' for IFC to Excel: DDC Viewer package built on demand, opened in the browser.

The package is written by the viewer's IFC exporter (``sources/ddc-viewer/exporters``) in a
separate Python process (``viewer_worker.py``), next to the accepted result (``<folder>/viewer``)
or in a per-user cache when the file was not converted; an existing package is reused.  The
viewer runs locally from ``file://``; nothing leaves the machine.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
TIMEOUT = 3600


def viewer_index():
    for path in (HERE / "viewer" / "index.html", HERE.parent / "ddc-viewer" / "index.html"):
        if path.is_file():
            return path
    return None


def viewer_url(index, package_js, language="en"):
    return Path(index).resolve().as_uri() + "?pkg=" + quote(Path(package_js).resolve().as_uri(), safe="") + "&lang=" + language


def package_folder(result):
    folder = result.get("folder") if result else None
    if folder and result.get("status") == "CONVERTED_WITH_LIMITS" and Path(folder).is_dir():
        return Path(folder) / "viewer"
    source = Path(result["source"])
    try:
        st = source.stat()
        key = "%s|%d|%d" % (source.resolve(), st.st_size, st.st_mtime_ns)
    except OSError:
        key = str(source)
    base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "DDC" / "IFC-to-Excel" / "viewer"
    return base / hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def worker_command(source, target):
    return [sys.executable, "-X", "utf8", "-B", str(HERE / "viewer_worker.py"), str(source), str(target)]


def build(source, target, runner=subprocess.run):
    """Run the worker; returns its JSON result line (never raises)."""
    try:
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        done = runner(worker_command(source, target), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      stdin=subprocess.DEVNULL, creationflags=flags, timeout=TIMEOUT)
        return json.loads(done.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return {"status": "FAILED", "message": "The viewer package took too long to build."}
    except Exception as exc:  # worker missing, crashed, or printed nothing
        return {"status": "FAILED", "message": "Viewer worker failed: %s" % type(exc).__name__}


def open_url(url):
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass


class ViewerButton:
    """Adds the button to *parent* of an IFC to Excel App (uses app.selected/app.status/app.root/app.tree)."""

    def __init__(self, app, parent, opener=None):
        from tkinter import ttk
        self.app = app
        self.opener = opener or open_url
        self.thread = None
        self.button = ttk.Button(parent, text="Open in viewer", command=self.click, state="disabled")
        self.button.pack(side="left", padx=(4, 0))
        app.tree.bind("<<TreeviewSelect>>", lambda event: self.refresh(), add="+")

    def refresh(self):
        result = self.app.selected()
        ok = bool(result and result.get("source") and viewer_index() is not None)
        self.button.configure(state="normal" if ok else "disabled")

    def click(self):
        result = self.app.selected()
        index = viewer_index()
        if not result or not result.get("source") or index is None:
            self.app.status.set("Viewer not available" if index is None else "Select a file")
            return None
        target = package_folder(result)
        package = target / "package.js"
        if package.is_file():
            return self.show(index, package)
        if self.thread is not None and self.thread.is_alive():
            self.app.status.set("Viewer package is being prepared")
            return None
        self.app.status.set("Preparing viewer for %s…" % Path(result["source"]).name)
        self.thread = threading.Thread(target=self._work, args=(result["source"], target, index), daemon=True)
        self.thread.start()
        return self.thread

    def _work(self, source, target, index):
        line = build(source, target)
        try:
            self.app.root.after(0, lambda: self._done(line, index))
        except Exception:
            pass

    def _done(self, line, index):
        package = Path(line.get("package", "")) if line.get("package") else None
        if line.get("status") == "VIEWER_PACKAGE_READY" and package and package.is_file():
            self.show(index, package)
        else:
            self.app.status.set("Viewer failed: %s" % (line.get("message") or line.get("status")))

    def show(self, index, package):
        url = viewer_url(index, package)
        self.app.set_status("viewer_opened_browser")
        self.opener(url)
        return url
