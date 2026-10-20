# Classification columns (`ddc classify`)

`ddc classify` adds classification columns to the element table: one code column and one title column per system.
Supported systems and the added column names:

| System id | Added columns | Owner | Licence situation (checked 2026-10-20) |
|---|---|---|---|
| `uniclass2015` | `Uniclass 2015 Code`, `Uniclass 2015 Title` | NBS (Hubexo North UK Ltd) | Published under CC BY-ND 4.0 on uniclass.thenbs.com: free to use and to share unchanged, with attribution. Users must not change the tables. Because a re-formatted or merged copy is an adaptation, **ddc-tools does not bundle it**. Download the tables yourself. |
| `omniclass` | `OmniClass Code`, `OmniClass Title` | CSI / CSC | Copyrighted and licensed by CSI (terms at omniclass.org/license). Not redistributable. |
| `masterformat` | `MasterFormat Code`, `MasterFormat Title` | CSI / CSC | Copyrighted and licensed by CSI. Not redistributable. |
| `din276` | `DIN 276 Code`, `DIN 276 Title` | DIN e.V. | Copyrighted standard sold by DIN Media. Not redistributable. |
| `gesn_ksr` | `GESN-KSR Code`, `GESN-KSR Title` | Ministry of Construction of the Russian Federation (FGIS CS) | Official normative documents; the redistribution terms of the published databases were not confirmed. Not bundled. |
| `gbt51269` | `GB/T 51269 Code`, `GB/T 51269 Title` | MOHURD / SAMR | Copyrighted national standard. Not redistributable. |
| `nlsfb` | `NL-SfB Code`, `NL-SfB Title` | BIM Loket | Intellectual property of BIM Loket; reuse terms not confirmed. Not bundled. |
| `cci` | `CCI Code`, `CCI Title` | Construction Classification International Collaboration | Core tables are reported to be CC BY 4.0, but this could not be confirmed from the publisher's own page. Not bundled. |

**ddc-tools ships no code lists.** Nothing in the package contains actual classification codes; a test enforces this.
You load the list you are entitled to use, and the tool uses it to fill titles and to warn about unknown codes.
Where a list is free to download (Uniclass, probably CCI), take it from the owner's site so that you also get
the current version and the owner's licence text. If you publish results that contain Uniclass codes or titles,
give the attribution the licence asks for.

This page describes how the tool is built, not legal advice. Check the current licence of every list you load.

## Workflow

```powershell
# 1. empty mapping template (UTF-8 with BOM, opens in Excel)
ddc classify template uniclass2015 -o uniclass_mapping.csv

# 2. optional: import your licensed code list (CSV or XLSX; code and title columns are detected, or name them)
ddc classify import uniclass2015 Uniclass2015_Ss.xlsx --code-col Code --title-col Title

# 3. fill the mapping and apply it to a table (CSV/XLSX/JSONL from `ddc table`, or a converter output)
ddc classify apply Project_rvt.xlsx --system uniclass2015 --mapping uniclass_mapping.csv --xlsx classified.xlsx
```

Imported lists are stored as `Code,Title` CSV in `%USERPROFILE%\.ddc-tools\classification\<system>.csv`
(`~/.ddc-tools/classification/` elsewhere), or in the folder named by `DDC_CLASSIFICATION_DIR`.

## Mapping file

One rule per row; the first matching rule wins.

| Column | Meaning |
|---|---|
| `Match Column` | Column of the table (`Category`, `Type Name`, `IfcClass`, `Layer`, ...) |
| `Match Value` | Case-insensitive pattern with `*` and `?` (`OST_Walls`, `*Beton*`, `Wall*`) |
| `Code` | Code to write |
| `Title` | Optional; empty = taken from the imported list |
| `Notes` | Free text, ignored |

Example (the codes are only an illustration of the format; use your own list):

```csv
Match Column,Match Value,Code,Title,Notes
Category,OST_Walls,Ss_25_10,,exterior and interior walls
Type Name,*Decke*,Ss_30_20,,slabs
```

The command prints a warning for every code that is not in the imported list and for every `Match Column` that is
missing from the table. Rows without a matching rule keep empty classification cells.
