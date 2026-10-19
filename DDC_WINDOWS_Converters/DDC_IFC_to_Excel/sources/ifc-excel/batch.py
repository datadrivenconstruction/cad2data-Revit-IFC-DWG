"""Serial subprocess controller. No Tk dependencies; owns only its child process."""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
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
                    result = self._one(source, output)
                if result["status"] == "CONVERTED_WITH_LIMITS" and self.on_accepted is not None:
                    try:
                        result["community"] = self.on_accepted(result)
                    except Exception as exc:
                        # Edition/presentation infrastructure must not invalidate a verified output.
                        result["community"] = {"edition": "community", "ad_pending": False,
                                               "warning": "Community counter unavailable: " + type(exc).__name__}
                result["index"] = index
                results.append(result)
                self.notify({"event": "result", **result})
        finally:
            self.notify({"event": "finished", "results": results, "cancel_requested": self.cancelled.is_set()})
        return results

    def _one(self, source, output):
        result = {"source": source, "status": "FAILED", "message": ""}
        process = None
        try:
            source = str(Path(source).resolve())
            result["source"] = source
            checked_pin = lambda path: pin(path, self.cancelled)
            out = Path(output).resolve()
            out.mkdir(parents=True, exist_ok=True)
            session = out / ("session-" + uuid.uuid4().hex)
            session.mkdir()
            source_pin = checked_pin(source)
            converter_pin = checked_pin(self.converter)
            module_paths = [self.converter.with_name(name) for name in ("semantics.py", "file_pins.py")]
            expected_modules = [checked_pin(path) for path in module_paths if path.is_file()]
            if self.converter.with_name("ifc_runtime.py").is_file():
                import ifc_runtime
                expected_modules.extend(checked_pin(path) for path in ifc_runtime.source_paths())
            command = ([str(self.python), "-X", "utf8", "-B", str(self.converter), source, "--output", str(session)]
                       if self.worker_command is None else
                       self.worker_command(self.python, self.converter, source, session))
            process = subprocess.Popen(command,
                                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            stdout, stderr = collect_output(process, self.cancelled)
            if self.cancelled.is_set():
                result.update(status="CANCELLED", message="Cancellation requested before result acceptance")
                return result
            try:
                message = json_object(stdout, MAX_RESPONSE_BYTES)
            except json.JSONDecodeError as exc:
                diagnostic = stderr.strip()[-4000:] or stdout.strip()[-1000:] or "No diagnostic output"
                raise RuntimeError(f"Converter returned no valid JSON (exit {process.returncode}): {diagnostic}") from exc
            if not isinstance(message, dict):
                raise ValueError("Converter response must be a JSON object")
            if process.returncode != 0 or message.get("status") != "CONVERTED_WITH_LIMITS":
                errors = message.get("errors")
                result["message"] = json.dumps(errors, ensure_ascii=False) if errors else (stderr.strip()[-4000:] or f"Converter failed (exit {process.returncode}, status {message.get('status')!r})")
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
            expected_names = {"drawing.xlsx", "data.sqlite", "data.jsonl"}
            if len(artifacts) != len(expected_names):
                raise ValueError("Incomplete artifact manifest")
            actual_names = set()
            for artifact in artifacts:
                artifact_path = Path(artifact["path"]).resolve()
                if artifact_path.parent != folder or artifact != checked_pin(artifact_path):
                    raise ValueError("Artifact binding/hash mismatch")
                actual_names.add(artifact_path.name)
            if actual_names != expected_names or workbook != folder / "drawing.xlsx":
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
            result.update(status="CANCELLED", message=str(exc) + "; job files are preserved but not accepted.")
        except Exception as exc:
            result["message"] = f"{type(exc).__name__}: {exc}"
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=5)
        return result
