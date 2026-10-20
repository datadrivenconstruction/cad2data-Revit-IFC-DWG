"""Optional Community registration kept on this computer only (no server, works offline).

One file shared by every DDC app: %APPDATA%/DataDrivenConstruction/registration.json
    {"email": "...", "registered_at": "<UTC ISO>", "products": ["ifc-excel", ...], "versions": {"ifc-excel": "2.0.0"}}
Registering in one app shows in the others. Unknown keys are preserved; damaged or foreign files
(for example an old licence file) read as "not registered" and never raise.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time

EMAIL = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")


def default_path():
    forced = os.environ.get("DDC_REGISTRATION_PATH")
    if forced:
        return Path(forced)
    base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(base) / "DataDrivenConstruction" / "registration.json"


def valid_email(text):
    text = (text or "").strip()
    return 3 <= len(text) <= 254 and ".." not in text and bool(EMAIL.match(text)) and len(text.split("@")[0]) <= 64


class RegistrationStore:
    def __init__(self, path=None):
        self.path = Path(path) if path else default_path()

    MAX_BYTES = 64 * 1024

    def _read(self):
        try:
            if self.path.stat().st_size > self.MAX_BYTES:
                return {}
            data = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def load(self):
        """Registration dict (email, registered_at, products, ...) or None."""
        data = self._read()
        email = data.get("email")
        if not isinstance(email, str) or not valid_email(email):
            return None
        products = data.get("products")
        data["products"] = [p for p in products if isinstance(p, str)] if isinstance(products, list) else []
        if not isinstance(data.get("registered_at"), str):
            data["registered_at"] = ""
        return data

    def email(self):
        data = self.load()
        return data["email"] if data else None

    def _write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(self.path.name + ".tmp")
        temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temporary, self.path)

    def register(self, email, product, version):
        """Store the address; raises ValueError for a bad address, OSError if the disk refuses."""
        email = (email or "").strip()
        if not valid_email(email):
            raise ValueError("invalid e-mail")
        current = self._read()
        keep = {k: v for k, v in current.items() if k not in ("email", "registered_at", "products", "versions")}
        previous = self.load()
        same = previous is not None and previous["email"].lower() == email.lower()
        products = list(previous["products"]) if same else []
        if product not in products:
            products.append(product)
        versions = current.get("versions") if same and isinstance(current.get("versions"), dict) else {}
        versions = {**versions, product: version}
        data = {**keep, "email": email,
                "registered_at": previous["registered_at"] if same and previous["registered_at"]
                else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "products": products, "versions": versions}
        self._write(data)
        return data

    def reset(self, product=None):
        """Forget this product's registration. Other apps keep theirs; when none is left the file is moved aside
        as registration.previous.json (nothing is deleted)."""
        if not self.path.exists():
            return
        data = self._read()
        products = data.get("products") if isinstance(data.get("products"), list) else []
        rest = [p for p in products if p != product] if product else []
        if rest and data.get("email"):
            versions = data.get("versions") if isinstance(data.get("versions"), dict) else {}
            data["products"] = rest
            data["versions"] = {k: v for k, v in versions.items() if k != product}
            try:
                self._write(data)
            except OSError:
                pass
            return
        backup = self.path.with_name("registration.previous.json")
        try:
            os.replace(self.path, backup)
        except OSError:
            pass
