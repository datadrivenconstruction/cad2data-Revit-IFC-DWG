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

<p align="center"><sub>GitHub が遅い、またはアクセスできない場合は、ミラーをご利用ください：<a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a>（同一ファイル、同一の SHA-256 値）。</sub></p>

# cad2data — RVT・IFC・DWG ファイル用 DDC コンバーター

Autodesk®、Revit®、AutoCAD® は Autodesk, Inc. の登録商標または商標です。IFC および buildingSMART® は buildingSMART International Ltd. の商標です。ファイル形式名（RVT、RFA、DWG、DXF）は形式を識別する目的でのみ使用しています。DataDrivenConstruction は Autodesk, Inc. と提携しておらず、同社の推奨・後援・認証を受けていません。

> これは日本語のクイックスタートです。詳細なドキュメントとリリースノートは[英語版](README.md)をご覧ください。ボタンやコマンドの名称は画面表示のままです。

**CAD/BIM ファイルを、オープンで構造化されたデータに — ローカルで、オフラインで、CAD ライセンス不要。**

| コンバーター | 入力 | 出力 |
|---|---|---|
| DDC RVT Converter | `.rvt`, `.rfa`（Revit 2019～2027） | GLB, glTF, OBJ, IFC4, JSONL / CSV / SQLite テーブル |
| DDC RVT to IFC | `.rvt`, `.rfa` | プロパティセット、数量、分類、材料を含む IFC4 |
| DDC IFC to Excel | `.ifc`, `.ifczip`（IFC2x3 / IFC4） | `drawing.xlsx`, `data.jsonl`, `data.sqlite` |
| DDC CAD Drawing to Excel | `.dwg`（R13～2018） | `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg` |
| DDC Data Viewer | `.xlsx`, `.csv`, `.jsonl`, `.parquet` + `.glb` | 3D モデルと連動するフィルター可能な表 |

## クイックスタート

1. [最新リリース](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest)を開き、必要なパッケージをダウンロードします。
   `*-Setup.exe`（ユーザー単位のインストーラー、管理者権限不要）または `*-portable.zip` です。
   GitHub が遅い場合・つながらない場合は[ミラー](https://cadbimconverter.com/download/)からダウンロードできます。
2. 同じリリースの `SHA256SUMS.txt` でダウンロードを検証します。
   ```powershell
   Get-FileHash .\DDC-RVT-Converter-*-portable.zip -Algorithm SHA256
   ```
3. ポータブル版を任意のフォルダー（例：`C:\DDC\RVT-Converter\`）に展開します。フォルダー構成は変更しないでください。
   日本語、スペース、`&` を含むパス（例：`C:\案件\東京 ビル & 設備\`）も使用できます。
4. アプリ（`RVT Converter.exe`、`IFC to Excel.exe`、`DWG to Excel.exe`）を起動し、ファイルまたはフォルダーをウィンドウにドロップして
   *Convert* を押します。コマンドラインでも実行できます（下記）。
5. 結果を Excel、Python/pandas、または DDC Data Viewer で開きます。

パッケージはまだコード署名されていないため、初回起動時に Windows SmartScreen が確認を求めることがあります。
動作環境：Windows 10/11 x64。Linux / macOS は近日対応予定。完全オフラインで動作し、Autodesk 製品・Excel・Python は不要です。

## コマンドライン

```powershell
# 入力ファイルの隣の「Project.converted」に GLB とレポートを出力
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt"

# 出力先を指定し、保存済みプロパティ（JSONL）と IFC4 も出力
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --properties --ifc

# IFC を Excel へ
C:\DDC\IFC-to-Excel\runtime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out\Building"

# DWG 図面
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"
```

RVT Converter の終了コード：`0` 正常、`2` 一部欠落を報告して出力（または引数エラー）、`1` 失敗。すべてのオプション：`RVTconverter.exe --help`。

## 無料ツール（ddc-tools、Python 3.9 以上、MIT）

```powershell
pip install ./ddc-tools
ddc table Project.converted --xlsx table.xlsx --csv table.csv --delimiter semicolon
```

- `--csv` は BOM 付き UTF-8 で書き出します（Excel で日本語・中国語・キリル文字・アラビア文字が正しく表示されます）。数値の小数点は常に `.` です。
- `--delimiter semicolon`（または `auto`）で、小数点にカンマを使うロケール向けのセミコロン区切り CSV を出力します。
- `--unit-headers` で見出しに単位を付けます：`Area [m2]`、`Volume [m3]`。
- `ddc classify` — 分類コード列（Uniclass、OmniClass、MasterFormat、DIN 276、GESN/KSR、GB/T 51269、NL-SfB、CCI）：[ドキュメント](ddc-tools/docs/CLASSIFICATION.md)。

## ライセンス

ワークフロー、ノートブック、スクリプト、ドキュメント：[MIT](LICENSE)。コンバーターのパッケージ：各パッケージ同梱の EULA（`EULA.txt`）に基づき、
個人・商用ともに無料。[LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) と [NOTICE](NOTICE) も参照してください。
セキュリティ：[SECURITY.md](SECURITY.md)。商標：[TRADEMARK.md](TRADEMARK.md)。

お問い合わせ・トレーニング：[info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io) · [datadrivenconstruction.io](https://datadrivenconstruction.io)。
不具合報告（機密モデルは添付しないでください）：[GitHub Issues](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues)。
