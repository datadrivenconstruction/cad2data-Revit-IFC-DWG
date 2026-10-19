"""Non-blocking registration state for desktop hosts with configured licensing.

This view controller is not an entitlement verifier. It delegates exclusively
to the injected LicenseCoordinator and never changes conversion permissions.
Without that configured dependency, full Community remains available. Importing
this module does not load crypto, contact a server or access a device key.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass, replace
from queue import Empty, Full, Queue
import re
from threading import Event, Thread, get_ident
from time import monotonic
from typing import Callable


@dataclass(frozen=True, slots=True)
class RegistrationState:
    available: bool = False
    busy: bool = False
    closed: bool = False
    paid: bool = False
    message_key: str = "service_unavailable"
    expires_at: int | None = None
    lease_until: int | None = None


def normalize_activation_code(value: object) -> str | None:
    """Accept canonical 256-bit codes; tolerate only outer ASCII paste spacing.

    Case, hyphens and underscores are meaningful. Never guess replacements,
    remove internal whitespace or include the supplied value in diagnostics.
    """
    if type(value) is not str or len(value) > 128:
        return None
    code = value.strip(" \t\r\n")
    if re.fullmatch(r"[A-Za-z0-9_-]{43}", code) is None:
        return None
    try:
        decoded = base64.urlsafe_b64decode(code + "=")
        if len(decoded) != 32 or base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii") != code:
            return None
    except (ValueError, UnicodeError):
        return None
    return code


def _background(work: Callable[[], None]) -> None:
    Thread(target=work, name="DdcLicenseRequest", daemon=True).start()


def _value(item: object) -> object:
    return getattr(item, "value", item)


_ACCESS_MESSAGES = {
    "trusted_time_unavailable": "clock_unavailable",
    "device_key_unavailable": "device_unavailable",
    "device_mismatch": "device_unavailable",
    "device_proof_failed": "device_unavailable",
    "cache_corrupt": "storage_error",
    "cache_unavailable": "storage_error",
    "entitlement_expired": "expired",
    "lease_expired": "renewal_required",
    "not_yet_valid": "clock_unavailable",
    "invalid_entitlement": "invalid_response",
    "product_mismatch": "wrong_product",
}
_SERVICE_MESSAGES = {
    "invalid_key": "invalid_input", "device_limit": "device_limit",
    "expired": "expired", "revoked": "revoked", "product_mismatch": "wrong_product",
    "not_yet_valid": "clock_unavailable", "clock_invalid": "clock_unavailable",
    "challenge_limit": "try_later", "storage_error": "service_rejected",
    "transfer_pending": "transfer_pending",
}
_STATUS_MESSAGES = {
    "invalid_input": "invalid_input", "trusted_time_unavailable": "clock_unavailable",
    "device_key_unavailable": "device_unavailable", "invalid_new_entitlement": "invalid_response",
    "cache_write_failed": "storage_error", "renewal_unavailable": "renewal_unavailable",
}
_CLIENT_MESSAGES = {
    "invalid_input": "invalid_input", "clock_unavailable": "clock_unavailable",
    "transport_failed": "network_error", "service_rejected": "service_rejected",
    "device_proof_failed": "device_unavailable", "invalid_challenge": "invalid_response",
    "invalid_response": "invalid_response", "invalid_entitlement": "invalid_response",
}


class RegistrationController:
    """Single-flight desktop state. All public methods belong to the UI thread.

    Slow coordinator calls run off the UI thread; workers only enqueue results.
    Closing discards late presentation updates, not an already submitted server
    transaction. No activation code is retained in state, logs or diagnostics.
    The production transport remains responsible for bounded network timeouts.
    """

    def __init__(self, coordinator=None, *, submit: Callable | None = None):
        self._owner = get_ident()
        self._coordinator = coordinator
        self._submit = submit or _background
        self._results = Queue(maxsize=1)
        self._closed = Event()
        self._refresh_due = monotonic() + 30
        available = coordinator is not None
        if available and (not callable(getattr(coordinator, "activate", None)) or
                          not callable(getattr(coordinator, "get_access", None)) or
                          type(getattr(coordinator, "product_id", None)) is not str):
            raise TypeError("a configured license coordinator is required")
        self._state = RegistrationState(available=available,
                                        message_key="ready" if available else "service_unavailable")

    @property
    def state(self) -> RegistrationState:
        return self._state

    def _check_thread(self):
        if get_ident() != self._owner:
            raise RuntimeError("registration state must be used on its owner thread")

    def _start(self, operation: str, work: Callable) -> bool:
        self._check_thread()
        if self._state.closed or self._state.busy or not self._state.available:
            return False
        self._state = replace(self._state, busy=True, message_key={
            "refresh": "checking", "activate": "activating", "renew": "renewing"}[operation])

        def run():
            try:
                outcome = (operation, work(), False)
            except Exception:
                # Never relay exception messages: transport errors may contain a code.
                outcome = (operation, None, True)
            if not self._closed.is_set():
                try:
                    self._results.put_nowait(outcome)
                except Full:
                    pass

        try:
            self._submit(run)
        except Exception:
            self._state = RegistrationState(available=True, message_key="operation_failed")
            return False
        return True

    def activate(self, raw_code: object) -> bool:
        self._check_thread()
        if self._state.closed or self._state.busy or not self._state.available:
            return False
        code = normalize_activation_code(raw_code)
        if code is None:
            self._state = replace(self._state, message_key="invalid_input")
            return False
        return self._start("activate", lambda: self._coordinator.activate(code))

    def refresh(self) -> bool:
        return self._start("refresh", lambda: self._coordinator.get_access(self._coordinator.product_id))

    def renew(self) -> bool:
        self._check_thread()
        if not callable(getattr(self._coordinator, "renew", None)):
            return False
        return self._start("renew", self._coordinator.renew)

    def poll(self) -> bool:
        self._check_thread()
        if self._state.closed:
            return False
        try:
            operation, result, failed = self._results.get_nowait()
        except Empty:
            # Refresh the visible Paid claim locally while the dialog remains
            # open. This never initiates a network renewal or a conversion.
            if self._state.paid and not self._state.busy and monotonic() >= self._refresh_due:
                return self.refresh()
            return False
        try:
            if failed:
                raise ValueError("operation failed")
            access = result if operation == "refresh" else result.access
            paid = access.paid is True
            expiry = lease = None
            if paid:
                expiry, lease = access.entitlement.expires_at, access.entitlement.lease_until
                if type(expiry) is not int or type(lease) is not int or not 0 < lease <= expiry:
                    raise ValueError("invalid presentation result")
            message = "paid" if paid else _ACCESS_MESSAGES.get(_value(access.reason), "community")
            if operation != "refresh":
                status = _value(result.status)
                if status == "activated":
                    message = "paid" if paid else "activation_saved_community"
                else:
                    message = _SERVICE_MESSAGES.get(_value(getattr(result, "service_error", None)))
                    message = message or _STATUS_MESSAGES.get(status)
                    message = message or _CLIENT_MESSAGES.get(_value(getattr(result, "client_error", None)))
                    message = message or "operation_failed"
            self._state = RegistrationState(available=True, paid=paid, message_key=message,
                                            expires_at=expiry, lease_until=lease)
        except Exception:
            self._state = RegistrationState(available=True, message_key="operation_failed")
        self._refresh_due = monotonic() + 30
        return True

    def close(self) -> None:
        self._check_thread()
        self._closed.set()
        self._state = replace(self._state, busy=False, closed=True, message_key="closed")
        try:
            self._results.get_nowait()
        except Empty:
            pass
