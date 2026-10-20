"""Feedback form, support dialog, support prompt card and the unsent-feedback bar (DESIGN_SPEC "Feedback & support prompt").

Every function takes the running ``gui.App``. Nothing is sent without a user action; nothing here blocks conversion.
"""
import queue
import threading
import tkinter as tk
from tkinter import ttk
import webbrowser

import feedback
import registration_store
import support_prompt

APP_NAME = "IFC to Excel"
APP_ID = "ifc-excel"
LINKS = {
    "star": support_prompt.STAR_URL,
    "email": "mailto:" + feedback.SUPPORT_EMAIL,
    "youtube": "https://www.youtube.com/@datadrivenconstruction",
    "telegram": "https://t.me/datadrivenconstruction",
    "privacy": feedback.PRIVACY_URL,
}


def open_link(app, url):
    """System browser only; a failure is a status line, never an exception."""
    try:
        (app.url_opener or webbrowser.open)(url)
    except Exception:
        app.status.set("Could not open the browser.")


class FeedbackDialog:
    SEND_GAP_SECONDS = 60

    def __init__(self, app, poster=None, clock=None):
        import time
        self.app = app
        self.poster = poster or feedback.post
        self.clock = clock or time.monotonic
        self.result_queue = queue.Queue()
        self.consent_at = None
        t = app.t
        top = self.top = app._dialog(t("fb_title"))
        top.minsize(int(480 * app._dpi), 0)
        body = ttk.Frame(top, padding=16)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=t("fb_category")).pack(anchor="w")
        self.category = ttk.Combobox(body, state="readonly", values=[t("fb_cat_" + c) for c in feedback.CATEGORIES])
        self.category.current(0)
        self.category.pack(fill="x", pady=(2, 8))
        ttk.Label(body, text=t("fb_message")).pack(anchor="w")
        self.message = tk.Text(body, height=6, wrap="word", relief="flat", borderwidth=0, highlightthickness=1,
                               font=(app._family, 9), padx=6, pady=4)
        self.message.pack(fill="x", pady=(2, 0))
        self.counter = ttk.Label(body, style="Caption.TLabel", text=f"0 / {feedback.MAX}")
        self.counter.pack(anchor="e")
        self.path_hint = ttk.Label(body, style="Caption.TLabel", text="", foreground=app.colors("warning"))
        self.path_hint.pack(anchor="w")
        ttk.Label(body, text=t("fb_name")).pack(anchor="w", pady=(6, 0))
        self.name = ttk.Entry(body)
        self.name.pack(fill="x", pady=(2, 6))
        ttk.Label(body, text=t("fb_email")).pack(anchor="w")
        self.email = ttk.Entry(body)
        saved = app.registered_email()
        if saved:
            self.email.insert(0, saved)
        self.email.pack(fill="x", pady=(2, 8))
        self.consent_var = tk.BooleanVar(value=False)
        row = ttk.Frame(body)
        row.pack(fill="x")
        self.consent = ttk.Checkbutton(row, text=t("fb_consent"), variable=self.consent_var, command=self._consent_changed)
        self.consent.pack(side="left")
        link = ttk.Label(body, text=t("fb_privacy"), style="Link.TLabel", cursor="hand2")
        link.pack(anchor="w", padx=(24, 0))
        link.bind("<Button-1>", lambda e: open_link(app, LINKS["privacy"]))
        self.tech = feedback.tech_line(APP_NAME, app.product_version(), app.build_id(), app.lang)
        ttk.Label(body, text=t("fb_tech"), style="Caption.TLabel").pack(anchor="w", pady=(10, 0))
        ttk.Label(body, text=self.tech, style="Caption.TLabel", wraplength=int(440 * app._dpi), justify="left").pack(anchor="w")
        ttk.Label(body, text=t("fb_nofiles"), style="Caption.TLabel").pack(anchor="w")
        self.status = ttk.Label(body, text="", wraplength=int(440 * app._dpi), justify="left")
        self.status.pack(anchor="w", pady=(8, 0))
        buttons = ttk.Frame(body, padding=(0, 10, 0, 0))
        buttons.pack(fill="x")
        self.send_button = ttk.Button(buttons, text=t("fb_send"), style="Accent.TButton", command=self.submit, state="disabled")
        self.send_button.pack(side="right")
        ttk.Button(buttons, text=t("cancel_plain"), command=top.destroy).pack(side="right", padx=(0, 6))
        self.github_button = ttk.Button(buttons, text=t("fb_github"), style="Flat.TButton", command=self.open_github)
        self.github_button.pack(side="left")
        self.mail_button = ttk.Button(buttons, text=t("fb_mail"), style="Flat.TButton", command=self.open_mail)
        self.mail_button.pack(side="left", padx=(4, 0))
        self.message.bind("<KeyRelease>", lambda e: self._edited())
        self.email.bind("<KeyRelease>", lambda e: self._edited())
        self.paint()
        app._present(top)
        self.message.focus_set()
        self._poll()

    # -- helpers
    def paint(self):
        c = self.app.colors
        self.message.configure(background=c("field"), foreground=c("text"), highlightbackground=c("border"),
                               highlightcolor=c("accent"), insertbackground=c("text"))

    def category_id(self):
        return feedback.CATEGORIES[max(0, self.category.current())]

    def text(self):
        return self.message.get("1.0", "end").strip()

    def _consent_changed(self):
        self.consent_at = feedback.iso(feedback.utc_now()) if self.consent_var.get() else None
        self._edited()

    def _edited(self):
        text = self.text()
        self.counter.configure(text=f"{len(text)} / {feedback.MAX}")
        self.path_hint.configure(text=self.app.t("fb_pathhint") if feedback.looks_like_path(text) else "")
        email = self.email.get().strip()
        self.send_button.configure(text=self.app.t("fb_send"),
                                   state="normal" if self.consent_var.get() else "disabled")

    def _say(self, key, error=False, **values):
        self.status.configure(text=self.app.t(key, **values), foreground=self.app.colors("error" if error else "text"))

    def open_github(self):
        open_link(self.app, feedback.github_url(self.category_id(), APP_NAME, self.app.product_version()))

    def open_mail(self):
        open_link(self.app, feedback.mailto(self.category_id(), self.text(), APP_NAME, self.app.product_version(),
                                            self.app.build_id(), self.app.lang))

    # -- sending
    def submit(self):
        app = self.app
        problem = feedback.check_message(self.text())
        if problem:
            return self._say("fb_" + problem, error=True)
        email = self.email.get().strip()
        if not email or not registration_store.valid_email(email):
            return self._say("fb_bademail", error=True)
        name = self.name.get().strip()
        if not name:
            return self._say("fb_needname", error=True)
        if not self.consent_var.get() or not self.consent_at:
            return None
        state = app.prompt
        last = getattr(app, "_last_feedback_send", None)
        if last is not None and self.clock() - last < self.SEND_GAP_SECONDS:
            return self._say("fb_wait", error=True)
        payload = feedback.build_payload(self.category_id(), self.text(), name, email, APP_NAME, app.product_version(),
                                         app.build_id(), app.lang, self.consent_at)
        self.payload = payload
        self.send_button.configure(state="disabled")
        self._say("fb_sending")
        poster, results = self.poster, self.result_queue
        threading.Thread(target=lambda: results.put(poster(payload)), daemon=True).start()
        return None

    def _poll(self):
        try:
            status, info = self.result_queue.get_nowait()
        except queue.Empty:
            try:
                if self.top.winfo_exists():
                    self.top.after(100, self._poll)
            except tk.TclError:
                pass
            return
        app = self.app
        try:
            if status == "sent":
                app._last_feedback_send = self.clock()
                self._say("fb_sent")
                self.send_button.configure(state="disabled")
            elif status == "rate_limited":
                path = feedback.enqueue(self.payload, APP_ID, self.consent_at)  # kept on this PC, offered later
                self._say("fb_ratelimit", error=True, n=info)
                if path:
                    self.status.configure(text=self.status.cget("text") + " " + app.t("fb_queued_short"))
                self.send_button.configure(state="disabled" if path else "normal")
            elif status == "invalid":
                widget = {"firstName": self.name, "name": self.name, "email": self.email}.get((info or {}).get("field"))
                self.status.configure(text=(info or {}).get("message") or "", foreground=app.colors("error"))
                if widget is not None:
                    widget.focus_set()
                self.send_button.configure(state="normal")
            else:  # offline, 5xx, timeout: keep it on this PC
                path = feedback.enqueue(self.payload, APP_ID, self.consent_at)
                self._say("fb_queued" if path else "fb_full", error=path is None)
                self.send_button.configure(state="disabled" if path else "normal")
        except tk.TclError:
            return
        self.last_status = status


