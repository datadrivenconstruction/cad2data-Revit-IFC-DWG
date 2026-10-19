"""Durable Community conversion counting and advertising-event outbox.

This module never opens a browser or makes a network request. Product adapters
must call it only after their own result has been accepted, and must isolate
errors from conversion output handling. ``ad_free`` is caller-supplied state,
not a security boundary: production adapters must derive it from a validated
paid entitlement, never from a user-controlled CLI switch.

``scope="product"`` (the default) keeps a separate counter for each product;
``scope="suite"`` counts Community completions across all products. Every
second accepted, non-ad-free completion adds one outbox event in the same
SQLite transaction as the counter increment and operation-id deduplication.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import secrets
import sqlite3
import time
from typing import Any


PRODUCT_IDS = frozenset({
    "rvt-converter",
    "revit-ifc",
    "dwg-excel",
    "ifc-excel",
    "excel-addin",
})
SCOPES = frozenset({"product", "suite"})
_SCHEMA_VERSION = 1
_DATABASE_BUSY_TIMEOUT_MS = 5000


def default_database_path() -> Path:
    """Return the per-user state DB path without collecting machine identity."""
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        base = Path(root) if root else Path.home() / "AppData" / "Local"
        return base / "DataDrivenConstruction" / "DDC" / "editions" / "community.sqlite"
    root = os.environ.get("XDG_STATE_HOME")
    base = Path(root) if root else Path.home() / ".local" / "state"
    return base / "ddc-licensing" / "community.sqlite3"


def _resolve_db(db_path: os.PathLike[str] | str | None) -> Path:
    path = Path(db_path) if db_path is not None else default_database_path()
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect(db_path: os.PathLike[str] | str | None) -> sqlite3.Connection:
    path = _resolve_db(db_path)
    # Keep an accounting hiccup from holding a converter's serial batch worker
    # for tens of seconds. The product adapter can warn and continue producing
    # output if this bounded accounting attempt still cannot acquire the DB.
    connection = sqlite3.connect(
        str(path), timeout=_DATABASE_BUSY_TIMEOUT_MS / 1000, isolation_level=None
    )
    try:
        connection.row_factory = sqlite3.Row
        connection.execute(f"PRAGMA busy_timeout={_DATABASE_BUSY_TIMEOUT_MS}")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA synchronous=FULL")
        # WAL lets readers list the outbox while another process records a result.
        # SQLite's busy_timeout does not reliably wait for concurrent journal-mode
        # transitions on first open, so retry that one setup pragma explicitly.
        deadline = time.monotonic() + _DATABASE_BUSY_TIMEOUT_MS / 1000
        while True:
            try:
                connection.execute("PRAGMA journal_mode=WAL")
                break
            except sqlite3.OperationalError as error:
                if "locked" not in str(error).lower() or time.monotonic() >= deadline:
                    raise
                time.sleep(0.02)
        _initialize(connection)
    except Exception:
        connection.close()
        raise
    return connection


def _initialize(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS counters (
            scope_key TEXT PRIMARY KEY,
            completed_count INTEGER NOT NULL CHECK (completed_count >= 0)
        );
        CREATE TABLE IF NOT EXISTS operations (
            operation_id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            scope_key TEXT NOT NULL,
            counted INTEGER NOT NULL CHECK (counted IN (0, 1)),
            recorded_utc TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS outbox (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scope_key TEXT NOT NULL,
            threshold_index INTEGER NOT NULL CHECK (threshold_index > 0),
            product_id TEXT NOT NULL,
            operation_id TEXT NOT NULL,
            created_utc TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'claimed', 'attempted')),
            attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
            lease_token TEXT,
            lease_until REAL,
            last_error_code TEXT,
            attempted_utc TEXT,
            UNIQUE (scope_key, threshold_index)
        );
        CREATE INDEX IF NOT EXISTS outbox_pending_idx
            ON outbox(status, lease_until, event_id);
        CREATE INDEX IF NOT EXISTS outbox_scope_pending_idx
            ON outbox(scope_key, event_id) WHERE status!='attempted';
        """
    )
    connection.execute(
        "INSERT OR IGNORE INTO metadata(key, value) VALUES('schema_version', ?)",
        (str(_SCHEMA_VERSION),),
    )
    row = connection.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
    if row["value"] != str(_SCHEMA_VERSION):
        raise RuntimeError(f"Unsupported Community DB schema version: {row['value']}")


def _validate(product_id: str, operation_id: str, scope: str) -> None:
    if not isinstance(product_id, str):
        raise ValueError("product_id must be a string")
    if product_id not in PRODUCT_IDS:
        raise ValueError(f"Unknown DDC product_id: {product_id!r}")
    if not isinstance(operation_id, str) or not operation_id or len(operation_id) > 512:
        raise ValueError("operation_id must be a non-empty string of at most 512 characters")
    if "\x00" in operation_id:
        raise ValueError("operation_id must not contain NUL")
    if not isinstance(scope, str) or scope not in SCOPES:
        raise ValueError("scope must be 'product' or 'suite'")


