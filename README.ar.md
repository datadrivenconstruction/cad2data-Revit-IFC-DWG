<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ar.md">العربية</a>
</p>

<div dir="rtl">

# cad2data — محولات DDC لملفات RVT وIFC وDWG

**حوّل ملفات CAD/BIM إلى بيانات مفتوحة ومنظمة محليًا ودون اتصال وبدون تراخيص CAD.**

<p align="center"><img src="docs/images/data-viewer-3d-grouped.png" width="100%" alt="DDC Data Viewer"></p>

## الجديد في DDC Converters 2.0

إصدار أكتوبر 2026 لخط المنتجات بالكامل: RVT Converter 2.0 وRVT to IFC 2.0 وIFC to Excel 2.0 وCAD Drawing to Excel 2.0 وData Viewer 2.0 وExcel Add-in 2.0.

- **أداة واحدة لكل عائلة صيغ.** تحويل `.rvt` / `.rfa` إلى GLB وglTF وOBJ وIFC4 وجداول JSONL / CSV / SQLite؛ و`.ifc` / `.ifczip` إلى Excel وJSONL وSQLite؛ و`.dwg` إلى Excel وCSV وJSONL وDXF وSVG.
- **ملفات Revit 2019–2027** تُقرأ مباشرة دون برامج Autodesk ودون تراخيص CAD.
- **تصدير IFC4 من Revit** مع مجموعات الخصائص والكميات والتصنيف والمواد، وبالملفات الشخصية `full` و`coordination` و`geometry`؛ والوحدات ونقطة الأصل والفئات والمراحل عبر سطر الأوامر.
- **معرّفات العناصر في كل مكان.** تحتفظ كل عقدة هندسية بمعرّف العنصر الأصلي، فتُربط الجداول والنموذج ثلاثي الأبعاد عبر `ElementId`.
- **تقرير لكل تشغيل.** يسرد `report.json` / `summary.json` بالأعداد ما قُرئ وما تُخطّي.
- **تطبيقات سطح المكتب وسطر الأوامر** لكل محول، مع رموز خروج مناسبة للمعالجة الدفعية وحالة JSON في سطر واحد للسكربتات.
- **DDC Data Viewer 2.0:** عارض مجاني للجداول والنموذج ثلاثي الأبعاد مع ربط ثنائي الاتجاه بين الصفوف والعناصر.
- **دون اتصال ومحمول.** Windows 10/11 x64؛ لا حاجة لتثبيت أي شيء سوى الحزمة (مثبّت أو zip محمول). إصدارات Linux / macOS قريبًا (coming soon).

التنزيل: [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (محمولة وجاهزة للتشغيل) و[صفحة الإصدارات](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (المثبّتات والحزم).

## المحولات

| الحزمة | الإصدار | المدخلات | المخرجات |
|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV / SQLite |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4 (مجموعات الخصائص والكميات والتصنيف والمواد) |
| **DDC IFC to Excel** | 2.0 | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC CAD Drawing to Excel** | 2.0 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 2.0 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

تحتفظ كل عقدة هندسية يكتبها RVT Converter بمعرّف العنصر الأصلي، فتُربط الجداول والنموذج ثلاثي الأبعاد عبر `ElementId`. تعمل جميع الحزم دون اتصال على Windows 10/11 x64 ولا تحتاج إلى برامج Autodesk أو Excel أو Python. إصدارات Linux / macOS قريبًا (coming soon).

## لقطات الشاشة

تشغيلات حقيقية للحزم الحالية على المبنى التجريبي الاصطناعي للعارض وعلى مثال IFC المفتوح في `Sample_Projects/`.

| | |
|---|---|
| ![](docs/images/data-viewer-3d-selection.png) | ![](docs/images/ifc-to-excel-table.png) |
| ![](docs/images/cli-rvt-ifc.png) | ![](docs/images/data-viewer-dark-ru.png) |

## البدء السريع

1. نزّل الحزمة من [أحدث إصدار](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest) ‏(`*-Setup.exe` أو `*-portable.zip`) وتحقق منها باستخدام `SHA256SUMS.txt`.
2. فك ضغط الحزمة المحمولة، مثلًا في `C:\DDC\`.
3. شغّل التطبيق أو استخدم سطر الأوامر:

</div>

```powershell
# RVT / RFA -> GLB + IFC4 + properties (JSONL)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --properties --ifc

# IFC / IFCZIP -> Excel + JSONL + SQLite
C:\DDC\IFC-to-Exceluntime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out\Building"

# DWG -> Excel + CSV + JSONL + DXF + SVG
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"
```

<div dir="rtl">

جميع الخيارات وملفات المخرجات ورموز الخروج في [README الإنجليزي](README.md#command-line).

## سير عمل n8n والدفاتر ووكلاء الذكاء الاصطناعي

تستدعي مسارات n8n ‏(`DDC_n8n_Workflows&Pipelines/`) ودفاتر Jupyter المحولات عبر `ddc convert` / `ddc table` (الأداة المجانية [`ddc-tools/`](ddc-tools/)) التي تبني من مخرجات المحولات الجدول المسطح (`*_rvt.xlsx`، ورقة `Project_Data`)؛ والهندسة ثلاثية الأبعاد بصيغة GLB. التثبيت لمرة واحدة: `pip install ddc-tools\`. ما جرى التحقق منه وما لا يغطيه مذكور في `README.md` بجوار المسارات والدفاتر. يتضمن `AI_AGENTS_INSTRUCTIONS/` السياق مع أوامر سطر الأوامر الحالية.

## النطاق المدعوم وملاحظات

- **RVT:** لا تُصدَّر الخامات؛ ويكتب تصدير IFC ملف IFC4 بهندسة مثلثية. العناصر التي يتعذر تمثيلها مدرجة في تقرير التشغيل.
- **IFC:** ملفات IFC2x3 وIFC4 STEP و`.ifczip`؛ ولا يُدعم IFCXML. تبقى السجلات الأصلية دائمًا في `data.jsonl` / `data.sqlite`.
- **DWG:** رسومات R13–2018. تُدرج بعض أنواع الكائنات (مثل بعض الجداول والخطوط الإرشادية المتعددة والأجسام ثلاثية الأبعاد والصور) في `report.json` على أنها *غير مدعومة* بدلًا من تصديرها بشكل خاطئ.
- **المنصات:** Windows 10/11 x64. **Linux / macOS قريبًا (coming soon).**

## الترخيص

سير العمل والدفاتر والسكربتات والوثائق: [MIT](LICENSE). حزم المحولات: مجانية للاستخدام الشخصي والتجاري وفق اتفاقية EULA المرفقة من DataDrivenConstruction؛ راجع [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) و[NOTICE](NOTICE).

## العلامات التجارية

Autodesk® وRevit® وAutoCAD® علامات تجارية مسجلة لشركة Autodesk, Inc. ‏IFC وbuildingSMART® علامتان تجاريتان لـ buildingSMART International Ltd. تُستخدم أسماء الصيغ (RVT وRFA وDWG وDXF وDGN) لتعريف صيغ الملفات فقط. لا ترتبط DataDrivenConstruction بشركة Autodesk, Inc. ولا تحظى بتأييدها أو اعتمادها. النص الكامل في [README.md](README.md#trademarks).

</div>
