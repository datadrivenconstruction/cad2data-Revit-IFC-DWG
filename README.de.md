<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ar.md">العربية</a>
</p>

# cad2data — DDC-Konverter für RVT-, IFC- und DWG-Dateien

**CAD/BIM-Dateien lokal, offline und ohne CAD-Lizenzen in offene, strukturierte Daten umwandeln.**

<p align="center"><img src="docs/images/data-viewer-3d-grouped.png" width="100%" alt="DDC Data Viewer"></p>

## Neu in DDC Converters 2.0

Der Oktober-2026-Release der gesamten Produktlinie: RVT Converter 2.0, RVT to IFC 2.0, IFC to Excel 2.0, CAD Drawing to Excel 2.0, Data Viewer 2.0 und Excel Add-in 2.0.

- **Ein Werkzeug pro Formatfamilie.** `.rvt` / `.rfa` nach GLB, glTF, OBJ, IFC4 und JSONL- / CSV- / SQLite-Tabellen; `.ifc` / `.ifczip` nach Excel, JSONL und SQLite; `.dwg` nach Excel, CSV, JSONL, DXF und SVG.
- **Revit 2019–2027** wird direkt gelesen, ohne Autodesk-Software und ohne CAD-Lizenzen.
- **IFC4-Export aus Revit** mit Property Sets, Mengen, Klassifikation und Materialien sowie den Profilen `full`, `coordination` und `geometry`; Einheiten, Ursprung, Kategorien und Phasen per Kommandozeile.
- **Element-IDs überall.** Jeder Geometrieknoten behält die native Element-ID, sodass Tabellen und 3D über `ElementId` verknüpft werden.
- **Ein Bericht pro Lauf.** `report.json` / `summary.json` listen mit Zählwerten auf, was gelesen und was übersprungen wurde.
- **Desktop-Apps und Kommandozeile** für jeden Konverter, stapelfreundliche Exit-Codes und JSON-Statuszeile für Skripte.
- **DDC Data Viewer 2.0:** kostenloser Tabellen- und 3D-Viewer mit wechselseitiger Verknüpfung von Zeilen und Elementen.
- **Offline und portabel.** Windows 10/11 x64, außer dem Paket (Installer oder portables Zip) ist nichts zu installieren. Linux- / macOS-Builds — coming soon.

Downloads: [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (portabel, sofort startbereit) und die [Releases-Seite](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (Installer und Pakete).

## Konverter

| Paket | Version | Liest | Schreibt |
|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV / SQLite |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4 (Property Sets, Mengen, Klassifikation, Materialien) |
| **DDC IFC to Excel** | 2.0 | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC CAD Drawing to Excel** | 2.0 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 2.0 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

Alle Pakete laufen offline unter Windows 10/11 x64 und benötigen weder Autodesk-Software noch Excel oder Python. Jedes Geometrie-Element des RVT Converters trägt die native Element-ID, sodass Tabellen und 3D verknüpft werden können.

## Screenshots

Echte Läufe der aktuellen Pakete: synthetisches Beispielgebäude des Viewers und das offene IFC-Beispiel aus `Sample_Projects/`.

| | |
|---|---|
| ![](docs/images/data-viewer-3d-selection.png) | ![](docs/images/ifc-to-excel-table.png) |
| ![](docs/images/cli-rvt-ifc.png) | ![](docs/images/data-viewer-dark-ru.png) |

## Schnellstart

1. Paket aus dem [neuesten Release](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest) laden (`*-Setup.exe` oder `*-portable.zip`) und mit `SHA256SUMS.txt` prüfen.
2. Portable-Paket z. B. nach `C:\DDC\` entpacken.
3. Desktop-App starten, Dateien hineinziehen und konvertieren — oder die Kommandozeile verwenden:

```powershell
# RVT / RFA -> GLB + IFC4 + properties (JSONL)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --properties --ifc

# IFC / IFCZIP -> Excel + JSONL + SQLite
C:\DDC\IFC-to-Exceluntime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out\Building"

# DWG -> Excel + CSV + JSONL + DXF + SVG
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"
```

Alle Optionen, Ausgabedateien und Exit-Codes: siehe [englisches README](README.md#command-line).

## n8n-Workflows, Notebooks und KI-Agenten

Die n8n-Workflows (`DDC_n8n_Workflows&Pipelines/`) und Jupyter-Notebooks rufen die Konverter über `ddc convert` / `ddc table` auf (kostenloses Werkzeug [`ddc-tools/`](ddc-tools/)), das aus der Konverterausgabe die flache Tabelle (`*_rvt.xlsx`, Blatt `Project_Data`) aufbaut; 3D-Geometrie ist GLB. Einmalige Installation: `pip install ddc-tools\`. Was geprüft wurde und was nicht abgedeckt ist, steht im `README.md` neben den Workflows und Notebooks. `AI_AGENTS_INSTRUCTIONS/` enthält den Kontext mit den aktuellen Befehlen.

## Unterstützter Umfang und Hinweise

- **RVT:** Texturen werden nicht exportiert; der IFC-Export schreibt tessellierte IFC4. Nicht darstellbare Elemente stehen im Laufbericht.
- **IFC:** IFC2x3- und IFC4-STEP-Dateien sowie `.ifczip`; IFCXML wird nicht unterstützt. Die Originaldatensätze bleiben stets in `data.jsonl` / `data.sqlite`.
- **DWG:** Zeichnungen R13–2018. Einige Objekttypen (z. B. bestimmte Tabellen, Multileader, 3D-Volumenkörper, Bilder) stehen in `report.json` als *nicht unterstützt*, statt falsch exportiert zu werden.
- **Plattformen:** Windows 10/11 x64. **Linux / macOS — coming soon.**

## Lizenz

Workflows, Notebooks, Skripte und Dokumentation: [MIT](LICENSE). Konverter-Pakete: kostenlos für private und gewerbliche Nutzung gemäß der mitgelieferten DataDrivenConstruction-EULA; siehe [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) und [NOTICE](NOTICE). Kontakt: info@datadrivenconstruction.io

## Marken

Autodesk®, Revit® und AutoCAD® sind eingetragene Marken von Autodesk, Inc. IFC und buildingSMART® sind Marken von buildingSMART International Ltd. Dateiformatnamen (RVT, RFA, DWG, DXF, DGN) dienen nur der Bezeichnung von Dateiformaten. DataDrivenConstruction ist nicht mit Autodesk, Inc. verbunden und wird von Autodesk weder unterstützt noch zertifiziert. Die DDC-Produkte sind unabhängige Software für Interoperabilität und enthalten bzw. verwenden keine Autodesk-Software, -SDKs oder -Quellcode. Vollständiger Text: [README.md](README.md#trademarks).
