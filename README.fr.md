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
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto/blob/main/DDC_in_additon/DDC_readme_content/CAD%20BIM%20Pipeline%20and%20Workflow.jpg" alt="Vue d'ensemble du Pipeline" width="100%"/>
</p>
<p align="center">

  <a href="LICENSE">
  <img src="https://img.shields.io/github/license/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto?color=blue&label=workflows%20licence" alt="Licence Workflows: MIT">
</a>
<a href="https://datadrivenconstruction.io">
  <img src="https://img.shields.io/badge/powered%20by-DataDrivenConstruction.io-orange" alt="Powered by DataDrivenConstruction.io">
</a>
<img src="https://img.shields.io/badge/input-.rvt%20.dwg%20.ifc%20.dgn-blue?logo=autodesk&logoColor=white" alt="Formats d'entrée"></br>
<img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.dae%20.html%20.pdf%20.ifc-green?logo=microsoft-excel&logoColor=white" alt="Formats de sortie">
<img src="https://img.shields.io/badge/ETL%20pipeline-Ready%20for%20CI/CD%20&%20Bots-success?logo=githubactions" alt="ETL Pipeline">

<!-- Tarification -->
<a href="https://dify.ai/pricing" target="_blank">
  <img alt="Static Badge" src="https://img.shields.io/badge/free-pricing?logo=free&color=%23155EEF&label=pricing&labelColor=%23528bff">
</a>
</br>


<h3 align="center">Traitement et conversion CAD/BIM (Revit, DWG, IFC, DGN) avec traitement par lots, regroupement, vérifications, estimation des coûts et rapports QTO. Visualisation des processus d'automatisation dans des agents ouverts et des workflows</h3>

<p align="center">
  Automatisez votre extraction et transformation de données CAD/BIM avec DDC UI, ligne de commande, PowerShell ou Workflows — sans dépendance fournisseur, sans licences Autodesk® ou CAD, et avec un contrôle total de vos données de projet
</p>

<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto/blob/main/DDC_in_additon/DDC_readme_content/DDC_GithubLogo.jpg" alt="Vue d'ensemble du Pipeline" width="100%"/>
</p>

## Table des Matières

