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

<p align="center"><sub>¿Descargas demasiado lentas o GitHub bloqueado? Use el espejo: <a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a> (mismos archivos, mismas sumas SHA-256).</sub></p>

<h1 align="center">cad2data — convertidores DDC para archivos RVT, IFC y DWG</h1>

<p align="center">
  <b>Convierta archivos CAD/BIM en datos abiertos y estructurados: en local, sin conexión y sin licencias CAD.</b><br>
  .rvt / .rfa → GLB · glTF · OBJ · IFC4 · JSONL/CSV &nbsp;|&nbsp; .ifc → Excel · JSONL · SQLite &nbsp;|&nbsp; .dwg → Excel · CSV · JSONL · DXF · SVG
</p>

<p align="center">
  <a href="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest"><img src="https://img.shields.io/github/v/release/datadrivenconstruction/cad2data-Revit-IFC-DWG?label=release" alt="Última versión"></a>
  <img src="https://img.shields.io/badge/input-.rvt%20.rfa%20.ifc%20.ifczip%20.dwg-blue" alt="Formatos de entrada">
  <img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.jsonl%20.glb%20.ifc%20.dxf%20.svg-green" alt="Formatos de salida">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Windows x64; Linux x64 y arm64; macOS arm64 y x64">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT%20(workflows%2C%20docs)%20%2B%20non-commercial%20EULA%20(converters)-blue" alt="Licencia"></a>
</p>

<p align="center">
  <img src="docs/images/data-viewer-3d-grouped.png" alt="DDC Data Viewer: tabla agrupada por categoría y nivel con el modelo 3D enlazado" width="100%">
</p>

---

<a id="whats-new-in-ddc-converters-20"></a>
## Novedades de DDC Converters 2.0

DDC Converters 2.0 es la versión de octubre de 2026 de toda la línea: RVT Converter 2.0, RVT to IFC 2.0,
IFC to Excel 2.0, CAD Drawing to Excel 2.0, Data Viewer 2.0 y Excel Add-in 2.0.
La compilación actual de RVT Converter y RVT to IFC es la [2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2).

- **Una herramienta por familia de formatos.** `.rvt` / `.rfa` a GLB, glTF, OBJ, IFC4 y tablas JSONL / CSV / SQLite;
  `.ifc` / `.ifczip` a Excel, JSONL y SQLite; `.dwg` a Excel, CSV, JSONL, DXF y SVG.
- **Los archivos de Revit 2016–2027** se leen directamente, sin necesidad de tener Revit instalado.
- **Exportación IFC4 desde Revit** con conjuntos de propiedades, cantidades, clasificación y materiales, y los perfiles
  `full`, `coordination` y `geometry`; opciones de unidades, origen, categorías y fases en la línea de comandos.
- **ID de elemento en todas partes.** Cada nodo de geometría conserva el ID nativo del elemento, de modo que tablas y 3D se unen por `ElementId`.
- **Un informe por cada ejecución.** `report.json` / `summary.json` indican, con recuentos, qué se leyó y qué se omitió.
- **Aplicaciones de escritorio y línea de comandos** para cada convertidor, códigos de salida aptos para lotes y estado JSON en una línea para scripts.
- **DDC Data Viewer 2.0:** visor gratuito de tablas y 3D con enlace bidireccional entre filas y elementos.
- **Sin conexión y portátil.** Windows 10/11 x64, sin nada que instalar aparte del paquete (instalador o zip portable).
  Los convertidores de línea de comandos y el Data Viewer para Linux (x64, arm64) y macOS (arm64, x64) están en [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1) (véase [DDC_LINUX_Converters](DDC_LINUX_Converters/README.md)).

