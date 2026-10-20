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

<p align="center"><sub>GitHub 下载慢或无法访问？请使用镜像下载：<a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a>（文件相同，SHA-256 校验值相同）。</sub></p>

# cad2data — 适用于 RVT、IFC 和 DWG 文件的 DDC 转换器

**在本地离线将 CAD/BIM 文件转换为开放的结构化数据，无需 CAD 许可证。**

<p align="center"><img src="docs/images/data-viewer-3d-grouped.png" width="100%" alt="DDC Data Viewer"></p>

## DDC Converters 2.0 新功能

整个产品线的 2026 年 10 月版本：RVT Converter 2.0、RVT to IFC 2.0、IFC to Excel 2.0、CAD Drawing to Excel 2.0、Data Viewer 2.0 和 Excel Add-in 2.0。

- **每类格式一个工具。** `.rvt` / `.rfa` 转为 GLB、glTF、OBJ、IFC4 以及 JSONL / CSV / SQLite 表格；`.ifc` / `.ifczip` 转为 Excel、JSONL 和 SQLite；`.dwg` 转为 Excel、CSV、JSONL、DXF 和 SVG。
- **Revit 2019–2027** 文件可直接读取，无需 Autodesk 软件，也无需 CAD 许可证。
- **从 Revit 导出 IFC4**，包含属性集、工程量、分类和材料，提供 `full`、`coordination` 和 `geometry` 三种配置；单位、原点、类别和阶段可通过命令行设置。
- **处处保留元素 ID。** 每个几何节点都保留原生元素 ID，表格与 3D 可通过 `ElementId` 关联。
- **每次运行都有报告。** `report.json` / `summary.json` 以计数列出已读取和已跳过的内容。
- **桌面应用与命令行**，每个转换器均提供，退出码适合批处理，并为脚本输出单行 JSON 状态。
- **DDC Data Viewer 2.0：** 免费的表格与 3D 查看器，行与元素双向联动。
- **离线且便携。** Windows 10/11 x64；除软件包（安装程序或便携 zip）外无需安装任何内容。Linux / macOS 版本即将推出（coming soon）。

下载：[`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/)（便携版，开箱即用）以及 [Releases 页面](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases)（安装程序和软件包）。

## 转换器

| 软件包 | 版本 | 输入 | 输出 |
|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV / SQLite |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4（属性集、工程量、分类、材料） |
| **DDC IFC to Excel** | 2.0 | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC CAD Drawing to Excel** | 2.0 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 2.0 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

RVT Converter 写出的每个几何节点都保留原生元素 ID，表格与 3D 可通过 `ElementId` 关联。所有软件包均可在 Windows 10/11 x64 上离线运行，无需 Autodesk 软件、Excel 或 Python。Linux / macOS 版本即将推出（coming soon）。

## 截图

当前软件包的真实运行结果：查看器自带的合成示例建筑，以及 `Sample_Projects/` 中的开放 IFC 示例。

| | |
|---|---|
| ![](docs/images/data-viewer-3d-selection.png) | ![](docs/images/ifc-to-excel-table.png) |
| ![](docs/images/cli-rvt-ifc.png) | ![](docs/images/data-viewer-dark-ru.png) |

## 快速开始

1. 从[最新版本](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest)下载软件包（`*-Setup.exe` 或 `*-portable.zip`），并用 `SHA256SUMS.txt` 校验。
2. 将便携版解压到例如 `C:\DDC\`。
3. 启动桌面应用，或使用命令行：

```powershell
# RVT / RFA -> GLB + IFC4 + properties (JSONL)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --properties --ifc

# IFC / IFCZIP -> Excel + JSONL + SQLite
C:\DDC\IFC-to-Exceluntime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out\Building"

# DWG -> Excel + CSV + JSONL + DXF + SVG
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"
```

全部选项、输出文件和退出码请参阅[英文 README](README.md#command-line)。

## n8n 工作流、Notebook 与 AI 智能体

n8n 工作流（`DDC_n8n_Workflows&Pipelines/`）和 Jupyter Notebook 通过 `ddc convert` / `ddc table`（免费工具 [`ddc-tools/`](ddc-tools/)）调用转换器，并由转换器输出构建平面表格（`*_rvt.xlsx`，工作表 `Project_Data`）；3D 几何为 GLB。一次性安装：`pip install ddc-tools\`。已验证的内容和未覆盖的内容见工作流和 Notebook 旁边的 `README.md`。`AI_AGENTS_INSTRUCTIONS/` 提供包含当前命令行的上下文。

## 支持范围与说明

- **RVT：** 不导出纹理；IFC 导出写出三角化（tessellated）的 IFC4。无法表示的元素会列入运行报告。
- **IFC：** 支持 IFC2x3 和 IFC4 STEP 文件以及 `.ifczip`；不支持 IFCXML。原始记录始终保留在 `data.jsonl` / `data.sqlite` 中。
- **DWG：** 支持 R13–2018 图纸。部分对象类型（例如某些表格、多重引线、3D 实体、图像）会在 `report.json` 中列为*不支持*，而不是错误导出。
- **平台：** Windows 10/11 x64。**Linux / macOS 即将推出（coming soon）。**

## 许可

工作流、Notebook、脚本、文档和 `ddc-tools`：[MIT](LICENSE)（开源，可用于商业用途）。转换器软件包（DDC 二进制文件）：专有软件，**仅限非商业用途免费**；商业用途需向我们申请许可：info@datadrivenconstruction.io。详见 [EULA](EULA.md)、[LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) 和 [NOTICE](NOTICE)。`ddc-tools` 的 MIT 许可不适用于它所调用的转换器。

**商业用途**指由企业、个体经营者、公共机构或其他组织（含其员工）使用或为其使用，用于有偿工作或服务（包括为客户处理文件）、产生或意图产生收入的项目，或用于向他人提供的产品、服务、流水线或 SaaS。**非商业用途**指个人学习、学术研究、师生教学与学习，以及非营利组织的评估，且均无报酬、收入或商业目的。

## 商标

Autodesk®、Revit® 和 AutoCAD® 是 Autodesk, Inc. 的注册商标。IFC 和 buildingSMART® 是 buildingSMART International Ltd. 的商标。文件格式名称（RVT、RFA、DWG、DXF、DGN）仅用于标识文件格式。DataDrivenConstruction 与 Autodesk, Inc. 无关联，亦未获其认可或认证。完整文本见 [README.md](README.md#trademarks)。
