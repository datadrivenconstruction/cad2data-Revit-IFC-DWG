<p align="center">
  <a href="README.md">🇬🇧 English</a> •
  <a href="README.de.md">🇩🇪 Deutsch</a> •
  <a href="README.es.md">🇪🇸 Español</a> •
  <a href="README.fr.md">🇫🇷 Français</a> •
  <a href="README.ru.md">🇷🇺 Русский</a> •
  <a href="README.zh.md">🇨🇳 中文</a> •
  <a href="README.ar.md">🇸🇦 العربية</a>
</p>

<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto/blob/main/DDC_in_additon/DDC_readme_content/CAD%20BIM%20Pipeline%20and%20Workflow.jpg" alt="Pipeline-Übersicht" width="100%"/>
</p>
<p align="center">

  <a href="LICENSE">
  <img src="https://img.shields.io/github/license/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto?color=blue&label=workflows%20licence" alt="Workflows Lizenz: MIT">
</a>
<a href="https://datadrivenconstruction.io">
  <img src="https://img.shields.io/badge/powered%20by-DataDrivenConstruction.io-orange" alt="Powered by DataDrivenConstruction.io">
</a>
<img src="https://img.shields.io/badge/input-.rvt%20.dwg%20.ifc%20.dgn-blue?logo=autodesk&logoColor=white" alt="Eingabeformate"></br>
<img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.dae%20.html%20.pdf%20.ifc-green?logo=microsoft-excel&logoColor=white" alt="Ausgabeformate">
<img src="https://img.shields.io/badge/ETL%20pipeline-Ready%20for%20CI/CD%20&%20Bots-success?logo=githubactions" alt="ETL Pipeline">

<!-- Preise -->
<a href="https://dify.ai/pricing" target="_blank">
  <img alt="Static Badge" src="https://img.shields.io/badge/free-pricing?logo=free&color=%23155EEF&label=pricing&labelColor=%23528bff">
</a>
</br>


<h3 align="center">CAD/BIM (Revit, DWG, IFC, DGN) Verarbeitung und Konvertierung mit Stapelverarbeitung, Gruppierung, Prüfungen, Kostenschätzung und QTO-Berichten. Visualisierung von Automatisierungsprozessen in offenen Agenten und Workflows</h3>

<p align="center">
  Automatisieren Sie Ihre CAD/BIM-Datenextraktion und -transformation mit DDC UI, Kommandozeile, PowerShell oder Workflows — ohne Herstellerbindung, ohne Autodesk®- oder CAD-Lizenzen und mit voller Kontrolle über Ihre Projektdaten
</p>

<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto/blob/main/DDC_in_additon/DDC_readme_content/DDC_GithubLogo.jpg" alt="Pipeline-Übersicht" width="100%"/>
</p>

## Inhaltsverzeichnis