Descargas: [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (portables, listos para usar) y la
[página de Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (instaladores y paquetes).

<a id="contents"></a>
## Contenido

- [Convertidores](#converters)
- [Capturas de pantalla](#screenshots)
- [Inicio rápido](#quick-start)
- [Línea de comandos](#command-line)
- [Procesamiento por lotes y automatización](#batch-processing-and-automation)
- [DDC Data Viewer](#ddc-data-viewer)
- [Herramientas gratuitas: comprobación de datos, mediciones de cantidades, Power BI y Excel](#free-tools-data-check-quantity-take-off-power-bi-and-excel)
- [Flujos de trabajo de n8n, notebooks y agentes de IA](#n8n-workflows-notebooks-and-ai-agents)
- [Alcance admitido y notas](#supported-scope-and-notes)
- [Estructura del repositorio](#repository-layout)
- [Licencias](#licensing)
- [Marcas registradas](#trademarks)

<a id="converters"></a>
## Convertidores

| Paquete | Versión | Lee | Escribe | Interfaz |
|---|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa` guardados con Revit 2016–2027 | GLB (por defecto), glTF, OBJ, IFC4, tabla de elementos (`elements.xlsx`, `elements.csv`: categoría, familia, tipo, nivel, área, volumen, longitud, parámetros), propiedades guardadas como JSONL; la aplicación de escritorio también escribe tablas CSV y SQLite | Aplicación de escritorio + CLI `RVTconverter.exe` |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4 con conjuntos de propiedades, cantidades, clasificación, materiales; perfiles `full`, `coordination`, `geometry` | Aplicación de escritorio (misma línea de comandos que RVT Converter) |
| **DDC IFC to Excel** | 2.0 | Archivos STEP IFC2x3 / IFC4, `.ifczip` | `drawing.xlsx` (objetos, propiedades, cantidades), `data.jsonl`, `data.sqlite`, `result.json` | Aplicación de escritorio + línea de comandos |
| **DDC CAD Drawing to Excel** | 2.0 | Dibujos `.dwg`, versiones de formato R13–2018 | `.xlsx` (Entities, Summary, Layers, Blocks), `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json` | Aplicación de escritorio + CLI `dwg2excel.exe` |
| **DDC Data Viewer** | 2.0 | Tablas `.xlsx`, `.csv`, `.jsonl`, `.parquet` + geometría `.glb` / `.dae` | vistas filtradas a XLSX / CSV | Aplicación de escritorio (gratuita) |

Cada nodo de geometría escrito por RVT Converter conserva el ID nativo del elemento, de modo que tablas y 3D pueden
unirse por `ElementId`. Todos los paquetes funcionan totalmente sin conexión en Windows 10/11 x64 y no necesitan Excel
ni una instalación de Python. Las compilaciones de línea de comandos para Linux y macOS están en la [release v2026.10.1](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1).

<a id="screenshots"></a>
## Capturas de pantalla

Todas las capturas siguientes proceden de ejecuciones reales de los paquetes de la versión actual. Utilizan modelos
de ejemplo abiertos de Revit (licencia MIT), el edificio de muestra sintético del visor y el ejemplo IFC abierto de [`Sample_Projects/`](Sample_Projects/).

| | |
|---|---|
| ![RVT Converter 2.0.2: conversión terminada de dos modelos de Revit](docs/images/rvt-converter-done.png) | ![RVT to IFC 2.0.2: panel de opciones de IFC](docs/images/rvt-to-ifc-options.png) |
| **DDC RVT Converter** — dos modelos de Revit convertidos; la carpeta de resultados se muestra por archivo. | **DDC RVT to IFC** — unidad de longitud, origen de coordenadas y el resto de ajustes de IFC en *More options*. |
| ![Data Viewer: selección 3D enlazada con filas de la tabla](docs/images/data-viewer-3d-selection.png) | ![Salida de IFC to Excel en el Data Viewer, agrupada por clase IFC](docs/images/ifc-to-excel-table.png) |
| **DDC Data Viewer** — un filtro sobre *Structural Columns* resalta en 3D los elementos enlazados; el panel de resumen suma área, volumen y longitud. | **DDC IFC to Excel** — `drawing.xlsx` del ejemplo IFC abierto Duplex, agrupado por clase IFC (333 objetos, 23 clases). |
| ![Ejecución de RVTconverter por línea de comandos](docs/images/cli-rvt-ifc.png) | ![Data Viewer en tema oscuro](docs/images/data-viewer-dark.png) |
| **Línea de comandos** — `RVTconverter.exe` escribe GLB, IFC4, la tabla de elementos y los informes, e imprime un resumen de estado. | **Tema oscuro** — el Data Viewer en tema oscuro, con el selector de idioma de la interfaz arriba a la derecha. |

<a id="quick-start"></a>
## Inicio rápido

1. Abra la [release 2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2) (RVT Converter, RVT to IFC) o la [página de Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (otros paquetes)
   y descargue el paquete que necesite: un `*-Setup.exe` (instalador por usuario) o un `*-portable.zip`.
2. Verifique la descarga con `SHA256SUMS.txt` de la misma release:
   ```powershell
   Get-FileHash .\DDC-RVT-Converter-*-portable.zip -Algorithm SHA256
   ```
3. Descomprima el paquete portable en una carpeta de su elección, por ejemplo `C:\DDC\RVT-Converter\`,
   `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`. Mantenga la estructura de carpetas tal como está.
4. Inicie la aplicación de escritorio (`RVT Converter.exe`, `IFC to Excel.exe`, `DWG to Excel.exe`), suelte archivos o
   carpetas en la ventana y pulse *Convert*, o use la línea de comandos que se describe a continuación.
5. Abra el resultado en Excel, Python/pandas o el [DDC Data Viewer](#ddc-data-viewer).

Windows SmartScreen puede pedir confirmación en el primer inicio de una descarga nueva; compruebe la suma SHA-256 de la release.

<a id="command-line"></a>
## Línea de comandos

Los ejemplos siguientes se ejecutaron con los binarios de la versión actual. Las rutas suponen que los paquetes
portables se descomprimieron en `C:\DDC\`.

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

| Salida | Cuándo | Contenido |
|---|---|---|
| `native_graph.glb` | siempre | mallas 3D, un nodo por elemento, nombrado por ElementId |
| `summary.json`, `report.json` | siempre | estado, recuentos, omisiones y diagnósticos por elemento |
| `properties.jsonl`, `property_scopes.jsonl` (+ manifiestos) | `--properties` | parámetros guardados por elemento (un objeto JSON por línea) |
| `native_graph.ifc`, `ifc.manifest.json`, `ifc.settings.json` | `--ifc` | IFC4 (geometría teselada, conjuntos de propiedades y de cantidades) |
| `native_graph.gltf` + `.bin`, `native_graph.obj` + `.mtl` | `--gltf`, `--obj` | la misma geometría que el GLB; OBJ en metros, eje Y hacia arriba |

Códigos de salida: `0` escrito sin lagunas notificadas, `2` escrito con lagunas notificadas (o argumentos no válidos),
`1` fallo de conversión o de E/S. Ejecute `RVTconverter.exe --help` para ver todas las opciones de IFC
(`--ifc-config`, `--ifc-phase`, `--ifc-design-options`, `--ifc-exclude-categories`, …).

### DDC IFC to Excel

La línea de comandos del paquete portable:

```powershell
C:\DDC\IFC-to-Excel\runtime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py `
    "C:\Models\Building.ifc" --output "C:\Out\Building"
```

El comando imprime una línea JSON (`"status": "CONVERTED"`, `"CONVERTED_WITH_LIMITS"` o `"FAILED"`)
y crea una subcarpeta nueva con `drawing.xlsx`, `data.jsonl`, `data.sqlite` y `result.json`.
Los archivos `.ifczip` se aceptan directamente.

### DDC CAD Drawing to Excel — `dwg2excel.exe`

```powershell
# one or more drawings; a new sub-folder per drawing
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"

# a whole folder: tables only, one JSON line per file for scripts
$dwg = (Get-ChildItem C:\Drawings -Filter *.dwg).FullName
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe @dwg -o C:\Out --no-dxf --no-svg --json
```

Cada carpeta de dibujo contiene `<name>.xlsx`, `<name>.csv`, `<name>.jsonl`, `<name>.dxf`, `<name>.svg`,
`report.json` y `REPORT.txt`. La línea de consola indica cuántos registros se decodificaron, se omitieron o son
de un tipo no admitido. Otras opciones: `--timeout`, `--memory-limit-mb`,
`--language en|ru`, `--version`.

<a id="batch-processing-and-automation"></a>
## Procesamiento por lotes y automatización

**PowerShell — todos los archivos RVT de un árbol de carpetas:**

```powershell
$exe = "C:\DDC\RVT-Converter\cli\RVTconverter.exe"
Get-ChildItem "C:\Projects" -Recurse -Include *.rvt | ForEach-Object {
    & $exe $_.FullName -o (Join-Path "C:\Out" $_.BaseName) --properties --ifc
    "{0}: exit {1}" -f $_.Name, $LASTEXITCODE
}
```

**Python — cargar propiedades de RVT y tablas de IFC con pandas:**

```python
import json, subprocess, pandas as pd

subprocess.run([r"C:\DDC\RVT-Converter\cli\RVTconverter.exe", r"C:\Models\Project.rvt",
                "-o", r"C:\Out\Project", "--properties"], check=False)
rows = [json.loads(line) for line in open(r"C:\Out\Project\properties.jsonl", encoding="utf-8")]
print(len(rows), "property records")

objects = pd.read_excel(r"C:\Out\Building\Building-<id>\drawing.xlsx", sheet_name="Objects")
print(objects.groupby("Category").size().sort_values(ascending=False))
```

**DWG en CI o bots:** `dwg2excel.exe --json` imprime una línea JSON por dibujo; analícela para recoger
el estado, la carpeta de salida y las estadísticas de decodificación.

<a id="ddc-data-viewer"></a>
## DDC Data Viewer

Un visor de escritorio gratuito para la salida de los convertidores: cuadrícula virtualizada para más de 100 000 filas, búsqueda, filtros,
agrupación con sumas, selector de columnas, exportación de la vista actual a XLSX/CSV y un panel 3D que enlaza
filas y elementos en ambos sentidos (GLB o DAE). Inglés, alemán y ruso; tema claro y oscuro.
Descargue `DDC-Data-Viewer-<version>-Setup.exe` o el zip portable de la release.

<a id="free-tools-data-check-quantity-take-off-power-bi-and-excel"></a>
<a id="free-tools-data-check-model-diff-bcf-issues-quantity-take-off-power-bi-and-excel"></a>
## Herramientas gratuitas: comprobación de datos, comparación de modelos, incidencias BCF, mediciones de cantidades, Power BI y Excel

[`ddc-tools/`](ddc-tools/) (Python 3.9+, MIT, sin conexión) trabaja con las tablas que escriben los convertidores
(XLSX, CSV, JSONL, SQLite, JSON):

- `ddc check` valida una exportación con reglas YAML (parámetros obligatorios, expresiones regulares, unicidad, rangos,
  valores permitidos) y escribe un XLSX en semáforo con detalles de ElementId / GlobalId, un informe JSON y un
  código de salida para CI.
- `ddc diff` compara dos exportaciones de un modelo (salida de los convertidores RVT, IFC o DWG): elementos añadidos / eliminados / modificados,
  valores antiguos y nuevos por propiedad y cantidad, XLSX de registro de cambios, JSON, un GLB coloreado según el estado del cambio y un código de salida para CI.
- `ddc bcf` escribe los hallazgos de `ddc check` y `ddc diff` como archivos de incidencias BCF 2.1 / 3.0 (componentes por GlobalId de IFC) y
  tabula cualquier archivo BCF en XLSX. BCF es un formato abierto de buildingSMART; no se declara ninguna certificación.
- `ddc qto` suma recuento, longitud, área y volumen por categoría, tipo y nivel en un XLSX con formato y avisa
  de las cantidades ausentes o nulas.
- [`ddc-tools/powerbi/`](ddc-tools/powerbi/) y [`ddc-tools/excel/`](ddc-tools/excel/): scripts de Power Query
  y un libro de Excel que leen una carpeta de exportación completa, sin necesidad de Python
  ([pasos](ddc-tools/docs/POWER_QUERY.md)).

```bash
pip install ./ddc-tools
ddc check Project.converted --rules ddc-tools/examples/rules_basic.yaml --xlsx check.xlsx
ddc qto Project.converted --xlsx qto.xlsx
ddc diff Model_v1.converted Model_v2.converted --xlsx changes.xlsx --glb diff.glb --bcf changes.bcf
```

Excel y Power BI son marcas registradas de Microsoft Corporation, utilizadas únicamente para indicar con qué trabajan los archivos.

<a id="n8n-workflows-notebooks-and-ai-agents"></a>
## Flujos de trabajo de n8n, notebooks y agentes de IA

- [`DDC_n8n_Workflows&Pipelines/`](DDC_n8n_Workflows&Pipelines/) — nueve flujos de trabajo de n8n (conversión,
  validación por lotes, clasificación con IA, estimación de costes y de CO2, informes QTO).
- [`DDC_in_additon/DDC_python_pipelines/`](DDC_in_additon/DDC_python_pipelines/) — notebooks de Jupyter para
  conversión, procesamiento por lotes y analítica.

> **Configuración:** los flujos de trabajo y los notebooks llaman a los convertidores de [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) mediante `ddc convert` /
> `ddc table` (herramienta gratuita [`ddc-tools/`](ddc-tools/)), que construye la tabla plana (`<name>_rvt.xlsx`, hoja `Project_Data`:
> `ID`, `Category`, `Type Name`, `Level`, `Volume`, ...) a partir de la salida `properties.jsonl` / IFC / DWG; la geometría 3D es GLB.
> Configuración única: `pip install ddc-tools\`. El `README.md` junto a los flujos de trabajo y los notebooks indica qué se comprobó y qué
> no está cubierto (por ejemplo: los pasos de IA de n8n 5-7 necesitan sus credenciales; las programaciones y los PDF de láminas no tienen
> equivalente; las cantidades de Revit proceden de las cantidades de IFC o de la malla GLB).

- [`AI_AGENTS_INSTRUCTIONS/`](AI_AGENTS_INSTRUCTIONS/) — contexto listo para agentes de programación
  (agentes de IA para programar) con las líneas de comandos actuales. Abra el repositorio en su
  agente y pida, por ejemplo, *"convert every .rvt in C:\Projects to IFC and summarise the reports"*.
- [DDC Skills for AI agents](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
  — automatizaciones listas para usar para datos de construcción.

<a id="supported-scope-and-notes"></a>
## Alcance admitido y notas

- **RVT:** no se exportan texturas; la exportación IFC escribe IFC4 teselado. Los elementos que no pueden
  representarse se enumeran en el informe de la ejecución.
- **IFC:** archivos STEP IFC2x3 e IFC4 y `.ifczip`; IFCXML no es compatible. Los registros originales siempre se conservan en
  `data.jsonl` / `data.sqlite`.
- **DWG:** dibujos R13–2018. Algunos tipos de objeto (por ejemplo, ciertas tablas, multi-directrices, sólidos 3D,
  imágenes) se enumeran como *unsupported* en `report.json` en lugar de exportarse de forma incorrecta.
- **Plataformas:** Windows 10/11 x64. **Linux (x64, arm64) y macOS (arm64, x64): convertidores de línea de comandos y Data Viewer, véase [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1).**

Los informes de errores con un pequeño archivo de ejemplo son muy bienvenidos; use
[GitHub Issues](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues) y no adjunte
modelos confidenciales.

<a id="repository-layout"></a>
## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `docs/` | notas de versión, capturas de pantalla |
| `ddc-tools/` | comprobación de datos gratuita, comparación de modelos, incidencias BCF, mediciones de cantidades, kit de Power BI y Excel |
| `DDC_n8n_Workflows&Pipelines/` | archivos JSON de flujos de trabajo de n8n |
| `DDC_in_additon/` | notebooks, presentaciones, imágenes |
| `AI_AGENTS_INSTRUCTIONS/` | instrucciones para agentes de IA de programación |
| `DDC_WINDOWS_Converters/` | convertidores portables para Windows (RVT, RVT-to-IFC, IFC to Excel, CAD Drawing to Excel, Data Viewer), textos de licencia y la documentación del complemento Excel → Revit; los instaladores están en la página de Releases |
| `DDC_LINUX_Converters/` | paquetes de datos CWICR, empaquetado de Qdrant y panel de telemetría |
| `Sample_Projects/` | archivos IFC de ejemplo abiertos |

<a id="licensing"></a>
## Licencias

- **Flujos de trabajo, notebooks, scripts, instrucciones de IA, documentación y `ddc-tools`** — [Licencia MIT](LICENSE).
  Código abierto, uso comercial permitido.
- **Convertidores DDC** (paquetes binarios en Releases y en `DDC_WINDOWS_Converters/` / `DDC_LINUX_Converters/`) —
  software propietario, **gratuito solo para uso no comercial**. **El uso comercial requiere una licencia bajo petición:**
  [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io). Términos: [EULA](EULA.md),
  [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) y [NOTICE](NOTICE). Los componentes de código abierto de terceros
  y sus licencias figuran en `licenses/` dentro de cada paquete.
- La licencia MIT de `ddc-tools` no se extiende a los convertidores que este invoca.

**Uso comercial** significa cualquier uso por parte de, o en nombre de, una empresa, compañía, profesional autónomo, administración
pública u otra organización (incluidos sus empleados o contratistas); en trabajos o servicios remunerados, incluido el
procesamiento de archivos para clientes; en un proyecto que genere o esté destinado a generar ingresos; o dentro de un
producto, servicio, pipeline u oferta SaaS puesto a disposición de terceros. La redistribución, el OEM y la integración SaaS
también están cubiertos.
**Uso no comercial** significa el aprendizaje personal y el uso como afición, la investigación académica, la docencia y el estudio por parte de
estudiantes e instructores, y la evaluación por parte de organizaciones sin ánimo de lucro, en todos los casos sin pago, ingresos
ni finalidad empresarial.

Informes de seguridad: véase [SECURITY.md](SECURITY.md). Patentes, marcas y control de exportaciones:
[PATENTS.md](PATENTS.md), [TRADEMARK.md](TRADEMARK.md), [EXPORT-COMPLIANCE.md](EXPORT-COMPLIANCE.md).

<a id="consulting-and-training"></a>
## Consultoría y formación

DataDrivenConstruction ayuda a empresas de construcción, ingeniería y tecnología a automatizar el procesamiento
de datos CAD/BIM y a crear pipelines ETL abiertos: talleres, consultoría y prototipos sobre sus datos reales.
Contacte con [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io) o visite
[datadrivenconstruction.io](https://datadrivenconstruction.io).

<p>
  <a href="https://x.com/datadrivenconst"><img src="https://img.shields.io/twitter/follow/datadrivenconst?logo=X&style=flat&color=%23f5f5f5" alt="Seguir en X"></a>
  <a href="https://www.youtube.com/@datadrivenconstruction"><img src="https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://www.linkedin.com/company/78381569"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?logoColor=white" alt="LinkedIn"></a>
</p>

Si estas herramientas le resultan útiles, marque el repositorio con una estrella para recibir avisos de nuevas versiones.

<a id="trademarks"></a>
## Marcas registradas

Autodesk y Revit son marcas registradas de Autodesk, Inc. DataDrivenConstruction es software independiente y no está afiliado a Autodesk, Inc. ni cuenta con su respaldo. RVT, RFA, DWG, DXF e IFC son nombres de formatos de archivo utilizados únicamente para indicar qué archivos se leen.