def _scope_key(product_id: str, scope: str) -> str:
    return product_id if scope == "product" else "suite"


def record_completed(
    product_id: str,
    operation_id: str,
    *,
    accepted: bool = True,
    ad_free: bool = False,
    db_path: os.PathLike[str] | str | None = None,
    scope: str = "product",
) -> dict[str, Any]:
    """Record one terminal conversion result exactly once across processes.

    ``accepted=False`` covers failed/cancelled/unaccepted output and writes no
    record. Accepted ``ad_free=True`` operations are deduplicated but do not
    increment Community counters or enqueue events. In production, callers
    must derive ``ad_free`` from locally verified signed entitlement; the
    argument itself is not trusted. A global operation-id primary key prevents
    nested GUI, bridge and backend callbacks from counting one job twice.

    Returns a small receipt dictionary with ``counted``, ``duplicate``, the
    resulting count, and optional ``event_id``. Storage errors are raised; a
    converter adapter must catch/report them separately and never rewrite or
    discard an otherwise accepted conversion result because accounting failed.
    """
    _validate(product_id, operation_id, scope)
    if not isinstance(accepted, bool) or not isinstance(ad_free, bool):
        raise ValueError("accepted and ad_free must be booleans")
    if not accepted:
        return {"recorded": False, "counted": False, "duplicate": False, "reason": "not_accepted"}

    key = _scope_key(product_id, scope)
    now = datetime.now(timezone.utc).isoformat()
    connection = _connect(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        configured_scope = connection.execute(
            "SELECT value FROM metadata WHERE key='accounting_scope'"
        ).fetchone()
        if configured_scope is None:
            connection.execute(
                "INSERT INTO metadata(key, value) VALUES('accounting_scope', ?)", (scope,)
            )
        elif configured_scope["value"] != scope:
            raise ValueError(
                "This Community database is already configured for "
                f"scope={configured_scope['value']!r}; use a new database to change scope"
            )
        existing = connection.execute(
            "SELECT product_id, scope_key, counted FROM operations WHERE operation_id=?",
            (operation_id,),
        ).fetchone()
        if existing is not None:
            connection.commit()
            return {
                "recorded": True,
                "counted": bool(existing["counted"]),
                "duplicate": True,
                "product_id": existing["product_id"],
                "scope": existing["scope_key"],
                "count": _read_count(connection, existing["scope_key"]),
                "event_id": None,
            }

        counted = not ad_free
        event_id: int | None = None
        if counted:
            connection.execute(
                "INSERT INTO counters(scope_key, completed_count) VALUES(?, 0) "
                "ON CONFLICT(scope_key) DO NOTHING",
                (key,),
            )
            connection.execute(
                "UPDATE counters SET completed_count=completed_count+1 WHERE scope_key=?",
                (key,),
            )
            count = _read_count(connection, key)
            if count % 2 == 0:
                cursor = connection.execute(
                    "INSERT INTO outbox(scope_key, threshold_index, product_id, operation_id, created_utc) "
                    "VALUES(?, ?, ?, ?, ?)",
                    (key, count // 2, product_id, operation_id, now),
                )
                event_id = int(cursor.lastrowid)
        else:
            count = _read_count(connection, key)

        connection.execute(
            "INSERT INTO operations(operation_id, product_id, scope_key, counted, recorded_utc) "
            "VALUES(?, ?, ?, ?, ?)",
            (operation_id, product_id, key, int(counted), now),
        )
        connection.commit()
        return {
            "recorded": True,
            "counted": counted,
            "duplicate": False,
            "product_id": product_id,
            "scope": key,
            "count": count,
            "event_id": event_id,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _read_count(connection: sqlite3.Connection, key: str) -> int:
    row = connection.execute(
        "SELECT completed_count FROM counters WHERE scope_key=?", (key,)
    ).fetchone()
    return int(row["completed_count"]) if row else 0


def list_pending(
    *,
    scope: str = "product",
    product_id: str | None = None,
    db_path: os.PathLike[str] | str | None = None,
) -> list[dict[str, Any]]:
    """List unattempted outbox entries for one product or suite scope.

    For ``scope="product"``, ``product_id`` is required. For ``scope="suite"``
    it must be omitted. Claimed-but-not-yet-attempted entries are included so
    callers can observe work held under a lease; use :func:`claim_pending` to
    safely acquire or reacquire an event.
    """
    if not isinstance(scope, str) or scope not in SCOPES:
        raise ValueError("scope must be 'product' or 'suite'")
    if scope == "product":
        if product_id not in PRODUCT_IDS:
            raise ValueError("product_id is required and must be a supported product for product scope")
        key = product_id
    else:
        if product_id is not None:
            raise ValueError("product_id must be omitted for suite scope")
        key = "suite"
    connection = _connect(db_path)
    try:
        rows = connection.execute(
            "SELECT event_id, scope_key, threshold_index, product_id, operation_id, created_utc, "
            "status, attempts, lease_until, last_error_code, attempted_utc FROM outbox "
            "WHERE scope_key=? AND status!='attempted' ORDER BY event_id",
            (key,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def has_pending(*, scope: str = "product", product_id: str | None = None,
                db_path: os.PathLike[str] | str | None = None) -> bool:
    """Bounded lookup for UI notifications, without loading the whole outbox."""
    key = _pending_scope_key(scope, product_id)
    connection = _connect(db_path)
    try:
        return connection.execute(
            "SELECT 1 FROM outbox WHERE scope_key=? AND status!='attempted' LIMIT 1",
            (key,),
        ).fetchone() is not None
    finally:
        connection.close()


def claim_pending(
    *,
    scope: str = "product",
    product_id: str | None = None,
    lease_seconds: int = 60,
    db_path: os.PathLike[str] | str | None = None,
) -> dict[str, Any] | None:
    """Atomically lease the oldest available outbox event to one caller.

    A crashed caller's lease becomes claimable after expiry. This deliberately
    provides at-least-once launch-attempt handling: a crash after an external
    browser was opened but before acknowledgment may lead to a retry. The
    module itself has no browser or network side effects.
    """
    key = _pending_scope_key(scope, product_id)
    if type(lease_seconds) is not int or not 1 <= lease_seconds <= 3600:
        raise ValueError("lease_seconds must be an integer from 1 to 3600")
    token = secrets.token_urlsafe(24)
    connection = _connect(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        # Setup and writer-lock acquisition can wait longer than a short lease.
        # Start the lease only after owning the transaction, otherwise another
        # process can immediately reclaim a lease we have just returned.
        now = time.time()
        row = connection.execute(
            "SELECT event_id FROM outbox WHERE scope_key=? AND "
            "(status='pending' OR (status='claimed' AND lease_until<=?)) "
            "ORDER BY event_id LIMIT 1",
            (key, now),
        ).fetchone()
        if row is None:
            connection.commit()
            return None
        event_id = int(row["event_id"])
        connection.execute(
            "UPDATE outbox SET status='claimed', attempts=attempts+1, lease_token=?, lease_until=? "
            "WHERE event_id=?",
            (token, now + lease_seconds, event_id),
        )
        claimed = connection.execute(
            "SELECT event_id, scope_key, threshold_index, product_id, operation_id, created_utc, "
            "status, attempts, lease_until, lease_token, last_error_code FROM outbox WHERE event_id=?",
            (event_id,),
        ).fetchone()
        connection.commit()
        return dict(claimed)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _pending_scope_key(scope: str, product_id: str | None) -> str:
    if not isinstance(scope, str) or scope not in SCOPES:
        raise ValueError("scope must be 'product' or 'suite'")
    if scope == "product":
        if product_id not in PRODUCT_IDS:
            raise ValueError("product_id is required and must be a supported product for product scope")
        return product_id
    if product_id is not None:
        raise ValueError("product_id must be omitted for suite scope")
    return "suite"


def acknowledge_launch_attempt(
    event_id: int,
    lease_token: str,
    *,
    db_path: os.PathLike[str] | str | None = None,
) -> bool:
    """Mark a claimed event as attempted if the lease token still matches.

    Call only after the adapter's launch attempt has returned. ``True`` means
    this caller acknowledged the event; it does not mean an ad was displayed.
    A stale token returns ``False`` and cannot acknowledge a newer lease.
    """
    if type(event_id) is not int or event_id < 1:
        raise ValueError("event_id must be a positive integer")
    if not isinstance(lease_token, str) or not lease_token:
        raise ValueError("lease_token must be non-empty")
    connection = _connect(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.execute(
            "UPDATE outbox SET status='attempted', attempted_utc=?, lease_token=NULL, lease_until=NULL "
            "WHERE event_id=? AND status='claimed' AND lease_token=?",
            (datetime.now(timezone.utc).isoformat(), event_id, lease_token),
        )
        connection.commit()
        return cursor.rowcount == 1
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def release_claim(
    event_id: int,
    lease_token: str,
    *,
    error_code: str | None = None,
    db_path: os.PathLike[str] | str | None = None,
) -> bool:
    """Return a claimed event to pending after a failed launch attempt.

    ``error_code`` is an optional short, non-sensitive diagnostic category
    retained with the event for support diagnostics. Never pass document paths,
    license tokens, user data, or other sensitive information. A stale lease
    token returns ``False``.
    """
    if type(event_id) is not int or event_id < 1:
        raise ValueError("event_id must be a positive integer")
    if not isinstance(lease_token, str) or not lease_token:
        raise ValueError("lease_token must be non-empty")
    if error_code is not None and (not isinstance(error_code, str) or len(error_code) > 64):
        raise ValueError("error_code must be at most 64 characters")
    connection = _connect(db_path)
    try:
        connection.execute("BEGIN IMMEDIATE")
        cursor = connection.execute(
            "UPDATE outbox SET status='pending', lease_token=NULL, lease_until=NULL, last_error_code=? "
            "WHERE event_id=? AND status='claimed' AND lease_token=?",
            (error_code, event_id, lease_token),
        )
        connection.commit()
        return cursor.rowcount == 1
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
