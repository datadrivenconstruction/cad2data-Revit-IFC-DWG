# International use of ddc-tools

## Paths

All file access goes through `ddc_tools.paths.fs()`. Folder and file names may contain Cyrillic, Chinese, Arabic,
Greek or accented letters, spaces, `&`, `#` and `%` (SQLite files are opened with a percent-encoded URI, so `#`/`%`
are safe). On Windows, absolute paths of about 240 characters and more get the extended-length prefix, UNC shares
(`\\server\share\...`) become `\\?\UNC\server\share\...`, so paths over 260 characters work without changing a system setting.
Converter processes are started without a shell, and their output is decoded as UTF-8 with replacement, so a legacy
console code page cannot crash a run.

OneDrive and other synced folders: use "Always keep on this device" for model folders; files that exist only in the
cloud cannot be read by any local tool.

## CSV, XLSX, JSON

| Topic | Behaviour |
|---|---|
| Encoding | CSV is written as UTF-8 with BOM (Excel shows non-Latin text correctly); `--no-bom` writes plain UTF-8. JSON and JSONL are UTF-8 without escapes (`ensure_ascii=False`), line ends are `\n`. |
| Reading CSV | UTF-8 (with or without BOM), UTF-16 (Excel "Unicode Text"), and Windows code pages 1251, 1253, 1252 (the system code page is tried first). Delimiter `,`, `;` or tab is detected from the header line. |
| Delimiter | `--delimiter comma` (default), `semicolon`, `tab`, or `auto` (`;` when the system locale uses a decimal comma, as Excel does). |
| Numbers | Written with `.` as the decimal point and without thousands separators, in every locale. Parsing accepts `12.5`, `12,5`, `1,234.5`, `1.234,5` and `1 234,5 m2` (when both separators occur the last one is the decimal separator). A single `1,234` is read as 1.234. |
| Units | Table quantities are metric (m, m2, m3) or the IFC project units as stored. `--unit-headers` writes `Length [m]`, `Area [m2]`, `Volume [m3]`. Default headers stay unchanged because spreadsheets and notebooks depend on them. |
| Dates | Reports carry `generated` as ISO 8601 with offset, for example `2026-10-20T13:05:00+00:00` (UTC). BCF uses UTC with `Z`. |

## Tests

`tests/test_intl.py` uses synthetic Cyrillic, Chinese, Arabic, German and Greek folder names and data, a
300+ character path (Windows), CSV in several encodings, number parsing, report timestamps and the classification
workflow.
