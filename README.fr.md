<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ar.md">العربية</a>
</p>

# cad2data — convertisseurs DDC pour fichiers RVT, IFC et DWG

**Transformez vos fichiers CAO/BIM en données ouvertes et structurées — en local, hors ligne, sans licence CAO.**

<p align="center"><img src="docs/images/data-viewer-3d-grouped.png" width="100%" alt="DDC Data Viewer"></p>

## Nouveautés d'octobre 2026

Les convertisseurs reposent désormais sur des **lecteurs de formats propres à DataDrivenConstruction** (RVT : Rust ; IFC et DWG : Python) et ne dépendent plus d'aucun SDK CAO tiers. Les programmes de génération 18.x (`RvtExporter.exe`, `IfcExporter.exe`, `DwgExporter.exe`, `DgnExporter.exe`, `RVT2IFCconverter.exe`) sont retirés du dépôt ; les nouveaux paquets sont publiés sur la [page des releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases). Le DGN n'est plus pris en charge pour l'instant. Tous les nouveaux convertisseurs sont des préversions et produisent un rapport de ce qui a été lu, ignoré ou refusé.

## Convertisseurs

| Paquet | Version | Lit | Écrit |
|---|---|---|---|
| **DDC RVT Converter** | 0.6.8 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV |
| **DDC RVT to IFC** | 0.6.8 | `.rvt`, `.rfa` | IFC4 |
| **DDC IFC to Excel** | 0.3.1 preview | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC DWG to Excel** | 0.4.1 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 0.1.1 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

Tous les paquets fonctionnent hors ligne sous Windows 10/11 x64, sans logiciel Autodesk, Excel ni Python.

## Captures d'écran

Exécutions réelles des paquets actuels avec le bâtiment synthétique du visualiseur et l'exemple IFC ouvert de `Sample_Projects/`.

| | |
|---|---|
| ![](docs/images/data-viewer-3d-selection.png) | ![](docs/images/ifc-to-excel-table.png) |
| ![](docs/images/cli-rvt-ifc.png) | ![](docs/images/data-viewer-dark-ru.png) |

## Démarrage rapide

1. Téléchargez le paquet depuis la [dernière release](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest) (`*-Setup.exe` ou `*-portable.zip`) et vérifiez-le avec `SHA256SUMS.txt`.
2. Décompressez le paquet portable, par ex. dans `C:\DDC\`.
3. Lancez l'application ou utilisez la ligne de commande :

```powershell
# RVT / RFA -> GLB + IFC4 + properties (JSONL)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --properties --ifc

# IFC / IFCZIP -> Excel + JSONL + SQLite
C:\DDC\IFC-to-Exceluntime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out\Building"

# DWG -> Excel + CSV + JSONL + DXF + SVG
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"
```

Options, fichiers de sortie et codes de retour : [README anglais](README.md#command-line).

## Workflows n8n, notebooks et agents IA

Les workflows n8n et les notebooks ont été écrits pour la ligne de commande 18.x (XLSX + DAE) et sont en cours de portage. En attendant, adaptez le chemin du convertisseur et l'étape d'analyse (propriétés RVT dans `properties.jsonl`, géométrie en GLB). `AI_AGENTS_INSTRUCTIONS/` décrit déjà les nouvelles commandes.

## Limites

RVT : complétude géométrique non certifiée, pas de textures, IFC4 tessellé. IFC : pas d'IFCXML. DWG : certains types d'objets sont signalés comme non pris en charge plutôt que mal exportés ; consultez `report.json`. Windows x64 uniquement pour l'instant ; Linux / macOS — coming soon.

## Licence

Workflows, notebooks, scripts et documentation : [MIT](LICENSE). Paquets de convertisseurs : gratuits pour un usage privé et commercial selon l'EULA DataDrivenConstruction fournie ; voir [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) et [NOTICE](NOTICE).

## Marques

Autodesk®, Revit® et AutoCAD® sont des marques déposées d'Autodesk, Inc. IFC et buildingSMART® sont des marques de buildingSMART International Ltd. Les noms de formats (RVT, RFA, DWG, DXF, DGN) servent uniquement à identifier des formats de fichiers. DataDrivenConstruction n'est ni affiliée à Autodesk, Inc., ni approuvée ou certifiée par elle. Texte complet : [README.md](README.md#trademarks).
