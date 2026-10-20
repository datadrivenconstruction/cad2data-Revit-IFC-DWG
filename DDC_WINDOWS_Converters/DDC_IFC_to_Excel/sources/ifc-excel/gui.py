"""Desktop front end (DESIGN_SPEC 2026-10): header, input card, options card, progress, summary card.

All Tk access stays on the main thread. Text comes from ``ui_i18n`` (EN/DE/RU), colours from ``ui_theme``
(light/dark, follows the OS unless overridden).
"""
import hashlib
import json
import os
from pathlib import Path
import queue
import sys
import threading
import time
import tkinter as tk
import weakref
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

from batch import BatchRunner
import dialogs
import feedback
import registration_store
import support_prompt
import ui_i18n
import ui_theme

PRODUCT = "DDC IFC to Excel"
UPDATES_URL = "https://github.com/datadrivenconstruction/ddc-ifc-to-excel/releases"
RELEASES_URL = "https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases"
WEBSITE_URL = "https://datadrivenconstruction.io"
IFC_TYPES = (".ifc", ".ifczip")
HERE = Path(__file__).resolve().parent

COLORS = dict(ui_theme.LIGHT)  # mutated in place by set_theme
STATUS_WORDS = {
    "QUEUED": ("st_queued", "muted"), "RUNNING": ("st_running", "accent"),
    "CONVERTED_WITH_LIMITS": ("st_done", "success"), "PARTIAL": ("st_partial", "warning"),
    "FAILED": ("st_failed", "error"), "CANCELLED": ("st_cancelled", "warning"),
    "NOT_STARTED": ("st_not_started", "muted"),
}
DEFAULT_OPTIONS = {"open_folder_when_done": False, "open_single_workbook": False, "keep_finished": True}


def app_data_dir():
    base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(base) / "DDC" / "IFC-to-Excel"


def logs_dir():
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "DDC" / "IFC-to-Excel" / "logs"


def product_version():
    try:
        import converter
        return converter.VERSION
    except Exception:
        return "development"


def build_hash():
    """Build id from the portable MANIFEST.json, else a short hash of the shipped code."""
    for manifest in (HERE.parent.parent / "MANIFEST.json", HERE / "MANIFEST.json"):
        try:
            return str(json.loads(manifest.read_text(encoding="utf-8"))["build_id"])
        except (OSError, ValueError, KeyError):
            continue
    digest = hashlib.sha256()
    for name in ("gui.py", "converter.py", "batch.py"):
        try:
            digest.update((HERE / name).read_bytes())
        except OSError:
            pass
    return digest.hexdigest()[:10]


def licences_dir():
    for candidate in (HERE / "licenses", HERE.parent.parent / "licenses"):
        if candidate.is_dir():
            return candidate
    return HERE / "licenses"


def third_party_components():
    """Lines of the COMPONENT SUMMARY in licenses/THIRD_PARTY_NOTICES.txt."""
    try:
        text = (licences_dir() / "THIRD_PARTY_NOTICES.txt").read_text(encoding="utf-8-sig")
        block = text.split("COMPONENT SUMMARY", 1)[1].strip().splitlines()
        lines = []
        for line in block:
            if line.startswith("- "):
                lines.append(line[2:].split("  [FLAG")[0].strip())
            elif lines and not line.strip():
                break
        if lines:
            return lines
    except (OSError, IndexError):
        pass
    return ["openpyxl - MIT", "et_xmlfile - MIT", "CPython runtime - PSF-2.0", "Fluent UI System Icons - MIT"]


def data_viewer_exe():
    """DDC Data Viewer next to this app (portable layout: ../DDC_Data_Viewer/DDC Data Viewer.exe), or None."""
    for base in (HERE.parent.parent.parent, HERE.parent.parent, HERE.parent):
        candidate = base / "DDC_Data_Viewer" / "DDC Data Viewer.exe"
        if candidate.is_file():
            return candidate
    return None


def human_size(path):
    try:
        size = os.path.getsize(path)
    except OSError:
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024.0


