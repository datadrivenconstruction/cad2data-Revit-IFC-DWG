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

<p align="center"><sub>下载太慢或 GitHub 无法访问？请使用镜像：<a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a>（文件相同，SHA-256 校验值相同）。</sub></p>

<h1 align="center">cad2data — 适用于 RVT、IFC 和 DWG 文件的 DDC 转换器</h1>

<p align="center">
  <b>将 CAD/BIM 文件转换为开放的结构化数据 — 本地、离线运行，无需 CAD 许可证。</b><br>
  .rvt / .rfa → GLB · glTF · OBJ · IFC4 · JSONL/CSV &nbsp;|&nbsp; .ifc → Excel · JSONL · SQLite &nbsp;|&nbsp; .dwg → Excel · CSV · JSONL · DXF · SVG
</p>

<p align="center">
  <a href="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest"><img src="https://img.shields.io/github/v/release/datadrivenconstruction/cad2data-Revit-IFC-DWG?label=release" alt="最新版本"></a>
  <img src="https://img.shields.io/badge/input-.rvt%20.rfa%20.ifc%20.ifczip%20.dwg-blue" alt="输入格式">
  <img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.jsonl%20.glb%20.ifc%20.dxf%20.svg-green" alt="输出格式">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Windows x64；Linux x64 和 arm64；macOS arm64 和 x64">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT%20(workflows%2C%20docs)%20%2B%20non-commercial%20EULA%20(converters)-blue" alt="许可证"></a>
</p>

<p align="center">
  <img src="docs/images/data-viewer-3d-grouped.png" alt="DDC Data Viewer：按类别和楼层分组的表格，以及与之联动的 3D 模型" width="100%">
</p>

---

<a id="whats-new-in-ddc-converters-20"></a>
## DDC Converters 2.0 新功能

DDC Converters 2.0 是整个产品线 2026 年 10 月的版本：RVT Converter 2.0、RVT to IFC 2.0、
IFC to Excel 2.0、CAD Drawing to Excel 2.0、Data Viewer 2.0 和 Excel Add-in 2.0。
当前的 RVT Converter 和 RVT to IFC 构建版本为 [2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2)。

- **每类格式一个工具。** `.rvt` / `.rfa` 转为 GLB、glTF、OBJ、IFC4 以及 JSONL / CSV / SQLite 表格；
  `.ifc` / `.ifczip` 转为 Excel、JSONL 和 SQLite；`.dwg` 转为 Excel、CSV、JSONL、DXF 和 SVG。
- **Revit 2016–2027** 文件可直接读取，无需安装 Revit。
- **从 Revit 导出 IFC4**，包含属性集、工程量、分类和材料，提供 `full`、`coordination` 和 `geometry` 三种配置；
  单位、原点、类别和阶段选项均可通过命令行设置。
- **处处保留元素 ID。** 每个几何节点都保留原生元素 ID，因此表格与 3D 可通过 `ElementId` 关联。
- **每次运行都有报告。** `report.json` / `summary.json` 以计数列出已读取和已跳过的内容。
- **桌面应用与命令行**，每个转换器均提供，退出码便于批处理，并为脚本输出单行 JSON 状态。
- **DDC Data Viewer 2.0：** 免费的表格与 3D 查看器，行与元素之间双向联动。
- **离线且便携。** Windows 10/11 x64，除软件包（安装程序或便携 zip）外无需安装任何其他内容。
  Linux（x64、arm64）和 macOS（arm64、x64）的命令行转换器及 Data Viewer 见 [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1)（参见 [DDC_LINUX_Converters](DDC_LINUX_Converters/README.md)）。

