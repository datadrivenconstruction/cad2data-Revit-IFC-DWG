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

## Novedades de octubre de 2026

Los convertidores se basan ahora en **lectores de formato propios de DataDrivenConstruction** (RVT: Rust; IFC y DWG: Python) y ya no dependen de ningún SDK CAD de terceros. Los programas de la generación 18.x (`RvtExporter.exe`, `IfcExporter.exe`, `DwgExporter.exe`, `DgnExporter.exe`, `RVT2IFCconverter.exe`) se han retirado del repositorio; los nuevos paquetes están en la [página de releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases). DGN no está soportado por ahora. Todos los convertidores nuevos son versiones preliminares y generan un informe de lo leído, omitido o rechazado.

## Convertidores

| Paquete | Versión | Lee | Escribe |
|---|---|---|---|
| **DDC RVT Converter** | 0.6.8 | `.rvt`, `.rfa` (Autodesk® Revit® 2019–2027) | GLB, glTF, OBJ, IFC4, JSONL / CSV |
| **DDC RVT to IFC** | 0.6.8 | `.rvt`, `.rfa` | IFC4 |
| **DDC IFC to Excel** | 0.3.1 preview | IFC2x3 / IFC4, `.ifczip` | XLSX, JSONL, SQLite |
| **DDC DWG to Excel** | 0.4.1 | `.dwg` (R13–2018) | XLSX, CSV, JSONL, DXF, SVG |
| **DDC Data Viewer** | 0.1.1 | XLSX, CSV, JSONL, Parquet + GLB / DAE | XLSX, CSV |

Todos los paquetes funcionan sin conexión en Windows 10/11 x64 y no requieren software de Autodesk, Excel ni Python.

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

Los flujos n8n y los notebooks se escribieron para la línea de comandos 18.x (XLSX + DAE) y se están adaptando a los nuevos convertidores. Mientras tanto, ajuste la ruta del convertidor y el paso de lectura (propiedades RVT en `properties.jsonl`, geometría en GLB). `AI_AGENTS_INSTRUCTIONS/` ya describe los nuevos comandos.

## Limitaciones

RVT: integridad geométrica no certificada, sin texturas, IFC4 teselado. IFC: sin IFCXML. DWG: algunos tipos de objeto se notifican como no soportados en lugar de exportarse mal; revise `report.json`. Por ahora solo Windows x64; Linux / macOS — coming soon.

## Licencia

Flujos, notebooks, scripts y documentación: [MIT](LICENSE). Paquetes de convertidores: gratuitos para uso privado y comercial según la EULA de DataDrivenConstruction incluida; véase [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) y [NOTICE](NOTICE).

## Marcas

Autodesk®, Revit® y AutoCAD® son marcas registradas de Autodesk, Inc. IFC y buildingSMART® son marcas de buildingSMART International Ltd. Los nombres de formato (RVT, RFA, DWG, DXF, DGN) solo identifican formatos de archivo. DataDrivenConstruction no está afiliada a Autodesk, Inc. ni respaldada o certificada por ella. Texto completo: [README.md](README.md#trademarks).
