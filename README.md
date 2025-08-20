<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/07/n8n-pipelines-CAD-BIM-Revit-IFC-AutoCAD-scaled.jpg" alt="Pipeline Overview" width="100%"/>
</p>


<h3 align="center">CAD/BIM (Revit, DWG, IFC, DGN) processing and conversion with batch handling, grouping, checks, cost estimation and QTO reports. Visualization of automation processes in open workflows</h3>

<p align="center">
  Automate your CAD/BIM data extraction and transformation using <a href="https://n8n.io">n8n</a>   </br> with no vendor lock-in, no Autodesk® or CAD licenses, and full control of your project data
</p>

<p align="center">
  <a href="https://n8n.io">
    <img src="https://img.shields.io/badge/powered%20by-n8n-ff6d5a?logo=n8n&logoColor=white" alt="n8n">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto?color=blue" alt="MIT License">
  </a>
  <a href="https://datadrivenconstruction.io">
    <img src="https://img.shields.io/badge/made%20by-DataDrivenConstruction.io-orange" alt="DataDrivenConstruction">
  </a>
  <img src="https://img.shields.io/badge/input-.rvt%20.dwg%20.ifc%20.dgn-blue?logo=autodesk&logoColor=white" alt="Input Formats"></br>
  <img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.dae%20.html%20.pdf-green?logo=microsoft-excel&logoColor=white" alt="Output Formats">
  <img src="https://img.shields.io/badge/ETL%20pipeline-Ready%20for%20CI/CD%20&%20Bots-success?logo=githubactions" alt="ETL Pipeline">
</p>


<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n-GitHub-DataDrivenConstruction.jpg" alt="Pipeline Overview" width="100%"/>
</p>

## Table of Contents

