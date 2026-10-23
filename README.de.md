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

<p align="center"><sub>Downloads zu langsam oder GitHub gesperrt? Nutzen Sie den Spiegel: <a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a> (gleiche Dateien, gleiche SHA-256-Summen).</sub></p>

<h1 align="center">cad2data — DDC-Konverter für RVT-, IFC- und DWG-Dateien</h1>

<p align="center">
  <b>CAD/BIM-Dateien in offene, strukturierte Daten umwandeln — lokal, offline, ohne CAD-Lizenzen.</b><br>
  .rvt / .rfa → GLB · glTF · OBJ · IFC4 · JSONL/CSV &nbsp;|&nbsp; .ifc → Excel · JSONL · SQLite &nbsp;|&nbsp; .dwg → Excel · CSV · JSONL · DXF · SVG
</p>

<p align="center">
  <a href="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest"><img src="https://img.shields.io/github/v/release/datadrivenconstruction/cad2data-Revit-IFC-DWG?label=release" alt="Neuester Release"></a>
  <img src="https://img.shields.io/badge/input-.rvt%20.rfa%20.ifc%20.ifczip%20.dwg-blue" alt="Eingabeformate">
  <img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.jsonl%20.glb%20.ifc%20.dxf%20.svg-green" alt="Ausgabeformate">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Windows x64; Linux x64 und arm64; macOS arm64 und x64">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT%20(workflows%2C%20docs)%20%2B%20non-commercial%20EULA%20(converters)-blue" alt="Lizenz"></a>
</p>

<p align="center">
  <img src="docs/images/data-viewer-3d-grouped.png" alt="DDC Data Viewer: nach Kategorie und Geschoss gruppierte Tabelle mit dem verknüpften 3D-Modell" width="100%">
</p>

---

<a id="whats-new-in-ddc-converters-20"></a>
## Neu in DDC Converters 2.0

DDC Converters 2.0 ist der Release der gesamten Produktlinie vom Oktober 2026: RVT Converter 2.0, RVT to IFC 2.0,
IFC to Excel 2.0, CAD Drawing to Excel 2.0, Data Viewer 2.0 und Excel Add-in 2.0.
Der aktuelle Build von RVT Converter und RVT to IFC ist [2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2).

- **Ein Werkzeug pro Formatfamilie.** `.rvt` / `.rfa` nach GLB, glTF, OBJ, IFC4 und JSONL- / CSV- / SQLite-Tabellen;
  `.ifc` / `.ifczip` nach Excel, JSONL und SQLite; `.dwg` nach Excel, CSV, JSONL, DXF und SVG.
- **Revit-2016–2027-Dateien** werden direkt gelesen, ohne installiertes Revit.
- **IFC4-Export aus Revit** mit Property Sets, Mengen, Klassifikation und Materialien sowie den Profilen
  `full`, `coordination` und `geometry`; Optionen für Einheiten, Ursprung, Kategorien und Phasen auf der Kommandozeile.
- **Element-IDs überall.** Jeder Geometrieknoten behält die native Element-ID, sodass Tabellen und 3D über `ElementId` verknüpft werden.
- **Ein Bericht für jeden Lauf.** `report.json` / `summary.json` listen mit Zählwerten auf, was gelesen und was übersprungen wurde.
- **Desktop-Apps und Kommandozeile** für jeden Konverter, stapelfreundliche Exit-Codes und eine einzeilige JSON-Statusmeldung für Skripte.
- **DDC Data Viewer 2.0:** kostenloser Tabellen- und 3D-Viewer mit wechselseitiger Verknüpfung von Zeilen und Elementen.
- **Offline und portabel.** Windows 10/11 x64, außer dem Paket (Installer oder portables Zip) ist nichts zu installieren.
  Kommandozeilen-Konverter und Data Viewer für Linux (x64, arm64) und macOS (arm64, x64) finden Sie unter [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1) (siehe [DDC_LINUX_Converters](DDC_LINUX_Converters/README.md)).

