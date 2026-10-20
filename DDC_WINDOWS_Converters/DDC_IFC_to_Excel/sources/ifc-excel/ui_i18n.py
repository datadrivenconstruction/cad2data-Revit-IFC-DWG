"""UI strings in 15 languages (owner order). English is the fallback.

Translations live in ``locales/<code>.json`` (one flat key -> text object per language, same keys as ``en.json``).
``S[key][code]`` is built from those files, so ``tr()`` and the tests keep the original shape.
"""
import json
import locale
import os

LANGUAGES = ("en", "de", "es", "fr", "ru", "pt", "it", "zh", "ja", "ko", "pl", "tr", "nl", "cs", "uk")
LANGUAGE_NAMES = {"en": "English", "de": "Deutsch", "es": "Español", "fr": "Français", "ru": "Русский",
                  "pt": "Português", "it": "Italiano", "zh": "中文(简体)", "ja": "日本語", "ko": "한국어",
                  "pl": "Polski", "tr": "Türkçe", "nl": "Nederlands", "cs": "Čeština", "uk": "Українська"}
# Windows primary language ids (LANGID & 0x3FF) -> code
_LANGID = {0x09: "en", 0x07: "de", 0x0A: "es", 0x0C: "fr", 0x19: "ru", 0x16: "pt", 0x10: "it", 0x04: "zh",
           0x11: "ja", 0x12: "ko", 0x15: "pl", 0x1F: "tr", 0x13: "nl", 0x05: "cs", 0x22: "uk"}
_NAMES = {"english": "en", "german": "de", "spanish": "es", "french": "fr", "russian": "ru", "portuguese": "pt",
          "italian": "it", "chinese": "zh", "japanese": "ja", "korean": "ko", "polish": "pl", "turkish": "tr",
          "dutch": "nl", "czech": "cs", "ukrainian": "uk"}

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")


def _load(code):
    with open(os.path.join(_DIR, code + ".json"), encoding="utf-8") as handle:
        return json.load(handle)


_CATALOGS = {code: _load(code) for code in LANGUAGES}
S = {key: {code: _CATALOGS[code].get(key, text) for code in LANGUAGES} for key, text in _CATALOGS["en"].items()}


def system_language():
    """The OS UI language when it is one of LANGUAGES, otherwise English."""
    forced = os.environ.get("DDC_UI_LANG", "").lower()
    if forced in LANGUAGES:
        return forced
    try:
        if os.name == "nt":  # the Windows display language wins over the regional format
            import ctypes
            code = _LANGID.get(ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF)
            if code:
                return code
        name = (locale.getlocale()[0] or "") or os.environ.get("LANG", "")
        lowered = name.lower()
        for code in LANGUAGES:
            if lowered.startswith(code):
                return code
        for word, code in _NAMES.items():
            if lowered.startswith(word):
                return code
    except Exception:
        pass
    return "en"


def tr(language, key, **values):
    entry = S.get(key)
    if entry is None:
        return key
    text = entry.get(language) or entry["en"]
    return text.format(**values) if values else text
