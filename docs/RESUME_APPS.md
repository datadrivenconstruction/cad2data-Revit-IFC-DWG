# RESUME: DDC Windows apps 2.0 (ui-refresh-2026-10), saved 2026-10-21 before reboot

Target: release v2026.10.1 (Linux/macOS already there). Publish only after E2E of the installed app is all OK.
Licence fixes: rvt_export/legal/RELEASE_2026.10.1_BUILD_FIXES.md. Specs: docs/ui-refresh-2026-10/DESIGN_SPEC.md,
rvt_export/legal/BRANCH_EDITS_FOR_OTHER_AGENTS.md (Support prompt, Registration lock, Licence change, Rename).

## State
- CAD Drawing to Excel 2.0.0 (sources/dwg-excel, master b5a2cc8): all code merged (UI, lock, support prompt, licence audit).
  Build was running at reboot -> rerun tools/build_release.py + packaging/build_installers.py (Inno: %LOCALAPPDATA%/Programs/Inno Setup 6/ISCC.exe),
  inject app key from rvt_export/_secrets/ddc-app-subscribe-key.txt. Then E2E, publish.
- Data Viewer 2.0.0 (sources/ddc-data-viewer, main 1451155, Compare mode): tests green (Rust 45, Node 89). Not built.
  Build: tools/build.py (target C:/b/ddv), packaging/build_package.py --version 2.0.0 --webview2-offline C:/.uiw/dl/MicrosoftEdgeWebView2RuntimeInstallerX64.exe.
  E2E incl. Compare ("Try with the sample building", changelog xlsx/BCF). Licence text stays (owner decision pending).
- IFC to Excel 2.0.1 (sources/ifc-excel, master + branch drop-pip 812001a WIP: drop pip from runtime; merge after full suite green).
  GLB output included. Build: launcher/refresh_portable.py --app-key-file <key>. After publish give SHA256 to OpenConstructionERP (PR #532).
- Excel Add-in 2026.10.1: built, C:/.uiw/out/DDC-Excel-AddIn-2026.10.1-unsigned.zip sha256 d982108a48ca9305a142bb69f0bc58ec4d4edef540caa324529187330dcd0dce.
- RVT Converter / RVT to IFC: 2.0.1 Windows assets NOT movable as-is (licence items) -> 2.0.2 by the RVT agent.
- IFC to Excel 2.0.0 already published in v2026.10.0 (sha256 0238bae0...).

## Next
1. DWG build -> E2E (lock open/closed with a short-expiry production-signed key via keygen, support prompt at 5th run, feedback, 15 langs, Open in Data Viewer) -> publish.
2. Viewer build -> E2E -> publish. 3. IFC build -> E2E (GLB in Viewer) -> publish.
4. Upload Add-in; v2026.10.1 latest; unified SHA256SUMS.txt (cosign bundle must be re-signed - owner/agent who signed); release notes; README/DDC_WINDOWS_Converters links -> v2026.10.1; merge PR #21.
5. 2.0 screenshot set for READMEs and site (after all 2.0 published).

## Open owner decisions
EULA 5.1 ad page vs no ads; Data Viewer licence model; vcruntime/VSTO redistribution; code signing; site PR #25 deploy (/api/app/subscribe, APP_KEYS);
G2/Capterra profiles; feedback retention 12 months; back up _secrets/ddc-license-signing.key.