def open_feedback(app, poster=None):
    return FeedbackDialog(app, poster=poster)


def open_support(app):
    t = app.t
    top = app._dialog(t("support_title"))
    body = ttk.Frame(top, padding=20)
    body.pack(fill="both", expand=True)
    wrap = int(440 * app._dpi)
    ttk.Label(body, text=t("support_title"), style="Title.TLabel").pack(anchor="w")
    ttk.Label(body, text=t("support_subtitle"), wraplength=wrap, justify="left").pack(anchor="w", pady=(8, 10))
    for button, body_key, url in ((t("prompt_star"), "support_star_body", LINKS["star"]),):
        ttk.Button(body, text=button, command=lambda u=url: (open_link(app, u), app.support_followed())).pack(anchor="w")
        ttk.Label(body, text=t(body_key), style="Caption.TLabel", wraplength=wrap, justify="left").pack(anchor="w", pady=(2, 8))
    share = support_prompt.share_url(app.lang)
    row = ttk.Frame(body)
    row.pack(anchor="w")
    ttk.Button(row, text=t("prompt_linkedin"), command=lambda: (open_link(app, share["linkedin"]), app.support_followed())).pack(side="left")
    ttk.Button(row, text=t("prompt_x"), command=lambda: (open_link(app, share["x"]), app.support_followed())).pack(side="left", padx=(6, 0))
    ttk.Label(body, text=t("support_share_body"), style="Caption.TLabel", wraplength=wrap, justify="left").pack(anchor="w", pady=(2, 8))
    more = ttk.Frame(body)
    more.pack(anchor="w")
    for label, key in (("E-mail", "email"), ("YouTube", "youtube"), ("Telegram", "telegram")):
        link = ttk.Label(more, text=label, style="Link.TLabel", cursor="hand2")
        link.pack(side="left", padx=(0, 14))
        link.bind("<Button-1>", lambda e, k=key: open_link(app, LINKS[k]))
    ttk.Label(body, text=t("support_thanks"), style="Caption.TLabel", wraplength=wrap, justify="left").pack(anchor="w", pady=(10, 0))
    bar = ttk.Frame(body, padding=(0, 12, 0, 0))
    bar.pack(fill="x")
    ok = ttk.Button(bar, text=t("close"), style="Accent.TButton", command=top.destroy)
    ok.pack(side="right")
    app._present(top)
    ok.focus_set()
    return top


