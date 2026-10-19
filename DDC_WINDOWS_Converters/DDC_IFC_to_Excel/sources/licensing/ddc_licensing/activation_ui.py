"""Small optional Tk registration view; the controller owns all background work.

Construct and use on the Tk owner thread. This module never opens a browser,
creates a device key, configures an issuer, or grants an edition itself.
"""
from datetime import datetime, timezone
import tkinter as tk
from tkinter import ttk

from .registration import RegistrationController


_TEXT = {
    "en": {
        "title": "DDC registration", "key": "Activation code", "show": "Show code",
        "activate": "Activate", "renew": "Refresh license", "close": "Close",
        "community_label": "Community", "paid_label": "Paid · advertising disabled",
        "policy": "Community includes all conversion features. A valid paid license removes advertising.",
        "expires": "License expires: {0} UTC",
        "service_unavailable": "Activation is not configured in this application. All Community features remain available.",
        "ready": "Enter your activation code.", "checking": "Checking license…",
        "activating": "Activating…", "renewing": "Refreshing license…",
        "paid": "Your license is active. Advertising is disabled.",
        "community": "All Community features are available.",
        "invalid_input": "Enter the complete activation code supplied with your license.",
        "network_error": "The licensing service could not be reached. Check your connection and try again.",
        "service_rejected": "The licensing service did not accept this request. Check your code or contact support.",
        "device_limit": "This license has reached its device limit. Contact support to change devices.",
        "expired": "Your license has expired. All Community features remain available.",
        "revoked": "This license is no longer valid. Contact support; Community features remain available.",
        "wrong_product": "This license does not cover this product. Check the license you purchased.",
        "clock_unavailable": "License validity could not be checked. Refresh the license when the service is available.",
        "device_unavailable": "The device license could not be verified. Try again or contact support.",
        "invalid_response": "The license response could not be verified. Try again or contact support.",
        "storage_error": "The license could not be saved on this computer. Try again or contact support.",
        "renewal_required": "Refresh the license to check whether paid access is still valid. Community features remain available.",
        "renewal_unavailable": "No valid saved license is available to refresh. Enter your activation code.",
        "try_later": "The licensing service is temporarily unavailable. Please try again later.",
        "transfer_pending": "License updates are paused while a device transfer is pending. Contact support.",
        "activation_saved_community": "The license was saved, but paid access could not be verified. Community features remain available.",
        "operation_failed": "The license operation could not be completed. Try again or contact support.",
        "closed": "Registration closed.",
    },
    "ru": {
        "title": "Регистрация DDC", "key": "Код активации", "show": "Показать код",
        "activate": "Активировать", "renew": "Обновить лицензию", "close": "Закрыть",
        "community_label": "Community", "paid_label": "Paid · реклама отключена",
        "policy": "В Community доступны все возможности конвертации. Действующая платная лицензия отключает рекламу.",
        "expires": "Срок лицензии: до {0} UTC",
        "service_unavailable": "Активация в этом приложении пока не настроена. Все возможности Community остаются доступны.",
        "ready": "Введите код активации.", "checking": "Проверка лицензии…",
        "activating": "Активация…", "renewing": "Обновление лицензии…",
        "paid": "Лицензия активна. Реклама отключена.",
        "community": "Все возможности Community доступны.",
        "invalid_input": "Введите полный код активации, полученный вместе с лицензией.",
        "network_error": "Не удалось связаться с сервисом лицензирования. Проверьте подключение и повторите попытку.",
        "service_rejected": "Сервис лицензирования отклонил запрос. Проверьте код или обратитесь в поддержку.",
        "device_limit": "Достигнут лимит устройств этой лицензии. Для смены устройства обратитесь в поддержку.",
        "expired": "Срок лицензии истёк. Все возможности Community остаются доступны.",
        "revoked": "Лицензия больше не действует. Обратитесь в поддержку; возможности Community остаются доступны.",
        "wrong_product": "Лицензия не распространяется на этот продукт. Проверьте приобретённую лицензию.",
        "clock_unavailable": "Не удалось проверить срок лицензии. Обновите лицензию, когда сервис будет доступен.",
        "device_unavailable": "Не удалось проверить лицензию устройства. Повторите попытку или обратитесь в поддержку.",
        "invalid_response": "Не удалось проверить ответ сервиса лицензирования. Повторите попытку или обратитесь в поддержку.",
        "storage_error": "Не удалось сохранить лицензию на этом компьютере. Повторите попытку или обратитесь в поддержку.",
        "renewal_required": "Обновите лицензию, чтобы проверить платный режим. Возможности Community остаются доступны.",
        "renewal_unavailable": "Нет действующей сохранённой лицензии для обновления. Введите код активации.",
        "try_later": "Сервис лицензирования временно недоступен. Повторите попытку позже.",
        "transfer_pending": "Обновление лицензии приостановлено на время переноса на другое устройство. Обратитесь в поддержку.",
        "activation_saved_community": "Лицензия сохранена, но платный режим пока не подтверждён. Возможности Community остаются доступны.",
        "operation_failed": "Не удалось завершить операцию с лицензией. Повторите попытку или обратитесь в поддержку.",
        "closed": "Регистрация закрыта.",
    },
}


