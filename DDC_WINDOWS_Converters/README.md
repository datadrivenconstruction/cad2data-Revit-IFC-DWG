# DDC Windows Converters — Proprietary Software

> **The files in this folder are NOT MIT-licensed.**
> They are proprietary software licensed under the
> DataDrivenConstruction Proprietary Software License and the
> DataDrivenConstruction Terms of Use and EULA at
> <https://datadrivenconstruction.io/term-of-use-and-eula/>.
>
> See [LICENSE-PROPRIETARY.txt](./LICENSE-PROPRIETARY.txt) and
> [EULA.txt](./EULA.txt) in this folder, and [NOTICE](../NOTICE)
> at the repository root, for the full terms.

## What is in this folder

| Sub-directory                      | Purpose                                           |
|------------------------------------|---------------------------------------------------|
| `DDC_CONVERTER_REVIT/`             | Revit (RVT) → structured data                     |
| `DDC_CONVERTER_Revit2IFC/`         | Revit (RVT) → IFC                                 |
| `DDC_CONVERTER_IFC/`               | IFC → structured data                             |
| `DDC_CONVERTER_DWG/`               | AutoCAD (DWG) → structured data                   |
| `DDC_CONVERTER_DGN/`               | MicroStation (DGN) → structured data              |
| `DDC_Update_Revit_from_Excel/`     | Round-trip updates from tabular data into Revit   |

Each sub-directory bundles one or more binary executables
(`*.exe`) together with Qt runtime libraries (`Qt6Core.dll`,
`Qt6Gui.dll`, `Qt6Widgets.dll`, etc.) and a local `LICENSE` file
carrying the third-party component attributions that apply to
those specific binaries (reference, Qt, and others).

## How these binaries relate to the MIT-licensed parts of the repo

The repository's MIT-licensed n8n workflows, AI agent
instructions, Python utilities, and samples orchestrate these
binaries via subprocess calls. You may freely study, modify, and
redistribute the MIT-licensed orchestration files; you may NOT
redistribute these binaries without a separate commercial
licence.

## Export control

Classified EAR99 under U.S. Export Administration Regulations
(15 CFR Parts 730-774) and subject to EU Regulation 2021/821 and
the German Außenwirtschaftsgesetz. Do not export to
jurisdictions subject to comprehensive U.S. or EU sanctions, or
to sanctioned persons. See [NOTICE](../NOTICE) for details.

## Contact

All enquiries (general, commercial licensing, security, privacy):
**info@datadrivenconstruction.io**
