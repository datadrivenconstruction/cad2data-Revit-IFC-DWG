<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.pt-BR.md">Português (Brasil)</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ja.md">日本語</a> •
  <a href="README.ar.md">العربية</a>
</p>

<p align="center"><sub>GitHub lent ou bloqué ? Utilisez le miroir : <a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a> (mêmes fichiers, mêmes sommes SHA-256).</sub></p>

# cad2data — convertisseurs DDC pour fichiers RVT, IFC et DWG

**Transformez vos fichiers CAO/BIM en données ouvertes et structurées — en local, hors ligne, sans licence CAO.**

<p align="center"><img src="docs/images/data-viewer-3d-grouped.png" width="100%" alt="DDC Data Viewer"></p>

## Nouveautés de DDC Converters 2.0

La version d'octobre 2026 de toute la gamme : RVT Converter 2.0, RVT to IFC 2.0, IFC to Excel 2.0, CAD Drawing to Excel 2.0, Data Viewer 2.0 et Excel Add-in 2.0.

- **Un outil par famille de formats.** `.rvt` / `.rfa` vers GLB, glTF, OBJ, IFC4 et tables JSONL / CSV / SQLite ; `.ifc` / `.ifczip` vers Excel, JSONL et SQLite ; `.dwg` vers Excel, CSV, JSONL, DXF et SVG.
- **Revit 2019–2027** est lu directement, sans logiciel Autodesk ni licence CAO.
- **Export IFC4 depuis Revit** avec jeux de propriétés, quantités, classification et matériaux, et les profils `full`, `coordination` et `geometry` ; unités, origine, catégories et phases en ligne de commande.
- **Des identifiants d'élément partout.** Chaque nœud de géométrie conserve l'identifiant natif de l'élément, ce qui permet de relier tableaux et 3D par `ElementId`.
- **Un rapport par exécution.** `report.json` / `summary.json` indiquent, avec des compteurs, ce qui a été lu et ce qui a été ignoré.
- **Applications de bureau et ligne de commande** pour chaque convertisseur, codes de retour adaptés au traitement par lots et statut JSON sur une ligne pour les scripts.
- **DDC Data Viewer 2.0 :** visualiseur gratuit de tableaux et de 3D avec liaison dans les deux sens entre lignes et éléments.
- **Hors ligne et portable.** Windows 10/11 x64 ; seul le paquet est à installer (installateur ou zip portable). Versions Linux / macOS — coming soon.

Téléchargements : [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (portables, prêts à l'emploi) et la [page des releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (installateurs et paquets).

## Convertisseurs

| Paquet | Version | Lit | Écrit |
|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV / SQLite |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4 (jeux de propriétés, quantités, classification, matériaux) |
| **DDC IFC to Excel** | 2.0 | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC CAD Drawing to Excel** | 2.0 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 2.0 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

Chaque nœud de géométrie écrit par RVT Converter conserve l'identifiant natif de l'élément, ce qui permet de relier tableaux et 3D par `ElementId`. Tous les paquets fonctionnent hors ligne sous Windows 10/11 x64, sans logiciel Autodesk, Excel ni Python. Versions Linux / macOS — coming soon.

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

Les workflows n8n (`DDC_n8n_Workflows&Pipelines/`) et les notebooks Jupyter appellent les convertisseurs via `ddc convert` / `ddc table` (outil gratuit [`ddc-tools/`](ddc-tools/)), qui construit le tableau plat (`*_rvt.xlsx`, feuille `Project_Data`) à partir de la sortie des convertisseurs ; la géométrie 3D est au format GLB. Installation unique : `pip install ddc-tools\`. Ce qui a été vérifié et ce qui n'est pas couvert figure dans le `README.md` à côté des workflows et des notebooks. `AI_AGENTS_INSTRUCTIONS/` fournit le contexte avec les lignes de commande actuelles.

## Périmètre pris en charge et remarques

- **RVT :** les textures ne sont pas exportées ; l'export IFC écrit de l'IFC4 tessellé. Les éléments qui ne peuvent pas être représentés figurent dans le rapport d'exécution.
- **IFC :** fichiers IFC2x3 et IFC4 STEP et `.ifczip` ; IFCXML n'est pas pris en charge. Les enregistrements d'origine restent toujours dans `data.jsonl` / `data.sqlite`.
- **DWG :** dessins R13–2018. Certains types d'objets (par exemple certains tableaux, multilignes de repère, solides 3D, images) sont indiqués dans `report.json` comme *non pris en charge* plutôt que mal exportés.
- **Plateformes :** Windows 10/11 x64. **Linux / macOS — coming soon.**

## Licence

Workflows, notebooks, scripts, documentation et `ddc-tools` : [MIT](LICENSE) (open source, y compris pour un usage commercial). Paquets de convertisseurs (binaires DDC) : propriétaires et **gratuits uniquement pour un usage non commercial** ; l'usage commercial exige une licence sur demande : info@datadrivenconstruction.io. Voir [EULA](EULA.md), [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) et [NOTICE](NOTICE). La licence MIT de `ddc-tools` ne s'étend pas aux convertisseurs qu'il appelle.

**Usage commercial** : tout usage par ou pour une entreprise, un indépendant, une administration ou une autre organisation (y compris ses employés), dans un travail ou un service rémunéré (y compris le traitement de fichiers pour des clients), dans un projet générant ou destiné à générer des revenus, ou au sein d'un produit, service, pipeline ou offre SaaS destiné à des tiers. **Usage non commercial** : apprentissage personnel, recherche académique, enseignement et études, et évaluation par des organisations à but non lucratif, dans chaque cas sans paiement, revenu ni but professionnel.

## Marques

Autodesk®, Revit® et AutoCAD® sont des marques déposées d'Autodesk, Inc. IFC et buildingSMART® sont des marques de buildingSMART International Ltd. Les noms de formats (RVT, RFA, DWG, DXF, DGN) servent uniquement à identifier des formats de fichiers. DataDrivenConstruction n'est ni affiliée à Autodesk, Inc., ni approuvée ou certifiée par elle. Texte complet : [README.md](README.md#trademarks).
