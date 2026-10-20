"""Serial subprocess controller. No Tk dependencies; owns only its child process."""
from __future__ import annotations
import errno
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import uuid
import zipfile
import file_pins


class _Cancelled(Exception):
    pass


MAX_RECEIPT_BYTES = 4 * 1024 * 1024
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_DIAGNOSTIC_BYTES = 1024 * 1024


def collect_output(process, cancel_event):
    """Collect both binary pipes concurrently, enforcing budgets during reads."""
    outputs = {"stdout": bytearray(), "stderr": bytearray()}
    failures = []
    failure_lock = threading.Lock()
    finished = {name: threading.Event() for name in outputs}

    def read(name, stream, limit):
        try:
            while True:
                # At most one sentinel byte beyond the budget is ever retained.
                chunk = stream.read1(min(65536, limit - len(outputs[name]) + 1))
                if not chunk:
                    return
                outputs[name].extend(chunk)
                if len(outputs[name]) > limit:
                    raise ValueError(f"Converter {name} exceeds the {limit}-byte protocol size limit")
        except Exception as exc:
            with failure_lock:
                failures.append(exc)
        finally:
            try:
                stream.close()
            except Exception as exc:
                with failure_lock:
                    failures.append(exc)
            finally:
                finished[name].set()

    threads = [threading.Thread(target=read, args=(name, stream, limit), daemon=True)
               for name, stream, limit in (("stdout", process.stdout, MAX_RESPONSE_BYTES),
                                           ("stderr", process.stderr, MAX_DIAGNOSTIC_BYTES))]
    try:
        for thread in threads:
            thread.start()
        exited_at = None
        while True:
            if cancel_event.is_set():
                raise _Cancelled("Conversion cancelled during subprocess output collection")
            with failure_lock:
                if failures:
                    raise failures[0]
            if process.poll() is not None:
                if all(event.is_set() for event in finished.values()):
                    # Inspect failures once more: a final read may have failed
                    # after the earlier check but before signalling completion.
                    with failure_lock:
                        if failures:
                            raise failures[0]
                    break
                if exited_at is None:
                    exited_at = time.monotonic()
                elif time.monotonic() - exited_at > 5:
                    raise RuntimeError("Converter output pipes did not close after exit")
            cancel_event.wait(.05)
        return tuple(outputs[name].decode("utf-8", errors="replace") for name in ("stdout", "stderr"))
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        # Own converter has no descendants holding these pipes. Daemon readers
        # avoid blocking shutdown if a faulty configured wrapper violates that.
        for thread, stream in zip(threads, (process.stdout, process.stderr)):
            if thread.ident is not None:
                thread.join(timeout=1)
            else:
                stream.close()


def json_object(raw, limit=MAX_RECEIPT_BYTES):
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if len(raw) > limit:
        raise ValueError("Converter JSON exceeds the protocol size limit")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate converter JSON key: " + key)
            result[key] = value
        return result
    def finite(number):
        value = float(number)
        if not math.isfinite(value):
            raise ValueError("Non-finite converter JSON number")
        return value
    def invalid_constant(number):
        raise ValueError("Invalid converter JSON constant: " + number)
    result = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=pairs,
                        parse_float=finite, parse_constant=invalid_constant)
    if not isinstance(result, dict):
        raise ValueError("Converter JSON must be an object")
    return result


SUPPORTED_SUFFIXES = (".ifc", ".ifczip")
MIN_FREE_BYTES = 64 * 1024 * 1024
_DISK_FULL = {errno.ENOSPC, getattr(errno, "EDQUOT", -1)}
_WINDOWS_DISK_FULL = {39, 112}  # ERROR_HANDLE_DISK_FULL, ERROR_DISK_FULL
_WINDOWS_LOCKED = {32, 33}  # ERROR_SHARING_VIOLATION, ERROR_LOCK_VIOLATION


