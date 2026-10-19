# DDC Windows Converters — Proprietary Software

> **The DDC binaries are NOT MIT-licensed.**
> They are proprietary software licensed under the
> DataDrivenConstruction Proprietary Software License and the
> DataDrivenConstruction Terms of Use and EULA at
> <https://datadrivenconstruction.io/term-of-use-and-eula/>.
>
> See [LICENSE-PROPRIETARY.txt](./LICENSE-PROPRIETARY.txt) and
> [EULA.txt](./EULA.txt) in this folder, and [NOTICE](../NOTICE)
> at the repository root, for the full terms.

## Where the converters are now

The DDC converters are no longer stored in git. The previous
generation of converter binaries has been removed from this
repository. The new first-party converters are distributed as
release packages through GitHub Releases:

<https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases>

| Product | Version | What it does |
|---------|---------|--------------|
| DDC RVT Converter | 0.6.8 | Desktop app (`RVT Converter.exe`) and CLI (`cli\RVTconverter.exe`). Reads `.rvt` / `.rfa` files saved by Autodesk® Revit® 2019–2027 and writes a GLB model, JSON summary/report, optional property tables and an experimental IFC4 file. The desktop app also writes CSV tables and SQLite. |
| DDC RVT-to-IFC | 0.6.8 | Desktop app built on the same engine and CLI as DDC RVT Converter, with IFC export as the default. |
| DDC IFC to Excel | 0.3.1-preview | Portable Python app with its own IFC reader. Reads IFC2x3 / IFC4 (SPF and IFCZIP) and writes `drawing.xlsx`, `data.jsonl`, `data.sqlite`, `result.json`. |
| DDC CAD drawing (.dwg) to Excel | 0.4.1 | Own `.dwg` decoder. Writes per-drawing `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json`, `REPORT.txt`, including counts of decoded / refused / unsupported records. |
| DDC Data Viewer | 0.1.1 | Free desktop viewer for XLSX / CSV / JSONL / Parquet tables with linked GLB / DAE 3D models. |

**Status: these are previews.** Quality has not been fully qualified.
Check the `report.json` / `REPORT.txt` / `result.json` files that
each tool writes, and verify results on your own data before relying
on them. MicroStation DGN conversion is discontinued (there is no
own DGN reader).

Suggested unpack locations: `C:\DDC\RVT-Converter\`,
`C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`.

Third-party components of each release package are listed in
`THIRD_PARTY_NOTICES` inside the package.

## What remains in this folder

| Sub-directory                      | Purpose                                           |
|------------------------------------|---------------------------------------------------|
| `DDC_Update_Revit_from_Excel/`     | Add-in for Autodesk® Revit®: round-trip updates from tabular data into a Revit model |

The MSI installers of the add-in were removed from git for legal
reasons and are distributed separately. The folder keeps its
documentation, license file and samples.

## How the binaries relate to the MIT-licensed parts of the repo

The repository's MIT-licensed n8n workflows, AI agent
instructions, Python utilities, and samples orchestrate the
converters via subprocess calls. You may freely study, modify, and
redistribute the MIT-licensed orchestration files; you may NOT
redistribute the DDC binaries without a separate commercial
licence.

## Trademarks

Autodesk®, Revit® and AutoCAD® are registered trademarks or
trademarks of Autodesk, Inc., and/or its subsidiaries and/or
affiliates. IFC and buildingSMART® are trademarks of buildingSMART
International Ltd. File-format names (RVT, RFA, DWG, DXF, DGN) are
used only to identify file formats. DataDrivenConstruction is not
affiliated with, endorsed by, sponsored by, or certified by
Autodesk, Inc. DDC products are independent software and do not
contain or use Autodesk software or SDKs.

## Export control

Classified EAR99 under U.S. Export Administration Regulations
(15 CFR Parts 730-774) and subject to EU Regulation 2021/821 and
the German Außenwirtschaftsgesetz. Do not export to
jurisdictions subject to comprehensive U.S. or EU sanctions, or
to sanctioned persons. See [NOTICE](../NOTICE) for details.

## Contact

All enquiries (general, commercial licensing, security, privacy):
**info@datadrivenconstruction.io**
