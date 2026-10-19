"""Trusted advertising targets. Opening a browser is an explicit UI responsibility."""
from pathlib import Path
from urllib.parse import urlsplit


def local_community_page():
    """Return only the bundled, offline page; no input-derived or network URL."""
    return (Path(__file__).parent / "assets" / "community.html").resolve(strict=True).as_uri()


def approved_https_page(url, *, allowed_hosts):
    """Validate an operator-configured destination; never accept model/receipt text."""
    if not isinstance(url, str) or len(url) > 2048 or any(ord(c) <= 32 or ord(c) == 127 for c in url):
        raise ValueError("Invalid advertising URL")
    if "\\" in url:
        raise ValueError("Backslashes are not allowed in advertising URLs")
    parsed = urlsplit(url)
    hosts = frozenset(h.lower() for h in allowed_hosts)
    if (parsed.scheme != "https" or not parsed.hostname or
            parsed.hostname.lower() not in hosts or parsed.username is not None or
            parsed.password is not None or parsed.port not in (None, 443) or parsed.fragment):
        raise ValueError("Advertising URL must be HTTPS on an approved host")
    # Return the configured URL unchanged. No project identifiers or tracking parameters added.
    return url
