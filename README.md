# 🏗️ CAD/BIM Converter to Excel + Geometry (+BBOX, +Schedules, +PDF Drawings) + Pipeline QTO Takeoff 

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/06/n8n-pipeline.jpg" alt="Pipeline Overview" width="100%"/>
</p>

**Convert your CAD/BIM files to structured data and 3D geometry without Autodesk® licences or APIs, for free and in open tools**
[![n8n](https://img.shields.io/badge/powered%20by-n8n-ff6d5a)](https://n8n.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![DataDrivenConstruction](https://img.shields.io/badge/by-DataDrivenConstruction-orange)](https://datadrivenconstruction.io)

## Overview

This automated pipeline converts CAD/BIM (`.rvt`, `.dwg`, `.ifc`, `.dgn`) files into structured Excel data and 3D geometry (DAE) using n8n workflow automation. Perfect for quantity takeoffs, data analysis, and downstream processing without requiring expensive licenses.

## Supported Formats

| Format | File Extension | Converter | Output |
|--------|----------------|-----------|--------|
| **Revit** | `.rvt` | RvtExporter.exe | Excel + DAE geometry |
| **IFC** | `.ifc` | IfcExporter.exe | Excel + DAE geometry |
| **AutoCAD** | `.dwg` | DwgExporter.exe | Excel data |
| **MicroStation** | `.dgn` | DgnExporter.exe | Excel data |

## Key Features

- 🔄 **Automated Conversion**: One-click conversion from CAD/BIM to Excel
- 📊 **Structured Data**: All elements and properties exported as Excel matrix DataFrame - project elements with native ID in the rows, all properties of all elements in the columns
- 🧱 **3D Geometry**: Polygonal geometry export for Revit/IFC (DAE format) with the native ID, which is also in DataFrame XLSX. In this way you get full project meta-information with geometry of each element
- 🖥️ **Offline Processing**: No internet, APIs, plugins or Autodesk® licenses required
- 📈 **Quantity Takeoffs**: Built-in QTO report generation for walls
- 🔧 **Extensible**: Easy to customize with Python or AI post-processing

## Quick Start

### Prerequisites
- [Node.js](https://nodejs.org/) installed
- [n8n](https://n8n.io/download) workflow platform
- DDC Converters ([Download](https://cadbimconverter.com/convertors/))

### Installation

1. **Install n8n**
   ```bash
   npx n8n
   ```

2. **Download Converters**
   - Place converter executables in a dedicated folder (e.g., `C:\Converters\`)

3. **Import Workflow**
   - Download workflow JSON from this repository
   - In n8n: **Import from file** → Select JSON
   - Configure file paths in the **Set** node

### Configuration Example

```javascript
// Basic conversion setup
path_to_converter: "C:\\Converters\\RvtExporter.exe"
source_file: "C:\\Projects\\Sample.rvt"
```


# ⚡️ Available Workflows

## 1. Basic Conversion
**File**: `n8n_Revit_IFC_DWG_Conversation_simple.json`

- Simple file conversion to Excel + geometry (for Revit and IFC)
- Minimal configuration required

```mermaid
graph TD;
    A[🟢 Manual Trigger] --> B[🛠 Set Basic Variables]
    B --> C[🧰 Execute Pipeline]
    C --> D[📂 Output XLSX DataFrame / +DAE for Revit and IFC]
```
Example Variables
```# Revit
path_to_converter: C:\Converters\RvtExporter.exe
source_file:       C:\Projects\Model.rvt

# IFC
path_to_converter: C:\Converters\IfcExporter.exe
source_file:       C:\Projects\Model.ifc

# DWG
path_to_converter: C:\Converters\DwgExporter.exe
source_file:       C:\Projects\Plan.dwg

# DGN
path_to_converter: C:\Converters\DgnExporter.exe
source_file:       C:\Projects\Bridge.dgn
```



<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/06/n8n_Revit_IFC_DWG_Conversation_simple-1.jpg" alt="QTO Report Sample" width="100%"/>
</p>

### 🔄 From CAD/BIM to DataFrame: Structuring the Future of Construction Data

Various CAD and BIM formats — such as `.rvt`, `.ifc`, `.dwg`, or `.dgn` — are often complex, closed, and difficult to work with.  
That's why we convert them into one of the most universal and powerful formats in modern data processing: the **DataFrame**.

A **DataFrame** is a tabular structure that organizes data into rows and columns — just like a spreadsheet, but designed for automation, analytics, and AI.

In the world of automation, analytics, and digital construction, **structured data** is the foundation — and DataFrames make it usable, transparent, and scalable.

> “Data processing is what probably one third of the world’s computing is done in every company. The data processing and data of most companies are in DataFrame, in table format”  
> – Jensen Huang, CEO of Nvidia (“NVIDIA CEO Jensen Huang Keynote at COMPUTEX 2024,” June 2, 2024), [Post #049](https://datadrivenconstruction.io/2025/06/049-dataframe-universal-tabular-data-format/)*

---

### 📊 Why DataFrames Matter

- ✅ Clear, structured format (rows = records, columns = properties)
- 🔄 Easily processed in ETL pipelines
- ⚙️ Fully compatible with **Python**, **pandas**, **n8n**, and LLMs
- 📈 Ideal for dashboards, analytics, validation, and reporting

From **automated QTO reports** to **quality checks and IFC parsing**,  
**DataFrames are the universal interface** between raw BIM data and intelligent workflows.

---

### 📚 Learn More:
- [048: Python Pandas – An Indispensable Tool](https://datadrivenconstruction.io/2025/06/048-python-pandas-an-indispensable-tool-for-working-with-data/)  
- [049: DataFrame – Universal Tabular Data Format](https://datadrivenconstruction.io/2025/06/049-dataframe-universal-tabular-data-format/)  
- [025: Structured Data in Construction](https://datadrivenconstruction.io/2025/06/025-structured-data/)
  
<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/06/n8n-pipeline-11.jpg" alt="QTO Report Sample" width="100%"/>
</p>

A DataFrame is the most widely used data structure in modern data processing and automation.
Popularized by tools like pandas in Python, it represents data in a simple table format — rows and columns — making it easy to filter, group, analyze, and visualize.

From financial modeling to BIM quantity take-offs, from AI training sets to engineering reports, the DataFrame has become the universal language of data-driven workflows. Its flexibility, readability, and compatibility with ETL pipelines make it the foundation of almost every modern automation task.


</p>
</p>
## 2. CAD-BIM data conversion with advanced settings (+BBOX, +Schedules, +PDF Drawings)
**File**: `n8n_All_Settings_Revit_IFC_DWG_Conversation_simple.json`

- Full control over export parameters
- Custom export modes: `basic`, `standard`, `complete`
- Optional features: +BoundingBox, +Revit Schedules, +PDF export for Drawings

#### Export Modes
- **Basic**: Essential geometry and properties
- **Standard**: Includes materials and parameters
- **Complete**: Full model data with relationships

#### Optional Outputs
- `bbox`: Include bounding box geometry
- `schedule`: Export Revit schedules
- `sheets2pdf`: Convert sheets to PDF
- `-no-xlsx`: Skip Excel export
- `-no-collada`: Skip geometry export
  

```mermaid
graph TD;
    A[🟢 Manual Trigger] --> B[🛠 Set Advanced Variables]
    B --> C[⚙️ Configure Export Mode]
    C --> D[🧰 Execute Pipeline]
    D --> E{Export Options}
    E -->|Standard| F[📊 XLSX + DAE]
    E -->|+BBox of Elements| G[📊 XLSX + DAE + BBox]
    E -->|+Revit Schedules in Excel| H[📊 XLSX + DAE + Schedules]
    E -->|+Drawings PDF| I[📊 XLSX + DAE + PDF]
```
<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/06/n8n_All_Settings_Revit_IFC_DWG_Conversation_simple-2.jpg" alt="QTO Report Sample" width="100%"/>
</p>
</p>
</p>
## 3. Simple ETL Pipeline ready for use in LLM chats as a basis for use cases
**File**: `n8n_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.json`

This straightforward **n8n pipeline** generates an Excel filename (XLSX) automatically after converting a Revit file, making it ready for immediate use in various tasks.

###  Pipeline Steps:

1. **Manual Start:** Trigger the workflow.
2. **Setup Paths:** Define paths to Revit converter and source RVT file.
3. **Conversion:** Convert RVT to XLSX.
4. **Check Result:** Verify conversion success.
5. **Generate XLSX Name:** Automatically create the Excel filename.
6. **Load Excel File:** Read and parse the Excel file into structured data.

You can also feed this JSON into Claude, DeepSeek, or ChatGPT, and the LLM will generate the code automatically. All that's left to do is import the generated code into n8n.

### Usage:
- Import JSON into n8n.
- Customize for your tasks.
- Automate similar ETL tasks easily.


<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/06/n8n_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.jpg" alt="QTO Report Sample" width="100%"/>
</p>

</p>
</p>
## 4. ETL Example from LLM (created in Claude) - Revit to HTML Quantity Takeoff Generator
**File**: `n8n_CAD_BIM_Quantity_TakeOff_HTML_Report_Generatorn.json`

- Automated wall quantity analysis
- Professional HTML reports
- Volume calculations by wall type

**Generated Reports Include:**
- 📊 Summary statistics (total elements, volumes, averages)
- 📋 Detailed breakdown by element type - "Type Name"
- 🎨 Interactive HTML dashboard

```mermaid
graph TD;
    A[🟢 Manual Trigger] --> B[🛠 Setup File Paths]
    B --> C[🔄 Run Revit Converter]
    C --> D{Conversion Success?}
    D -->|❌ Error| E[Show Error Message]
    D -->|✅ Success| F[📖 Read Excel File]
    F --> G[🔍 Parse to JSON]
    G --> H[🏗️ Filter OST_Walls]
    H --> I[🧹 Clean Wall Data]
    I --> J[📊 Group by Type & Sum Volume]
    J --> K[🎨 Generate HTML Report]
    K --> L[💾 Save Report File]
    L --> M[✅ Success Summary]
```



<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/06/n8n_CAD_BIM_Quantity_TakeOff_HTML_Report_Generator.jpg" alt="QTO Report Sample" width="100%"/>
</p>




## Next Level Automation

For AI-powered processing and advanced automation:

🤖 **[Full LLM Pipeline](https://github.com/datadrivenconstruction/CAD-BIM-to-Code-Automation-Pipeline-DDC-Workflow-with-LLM-ChatGPT)**

Features ChatGPT integration, element classification, and code generation.



## Contributing

We welcome contributions! Please feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation


## Support

- 🌐 **Website**: [DataDrivenConstruction.io](https://datadrivenconstruction.io)
- 💬 **Issues**: [GitHub Issues](https://github.com/datadrivenconstruction/Revit-IFC-DWG-DGN-Converter-in-n8n-with-QTO/issues)
- 📧 **Email**: info@datadrivenconstruction.io
  

## Consulting & Industry Training

We work with leading construction, engineering, major consulting agencies and technology firms around the world to help them implement open data principles, automate CAD/BIM processing and build robust ETL pipelines.

Our team provides hands-on workshops, strategic advice and prototyping with real-world project workflows in mind.

Over the last few years we have actively supported organisations seeking practical solutions for digital transformation and interoperability. Many have enquired about solving data quality problems - wanting to implement the open and automated methods we advocate. Today, these approaches are used in all planning, design and construction workflows around the world.

For inquiries or workshop bookings, visit [DataDrivenConstruction.io](https://datadrivenconstruction.io).


---

<p align="left">
 
  <a href="https://datadrivenconstruction.io">
    <img src="https://datadrivenconstruction.io/wp-content/uploads/2023/07/DataDrivenConstruction-1-1.png" alt="DDC Logo" width="200"/>
  </a>
  <br>
   <b>   Unlock the Power of Data in Construction</b>
   <br>
     🚀 Move to full-cycle data management  where only unified granular  <br /> structured data & processes remain and where  🔓 your data is yours
</p>
