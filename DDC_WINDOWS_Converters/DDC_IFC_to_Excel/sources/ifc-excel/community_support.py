"""Development desktop Community adapter; no browser or counter in the parser CLI."""
import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import threading


_LOAD_LOCK = threading.RLock()


class CommunitySupport:
    _PACKAGE_ALIAS = "_ddc_ifc_community_pilot"

    def __init__(self, *, db_path=None, coordinator=None):
        self.db_path = db_path
        self._ui = None
        if coordinator is not None and (
            getattr(coordinator, "product_id", None) != "ifc-excel"
            or not callable(getattr(coordinator, "get_access", None))
            or not callable(getattr(coordinator, "activate", None))
            or not callable(getattr(coordinator, "renew", None))
        ):
            raise ValueError("An explicitly configured IFC license coordinator is required")
        self._coordinator = coordinator

    def _load(self):
        with _LOAD_LOCK:
            return self._load_locked()

    def _load_locked(self, *, registration=False):
        if self._ui is None or registration:
            # Load only the reviewed sibling tree, isolated from ambient
            # site-packages, current-directory imports, sys.path order and the
            # generic ``ddc_licensing`` module cache. Packaged builds must pin
            # and verify their vendored copy before constructing this adapter.
            source_root = Path(__file__).resolve().parent.parent
            sibling = (source_root / "licensing").resolve()
            package_dir = (sibling / "ddc_licensing").resolve()
            init_path = package_dir / "__init__.py"
            if not init_path.is_file() or sibling.parent != source_root or package_dir.parent != sibling:
                raise ImportError("Reviewed sibling DDC licensing package is missing or outside sources")

            alias = self._PACKAGE_ALIAS
            sources = {
                alias: init_path,
                alias + ".community": package_dir / "community.py",
                alias + ".presentation": package_dir / "presentation.py",
                alias + ".community_ui": package_dir / "community_ui.py",
            }
            optional = {
                alias + ".registration": package_dir / "registration.py",
                alias + ".activation_ui": package_dir / "activation_ui.py",
            }
            known_sources = {**sources, **optional}
            if registration:
                sources.update(optional)
            unexpected = [name for name in sys.modules
                          if (name == alias or name.startswith(alias + ".")) and name not in known_sources]
            if unexpected:
                raise ImportError(f"Unexpected cached module occupies the private DDC namespace: {unexpected[0]}")
            for name, path in known_sources.items():
                if name not in sources and name not in sys.modules:
                    continue  # Conversion alone does not import the optional Tk view.
                if not path.is_file():
                    raise ImportError(f"Reviewed sibling module is missing: {path.name}")
                cached = sys.modules.get(name)
                if cached is not None and Path(getattr(cached, "__file__", "")).resolve() != path.resolve():
                    raise ImportError(f"Conflicting module already occupies the private DDC namespace: {name}")
                if name == alias and cached is not None:
                    cached_locations = [Path(item).resolve() for item in getattr(cached, "__path__", ())]
                    if cached_locations != [package_dir]:
                        raise ImportError("Conflicting package search path already occupies the private DDC namespace")

            created = []
            try:
                for name, path in sources.items():
                    if name in sys.modules:
                        continue
                    is_package = name == alias
                    spec = importlib.util.spec_from_file_location(
                        name,
                        path,
                        submodule_search_locations=[str(package_dir)] if is_package else None,
                    )
                    if spec is None or spec.loader is None:
                        raise ImportError(f"Cannot load reviewed sibling module: {path.name}")
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[name] = module
                    created.append(name)
                    spec.loader.exec_module(module)
            except Exception:
                for name in reversed(created):
                    sys.modules.pop(name, None)
                raise

            ui_module = sys.modules[alias + ".community_ui"]
            expected_ui = sources[alias + ".community_ui"]
            if Path(getattr(ui_module, "__file__", "")).resolve() != expected_ui.resolve():
                raise ImportError("Community UI did not load from the reviewed sibling package")
            CommunityUI = ui_module.CommunityUI
            if self._ui is None:
                self._ui = CommunityUI("ifc-excel", db_path=self.db_path,
                                       coordinator=self._coordinator)
            if registration:
                return sys.modules[alias + ".activation_ui"]
        return self._ui

    def registration_dialog(self, parent, *, language="en"):
        """Use the same explicitly injected coordinator as the accounting path.

        Default construction stays unconfigured; opening a view creates no
        issuer, device key, network transport or trusted-time provider.
        """
        with _LOAD_LOCK:
            module = self._load_locked(registration=True)
        controller_module = sys.modules[self._PACKAGE_ALIAS + ".registration"]
        controller = controller_module.RegistrationController(self._coordinator)
        return module.ActivationDialog(parent, controller=controller, language=language)

    def accepted(self, result):
        """BatchRunner calls only after all receipt/output checks have passed."""
        if result.get("status") != "CONVERTED_WITH_LIMITS":
            return {"edition": "community", "ad_pending": False, "counted": False}
        folder = os.path.normcase(str(Path(result["folder"]).resolve()))
        operation = hashlib.sha256(("ddc-ifc-operation-v1\0" + folder).encode("utf-8")).hexdigest()
        return self._load().accepted(operation)

    def launch_one_pending(self, *, opener=None):
        return self._load().launch_one_pending(opener=opener)