def friendly_error(kind, detail, *, winerror=None, code=None):
    """One plain sentence for the user, followed by the technical detail (never a traceback)."""
    detail = " ".join(str(detail or "").split())[:1500]
    text = detail.lower()
    if code in _DISK_FULL or winerror in _WINDOWS_DISK_FULL or "no space left" in text or "disk is full" in text             or "not enough space" in text or "temporary-disk budget" in text:
        lead = "Not enough free disk space. Free some space or choose another output folder."
    elif winerror is not None and 357 <= winerror <= 410:  # ERROR_CLOUD_FILE_* (OneDrive placeholders)
        lead = "The file is in OneDrive and is not available offline. Open OneDrive or choose 'Always keep on this device'."
    elif winerror in (51, 53, 59, 64, 67, 1231) or code in (errno.ETIMEDOUT, errno.EHOSTUNREACH) \
            or kind in ("TimeoutError", "ConnectionError"):
        lead = "The network location did not respond. Check the connection or copy the file locally."
    elif winerror in _WINDOWS_LOCKED or "being used by another process" in text:
        lead = "A file is in use by another program (for example Excel). Close it and try again."
    elif kind == "PermissionError" or code == errno.EACCES or "access is denied" in text or "permission denied" in text:
        lead = "Access denied. Check that the output folder is writable and the file is not read-only."
    elif kind == "FileNotFoundError" or code == errno.ENOENT:
        lead = "The file or folder was not found. It may have been moved, renamed or be offline."
    elif kind in ("BadZipFile", "BadZipfile") or "not a zip file" in text:
        lead = "The IFCZIP archive is damaged or is not a ZIP file."
    elif "step physical-file header" in text or "step" in text and "syntax" in text:
        lead = "The file is not a readable IFC model (damaged, truncated or another format)."
    elif kind == "MemoryError" or "memory" in text:
        lead = "Not enough memory to convert this model."
    elif kind == "TimeoutError" or kind == "ConnectionError" or code in (errno.ETIMEDOUT, errno.EHOSTUNREACH):
        lead = "The network location did not respond. Check the connection or copy the file locally."
    else:
        lead = "The file could not be converted."
    return f"{lead} Details: {kind}: {detail}" if detail else f"{lead} ({kind})"


def friendly_exception(exc):
    return friendly_error(type(exc).__name__, exc.strerror if isinstance(exc, OSError) and exc.strerror and not exc.filename else str(exc),
                          winerror=getattr(exc, "winerror", None), code=getattr(exc, "errno", None))


MAX_PATH = 260


def long_paths_enabled():
    """Windows refuses paths >= 260 characters unless LongPathsEnabled is set."""
    if os.name != "nt":
        return True
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\FileSystem") as key:
            return winreg.QueryValueEx(key, "LongPathsEnabled")[0] == 1
    except OSError:
        return False


def path_too_long(path, reserve=0):
    return len(os.path.abspath(str(path))) + reserve >= MAX_PATH and not long_paths_enabled()


LONG_PATH_MESSAGE = ("The path is longer than Windows allows (260 characters) and long paths are not enabled. "
                     "Move the file or output folder to a shorter path, for example C:\\IFC.")


def preflight_source(source):
    """Cheap checks before a subprocess is started; returns a user message or None."""
    path = Path(source)
    if path_too_long(path):
        return LONG_PATH_MESSAGE
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        return f"Unsupported file type '{path.suffix or '(none)'}'. Only .ifc and .ifczip files can be converted."
    try:
        size = path.stat().st_size
    except OSError as exc:
        return friendly_exception(exc)
    if not path.is_file():
        return "This is not a file. Only .ifc and .ifczip files can be converted."
    if size == 0:
        return "The file is empty (0 bytes). Re-export the model and try again."
    return None


def check_output_folder(output):
    """Create the output folder and prove it is writable; returns a user message or None."""
    if not str(output or "").strip():
        return "Choose an output folder."
    # Job folders add about 80 characters (session, job and artifact names).
    if path_too_long(output, reserve=80):
        return LONG_PATH_MESSAGE
    try:
        folder = Path(output)
        folder.mkdir(parents=True, exist_ok=True)
        probe = folder / (".ddc-write-test-" + uuid.uuid4().hex)
        with open(probe, "wb") as handle:
            handle.write(b"0")
        os.remove(probe)
        free = shutil.disk_usage(folder).free
    except OSError as exc:
        return friendly_exception(exc)
    if free < MIN_FREE_BYTES:
        return friendly_error("OSError", f"only {free // (1024 * 1024)} MB free in {output}", code=errno.ENOSPC)
    return None


