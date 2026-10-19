<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ar.md">العربية</a>
</p>

# cad2data — конвертеры DDC для файлов RVT, IFC и DWG

**Превращайте CAD/BIM-файлы в открытые структурированные данные — локально, офлайн и без CAD-лицензий.**

<p align="center"><img src="docs/images/data-viewer-3d-grouped.png" width="100%" alt="DDC Data Viewer"></p>

## Что изменилось в октябре 2026

Конвертеры переведены на **собственные читатели форматов DataDrivenConstruction** (RVT — Rust, IFC и DWG — Python) и больше не зависят от сторонних CAD-SDK. Старые программы поколения 18.x (`RvtExporter.exe`, `IfcExporter.exe`, `DwgExporter.exe`, `DgnExporter.exe`, `RVT2IFCconverter.exe`) сняты с поддержки и убраны из репозитория; новые пакеты публикуются на [странице релизов](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases). DGN пока не поддерживается. Все новые конвертеры — предварительные версии: каждый запуск пишет отчёт о том, что прочитано, пропущено или отклонено.

## Конвертеры

| Пакет | Версия | Читает | Пишет |
|---|---|---|---|
| **DDC RVT Converter** | 0.6.8 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV |
| **DDC RVT to IFC** | 0.6.8 | `.rvt`, `.rfa` | IFC4 |
| **DDC IFC to Excel** | 0.3.1 preview | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC DWG to Excel** | 0.4.1 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 0.1.1 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

Все пакеты работают офлайн в Windows 10/11 x64 и не требуют ПО Autodesk, Excel или Python. Каждый геометрический узел RVT Converter хранит исходный ElementId, поэтому таблицы и 3D связываются напрямую.

## Скриншоты

Реальные запуски текущих пакетов: синтетическое демо-здание просмотрщика и открытый IFC-пример из `Sample_Projects/`.

| | |
|---|---|
| ![](docs/images/data-viewer-3d-selection.png) | ![](docs/images/ifc-to-excel-table.png) |
| ![](docs/images/cli-rvt-ifc.png) | ![](docs/images/data-viewer-dark-ru.png) |

## Быстрый старт

1. Скачайте пакет из [последнего релиза](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest) (`*-Setup.exe` или `*-portable.zip`) и проверьте по `SHA256SUMS.txt`.
2. Распакуйте portable-пакет, например, в `C:\DDC\`.
3. Запустите приложение, перетащите файлы и нажмите «Конвертировать» — или используйте командную строку:

```powershell
# RVT / RFA -> GLB + IFC4 + properties (JSONL)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --properties --ifc

# IFC / IFCZIP -> Excel + JSONL + SQLite
C:\DDC\IFC-to-Exceluntime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out\Building"

# DWG -> Excel + CSV + JSONL + DXF + SVG
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"
```

Все параметры, выходные файлы и коды возврата — в [английском README](README.md#command-line).

## n8n-сценарии, ноутбуки и ИИ-агенты

n8n-сценарии (`DDC_n8n_Workflows&Pipelines/`) и Jupyter-ноутбуки написаны для старой командной строки 18.x (XLSX + DAE) и переносятся на новые конвертеры. До этого укажите путь к новому исполняемому файлу и поправьте шаг разбора (свойства RVT — `properties.jsonl`, геометрия — GLB). В `AI_AGENTS_INSTRUCTIONS/` уже описаны новые команды.

## Ограничения

RVT: полнота геометрии не сертифицирована, текстуры не экспортируются, IFC4 — тесселированный. IFC: IFCXML не поддерживается. DWG: часть типов объектов помечается как неподдерживаемые вместо неверного экспорта — проверяйте `report.json`. Пока только Windows x64.

## Лицензия

Сценарии, ноутбуки, скрипты и документация — [MIT](LICENSE). Пакеты конвертеров — бесплатно для частного и коммерческого использования по EULA DataDrivenConstruction, входящей в пакет; см. [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) и [NOTICE](NOTICE). Контакт: info@datadrivenconstruction.io

## Товарные знаки

Autodesk®, Revit® и AutoCAD® — зарегистрированные товарные знаки Autodesk, Inc. IFC и buildingSMART® — товарные знаки buildingSMART International Ltd. Названия форматов (RVT, RFA, DWG, DXF, DGN) используются только для обозначения форматов файлов. DataDrivenConstruction не связана с Autodesk, Inc. и не одобрена и не сертифицирована ею. Продукты DDC — независимое ПО для совместимости форматов; они не содержат и не используют ПО, SDK или исходный код Autodesk. Полный текст: [README.md](README.md#trademarks).
