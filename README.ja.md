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

<p align="center"><sub>ダウンロードが遅い、または GitHub にアクセスできない場合は、ミラーをご利用ください：<a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a>（同一ファイル、同一の SHA-256 値）。</sub></p>

<h1 align="center">cad2data — RVT・IFC・DWG ファイル用 DDC コンバーター</h1>

<p align="center">
  <b>CAD/BIM ファイルを、オープンで構造化されたデータに — ローカルで、オフラインで、CAD ライセンス不要。</b><br>
  .rvt / .rfa → GLB · glTF · OBJ · IFC4 · JSONL/CSV &nbsp;|&nbsp; .ifc → Excel · JSONL · SQLite &nbsp;|&nbsp; .dwg → Excel · CSV · JSONL · DXF · SVG
</p>

<p align="center">
  <a href="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest"><img src="https://img.shields.io/github/v/release/datadrivenconstruction/cad2data-Revit-IFC-DWG?label=release" alt="最新リリース"></a>
  <img src="https://img.shields.io/badge/input-.rvt%20.rfa%20.ifc%20.ifczip%20.dwg-blue" alt="入力形式">
  <img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.jsonl%20.glb%20.ifc%20.dxf%20.svg-green" alt="出力形式">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Windows x64、Linux x64 および arm64、macOS arm64 および x64">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT%20(workflows%2C%20docs)%20%2B%20non-commercial%20EULA%20(converters)-blue" alt="ライセンス"></a>
</p>

<p align="center">
  <img src="docs/images/data-viewer-3d-grouped.png" alt="DDC Data Viewer：カテゴリーとレベルでグループ化した表と、連動する 3D モデル" width="100%">
</p>

---

<a id="whats-new-in-ddc-converters-20"></a>
## DDC Converters 2.0 の新機能

DDC Converters 2.0 は、製品ライン全体の 2026 年 10 月リリースです。RVT Converter 2.0、RVT to IFC 2.0、
IFC to Excel 2.0、CAD Drawing to Excel 2.0、Data Viewer 2.0、Excel Add-in 2.0 が含まれます。
現在の RVT Converter と RVT to IFC のビルドは [2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2) です。

- **形式ファミリーごとに 1 つのツール。** `.rvt` / `.rfa` から GLB、glTF、OBJ、IFC4 と JSONL / CSV / SQLite テーブルへ。
  `.ifc` / `.ifczip` から Excel、JSONL、SQLite へ。`.dwg` から Excel、CSV、JSONL、DXF、SVG へ。
- **Revit 2016～2027** のファイルを直接読み込みます。Revit のインストールは不要です。
- **Revit からの IFC4 出力。** プロパティセット、数量、分類、材料に対応し、プロファイルは
  `full`、`coordination`、`geometry`。単位、原点、カテゴリー、フェーズのオプションをコマンドラインで指定できます。
- **あらゆる場所に要素 ID。** すべてのジオメトリノードがネイティブの要素 ID を保持するため、表と 3D を `ElementId` で結合できます。
- **実行ごとにレポート。** `report.json` / `summary.json` に、読み込んだ内容とスキップした内容が件数付きで記録されます。
- **各コンバーターにデスクトップアプリとコマンドライン。** バッチ処理向けの終了コードと、スクリプト用の 1 行 JSON ステータスを備えます。
- **DDC Data Viewer 2.0：** 行と要素を双方向に連動させる、無料の表・3D ビューアーです。
- **オフラインでポータブル。** Windows 10/11 x64。パッケージ（インストーラーまたはポータブル zip）以外にインストールするものはありません。
  Linux（x64、arm64）と macOS（arm64、x64）のコマンドラインコンバーターおよび Data Viewer は [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1) にあります（[DDC_LINUX_Converters](DDC_LINUX_Converters/README.md) を参照）。