def converter_failure(errors, stderr, returncode, status):
    """Converter JSON errors -> friendly text, keeping the converter's own words."""
    if isinstance(errors, list) and errors and all(isinstance(e, dict) for e in errors):
        first = errors[0]
        text = friendly_error(str(first.get("type") or "Error"), first.get("message") or "")
        if len(errors) > 1:
            text += f" (+{len(errors) - 1} more)"
        return text
    if errors:
        return friendly_error("Error", json.dumps(errors, ensure_ascii=False))
    return friendly_error("ConverterError", stderr.strip()[-4000:] or f"exit {returncode}, status {status!r}")


def discard_session(session):
    """Remove an unaccepted session folder so no partial output remains."""
    if session is None:
        return
    for attempt in range(5):
        shutil.rmtree(session, ignore_errors=True)
        if not os.path.exists(session):
            return
        time.sleep(0.1 * (attempt + 1))  # A just-killed child may still hold handles briefly.


def pin(path, cancel_event=None):
    def check_cancelled():
        if cancel_event is not None and cancel_event.is_set():
            raise _Cancelled("Cancellation requested during file validation")
    return file_pins.pin(path, check_cancelled)


class BatchRunner:
    def __init__(self, notify, converter=None, python=None, on_accepted=None, worker_command=None):
        self.notify = notify
        self.converter = Path(converter or Path(__file__).with_name("converter.py")).resolve()
        self.python = python or sys.executable
        self.cancelled = threading.Event()
        self.on_accepted = on_accepted
        # Explicit development bootstrap hook; ordinary/portable callers retain
        # their existing launcher contract. Never infer this from environment.
        self.worker_command = worker_command

    def cancel(self):
        self.cancelled.set()

    def run(self, sources, output):
        results = []
        try:
            for index, source in enumerate(sources):
                source = str(source)
                if self.cancelled.is_set():
                    result = {"source": source, "status": "NOT_STARTED", "message": "Batch cancelled before this file"}
                else:
                    self.notify({"event": "started", "index": index, "source": source})
                    # ``output`` may be a callable (source -> folder) for "next to the input file".
                    result = self._one(source, output(source) if callable(output) else output)
                if result["status"] == "CONVERTED_WITH_LIMITS" and self.on_accepted is not None:
                    try:
                        result["community"] = self.on_accepted(result)
                    except Exception as exc:
                        # Edition/presentation infrastructure must not invalidate a verified output.
                        result["community"] = {"edition": "community", "ad_pending": False,
                                               "warning": "Licence and Community counter unavailable (" + type(exc).__name__ + "). Running as Community; the workbook is kept."}
                result["index"] = index
                results.append(result)
                self.notify({"event": "result", **result})
        finally:
            self.notify({"event": "finished", "results": results, "cancel_requested": self.cancelled.is_set()})
        return results

    def _one(self, source, output):
        result = {"source": source, "status": "FAILED", "message": ""}
        process = None
        session = None
        try:
            problem = preflight_source(source)
            if problem:
                result["message"] = problem
                return result
            source = str(Path(source).resolve())
            result["source"] = source
            checked_pin = lambda path: pin(path, self.cancelled)
            out = Path(output).resolve()
            out.mkdir(parents=True, exist_ok=True)
            session = out / ("session-" + uuid.uuid4().hex)
            session.mkdir()
            source_pin = checked_pin(source)
            converter_pin = checked_pin(self.converter)
            module_paths = [self.converter.with_name(name) for name in ("semantics.py", "file_pins.py", "geometry_table.py", "xlsx_writer.py")]
            expected_modules = [checked_pin(path) for path in module_paths if path.is_file()]
            if self.converter.with_name("core_runtime.py").is_file():
                import core_runtime  # simplified mode: schema-free own reader
                expected_modules.extend(checked_pin(path) for path in core_runtime.source_paths())
            command = ([str(self.python), "-X", "utf8", "-B", str(self.converter), source, "--output", str(session)]
                       if self.worker_command is None else
                       self.worker_command(self.python, self.converter, source, session))
            process = subprocess.Popen(command,
                                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            stdout, stderr = collect_output(process, self.cancelled)
            if self.cancelled.is_set():
                result.update(status="CANCELLED", message="Cancelled; no partial files were kept.")
                return result
            try:
                message = json_object(stdout, MAX_RESPONSE_BYTES)
            except json.JSONDecodeError as exc:
                diagnostic = stderr.strip()[-4000:] or stdout.strip()[-1000:] or "No diagnostic output"
                raise RuntimeError(f"Converter returned no valid JSON (exit {process.returncode}): {diagnostic}") from exc
            if not isinstance(message, dict):
                raise ValueError("Converter response must be a JSON object")
            if process.returncode != 0 or message.get("status") != "CONVERTED_WITH_LIMITS":
                result["message"] = converter_failure(message.get("errors"), stderr, process.returncode, message.get("status"))
                return result
            folder = Path(message["folder"]).resolve()
            folder.relative_to(session)
            if folder == session:
                raise ValueError("Converter must return a fresh child job directory")
            with (folder / "result.json").open("rb") as stream:
                receipt = json_object(stream.read(MAX_RECEIPT_BYTES + 1))
            workbook = Path(message["data"]).resolve()
            workbook.relative_to(folder)
            if receipt.get("status") != "CONVERTED_WITH_LIMITS" or receipt.get("schema") != "ddc_ifc_excel/1":
                raise ValueError("Missing or invalid conversion receipt")
            if receipt.get("errors") != [] or message.get("errors", []) != []:
                raise ValueError("Successful conversion must not contain errors")
            if not isinstance(receipt.get("limitations"), list) or any(not isinstance(v, str) for v in receipt["limitations"]):
                raise ValueError("Receipt limitations must be a list of strings")
            if receipt.get("source") != source_pin or checked_pin(source) != source_pin or Path(receipt["data"]).resolve() != workbook:
                raise ValueError("Receipt input/output binding mismatch")
            if receipt.get("converter") != converter_pin or checked_pin(self.converter) != converter_pin:
                raise ValueError("Converter binding mismatch")
            if receipt.get("modules") != expected_modules or [checked_pin(p["path"]) for p in expected_modules] != expected_modules:
                raise ValueError("Converter module binding mismatch")
            artifacts = receipt.get("artifacts", [])
            if not isinstance(artifacts, list) or not 1 <= len(artifacts) <= 2:
                raise ValueError("Incomplete artifact manifest")
            actual_names = []
            for artifact in artifacts:
                artifact_path = Path(artifact["path"]).resolve()
                if artifact_path.parent != folder or artifact != checked_pin(artifact_path):
                    raise ValueError("Artifact binding/hash mismatch")
                actual_names.append(artifact_path.name)
            # <stem>.xlsx first; optional sidecar: data.jsonl (raw tables) or overflow.jsonl.
            if (Path(artifacts[0]["path"]).resolve() != workbook or workbook.parent != folder
                    or any(name not in ("data.jsonl", "overflow.jsonl") for name in actual_names[1:])):
                raise ValueError("Unexpected artifact manifest")
            if not workbook.is_file() or workbook.suffix.lower() != ".xlsx":
                raise ValueError("Workbook missing")
            with zipfile.ZipFile(workbook) as package:
                if not {"[Content_Types].xml", "xl/workbook.xml"}.issubset(package.namelist()) or package.testzip() is not None:
                    raise ValueError("Invalid XLSX package")
            if self.cancelled.is_set():
                raise _Cancelled("Cancellation requested before result acceptance")
            result.update(status="CONVERTED_WITH_LIMITS", folder=str(folder), workbook=str(workbook),
                          message="Written with limits. See result.json; full fidelity is not qualified.",
                          limitations=receipt.get("limitations", []))
        except _Cancelled as exc:
            result.update(status="CANCELLED", message="Cancelled; no partial files were kept.")
        except OSError as exc:
            result["message"] = friendly_exception(exc)
        except Exception as exc:
            result["message"] = f"{type(exc).__name__}: {exc}"
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            if result["status"] == "CANCELLED":
                discard_session(session)
        return result
