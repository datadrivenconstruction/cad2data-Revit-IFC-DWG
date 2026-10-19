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
Help menu gets **Feedback...** and **Support the project...** (opens the support dialog on demand, never suppressed by cooldown). Order: About, Licence, Check for updates, Feedback..., Support the project....

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

## Support prompt (ported from OpenConstructionERP, adapted)
Studied in repo datadrivenconstruction/OpenConstructionERP, `frontend/src`: `app/layout/SupportUsButton.tsx` (modal), `shared/ui/ReviewPromptCard.tsx` (corner card), `stores/useReviewPromptStore.ts` (cadence), texts in `app/locales/{en,de,ru}.ts` (keys `support.*`, `review_ask.*`).

### What OCERP does
* Support modal: header button "Support us". Auto-popup after 20 minutes of active (visible) tab time, at most once per 30 days (`localStorage oe_support_seen_at`, written on open and on close); skipped on the public demo and when the review card was shown within 4 days. Manual open is never suppressed. Rows: Star on GitHub, Review on G2, Share (Post on X, Post on LinkedIn, Copy text + link), case study by e-mail, Donate (PayPal, GitHub Sponsors). Esc closes.
* Review card (non-modal, bottom right, no backdrop, never blocks work): buttons Star on GitHub, Review on G2, Share on LinkedIn, Post on X; footer "Don't ask again" (terminal) and "Maybe later" (decline); the close X is a decline. Following any link is terminal.
* Cadence (`oe_review_prompt`): state `{firstSeenAt, activeDays[] (local YYYY-MM-DD, max 30), lastAskedAt, declineCount, status active|stopped}`. Eligible only if install age >= 7 days AND >= 5 distinct active days; >= 4 days since `lastAskedAt`; backoff by declines [4, 4, 14, 45] days; hard cap 4 declines, then never; `stopped` is terminal; not within 4 days of the support modal. `lastAskedAt` is stamped when shown, so a reload cannot replay. Unreadable storage fails closed (show nothing). The day counter runs unconditionally from the app shell.

### Adaptation for desktop apps
Trigger (all must hold; evaluated once after a conversion run finishes successfully; never at start, never during a run, never in CLI mode, never over an error dialog or first-run screen):
1. `successfulConversions >= N`, N = 5 (a run counts when at least one file converted and it was not cancelled; one increment per run; sum across all DDC apps).
2. `now - firstSeenAt >= D`, D = 7 days, and `activeDays >= 3` distinct local days.
3. Not stopped, `declineCount < 4`, and `now - lastShownAt >= backoff[declineCount]`, backoff `[7, 14, 30, 60]` days (longer than the web card: desktop use is bursty).
4. Cross-app quiet period: no DDC app showed the prompt within 3 days (shared file, so five installed apps do not produce five asks).

Presentation: non-modal card in the Summary area (bottom right, no backdrop, focus not stolen, Esc = Maybe later). It hides itself after 60 s without interaction and counts as shown, not as a decline.

Buttons: **Star on GitHub**, **Share on LinkedIn** (`https://www.linkedin.com/sharing/share-offsite/?url=<urlencoded star target>`), **Post on X** (`https://twitter.com/intent/tweet?text=<share.text>&url=<urlencoded star target>`), **Send feedback** (opens the form), **Maybe later** (decline), **Don't ask again** (terminal). Following Star / LinkedIn / X is terminal, as in OCERP. Help > Support the project... always works regardless of state and also lists e-mail, YouTube and Telegram. The OCERP donate row (PayPal, GitHub Sponsors) is off by default: no payment links in the apps until the owner decides.

