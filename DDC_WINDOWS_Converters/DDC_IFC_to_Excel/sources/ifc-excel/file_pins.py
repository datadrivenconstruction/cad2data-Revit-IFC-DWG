"""Bounded file identity/hash snapshots shared by conversion and acceptance."""
import hashlib
import os
from pathlib import Path
import stat


def _identity(info, *, with_ctime=True):
    fields = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
    return fields + (info.st_ctime_ns,) if with_ctime else fields


def pin(path, check_cancelled=lambda: None):
    check_cancelled()
    path = Path(path).resolve(strict=True)
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError('Expected a regular file while hashing: ' + str(path))
    digest = hashlib.sha256()
    total = 0
    with path.open('rb') as stream:
        descriptor_before = os.fstat(stream.fileno())
        # On Windows path.stat and fstat may expose different ctime semantics.
        # Compare ctime only within the same API, retaining it for change checks.
        if _identity(descriptor_before, with_ctime=False) != _identity(before, with_ctime=False):
            raise RuntimeError('File changed before hashing: ' + str(path))
        while True:
            check_cancelled()
            # One extra byte detects growth without chasing an expanding EOF.
            chunk = stream.read(min(1024 * 1024, before.st_size - total + 1))
            if not chunk:
                break
            total += len(chunk)
            if total > before.st_size:
                raise RuntimeError('File grew while hashing: ' + str(path))
            digest.update(chunk)
        if total != before.st_size or _identity(os.fstat(stream.fileno())) != _identity(descriptor_before):
            raise RuntimeError('File changed or was truncated while hashing: ' + str(path))
    check_cancelled()
    if _identity(path.stat()) != _identity(before):
        raise RuntimeError('File changed while hashing: ' + str(path))
    return dict(path=str(path), bytes=total, sha256=digest.hexdigest())
