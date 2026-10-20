"""Path helpers: Windows long paths (> 259 characters), UNC shares, non-ASCII and spaced names.

``fs(path)`` returns a string that is safe to pass to ``open()``/``os`` calls. On Windows an absolute path that
is close to the legacy MAX_PATH limit gets the extended-length prefix (drive paths and UNC shares).
On other systems, and for short paths, it is returned unchanged.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

LIMIT = 240          # leave room for file names the OS appends (temporary files, ".old-..." suffixes)
_BS = chr(92)
_EXT = _BS * 2 + "?" + _BS            # the extended-length prefix: two backslashes, '?', backslash
_UNC = _EXT + "UNC" + _BS


def fs(path: Union[str, "os.PathLike[str]"], force: bool = False, _windows: Optional[bool] = None) -> str:
    s = os.fspath(path)
    win = (os.name == "nt") if _windows is None else _windows
    if not win or s.startswith(_EXT):
        return s
    if len(s) < LIMIT and not force:
        return s
    if _windows is None:
        s = os.path.abspath(s)
    s = s.replace("/", _BS)
    if s.startswith(_BS * 2):
        return _UNC + s[2:]
    if len(s) > 1 and s[1] == ":":
        return _EXT + s
    return s


def ensure_parent(path: Union[str, "os.PathLike[str]"]) -> Path:
    """Create the parent folder of an output file and return the path."""
    p = Path(path)
    Path(fs(p.parent)).mkdir(parents=True, exist_ok=True)
    return p