def format_elapsed(seconds):
    seconds = int(max(0, seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


class Tooltip:
    """One-sentence hover hint; ``text`` may be a callable so it follows the UI language."""

    def __init__(self, widget, text):
        self.widget, self.text, self.tip, self.after_id = widget, text, None, None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._hide()
        try:
            self.after_id = self.widget.after(600, self._show)
        except tk.TclError:
            pass

    def _show(self):
        self.after_id = None
        try:
            text = self.text() if callable(self.text) else self.text
            x = self.widget.winfo_rootx() + 8
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 2
            self.tip = tk.Toplevel(self.widget)
            self.tip.wm_overrideredirect(True)
            self.tip.wm_geometry(f"+{x}+{y}")
            tk.Label(self.tip, text=text, background=COLORS["surface"], foreground=COLORS["text"],
                     relief="solid", borderwidth=1, padx=6, pady=3, font="TkDefaultFont").pack()
        except tk.TclError:
            self.tip = None

    def _hide(self, _event=None):
        if self.after_id is not None:
            try:
                self.widget.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None
        if self.tip is not None:
            try:
                self.tip.destroy()
            except tk.TclError:
                pass
            self.tip = None


class Settings:
    """Per-user JSON settings; ``path=None`` keeps everything in memory (tests)."""

    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.data = {}
        if self.path is not None:
            try:
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    self.data = loaded
            except (OSError, ValueError):
                self.data = {}

    TYPES = {"output": str, "input_dir": str, "geometry": str, "options": dict, "more_options": bool,
             "language": str, "theme": str, "log_open": bool}

    def get(self, key, default=None):
        value = self.data.get(key, default)
        expected = self.TYPES.get(key)
        if expected is not None and value is not None and not isinstance(value, expected):
            return default  # Hand-edited or damaged values fall back to defaults.
        return value

    def save(self, **values):
        self.data.update(values)
        if self.path is None:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(temporary, self.path)
        except OSError:
            pass  # Settings are a convenience; never block the workflow.


def apply_style(root, family="Segoe UI"):
    """ttk styles from the current COLORS tokens (re-run after a theme change)."""
    c = COLORS
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")  # the only built-in theme that honours custom colours
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont", "TkCaptionFont"):
        try:
            tkfont.nametofont(name).configure(family=family, size=9)
        except tk.TclError:
            pass
    root.configure(background=c["bg"])
    for key, value in (("background", c["field"]), ("foreground", c["text"]), ("selectBackground", c["accent"]),
                       ("selectForeground", c["on-accent"])):
        root.option_add("*TCombobox*Listbox." + key, value)
    style.configure(".", background=c["bg"], foreground=c["text"], bordercolor=c["border"], lightcolor=c["border"],
                    darkcolor=c["border"], troughcolor=c["border"], focuscolor=c["accent"], font=(family, 9))
    style.configure("TFrame", background=c["bg"])
    style.configure("Surface.TFrame", background=c["surface"])
    style.configure("Strip.TFrame", background=c["surface"], bordercolor=c["border"], lightcolor=c["border"],
                    darkcolor=c["border"], relief="solid", borderwidth=1)
    style.configure("TLabel", background=c["bg"], foreground=c["text"])
    style.configure("Surface.TLabel", background=c["surface"], foreground=c["text"])
    style.configure("SurfaceMuted.TLabel", background=c["surface"], foreground=c["muted"])
    style.configure("Muted.TLabel", background=c["bg"], foreground=c["muted"])
    style.configure("Caption.TLabel", background=c["bg"], foreground=c["muted"], font=(family, 8))
    style.configure("Title.TLabel", background=c["bg"], foreground=c["text"], font=(family, 11, "bold"))
    style.configure("Section.TLabel", background=c["bg"], foreground=c["text"], font=(family, 10, "bold"))
    style.configure("Link.TLabel", background=c["bg"], foreground=c["accent-ink"], font=(family, 9, "underline"))
    style.configure("Status.TLabel", background=c["bg"], foreground=c["muted"])
    style.configure("Done.Surface.TLabel", background=c["surface"], foreground=c["success"], font=(family, 9, "bold"))
    style.configure("Error.TLabel", background=c["bg"], foreground=c["error"])
    style.configure("TButton", background=c["surface"], foreground=c["text"], bordercolor=c["border"],
                    lightcolor=c["surface"], darkcolor=c["surface"], padding=(10, 3), relief="solid", borderwidth=1,
                    focusthickness=1, focuscolor=c["accent"])
    style.map("TButton", background=[("disabled", c["bg"]), ("pressed", c["pressed"]), ("active", c["hover"])],
              foreground=[("disabled", c["muted"])], bordercolor=[("focus", c["accent"])])
    style.configure("Accent.TButton", background=c["accent"], foreground=c["on-accent"], bordercolor=c["accent"],
                    lightcolor=c["accent"], darkcolor=c["accent"], font=(family, 9, "bold"), padding=(22, 4))
    style.map("Accent.TButton", background=[("disabled", c["badge"]), ("pressed", c["accent-hover"]), ("active", c["accent-hover"])],
              foreground=[("disabled", c["muted"])], bordercolor=[("disabled", c["border"]), ("active", c["accent-hover"])])
    style.configure("Flat.TButton", background=c["bg"], foreground=c["text"], bordercolor=c["bg"], lightcolor=c["bg"],
                    darkcolor=c["bg"], padding=(8, 3), borderwidth=1)
    style.map("Flat.TButton", background=[("disabled", c["bg"]), ("active", c["hover"]), ("pressed", c["pressed"])],
              foreground=[("disabled", c["muted"])], bordercolor=[("focus", c["accent"])])
    style.configure("Link.TButton", background=c["bg"], foreground=c["accent-ink"], bordercolor=c["bg"], lightcolor=c["bg"],
                    darkcolor=c["bg"], padding=(4, 2), borderwidth=1)
    style.map("Link.TButton", foreground=[("active", c["accent-ink"])], background=[("active", c["hover"])],
              bordercolor=[("focus", c["accent"])])
    style.configure("StatusLink.TButton", background=c["bg"], foreground=c["accent-ink"], bordercolor=c["bg"],
                    lightcolor=c["bg"], darkcolor=c["bg"], padding=(4, 0), borderwidth=1, font=(family, 8))
    style.map("StatusLink.TButton", background=[("active", c["hover"])], bordercolor=[("focus", c["accent"])])
    style.configure("Chip.Toolbutton", background=c["bg"], foreground=c["muted"], bordercolor=c["border"],
                    lightcolor=c["bg"], darkcolor=c["bg"], padding=(12, 2), relief="solid", borderwidth=1)
    style.map("Chip.Toolbutton",
              background=[("selected", c["selected"]), ("active", c["hover"])],
              foreground=[("selected", c["accent-ink"])], bordercolor=[("selected", c["accent"]), ("focus", c["accent"])],
              lightcolor=[("selected", c["selected"])], darkcolor=[("selected", c["selected"])])
    style.configure("TCheckbutton", background=c["bg"], foreground=c["text"], indicatorbackground=c["field"],
                    indicatorforeground=c["on-accent"], bordercolor=c["border"])
    style.map("TCheckbutton", background=[("active", c["bg"])],
              indicatorbackground=[("selected", c["accent"]), ("active", c["hover"])],
              indicatorforeground=[("selected", c["on-accent"])])
    style.configure("TEntry", fieldbackground=c["field"], foreground=c["text"], insertcolor=c["text"], bordercolor=c["border"],
                    padding=3)
    style.map("TEntry", bordercolor=[("focus", c["accent"])], fieldbackground=[("disabled", c["bg"])],
              foreground=[("disabled", c["muted"])])
    style.configure("Treeview", background=c["surface"], fieldbackground=c["surface"], foreground=c["text"],
                    bordercolor=c["border"], lightcolor=c["border"], darkcolor=c["border"], borderwidth=1,
                    rowheight=max(26, tkfont.nametofont("TkDefaultFont").metrics("linespace") + 12))
    style.map("Treeview", background=[("selected", "focus", c["selected"]), ("selected", "!focus", c["hover"])],
              foreground=[("selected", c["text"])])
    style.configure("Treeview.Heading", background=c["surface"], foreground=c["muted"], bordercolor=c["border"],
                    lightcolor=c["surface"], darkcolor=c["surface"], padding=(8, 4), relief="flat", font=(family, 9))
    style.map("Treeview.Heading", background=[("active", c["hover"])])
    for orient in ("Vertical", "Horizontal"):
        style.configure(f"{orient}.TScrollbar", background=c["border"], troughcolor=c["surface"], bordercolor=c["surface"],
                        arrowcolor=c["muted"], lightcolor=c["border"], darkcolor=c["border"], gripcount=0)
        style.map(f"{orient}.TScrollbar", background=[("active", c["muted"])])
    style.configure("Horizontal.TProgressbar", background=c["accent"], troughcolor=c["badge"], bordercolor=c["badge"],
                    lightcolor=c["accent"], darkcolor=c["accent"], thickness=6)
    style.configure("TSeparator", background=c["border"])
    return style


def set_titlebar_dark(window, dark):
    """The caption stays native; only the dark/light caption flag follows the app theme (best effort)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        value = ctypes.c_int(1 if dark else 0)
        for attribute in (20, 19):
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(value), 4) == 0:
                break
    except Exception:
        pass


class App:

    def __init__(self, root, *, settings=None, registration=None, prompt_state=None,
                 url_opener=None):
        self.root = root
        self.registration = registration if registration is not None else registration_store.RegistrationStore()
        self._status_spec = None
        self.prompt = prompt_state if prompt_state is not None else support_prompt.PromptState(dialogs.APP_ID)
        self.url_opener = url_opener
        self.queue_bar = None
        self.prompt_card = None
        self._prompt_after_id = None
        self._extras_after_id = None
        self.settings = settings if settings is not None else Settings(None)
        language = self.settings.get("language")
        self.lang = language if language in ui_i18n.LANGUAGES else ui_i18n.system_language()
        mode = self.settings.get("theme")
        self.theme_mode = mode if mode in ui_theme.MODES else "auto"
        self._texts = []        # (widget, key, option) relabelled on language change
        self._tooltips = []
        self._painters = []     # callables repainting plain tk widgets on theme change
        self._dialogs = []
        self._images = {}
        root.title("IFC to Excel · DataDrivenConstruction")
        self._family = ui_theme.font_family(root)
        name, tokens = ui_theme.resolve(self.theme_mode)
        self.theme_name = name
        COLORS.clear()
        COLORS.update(tokens)
        apply_style(root, self._family)
        self._dpi = max(1.0, root.winfo_fpixels("1i") / 96.0)
        self._set_icon(root)
        root.minsize(int(640 * self._dpi), int(420 * self._dpi))
        self._apply_default_geometry(self.settings.get("geometry"))
        self.events = queue.Queue()
        self.runner = None
        self.worker = None
        self.closing = False
        self._destroyed = False
        self._poll_after_id = None
        self.busy = False
        self.licence_window = None
        self._about = None
        self.files = []
        self._keys = set()
        self.results = {}
        self.log_lines = []
        self._started_at = None
        self._finished_seconds = 0.0
        self._last_clock = ""
        self.output = tk.StringVar(value=self.settings.get("output") or "")
        self.status = tk.StringVar(value=self.t("ready"))
        self.progress_text = tk.StringVar(value="")
        options = {**DEFAULT_OPTIONS, **{k: v for k, v in (self.settings.get("options") or {}).items()
                                          if k in DEFAULT_OPTIONS and isinstance(v, bool)}}
        self.options = {key: tk.BooleanVar(value=bool(options[key])) for key in DEFAULT_OPTIONS}
        self.chip_vars = {"xlsx": tk.BooleanVar(value=True)}
        self._build_menu()
        self._build_statusbar()
        self._build_body()
        self._build_context_menu()
        self._bind_keys()
        self._refresh_empty()
        self.show_details()
        self._repaint()
        root.protocol("WM_DELETE_WINDOW", self.request_close)
        root.bind("<Destroy>", self._on_destroy, add="+")
        self._poll_after_id = root.after(100, self.poll)
        # Persisted outbox work must not depend on another conversion result.
        # Defer the DB read/launch to the background worker after UI creation.
        self._extras_after_id = root.after(0, self._startup_extras)

    # ----- text, theme, language ----------------------------------------
    def t(self, key, **values):
        return ui_i18n.tr(self.lang, key, **values)

    def _text(self, widget, key, option="text"):
        """Set a translated option now and on every language change."""
        widget.configure(**{option: self.t(key)})
        self._texts.append((widget, key, option))
        return widget

    def _tip(self, widget, key):
        tip = Tooltip(widget, lambda: self.t(key))
        self._tooltips.append(tip)
        return tip

    def _set_icon(self, window):
        try:
            icon = HERE / "assets" / "ddc.ico"
            if icon.is_file():
                window.iconbitmap(default=str(icon)) if window is self.root else window.iconbitmap(str(icon))
        except tk.TclError:
            pass

    def set_language(self, language):
        if language not in ui_i18n.LANGUAGES or language == self.lang:
            return
        spec = self._status_spec
        was_ready = self.status.get() == self.t("ready")
        self.lang = language
        self.settings.save(language=language)
        for widget, key, option in list(self._texts):
            try:
                widget.configure(**{option: self.t(key)})
            except tk.TclError:
                pass
        self._retext_dynamic()
        if was_ready:
            self.status.set(self.t("ready"))
        elif spec is not None and self.status.get() == spec[2]:
            self.set_status(spec[0], **spec[1])
        for dialog in list(self._dialogs):
            try:
                dialog.destroy()
            except tk.TclError:
                pass
        self._dialogs.clear()
        self._about = self.licence_window = None
        self.show_details()

    def set_status(self, key, **values):
        """Status line from a translation key; re-rendered when the language changes."""
        text = self.t(key, **values)
        self._status_spec = (key, values, text)
        self.status.set(text)

    def registered_email(self):
        try:
            return self.registration.email()
        except Exception:
            return None

    def licence_label(self):
        email = self.registered_email()
        return self.t("reg_status", email=email) if email else self.t("status_bar")

    def refresh_licence_label(self):
        self.licence_button.configure(text=self.licence_label())

    def _retext_dynamic(self):
        self.refresh_licence_label()
        for index, source in enumerate(self.files):
            result = self.results.get(index)
            self._set_row(index, source, result["status"] if result else "QUEUED", result)
        for column, key in (("file", "col_name"), ("size", "col_size"), ("status", "col_status"), ("result", "col_result")):
            self.tree.heading(column, text=self.t(key))
        self.more_toggle.configure(text=("▾ " if self.more_frame.winfo_manager() else "▸ ") + self.t("more_options"))
        self.log_toggle.configure(text=("▾ " if self.log_frame.winfo_manager() else "▸ ") + self.t("log"))
        self._draw_drop()
        self._update_progress_text()
        self._update_summary()
        self.output_entry_hint()
        self._build_menu()
        self.language_var.set(self.lang)
        if self.queue_bar is not None:  # rebuilt so its texts follow the language
            self.hide_queue_bar()
            self.check_queue()
        if self.prompt_card is not None:
            self.hide_prompt()
            self.show_prompt(mark=False)

    def set_theme(self, mode):
        if mode not in ui_theme.MODES:
            return
        self.theme_mode = mode
        self.settings.save(theme=mode)
        name, tokens = ui_theme.resolve(mode)
        self.theme_name = name
        COLORS.clear()
        COLORS.update(tokens)
        apply_style(self.root, self._family)
        self.theme_var.set(mode)
        self._repaint()

    def cycle_theme(self):
        modes = ui_theme.MODES
        self.set_theme(modes[(modes.index(self.theme_mode) + 1) % len(modes)])

    def _repaint(self):
        self.root.configure(background=COLORS["bg"])
        for painter in list(self._painters):
            try:
                painter()
            except tk.TclError:
                pass
        for dialog in list(self._dialogs):
            try:
                dialog.configure(background=COLORS["bg"])
                set_titlebar_dark(dialog, self.theme_name == "dark")
            except tk.TclError:
                pass
        set_titlebar_dark(self.root, self.theme_name == "dark")
        self._draw_drop()
        self._tag_colours()

    def _tag_colours(self):
        for key in ("muted", "success", "warning", "error"):
            self.tree.tag_configure(key, foreground=COLORS[key])
        self.tree.tag_configure("accent", foreground=COLORS["accent-ink"])

    # ----- layout -------------------------------------------------------
    def _apply_default_geometry(self, saved=None):
        if isinstance(saved, str) and saved.count("x") == 1:
            try:
                size, _, _ = saved.partition("+")
                width, height = (int(v) for v in size.split("x"))
                if width >= 400 and height >= 300:
                    self.root.geometry(saved)
                    return
            except ValueError:
                pass
        dpi = getattr(self, "_dpi", max(1.0, self.root.winfo_fpixels("1i") / 96.0))
        width = min(int(880 * dpi), self.root.winfo_screenwidth() - int(40 * dpi))
        height = min(int(560 * dpi), self.root.winfo_screenheight() - int(90 * dpi))
        self.root.geometry(f"{width}x{height}")

    # ----- menu bar ------------------------------------------------------
    def _build_menu(self):
        t = self.t
        bar = tk.Menu(self.root, tearoff=False)
        file_menu = tk.Menu(bar, tearoff=False)
        file_menu.add_command(label=t("add_files"), accelerator="Ctrl+O", command=self.add_files)
        file_menu.add_command(label=t("add_folder"), accelerator="Ctrl+Shift+A", command=self.add_folder)
        file_menu.add_command(label=t("open_output"), accelerator="Ctrl+Shift+O", command=self.open_output_folder)
        file_menu.add_separator()
        file_menu.add_command(label=t("exit"), command=self.request_close)
        bar.add_cascade(label=t("menu_file"), menu=file_menu, underline=0)
        view = tk.Menu(bar, tearoff=False)
        theme_menu = tk.Menu(view, tearoff=False)
        self.theme_var = tk.StringVar(value=self.theme_mode)
        for mode in ui_theme.MODES:
            theme_menu.add_radiobutton(label=t("theme_" + mode + "_n"), value=mode, variable=self.theme_var,
                                       command=lambda m=mode: self.set_theme(m))
        language_menu = tk.Menu(view, tearoff=False)
        self.language_var = tk.StringVar(value=self.lang)
        for code in ui_i18n.LANGUAGES:
            language_menu.add_radiobutton(label=ui_i18n.LANGUAGE_NAMES[code], value=code, variable=self.language_var,
                                          command=lambda c=code: self.set_language(c))
        view.add_cascade(label=t("view_theme"), menu=theme_menu)
        view.add_cascade(label=t("view_language"), menu=language_menu)
        bar.add_cascade(label=t("menu_view"), menu=view, underline=0)
        help_menu = tk.Menu(bar, tearoff=False)
        help_menu.add_command(label=t("about"), accelerator="F1", command=self.show_about)
        help_menu.add_command(label=t("licence"), command=self.open_licence)
        help_menu.add_command(label=t("updates"), command=lambda: self._open_url(UPDATES_URL))
        help_menu.add_command(label=t("menu_feedback"), command=self.open_feedback)
        help_menu.add_command(label=t("menu_support"), command=self.open_support)
        help_menu.add_command(label=t("logs"), command=self.open_logs_folder)
        help_menu.add_command(label=t("eula"), command=self.open_licences_folder)
        bar.add_cascade(label=t("menu_help"), menu=help_menu, underline=0)
        self.root.configure(menu=bar)
        self.menubar, self.file_menu, self.help_menu = bar, file_menu, help_menu

    def _build_body(self):
        self._build_toolbar()
        self._build_options_row()      # bottom widgets are packed before the grid, which takes the rest
        self._build_strip()
        self._build_log()
        self._build_grid()
        import viewer_support  # "Open in Data Viewer": DDC Viewer package on demand (own code)
        self.viewer_button = viewer_support.ViewerButton(self, self.log_bar)
        self.viewer_button.button.pack_forget()  # shown by the summary strip instead
        if self.settings.get("log_open"):
            self.toggle_log()

    def _build_toolbar(self):
        bar = ttk.Frame(self.root, padding=(8, 6, 8, 6))
        bar.pack(side="top", fill="x")
        self.toolbar = bar
        self.add = ttk.Button(bar, command=self.add_files)
        self._text(self.add, "add_files").pack(side="left")
        self.add_folder_button = ttk.Button(bar, command=self.add_folder)
        self._text(self.add_folder_button, "add_folder").pack(side="left", padx=(4, 0))
        self.remove_button = ttk.Button(bar, command=self.remove_selected, style="Flat.TButton")
        self._text(self.remove_button, "remove").pack(side="left", padx=(4, 0))
        self.clear = ttk.Button(bar, command=self.clear_files, style="Flat.TButton")
        self._text(self.clear, "clear").pack(side="left", padx=(2, 0))
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        self._text(ttk.Label(bar), "output_label").pack(side="left")
        self.browse = ttk.Button(bar, command=self.choose_output)
        self._text(self.browse, "browse").pack(side="right")
        self.output_entry = ttk.Entry(bar, textvariable=self.output)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(6, 6), ipady=1)
        self.output_hint = tk.Label(self.output_entry, cursor="xterm", borderwidth=0, padx=0, pady=0)
        self.output_hint.bind("<Button-1>", lambda e: self.output_entry.focus_set())
        self.output.trace_add("write", lambda *a: self.output_entry_hint())
        self.output_entry_hint()
        self._tip(self.output_entry, "beside_source")

    def output_entry_hint(self):
        """Grey placeholder 'Beside the source file' while the field is empty."""
        hint = getattr(self, "output_hint", None)
        if hint is None:
            return
        try:
            if self.output.get().strip():
                hint.place_forget()
            else:
                hint.configure(text=self.t("beside_source"), background=COLORS["field"], foreground=COLORS["muted"],
                               font=(self._family, 9))
                hint.place(x=6, rely=0.5, anchor="w")
        except tk.TclError:
            pass

    @staticmethod
    def _autoscroll(bar, place, pack=False):
        """Scroll callback that shows the scrollbar only when the content does not fit."""
        def update(first, last):
            bar.set(first, last)
            needed = float(first) > 0.0 or float(last) < 1.0
            if needed and not bar.winfo_manager():
                (bar.pack if pack else bar.grid)(**place)
            elif not needed and bar.winfo_manager():
                (bar.pack_forget if pack else bar.grid_remove)()
        return update

    def _build_grid(self):
        area = ttk.Frame(self.root, padding=(8, 0, 8, 6))
        area.pack(side="top", fill="both", expand=True)
        self.table_frame = area
        self.tree = ttk.Treeview(area, columns=("file", "size", "status", "result", "x"), show="headings",
                                 selectmode="browse", height=4)
        heading = tkfont.nametofont("TkHeadingFont")
        for column, key, minimum, stretch in (("file", "col_name", 160, True), ("size", "col_size", 80, False),
                                              ("status", "col_status", 100, False), ("result", "col_result", 160, True)):
            text = self.t(key)
            self.tree.heading(column, text=text, anchor="e" if column == "size" else "w")
            sample = {"size": "9999.9 MB", "status": "Not started"}.get(column, "")
            width = max(int(minimum * self._dpi), heading.measure(text) + 24,
                        tkfont.nametofont("TkDefaultFont").measure(sample) + 24)
            self.tree.column(column, width=width if not stretch else width * 2, minwidth=width, stretch=stretch,
                             anchor="e" if column == "size" else "w")
        self.tree.heading("x", text="")
        self.tree.column("x", width=int(30 * self._dpi), minwidth=int(30 * self._dpi), stretch=False, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(area, orient="vertical", command=self.tree.yview)
        horizontal = ttk.Scrollbar(area, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self._autoscroll(vertical, dict(row=0, column=1, sticky="ns")),
                            xscrollcommand=self._autoscroll(horizontal, dict(row=1, column=0, sticky="ew")))
        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.show_details)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-1>", self._on_click, add="+")
        self.tree.bind("<Button-3>", self._on_right_click)
        self.tree.bind("<App>", self._on_menu_key)
        self.tree.bind("<Shift-F10>", self._on_menu_key)
        self.tree.bind("<Delete>", lambda e: self._key(self.remove_selected))
        # Empty state: a dashed drop area laid over the grid; a click chooses files.
        self.drop = tk.Canvas(self.tree, highlightthickness=0, borderwidth=0, cursor="hand2", takefocus=True)
        self.drop.bind("<Configure>", lambda e: self._draw_drop())
        self.drop.bind("<Button-1>", lambda e: self.add_files())
        self.drop.bind("<Return>", lambda e: self._key(self.add_files))
        self.drop.bind("<space>", lambda e: self._key(self.add_files))
        self.drop.bind("<Enter>", lambda e: self._draw_drop(hover=True))
        self.drop.bind("<Leave>", lambda e: self._draw_drop())
        self.drop.bind("<FocusIn>", lambda e: self._draw_drop(hover=True))
        self.drop.bind("<FocusOut>", lambda e: self._draw_drop())
        self._tag_colours()

    def _draw_drop(self, hover=False):
        canvas = getattr(self, "drop", None)
        if canvas is None:
            return
        try:
            canvas.delete("all")
            canvas.configure(background=COLORS["surface"])
            width, height = max(canvas.winfo_width(), 40), max(canvas.winfo_height(), 40)
            colour = COLORS["accent"] if hover else COLORS["border"]
            m, r = 8, 8
            points = [m + r, m, width - m - r, m, width - m, m, width - m, m + r, width - m, height - m - r,
                      width - m, height - m, width - m - r, height - m, m + r, height - m, m, height - m,
                      m, height - m - r, m, m + r, m, m]
            canvas.create_polygon(points, smooth=True, fill=COLORS["selected"] if hover else COLORS["surface"],
                                  outline=colour, width=1, dash=(4, 3))
            canvas.create_text(width // 2, height // 2 - 8, text=self.t("drop"), fill=COLORS["text"],
                               font=(self._family, 10, "bold"))
            canvas.create_text(width // 2, height // 2 + 12, text=self.t("drop_ctrl"), fill=COLORS["muted"],
                               font=(self._family, 9))
        except tk.TclError:
            pass

    def _refresh_empty(self):
        """The dashed drop area is the empty state of the grid."""
        drop = getattr(self, "drop", None)
        if drop is None:
            return
        if self.tree.get_children():
            drop.place_forget()
        else:
            offset = int(26 * self._dpi)
            drop.place(x=0, y=offset, relwidth=1, relheight=1, height=-offset)
            self._draw_drop()

    def _build_options_row(self):
        wrap = ttk.Frame(self.root)
        wrap.pack(side="bottom", fill="x")
        self.actions_frame = wrap
        self.more_frame = ttk.Frame(wrap, padding=(16, 2, 8, 4))  # packed by toggle_more
        for key, label in (("open_folder_when_done", "open_when_done"), ("open_single_workbook", "open_single"),
                           ("keep_finished", "keep_finished")):
            box = ttk.Checkbutton(self.more_frame, variable=self.options[key], command=self._save_options)
            self._text(box, label).pack(anchor="w")
        self.support_var = tk.BooleanVar(value=self.prompt.enabled())
        support_box = ttk.Checkbutton(self.more_frame, variable=self.support_var, command=self._set_support_suggestions)
        self._text(support_box, "support_off").pack(anchor="w")
        self.options_row = ttk.Frame(wrap, padding=(8, 6, 8, 6))
        self.options_row.pack(side="bottom", fill="x")
        row = self.options_row
        self.chip_xlsx = ttk.Checkbutton(row, text="✓ XLSX", style="Chip.Toolbutton", variable=self.chip_vars["xlsx"],
                                         command=lambda: self.chip_vars["xlsx"].set(True))
        self.chip_xlsx.pack(side="left")
        self._tip(self.chip_xlsx, "chip_tip")
        self.more_toggle = ttk.Button(row, style="Link.TButton", command=self.toggle_more, text="▸ " + self.t("more_options"))
        self.more_toggle.pack(side="left", padx=(10, 0))
        self.start = ttk.Button(row, style="Accent.TButton", command=self.run, default="active")
        self._text(self.start, "convert").pack(side="right")
        self.cancel_button = ttk.Button(row, command=self.cancel, state="disabled")
        self._text(self.cancel_button, "cancel").pack(side="right", padx=(0, 6))
        if self.settings.get("more_options"):
            self.toggle_more()

    def _build_strip(self):
        """Strip above the options row: progress while running, summary when finished; hidden when idle."""
        self.strip = ttk.Frame(self.root, padding=(8, 0, 8, 6))
        card = self.strip_card = ttk.Frame(self.strip, style="Strip.TFrame", padding=(10, 6))
        card.pack(fill="x")
        self.progress_box = ttk.Frame(card, style="Surface.TFrame")
        self.progress = ttk.Progressbar(self.progress_box, mode="determinate", style="Horizontal.TProgressbar",
                                        length=int(220 * self._dpi))
        self.progress.pack(side="left", pady=2)
        self.progress_label = ttk.Label(self.progress_box, textvariable=self.progress_text, style="Surface.TLabel")
        self.progress_label.pack(side="left", padx=(12, 0))
        self.summary_frame = ttk.Frame(card, style="Surface.TFrame")
        self.summary_done = ttk.Label(self.summary_frame, style="Done.Surface.TLabel")
        self._text(self.summary_done, "done", "text")
        self.summary_done.configure(text="✓ " + self.t("done"))
        self.summary_done.pack(side="left")
        self.summary_text = tk.StringVar(value="")
        ttk.Label(self.summary_frame, textvariable=self.summary_text, style="Surface.TLabel").pack(side="left", padx=(10, 0))
        self.copy_report_button = ttk.Button(self.summary_frame, command=self.copy_report)
        self._text(self.copy_report_button, "copy_report").pack(side="right")
        self.open_viewer_button = ttk.Button(self.summary_frame, command=self.open_in_viewer)
        self._text(self.open_viewer_button, "open_viewer")
        self.open_output_link = ttk.Button(self.summary_frame, command=self.open_output_folder)
        self._text(self.open_output_link, "open_output").pack(side="right", padx=(0, 6))

    def _build_log(self):
        bar = ttk.Frame(self.root, padding=(8, 0, 8, 0))
        bar.pack(side="bottom", fill="x")
        self.log_bar = bar
        self.log_toggle = ttk.Button(bar, style="Link.TButton", command=self.toggle_log, text="▸ " + self.t("log"))
        self.log_toggle.pack(side="left")
        self.copy_details_button = ttk.Button(bar, command=self.copy_details, state="disabled", style="Flat.TButton")
        self._text(self.copy_details_button, "copy_details").pack(side="right")
        self.open_folder_button = ttk.Button(bar, command=self.open_folder, state="disabled", style="Flat.TButton")
        self._text(self.open_folder_button, "open_folder").pack(side="right", padx=(0, 2))
        self.open_workbook_button = ttk.Button(bar, command=self.open_workbook, state="disabled", style="Flat.TButton")
        self._text(self.open_workbook_button, "open_workbook").pack(side="right", padx=(0, 2))
        self.log_frame = ttk.Frame(self.root, padding=(8, 2, 8, 4))
        self.details_frame = self.log_frame
        text_row = ttk.Frame(self.log_frame)
        text_row.pack(side="top", fill="x")
        self.details = tk.Text(text_row, height=5, wrap="word", state="disabled", relief="flat", borderwidth=0,
                               font=("Consolas", 9), highlightthickness=1, padx=8, pady=6)
        self.details.pack(side="left", fill="x", expand=True)
        detail_scroll = ttk.Scrollbar(text_row, orient="vertical", command=self.details.yview)
        self.details.configure(yscrollcommand=self._autoscroll(detail_scroll, dict(side="right", fill="y"), pack=True))

        def paint():
            self.details.configure(background=COLORS["field"], foreground=COLORS["text"],
                                   highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"],
                                   insertbackground=COLORS["text"], selectbackground=COLORS["selected"],
                                   selectforeground=COLORS["text"])
            self.details.tag_configure("muted", foreground=COLORS["muted"], font=(self._family, 9))
            self.details.tag_configure("error", foreground=COLORS["error"])
            self.output_entry_hint()
        self._painters.append(paint)
        paint()

    def _build_statusbar(self):
        ttk.Separator(self.root, orient="horizontal").pack(side="bottom", fill="x")
        bar = ttk.Frame(self.root, padding=(8, 2, 4, 2))
        bar.pack(side="bottom", fill="x")
        self.status_frame = bar
        self.licence_button = ttk.Button(bar, style="StatusLink.TButton", command=self.open_licence)
        self.licence_button.pack(side="right")
        self.refresh_licence_label()
        self.registration_button = self.licence_button  # kept for hosts that still use the old name
        self.status_label = ttk.Label(bar, textvariable=self.status, anchor="w", style="Status.TLabel")
        self.status_label.pack(side="left", fill="x", expand=True)

    def toggle_more(self):
        if self.more_frame.winfo_manager():
            self.more_frame.pack_forget()
            self.more_toggle.configure(text="▸ " + self.t("more_options"))
            shown = False
        else:
            self.more_frame.pack(side="top", fill="x", before=self.options_row)
            self.more_toggle.configure(text="▾ " + self.t("more_options"))
            shown = True
        self.settings.save(more_options=shown)

    def toggle_log(self, force=None):
        shown = bool(self.log_frame.winfo_manager())
        want = (not shown) if force is None else force
        if want == shown:
            return
        if want:
            self.log_frame.pack(side="bottom", fill="x", before=self.log_bar)
            self.log_toggle.configure(text="▾ " + self.t("log"))
        else:
            self.log_frame.pack_forget()
            self.log_toggle.configure(text="▸ " + self.t("log"))
        self.settings.save(log_open=want)

    def _build_context_menu(self):
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Open file", command=self.open_workbook)
        menu.add_command(label="Open folder", command=self.open_folder)
        menu.add_separator()
        menu.add_command(label="Copy path", command=self.copy_path)
        menu.add_command(label="Copy details", command=self.copy_details)
        menu.add_separator()
        menu.add_command(label="Remove", accelerator="Del", command=self.remove_selected)
        self.context_menu = menu
        self._painters.append(lambda: menu.configure(background=COLORS["surface"], foreground=COLORS["text"],
                                                     activebackground=COLORS["accent"], activeforeground=COLORS["on-accent"]))

    def _bind_keys(self):
        root = self.root
        root.bind("<Control-o>", lambda e: self._key(self.add_files))
        root.bind("<Control-O>", lambda e: self._key(self.open_output_folder) if e.state & 1 else self._key(self.add_files))
        root.bind("<Control-Shift-O>", lambda e: self._key(self.open_output_folder))
        root.bind("<Control-Shift-A>", lambda e: self._key(self.add_folder))
        root.bind("<Control-A>", lambda e: self._key(self.add_folder) if e.state & 1 else None)
        root.bind("<Control-r>", lambda e: self._key(self.run))
        root.bind("<Return>", self._on_return)
        root.bind("<KP_Enter>", self._on_return)
        root.bind("<Escape>", lambda e: self._key(self._on_escape))
        root.bind("<F1>", lambda e: self._key(self.show_about))

    def _on_escape(self):
        """Esc: running -> Cancel; otherwise the support card counts as "Maybe later"."""
        if self.busy:  # self.runner stays set after a finished run
            self.cancel()
        elif self.prompt_card is not None:
            self.prompt_later()

    def _key(self, action):
        action()
        return "break"

    def _on_return(self, event):
        if isinstance(event.widget, (ttk.Button, tk.Button, tk.Canvas, ttk.Combobox)):
            return None  # Let a focused control keep its own activation.
        return self._key(self.run)

    # ----- helpers ------------------------------------------------------
    def _save_options(self):
        self.settings.save(options={key: var.get() for key, var in self.options.items()})

    def _open_url(self, url):
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            self.status.set("Could not open the browser.")

    def _startfile(self, path):
        try:
            os.startfile(path)
            return True
        except (OSError, AttributeError) as exc:
            messagebox.showerror("Cannot open", str(exc), parent=self.root)
            return False

    def _copy(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.set_status("copied")

    def _row_values(self, index):
        source = self.files[index]
        result = self.results.get(index)
        raw = result["status"] if result else "QUEUED"
        return self._values(source, raw, result)

    def _values(self, source, raw, result=None):
        key, colour = STATUS_WORDS.get(raw, (None, "muted"))
        word = self.t(key) if key else raw.replace("_", " ").capitalize()
        outcome = ""
        if result:
            if raw == "CONVERTED_WITH_LIMITS" and result.get("workbook"):
                outcome = Path(result["workbook"]).name
            else:
                outcome = (result.get("message") or "").strip().splitlines()[0][:160] if result.get("message") else ""
                if raw == "FAILED" and outcome:
                    outcome += "  ·  " + self.t("details")
        return (Path(source).name, human_size(source), word, outcome, "✕"), (colour,)

    def _set_row(self, index, source, raw, result=None):
        values, tags = self._values(source, raw, result)
        self.tree.item(str(index), values=values, tags=tags)

    @staticmethod
    def _key_of(name):
        return os.path.normcase(os.path.abspath(name))

    def _insert(self, name):
        key = self._key_of(name)
        if key in self._keys:
            return False
        self._keys.add(key)
        index = len(self.files)
        self.files.append(name)
        values, tags = self._values(name, "QUEUED")
        self.tree.insert("", "end", iid=str(index), values=values, tags=tags)
        return True

    def _files_in_list(self):
        return self.t("files_in_list", n=len(self.files))

    def _add_paths(self, paths):
        paths = [str(p) for p in paths]
        supported = [p for p in paths if p.lower().endswith(IFC_TYPES)]
        added = sum(self._insert(os.path.normpath(p)) for p in supported)
        self._refresh_empty()
        skipped = len(paths) - len(supported)
        duplicates = len(supported) - added
        notes = []
        if duplicates:
            notes.append(self.t("already", n=duplicates))
        if skipped:
            notes.append(self.t("unsupported", n=skipped))
        if added or notes:
            self.status.set(self._files_in_list() + ("; " + ", ".join(notes) if notes else ""))
            self._hide_summary()
        return added

    def _rebuild(self, keep):
        files, results = self.files, self.results
        self.tree.delete(*self.tree.get_children())
        self.files, self.results, self._keys = [], {}, set()
        for old in keep:
            self._insert(files[old])
            if old in results:
                self.results[len(self.files) - 1] = results[old]
                self._set_row(len(self.files) - 1, files[old], results[old]["status"], results[old])
        self._refresh_empty()
        self.show_details()

    def drop_files(self, paths):
        """Entry point for native drag-and-drop (see enable_file_drop)."""
        if self.busy or self.closing:
            return 0
        expanded = []
        for path in paths:
            if os.path.isdir(path):
                expanded.extend(self._scan(path))
            else:
                expanded.append(path)
        return self._add_paths(expanded)

    @staticmethod
    def _scan(folder):
        found = []
        for base, _dirs, names in os.walk(folder):
            found.extend(os.path.join(base, n) for n in sorted(names) if n.lower().endswith(IFC_TYPES))
        return found

    # ----- lifecycle (unchanged behaviour) ------------------------------
    def _cancel_after(self, attribute):
        callback = getattr(self, attribute)
        setattr(self, attribute, None)
        if callback is not None:
            try:
                self.root.after_cancel(callback)
            except tk.TclError:
                pass  # The host may already have removed this Tcl command.

    def colors(self, name):
        return COLORS[name]

    def product_version(self):
        return product_version()

    def build_id(self):
        return build_hash()

    def _startup_extras(self):
        """After the window is shown: count the active day, offer unsent feedback."""
        self._extras_after_id = None
        if self.closing:
            return
        try:
            self.prompt.touch_day()
        except Exception:
            pass
        self.check_queue()

    # ----- feedback, support, prompt ------------------------------------
    def open_feedback(self, poster=None):
        return dialogs.open_feedback(self, poster=poster)

    def open_support(self):
        return dialogs.open_support(self)

    def check_queue(self):
        try:
            count = len(feedback.pending(dialogs.APP_ID))
        except Exception:
            count = 0
        if count and self.queue_bar is None and not self.closing:
            self.queue_bar = dialogs.build_queue_bar(self, count)
            self.queue_bar.pack(side="bottom", fill="x", after=self.status_frame)

    def hide_queue_bar(self):
        if self.queue_bar is not None:
            self.queue_bar.destroy()
            self.queue_bar = None

    def review_queue(self):
        dialogs.review_queue(self, feedback.pending(dialogs.APP_ID))

    def send_queue(self, opener=None):
        self.hide_queue_bar()
        results = queue.Queue()
        kwargs = {"opener": opener} if opener else {}

        def work():
            import time as _time
            results.put(feedback.resend(dialogs.APP_ID, pause=lambda: _time.sleep(2), **kwargs))
        threading.Thread(target=work, daemon=True).start()
        return results

    def maybe_show_prompt(self, converted, cancelled):
        """After a finished run: count it and show the support card when the cadence allows."""
        if converted <= 0 or cancelled or self.closing:
            return
        try:
            self.prompt.record_run(converted)
            if self.prompt.eligible():
                self.show_prompt()
        except Exception:
            pass

    def show_prompt(self, mark=True):
        if self.prompt_card is not None or self.closing:
            return
        self.prompt_card = dialogs.build_prompt_card(self, self.strip_card)
        self.prompt_card.pack(fill="x")
        if mark:
            self.prompt.mark_shown()  # shown, not declined: hides itself after 60 s
        self._prompt_after_id = self.root.after(60000, self.hide_prompt)

    def hide_prompt(self):
        self._cancel_after("_prompt_after_id")
        if self.prompt_card is not None:
            self.prompt_card.destroy()
            self.prompt_card = None

    def prompt_later(self):
        self.hide_prompt()
        self.prompt.decline()

    def prompt_never(self):
        self.hide_prompt()
        self.prompt.stop()
        self._sync_support_box()

    def support_followed(self):
        """Following Star / LinkedIn / X is terminal, as in the web card."""
        self.hide_prompt()
        self.prompt.stop()
        self._sync_support_box()

    def _sync_support_box(self):
        try:
            self.support_var.set(self.prompt.enabled())
        except tk.TclError:
            pass

    def _set_support_suggestions(self):
        self.prompt.set_enabled(self.support_var.get())

    def _on_destroy(self, event):
        if event.widget is not self.root or self._destroyed:
            return
        # A host can destroy the root without going through WM_DELETE_WINDOW.
        # Cancel only our callbacks while its Tcl interpreter is still usable.
        self._destroyed = True
        self.closing = True
        # Release PhotoImages on the Tk thread while the interpreter still exists;
        # otherwise a later garbage collection on a worker thread raises.
        self._images.clear()
        self._cancel_after("_poll_after_id")
        self._cancel_after("_extras_after_id")
        self._cancel_after("_prompt_after_id")
        if self.runner is not None:
            self.runner.cancel()

    def active(self):
        return self.worker is not None and self.worker.is_alive()

    # ----- dialogs ------------------------------------------------------
    def _dialog(self, title):
        top = tk.Toplevel(self.root)
        top.withdraw()
        top.title(title)
        top.transient(self.root)
        top.resizable(False, False)
        top.configure(background=COLORS["bg"])
        self._set_icon(top)
        self._dialogs.append(top)

        def forget(event):
            if event.widget is top and top in self._dialogs:
                self._dialogs.remove(top)
        top.bind("<Destroy>", forget, add="+")
        top.bind("<Escape>", lambda e: top.destroy())
        return top

    def _present(self, top):
        top.update_idletasks()
        try:
            x = self.root.winfo_rootx() + max(0, (self.root.winfo_width() - top.winfo_reqwidth()) // 2)
            y = self.root.winfo_rooty() + max(0, (self.root.winfo_height() - top.winfo_reqheight()) // 3)
            top.geometry(f"+{x}+{y}")
        except tk.TclError:
            pass
        set_titlebar_dark(top, self.theme_name == "dark")
        top.deiconify()

    def _wrap(self):
        return int(460 * self._dpi)

    def open_licence(self):
        """Community licence panel: free, no key, no registration."""
        if self.closing or self._destroyed:
            return
        window = self.licence_window
        if window is not None and window.winfo_exists():
            window.lift()
            window.focus_set()
            return
        top = self.licence_window = self._dialog(self.t("licence_title"))
        body = ttk.Frame(top, padding=20)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=self.t("licence_heading"), style="Title.TLabel").pack(anchor="w")
        ttk.Label(body, text=self.t("licence_text"), wraplength=self._wrap(), justify="left").pack(anchor="w", pady=(10, 0))
        self._build_registration(body, top)
        buttons = ttk.Frame(body, padding=(0, 16, 0, 0))
        buttons.pack(fill="x")
        ok = ttk.Button(buttons, text=self.t("close"), command=top.destroy, style="Accent.TButton")
        ok.pack(side="right")
        ttk.Button(buttons, text=self.t("subscribe"), command=lambda: self._open_url(WEBSITE_URL)).pack(side="right", padx=(0, 8))
        ttk.Button(buttons, text=self.t("eula"), command=self.open_licences_folder, style="Flat.TButton").pack(side="left")
        top.bind("<Return>", lambda e: top.destroy())
        self._present(top)
        ok.focus_set()

    def _build_registration(self, body, top):
        """Optional local e-mail registration; never blocks conversion."""
        frame = ttk.Frame(body)
        frame.pack(fill="x", pady=(14, 0))
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=(0, 10))
        ttk.Label(frame, text=self.t("reg_heading"), style="Section.TLabel", background=COLORS["bg"]).pack(anchor="w")
        top.registration_frame = frame
        self._render_registration(frame, top)

    def _render_registration(self, frame, top, editing=False):
        for child in list(frame.winfo_children())[2:]:
            child.destroy()
        email = self.registered_email()
        if email and not editing:
            top.registration_status = ttk.Label(frame, text=self.t("reg_status", email=email), style="Status.TLabel")
            top.registration_status.pack(anchor="w", pady=(6, 0))
            row = ttk.Frame(frame)
            row.pack(anchor="w", pady=(6, 0))
            top.change_button = ttk.Button(row, text=self.t("reg_change"), command=lambda: self._render_registration(frame, top, True))
            top.change_button.pack(side="left")
            top.reset_button = ttk.Button(row, text=self.t("reg_reset"), style="Flat.TButton",
                                          command=lambda: self.reset_registration(frame, top))
            top.reset_button.pack(side="left", padx=(6, 0))
            return
        ttk.Label(frame, text=self.t("reg_hint"), style="Caption.TLabel", wraplength=self._wrap(), justify="left").pack(anchor="w", pady=(4, 0))
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(6, 0))
        top.email_var = tk.StringVar(value=email or "")
        top.email_entry = ttk.Entry(row, textvariable=top.email_var, width=34)
        top.email_entry.pack(side="left", fill="x", expand=True)
        top.register_button = ttk.Button(row, text=self.t("reg_register"), style="Accent.TButton",
                                         command=lambda: self.register_email(top.email_var.get(), frame, top))
        top.register_button.pack(side="left", padx=(8, 0))
        top.registration_error = ttk.Label(frame, text="", foreground=COLORS["error"], wraplength=self._wrap(), justify="left")
        top.registration_error.pack(anchor="w", pady=(4, 0))
        top.email_entry.bind("<Return>", lambda e: (self.register_email(top.email_var.get(), frame, top), "break")[1])

    def register_email(self, text, frame=None, top=None):
        """Validate and store; inline error on bad input; True when saved."""
        top = top or self.licence_window
        frame = frame or getattr(top, "registration_frame", None)
        if not registration_store.valid_email(text):
            if top is not None and hasattr(top, "registration_error"):
                top.registration_error.configure(text=self.t("reg_invalid"))
            return False
        try:
            self.registration.register(text.strip(), "ifc-excel", product_version())
        except (OSError, ValueError):
            if top is not None and hasattr(top, "registration_error"):
                top.registration_error.configure(text=self.t("reg_failed"))
            return False
        self.refresh_licence_label()
        self.set_status("reg_saved")
        if frame is not None and top is not None and frame.winfo_exists():
            self._render_registration(frame, top)
        return True

    def reset_registration(self, frame=None, top=None):
        top = top or self.licence_window
        frame = frame or getattr(top, "registration_frame", None)
        try:
            self.registration.reset("ifc-excel")
        except OSError:
            pass
        self.refresh_licence_label()
        if frame is not None and top is not None and frame.winfo_exists():
            self._render_registration(frame, top)

    def open_registration(self):
        """Old name of the licence entry point."""
        self.open_licence()

    def open_licences_folder(self):
        folder = licences_dir()
        if folder.is_dir():
            self._startfile(str(folder))
        else:
            self.status.set("licenses/ folder not found")

    def show_about(self):
        if self._about is not None and self._about.winfo_exists():
            self._about.lift()
            return
        top = self._about = self._dialog(self.t("about_title"))
        body = ttk.Frame(top, padding=20)
        body.pack(fill="both", expand=True)
        head = ttk.Frame(body)
        head.pack(fill="x")
        if "logo" in self._images:
            ttk.Label(head, image=self._images["logo"]).pack(side="left", padx=(0, 12))
        titles = ttk.Frame(head)
        titles.pack(side="left")
        ttk.Label(titles, text=PRODUCT, style="Title.TLabel").pack(anchor="w")
        ttk.Label(titles, text=f"{self.t('version')} {product_version()}  |  {self.t('build')} {build_hash()}",
                  style="Caption.TLabel").pack(anchor="w")
        for text in (self.t("about_desc"),):
            ttk.Label(body, text=text, wraplength=self._wrap(), justify="left").pack(anchor="w", pady=(10, 0))
        ttk.Label(body, text=self.t("publisher"), style="Caption.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Label(body, text=self.t("about_edition"), style="Caption.TLabel").pack(anchor="w", pady=(2, 0))
        email = self.registered_email()
        ttk.Label(body, text=self.t("reg_state_yes", email=email) if email else self.t("reg_state_no"),
                  style="Caption.TLabel").pack(anchor="w", pady=(2, 0))
        links = ttk.Frame(body)
        links.pack(anchor="w", pady=(6, 0))
        for key, url in (("website", WEBSITE_URL), ("releases", RELEASES_URL)):
            link = ttk.Label(links, text=self.t(key), style="Link.TLabel", cursor="hand2")
            link.pack(side="left", padx=(0, 16))
            link.bind("<Button-1>", lambda e, u=url: self._open_url(u))
        ttk.Label(body, text=self.t("trademarks"), style="Caption.TLabel", wraplength=self._wrap(),
                  justify="left").pack(anchor="w", pady=(10, 0))
        buttons = ttk.Frame(body, padding=(0, 14, 0, 0))
        buttons.pack(fill="x")
        ok = ttk.Button(buttons, text=self.t("close"), command=top.destroy, style="Accent.TButton")
        ok.pack(side="right")
        ttk.Button(buttons, text=self.t("open_licences"), command=self.open_licences_folder).pack(side="right", padx=(0, 8))
        ttk.Button(buttons, text=self.t("licence"), command=lambda: (top.destroy(), self.open_licence()),
                   style="Flat.TButton").pack(side="left")
        top.bind("<Return>", lambda e: top.destroy())
        self._present(top)
        ok.focus_set()

    def show_error(self, sentence, details, log_path=None, short=None, modal=True):
        """Error modal: one plain sentence, Copy details (technical text), Open log; never a traceback."""
        top = self._dialog(self.t("err_title"))
        body = ttk.Frame(top, padding=20)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=self.t("err_title"), style="Title.TLabel", foreground=COLORS["error"]).pack(anchor="w")
        ttk.Label(body, text=sentence, wraplength=self._wrap(), justify="left").pack(anchor="w", pady=(10, 0))
        if short:
            ttk.Label(body, text=short, style="Caption.TLabel", wraplength=self._wrap(), justify="left").pack(anchor="w", pady=(6, 0))
        buttons = ttk.Frame(body, padding=(0, 16, 0, 0))
        buttons.pack(fill="x")
        ok = ttk.Button(buttons, text=self.t("close"), command=top.destroy, style="Accent.TButton")
        ok.pack(side="right")
        copy = ttk.Button(buttons, text=self.t("copy_details"), command=lambda: self._copy(details))
        copy.pack(side="right", padx=(0, 8))
        if log_path:
            ttk.Button(buttons, text=self.t("open_log"), command=lambda: self._startfile(str(log_path)),
                       style="Flat.TButton").pack(side="left")
        top.bind("<Return>", lambda e: top.destroy())
        self._present(top)
        ok.focus_set()
        if modal:
            try:
                top.grab_set()
                self.root.wait_window(top)
            except tk.TclError:
                pass
        return top

    # ----- commands -----------------------------------------------------
    def add_files(self):
        if self.busy or self.closing:
            return
        names = filedialog.askopenfilenames(
            parent=self.root, title=self.t("choose_files"), initialdir=self.settings.get("input_dir") or None,
            filetypes=[("IFC models (*.ifc, *.ifczip)", "*.ifc *.ifczip"), ("IFC STEP", "*.ifc"), ("IFCZIP archives", "*.ifczip")])
        if names:
            self.settings.save(input_dir=os.path.dirname(names[0]))
        self._add_paths(names)

    def add_folder(self):
        if self.busy or self.closing:
            return
        folder = filedialog.askdirectory(parent=self.root, title=self.t("choose_folder"), initialdir=self.settings.get("input_dir") or None)
        if not folder:
            return
        self.settings.save(input_dir=folder)
        if not self._add_paths(self._scan(folder)):
            self.set_status("no_ifc")

    def remove_selected(self):
        if self.busy or self.closing:
            return
        selection = self.tree.selection()
        if not selection:
            return
        index = int(selection[0])
        self._remove_index(index)

    def _remove_index(self, index):
        self._rebuild([i for i in range(len(self.files)) if i != index])
        children = self.tree.get_children()
        if children:
            target = str(min(index, len(children) - 1))
            self.tree.selection_set(target)
            self.tree.focus(target)
        self.status.set(self._files_in_list() if self.files else self.t("ready"))

    def clear_files(self):
        if self.busy or self.closing:
            return
        self.tree.delete(*self.tree.get_children())
        self.files.clear()
        self._keys.clear()
        self.results.clear()
        self.log_lines.clear()
        self._hide_summary()
        self._refresh_empty()
        self.show_details()
        self.progress.configure(value=0)
        self.progress_text.set("")
        self.status.set(self.t("ready"))

    def choose_output(self):
        if self.busy or self.closing:
            return
        path = filedialog.askdirectory(parent=self.root, title=self.t("output_folder"), initialdir=self.output.get() or None)
        if path:
            self.output.set(os.path.normpath(path))
            self.settings.save(output=self.output.get())

    def _output_target(self):
        """Explicit folder, or a callable resolving 'next to the input file'."""
        text = self.output.get().strip()
        if text:
            return text
        return lambda source: str(Path(source).resolve().parent / "IFC to Excel")

    def _accepted_results(self):
        return [r for _, r in sorted(self.results.items()) if r.get("status") == "CONVERTED_WITH_LIMITS"]

    def output_folder_for_open(self):
        text = self.output.get().strip()
        if text:
            return text
        accepted = self._accepted_results()
        if accepted and accepted[0].get("folder"):
            return str(Path(accepted[0]["folder"]).parent.parent)
        return ""

    def open_output_folder(self):
        folder = self.output_folder_for_open()
        if not folder:
            return
        if not os.path.isdir(folder):
            self.status.set("Output folder does not exist yet")
            return
        self._startfile(folder)

    def open_logs_folder(self):
        folder = logs_dir()
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        self._startfile(str(folder))

    def viewer_available(self):
        import viewer_support
        return data_viewer_exe() is not None or viewer_support.viewer_index() is not None

    def open_in_viewer(self):
        exe = data_viewer_exe()
        if exe is not None:
            targets = [r["workbook"] for r in self._accepted_results() if r.get("workbook")]
            if not targets:
                return
            try:
                import subprocess
                flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                subprocess.Popen([str(exe), *targets], cwd=str(exe.parent), close_fds=True, creationflags=flags)
                self.set_status("open_viewer")
            except OSError as exc:
                messagebox.showerror("Cannot open", str(exc), parent=self.root)
            return
        if not self.tree.selection():
            for index, result in sorted(self.results.items()):
                if result.get("status") == "CONVERTED_WITH_LIMITS":
                    self.tree.selection_set(str(index))
                    break
        self.viewer_button.click()

    def report_text(self):
        counts = self._counts()
        lines = [f"{PRODUCT} {product_version()}", time.strftime("%Y-%m-%d %H:%M:%S"),
                 f"{self.t('converted')}: {counts['converted']}, {self.t('skipped')}: {counts['skipped']}, "
                 f"{self.t('failed')}: {counts['failed']}, {self.t('total_time')}: {format_elapsed(self._finished_seconds)}", ""]
        for index, source in enumerate(self.files):
            result = self.results.get(index) or {}
            word = self.t(STATUS_WORDS.get(result.get("status", "QUEUED"), ("st_queued", ""))[0])
            lines.append(f"{source}: {word}" + (f" -> {result['workbook']}" if result.get("workbook") else "")
                         + (f" ({result['message'].strip().splitlines()[0]})" if result.get("status") == "FAILED" and result.get("message") else ""))
        return "\n".join(lines)

    def copy_report(self):
        self._copy(self.report_text())

    def run(self):
        if self.busy or self.closing:
            return
        if not self.files:
            messagebox.showwarning(self.t("nothing_title"), self.t("nothing_text"), parent=self.root)
            return
        import batch
        explicit = self.output.get().strip()
        if explicit:
            self.busy = True  # Ignore repeated clicks while the output folder is checked.
            try:
                problem = batch.check_output_folder(explicit)
            finally:
                self.busy = False
            if problem:
                self.set_status("cannot_write")
                messagebox.showerror(self.t("cannot_write"), problem, parent=self.root)
                return
        self._hide_summary()
        self.hide_prompt()
        self.settings.save(output=explicit)
        self.results.clear()
        self.log_lines.clear()
        self.show_details()
        for i, name in enumerate(self.files):
            self._set_row(i, name, "QUEUED")
        self._started_at = time.monotonic()
        self.set_busy(True)
        self._show_progress()
        self._progress(0)
        try:
            # The worker closes over plain objects only, never ``self``: if it
            # held the last App reference, Tk variables/images would be
            # finalised on the worker thread, which corrupts Tcl state.
            results = []
            events = self.events
            def notify(event):
                if event["event"] == "result":
                    results.append(event)
                if event["event"] != "finished":
                    events.put(event)
            runner = self.runner = BatchRunner(notify)
            sources, output = tuple(self.files), self._output_target()
            def work():
                failure = None
                try:
                    runner.run(sources, output)
                except Exception as exc:
                    failure = f"Conversion stopped unexpectedly: {type(exc).__name__}: {exc}"
                finally:
                    events.put({"event": "finished", "results": results, "failure": failure})
            self.worker = threading.Thread(target=work, daemon=False)
            self.worker.start()
        except (RuntimeError, OSError) as exc:
            self.worker = None
            self.runner = None
            self.set_busy(False)
            self.status.set("Could not start conversion")
            messagebox.showerror("Could not start conversion", str(exc), parent=self.root)

    def set_busy(self, busy):
        self.busy = busy
        for control in (self.add, self.add_folder_button, self.remove_button, self.clear, self.start,
                        self.browse, self.output_entry):
            control.configure(state="disabled" if busy else "normal")
        self.cancel_button.configure(state="normal" if busy else "disabled")
        try:
            self.drop.configure(cursor="arrow" if busy else "hand2")
        except tk.TclError:
            pass

    def _update_progress_text(self):
        if not self.files or (self._started_at is None and not self.results):
            self.progress_text.set("")
            return
        total = len(self.files)
        done = len(self.results)
        elapsed = (time.monotonic() - self._started_at) if (self.busy and self._started_at) else self._finished_seconds
        name = ""
        if self.busy:
            running = [i for i in range(total) if i not in self.results]
            if running:
                name = self.t("converting", name=Path(self.files[running[0]]).name) + "  |  "
        self.progress_text.set(f"{name}{self.t('progress_of', n=done, total=total)}  |  {self.t('elapsed', t=format_elapsed(elapsed))}")

    def _progress(self, finished):
        total = max(1, len(self.files))
        self.progress.configure(maximum=total, value=finished)
        self._update_progress_text()

    def cancel(self):
        if self.runner:
            self.runner.cancel()
            if self._destroyed:
                return
            self.cancel_button.configure(state="disabled")
            self.status.set("Cancelling…")

    def _log(self, line):
        self.log_lines.append(line)
        if not self.tree.selection():
            self.show_details()

    def poll(self):
        if self._destroyed:
            return
        # Tests/hosts may also pump poll explicitly. Keep one owned timer,
        # rather than leaving the previous scheduled invocation behind.
        self._cancel_after("_poll_after_id")
        try:
            while True:
                event = self.events.get_nowait()
                if event["event"] == "started":
                    self._set_row(event["index"], event["source"], "RUNNING")
                    self.set_status("converting", name=Path(event["source"]).name)
                    self._log(f"{Path(event['source']).name}: {self.t('st_running')}")
                    self._update_progress_text()
                elif event["event"] == "result":
                    self.results[event["index"]] = event
                    self._set_row(event["index"], event["source"], event["status"], event)
                    word = self.t(STATUS_WORDS.get(event["status"], ("st_queued", ""))[0])
                    detail = ""
                    if event["status"] == "FAILED" and event.get("message"):
                        detail = " - " + event["message"].strip().splitlines()[0][:200]
                    self._log(f"{Path(event['source']).name}: {word}{detail}")
                    self._progress(len(self.results))
                    self.show_details()
                elif event["event"] == "finished":
                    self._finished(event)
        except queue.Empty:
            pass
        if self.busy:
            clock = format_elapsed(time.monotonic() - self._started_at) if self._started_at else ""
            if clock != self._last_clock:
                self._last_clock = clock
                self._update_progress_text()
        if self.closing and not self.active():
            self.root.destroy()
            return
        self._poll_after_id = self.root.after(100, self.poll)

    def _counts(self):
        converted = sum(r["status"] == "CONVERTED_WITH_LIMITS" for r in self.results.values())
        failed = sum(r["status"] == "FAILED" for r in self.results.values())
        skipped = sum(r["status"] in ("CANCELLED", "NOT_STARTED") for r in self.results.values())
        return {"converted": converted, "failed": failed, "skipped": skipped}

    def _hide_summary(self):
        self.hide_prompt()
        if self.strip.winfo_manager():
            self.strip.pack_forget()
        for box in (self.progress_box, self.summary_frame):
            if box.winfo_manager():
                box.pack_forget()

    def _show_progress(self):
        if self.summary_frame.winfo_manager():
            self.summary_frame.pack_forget()
        self.progress_box.pack(fill="x")
        if not self.strip.winfo_manager():
            self.strip.pack(side="bottom", fill="x", after=self.actions_frame)

    def _update_summary(self):
        counts = self._counts()
        self.summary_done.configure(text="✓ " + self.t("done"))
        self.summary_text.set("  |  ".join((self.t("n_converted", n=counts["converted"]), self.t("n_skipped", n=counts["skipped"]),
                                            self.t("n_failed", n=counts["failed"]), format_elapsed(self._finished_seconds))))

    def _show_summary(self):
        self._update_summary()
        if self.viewer_available() and self._accepted_results():
            if not self.open_viewer_button.winfo_manager():
                self.open_viewer_button.pack(side="right", padx=(0, 6), before=self.open_output_link)
        else:
            self.open_viewer_button.pack_forget()
        self.open_output_link.configure(state="normal" if self._accepted_results() else "disabled")
        self.open_viewer_button.configure(
            text=self.t("open_viewer" if data_viewer_exe() is not None else "open_viewer_browser"))
        if self.progress_box.winfo_manager():
            self.progress_box.pack_forget()
        self.summary_frame.pack(fill="x")
        if not self.strip.winfo_manager():
            self.strip.pack(side="bottom", fill="x", after=self.actions_frame)

    def _finished(self, event):
        self.set_busy(False)
        if self._started_at is not None:
            self._finished_seconds = time.monotonic() - self._started_at
        results = event["results"]
        for index, source in enumerate(self.files):
            if index not in self.results:
                self.results[index] = {"source": source, "status": "FAILED", "message": event.get("failure") or "Conversion ended without a result. You can retry this file."}
                self._set_row(index, source, "FAILED", self.results[index])
        self._progress(len(self.files))
        self.show_details()
        total = len(self.files)
        written = sum(r["status"] == "CONVERTED_WITH_LIMITS" for r in results)
        if written == total:
            self.set_status("status_done", written=written, total=total)
        else:
            self.set_status("status_finished", written=written, total=total, rest=total - written)
        if event.get("failure"):
            self.status.set(self.status.get() + ". " + event["failure"])
        if not self.closing:
            self._show_summary()
            cancelled = bool(event.get("cancel_requested")) or any(r["status"] == "CANCELLED" for r in self.results.values())
            self.maybe_show_prompt(self._counts()["converted"], cancelled)
            if self._counts()["failed"]:
                self.toggle_log(True)
        if self.closing:
            return
        accepted = [r for r in self.results.values() if r["status"] == "CONVERTED_WITH_LIMITS"]
        if self.options["open_single_workbook"].get() and total == 1 and accepted and accepted[0].get("workbook"):
            self._startfile(accepted[0]["workbook"])
        elif self.options["open_folder_when_done"].get() and accepted:
            self.open_output_folder()
        if not self.options["keep_finished"].get() and accepted:
            self._rebuild([i for i in range(total) if self.results.get(i, {}).get("status") != "CONVERTED_WITH_LIMITS"])

    # ----- selection, details, context menu -----------------------------
    def selected(self):
        selection = self.tree.selection()
        return self.results.get(int(selection[0])) if selection else None

    def _selected_source(self):
        selection = self.tree.selection()
        if not selection:
            return None
        index = int(selection[0])
        return self.files[index] if index < len(self.files) else None

    def details_text(self, result):
        if not result:
            return ""
        key = STATUS_WORDS.get(result["status"], (None, ""))[0]
        word = self.t(key) if key else result["status"]
        lines = [f"{Path(result.get('source', '')).name}: {word} ({result['status']})"]
        if result.get("message"):
            lines.append(result["message"])
        lines.extend(result.get("limitations", []))
        if result.get("source"):
            lines.append("Source: " + result["source"])
        if result.get("workbook"):
            lines.append("Workbook: " + result["workbook"])
        return "\n".join(lines)

    def show_details(self, event=None):
        result = self.selected()
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        if result:
            self.details.insert("1.0", self.details_text(result), ("error",) if result["status"] == "FAILED" else ())
        elif self.log_lines:
            self.details.insert("1.0", "\n".join(self.log_lines))
            self.details.see("end")
        else:
            self.details.insert("1.0", self.t("select_hint"), ("muted",))
        self.details.configure(state="disabled")
        for key, button in (("workbook", self.open_workbook_button), ("folder", self.open_folder_button)):
            available = result and result["status"] == "CONVERTED_WITH_LIMITS" and result.get(key)
            button.configure(state="normal" if available else "disabled")
        self.copy_details_button.configure(state="normal" if result else "disabled")
        if result and result["status"] == "FAILED":
            self.toggle_log(True)

    def copy_details(self):
        result = self.selected()
        if result:
            self._copy(self.details_text(result))

    def copy_path(self):
        source = self._selected_source()
        if source:
            self._copy(source)

    def _on_click(self, event):
        """Last column: remove (x). Result column of a failed row: Details modal."""
        if self.tree.identify_region(event.x, event.y) != "cell":
            return None
        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if column == "#4" and row:
            result = self.results.get(int(row))
            if result and result.get("status") == "FAILED" and result.get("message"):
                self.tree.selection_set(row)
                self.show_result_error(result)
                return "break"
        if column != "#5":
            return None
        if row and not self.busy and not self.closing:
            self._remove_index(int(row))
            return "break"
        return None

    def show_result_error(self, result, modal=True):
        """Plain sentence in the modal; technical text behind Copy details."""
        sentence = (result.get("message") or "").strip().splitlines()[0] if result.get("message") else self.t("err_sentence")
        return self.show_error(sentence, self.details_text(result), logs_dir(), modal=modal)

    def _on_double_click(self, event):
        row = self.tree.identify_row(event.y)
        if not row:
            if not self.files:
                self.add_files()
            return
        self.tree.selection_set(row)
        result = self.results.get(int(row))
        if result and result["status"] == "CONVERTED_WITH_LIMITS" and result.get("workbook"):
            self.open_workbook()

    def _on_right_click(self, event):
        row = self.tree.identify_row(event.y)
        if not row:
            return
        self.tree.selection_set(row)
        self.tree.focus(row)
        self._popup(event.x_root, event.y_root)

    def _on_menu_key(self, event):
        focus = self.tree.focus()
        if focus:
            box = self.tree.bbox(focus) or (0, 0, 0, 0)
            self._popup(self.tree.winfo_rootx() + 20, self.tree.winfo_rooty() + box[1] + box[3])

    def _popup(self, x, y):
        result = self.selected()
        ok = bool(result and result["status"] == "CONVERTED_WITH_LIMITS")
        menu = self.context_menu
        menu.entryconfigure("Open file", state="normal" if ok and result.get("workbook") else "disabled")
        menu.entryconfigure("Open folder", state="normal" if ok and result.get("folder") else "disabled")
        menu.entryconfigure("Copy details", state="normal" if result else "disabled")
        menu.entryconfigure("Remove", state="disabled" if self.busy else "normal")
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def resize_labels(self, event):
        """Kept for host compatibility; the status bar no longer wraps."""

    def open_result(self, key):
        result = self.selected()
        if not result or result["status"] != "CONVERTED_WITH_LIMITS" or not result.get(key):
            messagebox.showinfo("No result", "Select a converted file.", parent=self.root)
            return
        try:
            os.startfile(result[key])
        except OSError as exc:
            messagebox.showerror("Cannot open result", str(exc), parent=self.root)

    def open_workbook(self):
        self.open_result("workbook")

    def open_folder(self):
        self.open_result("folder")

    def request_close(self):
        """Window close button: ask before stopping a running conversion."""
        if self.active() and not self.closing:
            if not messagebox.askyesno(self.t("running_title"), self.t("running_text"),
                                       icon="warning", default="no", parent=self.root):
                return
        self.close()

    def report_exception(self, kind, value, trace):
        """Tk callback errors: one plain sentence, Copy details, full text in the log file."""
        import traceback
        details = "".join(traceback.format_exception(kind, value, trace))
        log = logs_dir() / "gui-errors.log"
        try:
            log.parent.mkdir(parents=True, exist_ok=True)
            with open(log, "a", encoding="utf-8") as handle:
                handle.write(details + "\n")
        except OSError:
            log = None
        try:
            self.status.set("Unexpected error; details copied to the log" if log else "Unexpected error")
            self.show_error(self.t("err_sentence"), details, log, short=f"{type(value).__name__}: {value}")
        except tk.TclError:
            pass

    def close(self):
        if self._destroyed:
            return
        try:
            if self.root.state() == "normal" and not self.closing:
                self.settings.save(geometry=self.root.geometry())
        except tk.TclError:
            pass
        self.closing = True
        for dialog in list(self._dialogs):
            try:
                dialog.destroy()
            except tk.TclError:
                pass
        if self.active():
            self.set_busy(True)
            self.cancel()
        else:
            self.root.destroy()


def enable_file_drop(app):
    """Accept files dropped from Explorer (Win32 WM_DROPFILES; no third-party code)."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes
        user32, shell32 = ctypes.windll.user32, ctypes.windll.shell32
        hwnd = user32.GetParent(app.root.winfo_id())
        WM_DROPFILES, GWLP_WNDPROC = 0x0233, -4
        LRESULT = ctypes.c_ssize_t
        WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        user32.CallWindowProcW.restype = LRESULT
        user32.CallWindowProcW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        setter = getattr(user32, "SetWindowLongPtrW", None) or user32.SetWindowLongW
        setter.restype = ctypes.c_void_p
        setter.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
        shell32.DragQueryFileW.argtypes = [ctypes.c_void_p, wintypes.UINT, ctypes.c_wchar_p, wintypes.UINT]
        shell32.DragFinish.argtypes = [ctypes.c_void_p]

        def procedure(window, message, wparam, lparam):
            if message == WM_DROPFILES:
                count = shell32.DragQueryFileW(wparam, 0xFFFFFFFF, None, 0)
                paths = []
                for i in range(count):
                    length = shell32.DragQueryFileW(wparam, i, None, 0) + 1
                    buffer = ctypes.create_unicode_buffer(length)
                    shell32.DragQueryFileW(wparam, i, buffer, length)
                    paths.append(buffer.value)
                shell32.DragFinish(wparam)
                app.root.after(0, lambda: app.drop_files(paths))
                return 0
            return user32.CallWindowProcW(previous, window, message, wparam, lparam)

        callback = WNDPROC(procedure)
        previous = setter(hwnd, GWLP_WNDPROC, ctypes.cast(callback, ctypes.c_void_p))
        shell32.DragAcceptFiles(hwnd, True)
        app._drop_callback = callback  # Keep the thunk alive for the window's lifetime.
        return True
    except Exception:
        return False


def create_root(attempts=3):
    """Tk start-up can fail transiently while Tcl reads its library; retry briefly."""
    import time as _time
    for attempt in range(attempts):
        try:
            return tk.Tk()
        except tk.TclError:
            if attempt + 1 >= attempts:
                raise
            _time.sleep(0.25 * (attempt + 1))


def startup_failure(exc):
    """Last-resort report for pythonw (no console): log file plus a plain message box."""
    import traceback
    log = logs_dir() / "startup-errors.log"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as handle:
            handle.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)) + "\n")
        where = f"\n\nDetails were written to:\n{log}"
    except OSError:
        where = ""
    text = f"{PRODUCT} could not start.\n\n{type(exc).__name__}: {exc}{where}"
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, text, PRODUCT, 0x10)
    except Exception:
        print(text, file=sys.stderr)
    return text


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    import cli_usage
    code = cli_usage.run(argv)  # --help and headless conversion never open a window
    if code is not None:
        return code
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    try:
        root = create_root()
        app = App(root, settings=Settings(app_data_dir() / "settings.json"))
    except Exception as exc:
        startup_failure(exc)
        return 1
    root.report_callback_exception = app.report_exception
    root.update_idletasks()
    enable_file_drop(app)
    preload = [a for a in argv if not a.startswith("-")]
    if preload:
        root.after(200, lambda: app.drop_files(preload))
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
