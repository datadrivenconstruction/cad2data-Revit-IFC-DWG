"""Support prompt cadence and shared state (DESIGN_SPEC "Support prompt"). No Tk, never raises, fails closed.

State file (shared by all DDC apps): %APPDATA%/DataDrivenConstruction/prompt_state.json
"""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path

N_CONVERSIONS = 5
MIN_AGE_DAYS = 7
MIN_ACTIVE_DAYS = 3
BACKOFF_DAYS = (7, 14, 30, 60)
QUIET_DAYS = 3
MAX_BYTES = 64 * 1024
STAR_URL = "https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG"
SHARE_TEXT = {"en": "DDC converters: free Revit, IFC and DWG converters for construction data. No registration.",
              "de": "DDC-Konverter: kostenlose Revit-, IFC- und DWG-Konverter für Bauwesen-Daten. Ohne Registrierung.",
              "ru": "Конвертеры DDC: бесплатные конвертеры Revit, IFC и DWG для строительных данных. Без регистрации."}


def default_path():
    forced = os.environ.get("DDC_PROMPT_STATE")
    if forced:
        return Path(forced)
    base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(base) / "DataDrivenConstruction" / "prompt_state.json"


def _iso(moment):
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse(text):
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def share_url(language="en"):
    from urllib.parse import quote
    return {"linkedin": "https://www.linkedin.com/sharing/share-offsite/?url=" + quote(STAR_URL, safe=""),
            "x": "https://twitter.com/intent/tweet?text=" + quote(SHARE_TEXT.get(language, SHARE_TEXT["en"]), safe="")
                 + "&url=" + quote(STAR_URL, safe="")}


class PromptState:
    def __init__(self, app_id, path=None, clock=None):
        self.app_id = app_id
        self.path = Path(path) if path else default_path()
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.writable = True

    # -- storage
    def _read(self):
        """Dict or None when the file is damaged (it is then left untouched until the next write)."""
        try:
            if not self.path.exists():
                return {}
            if self.path.stat().st_size > MAX_BYTES:
                return None
            data = json.loads(self.path.read_text(encoding="utf-8-sig"))
            return data if isinstance(data, dict) else None
        except (OSError, ValueError):
            return None

    def data(self):
        """Merged view with defaults; wrong-typed fields fall back."""
        raw = self._read() or {}
        days = raw.get("activeDays")
        apps = raw.get("apps") if isinstance(raw.get("apps"), dict) else {}
        return {
            **raw,
            "firstSeenAt": raw.get("firstSeenAt") if _parse(raw.get("firstSeenAt")) else None,
            "activeDays": [d for d in days if isinstance(d, str)] if isinstance(days, list) else [],
            "lastShownAt": raw.get("lastShownAt") if _parse(raw.get("lastShownAt")) else None,
            "declineCount": raw.get("declineCount") if isinstance(raw.get("declineCount"), int) and raw["declineCount"] >= 0 else 0,
            "status": "stopped" if raw.get("status") == "stopped" else "active",
            "apps": {k: v for k, v in apps.items() if isinstance(k, str) and isinstance(v, dict)},
        }

    def _write(self, mutate):
        current = self._read()
        if current is None:  # damaged file: defaults apply, the file is left untouched, the prompt stays silent
            self.writable = False
            return self.data()
        view = self.data()
        merged = {**current, **{k: view[k] for k in ("firstSeenAt", "activeDays", "lastShownAt", "declineCount", "status", "apps")}}
        merged.setdefault("version", 1)
        mutate(merged)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_name(self.path.name + ".tmp")
            temporary.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(temporary, self.path)
            self.writable = True
        except OSError:
            self.writable = False  # fail closed: the prompt stays silent
        return merged

    # -- events
    def touch_day(self):
        now = self.clock()
        today = now.astimezone().strftime("%Y-%m-%d")

        def mutate(d):
            d["firstSeenAt"] = d["firstSeenAt"] or _iso(now)
            if today not in d["activeDays"]:
                d["activeDays"] = (d["activeDays"] + [today])[-30:]
        if self.data()["firstSeenAt"] is None or today not in self.data()["activeDays"]:
            self._write(mutate)

    def record_run(self, converted):
        """One successful, not cancelled run with at least one converted file counts once."""
        if converted <= 0:
            return

        def mutate(d):
            app = d["apps"].setdefault(self.app_id, {})
            app["successfulConversions"] = (app.get("successfulConversions") if isinstance(app.get("successfulConversions"), int) else 0) + 1
        self._write(mutate)

    def total_conversions(self):
        return sum(v.get("successfulConversions", 0) for v in self.data()["apps"].values()
                   if isinstance(v.get("successfulConversions", 0), int))

    def eligible(self):
        if not self.writable:
            return False
        d = self.data()
        now = self.clock()
        first = _parse(d["firstSeenAt"])
        if d["status"] == "stopped" or d["declineCount"] >= len(BACKOFF_DAYS) or first is None:
            return False
        if self.total_conversions() < N_CONVERSIONS or now - first < timedelta(days=MIN_AGE_DAYS) or len(d["activeDays"]) < MIN_ACTIVE_DAYS:
            return False
        shown = _parse(d["lastShownAt"])
        if shown is not None and (now < shown or now - shown < timedelta(days=BACKOFF_DAYS[d["declineCount"]])):
            return False
        for app in d["apps"].values():  # cross-app quiet period
            other = _parse(app.get("lastShownAt"))
            if other is not None and (now < other or now - other < timedelta(days=QUIET_DAYS)):
                return False
        return True

    def mark_shown(self):
        now = _iso(self.clock())

        def mutate(d):
            d["lastShownAt"] = now
            d["apps"].setdefault(self.app_id, {})["lastShownAt"] = now
        self._write(mutate)

    def decline(self):
        self._write(lambda d: d.__setitem__("declineCount", d["declineCount"] + 1))

    def stop(self):
        self._write(lambda d: d.__setitem__("status", "stopped"))

    def set_enabled(self, enabled):
        def mutate(d):
            d["status"] = "active" if enabled else "stopped"
            if enabled:
                d["declineCount"] = 0
        self._write(mutate)

    def enabled(self):
        return self.data()["status"] != "stopped"