def build_prompt_card(app, parent):
    """Non-modal card (bottom right of the summary); returns the frame, not yet packed."""
    t = app.t
    card = ttk.Frame(parent, style="Surface.TFrame", padding=(0, 8, 0, 0))
    ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(0, 8))
    ttk.Label(card, text=t("prompt_title"), style="Done.Surface.TLabel", foreground=app.colors("text")).pack(anchor="w")
    ttk.Label(card, text=t("prompt_body"), style="Surface.TLabel", wraplength=int(560 * app._dpi), justify="left").pack(anchor="w", pady=(2, 6))
    row = ttk.Frame(card, style="Surface.TFrame")
    row.pack(fill="x")
    share = support_prompt.share_url(app.lang)
    ttk.Button(row, text=t("prompt_star"), command=lambda: (open_link(app, LINKS["star"]), app.support_followed())).pack(side="left")
    ttk.Button(row, text=t("prompt_linkedin"), command=lambda: (open_link(app, share["linkedin"]), app.support_followed())).pack(side="left", padx=(6, 0))
    ttk.Button(row, text=t("prompt_x"), command=lambda: (open_link(app, share["x"]), app.support_followed())).pack(side="left", padx=(6, 0))
    ttk.Button(row, text=t("prompt_feedback"), command=lambda: (app.hide_prompt(), open_feedback(app))).pack(side="left", padx=(6, 0))
    ttk.Button(row, text=t("prompt_never"), style="Flat.TButton", command=app.prompt_never).pack(side="right")
    ttk.Button(row, text=t("prompt_later"), style="Flat.TButton", command=app.prompt_later).pack(side="right", padx=(0, 4))
    return card


def build_queue_bar(app, count):
    """Non-modal bar: n unsent messages. Send now / Review / Not now."""
    t = app.t
    bar = ttk.Frame(app.root, padding=(8, 4, 8, 4))
    ttk.Label(bar, text=t("fb_pending", n=count)).pack(side="left")
    ttk.Button(bar, text=t("fb_not_now"), style="Flat.TButton", command=app.hide_queue_bar).pack(side="right")
    ttk.Button(bar, text=t("fb_review"), command=app.review_queue).pack(side="right", padx=(0, 4))
    ttk.Button(bar, text=t("fb_send_now"), style="Accent.TButton", command=app.send_queue).pack(side="right", padx=(0, 4))
    return bar


def review_queue(app, items):
    """Modal list: each unsent message with Delete (a user action); Send happens through the bar."""
    t = app.t
    top = app._dialog(t("fb_review"))
    body = ttk.Frame(top, padding=16)
    body.pack(fill="both", expand=True)
    for path, record in items:
        row = ttk.Frame(body)
        row.pack(fill="x", pady=(0, 8))
        text = record.get("message", "").split("\n\n---\n")[0][:300]
        ttk.Label(row, text=f"{record.get('queued_at', '')}\n{text}", wraplength=int(420 * app._dpi), justify="left").pack(side="left")

        def remove(p=path, r=row):
            try:
                p.unlink()
            except OSError:
                pass
            r.destroy()
        ttk.Button(row, text=t("fb_delete"), style="Flat.TButton", command=remove).pack(side="right")
    ok = ttk.Button(body, text=t("close"), style="Accent.TButton", command=top.destroy)
    ok.pack(anchor="e")
    app._present(top)
    return top