- [Aperçu](#aperçu)
- [Formats Supportés](#formats-supportés)
- [Fonctionnalités Principales](#fonctionnalités-principales)
- [Exécution des Convertisseurs](#exécution-des-convertisseurs)
- [🖥️ Interface en Ligne de Commande (CLI)](#️-interface-en-ligne-de-commande-cli)
- [Démarrage Rapide avec n8n](#démarrage-rapide-avec-n8n)
- [Support](#support)

## Aperçu

Ce pipeline automatise la conversion des fichiers CAD/BIM vers Excel pour les métrés, l'analyse de données et le traitement ultérieur. Il prend en charge le fonctionnement hors ligne et l'extensibilité avec Python ou des outils d'IA.

## Formats Supportés

| Format | Extension de Fichier | Convertisseur | Sortie |
|--------|---------------------|---------------|--------|
| Revit (2015-2026) | `.rvt` | RvtExporter.exe | Base de données XLSX + Géométrie DAE + Nomenclatures + Plans PDF |
| Revit (2015-2026) | `.rvt` | RVT2IFC_converter.exe | IFC2x3, IFC4, IFC4.3, IFCXML, IFCZIP, HDF5 |
| IFC (2x3, 4x1, 4x4, 4x, 4.3) | `.ifc` | IfcExporter.exe | Base de données XLSX + Géométrie DAE |
| AutoCAD (1983-2026) | `.dwg` | DwgExporter.exe | Base de données XLSX + Plans PDF |
| MicroStation (v7-v8) | `.dgn` | DgnExporter.exe | Base de données XLSX |

## Fonctionnalités Principales

- Conversion automatique vers Excel (éléments en lignes, propriétés en colonnes).
- Export de géométrie polygonale 3D (DAE) avec IDs d'éléments correspondant aux données XLSX.
- Traitement hors ligne sans internet, APIs ou licences.
- Extensible pour le post-traitement personnalisé.

## Exécution des Convertisseurs

Les convertisseurs DDC peuvent être lancés de différentes manières — **n8n n'est qu'une des options** pour l'automatisation.
Selon votre workflow et votre niveau technique, vous pouvez choisir parmi quatre méthodes :

1. **Interface Graphique Utilisateur (UI)**
   - Idéal pour les utilisateurs non techniques et les conversions rapides ponctuelles.
   - Interface intuitive, aucune configuration requise — sélectionnez simplement un dossier et démarrez.

2. **Console / Terminal (CMD, PowerShell, Shell)**
   - Adapté aux utilisateurs avancés, développeurs et équipes techniques.
   - Flexible et scriptable, peut être intégré dans des scripts d'automatisation ou des processus par lots.

3. **Pipelines Python ou JavaScript**
   - Idéal pour les entreprises et équipes travaillant avec de grands ensembles de données.
   - Traitement évolutif de centaines de fichiers CAD (BIM) en parallèle.
   - Exemples prêts à l'emploi dans le dossier `DDC_Python_pipelines`.

4. **Workflows n8n**
   - Idéal pour les entreprises recherchant **une automatisation complète et une intégration système**.
   - Pipelines de bout en bout où la conversion CAD (BIM) fait partie d'un flux de données transparent.
   - Exemples dans le dossier `DDC_n8n_workflows`.

---

## 🖥️ Interface en Ligne de Commande (CLI)

Les convertisseurs DDC sont des outils de ligne de commande entièrement fonctionnels qui peuvent être intégrés dans **n'importe quel workflow d'automatisation**. Cela les rend parfaits pour le scripting, les pipelines CI/CD, les agents IA et les plateformes low-code.

### 🤖 Pourquoi le CLI est Important : Laissez l'IA Construire vos Pipelines

**Le principal avantage des outils CLI est que l'IA peut les utiliser directement.**

Les assistants de programmation IA modernes (**Claude Code**, **Cursor**, **GitHub Copilot**, **Windsurf**, **Aider**, **Cline**) peuvent exécuter des commandes shell, lire la documentation et construire des pipelines d'automatisation complets de manière autonome. Cela signifie :

> **Vous n'avez pas besoin d'écrire du code vous-même — décrivez simplement ce que vous voulez, et l'IA intégrera les convertisseurs DDC dans votre workflow.**

**Comment ça fonctionne :**
1. **Copiez cette documentation** (ou pointez l'IA vers ce README)
2. **Décrivez votre tâche** en langage naturel : *"Convertis tous les fichiers Revit du dossier X vers Excel, puis analyse les quantités de murs"*
3. **L'IA lit la syntaxe CLI**, écrit le script, l'exécute et traite les résultats

**Ce que l'IA peut faire avec les convertisseurs DDC :**
- ✅ Convertir par lots des centaines de fichiers CAD/BIM automatiquement
- ✅ Construire des pipelines ETL : Revit → Excel → Base de données → Tableau de bord
- ✅ Créer des scripts de validation qui vérifient la qualité des données BIM
- ✅ Générer des rapports à partir des données extraites (PDF, HTML, Excel)
- ✅ Intégrer les conversions dans les pipelines CI/CD
- ✅ Chaîner plusieurs outils : convertir → valider → classifier → estimer les coûts
- ✅ Planifier un traitement automatisé via cron/Task Scheduler

**Exemple de prompt pour assistant IA :**
```
J'ai des fichiers Revit dans C:\Projets. En utilisant DDC RvtExporter.exe situé dans C:\DDC\,
convertis tous les fichiers .rvt vers Excel avec les bounding boxes, puis crée un script Python
qui lit les fichiers XLSX et génère un rapport récapitulatif de tous les types de murs et leurs volumes.
```

**Cela transforme DDC d'un outil en un bloc de construction natif IA pour l'automatisation des données de construction.**

### RvtExporter.exe — Revit vers XLSX/DAE/PDF

```
===========================================
         DataDrivenConstruction
         DDC Revit Community
         Version: 17.1.1
===========================================

Usage: RvtExporter <fichier entrée> [<fichier sortie>] [<fichier sortie>] [<mode export>] [<fichier catégories>] [bbox] [room] [schedule] [sheets2pdf] [-no-xlsx] [-no-collada]
```

| Paramètre | Description |
|-----------|-------------|
| `<fichier entrée>` | Fichier `.rvt` / `.rfa` d'entrée (requis) |
| `[<fichier sortie>]` | Chemin de sortie pour fichier `.dae` (optionnel, activé par défaut) |
| `[<fichier sortie>]` | Chemin de sortie pour fichier `.xlsx` (optionnel, activé par défaut) |
| `[<mode export>]` | `basic` (309 catégories), `standard` (724), `complete` (1209), ou `custom` |
| `[<fichier catégories>]` | Fichier `.txt` avec noms de catégories (requis uniquement en mode `custom`) |
| `bbox` | Inclure les bounding boxes des éléments dans la sortie XLSX |
| `room` | Inclure les données ToRoom/FromRoom dans la sortie XLSX |
| `schedule` | Exporter toutes les nomenclatures Revit |
| `sheets2pdf` | Exporter toutes les feuilles en PDF |
| `-no-xlsx` | Désactiver l'export au format `.xlsx` |
| `-no-collada` | Désactiver l'export au format `.dae` |

**Exemples :**
```bash
# Conversion basique (XLSX + DAE)
RvtExporter.exe "C:\Projets\Batiment.rvt"

# Export complet avec bounding boxes, nomenclatures et feuilles PDF
RvtExporter.exe "C:\Projets\Batiment.rvt" complete bbox schedule sheets2pdf

# Exporter uniquement XLSX (sans géométrie 3D)
RvtExporter.exe "C:\Projets\Batiment.rvt" -no-collada

# Catégories personnalisées depuis fichier
RvtExporter.exe "C:\Projets\Batiment.rvt" custom "C:\Config\mes_categories.txt"
```

---

### RVT2IFCconverter.exe — Revit vers IFC

```
===========================================
         DataDrivenConstruction
         DDC RVT2IFC Community
         Version: 17.1.2
===========================================

Usage: Rvt2IfcConverter <entrée.rvt> [<sortie.ifc>] [preset|mode=<nom>] [config="..."] [key=value ...]
```

| Paramètre | Description |
|-----------|-------------|
| `<entrée.rvt>` | Fichier Revit `.rvt` / `.rfa` (requis) |
| `[<sortie.ifc>]` | Chemin de sortie IFC (optionnel) |
| `preset=<nom>` ou `mode=<nom>` | `standard`, `extended`, `custom` |
| `config="K=V; K=V; ..."` | Configuration personnalisée (séparée par point-virgule) |
| `key=value` | Paramètres de configuration individuels |

---

### Exemples d'Intégration

#### 🔹 Assistants de Programmation IA (Claude Code, Cursor, Copilot, Windsurf, Aider, Cline)

Les assistants IA avec accès au terminal peuvent exécuter directement les convertisseurs DDC et construire des workflows complets :

```bash
# Exemple : L'IA exécute cette commande quand vous demandez "convertis mon fichier Revit en Excel"
RvtExporter.exe "C:\Projets\Modele.rvt" complete bbox schedule
```

**Scénarios réels de workflows IA :**

| Vous dites à l'IA | L'IA fait |
|-------------------|-----------|
| *"Convertis Batiment.rvt en Excel avec toutes les données"* | Exécute `RvtExporter.exe Batiment.rvt complete bbox room` |
| *"Traite tous les fichiers Revit dans ce dossier"* | Écrit une boucle PowerShell, exécute le convertisseur pour chaque fichier |
| *"Exporte au format IFC 4.3"* | Exécute `RVT2IFCconverter.exe` avec le bon preset |
| *"Crée une estimation des coûts depuis ce modèle"* | Convertit en Excel → analyse les données → calcule les coûts |
| *"Valide la qualité des données BIM"* | Convertit → analyse XLSX → génère un rapport de validation |

**Outils IA supportés :**
- **Claude Code** — accès complet au terminal, peut exécuter les convertisseurs et analyser les résultats
- **Cursor** — IDE avec IA qui peut exécuter des commandes shell
- **GitHub Copilot CLI** — assistant IA en ligne de commande
- **Windsurf** — IDE propulsé par IA avec intégration terminal
- **Aider** — programmation en binôme avec IA dans le terminal
- **Cline** — extension VS Code avec accès shell
- **Open Interpreter** — IA qui exécute du code localement
- **AutoGPT / AgentGPT** — agents IA autonomes

**Conseil pro :** Partagez ce README avec votre assistant IA pour qu'il comprenne la syntaxe CLI complète et puisse construire des pipelines sophistiqués de manière autonome.

#### 🔹 PowerShell / Scripts Batch
```powershell
# PowerShell : Traiter tous les fichiers .rvt dans un dossier
Get-ChildItem "C:\Projets\*.rvt" | ForEach-Object {
    & "C:\DDC\RvtExporter.exe" $_.FullName
}
```

#### 🔹 Python Subprocess
```python
import subprocess

result = subprocess.run([
    r"C:\DDC\RvtExporter.exe",
    r"C:\Projets\Batiment.rvt",
    "complete", "bbox", "schedule"
], capture_output=True, text=True)

print(result.stdout)
```

#### 🔹 n8n (Nœud Execute Command)
```javascript
// Dans le nœud Execute Command de n8n
C:\DDC\RvtExporter.exe "{{ $json.filePath }}" complete bbox
```

---

## Démarrage Rapide avec n8n

### Prérequis

1. **Installer Node.js** depuis [nodejs.org](https://nodejs.org/).
2. **Démarrer n8n** dans l'invite de commandes :
   ```
   npx n8n
   ```
   Accès à `http://localhost:5678`.
3. **Télécharger ce dépôt depuis GitHub**
   - Cliquez sur le bouton vert "Code" → "Download ZIP"
   - Décompressez le dossier
4. **Exécuter le Workflow**
     - Vous êtes prêt. Cliquez simplement sur **Execute Workflow** dans n8n pour traiter vos fichiers CAD-BIM

---

## Support

🌐 **Site web** : [DataDrivenConstruction.io](https://datadrivenconstruction.io)
💬 **Issues** : [GitHub Issues](https://github.com/datadrivenconstruction/Revit-IFC-DWG-DGN-Converter-in-n8n-with-QTO/issues)
📧 **Email** : info@datadrivenconstruction.io

---

<p align="left">
  <a href="https://datadrivenconstruction.io">
    <img src="https://datadrivenconstruction.io/wp-content/uploads/2023/07/DataDrivenConstruction-1-1.png" alt="DDC Logo" width="200"/>
  </a>
  <br>
   <b>   Libérez la Puissance des Données dans la Construction</b>
   <br>
     🚀 Passez à la gestion de données en cycle complet où seules restent <br /> les données et processus structurés unifiés et où 🔓 vos données vous appartiennent
</p>
