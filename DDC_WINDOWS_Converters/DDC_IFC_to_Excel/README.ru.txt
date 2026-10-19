DDC IFC to Excel — локальный переносимый кандидат

Windows x64. Откройте IFC to Excel.exe, выберите IFC/IFCZIP и папку результата.
Python, Excel и CAD-библиотеки отдельно устанавливать не требуется.
Перемещайте всю папку приложения целиком; исходные файлы моделей не изменяются.

Community сохраняет все возможности. Каждые две принятые конвертации GUI
открывают локальную рекламную страницу, которую можно сразу закрыть.
Paid и аппаратная активация ещё не подключены к этому кандидату.

Это preview: геометрия, вычисленные свойства и полнота исходных данных не
квалифицированы. IFCXML не поддерживается. Чистая Windows пока не проверена.
Оригинальные записи остаются в JSONL/SQLite; длинные ячейки Excel вынесены
в отдельный файл. Сохраняйте всю папку результата, включая протокол и sidecar.

Кандидат только для локальной проверки. Перед внешним распространением
требуется завершить проверку прав на generated-данные стандартных IFC-схем.
Источники и уведомления: SOURCES.json, runtime/LICENSE.txt,
runtime/Lib/site-packages/*dist-info и sources/ifc-independent/schemas/official/NOTICE.txt.

0.2.5-preview: IFCZIP принимает только STORED/DEFLATED.
Подменённые размеры/CRC, незавершённые потоки DEFLATE и данные после
конца потока отклоняются. BZIP2/LZMA для IFC-моделей не поддерживаются.

0.2.6-preview: целые значения STEP REAL сохраняются точно, если binary64
теряет целые единицы. Дробные REAL и пересчёт единиц с коэффициентом,
отличным от 1, остаются binary64; полная десятичная точность не заявляется.

0.2.7-preview: GUI recovers from worker startup and execution failures; stale details are cleared, result actions require an accepted selection, and the file list scrolls. Conversion fidelity limits are unchanged.

0.2.8-preview: Exact REAL source text and bounded exact SI text are exported alongside compatible numeric values; own reader snapshot/ASCII controls and GUI lifecycle fixes included. Partial semantics only; full fidelity, clean-machine and installed VSTO qualification remain open.

0.2.9-preview: Direct Python row_limit is a strict built-in integer from 2 to 1048576; NaN, floats and booleans are refused before input/output work. Valid integer splitting and exact sidecars retain the reviewed028 behavior. Partial semantics only; full fidelity, clean-machine and installed VSTO qualification remain open.

0.3.0-preview: Approximate unit conversion is bounded to 32 unit nodes including SI; deeper or cyclic chains retain explicit unresolved diagnostics and raw source rows. Iterative nested-property traversal preserves source order, repeated/shared branches, cycle markers and following siblings without Python call-stack recursion. Authored1100-level source checks passed; arbitrary graph resource bounds are not qualified. Reviewed029 row-limit guards remain. Partial semantics only; full fidelity, clean-machine and installed VSTO qualification remain open.

Local candidate registration-20261006-03: current IFC source, registration dialog, Community/Paid accounting adapter and minimum-window layout. Registration is unconfigured by default. Production activation and clean Windows remain unqualified. This candidate does not modify installed applications.

Local candidate dimensions-20261007-02: source-typed conversion-unit dimensional exponents; malformed REAL/logical declarations remain unresolved instead of claiming normalized SI. Same 0.3.0-preview GUI/CLI, runtime, launcher and unconfigured registration. No production activation or clean Windows qualification. No installed product changes.

Local candidate aggregate-20261007-03: separate aggregate limit 999999 under unchanged total-record 1000000 value-node limit and positional 100000 limit; no discarded values or geometry/fidelity claim. Existing dimension and registration fixes retained. Same 0.3.0-preview GUI/CLI, runtime, launcher and unconfigured registration. No production activation or clean Windows qualification. No installed product changes.

0.3.1-preview / streaming-20261008-01: property candidates processed per owner, measure rows in bounded batches; explicit memory error and failure stage. Local QA candidate only. Full source fidelity, installed Excel and clean Windows remain unqualified. No production activation.
