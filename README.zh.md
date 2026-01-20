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
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto/blob/main/DDC_in_additon/DDC_readme_content/CAD%20BIM%20Pipeline%20and%20Workflow.jpg" alt="流程概览" width="100%"/>
</p>
<p align="center">

  <a href="LICENSE">
  <img src="https://img.shields.io/github/license/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto?color=blue&label=workflows%20licence" alt="工作流许可证: MIT">
</a>
<a href="https://datadrivenconstruction.io">
  <img src="https://img.shields.io/badge/powered%20by-DataDrivenConstruction.io-orange" alt="Powered by DataDrivenConstruction.io">
</a>
<img src="https://img.shields.io/badge/input-.rvt%20.dwg%20.ifc%20.dgn-blue?logo=autodesk&logoColor=white" alt="输入格式"></br>
<img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.dae%20.html%20.pdf%20.ifc-green?logo=microsoft-excel&logoColor=white" alt="输出格式">
<img src="https://img.shields.io/badge/ETL%20pipeline-Ready%20for%20CI/CD%20&%20Bots-success?logo=githubactions" alt="ETL 流程">

<!-- 定价 -->
<a href="https://dify.ai/pricing" target="_blank">
  <img alt="Static Badge" src="https://img.shields.io/badge/free-pricing?logo=free&color=%23155EEF&label=pricing&labelColor=%23528bff">
</a>
</br>


<h3 align="center">CAD/BIM（Revit、DWG、IFC、DGN）处理和转换，支持批量处理、分组、检查、成本估算和工程量报告。在开放代理和工作流中可视化自动化流程</h3>

<p align="center">
  使用 DDC UI、命令行、PowerShell 或工作流自动化您的 CAD/BIM 数据提取和转换 — 无供应商锁定，无需 Autodesk® 或 CAD 许可证，完全控制您的项目数据
</p>

<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto/blob/main/DDC_in_additon/DDC_readme_content/DDC_GithubLogo.jpg" alt="流程概览" width="100%"/>
</p>

## 目录