下载：[`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/)（便携版，开箱即用）以及
[Releases 页面](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases)（安装程序和软件包）。

<a id="contents"></a>
## 目录

- [转换器](#converters)
- [截图](#screenshots)
- [快速开始](#quick-start)
- [命令行](#command-line)
- [批处理与自动化](#batch-processing-and-automation)
- [DDC Data Viewer](#ddc-data-viewer)
- [免费工具：数据检查、工程量统计、Power BI 和 Excel](#free-tools-data-check-quantity-take-off-power-bi-and-excel)
- [n8n 工作流、Notebook 和 AI 智能体](#n8n-workflows-notebooks-and-ai-agents)
- [支持范围与说明](#supported-scope-and-notes)
- [仓库结构](#repository-layout)
- [许可](#licensing)
- [商标](#trademarks)

<a id="converters"></a>
## 转换器

| 软件包 | 版本 | 读取 | 写入 | 界面 |
|---|---|---|---|---|
| **DDC RVT Converter** | 2.0 | 由 Revit 2016–2027 保存的 `.rvt`、`.rfa` | GLB（默认）、glTF、OBJ、IFC4、元素表（`elements.xlsx`、`elements.csv`：类别、族、类型、楼层、面积、体积、长度、参数）、保存的属性（JSONL）；桌面应用还可写出 CSV 表格和 SQLite | 桌面应用 + `RVTconverter.exe` 命令行 |
| **DDC RVT to IFC** | 2.0 | `.rvt`、`.rfa` | 含属性集、工程量、分类、材料的 IFC4；配置 `full`、`coordination`、`geometry` | 桌面应用（命令行与 RVT Converter 相同） |
| **DDC IFC to Excel** | 2.0 | IFC2x3 / IFC4 STEP 文件、`.ifczip` | `drawing.xlsx`（对象、属性、工程量）、`data.jsonl`、`data.sqlite`、`result.json` | 桌面应用 + 命令行 |
| **DDC CAD Drawing to Excel** | 2.0 | `.dwg` 图纸，R13–2018 格式版本 | `.xlsx`（Entities、Summary、Layers、Blocks）、`.csv`、`.jsonl`、`.dxf`、`.svg`、`report.json` | 桌面应用 + `dwg2excel.exe` 命令行 |
| **DDC Data Viewer** | 2.0 | `.xlsx`、`.csv`、`.jsonl`、`.parquet` 表格 + `.glb` / `.dae` 几何 | 筛选后的视图导出为 XLSX / CSV | 桌面应用（免费） |

RVT Converter 写出的每个几何节点都保留原生元素 ID，因此表格与 3D 可通过 `ElementId`
关联。所有软件包均可在 Windows 10/11 x64 上完全离线运行，无需 Excel，
也无需安装 Python。Linux 和 macOS 命令行版本见 [v2026.10.1 版本](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1)。

<a id="screenshots"></a>
## 截图

以下所有截图均来自当前版本软件包的真实运行。它们使用开放的
Revit 示例模型（MIT 许可证）、查看器自带的合成示例建筑，以及 [`Sample_Projects/`](Sample_Projects/) 中的开放 IFC 示例。

| | |
|---|---|
| ![RVT Converter 2.0.2：两个 Revit 模型转换完成](docs/images/rvt-converter-done.png) | ![RVT to IFC 2.0.2：IFC 选项面板](docs/images/rvt-to-ifc-options.png) |
| **DDC RVT Converter** — 两个 Revit 模型已转换；结果文件夹按文件列出。 | **DDC RVT to IFC** — 长度单位、坐标原点及其他 IFC 设置位于*更多选项*中。 |
| ![Data Viewer：3D 选择与表格行联动](docs/images/data-viewer-3d-selection.png) | ![Data Viewer 中按 IFC 类分组的 IFC to Excel 输出](docs/images/ifc-to-excel-table.png) |
| **DDC Data Viewer** — 对*结构柱*的筛选会在 3D 中高亮显示关联元素；汇总面板对面积、体积和长度求和。 | **DDC IFC to Excel** — 开放 Duplex IFC 示例的 `drawing.xlsx`，按 IFC 类分组（333 个对象，23 个类）。 |
| ![RVTconverter 命令行运行](docs/images/cli-rvt-ifc.png) | ![深色主题的 Data Viewer](docs/images/data-viewer-dark.png) |
| **命令行** — `RVTconverter.exe` 写出 GLB、IFC4、元素表和报告，并打印状态摘要。 | **深色主题** — 深色主题下的 Data Viewer，右上角为界面语言切换。 |

<a id="quick-start"></a>
## 快速开始

1. 打开 [2.0.2 版本](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2)（RVT Converter、RVT to IFC）或 [Releases 页面](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases)（其他软件包），
   下载所需的软件包 — `*-Setup.exe`（按用户安装的安装程序）或 `*-portable.zip`。
2. 使用同一版本中的 `SHA256SUMS.txt` 校验下载文件：
   ```powershell
   Get-FileHash .\DDC-RVT-Converter-*-portable.zip -Algorithm SHA256
   ```
3. 将便携包解压到任意文件夹，例如 `C:\DDC\RVT-Converter\`、
   `C:\DDC\IFC-to-Excel\`、`C:\DDC\DWG-to-Excel\`。请保持文件夹结构不变。
4. 启动桌面应用（`RVT Converter.exe`、`IFC to Excel.exe`、`DWG to Excel.exe`），将文件或
   文件夹拖入窗口并点击*转换* — 或使用下面的命令行。
5. 在 Excel、Python/pandas 或 [DDC Data Viewer](#ddc-data-viewer) 中打开结果。

新下载的程序首次启动时，Windows SmartScreen 可能要求确认；请核对版本中的 SHA-256 校验值。

<a id="command-line"></a>
## 命令行

以下示例使用当前版本的二进制文件运行。路径假定便携包已解压到 `C:\DDC\`。

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

| 输出 | 何时生成 | 内容 |
|---|---|---|
| `native_graph.glb` | 始终 | 3D 网格，每个元素一个节点，以 ElementId 命名 |
| `summary.json`、`report.json` | 始终 | 状态、计数、遗漏项以及逐元素诊断信息 |
| `properties.jsonl`、`property_scopes.jsonl`（+ 清单文件） | `--properties` | 每个元素保存的参数（每行一个 JSON 对象） |
| `native_graph.ifc`、`ifc.manifest.json`、`ifc.settings.json` | `--ifc` | IFC4（三角化几何、属性集和工程量集） |
| `native_graph.gltf` + `.bin`、`native_graph.obj` + `.mtl` | `--gltf`、`--obj` | 与 GLB 相同的几何；OBJ 以米为单位，Y 轴向上 |

退出码：`0` 表示写出完成且无已报告的缺失，`2` 表示写出完成但有已报告的缺失（或参数无效），
`1` 表示转换或 I/O 失败。运行 `RVTconverter.exe --help` 查看全部 IFC 选项
（`--ifc-config`、`--ifc-phase`、`--ifc-design-options`、`--ifc-exclude-categories` 等）。

### DDC IFC to Excel

便携包的命令行：

```powershell
C:\DDC\IFC-to-Excel\runtime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py `
    "C:\Models\Building.ifc" --output "C:\Out\Building"
```

该命令会输出一行 JSON（`"status": "CONVERTED"`、`"CONVERTED_WITH_LIMITS"` 或 `"FAILED"`），
并创建一个新的子文件夹，其中包含 `drawing.xlsx`、`data.jsonl`、`data.sqlite` 和 `result.json`。
可直接接受 `.ifczip` 文件。

### DDC CAD Drawing to Excel — `dwg2excel.exe`

```powershell
# one or more drawings; a new sub-folder per drawing
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"

# a whole folder: tables only, one JSON line per file for scripts
$dwg = (Get-ChildItem C:\Drawings -Filter *.dwg).FullName
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe @dwg -o C:\Out --no-dxf --no-svg --json
```

每个图纸文件夹包含 `<name>.xlsx`、`<name>.csv`、`<name>.jsonl`、`<name>.dxf`、`<name>.svg`、
`report.json` 和 `REPORT.txt`。控制台输出的一行会报告已解码、已跳过以及
不受支持类型的记录数量。其他选项：`--timeout`、`--memory-limit-mb`、
`--language en|ru`、`--version`。

<a id="batch-processing-and-automation"></a>
## 批处理与自动化

**PowerShell — 文件夹树中的每个 RVT 文件：**

```powershell
$exe = "C:\DDC\RVT-Converter\cli\RVTconverter.exe"
Get-ChildItem "C:\Projects" -Recurse -Include *.rvt | ForEach-Object {
    & $exe $_.FullName -o (Join-Path "C:\Out" $_.BaseName) --properties --ifc
    "{0}: exit {1}" -f $_.Name, $LASTEXITCODE
}
```

**Python — 使用 pandas 加载 RVT 属性和 IFC 表格：**

```python
import json, subprocess, pandas as pd

subprocess.run([r"C:\DDC\RVT-Converter\cli\RVTconverter.exe", r"C:\Models\Project.rvt",
                "-o", r"C:\Out\Project", "--properties"], check=False)
rows = [json.loads(line) for line in open(r"C:\Out\Project\properties.jsonl", encoding="utf-8")]
print(len(rows), "property records")

objects = pd.read_excel(r"C:\Out\Building\Building-<id>\drawing.xlsx", sheet_name="Objects")
print(objects.groupby("Category").size().sort_values(ascending=False))
```

**CI 或机器人中的 DWG：** `dwg2excel.exe --json` 为每张图纸输出一行 JSON；解析它即可收集
状态、输出文件夹和解码统计信息。

<a id="ddc-data-viewer"></a>
## DDC Data Viewer

用于查看转换器输出的免费桌面查看器：支持 10 万行以上的虚拟化表格、搜索、筛选、
带求和的分组、列选择器、将当前视图导出为 XLSX/CSV，以及可在行
与元素之间双向联动的 3D 面板（GLB 或 DAE）。支持英语、德语和俄语；浅色和深色主题。
请从发布版本中下载 `DDC-Data-Viewer-<version>-Setup.exe` 或便携 zip。

<a id="free-tools-data-check-quantity-take-off-power-bi-and-excel"></a>
## 免费工具：数据检查、模型差异、BCF 问题、工程量统计、Power BI 和 Excel

[`ddc-tools/`](ddc-tools/)（Python 3.9+，MIT，离线）可处理转换器写出的表格
（XLSX、CSV、JSONL、SQLite、JSON）：

- `ddc check` 依据 YAML 规则（必需参数、正则表达式、唯一性、范围、
  允许值）验证导出结果，并写出带红绿灯标识、含 ElementId / GlobalId 详情的 XLSX、JSON 报告以及
  供 CI 使用的退出码。
- `ddc diff` 比较模型的两次导出（RVT、IFC 或 DWG 转换器输出）：新增 / 删除 / 修改的元素，
  每个属性和工程量的新旧值、变更日志 XLSX、JSON、按变更状态着色的 GLB，以及供 CI 使用的退出码。
- `ddc bcf` 将 `ddc check` 和 `ddc diff` 的发现写成 BCF 2.1 / 3.0 问题文件（构件按 IFC GlobalId 标识），并
  将任意 BCF 文件整理为 XLSX 表格。BCF 是 buildingSMART 的开放格式；不声称已获认证。
- `ddc qto` 按类别、类型和楼层汇总数量、长度、面积和体积，生成格式化的 XLSX，并对
  缺失或为零的工程量发出警告。
- [`ddc-tools/powerbi/`](ddc-tools/powerbi/) 和 [`ddc-tools/excel/`](ddc-tools/excel/)：Power Query 脚本
  和 Excel 工作簿，可读取整个导出文件夹，无需 Python
  （[步骤](ddc-tools/docs/POWER_QUERY.md)）。

```bash
pip install ./ddc-tools
ddc check Project.converted --rules ddc-tools/examples/rules_basic.yaml --xlsx check.xlsx
ddc qto Project.converted --xlsx qto.xlsx
ddc diff Model_v1.converted Model_v2.converted --xlsx changes.xlsx --glb diff.glb --bcf changes.bcf
```

Excel 和 Power BI 是 Microsoft Corporation 的商标，此处仅用于说明这些文件可配合使用的软件。

<a id="n8n-workflows-notebooks-and-ai-agents"></a>
## n8n 工作流、Notebook 和 AI 智能体

- [`DDC_n8n_Workflows&Pipelines/`](DDC_n8n_Workflows&Pipelines/) — 九个 n8n 工作流（转换、
  批量验证、AI 分类、成本与 CO2 估算、QTO 报告）。
- [`DDC_in_additon/DDC_python_pipelines/`](DDC_in_additon/DDC_python_pipelines/) — 用于
  转换、批处理和分析的 Jupyter Notebook。

> **设置：** 这些工作流和 Notebook 通过 `ddc convert` /
> `ddc table`（免费工具 [`ddc-tools/`](ddc-tools/)）调用 [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) 中的转换器，它会根据 `properties.jsonl` / IFC / DWG 输出生成扁平表格（`<name>_rvt.xlsx`，工作表 `Project_Data`：
> `ID`、`Category`、`Type Name`、`Level`、`Volume` 等）；3D 几何为 GLB。
> 一次性设置：`pip install ddc-tools\`。工作流和 Notebook 旁的 `README.md` 说明了已检查的内容和
> 未覆盖的内容（例如：n8n 5-7 的 AI 步骤需要您自己的凭据；计划任务和图纸 PDF 没有
> 对应功能；Revit 工程量来自 IFC 工程量或 GLB 网格）。

- [`AI_AGENTS_INSTRUCTIONS/`](AI_AGENTS_INSTRUCTIONS/) — 为编码智能体
  （AI 编码智能体）准备的现成上下文，包含当前命令行。在您的
  智能体中打开该仓库，然后提问，例如 *"convert every .rvt in C:\Projects to IFC and summarise the reports"*。
- [面向 AI 智能体的 DDC Skills](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
  — 面向建筑数据的现成自动化方案。

<a id="supported-scope-and-notes"></a>
## 支持范围与说明

- **RVT：** 不导出纹理；IFC 导出写出三角化的 IFC4。无法
  表示的元素会列在运行报告中。
- **IFC：** 支持 IFC2x3 和 IFC4 STEP 文件以及 `.ifczip`；不支持 IFCXML。原始记录始终保留在
  `data.jsonl` / `data.sqlite` 中。
- **DWG：** R13–2018 图纸。部分对象类型（例如某些表格、多重引线、3D 实体、
  图像）会在 `report.json` 中列为*不支持*，而不是被错误地导出。
- **平台：** Windows 10/11 x64。**Linux（x64、arm64）和 macOS（arm64、x64）：命令行转换器和 Data Viewer，见 [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1)。**

欢迎提交附带小型示例文件的错误报告 — 请使用
[GitHub Issues](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues)，并且不要附加
机密模型。

<a id="repository-layout"></a>
## 仓库结构

| 路径 | 内容 |
|---|---|
| `docs/` | 发布说明、截图 |
| `ddc-tools/` | 免费的数据检查、模型差异、BCF 问题、工程量统计、Power BI 和 Excel 工具包 |
| `DDC_n8n_Workflows&Pipelines/` | n8n 工作流 JSON 文件 |
| `DDC_in_additon/` | Notebook、演示文稿、图像 |
| `AI_AGENTS_INSTRUCTIONS/` | 面向 AI 编码智能体的说明 |
| `DDC_WINDOWS_Converters/` | 便携版 Windows 转换器（RVT、RVT-to-IFC、IFC to Excel、CAD Drawing to Excel、Data Viewer）、许可证文本以及 Excel → Revit 插件文档；安装程序位于 Releases 页面 |
| `DDC_LINUX_Converters/` | CWICR 数据包、Qdrant 打包和遥测仪表板 |
| `Sample_Projects/` | 开放的 IFC 示例文件 |

<a id="licensing"></a>
## 许可

- **工作流、Notebook、脚本、AI 说明、文档和 `ddc-tools`** — [MIT 许可证](LICENSE)。
  开源，允许商业使用。
- **DDC 转换器**（Releases 以及 `DDC_WINDOWS_Converters/` / `DDC_LINUX_Converters/` 中的二进制软件包）—
  专有软件，**仅限非商业用途免费使用。商业使用需按需申请许可证：**
  [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io)。条款：[EULA](EULA.md)、
  [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) 和 [NOTICE](NOTICE)。第三方开源组件
  及其许可证列于每个软件包内的 `licenses/` 中。
- `ddc-tools` 的 MIT 许可证不适用于其所调用的转换器。

**商业使用**是指由企业、公司、个体从业者、公共
机构或其他组织（包括其员工或承包商）使用或代表其使用；用于有偿工作或服务，包括
为客户处理文件；用于产生或旨在产生收入的项目；或用于向他人提供的
产品、服务、流水线或 SaaS 产品之中。再分发、OEM 和 SaaS 集成
同样属于商业使用。
**非商业使用**是指个人学习和业余爱好使用、学术研究、学生和教师的教学与学习，
以及非营利组织的评估，且均不涉及付款、收入
或商业目的。

安全报告：见 [SECURITY.md](SECURITY.md)。专利、商标和出口管制：
[PATENTS.md](PATENTS.md)、[TRADEMARK.md](TRADEMARK.md)、[EXPORT-COMPLIANCE.md](EXPORT-COMPLIANCE.md)。

<a id="consulting-and-training"></a>
## 咨询与培训

DataDrivenConstruction 帮助建筑、工程和技术公司自动化 CAD/BIM 数据
处理并构建开放的 ETL 流水线 — 基于您的真实数据提供工作坊、咨询和原型。
请联系 [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io) 或访问
[datadrivenconstruction.io](https://datadrivenconstruction.io)。

<p>
  <a href="https://x.com/datadrivenconst"><img src="https://img.shields.io/twitter/follow/datadrivenconst?logo=X&style=flat&color=%23f5f5f5" alt="在 X 上关注"></a>
  <a href="https://www.youtube.com/@datadrivenconstruction"><img src="https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://www.linkedin.com/company/78381569"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?logoColor=white" alt="LinkedIn"></a>
</p>

如果这些工具对您有帮助，请为仓库加星，以便接收新版本通知。

<a id="trademarks"></a>
## 商标

Autodesk 和 Revit 是 Autodesk, Inc. 的商标。DataDrivenConstruction 是独立软件，与 Autodesk, Inc. 无关联，也未获其认可。RVT、RFA、DWG、DXF 和 IFC 是文件格式名称，仅用于说明读取哪些文件。
