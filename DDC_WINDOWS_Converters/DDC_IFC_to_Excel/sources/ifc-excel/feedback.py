"""Feedback form back end: payload, offline queue, send, fallback links (DESIGN_SPEC "Feedback & support prompt").

No Tk here. Nothing is sent without the user pressing Send / Send now; files, paths, user and machine names are never attached.
"""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import platform
import re
import secrets
import urllib.error
import urllib.parse
import urllib.request


RELAY_URL = "https://openconstructionerp.com/api/inquiry"
SOURCE = "ddc-desktop-feedback"
SUPPORT_EMAIL = "info@datadrivenconstruction.io"
PRIVACY_URL = "https://cadbimconverter.com/datenschutz-impressum/"
ISSUES = "https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues/new"
CATEGORIES = ("Bug", "Conversion problem", "Idea", "Question", "Other")
ISSUE_TEMPLATES = {"Bug": "bug_report.yml", "Conversion problem": "conversion_problem.yml", "Idea": "feature_request.yml"}
MAX_FILES, MAX_BYTES, MAX_AGE_DAYS = 20, 16 * 1024, 90
MIN, MAX = 10, 4000
PATH_LIKE = re.compile(r"[A-Za-z]:\\|\\\\")


def queue_dir():
    forced = os.environ.get("DDC_FEEDBACK_QUEUE")
    if forced:
        return Path(forced)
    base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(base) / "DataDrivenConstruction" / "feedback_queue"


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def looks_like_path(text):
    return bool(PATH_LIKE.search(text or ""))


def check_message(text):
    """None when fine, else 'short' / 'long'."""
    length = len((text or "").strip())
    return "short" if length < MIN else "long" if length > MAX else None


def os_label():
    system = platform.system()
    if system == "Windows":
        build = platform.version()  # 10.0.26100
        try:
            number = int(build.split(".")[2])
        except (IndexError, ValueError):
            number = 0
        return f"Windows {'11' if number >= 22000 else '10'} ({build})"
    return f"{system} {platform.release()}".strip()


def tech_line(app_name, version, build, language):
    """Exactly these fields, nothing else."""
    return f"App: {app_name} {version} (build {build}) / {os_label()} / language {language}"


def build_payload(category, message, name, email, app_name, version, build, language, consent_at):
    block = (f"\n\n---\nCategory: {category}\nApp: {app_name} {version}\nOS: {os_label()}\nLanguage: {language}\n"
             f"Consent: yes {consent_at}")
    payload = {"name": name.strip(), "email": (email or "").strip(), "message": message.strip() + block,
               "topic": "Support", "source": SOURCE}
    return payload


def mailto(category, message, app_name, version, build, language):
    subject = f"{app_name} {version} feedback: {category}"
    body = message.strip() + "\n\n" + tech_line(app_name, version, build, language)
    url = "mailto:" + SUPPORT_EMAIL + "?" + urllib.parse.urlencode({"subject": subject, "body": body}, quote_via=urllib.parse.quote)
    return url if len(url) <= 1800 else url[:1800].rsplit("%", 1)[0]


def github_url(category, app_name, version):
    query = urllib.parse.urlencode({"app": app_name, "version": version, "os": os_label()}, quote_via=urllib.parse.quote)
    template = ISSUE_TEMPLATES.get(category)
    if template is None:
        return ISSUES + "/choose"
    return f"{ISSUES}?template={template}&{query}"


# ---------------------------------------------------------------- queue
def _files(folder=None):
    folder = Path(folder) if folder else queue_dir()
    try:
        return sorted(p for p in folder.glob("*.json") if p.is_file())
    except OSError:
        return []


def queue_full(folder=None):
    return len(_files(folder)) >= MAX_FILES


def enqueue(payload, app_id, consent_at, folder=None):
    """Store one message; returns the path, or None when the queue is full / the body is too large / disk refuses."""
    folder = Path(folder) if folder else queue_dir()
    if queue_full(folder):
        return None
    record = {**payload, "app": app_id, "queued_at": iso(utc_now()), "consent_at": consent_at}
    text = json.dumps(record, ensure_ascii=False, indent=1)
    if len(text.encode("utf-8")) > MAX_BYTES:
        return None
    try:
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / f"{utc_now().strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}.json"
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, target)
        return target
    except OSError:
        return None


def pending(app_id, folder=None, now=None):
    """[(path, record)] for this app: consent given, valid, not older than 90 days."""
    now = now or utc_now()
    found = []
    for path in _files(folder):
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            record = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(record, dict) or record.get("app") != app_id or not record.get("consent_at"):
                continue
            queued = datetime.strptime(record["queued_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if now - queued > timedelta(days=MAX_AGE_DAYS):
                continue
            found.append((path, record))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return found


def body_of(record):
    return {k: record[k] for k in ("name", "email", "message", "topic", "source") if k in record}


# ---------------------------------------------------------------- network
def post(payload, timeout=15, opener=urllib.request.urlopen):
    """('sent', None) | ('rate_limited', minutes) | ('invalid', {field,message}) | ('offline', reason). Never raises."""
    request = urllib.request.Request(RELAY_URL, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
    try:
        with opener(request, timeout=timeout) as response:
            return ("sent", None) if 200 <= response.status < 300 else ("offline", f"HTTP {response.status}")
    except urllib.error.HTTPError as error:
        try:
            data = json.loads(error.read(65536).decode("utf-8", "replace"))
        except (ValueError, OSError):
            data = {}
        if error.code == 429:
            seconds = data.get("retry_after") if isinstance(data, dict) else None
            try:
                seconds = int(seconds if seconds is not None else error.headers.get("Retry-After", 3600))
            except (TypeError, ValueError):
                seconds = 3600
            return "rate_limited", max(1, round(seconds / 60))
        if error.code == 400 and isinstance(data, dict):
            return "invalid", {"field": data.get("field"), "message": data.get("message") or data.get("error")}
        return "offline", f"HTTP {error.code}"
    except (urllib.error.URLError, OSError, ValueError) as error:
        return "offline", type(error).__name__


def resend(app_id, folder=None, opener=urllib.request.urlopen, pause=None):
    """Send queued messages one by one; a file is removed only after HTTP 2xx. Returns (sent, left)."""
    folder = Path(folder) if folder else queue_dir()
    lock = folder / ".sending"
    try:
        folder.mkdir(parents=True, exist_ok=True)
        handle = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(handle)
    except OSError:
        return 0, len(pending(app_id, folder))
    sent = 0
    try:
        for path, record in pending(app_id, folder):
            status, _ = post(body_of(record), opener=opener)
            if status != "sent":
                break
            try:
                path.unlink()
            except OSError:
                break
            sent += 1
            if pause:
                pause()
    finally:
        try:
            lock.unlink()
        except OSError:
            pass
    return sent, len(pending(app_id, folder))
