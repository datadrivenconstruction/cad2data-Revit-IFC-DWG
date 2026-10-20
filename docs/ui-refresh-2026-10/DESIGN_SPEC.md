# DDC Converters - unified UI spec (2026-10)

One page. Applies to RVT Converter, RVT to IFC, IFC to Excel, DWG to Excel, Data Viewer.

## Tokens
| Token | Light | Dark |
|---|---|---|
| bg | #F6F7F9 | #15181D |
| surface | #FFFFFF | #1E232A |
| border | #DDE1E6 | #2E353E |
| text | #1A1D21 | #E8EBEF |
| muted | #5F6873 | #9AA3AD |
| accent (DDC teal) | #0F7B6C | #3CC2AE |
| accent-hover | #0B6457 | #5ED3C1 |
| success | #1E8E3E | #4CC26A |
| warning | #B26A00 | #F0B44C |
| error | #C62828 | #F2726F |

No Autodesk colours, logos or styling. Only the DDC icon (`ddc.ico`).

Typography: Segoe UI Variable / Segoe UI (Windows), fallback system-ui. Sizes 20 title, 14 section, 12 body, 11 caption. Spacing grid 4 px; outer padding 16; card radius 8; buttons 32 px high, radius 6.

Theme: follows the OS (light/dark), override in Settings. Languages: EN (default, follows OS), DE, RU; switch in header, persisted.

## Main window layout (all converters)
1. Header: icon + product name + version, right side: language, theme, Help menu (About, Licence, Check for updates).
2. Input card: large drop zone "Drop files or a folder here" + "Choose files" / "Choose folder"; list of chosen files with size and remove (x).
3. Options card: output formats as toggle chips (XLSX, CSV, DAE/GLB, IFC, ...); output folder (default: next to input) with Browse.
4. Primary action: one accent button "Convert" (Enter). Secondary: Cancel while running.
5. Progress: determinate bar + current file + "n of N" + elapsed; collapsible log.
6. Summary card: converted / skipped / failed counts, total time, buttons **Open output folder**, **Open in Data Viewer** (when a viewer is present), **Copy report**.
7. Status bar: "Community edition - free, no registration required".

## Errors
Modal with: one plain sentence (what happened + what to do), "Copy details" (technical text), "Open log". Never a raw traceback in the main text.

## Licence / About
- About: product, version, build hash, short description, links (website, GitHub releases), third-party licences list (licenses/ folder), trademark disclaimer from legal/TRADEMARKS.md.
- Licence: "Community edition. Free for commercial and non-commercial use. No account, key or registration is required." Optional "Subscribe to updates" link to the DDC website. No activation-code field (Pro discontinued; no licensing server).

## CLI
`--help` / `-h` / `/?` prints usage to stdout and exits 0, never opens a window.


---

# Reference: RVT Converter Desktop (2026-10-19)

Owner decision: the RVT Converter Desktop UI (WPF, `apps/RVTConverter.Desktop`) is the reference design for every DDC converter. Where this section and the tables above disagree, this section wins. In particular the accent is the RVT blue `#175DAB`, not the teal listed in "Tokens" above, and the layout is the compact desktop-tool layout below, not the card layout. Mockup: `mockup.html` / `mockup.png` (light working state, dark empty state, light finished state). Screenshots of the shipped 0.6.8 are in `before/rvt-*.png`, `before/rvt2ifc-*.png`.

## Two generations exist - do not mix them up
* Shipped portable 0.6.8 (built from the a4ee1fcd lineage): large "web style" window, DDC logo banner, three tabs (Convert / History / How it works), three numbered cards, "Preview" tag. About, Licence, menu, status bar: none. After a conversion it opens a browser tab with the Community advertising page, which still says "a paid licence removes advertising pages".
* `branding-068` / release 0.6.9 (commit 6a533099 and later): compact Fluent-style window with File/Help menu, toolbar, file grid, bottom options bar, status bar, About with licence block. This is the base to keep.

## What is good (keep)
* One window, one job: files grid in the middle, options in one bottom row, one primary button. No wizard, no tabs needed for the main path.
* Neutral grey canvas + white surfaces + a single accent; light and dark follow the OS; Segoe UI 12 px; 4 px radius; 1 px lines. Dense but readable.
* Menu bar with real keyboard shortcuts (Ctrl+O add files, Ctrl+Shift+A add folder).
* Per-file status badges (Waiting / Converting / Written / Gaps / Error) and the result text in the grid row.
* "Beside the source file" as default output; More options kept off the main path.
* Native-size About dialog (name, version, engine hash, publisher, links, licences).

