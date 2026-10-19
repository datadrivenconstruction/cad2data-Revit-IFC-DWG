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

## الجديد في أكتوبر 2026

أصبحت المحولات تعتمد على **قارئات صيغ خاصة بشركة DataDrivenConstruction** ‏(RVT: ‏Rust؛ IFC وDWG: ‏Python) ولم تعد تعتمد على أي SDK خارجي لبرامج CAD. أُوقفت برامج الجيل 18.x ‏(`RvtExporter.exe` و`IfcExporter.exe` و`DwgExporter.exe` و`DgnExporter.exe` و`RVT2IFCconverter.exe`) وأزيلت من المستودع، وتُنشر الحزم الجديدة في [صفحة الإصدارات](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases). صيغة DGN غير مدعومة حاليًا. جميع المحولات الجديدة إصدارات تجريبية، ويكتب كل تشغيل تقريرًا بما قُرئ أو تُخطّي أو رُفض.

## المحولات

| الحزمة | الإصدار | المدخلات | المخرجات |
|---|---|---|---|
| **DDC RVT Converter** | 0.6.8 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV |
| **DDC RVT to IFC** | 0.6.8 | `.rvt`, `.rfa` | IFC4 |
| **DDC IFC to Excel** | 0.3.1 preview | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC DWG to Excel** | 0.4.1 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 0.1.2 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

تعمل جميع الحزم دون اتصال على Windows 10/11 x64 ولا تحتاج إلى برامج Autodesk أو Excel أو Python.

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

نُقلت مسارات n8n ‏(`DDC_n8n_Workflows&Pipelines/`) ودفاتر Jupyter إلى المحولات الجديدة: فهي تستدعي المحولات عبر `ddc convert` / `ddc table` (الأداة المجانية [`ddc-tools/`](ddc-tools/)) التي تبني من مخرجات المحولات الجدول المسطح بالتخطيط القديم (`*_rvt.xlsx`، ورقة `Project_Data`)، واستُبدل DAE بـ GLB. التثبيت لمرة واحدة: `pip install ddc-tools\`. ما جرى التحقق منه وما لا يغطيه النقل مذكور في `README.md` بجوار المسارات والدفاتر. يصف `AI_AGENTS_INSTRUCTIONS/` الأوامر الجديدة.

## القيود

RVT: اكتمال الهندسة غير معتمد، لا تُصدَّر الخامات، وIFC4 بهندسة مثلثية. IFC: لا يدعم IFCXML. DWG: يُبلَّغ عن بعض أنواع الكائنات كغير مدعومة بدلًا من تصديرها بشكل خاطئ — راجع `report.json`. حاليًا Windows x64 فقط؛ Linux / macOS قريبًا (coming soon).

## الترخيص

سير العمل والدفاتر والسكربتات والوثائق: [MIT](LICENSE). حزم المحولات: مجانية للاستخدام الشخصي والتجاري وفق اتفاقية EULA المرفقة من DataDrivenConstruction؛ راجع [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) و[NOTICE](NOTICE).

## العلامات التجارية

Autodesk® وRevit® وAutoCAD® علامات تجارية مسجلة لشركة Autodesk, Inc. ‏IFC وbuildingSMART® علامتان تجاريتان لـ buildingSMART International Ltd. تُستخدم أسماء الصيغ (RVT وRFA وDWG وDXF وDGN) لتعريف صيغ الملفات فقط. لا ترتبط DataDrivenConstruction بشركة Autodesk, Inc. ولا تحظى بتأييدها أو اعتمادها. النص الكامل في [README.md](README.md#trademarks).

</div>