- [Tutorial Videos](#tutorial-videos)
- [Overview](#overview)
- [Supported Formats](#supported-formats)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [📁 Workflows](#n8n-workflows-for-working-with-cadbim-data)
  - [⚡️ 1. Revit, IFC, DWG, DGN Basic Conversion](#️-1-revit-ifc-dwg-dgn-basic-conversion)
  - [⚡️ 2. Revit Conversion with Advanced Settings](#️-2-revit-conversion-with-advanced-settings)
  - [⚡️ 3. Revit, IFC, DWG Batch Conversion with Validation and Reporting](#️-3-revit-ifc-dwg-batch-conversion-with-validation-and-reporting)
  - [⚡️ 4. Multi-Format CAD (BIM) Validation for Revit, IFC, DWG, DGN](#️-4-multi-format-cad-bim-validation-for-revit-ifc-dwg-dgn)
  - [⚡️ 5. Universal BIM/CAD Classification with AI & RAG for Revit, IFC, DWG, DGN](#️-5-universal-bimcad-classification-with-ai--rag-for-revit-ifc-dwg-dgn)
  - [⚡️ 6. Construction Price Estimation Pipeline for Revit and IFC with LLM (AI)](#️-6-construction-price-estimation-pipeline-for-revit-and-ifc-with-llm-ai)
  - [⚡️ 7. Carbon Footprint CO2 Estimator for Revit and IFC with LLM (AI)](#️-7-carbon-footprint-co2-estimator-for-revit-and-ifc-with-llm-ai)
  - [⚡️ 8. Simple ETL for LLM Use Cases for Revit, IFC, DWG, DGN](#️-8-simple-etl-for-llm-use-cases-for-revit-ifc-dwg-dgn)
  - [⚡️ 9. Revit and IFC to HTML Quantity Takeoff](#️-9-revit-and-ifc-to-html-quantity-takeoff)
- [Troubleshooting](#troubleshooting)
- [What is DataFrames?](#what-is-dataframes)
- [Re-import Data into Revit](#️re-import-data-into-revit)
- [Contributing](#contributing)
- [🆘 Support](#support)
- [🎓 Consulting and Training](#consulting-and-training)




## Tutorial Videos

<table style="border: none; border-collapse: collapse;">
  <tr>
    <td style="border: none; padding-right: 12px; vertical-align: top;">
      <a href="https://youtu.be/HUbEPo-yfeA?si=Gjbj2glKgU3q-XZC" target="_blank">
        <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/07/n8n-how-to-install.png" alt="n8n Quick Start" width="460" height="315">
      </a>
    </td>
    <td style="border: none; vertical-align: top;">
     <b> n8n Quick Start: Easy Installation & Pipeline Creation (Templates and LLM) </b>
      <br>
        Step-by-step beginner tutorial on setting up <strong>n8n</strong> from scratch, building your first automation pipeline, and using LLMs (like ChatGPT/Claude) to generate automations.<br>
        <a href="https://youtu.be/HUbEPo-yfeA?si=Gjbj2glKgU3q-XZC" target="_blank">Watch n8n Quick Start on YouTube</a>
      </br>
    </td>
  </tr>
  <tr>
    <td style="border: none; padding-right: 12px; vertical-align: top;">
      <a href="https://www.youtube.com/watch?v=PMTZNRFjD6c" target="_blank">
        <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/07/CAD-BIM-n8n-pipeline.png" alt="CAD-BIM n8n Pipeline" width="760" height="315">
      </a>
    </td>
    <td style="border: none; vertical-align: top;">
     <b> CAD-BIM Data Pipeline Tutorial </b>
      <br>
        Full hands-on walkthrough: automate complex <strong>CAD-BIM data processing</strong> workflows in <code>n8n</code>, including conversion, validation, and actionable analytics.<br>
        <a href="https://www.youtube.com/watch?v=PMTZNRFjD6c" target="_blank">Watch CAD-BIM Pipeline Tutorial on YouTube</a>
      </br>
    </td>
  </tr>
  <tr>
    <td style="border: none; padding-right: 12px; vertical-align: top;">
      <a href="https://www.youtube.com/watch?v=p84AmP2dcvg" target="_blank">
        <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/07/n8n-how-to-install.jpg" alt="Automated CAD/BIM Validation" width="460" height="315">
      </a>
    </td>
    <td style="border: none; vertical-align: top;">
     <b> ⚡️Automated CAD/BIM Data Validation with n8n | The End of Manual BIM Checks </b>
      <br>
        Discover how to fully automate <strong>CAD/BIM data validation</strong> workflows using the free, open-source <code>n8n</code> platform.Ideal for project teams looking to save hours (or days) every week.<br>
        <a href="https://www.youtube.com/watch?v=p84AmP2dcvg" target="_blank">Watch Automated Validation Tutorial on YouTube</a>
      </br>
    </td>
  </tr>
</table>






## Overview

This pipeline automates the conversion of CAD/BIM files to Excel for quantity takeoffs, data analysis, and further processing. It supports offline operation and extensibility with Python or AI tools.

⭐ **If you find our tools helpful, please consider starring our repository** 🤝

## Supported Formats

| Format | File Extension | Converter | Output |
|--------|----------------|-----------|--------|
| Revit (2015-2025) | `.rvt` | RvtExporter.exe | XLSX database + DAE geometry + Schedules + PDF Drawings |
| IFC (2x3, 4x1, 4x4, 4x, 4.3) | `.ifc` | IfcExporter.exe | XLSX database + DAE geometry |
| AutoCAD (1983-2025) | `.dwg` | DwgExporter.exe | XLSX database + PDF Drawings |
| MicroStation (v7-v8) | `.dgn` | DgnExporter.exe | XLSX database |

## Key Features

- Automated conversion to Excel (elements as rows, properties as columns).
- Export of 3D polygonal geometry (DAE) with element IDs matching the XLSX data.
- Offline processing without internet, APIs, or licenses.
- Extensible for custom post-processing.

## Quick Start

### Prerequisites

1. **Install Node.js** from [nodejs.org](https://nodejs.org/).
2. **Start n8n** in Command Prompt:
   ```
   npx n8n
   ```
   Access at `http://localhost:5678`.
3. **Download this repository from GitHub**  
   - Click the green "Code" button → "Download ZIP"
   - Unzip the folder
4. **Run the Workflow**
     - You're ready. Just click **Execute Workflow** in n8n to start process your CAD-BIM files
<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/07/Install-Nodejs-and-n8n.png" alt="Pipeline Overview" width="100%"/>
  <br></br>
</p>

# n8n Workflows for working with CAD/BIM data

### ⚡️ 1. Revit, IFC, DWG, DGN Basic Conversion 
**File**: `n8n_1_Revit_IFC_DWG_Conversation_simple.json`

Converts CAD/BIM files (`.rvt`, `.ifc`, `.dwg`, `.dgn`) to Excel (XLSX) and Collada (DAE) for Revit/IFC files. Minimal configuration for quick setup.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Revit_IFC_DWG_Conversation_simple-1.jpg" alt="Basic Conversion" width="100%"/>
</p>

#### Installation
1. Import `n8n_1_Revit_IFC_DWG_Conversation_simple.json` into n8n via **Workflows > Import from File**.
2. Update **Set Variables** node:
   ```
   # Revit
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   path_project_file: C:\Projects\Model.rvt

   # IFC
   path_to_converter: C:\Converters\datadrivenlibs\IfcExporter.exe
   path_project_file: C:\Projects\Model.ifc

   # DWG
   path_to_converter: C:\Converters\datadrivenlibs\DwgExporter.exe
   path_project_file: C:\Projects\Plan.dwg

   # DGN
   path_to_converter: C:\Converters\datadrivenlibs\DgnExporter.exe
   path_project_file: C:\Projects\Bridge.dgn
   ```
3. Ensure the converter is in the `datadrivenlibs` folder, e.g., `C:\Converters\datadrivenlibs\XxxExporter.exe`.

#### Usage
1. Run the workflow via **Manual Trigger**.
2. Check the output folder for XLSX, DAE, and PDF files.
3. Monitor logs for conversion status.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Set Variables];
    B --> C[Execute Pipeline];
    C --> D[Output XLSX + DAE + PDF];
```



### ⚡️ 2. Revit Conversion with Advanced Settings
**File**: `n8n_2_All_Settings_Revit_IFC_DWG_Conversation_simple.json`

Converts CAD/BIM files with customizable export modes (basic: 309 categories, standard: 724 categories, complete: all 1209 categories) and optional outputs like bounding box, Revit schedules, or PDF drawings.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_All_Settings_Revit_IFC_DWG_Conversation_simple-1.jpg" alt="Basic Conversion" width="100%"/>
</p>

#### Installation
1. Import `n8n_2_All_Settings_Revit_IFC_DWG_Conversation_simple.json` into n8n via **Workflows > Import from File**.
2. Update **Set Variables** node with converter and file paths (same as Basic Conversion).
3. Configure export options:
   ```
   export_mode: basic | standard | complete
   bbox: true | false
   schedule: true | false
   sheets2pdf: true | false
   no-xlsx: true | false
   no-collada: true | false
   ```

#### Usage
1. Run the workflow via **Manual Trigger**.
2. Check the output folder for XLSX, DAE, schedules, or PDF files based on settings.
3. Monitor logs for conversion status.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Set Variables];
    B --> C[Execute Pipeline];
    C --> D{Export Options};
    D -->|Standard| F[XLSX + DAE];
    D -->|+BBox| G[XLSX + DAE + BBox];
    D -->|+Schedules| H[XLSX + DAE + Schedules];
    D -->|+PDF| I[XLSX + DAE + PDF];
```



### ⚡️ 3. Revit, IFC, DWG Batch Conversion with Validation and Reporting
**File**: `n8n_3_CAD-BIM-Batch-Converter-Pipeline.json`

Automates batch conversion of Revit (`.rvt`) files to Excel (XLSX) and Collada (DAE), validates outputs, tracks processing times, and generates an HTML report with metrics, file links, and configuration details.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/CAD-BIM-Batch-Converter-Pipeline-1.jpg" alt="Advanced Conversion" width="100%"/>
</p>

#### Installation
1. Import `n8n_3_CAD-BIM-Batch-Converter-Pipeline.json` into n8n via **Workflows > Import from File**.
2. Update **Set Configuration Parameters** node:
   ```
   converter_path: C:\Converters\datadrivenlibs\RvtExporter.exe
   source_folder: C:\Sample_Projects
   output_folder: C:\Output
   include_subfolders: true
   file_extension: .rvt
   ```
3. Ensure `RvtExporter.exe` is in `C:\Converters\datadrivenlibs\` and `.rvt` files are in the source folder.

#### Usage
1. Run the workflow via **Manual Trigger**.
2. Monitor logs for file discovery and conversion progress.
3. Review the HTML report (auto-opens in browser) with:
   - Metrics (files processed, success rate, time, sizes).
   - Success/failure tables with file links.
4. Check the output folder for XLSX and DAE files.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Set Config];
    B --> C[Scan Files];
    C --> D[Batch Convert];
    D --> E[Validate Outputs];
    E --> F[Track Metrics];
    F --> G[Generate HTML Report];
    G --> H[Save & Open Report];
```



### ⚡️ 4. Multi-Format CAD (BIM) Validation for Revit, IFC, DWG, DGN
**Files**: `n8n_4_Validation_CAD_BIM_Revit_IFC_DWG.json`, `DDC_BIM_Requirements_Table_for_Revit_IFC_DWG.xlsx`

Validates CAD/BIM data against predefined rules, generating color-coded Excel reports with data quality metrics.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Validation_CAD_BIM_Revit_IFC_DWG-1.jpg" alt="Validation Pipeline" width="100%"/>
</p>

#### Installation
1. Import `n8n_3_Validation_CAD_BIM_Revit_IFC_DWG.json` into n8n via **Workflows > Import from File**.
2. Update **Setup Paths** node:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   validation_rules_path: C:\Validation\DDC_Revit_IFC_Validation_Table.xlsx
   ```
3. Ensure the converter and validation rules file are accessible.

#### Usage
1. Run the workflow via **Manual Trigger**.
2. Check the output folder for the color-coded XLSX report.
3. Review data quality metrics (fill rates, unique values, patterns).
4. Monitor logs for validation status.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Setup Paths];
    B --> C{File Exists?};
    C -->|No| D[Convert to Structured];
    C -->|Yes| E[Load Data];
    D --> E;
    E --> F[Load Rules];
    F --> G[Validate Data];
    G --> H[Calculate Metrics];
    H --> I[Generate Report];
    I --> J[Save & Open];
```

### ⚡️ 5. Universal BIM/CAD Classification with AI & RAG for Revit, IFC, DWG, DGN
**File**: `n8n_5_CAD_BIM_Automatic_Classification_with_LLM_and_RAG.json`

Intelligently classifies building elements from CAD/BIM files using AI and ANY classification system - international standards (Omniclass, Uniclass, etc.) or your custom/proprietary classifications. Supports automatic dictionary extraction from mapping files.

#### Key Features
- **Universal Classification**: Works with ANY classification system - standard or custom
- **AI-Powered Classification**: Uses LLMs to classify elements with confidence scoring
- **Smart Mapping**: Automatically extracts dictionaries from Excel, CSV, PDF files
- **Automatic Filtering**: Separates building elements from drawings/annotations
- **Hierarchical Support**: Handles both flat and hierarchical classification structures
- **Professional Reports**: Interactive HTML dashboards + multi-sheet Excel
- **RAG Technology**: Retrieval-Augmented Generation for accurate classification

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/Auto-classification-CAD-BIM.jpg" alt="Universal Classification" width="100%"/>
</p>

#### Installation
1. Import `n8n_5_CAD_BIM_Automatic_Classification_with_LLM_and_RAG.json` into n8n
2. Configure AI credentials (OpenAI/Anthropic/OpenRouter/Gemini/xAI)
3. Update **Setup - Define file paths** node:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   group_by: Type Name
   classification_name: [Any classification name]
   optional_mapping_file: C:\Classifications\[your_classification].xlsx
   optional_help_prompt: "Additional context for AI"
   ```

#### Classification Flexibility
This pipeline works with **ANY classification system**:
- ✅ International standards (Omniclass, Uniclass, MasterFormat, etc.)
- ✅ National standards (DIN, NF, BS, etc.)
- ✅ Company-specific classifications
- ✅ Custom project classifications
- ✅ Proprietary coding systems
- ✅ Any structured classification in Excel/CSV/PDF format

#### How It Works
1. **With Mapping File**: Provide your classification dictionary (Excel/CSV/PDF) - the AI will extract codes and apply them accurately
2. **Without Mapping File**: AI uses its knowledge to classify according to the standard you specify
3. **Hybrid Mode**: Combine mapping file with AI intelligence for best results

**⏱️ Processing Time:** 3-10 seconds per element group (varies by LLM model)

```mermaid
graph LR;
    A[CAD/BIM File] --> B[Convert to Excel];
    B --> C[Filter Elements];
    C --> D{Mapping File?};
    D -->|Yes| E[Extract Dictionary];
    D -->|No| F[Direct AI Classification];
    E --> G[AI Classification with RAG];
    F --> G;
    G --> H[Confidence Scoring];
    H --> I[Professional Reports];
```







### ⚡️ 6. Construction Price Estimation Pipeline for Revit and IFC with LLM (AI)
**File:** `n8n_6_Construction_Price_Estimation_Pipeline.json`

Automates cost estimation for building elements from CAD/BIM files. Uses AI to classify materials, search market prices, and generate comprehensive cost reports.

#### Key Features
- **AI Classification**: Materials across EU/DE/US standards
- **Smart Pricing**: Region-specific databases with fallbacks
- **Cost Analysis**: Total costs, cost per unit, top 10 groups
- **Multi-Format Output**: Excel workbook + HTML report with charts

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Construction_Price_Estimation_with_LLM_for_Revt_and_IFC-2.jpg" alt="Price Estimation" width="100%"/>
</p>


#### Installation
1. Import `Construction_Price_Estimation_Pipeline.json` into n8n
2. Configure AI credentials (OpenAI/Anthropic)
3. Update **Set Parameters** node:
   ```
   input_file_path: C:\Output\Project_Elements.xlsx
   grouping_parameter: Type Name )
   country: Germany
   ```
- Grouping parameter (group_by, e.g. 'Type Name', 'IfcType' for IFC or other)
- Country (country for which the values will be calculated, e.g. 'Germany'or 'Brazil')

**⏱️ Processing Time:** 5-15 seconds per element group (depends on LLM speed)

```mermaid
graph LR;
    A[CAD/BIM Excel] --> B[Group Elements];
    B --> C[AI Classification];
    C --> D[Price Search];
    D --> E[Cost Calculation];
    E --> F[Reports: Excel + HTML];
```



### ⚡️ 7. Carbon Footprint CO2 Estimator for Revit and IFC with LLM (AI)

**File:** `n8n_7_Carbon_Footprint_CO2_Estimator_for_Revit_and_IFC.json`

Calculates embodied carbon emissions for building projects. Analyzes materials, applies emission factors, and generates professional sustainability reports.

#### Key Features
- **Embodied Carbon Analysis**: A1-A3 lifecycle stages
- **Material Classification**: EU/DE/US standards with density data
- **Emission Factors**: Industry-standard CO2e factors per material
- **Impact Assessment**: Critical/High/Medium/Low categorization
- **Professional Reports**: McKinsey-style HTML + Multi-sheet Excel

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Carbon_Footprint_CO2_Estimator_for_Revit-and_IFC-1.jpg" alt="CO2 Estimator" width="100%"/>
</p>

#### Installation
1. Import `n8n_6_Carbon_Footprint_CO2_Estimator_for_Revit_and_IFC.json` into n8n
2. Configure AI credentials (OpenAI/Anthropic)
3. Update **Setup - Define file paths** node:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   group_by: Type Name (Category or other)
   country: Germany (country for which the values will be calculated, e.g. 'Germany'or 'Brazil')

   ```

**⏱️ Processing Time:** 5-15 seconds per element group (depends on LLM speed)


```mermaid
graph LR;
    A[Revit/IFC File] --> B[Convert to Excel];
    B --> C[Group Elements];
    C --> D[AI Material Analysis];
    D --> E[CO2 Calculation];
    E --> F[Generate Reports];
    F --> G[Excel + HTML Output];
```






### ⚡️ 8. Simple ETL for LLM Use Cases for Revit, IFC, DWG, DGN
**File**: `n8n_8_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.json`

Converts a Revit file to Excel, generates an XLSX filename, and parses data for LLM-based automation tasks.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX-1.jpg" alt="QTO Generator" width="100%"/>
</p>

#### Installation
1. Import `n8n_4_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.json` into n8n via **Workflows > Import from File**.
2. Update **Setup Paths** node:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   ```
3. Ensure the converter is accessible.

#### Usage
1. Run the workflow via **Manual Trigger**.
2. Check the output folder for the XLSX file.
3. Use the parsed data for LLM tasks (e.g., feed JSON to Claude or ChatGPT).
4. Monitor logs for conversion and parsing status.




### ⚡️ 9. Revit and IFC to HTML Quantity Takeoff
**File**: `n8n_9_CAD_BIM_Quantity_TakeOff_HTML_Report_Generatorn.json`

Analyzes Revit wall data, calculates volumes by type, and generates interactive HTML reports with summary statistics.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_CAD_BIM_Quantity_TakeOff_HTML_Report_Generator-2.jpg" alt="QTO Generator" width="100%"/>
</p>

#### Installation
1. Import `n8n_5_CAD_BIM_Quantity_TakeOff_HTML_Report_Generatorn.json` into n8n via **Workflows > Import from File**.
2. Update **Setup Paths** node:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   ```
3. Ensure the converter is accessible.

#### Usage
1. Run the workflow via **Manual Trigger**.
2. Check the output folder for the HTML report.
3. Review the report (auto-opens in browser) for wall quantities and statistics.
4. Monitor logs for processing status.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Setup Paths];
    B --> C[Run Converter];
    C --> D{Success?};
    D -->|No| E[Error Message];
    D -->|Yes| F[Read Excel];
    F --> G[Parse Data];
    G --> H[Filter Walls];
    H --> I[Clean Data];
    I --> J[Group & Sum];
    J --> K[Generate HTML];
    K --> L[Save Report];
    L --> M[Success];
```



## Troubleshooting

### Module 'os' Blocked Error
In n8n versions 1.98.0–1.101.x, the `os` module is blocked, affecting libraries like pandas. Solution: Use the latest version with `npx n8n@latest`.


## What is DataFrames?

CAD/BIM formats like `.rvt`, `.ifc`, `.dwg`, or `.dgn` are complex and proprietary. Converting them into **DataFrames**—tabular structures with rows (elements) and columns (properties)—enables efficient data processing. Popularized by Python’s pandas library, DataFrames are widely used for their compatibility with automation, analytics, and AI tools. They simplify tasks like filtering, grouping, and visualization, making them ideal for dashboards, quantity takeoffs, and validation.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/06/n8n-pipeline-11.jpg" alt="DataFrame Example" width="100%"/>
</p>

**Learn More:**
- [Python Pandas – An Indispensable Tool](https://datadrivenconstruction.io/2025/06/048-python-pandas-an-indispensable-tool-for-working-with-data/)
- [DataFrame – Universal Tabular Data Format](https://datadrivenconstruction.io/2025/06/049-dataframe-universal-tabular-data-format/)
- [Structured Data in Construction](https://datadrivenconstruction.io/2025/06/025-structured-data/)


## Re-import Data into Revit

After transforming and enriching your Excel data, you can effortlessly push the modified data back into your Revit project. Our dedicated tool **[ImportExcelToRevit](https://github.com/datadrivenconstruction/ImportExcelToRevit)** makes this process seamless by directly importing updated Excel sheets into Revit parameters and families.

> **Simplify your BIM workflow:** Revit ➡️ Excel ➡️ Transform ➡️ Excel ➡️ Revit.
https://github.com/datadrivenconstruction/ImportExcelToRevit

![enter image description here](https://datadrivenconstruction.io/wp-content/uploads/2024/07/project-data-3.gif)



## Contributing

We welcome contributions! Please feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation


## Support

🌐 **Website**: [DataDrivenConstruction.io](https://datadrivenconstruction.io)
💬 **Issues**: [GitHub Issues](https://github.com/datadrivenconstruction/Revit-IFC-DWG-DGN-Converter-in-n8n-with-QTO/issues)
📧 **Email**: info@datadrivenconstruction.io
  

## Consulting and Training

We work with leading construction, engineering, major consulting agencies and technology firms around the world to help them implement open data principles, automate CAD/BIM processing and build robust ETL pipelines.

If you would like to test this solution with your own data, or are interested in adapting the workflow to real project tasks, feel free to contact us.

Our team delivers hands-on workshops, provides strategic consulting, and develops prototypes tailored to real project processes. We actively support organizations seeking practical solutions for digital transformation and interoperability, focusing on data quality and classification challenges, and driving the adoption of open and automated workflows.

Contact us for a free consultation where we'll discuss your challenges and demonstrate how n8n automation can transform your operations. Reach out via Email at [@DataDrivenConstruction](mailto: info@datadrivenconstruction.io) or visit our website at [datadrivenconstruction.io](https://datadrivenconstruction.io) to learn more about our services.

---

<p align="left">
 
  <a href="https://datadrivenconstruction.io">
    <img src="https://datadrivenconstruction.io/wp-content/uploads/2023/07/DataDrivenConstruction-1-1.png" alt="DDC Logo" width="200"/>
  </a>
  <br>
   <b>   Unlock the Power of Data in Construction</b>
   <br>
     🚀 Move to full-cycle data management  where only unified <br /> structured data & processes remain and where  🔓 your data is yours
</p>

