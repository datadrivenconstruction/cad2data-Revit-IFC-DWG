"""Design tokens (DESIGN_SPEC 2026-10) and OS light/dark detection."""
import sys

# Reference: RVT Converter Desktop (Theme.cs), DESIGN_SPEC "Reference" section.
LIGHT = {
    "bg": "#F3F3F3", "surface": "#FFFFFF", "field": "#FFFFFF", "border": "#D0D0D0", "text": "#1F1F1F", "muted": "#5F6368",
    "accent": "#175DAB", "accent-hover": "#124C8C", "accent-ink": "#175DAB", "on-accent": "#FFFFFF",
    "hover": "#E8E8E8", "pressed": "#DADADA", "selected": "#CCE0F5", "badge": "#EBEBEB",
    "success": "#1E7B45", "success-bg": "#E3F1E8", "warning": "#A65F00", "warning-bg": "#FBF0DC",
    "error": "#B3261E", "error-bg": "#F9E3E1",
}
DARK = {
    "bg": "#202020", "surface": "#2B2B2B", "field": "#1F1F1F", "border": "#404040", "text": "#F0F0F0", "muted": "#A8A8A8",
    "accent": "#175DAB", "accent-hover": "#2A6EBB", "accent-ink": "#7EB0E8", "on-accent": "#FFFFFF",
    "hover": "#383838", "pressed": "#454545", "selected": "#1E3F64", "badge": "#3A3A3A",
    "success": "#6CC48F", "success-bg": "#1E3A29", "warning": "#E8B661", "warning-bg": "#43361C",
    "error": "#F2A49D", "error-bg": "#4A2522",
}
MODES = ("auto", "light", "dark")


def os_uses_dark():
    """Windows 'Apps use light theme' registry flag; any failure means light."""
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
            return winreg.QueryValueEx(key, "AppsUseLightTheme")[0] == 0
    except Exception:
        return False


def resolve(mode):
    """Return (name, tokens) for a preference of auto / light / dark."""
    name = mode if mode in ("light", "dark") else ("dark" if os_uses_dark() else "light")
    return name, dict(DARK if name == "dark" else LIGHT)


def contrast(foreground, background):
    """WCAG contrast ratio of two #RRGGBB colours."""
    def lum(colour):
        channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    a, b = sorted((lum(foreground), lum(background)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def font_family(root):
    from tkinter import font as tkfont
    families = set(tkfont.families(root))
    for name in ("Segoe UI Variable Text", "Segoe UI Variable", "Segoe UI"):
        if name in families:
            return name
    return "TkDefaultFont"
