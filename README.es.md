<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ar.md">العربية</a>
</p>

# cad2data — convertidores DDC para archivos RVT, IFC y DWG

**Convierta archivos CAD/BIM en datos abiertos y estructurados: en local, sin conexión y sin licencias CAD.**

<p align="center"><img src="docs/images/data-viewer-3d-grouped.png" width="100%" alt="DDC Data Viewer"></p>

## Novedades de DDC Converters 2.0

La versión de octubre de 2026 de toda la línea: RVT Converter 2.0, RVT to IFC 2.0, IFC to Excel 2.0, CAD Drawing to Excel 2.0, Data Viewer 2.0 y Excel Add-in 2.0.

- **Una herramienta por familia de formatos.** `.rvt` / `.rfa` a GLB, glTF, OBJ, IFC4 y tablas JSONL / CSV / SQLite; `.ifc` / `.ifczip` a Excel, JSONL y SQLite; `.dwg` a Excel, CSV, JSONL, DXF y SVG.
- **Revit 2019–2027** se lee directamente, sin software de Autodesk y sin licencias CAD.
- **Exportación IFC4 desde Revit** con conjuntos de propiedades, cantidades, clasificación y materiales, y los perfiles `full`, `coordination` y `geometry`; unidades, origen, categorías y fases desde la línea de comandos.
- **ID de elemento en todas partes.** Cada nodo de geometría conserva el ID nativo del elemento, de modo que tablas y 3D se unen por `ElementId`.
- **Un informe por ejecución.** `report.json` / `summary.json` indican con recuentos qué se leyó y qué se omitió.
- **Aplicaciones de escritorio y línea de comandos** para cada convertidor, códigos de salida aptos para lotes y estado JSON en una línea para scripts.
- **DDC Data Viewer 2.0:** visor gratuito de tablas y 3D con enlace bidireccional entre filas y elementos.
- **Sin conexión y portátil.** Windows 10/11 x64; solo hay que instalar el paquete (instalador o zip portable). Compilaciones para Linux / macOS — coming soon.

Descargas: [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (portables, listos para usar) y la [página de releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (instaladores y paquetes).

## Convertidores

| Paquete | Versión | Lee | Escribe |
|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV / SQLite |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4 (conjuntos de propiedades, cantidades, clasificación, materiales) |
| **DDC IFC to Excel** | 2.0 | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC CAD Drawing to Excel** | 2.0 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 2.0 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

Cada nodo de geometría escrito por RVT Converter conserva el ID nativo del elemento, de modo que tablas y 3D se unen por `ElementId`. Todos los paquetes funcionan sin conexión en Windows 10/11 x64 y no requieren software de Autodesk, Excel ni Python. Compilaciones para Linux / macOS — coming soon.

## Capturas

Ejecuciones reales de los paquetes actuales con el edificio sintético del visor y el ejemplo IFC abierto de `Sample_Projects/`.

| | |
|---|---|
| ![](docs/images/data-viewer-3d-selection.png) | ![](docs/images/ifc-to-excel-table.png) |
| ![](docs/images/cli-rvt-ifc.png) | ![](docs/images/data-viewer-dark-ru.png) |

## Inicio rápido

1. Descargue el paquete de la [última release](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest) (`*-Setup.exe` o `*-portable.zip`) y verifíquelo con `SHA256SUMS.txt`.
2. Descomprima el paquete portable, p. ej. en `C:\DDC\`.
3. Inicie la aplicación o use la línea de comandos:

```powershell
# RVT / RFA -> GLB + IFC4 + properties (JSONL)
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Models\Project.rvt" -o "C:\Out\Project" --properties --ifc

# IFC / IFCZIP -> Excel + JSONL + SQLite
C:\DDC\IFC-to-Exceluntime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py "C:\Models\Building.ifc" --output "C:\Out\Building"

# DWG -> Excel + CSV + JSONL + DXF + SVG
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"
```

Opciones, archivos de salida y códigos de salida: [README en inglés](README.md#command-line).

## Flujos n8n, notebooks y agentes de IA

Los flujos n8n (`DDC_n8n_Workflows&Pipelines/`) y los notebooks de Jupyter llaman a los convertidores mediante `ddc convert` / `ddc table` (herramienta gratuita [`ddc-tools/`](ddc-tools/)), que construye la tabla plana (`*_rvt.xlsx`, hoja `Project_Data`) a partir de la salida de los convertidores; la geometría 3D es GLB. Instalación única: `pip install ddc-tools\`. Lo comprobado y lo no cubierto figura en el `README.md` junto a los flujos y notebooks. `AI_AGENTS_INSTRUCTIONS/` contiene el contexto con las líneas de comandos actuales.

## Alcance admitido y notas

- **RVT:** las texturas no se exportan; la exportación IFC escribe IFC4 teselado. Los elementos que no pueden representarse constan en el informe de la ejecución.
- **IFC:** archivos IFC2x3 e IFC4 STEP y `.ifczip`; IFCXML no está soportado. Los registros originales permanecen siempre en `data.jsonl` / `data.sqlite`.
- **DWG:** dibujos R13–2018. Algunos tipos de objeto (por ejemplo ciertas tablas, multiflechas, sólidos 3D, imágenes) figuran en `report.json` como *no soportados* en lugar de exportarse mal.
- **Plataformas:** Windows 10/11 x64. **Linux / macOS — coming soon.**

## Licencia

Flujos, notebooks, scripts y documentación: [MIT](LICENSE). Paquetes de convertidores: gratuitos para uso privado y comercial según la EULA de DataDrivenConstruction incluida; véase [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) y [NOTICE](NOTICE).

## Marcas

Autodesk®, Revit® y AutoCAD® son marcas registradas de Autodesk, Inc. IFC y buildingSMART® son marcas de buildingSMART International Ltd. Los nombres de formato (RVT, RFA, DWG, DXF, DGN) solo identifican formatos de archivo. DataDrivenConstruction no está afiliada a Autodesk, Inc. ni respaldada o certificada por ella. Texto completo: [README.md](README.md#trademarks).