- [概述](#概述)
- [支持的格式](#支持的格式)
- [主要功能](#主要功能)
- [运行转换器](#运行转换器)
- [🖥️ 命令行界面 (CLI)](#️-命令行界面-cli)
- [使用 n8n 快速入门](#使用-n8n-快速入门)
- [支持](#支持)

## 概述

此流程自动将 CAD/BIM 文件转换为 Excel，用于工程量计算、数据分析和后续处理。支持离线操作，可通过 Python 或 AI 工具扩展。

## 支持的格式

| 格式 | 文件扩展名 | 转换器 | 输出 |
|------|-----------|--------|------|
| Revit (2015-2026) | `.rvt` | RvtExporter.exe | XLSX 数据库 + DAE 几何体 + 明细表 + PDF 图纸 |
| Revit (2015-2026) | `.rvt` | RVT2IFC_converter.exe | IFC2x3、IFC4、IFC4.3、IFCXML、IFCZIP、HDF5 |
| IFC (2x3, 4x1, 4x4, 4x, 4.3) | `.ifc` | IfcExporter.exe | XLSX 数据库 + DAE 几何体 |
| AutoCAD (1983-2026) | `.dwg` | DwgExporter.exe | XLSX 数据库 + PDF 图纸 |
| MicroStation (v7-v8) | `.dgn` | DgnExporter.exe | XLSX 数据库 |

## 主要功能

- 自动转换为 Excel（元素作为行，属性作为列）。
- 导出 3D 多边形几何体 (DAE)，元素 ID 与 XLSX 数据匹配。
- 离线处理，无需互联网、API 或许可证。
- 可扩展用于自定义后处理。

## 运行转换器

DDC 转换器可以通过不同方式启动 — **n8n 只是自动化的选项之一**。
根据您的工作流程和技术背景，您可以选择以下四种方法：

1. **图形用户界面 (UI)**
   - 最适合非技术用户和快速单次转换。
   - 直观的界面，无需设置 — 只需选择文件夹并开始。

2. **控制台/终端 (CMD、PowerShell、Shell)**
   - 适合高级用户、开发人员和技术团队。
   - 灵活且可脚本化，可集成到自动化脚本或批处理过程中。

3. **Python 或 JavaScript 流程**
   - 适合处理大型数据集的企业和团队。
   - 可扩展并行处理数百个 CAD (BIM) 文件。
   - `DDC_Python_pipelines` 文件夹中有现成示例。

4. **n8n 工作流**
   - 适合寻求**完全自动化和系统集成**的企业。
   - 端到端流程，CAD (BIM) 转换成为无缝数据流的一部分。
   - `DDC_n8n_workflows` 文件夹中有示例。

---

## 🖥️ 命令行界面 (CLI)

DDC 转换器是功能齐全的命令行工具，可以集成到**任何自动化工作流程**中。这使它们非常适合脚本编写、CI/CD 流程、AI 代理和低代码平台。

### 🤖 为什么 CLI 很重要：让 AI 构建您的流程

**CLI 工具的主要优势是 AI 可以直接使用它们。**

现代 AI 编程助手（**Claude Code**、**Cursor**、**GitHub Copilot**、**Windsurf**、**Aider**、**Cline**）可以执行 shell 命令、阅读文档并自主构建完整的自动化流程。这意味着：

> **您无需自己编写代码 — 只需描述您想要什么，AI 就会将 DDC 转换器集成到您的工作流程中。**

**工作原理：**
1. **复制此文档**（或将 AI 指向此 README）
2. **用自然语言描述您的任务**：*"将文件夹 X 中的所有 Revit 文件转换为 Excel，然后分析墙体数量"*
3. **AI 读取 CLI 语法**，编写脚本，执行并处理结果

**AI 可以使用 DDC 转换器做什么：**
- ✅ 自动批量转换数百个 CAD/BIM 文件
- ✅ 构建 ETL 流程：Revit → Excel → 数据库 → 仪表板
- ✅ 创建验证脚本检查 BIM 数据质量
- ✅ 从提取的数据生成报告（PDF、HTML、Excel）
- ✅ 将转换集成到 CI/CD 流程中
- ✅ 链接多个工具：转换 → 验证 → 分类 → 估算成本
- ✅ 通过 cron/任务计划程序安排自动处理

**AI 助手提示示例：**
```
我在 C:\Projects 中有 Revit 文件。使用位于 C:\DDC\ 的 DDC RvtExporter.exe，
将所有 .rvt 文件转换为带有边界框的 Excel，然后创建一个 Python 脚本
读取 XLSX 文件并生成所有墙体类型及其体积的汇总报告。
```

**这将 DDC 从一个工具转变为建筑数据自动化的 AI 原生构建块。**

### RvtExporter.exe — Revit 转 XLSX/DAE/PDF

```
===========================================
         DataDrivenConstruction
         DDC Revit Community
         Version: 17.1.1
===========================================

Usage: RvtExporter <输入文件> [<输出文件>] [<输出文件>] [<导出模式>] [<类别文件>] [bbox] [room] [schedule] [sheets2pdf] [-no-xlsx] [-no-collada]
```

| 参数 | 描述 |
|------|------|
| `<输入文件>` | 输入 `.rvt` / `.rfa` 文件（必需） |
| `[<输出文件>]` | `.dae` 文件的输出路径（可选，默认启用） |
| `[<输出文件>]` | `.xlsx` 文件的输出路径（可选，默认启用） |
| `[<导出模式>]` | `basic`（309 个类别）、`standard`（724 个）、`complete`（1209 个）或 `custom` |
| `[<类别文件>]` | 包含类别名称的 `.txt` 文件（仅在 `custom` 模式下需要） |
| `bbox` | 在 XLSX 输出中包含元素边界框 |
| `room` | 在 XLSX 输出中包含 ToRoom/FromRoom 数据 |
| `schedule` | 导出所有 Revit 明细表 |
| `sheets2pdf` | 将所有图纸导出为 PDF |
| `-no-xlsx` | 禁用导出到 `.xlsx` 格式 |
| `-no-collada` | 禁用导出到 `.dae` 格式 |

**示例：**
```bash
# 基本转换（XLSX + DAE）
RvtExporter.exe "C:\Projects\Building.rvt"

# 完整导出，包含边界框、明细表和 PDF 图纸
RvtExporter.exe "C:\Projects\Building.rvt" complete bbox schedule sheets2pdf

# 仅导出 XLSX（无 3D 几何体）
RvtExporter.exe "C:\Projects\Building.rvt" -no-collada

# 从文件自定义类别
RvtExporter.exe "C:\Projects\Building.rvt" custom "C:\Config\my_categories.txt"
```

---

### RVT2IFCconverter.exe — Revit 转 IFC

```
===========================================
         DataDrivenConstruction
         DDC RVT2IFC Community
         Version: 17.1.2
===========================================

Usage: Rvt2IfcConverter <input.rvt> [<output.ifc>] [preset|mode=<name>] [config="..."] [key=value ...]
```

| 参数 | 描述 |
|------|------|
| `<input.rvt>` | Revit 文件 `.rvt` / `.rfa`（必需） |
| `[<output.ifc>]` | 输出 IFC 路径（可选） |
| `preset=<name>` 或 `mode=<name>` | `standard`、`extended`、`custom` |
| `config="K=V; K=V; ..."` | 自定义配置（分号分隔） |
| `key=value` | 单独的配置参数 |

---

### 集成示例

#### 🔹 AI 编程助手（Claude Code、Cursor、Copilot、Windsurf、Aider、Cline）

具有终端访问权限的 AI 助手可以直接执行 DDC 转换器并构建完整的工作流程：

```bash
# 示例：当您询问"将我的 Revit 文件转换为 Excel"时，AI 执行此命令
RvtExporter.exe "C:\Projects\Model.rvt" complete bbox schedule
```

**真实的 AI 工作流场景：**

| 您对 AI 说 | AI 执行 |
|-----------|---------|
| *"将 Building.rvt 转换为包含所有数据的 Excel"* | 运行 `RvtExporter.exe Building.rvt complete bbox room` |
| *"处理此文件夹中的所有 Revit 文件"* | 编写 PowerShell 循环，为每个文件执行转换器 |
| *"导出为 IFC 4.3 格式"* | 使用正确的预设运行 `RVT2IFCconverter.exe` |
| *"从此模型创建成本估算"* | 转换为 Excel → 解析数据 → 计算成本 |
| *"验证 BIM 数据质量"* | 转换 → 分析 XLSX → 生成验证报告 |

**支持的 AI 工具：**
- **Claude Code** — 完整的终端访问，可以运行转换器并分析结果
- **Cursor** — 可以执行 shell 命令的 AI IDE
- **GitHub Copilot CLI** — 命令行 AI 助手
- **Windsurf** — 具有终端集成的 AI 驱动 IDE
- **Aider** — 终端中的 AI 配对编程
- **Cline** — 具有 shell 访问权限的 VS Code 扩展
- **Open Interpreter** — 本地运行代码的 AI
- **AutoGPT / AgentGPT** — 自主 AI 代理

**专业提示：** 与您的 AI 助手分享此 README，使其理解完整的 CLI 语法并能够自主构建复杂的流程。

#### 🔹 PowerShell / 批处理脚本
```powershell
# PowerShell：处理文件夹中的所有 .rvt 文件
Get-ChildItem "C:\Projects\*.rvt" | ForEach-Object {
    & "C:\DDC\RvtExporter.exe" $_.FullName
}
```

#### 🔹 Python Subprocess
```python
import subprocess

result = subprocess.run([
    r"C:\DDC\RvtExporter.exe",
    r"C:\Projects\Building.rvt",
    "complete", "bbox", "schedule"
], capture_output=True, text=True)

print(result.stdout)
```

#### 🔹 n8n（Execute Command 节点）
```javascript
// 在 n8n Execute Command 节点中
C:\DDC\RvtExporter.exe "{{ $json.filePath }}" complete bbox
```

---

## 使用 n8n 快速入门

### 先决条件

1. **安装 Node.js**，从 [nodejs.org](https://nodejs.org/) 下载。
2. **启动 n8n**，在命令提示符中运行：
   ```
   npx n8n
   ```
   访问 `http://localhost:5678`。
3. **从 GitHub 下载此仓库**
   - 点击绿色的 "Code" 按钮 → "Download ZIP"
   - 解压文件夹
4. **运行工作流**
     - 准备就绪。只需在 n8n 中点击 **Execute Workflow** 即可处理您的 CAD-BIM 文件

---

## 支持

🌐 **网站**：[DataDrivenConstruction.io](https://datadrivenconstruction.io)
💬 **问题**：[GitHub Issues](https://github.com/datadrivenconstruction/Revit-IFC-DWG-DGN-Converter-in-n8n-with-QTO/issues)
📧 **邮箱**：info@datadrivenconstruction.io

---

<p align="left">
  <a href="https://datadrivenconstruction.io">
    <img src="https://datadrivenconstruction.io/wp-content/uploads/2023/07/DataDrivenConstruction-1-1.png" alt="DDC Logo" width="200"/>
  </a>
  <br>
   <b>   释放建筑数据的力量</b>
   <br>
     🚀 转向全周期数据管理，只保留统一的 <br /> 结构化数据和流程，🔓 您的数据属于您
</p>