class ActivationDialog(tk.Toplevel):
    """Non-modal registration dialog; closing discards late controller results."""

    def __init__(self, parent, controller=None, *, language="en"):
        super().__init__(parent)
        self.controller = controller if controller is not None else RegistrationController()
        self.texts = _TEXT["ru" if language.lower().split("-")[0].split("_")[0] == "ru" else "en"]
        self._closed = False
        self._poll_id = None
        self._layout_after_id = None
        self.title(self.texts["title"])
        self.transient(parent)
        self.minsize(460, 370)
        self.geometry("560x410")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        frame = ttk.Frame(self, padding=16)
        self._frame = frame
        frame.grid(sticky="nsew")
        frame.columnconfigure(0, weight=1)
        self.edition = tk.StringVar(self)
        ttk.Label(frame, textvariable=self.edition, font=("Segoe UI", 13, "bold")).grid(sticky="w")
        self.policy_label = ttk.Label(frame, text=self.texts["policy"], wraplength=500)
        self.policy_label.grid(sticky="ew", pady=(8, 12))
        ttk.Label(frame, text=self.texts["key"]).grid(sticky="w")
        self.code = tk.StringVar(self)
        self.code_entry = ttk.Entry(frame, textvariable=self.code, show="*", takefocus=True)
        self.code_entry.grid(sticky="ew", pady=(4, 0))
        self.show_code = tk.BooleanVar(self, value=False)
        self.show_button = ttk.Checkbutton(frame, text=self.texts["show"], variable=self.show_code, command=self._toggle_code)
        self.show_button.grid(sticky="w", pady=4)
        self.message = tk.StringVar(self)
        self.message_label = ttk.Label(frame, textvariable=self.message, wraplength=500)
        self.message_label.grid(sticky="ew", pady=(4, 4))
        self.expiry = tk.StringVar(self)
        ttk.Label(frame, textvariable=self.expiry).grid(sticky="w")
        frame.rowconfigure(7, weight=1)
        buttons = ttk.Frame(frame)
        self._buttons = buttons
        buttons.grid(row=8, sticky="ew", pady=(12, 0))
        self.activate_button = ttk.Button(buttons, text=self.texts["activate"], command=self._activate)
        self.activate_button.pack(side="left")
        self.renew_button = ttk.Button(buttons, text=self.texts["renew"], command=self._renew)
        self.renew_button.pack(side="left", padx=8)
        self.close_button = ttk.Button(buttons, text=self.texts["close"], command=self.close)
        self.close_button.pack(side="right")
        self.bind("<Return>", self._return)
        self.bind("<Escape>", lambda _event: self.close())
        self.bind("<Configure>", self._resize, add="+")
        self.bind("<Destroy>", self._destroyed, add="+")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.controller.refresh()
        self._render()
        self._poll_id = self.after(60, self._poll)
        self.code_entry.focus_set()

    def _resize(self, event):
        if event.widget is self:
            width = max(160, event.width - 40)
            self.policy_label.configure(wraplength=width)
            self.message_label.configure(wraplength=width)
            self._schedule_layout()

    def _schedule_layout(self):
        if not self._closed and self._layout_after_id is None:
            self._layout_after_id = self.after_idle(self._fit_minimum)

    def _fit_minimum(self):
        self._layout_after_id = None
        if not self._closed:
            # Text wrapping and native font/DPI metrics determine the floor.
            # All three localized buttons must fit on the same row.
            self.minsize(max(460, self._buttons.winfo_reqwidth() + 32),
                         max(300, self._frame.winfo_reqheight()))

    def _toggle_code(self):
        self.code_entry.configure(show="" if self.show_code.get() else "*")

    def _return(self, event):
        # Preserve the focused button's keyboard action; only entry Return activates.
        if event.widget is self.code_entry:
            self._activate()
            return "break"

    def _activate(self):
        if self._closed or self.controller.state.busy or not self.controller.state.available:
            return
        code = self.code.get()
        self.code.set("")
        self.show_code.set(False)
        self._toggle_code()
        self.controller.activate(code)
        self._render()

    def _renew(self):
        if self._closed or self.controller.state.busy or not self.controller.state.available:
            return
        self.controller.renew()
        self._render()

    def _render(self):
        state = self.controller.state
        enabled = state.available and not state.busy and not state.closed
        for widget in (self.code_entry, self.show_button, self.activate_button, self.renew_button):
            widget.configure(state="normal" if enabled else "disabled")
        self.edition.set(self.texts["paid_label" if state.paid else "community_label"])
        self.message.set(self.texts.get(state.message_key, self.texts["operation_failed"]))
        value = ""
        if state.paid and state.expires_at is not None:
            try:
                value = self.texts["expires"].format(datetime.fromtimestamp(state.expires_at, timezone.utc).strftime("%Y-%m-%d %H:%M"))
            except (ValueError, OverflowError, OSError):
                pass  # No fabricated expiration date if host state is outside platform range.
        self.expiry.set(value)
        self._schedule_layout()

    def _poll(self):
        self._poll_id = None
        if self._closed:
            return
        if self.controller.poll():
            self._render()
        self._poll_id = self.after(60, self._poll)

    def _stop(self):
        if self._closed:
            return
        self._closed = True
        try:
            self.code.set("")
        except tk.TclError:
            pass  # The owning Tcl interpreter may already have been destroyed.
        for attribute in ("_poll_id", "_layout_after_id"):
            callback = getattr(self, attribute)
            setattr(self, attribute, None)
            if callback is None:
                continue
            try:
                self.after_cancel(callback)
            except tk.TclError:
                pass  # Parent destruction may have removed this owned callback already.
        self.controller.close()

    def _destroyed(self, event):
        if event.widget is self:
            self._stop()

    def close(self):
        if self._closed:
            return
        self._stop()
        self.destroy()