Downloads: [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (portabel, sofort startbereit) und die
[Releases-Seite](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (Installer und Pakete).

<a id="contents"></a>
## Inhalt

- [Konverter](#converters)
- [Screenshots](#screenshots)
- [Schnellstart](#quick-start)
- [Kommandozeile](#command-line)
- [Stapelverarbeitung und Automatisierung](#batch-processing-and-automation)
- [DDC Data Viewer](#ddc-data-viewer)
- [Kostenlose Werkzeuge: Datenprüfung, Mengenermittlung, Power BI und Excel](#free-tools-data-check-quantity-take-off-power-bi-and-excel)
- [n8n-Workflows, Notebooks und KI-Agenten](#n8n-workflows-notebooks-and-ai-agents)
- [Unterstützter Umfang und Hinweise](#supported-scope-and-notes)
- [Repository-Struktur](#repository-layout)
- [Lizenzierung](#licensing)
- [Marken](#trademarks)

<a id="converters"></a>
## Konverter

| Paket | Version | Liest | Schreibt | Oberfläche |
|---|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa`, gespeichert mit Revit 2016–2027 | GLB (Standard), glTF, OBJ, IFC4, Elementtabelle (`elements.xlsx`, `elements.csv`: Kategorie, Familie, Typ, Geschoss, Fläche, Volumen, Länge, Parameter), gespeicherte Eigenschaften als JSONL; die Desktop-App schreibt zusätzlich CSV-Tabellen und SQLite | Desktop-App + CLI `RVTconverter.exe` |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4 mit Property Sets, Mengen, Klassifikation, Materialien; Profile `full`, `coordination`, `geometry` | Desktop-App (gleiche Kommandozeile wie RVT Converter) |
| **DDC IFC to Excel** | 2.0 | IFC2x3- / IFC4-STEP-Dateien, `.ifczip` | `drawing.xlsx` (Objekte, Eigenschaften, Mengen), `data.jsonl`, `data.sqlite`, `result.json` | Desktop-App + Kommandozeile |
| **DDC CAD Drawing to Excel** | 2.0 | `.dwg`-Zeichnungen, Formatversionen R13–2018 | `.xlsx` (Entities, Summary, Layers, Blocks), `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json` | Desktop-App + CLI `dwg2excel.exe` |
| **DDC Data Viewer** | 2.0 | Tabellen `.xlsx`, `.csv`, `.jsonl`, `.parquet` + Geometrie `.glb` / `.dae` | gefilterte Ansichten als XLSX / CSV | Desktop-App (kostenlos) |

Jeder vom RVT Converter geschriebene Geometrieknoten behält die native Element-ID, sodass Tabellen und 3D über
`ElementId` verknüpft werden können. Alle Pakete laufen vollständig offline unter Windows 10/11 x64 und benötigen weder Excel
noch eine Python-Installation. Kommandozeilen-Builds für Linux und macOS finden Sie im [Release v2026.10.1](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1).

<a id="screenshots"></a>
## Screenshots

Alle folgenden Screenshots stammen aus echten Läufen der Pakete des aktuellen Releases. Sie verwenden offene
Revit-Beispielmodelle (MIT-Lizenz), das synthetische Beispielgebäude des Viewers und das offene IFC-Beispiel in [`Sample_Projects/`](Sample_Projects/).

| | |
|---|---|
| ![RVT Converter 2.0.2: abgeschlossene Konvertierung von zwei Revit-Modellen](docs/images/rvt-converter-done.png) | ![RVT to IFC 2.0.2: Optionsbereich für IFC](docs/images/rvt-to-ifc-options.png) |
| **DDC RVT Converter** — zwei Revit-Modelle konvertiert; der Ergebnisordner wird pro Datei aufgelistet. | **DDC RVT to IFC** — Längeneinheit, Koordinatenursprung und weitere IFC-Einstellungen unter *More options*. |
| ![Data Viewer: 3D-Auswahl verknüpft mit Tabellenzeilen](docs/images/data-viewer-3d-selection.png) | ![Ausgabe von IFC to Excel im Data Viewer, gruppiert nach IFC-Klasse](docs/images/ifc-to-excel-table.png) |
| **DDC Data Viewer** — ein Filter auf *Structural Columns* hebt die verknüpften Elemente in 3D hervor; der Summenbereich addiert Fläche, Volumen und Länge. | **DDC IFC to Excel** — `drawing.xlsx` des offenen IFC-Beispiels Duplex, gruppiert nach IFC-Klasse (333 Objekte, 23 Klassen). |
| ![Lauf von RVTconverter auf der Kommandozeile](docs/images/cli-rvt-ifc.png) | ![Data Viewer im dunklen Design](docs/images/data-viewer-dark.png) |
| **Kommandozeile** — `RVTconverter.exe` schreibt GLB, IFC4, die Elementtabelle und Berichte und gibt eine Statuszusammenfassung aus. | **Dunkles Design** — der Data Viewer im dunklen Design, mit dem Umschalter für die Oberflächensprache oben rechts. |

<a id="quick-start"></a>
## Schnellstart

1. Öffnen Sie den [Release 2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2) (RVT Converter, RVT to IFC) oder die [Releases-Seite](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (übrige Pakete)
   und laden Sie das gewünschte Paket herunter — eine `*-Setup.exe` (Installer pro Benutzer) oder ein `*-portable.zip`.
2. Prüfen Sie den Download anhand von `SHA256SUMS.txt` aus demselben Release:
   ```powershell
   Get-FileHash .\DDC-RVT-Converter-*-portable.zip -Algorithm SHA256
   ```
3. Entpacken Sie das portable Paket in einen Ordner Ihrer Wahl, zum Beispiel `C:\DDC\RVT-Converter\`,
   `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`. Behalten Sie die Ordnerstruktur bei.
4. Starten Sie die Desktop-App (`RVT Converter.exe`, `IFC to Excel.exe`, `DWG to Excel.exe`), ziehen Sie Dateien oder
   Ordner in das Fenster und klicken Sie auf *Convert* — oder verwenden Sie die folgende Kommandozeile.
5. Öffnen Sie das Ergebnis in Excel, Python/pandas oder im [DDC Data Viewer](#ddc-data-viewer).

Windows SmartScreen kann beim ersten Start eines neuen Downloads um Bestätigung bitten; prüfen Sie die SHA-256-Summe aus dem Release.

<a id="command-line"></a>
## Kommandozeile

Die folgenden Beispiele wurden mit den Binärdateien des aktuellen Releases ausgeführt. Die Pfade setzen voraus, dass die portablen
Pakete nach `C:\DDC\` entpackt wurden.

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

| Ausgabe | Wann | Inhalt |
|---|---|---|
| `native_graph.glb` | immer | 3D-Meshes, ein Knoten pro Element, benannt nach ElementId |
| `summary.json`, `report.json` | immer | Status, Zählwerte, Auslassungen und Diagnosen pro Element |
| `properties.jsonl`, `property_scopes.jsonl` (+ Manifeste) | `--properties` | gespeicherte Parameter pro Element (ein JSON-Objekt pro Zeile) |
| `native_graph.ifc`, `ifc.manifest.json`, `ifc.settings.json` | `--ifc` | IFC4 (tesselierte Geometrie, Property- und Mengensets) |
| `native_graph.gltf` + `.bin`, `native_graph.obj` + `.mtl` | `--gltf`, `--obj` | gleiche Geometrie wie GLB; OBJ in Metern, Y-up |

Exit-Codes: `0` ohne gemeldete Lücken geschrieben, `2` mit gemeldeten Lücken geschrieben (oder ungültige Argumente),
`1` Konvertierungs- oder E/A-Fehler. Mit `RVTconverter.exe --help` sehen Sie alle IFC-Optionen
(`--ifc-config`, `--ifc-phase`, `--ifc-design-options`, `--ifc-exclude-categories`, …).

### DDC IFC to Excel

Die Kommandozeile des portablen Pakets:

```powershell
C:\DDC\IFC-to-Excel\runtime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py `
    "C:\Models\Building.ifc" --output "C:\Out\Building"
```

Der Befehl gibt eine JSON-Zeile aus (`"status": "CONVERTED"`, `"CONVERTED_WITH_LIMITS"` oder `"FAILED"`)
und legt einen neuen Unterordner mit `drawing.xlsx`, `data.jsonl`, `data.sqlite` und `result.json` an.
`.ifczip`-Dateien werden direkt akzeptiert.

### DDC CAD Drawing to Excel — `dwg2excel.exe`

```powershell
# one or more drawings; a new sub-folder per drawing
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"

# a whole folder: tables only, one JSON line per file for scripts
$dwg = (Get-ChildItem C:\Drawings -Filter *.dwg).FullName
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe @dwg -o C:\Out --no-dxf --no-svg --json
```

Jeder Zeichnungsordner enthält `<name>.xlsx`, `<name>.csv`, `<name>.jsonl`, `<name>.dxf`, `<name>.svg`,
`report.json` und `REPORT.txt`. Die Konsolenzeile meldet, wie viele Datensätze dekodiert, übersprungen wurden oder
von einem nicht unterstützten Typ sind. Weitere Optionen: `--timeout`, `--memory-limit-mb`,
`--language en|ru`, `--version`.

<a id="batch-processing-and-automation"></a>
## Stapelverarbeitung und Automatisierung

**PowerShell — jede RVT-Datei in einem Ordnerbaum:**

```powershell
$exe = "C:\DDC\RVT-Converter\cli\RVTconverter.exe"
Get-ChildItem "C:\Projects" -Recurse -Include *.rvt | ForEach-Object {
    & $exe $_.FullName -o (Join-Path "C:\Out" $_.BaseName) --properties --ifc
    "{0}: exit {1}" -f $_.Name, $LASTEXITCODE
}
```

**Python — RVT-Eigenschaften und IFC-Tabellen mit pandas laden:**

```python
import json, subprocess, pandas as pd

subprocess.run([r"C:\DDC\RVT-Converter\cli\RVTconverter.exe", r"C:\Models\Project.rvt",
                "-o", r"C:\Out\Project", "--properties"], check=False)
rows = [json.loads(line) for line in open(r"C:\Out\Project\properties.jsonl", encoding="utf-8")]
print(len(rows), "property records")

objects = pd.read_excel(r"C:\Out\Building\Building-<id>\drawing.xlsx", sheet_name="Objects")
print(objects.groupby("Category").size().sort_values(ascending=False))
```

**DWG in CI oder Bots:** `dwg2excel.exe --json` gibt pro Zeichnung eine JSON-Zeile aus; werten Sie sie aus, um
Status, Ausgabeordner und Dekodierstatistik zu erfassen.

<a id="ddc-data-viewer"></a>
## DDC Data Viewer

Ein kostenloser Desktop-Viewer für die Ausgabe der Konverter: virtualisiertes Raster für über 100.000 Zeilen, Suche, Filter,
Gruppierung mit Summen, Spaltenauswahl, Export der aktuellen Ansicht nach XLSX/CSV und ein 3D-Bereich, der
Zeilen und Elemente in beide Richtungen verknüpft (GLB oder DAE). Englisch, Deutsch und Russisch; helles und dunkles Design.
Laden Sie `DDC-Data-Viewer-<version>-Setup.exe` oder das portable Zip aus dem Release herunter.

<a id="free-tools-data-check-quantity-take-off-power-bi-and-excel"></a>
## Kostenlose Werkzeuge: Datenprüfung, Modellvergleich, BCF-Issues, Mengenermittlung, Power BI und Excel

[`ddc-tools/`](ddc-tools/) (Python 3.9+, MIT, offline) arbeitet mit den Tabellen, die die Konverter schreiben
(XLSX, CSV, JSONL, SQLite, JSON):

- `ddc check` prüft einen Export anhand von YAML-Regeln (erforderliche Parameter, Regex, Eindeutigkeit, Wertebereiche,
  erlaubte Werte) und schreibt eine Ampel-XLSX mit Details zu ElementId / GlobalId, einen JSON-Bericht und einen
  Exit-Code für CI.
- `ddc diff` vergleicht zwei Exporte eines Modells (Ausgabe des RVT-, IFC- oder DWG-Konverters): hinzugefügte / entfernte / geänderte Elemente,
  alte und neue Werte je Eigenschaft und Menge, Änderungsprotokoll als XLSX, JSON, ein nach Änderungsstatus eingefärbtes GLB und ein Exit-Code für CI.
- `ddc bcf` schreibt die Befunde von `ddc check` und `ddc diff` als BCF-2.1- / 3.0-Issue-Dateien (Komponenten über IFC-GlobalId) und
  tabelliert jede BCF-Datei in XLSX. BCF ist ein offenes Format von buildingSMART; eine Zertifizierung wird nicht beansprucht.
- `ddc qto` summiert Anzahl, Länge, Fläche und Volumen nach Kategorie, Typ und Geschoss in eine formatierte XLSX und warnt
  vor fehlenden oder auf null stehenden Mengen.
- [`ddc-tools/powerbi/`](ddc-tools/powerbi/) und [`ddc-tools/excel/`](ddc-tools/excel/): Power-Query-Skripte
  und eine Excel-Arbeitsmappe, die einen ganzen Exportordner lesen, ohne Python
  ([Schritte](ddc-tools/docs/POWER_QUERY.md)).

```bash
pip install ./ddc-tools
ddc check Project.converted --rules ddc-tools/examples/rules_basic.yaml --xlsx check.xlsx
ddc qto Project.converted --xlsx qto.xlsx
ddc diff Model_v1.converted Model_v2.converted --xlsx changes.xlsx --glb diff.glb --bcf changes.bcf
```

Excel und Power BI sind Marken der Microsoft Corporation und werden nur verwendet, um anzugeben, womit die Dateien funktionieren.

<a id="n8n-workflows-notebooks-and-ai-agents"></a>
## n8n-Workflows, Notebooks und KI-Agenten

- [`DDC_n8n_Workflows&Pipelines/`](DDC_n8n_Workflows&Pipelines/) — neun n8n-Workflows (Konvertierung,
  Stapelvalidierung, KI-Klassifizierung, Kosten- und CO2-Schätzung, QTO-Berichte).
- [`DDC_in_additon/DDC_python_pipelines/`](DDC_in_additon/DDC_python_pipelines/) — Jupyter-Notebooks für
  Konvertierung, Stapelverarbeitung und Analysen.

> **Einrichtung:** Die Workflows und Notebooks rufen die Konverter in [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) über `ddc convert` /
> `ddc table` auf (kostenloses Werkzeug [`ddc-tools/`](ddc-tools/)); dieses erstellt die flache Tabelle (`<name>_rvt.xlsx`, Blatt `Project_Data`:
> `ID`, `Category`, `Type Name`, `Level`, `Volume`, ...) aus der Ausgabe von `properties.jsonl` / IFC / DWG; 3D-Geometrie ist GLB.
> Einmalige Einrichtung: `pip install ddc-tools\`. Die `README.md` neben den Workflows und Notebooks sagt, was geprüft wurde und was
> nicht abgedeckt ist (zum Beispiel: Die KI-Schritte von n8n 5-7 benötigen Ihre Zugangsdaten; Zeitpläne und Plan-PDFs haben kein
> Gegenstück; Revit-Mengen stammen aus IFC-Mengen oder dem GLB-Mesh).

- [`AI_AGENTS_INSTRUCTIONS/`](AI_AGENTS_INSTRUCTIONS/) — fertiger Kontext für Coding-Agenten
  (KI-Coding-Agenten) mit den aktuellen Kommandozeilen. Öffnen Sie das Repository in Ihrem
  Agenten und fragen Sie zum Beispiel *"convert every .rvt in C:\Projects to IFC and summarise the reports"*.
- [DDC Skills for AI agents](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
  — fertige Automatisierungen für Baudaten.

<a id="supported-scope-and-notes"></a>
## Unterstützter Umfang und Hinweise

- **RVT:** Texturen werden nicht exportiert; der IFC-Export schreibt tesseliertes IFC4. Elemente, die nicht
  darstellbar sind, werden im Laufbericht aufgeführt.
- **IFC:** IFC2x3- und IFC4-STEP-Dateien sowie `.ifczip`; IFCXML wird nicht unterstützt. Originaldatensätze bleiben immer in
  `data.jsonl` / `data.sqlite` erhalten.
- **DWG:** Zeichnungen R13–2018. Einige Objekttypen (zum Beispiel bestimmte Tabellen, Multileader, 3D-Volumenkörper,
  Bilder) werden in `report.json` als *unsupported* aufgeführt, statt fehlerhaft exportiert zu werden.
- **Plattformen:** Windows 10/11 x64. **Linux (x64, arm64) und macOS (arm64, x64): Kommandozeilen-Konverter und Data Viewer, siehe [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1).**

Fehlermeldungen mit einer kleinen Beispieldatei sind sehr willkommen — nutzen Sie bitte
[GitHub Issues](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues) und hängen Sie keine
vertraulichen Modelle an.

<a id="repository-layout"></a>
## Repository-Struktur

| Pfad | Inhalt |
|---|---|
| `docs/` | Release Notes, Screenshots |
| `ddc-tools/` | kostenlose Datenprüfung, Modellvergleich, BCF-Issues, Mengenermittlung, Power-BI- und Excel-Kit |
| `DDC_n8n_Workflows&Pipelines/` | n8n-Workflow-JSON-Dateien |
| `DDC_in_additon/` | Notebooks, Präsentationen, Bilder |
| `AI_AGENTS_INSTRUCTIONS/` | Anweisungen für KI-Coding-Agenten |
| `DDC_WINDOWS_Converters/` | portable Windows-Konverter (RVT, RVT-to-IFC, IFC to Excel, CAD Drawing to Excel, Data Viewer), Lizenztexte und die Dokumentation des Excel-→-Revit-Add-ins; Installer finden Sie auf der Releases-Seite |
| `DDC_LINUX_Converters/` | CWICR-Datenpakete, Qdrant-Paketierung und Telemetrie-Dashboard |
| `Sample_Projects/` | offene IFC-Beispieldateien |

<a id="licensing"></a>
## Lizenzierung

- **Workflows, Notebooks, Skripte, KI-Anweisungen, Dokumentation und `ddc-tools`** — [MIT-Lizenz](LICENSE).
  Open Source, kommerzielle Nutzung erlaubt.
- **DDC-Konverter** (Binärpakete auf Releases und in `DDC_WINDOWS_Converters/` / `DDC_LINUX_Converters/`) —
  proprietäre Software, **nur für die nicht-kommerzielle Nutzung kostenlos**. **Für die kommerzielle Nutzung ist auf Anfrage eine Lizenz erforderlich:**
  [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io). Bedingungen: [EULA](EULA.md),
  [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) und [NOTICE](NOTICE). Open-Source-Komponenten von Drittanbietern
  und ihre Lizenzen sind in `licenses/` in jedem Paket aufgeführt.
- Die MIT-Lizenz von `ddc-tools` erstreckt sich nicht auf die von ihm aufgerufenen Konverter.

**Kommerzielle Nutzung** bezeichnet jede Nutzung durch oder im Auftrag eines Unternehmens, einer Firma, einer selbstständigen Fachperson, einer Behörde
oder einer sonstigen Organisation (einschließlich ihrer Beschäftigten oder Auftragnehmer); in bezahlter Arbeit oder bezahlten Dienstleistungen, einschließlich der
Verarbeitung von Dateien für Kunden; in einem Projekt, das Einnahmen erzielt oder erzielen soll; oder innerhalb eines
Produkts, Dienstes, einer Pipeline oder eines SaaS-Angebots, das Dritten zur Verfügung gestellt wird. Weiterverbreitung, OEM- und SaaS-Integration
sind ebenfalls erfasst.
**Nicht-kommerzielle Nutzung** bezeichnet persönliches Lernen und Hobbynutzung, akademische Forschung, Lehre und Studium durch
Studierende und Lehrende sowie die Evaluierung durch gemeinnützige Organisationen, jeweils ohne Bezahlung, Einnahmen
oder geschäftlichen Zweck.

Sicherheitsmeldungen: siehe [SECURITY.md](SECURITY.md). Patente, Marken und Exportkontrolle:
[PATENTS.md](PATENTS.md), [TRADEMARK.md](TRADEMARK.md), [EXPORT-COMPLIANCE.md](EXPORT-COMPLIANCE.md).

<a id="consulting-and-training"></a>
## Beratung und Schulung

DataDrivenConstruction unterstützt Bau-, Ingenieur- und Technologieunternehmen dabei, die Verarbeitung von CAD/BIM-Daten zu automatisieren
und offene ETL-Pipelines aufzubauen — Workshops, Beratung und Prototypen mit Ihren echten Daten.
Kontakt: [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io) oder besuchen Sie
[datadrivenconstruction.io](https://datadrivenconstruction.io).

<p>
  <a href="https://x.com/datadrivenconst"><img src="https://img.shields.io/twitter/follow/datadrivenconst?logo=X&style=flat&color=%23f5f5f5" alt="Auf X folgen"></a>
  <a href="https://www.youtube.com/@datadrivenconstruction"><img src="https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://www.linkedin.com/company/78381569"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?logoColor=white" alt="LinkedIn"></a>
</p>

Wenn Ihnen diese Werkzeuge nützen, geben Sie dem Repository bitte einen Stern, um über neue Releases informiert zu werden.

<a id="trademarks"></a>
## Marken

Autodesk und Revit sind Marken von Autodesk, Inc. DataDrivenConstruction ist unabhängige Software und steht in keiner Verbindung zu Autodesk, Inc. und wird von dieser nicht unterstützt. RVT, RFA, DWG, DXF und IFC sind Dateiformatnamen, die nur verwendet werden, um anzugeben, welche Dateien gelesen werden.