## What is redundant or weak (change)
1. Licence block in About has an activation-code field, "Buy licence", "Refresh licence", "Deactivate this device". Pro is discontinued and there is no licensing server: remove all four; replace with Community text and optional registration (section "Registration").
2. Status bar right side only says "Community" with no meaning. Make it "Community edition - free, no registration required" and make it a link to the Licence dialog.
3. "More options" expands over the whole file grid and pushes the grid away; it is a 7-section accordion with full-width combo boxes (1600 px wide dropdowns). Make it a right-docked 320 px panel (grid stays visible), single column, groups collapsed by default.
4. Bottom bar mixes a preset combo, two checkboxes and a format combo with different heights. Replace by: preset combo + toggle chips (Properties, IFC4, glTF, OBJ) in one 44 px row; chips show state without opening More options (glTF/OBJ are currently hidden inside More options).
5. Empty state is only a grey sentence. Use a dashed drop area with one bold line ("Drop .rvt or .rfa files or a folder here") and "or press Ctrl+O".
6. No progress indicator in the compact window except status text. Add a 40 px strip above the options row: determinate bar, "n of N - current file - elapsed", Cancel.
7. After a run there is no way to open the result. Add the same strip as summary: converted / skipped / failed counts, total time, buttons Open output folder, Open in Data Viewer (only when the viewer is found), Copy report.
8. Errors: grid shows only "The action failed. Open the log for details." Show a plain sentence in the Result column plus a "Details" link that opens a modal with the sentence, "Copy details" (technical text) and "Open log". Never a raw traceback in the main text.
9. Window opens at the size left by the last session even when huge; default 880x560, min 640x420, remember size and position, clamp to the work area.
10. Output folder is a bare checkbox; add an editable path field + Browse (enabled when "Beside the source file" is off).
11. Help > "How it works" tab and History tab can stay but must not be needed for the first conversion; the browser advert tab after conversion is removed (no advertising in a free product).

## Concrete compact layout (default 880 x 560, all sizes in dip)
| Zone | Height | Content |
|---|---|---|
| Title bar | native | DDC product icon (`icons/rvt.ico`, `icons/ifc.ico` for Revit to IFC), "RVT Converter - DataDrivenConstruction" |
| Menu | 24 | File (Add files, Add folder, Open output folder, Exit), View (Theme, Language, Scale), Help (How it works, Licence..., Check for updates, Logs folder, Licenses, About) |
| Toolbar | 36 | Add files..., Add folder..., Remove | Output: [path field, flexible] [Browse...] |
| File grid | flexible | columns Name (flex), Size 80, Status 100, Result (flex 1.2); rows 30, header 26; empty state = drop area |
| Progress / summary strip | 40, hidden when idle | see items 6, 7 |
| Options row | 44 | preset combo 150 x 26, chips 24 high (radius 12), More options toggle, spacer, Convert 96 x 28 |
| Status bar | 22 | left: state text; right: Community edition link |

Order of tab stops: Add files, Add folder, Remove, Output path, Browse, grid, preset, chips, More options, Convert. Enter = Convert when enabled, Esc = Cancel while running, Delete = Remove.
Spacing grid 4 (outer margin 8). Buttons 26 high (primary 28), radius 4. Font Segoe UI 12 (caption 11, dialog title 14).

