<p align="center">
  <a href="README.md">🇬🇧 English</a> •
  <a href="README.de.md">🇩🇪 Deutsch</a> •
  <a href="README.es.md">🇪🇸 Español</a> •
  <a href="README.fr.md">🇫🇷 Français</a> •
  <a href="README.ru.md">🇷🇺 Русский</a> •
  <a href="README.zh.md">🇨🇳 中文</a> •
  <a href="README.ar.md">🇸🇦 العربية</a>
</p>

<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto/blob/main/DDC_in_additon/DDC_readme_content/CAD%20BIM%20Pipeline%20and%20Workflow.jpg" alt="Vista general del Pipeline" width="100%"/>
</p>
<p align="center">

  <a href="LICENSE">
  <img src="https://img.shields.io/github/license/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto?color=blue&label=workflows%20licence" alt="Licencia de Workflows: MIT">
</a>
<a href="https://datadrivenconstruction.io">
  <img src="https://img.shields.io/badge/powered%20by-DataDrivenConstruction.io-orange" alt="Powered by DataDrivenConstruction.io">
</a>
<img src="https://img.shields.io/badge/input-.rvt%20.dwg%20.ifc%20.dgn-blue?logo=autodesk&logoColor=white" alt="Formatos de entrada"></br>
<img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.dae%20.html%20.pdf%20.ifc-green?logo=microsoft-excel&logoColor=white" alt="Formatos de salida">
<img src="https://img.shields.io/badge/ETL%20pipeline-Ready%20for%20CI/CD%20&%20Bots-success?logo=githubactions" alt="ETL Pipeline">

<!-- Precios -->
<a href="https://dify.ai/pricing" target="_blank">
  <img alt="Static Badge" src="https://img.shields.io/badge/free-pricing?logo=free&color=%23155EEF&label=pricing&labelColor=%23528bff">
</a>
</br>


<h3 align="center">Procesamiento y conversión de CAD/BIM (Revit, DWG, IFC, DGN) con manejo por lotes, agrupación, verificaciones, estimación de costos e informes QTO. Visualización de procesos de automatización en agentes abiertos y flujos de trabajo</h3>

<p align="center">
  Automatice su extracción y transformación de datos CAD/BIM usando DDC UI, línea de comandos, PowerShell o Workflows — sin dependencia de proveedores, sin licencias de Autodesk® o CAD, y con control total de los datos de su proyecto
</p>