- [Übersicht](#übersicht)
- [Unterstützte Formate](#unterstützte-formate)
- [Hauptfunktionen](#hauptfunktionen)
- [Ausführung der Konverter](#ausführung-der-konverter)
- [🖥️ Kommandozeilen-Schnittstelle (CLI)](#️-kommandozeilen-schnittstelle-cli)
- [Schnellstart mit n8n](#schnellstart-mit-n8n)
- [Unterstützung](#unterstützung)

## Übersicht

Diese Pipeline automatisiert die Konvertierung von CAD/BIM-Dateien nach Excel für Mengenermittlung, Datenanalyse und Weiterverarbeitung. Sie unterstützt Offline-Betrieb und Erweiterbarkeit mit Python oder KI-Tools.

## Unterstützte Formate

| Format | Dateierweiterung | Konverter | Ausgabe |
|--------|------------------|-----------|---------|
| Revit (2015-2026) | `.rvt` | RvtExporter.exe | XLSX-Datenbank + DAE-Geometrie + Bauteillisten + PDF-Zeichnungen |
| Revit (2015-2026) | `.rvt` | RVT2IFC_converter.exe | IFC2x3, IFC4, IFC4.3, IFCXML, IFCZIP, HDF5 |
| IFC (2x3, 4x1, 4x4, 4x, 4.3) | `.ifc` | IfcExporter.exe | XLSX-Datenbank + DAE-Geometrie |
| AutoCAD (1983-2026) | `.dwg` | DwgExporter.exe | XLSX-Datenbank + PDF-Zeichnungen |
| MicroStation (v7-v8) | `.dgn` | DgnExporter.exe | XLSX-Datenbank |

## Hauptfunktionen

- Automatische Konvertierung nach Excel (Elemente als Zeilen, Eigenschaften als Spalten).
- Export von 3D-Polygongeometrie (DAE) mit Element-IDs, die den XLSX-Daten entsprechen.
- Offline-Verarbeitung ohne Internet, APIs oder Lizenzen.
- Erweiterbar für benutzerdefinierte Nachbearbeitung.

## Ausführung der Konverter

Die DDC-Konverter können auf verschiedene Arten gestartet werden — **n8n ist nur eine der Möglichkeiten** zur Automatisierung.
Je nach Workflow und technischem Hintergrund können Sie zwischen vier Methoden wählen:

1. **Grafische Benutzeroberfläche (UI)**
   - Ideal für nicht-technische Anwender und schnelle Einzelkonvertierungen.
   - Intuitive Oberfläche, keine Einrichtung erforderlich — einfach Ordner auswählen und starten.

2. **Konsole / Terminal (CMD, PowerShell, Shell)**
   - Geeignet für fortgeschrittene Benutzer, Entwickler und technische Teams.
   - Flexibel und skriptfähig, kann in Automatisierungsskripte oder Stapelprozesse integriert werden.

3. **Python- oder JavaScript-Pipelines**
   - Ideal für Unternehmen und Teams, die mit großen Datenmengen arbeiten.
   - Skalierbare Verarbeitung von Hunderten von CAD (BIM)-Dateien parallel.
   - Fertige Beispiele im Ordner `DDC_Python_pipelines`.

4. **n8n Workflows**
   - Ideal für Unternehmen, die **vollständige Automatisierung und Systemintegration** suchen.
   - End-to-End-Pipelines, bei denen CAD (BIM)-Konvertierung Teil eines nahtlosen Datenflusses wird.
   - Beispiele im Ordner `DDC_n8n_workflows`.

---

## 🖥️ Kommandozeilen-Schnittstelle (CLI)

Die DDC-Konverter sind voll funktionsfähige Kommandozeilen-Tools, die in **jeden Automatisierungs-Workflow** integriert werden können. Das macht sie perfekt für Scripting, CI/CD-Pipelines, KI-Agenten und Low-Code-Plattformen.

### 🤖 Warum CLI wichtig ist: Lassen Sie KI Ihre Pipelines erstellen

**Der Hauptvorteil von CLI-Tools ist, dass KI sie direkt nutzen kann.**

Moderne KI-Coding-Assistenten (**Claude Code**, **Cursor**, **GitHub Copilot**, **Windsurf**, **Aider**, **Cline**) können Shell-Befehle ausführen, Dokumentation lesen und vollständige Automatisierungs-Pipelines autonom erstellen. Das bedeutet:

> **Sie müssen keinen Code selbst schreiben — beschreiben Sie einfach, was Sie wollen, und die KI integriert DDC-Konverter in Ihren Workflow.**

**So funktioniert es:**
1. **Kopieren Sie diese Dokumentation** (oder verweisen Sie die KI auf diese README)
2. **Beschreiben Sie Ihre Aufgabe** in natürlicher Sprache: *"Konvertiere alle Revit-Dateien im Ordner X nach Excel und analysiere dann die Wandmengen"*
3. **Die KI liest die CLI-Syntax**, schreibt das Skript, führt es aus und verarbeitet die Ergebnisse

**Was KI mit DDC-Konvertern tun kann:**
- ✅ Hunderte von CAD/BIM-Dateien automatisch stapelweise konvertieren
- ✅ ETL-Pipelines erstellen: Revit → Excel → Datenbank → Dashboard
- ✅ Validierungsskripte erstellen, die BIM-Datenqualität prüfen
- ✅ Berichte aus extrahierten Daten generieren (PDF, HTML, Excel)
- ✅ Konvertierungen in CI/CD-Pipelines integrieren
- ✅ Mehrere Tools verketten: konvertieren → validieren → klassifizieren → Kosten schätzen
- ✅ Automatisierte Verarbeitung über cron/Task Scheduler planen

**Beispiel-Prompt für KI-Assistenten:**
```
Ich habe Revit-Dateien in C:\Projekte. Mit DDC RvtExporter.exe in C:\DDC\,
konvertiere alle .rvt-Dateien nach Excel mit Bounding Boxes, erstelle dann ein Python-Skript,
das die XLSX-Dateien liest und einen Zusammenfassungsbericht aller Wandtypen und ihrer Volumina generiert.
```

**Dies verwandelt DDC von einem Tool in einen KI-nativen Baustein für Bauautomatisierung.**

### RvtExporter.exe — Revit zu XLSX/DAE/PDF

```
===========================================
         DataDrivenConstruction
         DDC Revit Community
         Version: 17.1.1
===========================================

Usage: RvtExporter <Eingabedatei> [<Ausgabedatei>] [<Ausgabedatei>] [<Exportmodus>] [<Kategoriedatei>] [bbox] [room] [schedule] [sheets2pdf] [-no-xlsx] [-no-collada]
```

| Parameter | Beschreibung |
|-----------|--------------|
| `<Eingabedatei>` | Eingabe `.rvt` / `.rfa` Datei (erforderlich) |
| `[<Ausgabedatei>]` | Ausgabepfad für `.dae` Datei (optional, standardmäßig aktiviert) |
| `[<Ausgabedatei>]` | Ausgabepfad für `.xlsx` Datei (optional, standardmäßig aktiviert) |
| `[<Exportmodus>]` | `basic` (309 Kategorien), `standard` (724), `complete` (1209), oder `custom` |
| `[<Kategoriedatei>]` | `.txt` Datei mit Kategorienamen (nur im `custom` Modus erforderlich) |
| `bbox` | Bounding Boxes der Elemente in XLSX-Ausgabe einschließen |
| `room` | ToRoom/FromRoom-Daten in XLSX-Ausgabe einschließen |
| `schedule` | Alle Revit-Bauteillisten exportieren |
| `sheets2pdf` | Alle Blätter als PDF exportieren |
| `-no-xlsx` | Export nach `.xlsx` Format deaktivieren |
| `-no-collada` | Export nach `.dae` Format deaktivieren |

**Beispiele:**
```bash
# Basis-Konvertierung (XLSX + DAE)
RvtExporter.exe "C:\Projekte\Gebaeude.rvt"

# Vollständiger Export mit Bounding Boxes, Bauteillisten und PDF-Blättern
RvtExporter.exe "C:\Projekte\Gebaeude.rvt" complete bbox schedule sheets2pdf

# Nur XLSX exportieren (keine 3D-Geometrie)
RvtExporter.exe "C:\Projekte\Gebaeude.rvt" -no-collada

# Benutzerdefinierte Kategorien aus Datei
RvtExporter.exe "C:\Projekte\Gebaeude.rvt" custom "C:\Config\meine_kategorien.txt"
```

---

### RVT2IFCconverter.exe — Revit zu IFC

```
===========================================
         DataDrivenConstruction
         DDC RVT2IFC Community
         Version: 17.1.2
===========================================

Usage: Rvt2IfcConverter <eingabe.rvt> [<ausgabe.ifc>] [preset|mode=<name>] [config="..."] [key=value ...]
```

| Parameter | Beschreibung |
|-----------|--------------|
| `<eingabe.rvt>` | Revit-Datei `.rvt` / `.rfa` (erforderlich) |
| `[<ausgabe.ifc>]` | Ausgabe-IFC-Pfad (optional) |
| `preset=<name>` oder `mode=<name>` | `standard`, `extended`, `custom` |
| `config="K=V; K=V; ..."` | Benutzerdefinierte Konfiguration (semikolon-getrennt) |
| `key=value` | Individuelle Konfigurationsparameter |

---

### Integrationsbeispiele

#### 🔹 KI-Coding-Assistenten (Claude Code, Cursor, Copilot, Windsurf, Aider, Cline)

KI-Assistenten mit Terminal-Zugang können DDC-Konverter direkt ausführen und komplette Workflows erstellen:

```bash
# Beispiel: KI führt diesen Befehl aus, wenn Sie fragen "konvertiere meine Revit-Datei nach Excel"
RvtExporter.exe "C:\Projekte\Modell.rvt" complete bbox schedule
```

**Reale KI-Workflow-Szenarien:**

| Sie sagen zur KI | KI macht |
|------------------|----------|
| *"Konvertiere Gebaeude.rvt nach Excel mit allen Daten"* | Führt `RvtExporter.exe Gebaeude.rvt complete bbox room` aus |
| *"Verarbeite alle Revit-Dateien in diesem Ordner"* | Schreibt PowerShell-Schleife, führt Konverter für jede Datei aus |
| *"Exportiere ins IFC 4.3 Format"* | Führt `RVT2IFCconverter.exe` mit korrektem Preset aus |
| *"Erstelle eine Kostenschätzung aus diesem Modell"* | Konvertiert nach Excel → analysiert Daten → berechnet Kosten |
| *"Validiere BIM-Datenqualität"* | Konvertiert → analysiert XLSX → erstellt Validierungsbericht |

**Unterstützte KI-Tools:**
- **Claude Code** — voller Terminal-Zugang, kann Konverter ausführen und Ergebnisse analysieren
- **Cursor** — IDE mit KI, die Shell-Befehle ausführen kann
- **GitHub Copilot CLI** — Kommandozeilen-KI-Assistent
- **Windsurf** — KI-gestützte IDE mit Terminal-Integration
- **Aider** — KI-Pair-Programming im Terminal
- **Cline** — VS Code-Erweiterung mit Shell-Zugang
- **Open Interpreter** — KI, die Code lokal ausführt
- **AutoGPT / AgentGPT** — autonome KI-Agenten

**Profi-Tipp:** Teilen Sie diese README mit Ihrem KI-Assistenten, damit er die vollständige CLI-Syntax versteht und anspruchsvolle Pipelines autonom erstellen kann.

#### 🔹 PowerShell / Batch-Skripte
```powershell
# PowerShell: Alle .rvt-Dateien in einem Ordner verarbeiten
Get-ChildItem "C:\Projekte\*.rvt" | ForEach-Object {
    & "C:\DDC\RvtExporter.exe" $_.FullName
}
```

#### 🔹 Python Subprocess
```python
import subprocess

result = subprocess.run([
    r"C:\DDC\RvtExporter.exe",
    r"C:\Projekte\Gebaeude.rvt",
    "complete", "bbox", "schedule"
], capture_output=True, text=True)

print(result.stdout)
```

#### 🔹 n8n (Execute Command Node)
```javascript
// Im n8n Execute Command Node
C:\DDC\RvtExporter.exe "{{ $json.filePath }}" complete bbox
```

---

## Schnellstart mit n8n

### Voraussetzungen

1. **Node.js installieren** von [nodejs.org](https://nodejs.org/).
2. **n8n starten** in der Eingabeaufforderung:
   ```
   npx n8n
   ```
   Zugriff unter `http://localhost:5678`.
3. **Dieses Repository von GitHub herunterladen**
   - Klicken Sie auf den grünen "Code"-Button → "Download ZIP"
   - Entpacken Sie den Ordner
4. **Workflow ausführen**
     - Sie sind bereit. Klicken Sie einfach auf **Execute Workflow** in n8n, um Ihre CAD-BIM-Dateien zu verarbeiten

---

## Unterstützung

🌐 **Website**: [DataDrivenConstruction.io](https://datadrivenconstruction.io)
💬 **Issues**: [GitHub Issues](https://github.com/datadrivenconstruction/Revit-IFC-DWG-DGN-Converter-in-n8n-with-QTO/issues)
📧 **E-Mail**: info@datadrivenconstruction.io

---

<p align="left">
  <a href="https://datadrivenconstruction.io">
    <img src="https://datadrivenconstruction.io/wp-content/uploads/2023/07/DataDrivenConstruction-1-1.png" alt="DDC Logo" width="200"/>
  </a>
  <br>
   <b>   Erschließen Sie die Macht der Daten im Bauwesen</b>
   <br>
     🚀 Wechseln Sie zu vollständigem Datenmanagement, wo nur einheitliche <br /> strukturierte Daten & Prozesse bleiben und wo 🔓 Ihre Daten Ihnen gehören
</p>