## Tokens taken from the reference (`Theme.cs`)
| Token | Light | Dark |
|---|---|---|
| Canvas | #F3F3F3 | #202020 |
| Surface | #FFFFFF | #2B2B2B |
| Field | #FFFFFF | #1F1F1F |
| Ink | #1F1F1F | #F0F0F0 |
| Muted | #5F6368 | #A8A8A8 |
| Accent | #175DAB | #175DAB |
| AccentHover | #124C8C | #2A6EBB |
| AccentInk (links, chip text) | #175DAB | #7EB0E8 |
| Line | #D0D0D0 | #404040 |
| Hover / Tint | #E8E8E8 | #383838 |
| Pressed | #DADADA | #454545 |
| Selected | #CCE0F5 | #1E3F64 |
| Badge | #EBEBEB | #3A3A3A |
| OkInk / Success | #1E7B45 / #E3F1E8 | #6CC48F / #1E3A29 |
| WarningInk / Warning | #A65F00 / #FBF0DC | #E8B661 / #43361C |
| DangerInk / Danger | #B3261E / #F9E3E1 | #F2A49D / #4A2522 |
Title bar colour is the Windows caption (#53687A in the screenshots): do not paint a custom one.

# Registration (optional, server-less)

All DDC apps may offer an optional Community registration. It never blocks conversion, works offline, and sends nothing anywhere.

* File: `%APPDATA%\DataDrivenConstruction\registration.json`, shared by all DDC apps of the user.
* Format (UTF-8, no BOM): `{"email":"name@example.com","registered_at":"2026-10-19T21:30:00Z","products":["rvt-converter","revit-to-ifc"]}`. `registered_at` is UTC ISO 8601; `products` is a de-duplicated list of product ids that registered.
* Writing: write `registration.json.tmp` in the same folder, flush, then replace atomically (`File.Replace` / `File.Move` overwrite). Merge, do not overwrite: read the current file first, add the own product id, keep unknown fields.
* Reading: a missing, empty, corrupt, oversized (> 64 KB) or wrong-typed file means "not registered"; never throw, never delete the file; a corrupt file is left untouched until the user registers again (then replaced).
* Validation: trim, one `@`, non-empty local part, domain with a dot, no spaces, length <= 254.
* UI (Help > Licence...): text "Community edition. Free for commercial and non-commercial use. No account, key or registration is required."; below it an optional e-mail field with Register, and once registered the address plus Change and Reset (Reset removes only the own product id, deletes the file if the list becomes empty). Status "Registered: name@example.com" or "Not registered (optional)" in About and, in short form, in the status bar link.
* No activation code, no "Buy licence", no network calls.

## Installers
RVT apps have no `Setup.exe`. The per-user installer is an MSI built by `tools/build_installer.py PUBLISHED_FOLDER NEW_OUTPUT_FOLDER` (Windows MSI API + makecab, version read from `apps/RVTConverter.Desktop/RVTConverter.Desktop.csproj`); it verifies the published `MANIFEST.json` first. The portable folders (`DDC_RVT_Converter`, `DDC_RVT_to_IFC`) are built by `tools/build_desktop.ps1` and the attested release scripts (`tools/build_attested_release.ps1`). Earlier installer manifests: `docs/releases/*/installer.json`.


# Feedback & support prompt

Applies to all DDC desktop apps. Nothing here blocks conversion; every network call is user-initiated or a queued resend the user confirmed.

## Menu
Help menu gets **Feedback...** and, in the free edition only, **Support the project...** (opens the support card on demand). Order: About, Licence, Check for updates, Feedback..., Support the project....

## Feedback form (modal, 480 x auto dip)
| Field | Rule |
|---|---|
| Category (dropdown) | Bug / Conversion problem / Idea / Question / Other. Default Bug |
| Message (multiline) | required, 10..4000 chars, counter shown |
| Name (single line) | required by the current endpoint (see contract); label "Your first name" |
| E-mail (single line) | optional in the UI; validation as in Registration (trim, one `@`, domain with a dot, <= 254). Helper text: "Only if you want a reply." |
| Consent (checkbox, unchecked by default) | "I agree that DataDrivenConstruction processes this message (and the e-mail if given) to answer it. Privacy policy" (link https://cadbimconverter.com/datenschutz-impressum/). Send is disabled until ticked |
| Technical info (read-only, always visible, one line, expandable) | `App: RVT Converter 0.6.8 (build abc1234) / Windows 11 24H2 (10.0.26100) / language en`. Exactly these fields, nothing else |

Rules:
* App name, version and OS are attached automatically and shown before sending. A "Show payload" expander with the exact JSON is recommended.
* Never attach files, file names, folder paths, log content, user name, machine name, IP or hardware ids. If the message text looks like a path (`[A-Za-z]:\` or `\\`), show a non-blocking hint "Please remove personal paths and project names".
* Buttons: **Send** (accent), **Cancel**, links "Open GitHub issue instead" and "Write an e-mail".
* States: Sending... (button disabled, 15 s timeout) -> "Thank you, your message was sent." or an error text with the alternatives (queue, GitHub, e-mail).
* Offline, HTTP 5xx, network error or timeout: save to the queue and say "No connection. Saved on this PC; we will offer to send it at the next start."
* HTTP 429: show "Too many messages from your network. Try again in N minutes" (from `retry_after`), keep the text in the form, offer GitHub / e-mail. Do not queue (it would hit the limit again).
* HTTP 400 with `field`: highlight that field, show the server `message`.

## Offline queue
* Folder: `%APPDATA%\DataDrivenConstruction\feedback_queue\`, one UTF-8 (no BOM) JSON file per message, name `<UTC yyyyMMddTHHmmssZ>-<8 hex random>.json`. Content = the exact request body plus `"queued_at"` and `"consent_at"` (UTC ISO 8601; time the user ticked consent). Write `.tmp`, then atomic replace, as for registration.json.
* Cap: 20 files, 16 KB each. When full, the form says so and offers GitHub / e-mail (nothing is evicted). Files older than 90 days are ignored at start and offered for deletion by the user only; the app never deletes silently.
* At next start (after the main window is shown): if the queue has files, a non-modal bar "n unsent feedback message(s). Send now / Review / Not now". Send now posts them one by one (one request per 2 s); a file is removed only after HTTP 2xx. On 429 stop and keep the rest. Review shows each message with Send / Delete (user actions).
* A message without `consent_at` is never sent.
* All apps share the folder; each app sends only files whose `app` equals its own product id. Use a create-exclusive lock file `.sending` while resending.

## Endpoint contract (verified 2026-10-19 against the live relay used by the cadbimconverter.com contact form)
The site form posts to the DDC relay, not to the cadbimconverter VPS (its FastAPI service has only `/api/dl`, `/api/resend`, `/api/confirm`, `/api/unsubscribe`, `/admin`).

* URL: `POST https://openconstructionerp.com/api/inquiry` (one constant in the app; same as `relay` in `website/src/data/site.ts`).
* Headers: `Content-Type: application/json` (otherwise 400 `{"error":"Invalid JSON"}`). No Origin or Referer needed: a plain client without Origin reached validation. No auth, no CSRF token.
* CORS: preflight returns 200 with `Access-Control-Allow-Origin: *`, `Allow-Methods: POST, GET, OPTIONS`, `Allow-Headers: Content-Type`. Irrelevant for a desktop client.
* Server: Python `BaseHTTPServer` behind Caddy. `GET /api/inquiry` is 404; `GET /api/health` on the same host is 200.
* Body (JSON object):
  * `name` string, required. The server checks for a real first name: `x` is rejected with `{"error":"invalid_identity","field":"firstName","message":"Please enter your real first name."}`.
  * `email` string, required (missing -> `{"error":"Missing: email","field":"email","message":"Please fill in all required fields."}`).
  * `message` string, required.
  * `topic` string. Website values: cad2data licence, Ad-free licence, Education licence, Custom solution, Workshop, Support. Desktop uses `Support`.
  * `source` string. Website: `cbc-site-form` (chat: `cbc-site-chat`). Desktop proposal: `ddc-desktop-feedback`.
  * `company`, `page` optional on the website. Handling of further keys (`category`, `app`, `app_version`, `os`) is NOT verified, see test note. Until the owner confirms that the relay keeps them, the app also packs them into `message` as a final block:
    `\n\n---\nCategory: Bug\nApp: RVT Converter 0.6.8\nOS: Windows 11 24H2 (10.0.26100)\nLanguage: en\nConsent: yes 2026-10-19T21:30:00Z`
  * Honeypot `website` must be empty or absent (the app sends no such key); the site also waits 2.5 s after page load.
* Success: HTTP 200 (the site only checks `r.ok`).
* Errors seen: 400 `{"error","field","message"}`; 429 `{"error":"rate_limited","message":"...","retry_after":<seconds>}` plus `Retry-After` header.
* Rate limit: per source address, window about one hour (`retry_after` 3585 s after about seven requests, including invalid ones, so rejected requests probably count). Exact quota unknown. App rule: at most one send per 60 s, at most 5 per hour, stop on 429.
* Test submission: NOT delivered. The single marked submission ("DDC desktop feedback endpoint test - please ignore") got 429 because the earlier validation probes had used the quota. It was not repeated. To verify the full contract, wait an hour and send one request with the final body.
* Server-side blockers for the optional-e-mail design (decision for the owner; the relay source is not in the website repo and was not touched):
  1. `email` is required but the UI e-mail is optional. Proposal: for `source: "ddc-desktop-feedback"` the relay accepts empty `email`.
  2. `name` is validated as a real first name; relax for this source (or the app asks for it, as above).
  3. Store and forward `app`, `app_version`, `os`, `category`, `language` for this source.
  Until then, without an e-mail the Send button is replaced by "Send by e-mail" (mailto) and "Open GitHub issue".
* Fallbacks always available: mailto `mailto:info@datadrivenconstruction.io?subject=<app> <version> feedback: <category>&body=<message + technical block>` (URL-encoded, about 1800 chars max); GitHub issue (below).

## Links
| Target | URL |
|---|---|
| New GitHub issue (chooser) | `https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues/new/choose` |
| Prefilled bug | `https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues/new?template=bug_report.yml&app=<App%20name>&version=<ver>&os=<OS%20build>` |
| Prefilled conversion problem | `.../issues/new?template=conversion_problem.yml&app=<App%20name>&version=<ver>&os=<OS%20build>&input_format=<fmt>` |
| Prefilled feature | `.../issues/new?template=feature_request.yml&app=<App%20name>&version=<ver>&os=<OS%20build>` |

Query keys equal the field `id` values in `.github/ISSUE_TEMPLATE/*.yml` (`app`, `version`, `os`, `input_format`). `app` must equal a dropdown option text exactly (RVT Converter, RVT to IFC, IFC to Excel, DWG to Excel, Data Viewer). URL-encode everything, keep the URL under 8000 characters, never put message text, paths or file names in it. The canonical repository name is `cad2data-Revit-IFC-DWG` (the old `-DGN` name redirects).

| Channel | Link |
|---|---|
| Support e-mail | info@datadrivenconstruction.io |
| Websites | https://datadrivenconstruction.io , https://cadbimconverter.com |
| Contact form | https://cadbimconverter.com/contact/ |
| Book a call | https://calendly.com/datadrivenconstruction |
| GitHub org | https://github.com/datadrivenconstruction |
| Converters repo (star target) | https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG |
| LinkedIn company | https://www.linkedin.com/company/datadrivenconstruction (cadbimconverter.com) vs https://www.linkedin.com/company/data-driven-construction (datadrivenconstruction.io); the two sites differ, owner to confirm the canonical one |
| LinkedIn author | https://www.linkedin.com/in/boikoartem/ |
| Telegram | https://t.me/datadrivenconstruction |
| YouTube | https://www.youtube.com/@datadrivenconstruction (also https://www.youtube.com/@OpenConstructionAcademy) |
| X | https://x.com/datadrivenconst |

Open all links in the system browser (`ShellExecute`), never in an embedded web view.

## Support prompt (free edition only) - rev 2026-10-20
Supersedes the earlier "Support prompt (ported from OpenConstructionERP)" text. Nothing here blocks work; no network call except the optional newsletter sign-up.

### 1. Counter (per app, offline)
* File `%APPDATA%\DataDrivenConstruction\prompt_state.json` (UTF-8, no BOM; same atomic write/merge/corrupt-file rules as `registration.json`). One counter per product id, key `counters.<product-id>`; apps never read or change another app's counter. The file is shared only so that the newsletter flag is shared.
* What counts (+1, once): one successful run = one increment, a batch run of N files is 1 (success = at least one file converted, not cancelled). Data Viewer: one successful file open = 1. Failures, cancels, CLI/headless runs, re-opening the same file in the same session still count only if it is a new successful open (Viewer) / new run (converters). CLI mode never increments and never shows.
* Show rule: after the increment, show the card when `n % 5 == 0` (5, 10, 15, ...), once, after the summary/file is displayed and the UI is idle (never during a run, never over an error dialog, never at start). The shown flag is not stored; the next show is at the next multiple of 5. Counter is a non-negative int, clamp to 0..1,000,000,000; if the file cannot be read or written, show nothing (fail closed) and count in memory only.
* Works fully offline; the card never waits for the network.

```json
{
  "version": 2,
  "counters": { "rvt-converter": 10, "data-viewer": 3 },
  "newsletter": {
    "subscribedAt": "2026-10-20T10:00:00Z",
    "pending": { "email": "...", "consentAt": "...", "consentTextVersion": "updates-2026-10-20", "queuedAt": "..." }
  }
}
```
Unknown keys are kept. `pending` is also mirrored as a queue file (below). Earlier fields (`status`, `declineCount`, `activeDays`, `lastShownAt`, `apps`) are ignored and may be dropped on next write.

### 2. Commercial edition never shows it
Contract: the licence file in the program folder, `licence.json` next to the executable, contains `"commercial_licence": true`, written only by the licensed (full) build. Rules:
* The free build has no such file or the value is not the JSON boolean `true`: prompt enabled.
* Read at start; missing/unreadable/invalid = free. Only the literal `true` counts (not "true", 1).
* Alternative equivalent for a compiled constant: `BuildInfo.CommercialLicence` (bool) set by the licensed build pipeline; the app uses `constant || licence.json`.
* If commercial: no counter increments, no card, no newsletter field, menu item "Support the project..." is hidden. "Send feedback" stays available.
* Users cannot unlock it by editing the file in the free build because the free installer does not ship the file and the legal licence (not this flag) governs commercial use; the flag only controls UI.

### 3. Card (free edition)
Non-modal card in the summary area (bottom right of the window, no backdrop, focus not stolen). Contents, in order:
1. Title and short text (neutral wording, no incentive, no filtering).
2. **Star on GitHub** - https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG
3. **Share a post** - split button/menu: LinkedIn `https://www.linkedin.com/sharing/share-offsite/?url=<urlencoded star target>` and X `https://twitter.com/intent/tweet?text=<share.text>&url=<urlencoded star target>`; text localised.
4. **Review on G2** / **Review on Capterra** - only if a product profile URL is configured. Status 2026-10-20: **none yet for the converters -> both buttons hidden** (see section 4). Constants `G2_REVIEW_URL`, `CAPTERRA_REVIEW_URL` are `null`; the button renders only when non-null. Never use the OpenConstructionERP G2 page for the converters.
5. **Send feedback** - opens the feedback form (kept).
6. Newsletter row (unless subscribed): e-mail field, consent checkbox (unchecked), **Subscribe**.
7. **Not now** and the window close X - hide the card. Esc = Not now. The card auto-hides after 60 s without interaction.

Removed in the free edition: "Don't ask again", and the Settings checkbox "Show occasional support suggestions" (no opt-out). The legacy "terminal after clicking Star/Share/Review" rule is also removed: clicking a link does not stop future cards (wording stays neutral; every 5th success only).
Review wording is neutral: no rewards, no "only if happy", no routing of unhappy users elsewhere; "Send feedback" sits next to, not instead of, the review buttons.

### 4. G2 / Capterra findings (2026-10-20)
* g2.com and capterra.com return 403 to automated fetch. Web searches (`DataDrivenConstruction`, `cad2data`, `DDC RVT Converter`, restricted to g2.com / capterra.com) returned no G2 or Capterra page; only GitHub, n8n, skill directories. Result: **no known profile for the DDC converters on either site**. Not proof of absence: the owner should check once in a browser. If a profile is created, add its URL to the two constants; no other change is needed.
* Known G2 page https://www.g2.com/products/openconstructionerp/reviews belongs to a different product and must not be used.

### 5. Newsletter sign-up
Shown in the card only while `newsletter.subscribedAt` is absent. After success, set `newsletter.subscribedAt` (UTC ISO 8601), clear `pending`, and hide the field on all later cards (in all DDC apps, since the file is shared).
* Consent checkbox: unchecked by default; Subscribe disabled until e-mail is valid (trim, one `@`, domain with a dot, <= 254) AND the box is ticked.
* Privacy link: https://cadbimconverter.com/datenschutz-impressum/ (the page holds the English privacy notice, section "Product updates by e-mail (optional)"; German translation below it). Open in the system browser.
* Endpoint (pending: endpoint). Existing site endpoint `POST https://cadbimconverter.com/api/subscribe` (verified 2026-10-20; handler in ddc-website branch `v4`, `services/downloads/app/main.py`): requires a browser Origin/Referer from cadbimconverter.com (otherwise 403 `bad_origin`), JSON body `{email, website (honeypot, empty), elapsed (ms, >= 1200), page}`, rate limit 5 per 10 min and 20 per day per address and 3 per hour per e-mail, e-mail syntax + MX + disposable-domain checks, always double opt-in (confirmation mail with a button, posted confirm page; nothing is sent before confirm), stored in the site's SQLite `leads` table with `consent_log` (action, text version, truncated IP), every mail carries a one-click unsubscribe. A desktop client sends no Origin, so it cannot use that route.
* App route (PR https://github.com/datadrivenconstruction/ddc-website/pull/25, not deployed): `POST https://cadbimconverter.com/api/app/subscribe`, headers `Content-Type: application/json`, `X-DDC-App-Key: <key from app build config>`; body `{"email":"a@b.com","consent":true,"app":"rvt-converter","app_version":"2.0.1"}`; no Origin needed. Success `200 {"ok":true,"mail":true,"confirmationSent":true}` (same answer for new, pending, already confirmed). Errors: 400 `consent_required` / `email_invalid` / `email_disposable` / `email_nomx`, 403 `bad_key`, 503 `disabled` (until the site sets `APP_KEYS`), 429 `rate_limited` with `retry_after`. Until the PR is merged and deployed (steps in the PR), the app must treat any non-2xx/ok:false as "not subscribed" and use the queue; the key is not a secret, protection is rate limit + consent + double opt-in. "Subscribed" in the app means the request was accepted; the user still has to confirm by e-mail, and the UI text says so.
* UI after Subscribe: "Please open the e-mail we sent and press the confirm button." Field hidden afterwards (state flag).
* Offline or 5xx/timeout: store the request in `%APPDATA%\DataDrivenConstruction\feedback_queue\newsletter-<UTC>-<hex>.json` containing `email`, `consent: true`, `consentAt` (UTC), `consentTextVersion`, `app`, `app_version`; also mark `newsletter.pending` in prompt_state.json. The card shows "Saved. We will send it when you are online." The field stays hidden while `pending` exists. Resend at next start (after the main window is shown) and after the next successful conversion/open, one request per 2 s, at most 5 per hour; remove the file and set `subscribedAt` only after 2xx ok:true. On 400 `email_*` drop the file and show the field again. A queue item without `consentAt` is never sent. User can cancel the pending item from Help > Feedback > Pending.
* No e-mail address is stored anywhere else in the app, and `registration.json` (Community registration) is a separate, offline-only feature; do not copy its address into the sign-up without the checkbox.

### 6. Texts
EN is the source. Placeholders `{n}` are not used here.

| Key | EN | DE | RU |
|---|---|---|---|
| support.card.title | If DDC helps you | Wenn DDC Ihnen hilft | Если DDC вам помогает |
| support.card.body | If DDC helps you, a short honest review helps others find it. | Wenn DDC Ihnen hilft, hilft eine kurze, ehrliche Bewertung anderen, es zu finden. | Если DDC вам помогает, короткий честный отзыв поможет другим найти его. |
| support.card.aria | DDC support options | DDC-Unterstützungsoptionen | Способы поддержать DDC |
| support.star | Star on GitHub | Auf GitHub einen Stern geben | Поставить звезду на GitHub |
| support.share | Share a post | Beitrag teilen | Поделиться постом |
| support.share.linkedin | LinkedIn | LinkedIn | LinkedIn |
| support.share.x | X | X | X |
| support.share.text | DDC converters: Revit, IFC and DWG to Excel and IFC for construction data. Free for non-commercial use. | DDC-Konverter: Revit, IFC und DWG nach Excel und IFC für Bauwesen-Daten. Kostenlos für nicht-kommerzielle Nutzung. | Конвертеры DDC: Revit, IFC и DWG в Excel и IFC для строительных данных. Бесплатно для некоммерческого использования. |
| support.review.g2 | Review on G2 | Auf G2 bewerten | Отзыв на G2 |
| support.review.capterra | Review on Capterra | Auf Capterra bewerten | Отзыв на Capterra |
| support.feedback | Send feedback | Feedback senden | Отправить отзыв |
| support.notnow | Not now | Jetzt nicht | Не сейчас |
| support.close | Close | Schließen | Закрыть |
| newsletter.title | Product updates by e-mail | Produkt-Updates per E-Mail | Новости продукта по e-mail |
| newsletter.email | E-mail address | E-Mail-Adresse | Адрес e-mail |
| newsletter.consent | I want to receive product updates (new releases and important fixes) from DataDrivenConstruction by e-mail. I can unsubscribe at any time. | Ich möchte Produkt-Updates (neue Versionen und wichtige Korrekturen) von DataDrivenConstruction per E-Mail erhalten. Ich kann mich jederzeit abmelden. | Я хочу получать по e-mail новости продукта от DataDrivenConstruction (новые версии и важные исправления). Отписаться можно в любой момент. |
| newsletter.privacy | Privacy | Datenschutz | Конфиденциальность |
| newsletter.note | We first send one e-mail to confirm (double opt-in). Your address is used only for these updates. | Wir senden zuerst eine Bestätigungs-E-Mail (Double-Opt-in). Ihre Adresse wird nur für diese Updates verwendet. | Сначала мы отправим одно письмо для подтверждения (double opt-in). Адрес используется только для этих новостей. |
| newsletter.subscribe | Subscribe | Abonnieren | Подписаться |
| newsletter.ok | Please open the e-mail we sent and press the confirm button. | Bitte öffnen Sie die gesendete E-Mail und klicken Sie auf Bestätigen. | Откройте отправленное письмо и нажмите кнопку подтверждения. |
| newsletter.queued | Saved. We will send it when you are online. | Gespeichert. Wir senden es, sobald Sie online sind. | Сохранено. Отправим, когда появится соединение. |
| newsletter.invalid | Please enter a valid e-mail address. | Bitte geben Sie eine gültige E-Mail-Adresse ein. | Введите корректный адрес e-mail. |
| newsletter.ratelimit | Too many attempts. Please try again later. | Zu viele Versuche. Bitte versuchen Sie es später erneut. | Слишком много попыток. Повторите позже. |

Consent text version string: `updates-2026-10-20` (bump whenever `newsletter.consent` changes in any language; the server stores it with the request).
Key list for all 15 locales: every `support.*` and `newsletter.*` key above (25 keys, as listed); the 15 UI locales are those of the language menu (owner order: RU is the fifth entry; pt-BR is included; the exact list is owned by the language-menu spec, not repeated here). EN, DE and RU are translated above; the remaining locales get these keys and fall back to EN at runtime until translated. Review/Capterra keys exist even when the buttons are hidden.

### 7. Test cases (unit tests on the pure logic, no UI)
Counter / show rule `shouldShow(n)` after increment:
| Case | Input | Expected |
|---|---|---|
| T1 | n 1..4 | no |
| T2 | n = 5 | yes |
| T3 | n = 6, 7, 8, 9 | no |
| T4 | n = 10 | yes; 15, 20 yes; 11 no |
| T5 | commercial_licence true, n = 5 | no; counter unchanged (stays 0) |
| T6 | licence.json missing / `"true"` string / 1 / invalid JSON | free (card shows at n=5) |
| T7 | failed run, cancelled run, CLI run | counter unchanged |
| T8 | batch of 30 files, success | counter +1 only |
| T9 | Viewer: 5 successful file opens | yes at 5th |
| T10 | two apps, each 4 successes | no card in either (separate counters); app A 5th success shows only in A |
| T11 | prompt_state.json corrupt / > 64 KB / unwritable | no card, no throw, file untouched |
| T12 | unknown keys in the file | preserved after a counter write |
| T13 | counter 10, card shown, app restarted, 11th | no card; 15th yes |
Newsletter:
| Case | Input | Expected |
|---|---|---|
| N1 | `subscribedAt` set | field not rendered |
| N2 | consent unchecked or invalid e-mail | Subscribe disabled, no request |
| N3 | consent checked, valid e-mail, server ok:true | `subscribedAt` set, field hidden, `pending` cleared |
| N4 | offline | queue file created with `consentAt`, `pending` set, field hidden, "Saved" text |
| N5 | queued item, online at next start | request sent, file removed, `subscribedAt` set |
| N6 | queued item, server 400 `email_invalid` | file removed, field shown again |
| N7 | queue item without `consentAt` | never sent |
| N8 | 429 | queue kept, no retry before 60 s |
| N9 | commercial | no newsletter field |
Buttons:
| B1 | G2/Capterra URLs null | no review buttons rendered |
| B2 | free edition | no "Don't ask again", no Settings opt-out, "Send feedback" present, "Not now" and X hide the card |