<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto/blob/main/DDC_in_additon/DDC_readme_content/DDC_GithubLogo.jpg" alt="Vista general del Pipeline" width="100%"/>
</p>

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Formatos Soportados](#formatos-soportados)
- [Características Principales](#características-principales)
- [Ejecución de los Conversores](#ejecución-de-los-conversores)
- [🖥️ Interfaz de Línea de Comandos (CLI)](#️-interfaz-de-línea-de-comandos-cli)
- [Inicio Rápido con n8n](#inicio-rápido-con-n8n)
- [Soporte](#soporte)

## Descripción General

Este pipeline automatiza la conversión de archivos CAD/BIM a Excel para mediciones, análisis de datos y procesamiento posterior. Soporta operación offline y extensibilidad con Python o herramientas de IA.

## Formatos Soportados

| Formato | Extensión de Archivo | Conversor | Salida |
|---------|---------------------|-----------|--------|
| Revit (2015-2026) | `.rvt` | RvtExporter.exe | Base de datos XLSX + Geometría DAE + Tablas de planificación + Planos PDF |
| Revit (2015-2026) | `.rvt` | RVT2IFC_converter.exe | IFC2x3, IFC4, IFC4.3, IFCXML, IFCZIP, HDF5 |
| IFC (2x3, 4x1, 4x4, 4x, 4.3) | `.ifc` | IfcExporter.exe | Base de datos XLSX + Geometría DAE |
| AutoCAD (1983-2026) | `.dwg` | DwgExporter.exe | Base de datos XLSX + Planos PDF |
| MicroStation (v7-v8) | `.dgn` | DgnExporter.exe | Base de datos XLSX |

## Características Principales

- Conversión automática a Excel (elementos como filas, propiedades como columnas).
- Exportación de geometría poligonal 3D (DAE) con IDs de elementos que coinciden con los datos XLSX.
- Procesamiento offline sin internet, APIs o licencias.
- Extensible para post-procesamiento personalizado.

## Ejecución de los Conversores

Los conversores DDC pueden ejecutarse de diferentes maneras — **n8n es solo una de las opciones** para automatización.
Dependiendo de su flujo de trabajo y conocimiento técnico, puede elegir entre cuatro métodos:

1. **Interfaz Gráfica de Usuario (UI)**
   - Ideal para usuarios no técnicos y conversiones rápidas individuales.
   - Interfaz intuitiva, sin configuración requerida — simplemente seleccione una carpeta y comience.

2. **Consola / Terminal (CMD, PowerShell, Shell)**
   - Adecuado para usuarios avanzados, desarrolladores y equipos técnicos.
   - Flexible y scriptable, puede integrarse en scripts de automatización o procesos por lotes.

3. **Pipelines Python o JavaScript**
   - Ideal para empresas y equipos que trabajan con grandes conjuntos de datos.
   - Procesamiento escalable de cientos de archivos CAD (BIM) en paralelo.
   - Ejemplos listos para usar en la carpeta `DDC_Python_pipelines`.

4. **Flujos de trabajo n8n**
   - Ideal para empresas que buscan **automatización completa e integración de sistemas**.
   - Pipelines de extremo a extremo donde la conversión CAD (BIM) se convierte en parte de un flujo de datos sin interrupciones.
   - Ejemplos en la carpeta `DDC_n8n_workflows`.

---

## 🖥️ Interfaz de Línea de Comandos (CLI)

Los conversores DDC son herramientas de línea de comandos completamente funcionales que pueden integrarse en **cualquier flujo de trabajo de automatización**. Esto los hace perfectos para scripting, pipelines CI/CD, agentes de IA y plataformas low-code.

### 🤖 Por qué CLI es Importante: Deje que la IA Construya sus Pipelines

**La principal ventaja de las herramientas CLI es que la IA puede usarlas directamente.**

Los asistentes de programación con IA modernos (**Claude Code**, **Cursor**, **GitHub Copilot**, **Windsurf**, **Aider**, **Cline**) pueden ejecutar comandos de shell, leer documentación y construir pipelines de automatización completos de forma autónoma. Esto significa:

> **No necesita escribir código usted mismo — simplemente describa lo que quiere, y la IA integrará los conversores DDC en su flujo de trabajo.**

**Cómo funciona:**
1. **Copie esta documentación** (o apunte a la IA a este README)
2. **Describa su tarea** en lenguaje natural: *"Convierte todos los archivos Revit en la carpeta X a Excel, luego analiza las cantidades de muros"*
3. **La IA lee la sintaxis CLI**, escribe el script, lo ejecuta y procesa los resultados

**Lo que la IA puede hacer con los conversores DDC:**
- ✅ Convertir por lotes cientos de archivos CAD/BIM automáticamente
- ✅ Construir pipelines ETL: Revit → Excel → Base de datos → Dashboard
- ✅ Crear scripts de validación que verifican la calidad de datos BIM
- ✅ Generar informes a partir de datos extraídos (PDF, HTML, Excel)
- ✅ Integrar conversiones en pipelines CI/CD
- ✅ Encadenar múltiples herramientas: convertir → validar → clasificar → estimar costos
- ✅ Programar procesamiento automatizado vía cron/Task Scheduler

**Ejemplo de prompt para asistente de IA:**
```
Tengo archivos Revit en C:\Proyectos. Usando DDC RvtExporter.exe ubicado en C:\DDC\,
convierte todos los archivos .rvt a Excel con bounding boxes, luego crea un script Python
que lea los archivos XLSX y genere un informe resumido de todos los tipos de muros y sus volúmenes.
```

**Esto transforma DDC de una herramienta en un bloque de construcción nativo de IA para automatización de datos de construcción.**

### RvtExporter.exe — Revit a XLSX/DAE/PDF

```
===========================================
         DataDrivenConstruction
         DDC Revit Community
         Version: 17.1.1
===========================================

Usage: RvtExporter <archivo entrada> [<archivo salida>] [<archivo salida>] [<modo exportación>] [<archivo categorías>] [bbox] [room] [schedule] [sheets2pdf] [-no-xlsx] [-no-collada]
```

| Parámetro | Descripción |
|-----------|-------------|
| `<archivo entrada>` | Archivo `.rvt` / `.rfa` de entrada (requerido) |
| `[<archivo salida>]` | Ruta de salida para archivo `.dae` (opcional, habilitado por defecto) |
| `[<archivo salida>]` | Ruta de salida para archivo `.xlsx` (opcional, habilitado por defecto) |
| `[<modo exportación>]` | `basic` (309 categorías), `standard` (724), `complete` (1209), o `custom` |
| `[<archivo categorías>]` | Archivo `.txt` con nombres de categorías (requerido solo en modo `custom`) |
| `bbox` | Incluir bounding boxes de elementos en salida XLSX |
| `room` | Incluir datos ToRoom/FromRoom en salida XLSX |
| `schedule` | Exportar todas las tablas de planificación de Revit |
| `sheets2pdf` | Exportar todas las hojas a PDF |
| `-no-xlsx` | Deshabilitar exportación a formato `.xlsx` |
| `-no-collada` | Deshabilitar exportación a formato `.dae` |

**Ejemplos:**
```bash
# Conversión básica (XLSX + DAE)
RvtExporter.exe "C:\Proyectos\Edificio.rvt"

# Exportación completa con bounding boxes, tablas y hojas PDF
RvtExporter.exe "C:\Proyectos\Edificio.rvt" complete bbox schedule sheets2pdf

# Exportar solo XLSX (sin geometría 3D)
RvtExporter.exe "C:\Proyectos\Edificio.rvt" -no-collada

# Categorías personalizadas desde archivo
RvtExporter.exe "C:\Proyectos\Edificio.rvt" custom "C:\Config\mis_categorias.txt"
```

---

### RVT2IFCconverter.exe — Revit a IFC

```
===========================================
         DataDrivenConstruction
         DDC RVT2IFC Community
         Version: 17.1.2
===========================================

Usage: Rvt2IfcConverter <entrada.rvt> [<salida.ifc>] [preset|mode=<nombre>] [config="..."] [key=value ...]
```

| Parámetro | Descripción |
|-----------|-------------|
| `<entrada.rvt>` | Archivo Revit `.rvt` / `.rfa` (requerido) |
| `[<salida.ifc>]` | Ruta de salida IFC (opcional) |
| `preset=<nombre>` o `mode=<nombre>` | `standard`, `extended`, `custom` |
| `config="K=V; K=V; ..."` | Configuración personalizada (separada por punto y coma) |
| `key=value` | Parámetros de configuración individuales |

---

### Ejemplos de Integración

#### 🔹 Asistentes de Programación con IA (Claude Code, Cursor, Copilot, Windsurf, Aider, Cline)

Los asistentes de IA con acceso a terminal pueden ejecutar directamente los conversores DDC y construir flujos de trabajo completos:

```bash
# Ejemplo: IA ejecuta este comando cuando preguntas "convierte mi archivo Revit a Excel"
RvtExporter.exe "C:\Proyectos\Modelo.rvt" complete bbox schedule
```

**Escenarios reales de flujos de trabajo con IA:**

| Usted dice a la IA | La IA hace |
|--------------------|-----------|
| *"Convierte Edificio.rvt a Excel con todos los datos"* | Ejecuta `RvtExporter.exe Edificio.rvt complete bbox room` |
| *"Procesa todos los archivos Revit en esta carpeta"* | Escribe bucle PowerShell, ejecuta conversor para cada archivo |
| *"Exporta a formato IFC 4.3"* | Ejecuta `RVT2IFCconverter.exe` con preset correcto |
| *"Crea una estimación de costos desde este modelo"* | Convierte a Excel → analiza datos → calcula costos |
| *"Valida la calidad de datos BIM"* | Convierte → analiza XLSX → genera informe de validación |

**Herramientas de IA soportadas:**
- **Claude Code** — acceso completo a terminal, puede ejecutar conversores y analizar resultados
- **Cursor** — IDE con IA que puede ejecutar comandos de shell
- **GitHub Copilot CLI** — asistente de IA de línea de comandos
- **Windsurf** — IDE impulsado por IA con integración de terminal
- **Aider** — programación en pareja con IA en terminal
- **Cline** — extensión de VS Code con acceso a shell
- **Open Interpreter** — IA que ejecuta código localmente
- **AutoGPT / AgentGPT** — agentes de IA autónomos

**Consejo profesional:** Comparta este README con su asistente de IA para que entienda la sintaxis CLI completa y pueda construir pipelines sofisticados de forma autónoma.

#### 🔹 PowerShell / Scripts Batch
```powershell
# PowerShell: Procesar todos los archivos .rvt en una carpeta
Get-ChildItem "C:\Proyectos\*.rvt" | ForEach-Object {
    & "C:\DDC\RvtExporter.exe" $_.FullName
}
```

#### 🔹 Python Subprocess
```python
import subprocess

result = subprocess.run([
    r"C:\DDC\RvtExporter.exe",
    r"C:\Proyectos\Edificio.rvt",
    "complete", "bbox", "schedule"
], capture_output=True, text=True)

print(result.stdout)
```

#### 🔹 n8n (Nodo Execute Command)
```javascript
// En nodo Execute Command de n8n
C:\DDC\RvtExporter.exe "{{ $json.filePath }}" complete bbox
```

---

## Inicio Rápido con n8n

### Prerrequisitos

1. **Instalar Node.js** desde [nodejs.org](https://nodejs.org/).
2. **Iniciar n8n** en el símbolo del sistema:
   ```
   npx n8n
   ```
   Acceda en `http://localhost:5678`.
3. **Descargar este repositorio de GitHub**
   - Haga clic en el botón verde "Code" → "Download ZIP"
   - Descomprima la carpeta
4. **Ejecutar el Flujo de Trabajo**
     - Está listo. Simplemente haga clic en **Execute Workflow** en n8n para procesar sus archivos CAD-BIM

---

## Soporte

🌐 **Sitio web**: [DataDrivenConstruction.io](https://datadrivenconstruction.io)
💬 **Issues**: [GitHub Issues](https://github.com/datadrivenconstruction/Revit-IFC-DWG-DGN-Converter-in-n8n-with-QTO/issues)
📧 **Email**: info@datadrivenconstruction.io

---

<p align="left">
  <a href="https://datadrivenconstruction.io">
    <img src="https://datadrivenconstruction.io/wp-content/uploads/2023/07/DataDrivenConstruction-1-1.png" alt="DDC Logo" width="200"/>
  </a>
  <br>
   <b>   Libere el Poder de los Datos en la Construcción</b>
   <br>
     🚀 Pase a la gestión de datos de ciclo completo donde solo quedan <br /> datos y procesos estructurados unificados y donde 🔓 sus datos son suyos
</p>