### State file
`%APPDATA%\DataDrivenConstruction\prompt_state.json`, shared by all DDC apps, UTF-8 no BOM, same atomic write and merge rules as `registration.json` (read, merge own keys, keep unknown fields, `.tmp` + replace; missing, corrupt, > 64 KB or wrong-typed means defaults and the file is left untouched; never throw; if the folder is not writable the prompt is silently disabled, fail closed).
```json
{
  "version": 1,
  "firstSeenAt": "2026-10-19T21:30:00Z",
  "activeDays": ["2026-10-19", "2026-10-21"],
  "lastShownAt": "2026-10-26T09:12:00Z",
  "declineCount": 1,
  "status": "active",
  "apps": { "rvt-converter": { "successfulConversions": 7, "lastShownAt": "2026-10-26T09:12:00Z" } },
  "feedback": { "lastSentAt": "2026-10-20T10:00:00Z" }
}
```
`status` is `active` or `stopped` (set by Don't ask again or by following a link; shared by all apps). Times are UTC ISO 8601; `activeDays` are local calendar days (max 30 kept). If the system clock is earlier than `lastShownAt`, treat as "shown recently".
Settings > General: checkbox "Show occasional support suggestions" (default on). Off writes `status: stopped`; on again resets `declineCount` to 0 and `status` to `active`. Disabling never affects the Feedback menu item.

### Texts (shipped in the app resource files; follow the app language)
| Key | EN | DE | RU |
|---|---|---|---|
| menu.feedback | Feedback... | Feedback... | Обратная связь... |
| menu.support | Support the project... | Projekt unterstützen... | Поддержать проект... |
| prompt.title | Enjoying DDC converters? | Gefallen Ihnen die DDC-Konverter? | Нравятся конвертеры DDC? |
| prompt.body | A minute of honest feedback helps other construction teams find and trust the tools. It genuinely makes a difference to us. | Eine Minute ehrliches Feedback hilft anderen Bauteams, die Werkzeuge zu finden und ihnen zu vertrauen. Das bedeutet uns wirklich viel. | Минута честного отзыва помогает другим строительным командам найти инструменты и довериться им. Для нас это действительно много значит. |
| prompt.star | Star on GitHub | Auf GitHub einen Stern geben | Поставить звезду на GitHub |
| prompt.linkedin | Share on LinkedIn | Auf LinkedIn teilen | Поделиться в LinkedIn |
| prompt.x | Post on X | Auf X posten | Опубликовать в X |
| prompt.feedback | Send feedback | Feedback senden | Отправить отзыв |
| prompt.later | Maybe later | Vielleicht später | Может быть, позже |
| prompt.never | Don't ask again | Nicht mehr fragen | Больше не спрашивать |
| prompt.aria | Rate DDC converters | DDC-Konverter bewerten | Оценить конвертеры DDC |
| support.title | Help DDC converters grow | Helfen Sie den DDC-Konvertern zu wachsen | Помогите конвертерам DDC расти |
| support.subtitle | We build this in the open and ship every feature for free. A few tiny actions from you keep development going. | Wir entwickeln dies offen und stellen jede Funktion kostenlos bereit. Ein paar kleine Aktionen Ihrerseits halten die Entwicklung am Laufen. | Мы разрабатываем это в открытом виде и выпускаем каждую функцию бесплатно. Несколько небольших действий с вашей стороны поддерживают разработку. |
| support.star_body | 30 seconds. Stars are how new construction teams discover the project. | 30 Sekunden. Über Sterne entdecken neue Bauteams das Projekt. | 30 секунд. Через звёзды новые строительные команды узнают о проекте. |
| support.share_body | One post on LinkedIn or X reaches dozens of estimators, planners and BIM managers. | Ein Beitrag auf LinkedIn oder X erreicht Dutzende Kalkulatoren, Planer und BIM-Manager. | Один пост в LinkedIn или X достигает десятков сметчиков, планировщиков и BIM-менеджеров. |
| support.thanks | Thank you. Every star, share and story keeps this project alive. | Vielen Dank. Jeder Stern, jedes Teilen und jede Geschichte hält dieses Projekt am Leben. | Спасибо. Каждая звезда, репост и история поддерживает этот проект. |
| share.text | DDC converters: free Revit, IFC and DWG converters for construction data. No registration. | DDC-Konverter: kostenlose Revit-, IFC- und DWG-Konverter für Bauwesen-Daten. Ohne Registrierung. | Конвертеры DDC: бесплатные конвертеры Revit, IFC и DWG для строительных данных. Без регистрации. |
| fb.title | Send feedback | Feedback senden | Отправить отзыв |
| fb.category | Category | Kategorie | Категория |
| fb.cat.* | Bug / Conversion problem / Idea / Question / Other | Fehler / Konvertierungsproblem / Idee / Frage / Sonstiges | Ошибка / Проблема конвертации / Идея / Вопрос / Другое |
| fb.message | Message | Nachricht | Сообщение |
| fb.name | Your first name | Ihr Vorname | Ваше имя |
| fb.email | E-mail (optional, only if you want a reply) | E-Mail (optional, nur für eine Antwort) | E-mail (необязательно, только для ответа) |
| fb.consent | I agree that DataDrivenConstruction processes this message to answer it. | Ich bin einverstanden, dass DataDrivenConstruction diese Nachricht zur Beantwortung verarbeitet. | Я согласен, что DataDrivenConstruction обрабатывает это сообщение, чтобы ответить на него. |
| fb.tech | Sent with your message: | Wird mit Ihrer Nachricht gesendet: | Отправляется вместе с сообщением: |
| fb.nofiles | No files, file names or folders are sent. | Es werden keine Dateien, Dateinamen oder Ordner gesendet. | Файлы, имена файлов и папки не отправляются. |
| fb.pathhint | Please remove personal paths and project names. | Bitte entfernen Sie persönliche Pfade und Projektnamen. | Удалите личные пути и названия проектов. |
| fb.send | Send | Senden | Отправить |
| fb.sent | Thank you, your message was sent. | Vielen Dank, Ihre Nachricht wurde gesendet. | Спасибо, сообщение отправлено. |
| fb.queued | No connection. Saved on this PC; we will offer to send it at the next start. | Keine Verbindung. Auf diesem PC gespeichert; wir bieten das Senden beim nächsten Start an. | Нет соединения. Сохранено на этом компьютере; предложим отправить при следующем запуске. |
| fb.ratelimit | Too many messages from your network. Try again in {n} minutes. | Zu viele Nachrichten aus Ihrem Netzwerk. Versuchen Sie es in {n} Minuten erneut. | Слишком много сообщений из вашей сети. Повторите через {n} мин. |
| fb.github | Open GitHub issue instead | Stattdessen GitHub-Issue öffnen | Открыть issue на GitHub |
| fb.mail | Write an e-mail | E-Mail schreiben | Написать письмо |
| fb.pending | {n} unsent feedback message(s). | {n} nicht gesendete Feedback-Nachricht(en). | Неотправленных сообщений: {n}. |
| fb.pending.actions | Send now / Review / Not now | Jetzt senden / Ansehen / Nicht jetzt | Отправить / Просмотреть / Не сейчас |

Do not port OCERP's sentence about subscriber counts and reach; no unverifiable claims in the apps.
