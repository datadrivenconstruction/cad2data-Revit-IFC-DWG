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

## Что нового в DDC Converters 2.0

Октябрьский релиз 2026 года для всей линейки: RVT Converter 2.0, RVT to IFC 2.0, IFC to Excel 2.0, CAD Drawing to Excel 2.0, Data Viewer 2.0 и Excel Add-in 2.0.

- **Один инструмент на семейство форматов.** `.rvt` / `.rfa` в GLB, glTF, OBJ, IFC4 и таблицы JSONL / CSV / SQLite; `.ifc` / `.ifczip` в Excel, JSONL и SQLite; `.dwg` в Excel, CSV, JSONL, DXF и SVG.
- **Файлы Revit 2019–2027** читаются напрямую, без ПО Autodesk и без CAD-лицензий.
- **Экспорт IFC4 из Revit** с наборами свойств, количествами, классификацией и материалами, профили `full`, `coordination` и `geometry`; единицы, начало координат, категории и стадии задаются в командной строке.
- **Идентификаторы элементов везде.** Каждый геометрический узел хранит исходный ElementId, поэтому таблицы и 3D связываются по `ElementId`.
- **Отчёт для каждого запуска.** `report.json` / `summary.json` с числами показывают, что прочитано и что пропущено.
- **Приложения и командная строка** для каждого конвертера, коды возврата для пакетной обработки и однострочный JSON-статус для скриптов.
- **DDC Data Viewer 2.0:** бесплатный просмотрщик таблиц и 3D с двусторонней связью строк и элементов.
- **Офлайн и портативно.** Windows 10/11 x64; кроме пакета (установщик или portable zip) ничего ставить не нужно. Сборки для Linux / macOS — coming soon.

Загрузки: [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (portable, готовы к запуску) и [страница релизов](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (установщики и пакеты).

## Конвертеры

| Пакет | Версия | Читает | Пишет |
|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV / SQLite |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4 (наборы свойств, количества, классификация, материалы) |
| **DDC IFC to Excel** | 2.0 | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC CAD Drawing to Excel** | 2.0 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 2.0 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

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

n8n-сценарии (`DDC_n8n_Workflows&Pipelines/`) и Jupyter-ноутбуки вызывают конвертеры через `ddc convert` / `ddc table` (бесплатный инструмент [`ddc-tools/`](ddc-tools/)), который собирает из выхода конвертеров плоскую таблицу (`*_rvt.xlsx`, лист `Project_Data`); 3D-геометрия — GLB. Разовая установка: `pip install ddc-tools\`. Что проверено и что не покрыто, написано в `README.md` рядом со сценариями и ноутбуками. В `AI_AGENTS_INSTRUCTIONS/` собран контекст с актуальными командами.

## Поддерживаемый объём и примечания

- **RVT:** текстуры не экспортируются; экспорт IFC пишет тесселированный IFC4. Элементы, которые нельзя представить, перечислены в отчёте запуска.
- **IFC:** файлы IFC2x3 и IFC4 STEP и `.ifczip`; IFCXML не поддерживается. Исходные записи всегда остаются в `data.jsonl` / `data.sqlite`.
- **DWG:** чертежи R13–2018. Часть типов объектов (например, некоторые таблицы, мультивыноски, 3D-тела, изображения) помечается в `report.json` как *неподдерживаемые* вместо неверного экспорта.
- **Платформы:** Windows 10/11 x64. **Linux / macOS — coming soon.**

## Лицензия

Сценарии, ноутбуки, скрипты и документация — [MIT](LICENSE). Пакеты конвертеров — бесплатно для частного и коммерческого использования по EULA DataDrivenConstruction, входящей в пакет; см. [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) и [NOTICE](NOTICE). Контакт: info@datadrivenconstruction.io

## Товарные знаки

Autodesk®, Revit® и AutoCAD® — зарегистрированные товарные знаки Autodesk, Inc. IFC и buildingSMART® — товарные знаки buildingSMART International Ltd. Названия форматов (RVT, RFA, DWG, DXF, DGN) используются только для обозначения форматов файлов. DataDrivenConstruction не связана с Autodesk, Inc. и не одобрена и не сертифицирована ею. Продукты DDC — независимое ПО для совместимости форматов; они не содержат и не используют ПО, SDK или исходный код Autodesk. Полный текст: [README.md](README.md#trademarks).
