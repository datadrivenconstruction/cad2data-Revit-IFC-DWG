<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
    <a href="README.pt-BR.md">Português (Brasil)</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ja.md">日本語</a> •
  <a href="README.ar.md">العربية</a>
</p>

<p align="center"><sub>Téléchargements trop lents ou GitHub bloqué ? Utilisez le miroir : <a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a> (mêmes fichiers, mêmes sommes SHA-256).</sub></p>

<h1 align="center">cad2data — convertisseurs DDC pour fichiers RVT, IFC et DWG</h1>

<p align="center">
  <b>Transformez vos fichiers CAO/BIM en données ouvertes et structurées — en local, hors ligne, sans licence CAO.</b><br>
  .rvt / .rfa → GLB · glTF · OBJ · IFC4 · JSONL/CSV &nbsp;|&nbsp; .ifc → Excel · JSONL · SQLite &nbsp;|&nbsp; .dwg → Excel · CSV · JSONL · DXF · SVG
</p>

<p align="center">
  <a href="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest"><img src="https://img.shields.io/github/v/release/datadrivenconstruction/cad2data-Revit-IFC-DWG?label=release" alt="Dernière version"></a>
  <img src="https://img.shields.io/badge/input-.rvt%20.rfa%20.ifc%20.ifczip%20.dwg-blue" alt="Formats d'entrée">
  <img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.jsonl%20.glb%20.ifc%20.dxf%20.svg-green" alt="Formats de sortie">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Windows x64 ; Linux x64 et arm64 ; macOS arm64 et x64">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT%20(workflows%2C%20docs)%20%2B%20non-commercial%20EULA%20(converters)-blue" alt="Licence"></a>
</p>

<p align="center">
  <img src="docs/images/data-viewer-3d-grouped.png" alt="DDC Data Viewer : tableau regroupé par catégorie et par niveau avec le modèle 3D lié" width="100%">
</p>

---

<a id="whats-new-in-ddc-converters-20"></a>
## Nouveautés de DDC Converters 2.0

DDC Converters 2.0 est la version d'octobre 2026 de toute la gamme : RVT Converter 2.0, RVT to IFC 2.0,
IFC to Excel 2.0, CAD Drawing to Excel 2.0, Data Viewer 2.0 et Excel Add-in 2.0.
La version actuelle de RVT Converter et RVT to IFC est la [2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2).

- **Un outil par famille de formats.** `.rvt` / `.rfa` vers GLB, glTF, OBJ, IFC4 et tables JSONL / CSV / SQLite ;
  `.ifc` / `.ifczip` vers Excel, JSONL et SQLite ; `.dwg` vers Excel, CSV, JSONL, DXF et SVG.
- **Les fichiers Revit 2016–2027** sont lus directement, sans installation de Revit.
- **Export IFC4 depuis Revit** avec jeux de propriétés, quantités, classification et matériaux, et les profils
  `full`, `coordination` et `geometry` ; options d'unités, d'origine, de catégories et de phases en ligne de commande.
- **Des identifiants d'élément partout.** Chaque nœud de géométrie conserve l'identifiant natif de l'élément, ce qui permet de relier tableaux et 3D par `ElementId`.
- **Un rapport pour chaque exécution.** `report.json` / `summary.json` indiquent, avec des compteurs, ce qui a été lu et ce qui a été ignoré.
- **Applications de bureau et ligne de commande** pour chaque convertisseur, codes de retour adaptés au traitement par lots et statut JSON sur une ligne pour les scripts.
- **DDC Data Viewer 2.0 :** visualiseur gratuit de tableaux et de 3D avec liaison dans les deux sens entre lignes et éléments.
- **Hors ligne et portable.** Windows 10/11 x64, rien à installer en dehors du paquet (installateur ou zip portable).
  Les convertisseurs en ligne de commande pour Linux (x64, arm64) et macOS (arm64, x64) ainsi que le Data Viewer se trouvent dans les [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1) (voir [DDC_LINUX_Converters](DDC_LINUX_Converters/README.md)).