ダウンロード：[`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/)（ポータブル版、すぐに実行可能）と
[Releases ページ](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases)（インストーラーとパッケージ）。

<a id="contents"></a>
## 目次

- [コンバーター](#converters)
- [スクリーンショット](#screenshots)
- [クイックスタート](#quick-start)
- [コマンドライン](#command-line)
- [バッチ処理と自動化](#batch-processing-and-automation)
- [DDC Data Viewer](#ddc-data-viewer)
- [無料ツール：データチェック、数量拾い出し、Power BI と Excel](#free-tools-data-check-quantity-take-off-power-bi-and-excel)
- [n8n ワークフロー、ノートブック、AI エージェント](#n8n-workflows-notebooks-and-ai-agents)
- [対応範囲と注意事項](#supported-scope-and-notes)
- [リポジトリ構成](#repository-layout)
- [ライセンス](#licensing)
- [商標](#trademarks)

<a id="converters"></a>
## コンバーター

| パッケージ | バージョン | 読み込み | 書き出し | インターフェース |
|---|---|---|---|---|
| **DDC RVT Converter** | 2.0 | Revit 2016～2027 で保存された `.rvt`、`.rfa` | GLB（既定）、glTF、OBJ、IFC4、要素テーブル（`elements.xlsx`、`elements.csv`：カテゴリー、ファミリ、タイプ、レベル、面積、体積、長さ、パラメーター）、保存済みプロパティ（JSONL）。デスクトップアプリは CSV テーブルと SQLite も出力 | デスクトップアプリ + `RVTconverter.exe` CLI |
| **DDC RVT to IFC** | 2.0 | `.rvt`、`.rfa` | プロパティセット、数量、分類、材料を含む IFC4。プロファイル `full`、`coordination`、`geometry` | デスクトップアプリ（RVT Converter と同じコマンドライン） |
| **DDC IFC to Excel** | 2.0 | IFC2x3 / IFC4 STEP ファイル、`.ifczip` | `drawing.xlsx`（オブジェクト、プロパティ、数量）、`data.jsonl`、`data.sqlite`、`result.json` | デスクトップアプリ + コマンドライン |
| **DDC CAD Drawing to Excel** | 2.0 | `.dwg` 図面、R13～2018 の形式バージョン | `.xlsx`（Entities、Summary、Layers、Blocks）、`.csv`、`.jsonl`、`.dxf`、`.svg`、`report.json` | デスクトップアプリ + `dwg2excel.exe` CLI |
| **DDC Data Viewer** | 2.0 | `.xlsx`、`.csv`、`.jsonl`、`.parquet` テーブル + `.glb` / `.dae` ジオメトリ | フィルター済みビューの XLSX / CSV 出力 | デスクトップアプリ（無料） |

RVT Converter が書き出すすべてのジオメトリノードはネイティブの要素 ID を保持するため、表と 3D を
`ElementId` で結合できます。すべてのパッケージは Windows 10/11 x64 で完全オフラインで動作し、Excel も
Python のインストールも不要です。Linux と macOS のコマンドライン版は [v2026.10.1 リリース](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1)にあります。

<a id="screenshots"></a>
## スクリーンショット

以下のスクリーンショットはすべて、現行リリースのパッケージを実際に実行して取得したものです。オープンな
Revit サンプルモデル（MIT ライセンス）、ビューアー用の合成サンプル建物、および [`Sample_Projects/`](Sample_Projects/) のオープンな IFC サンプルを使用しています。

| | |
|---|---|
| ![RVT Converter 2.0.2：2 つの Revit モデルの変換完了画面](docs/images/rvt-converter-done.png) | ![RVT to IFC 2.0.2：IFC オプションパネル](docs/images/rvt-to-ifc-options.png) |
| **DDC RVT Converter** — 2 つの Revit モデルを変換。結果フォルダーがファイルごとに一覧表示されます。 | **DDC RVT to IFC** — 長さの単位、座標原点などの IFC 設定は *More options* にあります。 |
| ![Data Viewer：表の行と連動する 3D 選択](docs/images/data-viewer-3d-selection.png) | ![Data Viewer で表示した IFC to Excel の出力（IFC クラス別にグループ化）](docs/images/ifc-to-excel-table.png) |
| **DDC Data Viewer** — *Structural Columns* でフィルターすると、連動する要素が 3D でハイライトされます。サマリーパネルは面積、体積、長さを合計します。 | **DDC IFC to Excel** — オープンな Duplex IFC サンプルの `drawing.xlsx`。IFC クラス別にグループ化（333 オブジェクト、23 クラス）。 |
| ![RVTconverter のコマンドライン実行](docs/images/cli-rvt-ifc.png) | ![ダークテーマの Data Viewer](docs/images/data-viewer-dark.png) |
| **コマンドライン** — `RVTconverter.exe` は GLB、IFC4、要素テーブル、レポートを書き出し、ステータスの概要を表示します。 | **ダークテーマ** — ダークテーマの Data Viewer。右上に表示言語の切り替えがあります。 |

<a id="quick-start"></a>
## クイックスタート

1. [2.0.2 リリース](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2)（RVT Converter、RVT to IFC）または [Releases ページ](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases)（その他のパッケージ）を開き、
   必要なパッケージをダウンロードします。`*-Setup.exe`（ユーザー単位のインストーラー）または `*-portable.zip` です。
2. 同じリリースの `SHA256SUMS.txt` でダウンロードを検証します。
   ```powershell
   Get-FileHash .\DDC-RVT-Converter-*-portable.zip -Algorithm SHA256
   ```
3. ポータブルパッケージを任意のフォルダー（例：`C:\DDC\RVT-Converter\`、
   `C:\DDC\IFC-to-Excel\`、`C:\DDC\DWG-to-Excel\`）に展開します。フォルダー構成は変更しないでください。
4. デスクトップアプリ（`RVT Converter.exe`、`IFC to Excel.exe`、`DWG to Excel.exe`）を起動し、ファイルまたは
   フォルダーをウィンドウにドロップして *Convert* を押します。または下記のコマンドラインを使用します。
5. 結果を Excel、Python/pandas、または [DDC Data Viewer](#ddc-data-viewer) で開きます。

新しくダウンロードしたファイルの初回起動時に Windows SmartScreen が確認を求めることがあります。リリースに記載の SHA-256 値を確認してください。

<a id="command-line"></a>
## コマンドライン

以下の例は、現行リリースのバイナリで実行したものです。パスは、ポータブルパッケージを
`C:\DDC\` に展開した前提です。

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

| 出力 | 条件 | 内容 |
|---|---|---|
| `native_graph.glb` | 常時 | 3D メッシュ。要素ごとに 1 ノードで、ElementId を名前に使用 |
| `summary.json`, `report.json` | 常時 | ステータス、件数、省略された項目、要素ごとの診断情報 |
| `properties.jsonl`, `property_scopes.jsonl` (+ manifests) | `--properties` | 要素ごとの保存済みパラメーター（1 行に 1 つの JSON オブジェクト） |
| `native_graph.ifc`, `ifc.manifest.json`, `ifc.settings.json` | `--ifc` | IFC4（テッセレーションされたジオメトリ、プロパティセットと数量セット） |
| `native_graph.gltf` + `.bin`, `native_graph.obj` + `.mtl` | `--gltf`, `--obj` | GLB と同じジオメトリ。OBJ はメートル単位、Y-up |

終了コード：`0` は報告された欠落なしで書き出し済み、`2` は報告された欠落ありで書き出し済み（または引数が不正）、
`1` は変換または I/O の失敗です。すべての IFC オプション
（`--ifc-config`、`--ifc-phase`、`--ifc-design-options`、`--ifc-exclude-categories`、…）は `RVTconverter.exe --help` で確認できます。

### DDC IFC to Excel

ポータブルパッケージのコマンドライン：

```powershell
C:\DDC\IFC-to-Excel\runtime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py `
    "C:\Models\Building.ifc" --output "C:\Out\Building"
```

このコマンドは 1 行の JSON（`"status": "CONVERTED"`、`"CONVERTED_WITH_LIMITS"`、`"FAILED"` のいずれか）を出力し、
`drawing.xlsx`、`data.jsonl`、`data.sqlite`、`result.json` を含む新しいサブフォルダーを作成します。
`.ifczip` ファイルはそのまま受け付けます。

### DDC CAD Drawing to Excel — `dwg2excel.exe`

```powershell
# one or more drawings; a new sub-folder per drawing
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"

# a whole folder: tables only, one JSON line per file for scripts
$dwg = (Get-ChildItem C:\Drawings -Filter *.dwg).FullName
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe @dwg -o C:\Out --no-dxf --no-svg --json
```

各図面のフォルダーには `<name>.xlsx`、`<name>.csv`、`<name>.jsonl`、`<name>.dxf`、`<name>.svg`、
`report.json`、`REPORT.txt` が含まれます。コンソールの出力行には、デコードされたレコード、スキップされたレコード、
未対応の種類のレコードの数が表示されます。その他のオプション：`--timeout`、`--memory-limit-mb`、
`--language en|ru`、`--version`。

<a id="batch-processing-and-automation"></a>
## バッチ処理と自動化

**PowerShell — フォルダーツリー内のすべての RVT ファイル：**

```powershell
$exe = "C:\DDC\RVT-Converter\cli\RVTconverter.exe"
Get-ChildItem "C:\Projects" -Recurse -Include *.rvt | ForEach-Object {
    & $exe $_.FullName -o (Join-Path "C:\Out" $_.BaseName) --properties --ifc
    "{0}: exit {1}" -f $_.Name, $LASTEXITCODE
}
```

**Python — pandas で RVT のプロパティと IFC のテーブルを読み込む：**

```python
import json, subprocess, pandas as pd

subprocess.run([r"C:\DDC\RVT-Converter\cli\RVTconverter.exe", r"C:\Models\Project.rvt",
                "-o", r"C:\Out\Project", "--properties"], check=False)
rows = [json.loads(line) for line in open(r"C:\Out\Project\properties.jsonl", encoding="utf-8")]
print(len(rows), "property records")

objects = pd.read_excel(r"C:\Out\Building\Building-<id>\drawing.xlsx", sheet_name="Objects")
print(objects.groupby("Category").size().sort_values(ascending=False))
```

**CI やボットでの DWG：** `dwg2excel.exe --json` は図面ごとに 1 行の JSON を出力します。これを解析して、
ステータス、出力フォルダー、デコード統計を収集できます。

<a id="ddc-data-viewer"></a>
## DDC Data Viewer

コンバーターの出力用の無料デスクトップビューアーです。10 万行以上に対応する仮想化グリッド、検索、フィルター、
合計付きグループ化、列の選択、現在のビューの XLSX/CSV 出力、行と要素を双方向に連動させる 3D パネル
（GLB または DAE）を備えます。英語、ドイツ語、ロシア語に対応し、ライトテーマとダークテーマがあります。
リリースから `DDC-Data-Viewer-<version>-Setup.exe` またはポータブル zip をダウンロードしてください。

<a id="free-tools-data-check-quantity-take-off-power-bi-and-excel"></a>
## 無料ツール：データチェック、モデル差分、BCF 課題、数量拾い出し、Power BI と Excel

[`ddc-tools/`](ddc-tools/)（Python 3.9+、MIT、オフライン）は、コンバーターが書き出すテーブル
（XLSX、CSV、JSONL、SQLite、JSON）を対象に動作します。

- `ddc check` は、出力を YAML ルール（必須パラメーター、正規表現、一意性、範囲、
  許容値）に照らして検証し、ElementId / GlobalId の詳細を含む信号機形式の XLSX、JSON レポート、
  CI 用の終了コードを出力します。
- `ddc diff` は、モデルの 2 つの出力（RVT、IFC、DWG コンバーターの出力）を比較します。追加 / 削除 / 変更された要素、
  プロパティと数量ごとの旧値から新値、変更履歴 XLSX、JSON、変更状態で色分けした GLB、CI 用の終了コードを出力します。
- `ddc bcf` は、`ddc check` と `ddc diff` の結果を BCF 2.1 / 3.0 の課題ファイル（IFC GlobalId によるコンポーネント）として書き出し、
  任意の BCF ファイルを XLSX に表形式で出力します。BCF は buildingSMART のオープンな形式であり、認証を受けているとは主張しません。
- `ddc qto` は、数量、長さ、面積、体積をカテゴリー、タイプ、レベル別に集計して整形済みの XLSX に出力し、
  欠落またはゼロの数量について警告します。
- [`ddc-tools/powerbi/`](ddc-tools/powerbi/) と [`ddc-tools/excel/`](ddc-tools/excel/)：出力フォルダー全体を読み込む
  Power Query スクリプトと Excel ブック。Python は不要です
  （[手順](ddc-tools/docs/POWER_QUERY.md)）。

```bash
pip install ./ddc-tools
ddc check Project.converted --rules ddc-tools/examples/rules_basic.yaml --xlsx check.xlsx
ddc qto Project.converted --xlsx qto.xlsx
ddc diff Model_v1.converted Model_v2.converted --xlsx changes.xlsx --glb diff.glb --bcf changes.bcf
```

Excel と Power BI は Microsoft Corporation の商標であり、ファイルがどのソフトウェアと連携するかを示す目的でのみ使用しています。

<a id="n8n-workflows-notebooks-and-ai-agents"></a>
## n8n ワークフロー、ノートブック、AI エージェント

- [`DDC_n8n_Workflows&Pipelines/`](DDC_n8n_Workflows&Pipelines/) — 9 つの n8n ワークフロー（変換、
  バッチ検証、AI 分類、コストと CO2 の見積もり、QTO レポート）。
- [`DDC_in_additon/DDC_python_pipelines/`](DDC_in_additon/DDC_python_pipelines/) — 変換、
  バッチ処理、分析用の Jupyter ノートブック。

> **セットアップ：** ワークフローとノートブックは、`ddc convert` /
> `ddc table`（無料ツール [`ddc-tools/`](ddc-tools/)）を通じて [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) のコンバーターを呼び出します。これにより、`properties.jsonl` / IFC / DWG の出力から
> フラットなテーブル（`<name>_rvt.xlsx`、シート `Project_Data`：
> `ID`、`Category`、`Type Name`、`Level`、`Volume`、...）が作成されます。3D ジオメトリは GLB です。
> 初回セットアップ：`pip install ddc-tools\`。ワークフローとノートブックの隣にある `README.md` に、確認した内容と
> 対象外の内容が記載されています（例：n8n 5～7 の AI ステップにはご自身の認証情報が必要です。スケジュールとシート PDF に
> 相当する機能はありません。Revit の数量は IFC の数量または GLB メッシュから取得します）。

- [`AI_AGENTS_INSTRUCTIONS/`](AI_AGENTS_INSTRUCTIONS/) — コーディングエージェント
  （AI コーディングエージェント）向けの、最新のコマンドラインを記載した即利用可能なコンテキスト。リポジトリを
  エージェントで開き、たとえば *"convert every .rvt in C:\Projects to IFC and summarise the reports"* と依頼してください。
- [DDC Skills for AI agents](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
  — 建設データ向けの、すぐに使える自動化。

<a id="supported-scope-and-notes"></a>
## 対応範囲と注意事項

- **RVT：** テクスチャは出力されません。IFC 出力はテッセレーションされた IFC4 を書き出します。表現できない
  要素は実行レポートに一覧表示されます。
- **IFC：** IFC2x3 と IFC4 の STEP ファイル、および `.ifczip`。IFCXML は未対応です。元のレコードは常に
  `data.jsonl` / `data.sqlite` に残ります。
- **DWG：** R13～2018 の図面。一部のオブジェクト種別（たとえば特定の表、マルチ引出線、3D ソリッド、
  画像）は、誤って出力される代わりに `report.json` で *unsupported* として一覧表示されます。
- **プラットフォーム：** Windows 10/11 x64。**Linux（x64、arm64）と macOS（arm64、x64）：コマンドラインコンバーターと Data Viewer。[Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1) を参照してください。**

小さなサンプルファイル付きの不具合報告を歓迎します。
[GitHub Issues](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues) をご利用ください。
機密性のあるモデルは添付しないでください。

<a id="repository-layout"></a>
## リポジトリ構成

| パス | 内容 |
|---|---|
| `docs/` | リリースノート、スクリーンショット |
| `ddc-tools/` | 無料のデータチェック、モデル差分、BCF 課題、数量拾い出し、Power BI と Excel キット |
| `DDC_n8n_Workflows&Pipelines/` | n8n ワークフローの JSON ファイル |
| `DDC_in_additon/` | ノートブック、プレゼンテーション、画像 |
| `AI_AGENTS_INSTRUCTIONS/` | AI コーディングエージェント向けの指示 |
| `DDC_WINDOWS_Converters/` | ポータブル版 Windows コンバーター（RVT、RVT-to-IFC、IFC to Excel、CAD Drawing to Excel、Data Viewer）、ライセンス文書、Excel → Revit アドインのドキュメント。インストーラーは Releases ページにあります |
| `DDC_LINUX_Converters/` | CWICR データパッケージ、Qdrant パッケージング、テレメトリダッシュボード |
| `Sample_Projects/` | オープンな IFC サンプルファイル |

<a id="licensing"></a>
## ライセンス

- **ワークフロー、ノートブック、スクリプト、AI 向け指示、ドキュメント、`ddc-tools`** — [MIT License](LICENSE)。
  オープンソースで、商用利用も可能です。
- **DDC コンバーター**（Releases および `DDC_WINDOWS_Converters/` / `DDC_LINUX_Converters/` のバイナリパッケージ）—
  プロプライエタリソフトウェアで、**非商用利用に限り無料**です。**商用利用にはご依頼に応じたライセンスが必要です：**
  [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io)。条項：[EULA](EULA.md)、
  [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY)、[NOTICE](NOTICE)。サードパーティのオープンソースコンポーネント
  とそのライセンスは、各パッケージ内の `licenses/` に記載されています。
- `ddc-tools` の MIT ライセンスは、それが呼び出すコンバーターには及びません。

**商用利用**とは、企業、会社、自営の専門家、公的機関、その他の組織による（その従業員や請負業者を含む）、
またはそれらのための利用；有償の業務やサービスでの利用（顧客のファイルの処理を含む）；収益を生む、または生む意図のある
プロジェクトでの利用；他者に提供される製品、サービス、パイプライン、SaaS の内部での利用を指します。
再配布、OEM、SaaS への統合も含まれます。
**非商用利用**とは、個人の学習や趣味での利用、学術研究、学生と教員による教育と学習、
非営利団体による評価を指し、いずれも対価、収益、事業目的を伴わないものです。

セキュリティ報告：[SECURITY.md](SECURITY.md) を参照してください。特許、商標、輸出管理：
[PATENTS.md](PATENTS.md)、[TRADEMARK.md](TRADEMARK.md)、[EXPORT-COMPLIANCE.md](EXPORT-COMPLIANCE.md)。

<a id="consulting-and-training"></a>
## コンサルティングとトレーニング

DataDrivenConstruction は、建設、エンジニアリング、テクノロジー分野の企業が CAD/BIM データ処理を自動化し、
オープンな ETL パイプラインを構築するのを支援します。実データに基づくワークショップ、コンサルティング、プロトタイプを提供します。
ご連絡は [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io) まで、または
[datadrivenconstruction.io](https://datadrivenconstruction.io) をご覧ください。

<p>
  <a href="https://x.com/datadrivenconst"><img src="https://img.shields.io/twitter/follow/datadrivenconst?logo=X&style=flat&color=%23f5f5f5" alt="X でフォロー"></a>
  <a href="https://www.youtube.com/@datadrivenconstruction"><img src="https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://www.linkedin.com/company/78381569"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?logoColor=white" alt="LinkedIn"></a>
</p>

これらのツールがお役に立てば、リポジトリにスターを付けて、新しいリリースの通知を受け取ってください。

<a id="trademarks"></a>
## 商標

Autodesk および Revit は Autodesk, Inc. の商標です。DataDrivenConstruction は独立したソフトウェアであり、Autodesk, Inc. と提携しておらず、同社の推奨も受けていません。RVT、RFA、DWG、DXF、IFC は、どのファイルを読み込むかを示す目的でのみ使用しているファイル形式名です。
