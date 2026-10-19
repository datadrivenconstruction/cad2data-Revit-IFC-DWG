<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ar.md">العربية</a>
</p>

# cad2data — 适用于 RVT、IFC 和 DWG 文件的 DDC 转换器

**在本地离线将 CAD/BIM 文件转换为开放的结构化数据，无需 CAD 许可证。**

<p align="center"><img src="docs/images/data-viewer-3d-grouped.png" width="100%" alt="DDC Data Viewer"></p>

## 2026 年 10 月更新

转换器现已基于 **DataDrivenConstruction 自研的文件读取器**（RVT：Rust；IFC 与 DWG：Python），不再依赖任何第三方 CAD SDK。旧版 18.x 程序（`RvtExporter.exe`、`IfcExporter.exe`、`DwgExporter.exe`、`DgnExporter.exe`、`RVT2IFCconverter.exe`）已停用并从仓库中移除；新软件包发布在 [Releases 页面](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases)。暂不支持 DGN。所有新转换器均为预览版，每次运行都会生成报告，说明已读取、跳过或拒绝的内容。

## 转换器

| 软件包 | 版本 | 输入 | 输出 |
|---|---|---|---|
| **DDC RVT Converter** | 0.6.8 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV |
| **DDC RVT to IFC** | 0.6.8 | `.rvt`, `.rfa` | IFC4 |
| **DDC IFC to Excel** | 0.3.1 preview | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC DWG to Excel** | 0.4.1 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 0.1.1 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

所有软件包均可在 Windows 10/11 x64 上离线运行，无需 Autodesk 软件、Excel 或 Python。

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

n8n 工作流和 Jupyter Notebook 是为旧版 18.x 命令行（XLSX + DAE）编写的，正在迁移到新转换器。在此之前，请修改转换器路径并调整解析步骤（RVT 属性为 `properties.jsonl`，几何为 GLB）。`AI_AGENTS_INSTRUCTIONS/` 已包含新命令。

## 限制

RVT：几何完整性未经认证，不导出纹理，IFC4 为三角化几何。IFC：不支持 IFCXML。DWG：部分对象类型会被报告为不支持，而不是错误导出——请查看 `report.json`。目前仅支持 Windows x64；Linux / macOS 即将推出（coming soon）。

## 许可

工作流、Notebook、脚本和文档：[MIT](LICENSE)。转换器软件包：依据随附的 DataDrivenConstruction EULA 可免费用于个人和商业用途；另见 [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) 和 [NOTICE](NOTICE)。

## 商标

Autodesk®、Revit® 和 AutoCAD® 是 Autodesk, Inc. 的注册商标。IFC 和 buildingSMART® 是 buildingSMART International Ltd. 的商标。文件格式名称（RVT、RFA、DWG、DXF、DGN）仅用于标识文件格式。DataDrivenConstruction 与 Autodesk, Inc. 无关联，亦未获其认可或认证。完整文本见 [README.md](README.md#trademarks)。