Téléchargements : [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (portables, prêts à l'emploi) et la
[page des releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (installateurs et paquets).

<a id="contents"></a>
## Sommaire

- [Convertisseurs](#converters)
- [Captures d'écran](#screenshots)
- [Démarrage rapide](#quick-start)
- [Ligne de commande](#command-line)
- [Traitement par lots et automatisation](#batch-processing-and-automation)
- [DDC Data Viewer](#ddc-data-viewer)
- [Outils gratuits : contrôle des données, métrés, Power BI et Excel](#free-tools-data-check-quantity-take-off-power-bi-and-excel)
- [Workflows n8n, notebooks et agents IA](#n8n-workflows-notebooks-and-ai-agents)
- [Périmètre pris en charge et remarques](#supported-scope-and-notes)
- [Structure du dépôt](#repository-layout)
- [Licences](#licensing)
- [Marques](#trademarks)

<a id="converters"></a>
## Convertisseurs

| Paquet | Version | Lit | Écrit | Interface |
|---|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa` enregistrés par Revit 2016–2027 | GLB (par défaut), glTF, OBJ, IFC4, table des éléments (`elements.xlsx`, `elements.csv` : catégorie, famille, type, niveau, surface, volume, longueur, paramètres), propriétés enregistrées en JSONL ; l'application de bureau écrit aussi des tables CSV et SQLite | Application de bureau + CLI `RVTconverter.exe` |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4 avec jeux de propriétés, quantités, classification, matériaux ; profils `full`, `coordination`, `geometry` | Application de bureau (même ligne de commande que RVT Converter) |
| **DDC IFC to Excel** | 2.0 | fichiers STEP IFC2x3 / IFC4, `.ifczip` | `drawing.xlsx` (objets, propriétés, quantités), `data.jsonl`, `data.sqlite`, `result.json` | Application de bureau + ligne de commande |
| **DDC CAD Drawing to Excel** | 2.0 | dessins `.dwg`, versions de format R13–2018 | `.xlsx` (Entities, Summary, Layers, Blocks), `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json` | Application de bureau + CLI `dwg2excel.exe` |
| **DDC Data Viewer** | 2.0 | tables `.xlsx`, `.csv`, `.jsonl`, `.parquet` + géométrie `.glb` / `.dae` | vues filtrées vers XLSX / CSV | Application de bureau (gratuite) |

Chaque nœud de géométrie écrit par RVT Converter conserve l'identifiant natif de l'élément, ce qui permet de relier
tableaux et 3D par `ElementId`. Tous les paquets fonctionnent entièrement hors ligne sous Windows 10/11 x64 et n'exigent ni Excel
ni installation de Python. Les versions en ligne de commande pour Linux et macOS se trouvent dans la [release v2026.10.1](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1).

<a id="screenshots"></a>
## Captures d'écran

Toutes les captures d'écran ci-dessous proviennent d'exécutions réelles des paquets de la release actuelle. Elles utilisent des
modèles Revit d'exemple ouverts (licence MIT), le bâtiment d'exemple synthétique du visualiseur et l'exemple IFC ouvert de [`Sample_Projects/`](Sample_Projects/).

| | |
|---|---|
| ![RVT Converter 2.0.2 : conversion terminée de deux modèles Revit](docs/images/rvt-converter-done.png) | ![RVT to IFC 2.0.2 : panneau des options IFC](docs/images/rvt-to-ifc-options.png) |
| **DDC RVT Converter** — deux modèles Revit convertis ; le dossier de résultat est indiqué pour chaque fichier. | **DDC RVT to IFC** — unité de longueur, origine des coordonnées et autres réglages IFC dans *More options*. |
| ![Data Viewer : sélection 3D liée aux lignes du tableau](docs/images/data-viewer-3d-selection.png) | ![Sortie d'IFC to Excel dans le Data Viewer, regroupée par classe IFC](docs/images/ifc-to-excel-table.png) |
| **DDC Data Viewer** — un filtre sur *Structural Columns* met en évidence les éléments liés en 3D ; le panneau de synthèse totalise surface, volume et longueur. | **DDC IFC to Excel** — `drawing.xlsx` de l'exemple IFC ouvert Duplex, regroupé par classe IFC (333 objets, 23 classes). |
| ![Exécution en ligne de commande de RVTconverter](docs/images/cli-rvt-ifc.png) | ![Data Viewer en thème sombre](docs/images/data-viewer-dark.png) |
| **Ligne de commande** — `RVTconverter.exe` écrit le GLB, l'IFC4, la table des éléments et les rapports, puis affiche un résumé de statut. | **Thème sombre** — le Data Viewer en thème sombre, avec le sélecteur de langue de l'interface en haut à droite. |

<a id="quick-start"></a>
## Démarrage rapide

1. Ouvrez la [release 2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2) (RVT Converter, RVT to IFC) ou la [page des releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (autres paquets)
   et téléchargez le paquet dont vous avez besoin — un `*-Setup.exe` (installateur par utilisateur) ou un `*-portable.zip`.
2. Vérifiez le téléchargement avec `SHA256SUMS.txt` de la même release :
   ```powershell
   Get-FileHash .\DDC-RVT-Converter-*-portable.zip -Algorithm SHA256
   ```
3. Décompressez le paquet portable dans le dossier de votre choix, par exemple `C:\DDC\RVT-Converter\`,
   `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`. Conservez l'arborescence telle quelle.
4. Lancez l'application de bureau (`RVT Converter.exe`, `IFC to Excel.exe`, `DWG to Excel.exe`), déposez des fichiers ou
   des dossiers dans la fenêtre et cliquez sur *Convert* — ou utilisez la ligne de commande ci-dessous.
5. Ouvrez le résultat dans Excel, Python/pandas ou le [DDC Data Viewer](#ddc-data-viewer).

Windows SmartScreen peut demander une confirmation au premier lancement d'un nouveau téléchargement ; vérifiez la somme SHA-256 de la release.

<a id="command-line"></a>
## Ligne de commande

Les exemples ci-dessous ont été exécutés avec les binaires de la release actuelle. Les chemins supposent que les paquets
portables ont été décompressés dans `C:\DDC\`.

### DDC RVT Converter — `RVTconverter.exe`

```powershell
# GLB + reports into "Project.converted" next to the input (existing folders are never overwritten)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt"

# choose the output folder, add saved properties (JSONL) and an IFC4 file
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --properties --ifc

# IFC for coordination: millimetres, survey point origin, only doors and windows
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" --ifc --ifc-profile coordination `
    --ifc-units mm --ifc-origin survey-point --ifc-categories Doors,Windows

# additional geometry formats
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Family.rfa" --gltf --obj
```

| Sortie | Quand | Contenu |
|---|---|---|
| `native_graph.glb` | toujours | maillages 3D, un nœud par élément, nommé par ElementId |
| `summary.json`, `report.json` | toujours | statut, compteurs, omissions et diagnostics par élément |
| `properties.jsonl`, `property_scopes.jsonl` (+ manifestes) | `--properties` | paramètres enregistrés par élément (un objet JSON par ligne) |
| `native_graph.ifc`, `ifc.manifest.json`, `ifc.settings.json` | `--ifc` | IFC4 (géométrie tessellée, jeux de propriétés et de quantités) |
| `native_graph.gltf` + `.bin`, `native_graph.obj` + `.mtl` | `--gltf`, `--obj` | même géométrie que le GLB ; OBJ en mètres, axe Y vers le haut |

Codes de retour : `0` écrit sans lacune signalée, `2` écrit avec des lacunes signalées (ou arguments invalides),
`1` échec de conversion ou d'E/S. Lancez `RVTconverter.exe --help` pour toutes les options IFC
(`--ifc-config`, `--ifc-phase`, `--ifc-design-options`, `--ifc-exclude-categories`, …).

### DDC IFC to Excel

La ligne de commande du paquet portable :

```powershell
C:\DDC\IFC-to-Excel\runtime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py `
    "C:\Models\Building.ifc" --output "C:\Out\Building"
```

La commande affiche une ligne JSON (`"status": "CONVERTED"`, `"CONVERTED_WITH_LIMITS"` ou `"FAILED"`)
et crée un nouveau sous-dossier contenant `drawing.xlsx`, `data.jsonl`, `data.sqlite` et `result.json`.
Les fichiers `.ifczip` sont acceptés directement.

### DDC CAD Drawing to Excel — `dwg2excel.exe`

```powershell
# one or more drawings; a new sub-folder per drawing
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"

# a whole folder: tables only, one JSON line per file for scripts
$dwg = (Get-ChildItem C:\Drawings -Filter *.dwg).FullName
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe @dwg -o C:\Out --no-dxf --no-svg --json
```

Chaque dossier de dessin contient `<name>.xlsx`, `<name>.csv`, `<name>.jsonl`, `<name>.dxf`, `<name>.svg`,
`report.json` et `REPORT.txt`. La ligne affichée dans la console indique combien d'enregistrements ont été décodés, ignorés ou sont
d'un type non pris en charge. Autres options : `--timeout`, `--memory-limit-mb`,
`--language en|ru`, `--version`.

<a id="batch-processing-and-automation"></a>
## Traitement par lots et automatisation

**PowerShell — tous les fichiers RVT d'une arborescence de dossiers :**

```powershell
$exe = "C:\DDC\RVT-Converter\cli\RVTconverter.exe"
Get-ChildItem "C:\Projects" -Recurse -Include *.rvt | ForEach-Object {
    & $exe $_.FullName -o (Join-Path "C:\Out" $_.BaseName) --properties --ifc
    "{0}: exit {1}" -f $_.Name, $LASTEXITCODE
}
```

**Python — charger les propriétés RVT et les tables IFC avec pandas :**

```python
import json, subprocess, pandas as pd

subprocess.run([r"C:\DDC\RVT-Converter\cli\RVTconverter.exe", r"C:\Models\Project.rvt",
                "-o", r"C:\Out\Project", "--properties"], check=False)
rows = [json.loads(line) for line in open(r"C:\Out\Project\properties.jsonl", encoding="utf-8")]
print(len(rows), "property records")

objects = pd.read_excel(r"C:\Out\Building\Building-<id>\drawing.xlsx", sheet_name="Objects")
print(objects.groupby("Category").size().sort_values(ascending=False))
```

**DWG en CI ou dans des bots :** `dwg2excel.exe --json` affiche une ligne JSON par dessin ; analysez-la pour récupérer
le statut, le dossier de sortie et les statistiques de décodage.

<a id="ddc-data-viewer"></a>
## DDC Data Viewer

Un visualiseur de bureau gratuit pour la sortie des convertisseurs : grille virtualisée pour plus de 100 000 lignes, recherche, filtres,
regroupement avec sommes, sélecteur de colonnes, export de la vue courante en XLSX/CSV et panneau 3D qui relie
lignes et éléments dans les deux sens (GLB ou DAE). Anglais, allemand et russe ; thème clair et sombre.
Téléchargez `DDC-Data-Viewer-<version>-Setup.exe` ou le zip portable depuis la release.

<a id="free-tools-data-check-quantity-take-off-power-bi-and-excel"></a>
## Outils gratuits : contrôle des données, comparaison de modèles, tickets BCF, métrés, Power BI et Excel

[`ddc-tools/`](ddc-tools/) (Python 3.9+, MIT, hors ligne) travaille sur les tables écrites par les convertisseurs
(XLSX, CSV, JSONL, SQLite, JSON) :

- `ddc check` valide un export selon des règles YAML (paramètres obligatoires, expressions régulières, unicité, plages,
  valeurs autorisées) et écrit un XLSX à feux tricolores avec le détail par ElementId / GlobalId, un rapport JSON et un
  code de retour pour la CI.
- `ddc diff` compare deux exports d'un modèle (sortie du convertisseur RVT, IFC ou DWG) : éléments ajoutés / supprimés / modifiés,
  anciennes et nouvelles valeurs par propriété et par quantité, XLSX de journal des modifications, JSON, un GLB coloré selon l'état de modification et un code de retour pour la CI.
- `ddc bcf` écrit les constats de `ddc check` et `ddc diff` sous forme de fichiers de tickets BCF 2.1 / 3.0 (composants identifiés par IFC GlobalId) et
  met en tableau XLSX tout fichier BCF. BCF est un format ouvert de buildingSMART ; aucune certification n'est revendiquée.
- `ddc qto` totalise nombre, longueur, surface et volume par catégorie, type et niveau dans un XLSX mis en forme et signale
  les quantités manquantes ou nulles.
- [`ddc-tools/powerbi/`](ddc-tools/powerbi/) et [`ddc-tools/excel/`](ddc-tools/excel/) : scripts Power Query
  et classeur Excel qui lisent un dossier d'export entier, sans Python
  ([étapes](ddc-tools/docs/POWER_QUERY.md)).

```bash
pip install ./ddc-tools
ddc check Project.converted --rules ddc-tools/examples/rules_basic.yaml --xlsx check.xlsx
ddc qto Project.converted --xlsx qto.xlsx
ddc diff Model_v1.converted Model_v2.converted --xlsx changes.xlsx --glb diff.glb --bcf changes.bcf
```

Excel et Power BI sont des marques de Microsoft Corporation, utilisées uniquement pour indiquer avec quoi les fichiers fonctionnent.

<a id="n8n-workflows-notebooks-and-ai-agents"></a>
## Workflows n8n, notebooks et agents IA

- [`DDC_n8n_Workflows&Pipelines/`](DDC_n8n_Workflows&Pipelines/) — neuf workflows n8n (conversion,
  validation par lots, classification par IA, estimation des coûts et du CO2, rapports de métrés).
- [`DDC_in_additon/DDC_python_pipelines/`](DDC_in_additon/DDC_python_pipelines/) — notebooks Jupyter pour
  la conversion, le traitement par lots et l'analyse.

> **Configuration :** les workflows et notebooks appellent les convertisseurs de [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) via `ddc convert` /
> `ddc table` (outil gratuit [`ddc-tools/`](ddc-tools/)), qui construit la table à plat (`<name>_rvt.xlsx`, feuille `Project_Data` :
> `ID`, `Category`, `Type Name`, `Level`, `Volume`, ...) à partir de la sortie `properties.jsonl` / IFC / DWG ; la géométrie 3D est au format GLB.
> Configuration unique : `pip install ddc-tools\`. Le `README.md` placé à côté des workflows et des notebooks indique ce qui a été vérifié et ce qui n'est
> pas couvert (par exemple : les étapes IA de n8n 5-7 nécessitent vos identifiants ; les planifications et les PDF de planches n'ont pas
> d'équivalent ; les quantités Revit proviennent des quantités IFC ou du maillage GLB).

- [`AI_AGENTS_INSTRUCTIONS/`](AI_AGENTS_INSTRUCTIONS/) — contexte prêt à l'emploi pour les agents de programmation
  (agents IA de programmation) avec les lignes de commande actuelles. Ouvrez le dépôt dans votre
  agent et demandez, par exemple, *"convert every .rvt in C:\Projects to IFC and summarise the reports"*.
- [DDC Skills for AI agents](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
  — automatisations prêtes à l'emploi pour les données de la construction.

<a id="supported-scope-and-notes"></a>
## Périmètre pris en charge et remarques

- **RVT :** les textures ne sont pas exportées ; l'export IFC écrit de l'IFC4 tessellé. Les éléments qui ne peuvent pas être
  représentés sont listés dans le rapport d'exécution.
- **IFC :** fichiers STEP IFC2x3 et IFC4 et `.ifczip` ; IFCXML n'est pas pris en charge. Les enregistrements d'origine restent toujours dans
  `data.jsonl` / `data.sqlite`.
- **DWG :** dessins R13–2018. Certains types d'objets (par exemple certains tableaux, multilignes de repère, solides 3D,
  images) sont listés comme *unsupported* dans `report.json` au lieu d'être exportés de façon incorrecte.
- **Plateformes :** Windows 10/11 x64. **Linux (x64, arm64) et macOS (arm64, x64) : convertisseurs en ligne de commande et Data Viewer, voir les [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1).**

Les rapports de bogues accompagnés d'un petit fichier d'exemple sont les bienvenus — utilisez
[GitHub Issues](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues) et ne joignez pas
de modèles confidentiels.

<a id="repository-layout"></a>
## Structure du dépôt

| Chemin | Contenu |
|---|---|
| `docs/` | notes de version, captures d'écran |
| `ddc-tools/` | outils gratuits de contrôle des données, comparaison de modèles, tickets BCF, métrés, kit Power BI et Excel |
| `DDC_n8n_Workflows&Pipelines/` | fichiers JSON de workflows n8n |
| `DDC_in_additon/` | notebooks, présentations, images |
| `AI_AGENTS_INSTRUCTIONS/` | instructions pour les agents IA de programmation |
| `DDC_WINDOWS_Converters/` | convertisseurs Windows portables (RVT, RVT-to-IFC, IFC to Excel, CAD Drawing to Excel, Data Viewer), textes de licence et documentation du complément Excel → Revit ; les installateurs sont sur la page des Releases |
| `DDC_LINUX_Converters/` | paquets de données CWICR, packaging Qdrant et tableau de bord de télémétrie |
| `Sample_Projects/` | fichiers IFC d'exemple ouverts |

<a id="licensing"></a>
## Licences

- **Workflows, notebooks, scripts, instructions IA, documentation et `ddc-tools`** — [licence MIT](LICENSE).
  Open source, usage commercial autorisé.
- **Convertisseurs DDC** (paquets binaires sur les Releases et dans `DDC_WINDOWS_Converters/` / `DDC_LINUX_Converters/`) —
  logiciel propriétaire, **gratuit pour un usage non commercial uniquement**. **Un usage commercial nécessite une licence sur demande :**
  [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io). Conditions : [EULA](EULA.md),
  [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) et [NOTICE](NOTICE). Les composants open source tiers
  et leurs licences sont listés dans `licenses/` à l'intérieur de chaque paquet.
- La licence MIT de `ddc-tools` ne s'étend pas aux convertisseurs qu'il appelle.

**Usage commercial** désigne tout usage par ou pour le compte d'une entreprise, d'une société, d'un professionnel indépendant, d'une autorité
publique ou de toute autre organisation (y compris ses employés ou sous-traitants) ; dans le cadre d'un travail ou de services rémunérés, y compris le
traitement de fichiers pour des clients ; dans un projet qui génère ou est destiné à générer des revenus ; ou au sein d'un
produit, service, pipeline ou offre SaaS mis à la disposition de tiers. La redistribution, l'intégration OEM et SaaS
sont également couvertes.
**Usage non commercial** désigne l'apprentissage personnel et les loisirs, la recherche universitaire, l'enseignement et l'étude par
des étudiants et des enseignants, et l'évaluation par des organisations à but non lucratif, dans chaque cas sans paiement, revenu
ni but commercial.

Signalement de failles de sécurité : voir [SECURITY.md](SECURITY.md). Brevets, marques et contrôle des exportations :
[PATENTS.md](PATENTS.md), [TRADEMARK.md](TRADEMARK.md), [EXPORT-COMPLIANCE.md](EXPORT-COMPLIANCE.md).

<a id="consulting-and-training"></a>
## Conseil et formation

DataDrivenConstruction aide les entreprises de la construction, de l'ingénierie et de la technologie à automatiser le traitement des données
CAO/BIM et à bâtir des pipelines ETL ouverts — ateliers, conseil et prototypes sur vos données réelles.
Contact : [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io) ou
[datadrivenconstruction.io](https://datadrivenconstruction.io).

<p>
  <a href="https://x.com/datadrivenconst"><img src="https://img.shields.io/twitter/follow/datadrivenconst?logo=X&style=flat&color=%23f5f5f5" alt="Suivre sur X"></a>
  <a href="https://www.youtube.com/@datadrivenconstruction"><img src="https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://www.linkedin.com/company/78381569"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?logoColor=white" alt="LinkedIn"></a>
</p>

Si ces outils vous sont utiles, mettez une étoile au dépôt pour être informé des nouvelles releases.

<a id="trademarks"></a>
## Marques

Autodesk et Revit sont des marques d'Autodesk, Inc. DataDrivenConstruction est un logiciel indépendant, non affilié à Autodesk, Inc. et non approuvé par celle-ci. RVT, RFA, DWG, DXF et IFC sont des noms de formats de fichiers utilisés uniquement pour indiquer quels fichiers sont lus.
