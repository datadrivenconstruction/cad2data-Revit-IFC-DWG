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
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/CAD%20BIM%20Pipeline%20and%20Workflow.jpg" alt="Обзор пайплайна" width="100%"/>
</p>
<p align="center">

  <a href="LICENSE">
  <img src="https://img.shields.io/github/license/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN?color=blue&label=workflows%20licence" alt="Лицензия воркфлоу: MIT">
</a>
<a href="https://datadrivenconstruction.io">
  <img src="https://img.shields.io/badge/powered%20by-DataDrivenConstruction.io-orange" alt="Powered by DataDrivenConstruction.io">
</a>
<img src="https://img.shields.io/badge/input-.rvt%20.dwg%20.ifc%20.dgn-blue?logoColor=white" alt="Форматы ввода"></br>
<img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.dae%20.html%20.pdf%20.ifc-green?logo=microsoft-excel&logoColor=white" alt="Форматы вывода">
<img src="https://img.shields.io/badge/ETL%20pipeline-Ready%20for%20CI/CD%20&%20Bots-success?logo=githubactions" alt="ETL пайплайн">

<!-- Ценообразование -->
<a href="https://dify.ai/pricing" target="_blank">
  <img alt="Static Badge" src="https://img.shields.io/badge/free-pricing?logo=free&color=%23155EEF&label=pricing&labelColor=%23528bff">
</a>
</br>


<h3 align="center">Обработка и конвертация CAD/BIM (Revit, DWG, IFC, DGN) с пакетной обработкой, группировкой, проверками, оценкой стоимости и отчётами QTO. Визуализация процессов автоматизации в открытых агентах и воркфлоу</h3>

<p align="center">
  Автоматизируйте извлечение и преобразование данных CAD/BIM с помощью DDC UI, командной строки, PowerShell или воркфлоу — без привязки к вендору, без лицензий Autodesk® или CAD, с полным контролем над данными вашего проекта
</p>

<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/DDC_GithubLogo.jpg" alt="Обзор пайплайна" width="100%"/>
</p>
<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/09/bandicam-2025-09-14-13-05-05-897.gif" width="100%"/>
<p align="center">
 Клиенты и пользователи DataDrivenConstruction
  <br>
  <a href="https://datadrivenconstruction.io/">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/Clients_DataDrivenConstruction_logos.png" width="95%"/>
  </a>
  <br></br>
</p>


## Содержание

- [Обучающие видео](#обучающие-видео)
- [Обзор](#обзор)
- [Поддерживаемые форматы](#поддерживаемые-форматы)
- [Основные функции](#основные-функции)
- [Запуск конвертеров](#запуск-конвертеров)
- [🖥️ Командная строка (CLI)](#️-командная-строка-cli)
- [🚀 Интеграция с ИИ](#-интеграция-с-ии--идеальное-топливо-для-ии-продуктов)
  - [📂 Папка AI_AGENTS_INSTRUCTIONS](#-папка-ai_agents_instructions--готовый-контекст-для-ии-ассистентов)
- [Быстрый старт](#быстрый-старт)
- [📁 Воркфлоу](#воркфлоу-n8n-для-работы-с-данными-cadbim)
  - [⚡️ 1. Базовая конвертация Revit, IFC, DWG, DGN](#️-1-базовая-конвертация-revit-ifc-dwg-dgn)
  - [⚡️ 2. Конвертация Revit с расширенными настройками](#️-2-конвертация-revit-с-расширенными-настройками)
  - [⚡️ 3. Пакетная конвертация Revit, IFC, DWG с валидацией и отчётами](#️-3-пакетная-конвертация-revit-ifc-dwg-с-валидацией-и-отчётами)
  - [⚡️ 4. Мультиформатная валидация CAD (BIM) для Revit, IFC, DWG, DGN](#️-4-мультиформатная-валидация-cad-bim-для-revit-ifc-dwg-dgn)
  - [⚡️ 5. Универсальная классификация BIM/CAD с ИИ и RAG](#️-5-универсальная-классификация-bimcad-с-ии-и-rag-для-revit-ifc-dwg-dgn)
  - [⚡️ 6. Пайплайны оценки стоимости строительства](#️-6-пайплайны-оценки-стоимости-строительства)
  - [⚡️ 7. Калькулятор углеродного следа CO2](#️-7-калькулятор-углеродного-следа-co2-для-revit-и-ifc-с-llm-ии)
  - [⚡️ 8. Простой ETL для LLM-задач](#️-8-простой-etl-для-llm-задач-для-revit-ifc-dwg-dgn)
  - [⚡️ 9. HTML-отчёт по объёмам из Revit и IFC](#️-9-revit-и-ifc-в-html-отчёт-по-объёмам)
- [Устранение неполадок](#устранение-неполадок)
- [Что такое DataFrames?](#что-такое-dataframes)
- [Excel в Revit. Обновление проекта из Excel](#excel-в-revit-обновление-проекта-из-excel)
- [🗃️ DDC CWICR - База данных строительных расценок](#️-ddc-cwicr---база-данных-строительных-расценок)
- [Участие в разработке](#участие-в-разработке)
- [🆘 Поддержка](#поддержка)
- [🎓 Консалтинг и обучение](#консалтинг-и-обучение)




## Обучающие видео

<table style="border: none; border-collapse: collapse;">
  <!-- Новые видео вверху -->
  <tr>
    <td style="border: none; padding-right: 12px; vertical-align: top;">
      <a href="https://www.youtube.com/watch?v=fHkXDMLzWzQ" target="_blank">
        <img src="DDC_in_additon/DDC_readme_content/DDC_Converter.png" alt="DDC Конвертер" width="460" height="315">
      </a>
    </td>
    <td style="border: none; vertical-align: top;">
     <b> Обзор универсального конвертера CAD/BIM </b>
      <br>
        Введение в <strong>DDC Converter</strong> для пайплайнов Revit, IFC, DWG и DGN — конвертация, валидация и сценарии автоматизации.<br>
        <a href="https://www.youtube.com/watch?v=fHkXDMLzWzQ" target="_blank">Смотреть обзор конвертера на YouTube</a>
      </br>
    </td>
  </tr>
  <tr>
    <td style="border: none; padding-right: 12px; vertical-align: top;">
      <a href="https://www.youtube.com/watch?v=jVU7vlMNTO0" target="_blank">
        <img src="DDC_in_additon/DDC_readme_content/DWG to Excel.png" alt="Пайплайн DWG в Excel" width="460" height="315">
      </a>
    </td>
    <td style="border: none; vertical-align: top;">
     <b> Пайплайн конвертации DWG в Excel </b>
      <br>
        Пошаговое руководство по автоматизации конвертации данных <strong>DWG в Excel</strong> с использованием <code>n8n</code>, что упрощает использование данных CAD-проектов в отчётности и анализе.<br>
        <a href="https://www.youtube.com/watch?v=jVU7vlMNTO0" target="_blank">Смотреть пайплайн DWG в Excel на YouTube</a>
      </br>
    </td>
  </tr>
  <tr>
    <td style="border: none; padding-right: 12px; vertical-align: top;">
      <a href="https://youtu.be/QBaH8oBsPpM?si=gno6LZf98d6gWdPl" target="_blank">
        <img src="DDC_in_additon/DDC_readme_content/ETL with Revit and IFC.png" alt="ETL с Revit и IFC" width="460" height="315">
      </a>
    </td>
    <td style="border: none; vertical-align: top;">
     <b> ETL с Revit и IFC </b>
      <br>
        Узнайте, как построить полноценный <strong>ETL-пайплайн</strong> с данными Revit и IFC: извлечение, преобразование, валидация и загрузка информации проекта в открытые форматы.<br>
        <a href="https://youtu.be/QBaH8oBsPpM?si=gno6LZf98d6gWdPl" target="_blank">Смотреть туториал ETL с Revit и IFC на YouTube</a>
      </br>
    </td>
  </tr>

  <!-- Существующие видео -->
  <tr>
    <td style="border: none; padding-right: 12px; vertical-align: top;">
      <a href="https://youtu.be/HUbEPo-yfeA?si=Gjbj2glKgU3q-XZC" target="_blank">
        <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/07/n8n-how-to-install.png" alt="Быстрый старт n8n" width="460" height="315">
      </a>
    </td>
    <td style="border: none; vertical-align: top;">
     <b> Быстрый старт n8n: простая установка и создание пайплайна (шаблоны и LLM) </b>
      <br>
        Пошаговый туториал для начинающих по настройке <strong>n8n</strong> с нуля, созданию первого пайплайна автоматизации и использованию LLM (ChatGPT/Claude) для генерации автоматизаций.<br>
        <a href="https://youtu.be/HUbEPo-yfeA?si=Gjbj2glKgU3q-XZC" target="_blank">Смотреть быстрый старт n8n на YouTube</a>
      </br>
    </td>
  </tr>
  <tr>
    <td style="border: none; padding-right: 12px; vertical-align: top;">
      <a href="https://www.youtube.com/watch?v=PMTZNRFjD6c" target="_blank">
        <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/07/CAD-BIM-n8n-pipeline.png" alt="Пайплайн CAD-BIM n8n" width="760" height="315">
      </a>
    </td>
    <td style="border: none; vertical-align: top;">
     <b> Туториал по пайплайну данных CAD-BIM </b>
      <br>
        Полное практическое руководство: автоматизация сложных воркфлоу <strong>обработки данных CAD-BIM</strong> в <code>n8n</code>, включая конвертацию, валидацию и практическую аналитику.<br>
        <a href="https://www.youtube.com/watch?v=PMTZNRFjD6c" target="_blank">Смотреть туториал по пайплайну CAD-BIM на YouTube</a>
      </br>
    </td>
  </tr>
  <tr>
    <td style="border: none; padding-right: 12px; vertical-align: top;">
      <a href="https://www.youtube.com/watch?v=p84AmP2dcvg" target="_blank">
        <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/07/n8n-how-to-install.jpg" alt="Автоматическая валидация CAD/BIM" width="460" height="315">
      </a>
    </td>
    <td style="border: none; vertical-align: top;">
     <b> ⚡️Автоматическая валидация данных CAD/BIM с n8n | Конец ручных проверок BIM </b>
      <br>
        Узнайте, как полностью автоматизировать воркфлоу <strong>валидации данных CAD/BIM</strong> с помощью бесплатной open-source платформы <code>n8n</code>. Идеально для проектных команд, желающих экономить часы (или дни) каждую неделю.<br>
        <a href="https://www.youtube.com/watch?v=p84AmP2dcvg" target="_blank">Смотреть туториал по автоматической валидации на YouTube</a>
      </br>
    </td>
  </tr>
</table>


<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/DDC_Github_Apps.jpg" alt="Обзор пайплайна" width="100%"/>
</p>

</p>
<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/DDC_n8n_CAD_BIM.gif" alt="Обзор пайплайна" width="100%"/>
   <br></br>
</p>



## Обзор

Этот пайплайн автоматизирует конвертацию файлов CAD/BIM в Excel для подсчёта объёмов, анализа данных и дальнейшей обработки. Поддерживает офлайн-работу и расширяемость с помощью Python или инструментов ИИ.


## Поддерживаемые форматы

| Формат | Расширение файла | Конвертер | Вывод |
|--------|------------------|-----------|-------|
| Revit (2015-2026) | `.rvt` | RvtExporter.exe | База данных XLSX + Геометрия DAE + Спецификации + Чертежи PDF |
| Revit (2015-2026) | `.rvt` | RVT2IFC_converter.exe | IFC2x3, IFC4, IFC4.3, IFCXML, IFCZIP, HDF5 |
| IFC (2x3, 4x1, 4x4, 4x, 4.3) | `.ifc` | IfcExporter.exe | База данных XLSX + Геометрия DAE |
| AutoCAD (1983-2026) | `.dwg` | DwgExporter.exe | База данных XLSX + Чертежи PDF |
| MicroStation (v7-v8) | `.dgn` | DgnExporter.exe | База данных XLSX |

## Основные функции

- Автоматическая конвертация в Excel (элементы как строки, свойства как столбцы).
- Экспорт 3D полигональной геометрии (DAE) с ID элементов, соответствующими данным XLSX.
- Офлайн-обработка без интернета, API или лицензий.
- Расширяемость для пользовательской постобработки.

## Запуск конвертеров

Конвертеры DDC можно запускать разными способами — **n8n это лишь один из вариантов** для автоматизации.
В зависимости от вашего рабочего процесса и технического уровня, вы можете выбрать один из четырёх методов:

1. **Графический интерфейс (UI)**
   - Лучше всего подходит для нетехнических пользователей и быстрых разовых конвертаций.
   - Интуитивно понятный интерфейс, настройка не требуется — просто выберите папку и начните.
<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/UI%20Converter%20DDC.jpg" width="100%"/>
  <br></br>
</p>

2. **Консоль / Терминал (CMD, PowerShell, Shell)**
   - Подходит для продвинутых пользователей, разработчиков и технических команд.
   - Гибкий и скриптуемый, можно интегрировать в скрипты автоматизации или пакетные процессы.
<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/Terminal%20Version%20CMD%20DDC.jpg" width="100%"/>
  <br></br>
</p>

3. **Пайплайны Python или JavaScript**
   - Идеально для предприятий и команд, работающих с большими наборами данных.
   - Масштабируемая параллельная обработка сотен файлов CAD (BIM).
   - Готовые примеры в папке `DDC_Python_pipelines`.
<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/Code%20DDC.jpg" width="100%"/>
  <br></br>
</p>

4. **Воркфлоу n8n**
   - Идеально для компаний, стремящихся к **полной автоматизации и системной интеграции**.
   - Сквозные пайплайны, где конвертация CAD (BIM) становится частью бесшовного потока данных.
   - Примеры в папке `DDC_n8n_Workflows&Pipelines`.
  <p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/n8n%20pipeline%20DDC.jpg" width="100%"/>
  <br></br>
</p>

---

## 🖥️ Командная строка (CLI)

Конвертеры DDC — это полнофункциональные инструменты командной строки, которые можно интегрировать в **любой рабочий процесс автоматизации**. Это делает их идеальными для скриптинга, CI/CD пайплайнов, ИИ-агентов и low-code платформ.

### 🤖 Почему CLI важен: пусть ИИ строит ваши пайплайны

**Главное преимущество CLI-инструментов в том, что ИИ может использовать их напрямую.**

Современные ИИ-ассистенты для программирования (**Claude Code**, **Cursor**, **GitHub Copilot**, **Windsurf**, **Aider**, **Cline**) могут выполнять shell-команды, читать документацию и автономно создавать полноценные пайплайны автоматизации. Это означает:

> **Вам не нужно писать код самостоятельно — просто опишите, что вы хотите, и ИИ интегрирует конвертеры DDC в ваш рабочий процесс.**

**Как это работает:**
1. **Скопируйте эту документацию** (или укажите ИИ на этот README)
2. **Опишите вашу задачу** на естественном языке: *"Конвертируй все файлы Revit в папке X в Excel, затем проанализируй объёмы стен"*
3. **ИИ читает синтаксис CLI**, пишет скрипт, выполняет его и обрабатывает результаты

**Что ИИ может делать с конвертерами DDC:**
- ✅ Автоматически пакетно конвертировать сотни файлов CAD/BIM
- ✅ Строить ETL-пайплайны: Revit → Excel → База данных → Дашборд
- ✅ Создавать скрипты валидации, проверяющие качество данных BIM
- ✅ Генерировать отчёты из извлечённых данных (PDF, HTML, Excel)
- ✅ Интегрировать конвертации в CI/CD пайплайны
- ✅ Связывать несколько инструментов: конвертировать → валидировать → классифицировать → оценить стоимость
- ✅ Планировать автоматическую обработку через cron/Планировщик задач

**Пример промпта для ИИ-ассистента:**
```
У меня есть файлы Revit в C:\Projects. Используя DDC RvtExporter.exe, расположенный в C:\DDC\,
конвертируй все файлы .rvt в Excel с bounding boxes, затем создай Python-скрипт,
который читает файлы XLSX и генерирует сводный отчёт по всем типам стен и их объёмам.
```

ИИ выполнит:
1. Сканирование папки на файлы `.rvt`
2. Запуск `RvtExporter.exe` для каждого файла с правильными параметрами
3. Написание Python-кода для парсинга полученных `.xlsx` файлов
4. Генерацию сводного отчёта

**Это превращает DDC из инструмента в нативный строительный блок для автоматизации данных в строительстве с помощью ИИ.**

### RvtExporter.exe — Revit в XLSX/DAE/PDF

```
===========================================
         DataDrivenConstruction
         DDC Revit Community
         Version: 17.1.1
===========================================

Usage: RvtExporter <входной файл> [<выходной файл>] [<выходной файл>] [<режим экспорта>] [<файл категорий>] [bbox] [room] [schedule] [sheets2pdf] [-no-xlsx] [-no-collada]
```

| Параметр | Описание |
|----------|----------|
| `<входной файл>` | Входной файл `.rvt` / `.rfa` (обязательно) |
| `[<выходной файл>]` | Путь вывода для файла `.dae` (опционально, включено по умолчанию) |
| `[<выходной файл>]` | Путь вывода для файла `.xlsx` (опционально, включено по умолчанию) |
| `[<режим экспорта>]` | `basic` (309 категорий), `standard` (724), `complete` (1209), или `custom` |
| `[<файл категорий>]` | Файл `.txt` с названиями категорий (требуется только в режиме `custom`) |
| `bbox` | Включить bounding boxes элементов в вывод XLSX |
| `room` | Включить данные ToRoom/FromRoom в вывод XLSX |
| `schedule` | Экспортировать все спецификации Revit |
| `sheets2pdf` | Экспортировать все листы в PDF |
| `-no-xlsx` | Отключить экспорт в формат `.xlsx` |
| `-no-collada` | Отключить экспорт в формат `.dae` |

**Примеры:**
```bash
# Базовая конвертация (XLSX + DAE)
RvtExporter.exe "C:\Projects\Building.rvt"

# Полный экспорт с bounding boxes, спецификациями и листами PDF
RvtExporter.exe "C:\Projects\Building.rvt" complete bbox schedule sheets2pdf

# Экспорт только XLSX (без 3D-геометрии)
RvtExporter.exe "C:\Projects\Building.rvt" -no-collada

# Пользовательские категории из файла
RvtExporter.exe "C:\Projects\Building.rvt" custom "C:\Config\my_categories.txt"
```

---

### RVT2IFCconverter.exe — Revit в IFC

```
===========================================
         DataDrivenConstruction
         DDC RVT2IFC Community
         Version: 17.1.2
===========================================

Usage: Rvt2IfcConverter <input.rvt> [<output.ifc>] [preset|mode=<name>] [config="..."] [key=value ...]
```

| Параметр | Описание |
|----------|----------|
| `<input.rvt>` | Файл Revit `.rvt` / `.rfa` (обязательно) |
| `[<output.ifc>]` | Путь вывода IFC (опционально) |
| `preset=<name>` или `mode=<name>` | `standard`, `extended`, `custom` |
| `config="K=V; K=V; ..."` | Пользовательская конфигурация (разделённая точкой с запятой) |
| `key=value` | Отдельные параметры конфигурации |

**Примеры:**
```bash
# Стандартный экспорт IFC
RVT2IFCconverter.exe "C:\Projects\Building.rvt"

# Расширенный экспорт с большей детализацией
RVT2IFCconverter.exe "C:\Projects\Building.rvt" preset=extended

# Пользовательский путь вывода
RVT2IFCconverter.exe "C:\Projects\Building.rvt" "D:\Output\model.ifc"

# Пользовательская конфигурация
RVT2IFCconverter.exe "C:\Projects\Building.rvt" config="ExportBaseQuantities=true; SitePlacement=Shared"
```

---

### Примеры интеграции

CLI-инструменты можно вызывать практически из любой среды:

#### 🔹 PowerShell / Batch-скрипты
```powershell
# PowerShell: Обработать все файлы .rvt в папке
Get-ChildItem "C:\Projects\*.rvt" | ForEach-Object {
    & "C:\DDC\RvtExporter.exe" $_.FullName
}
```

```batch
:: Batch: Простая конвертация
@echo off
"C:\DDC\RvtExporter.exe" "%1" complete bbox schedule
```

#### 🔹 Задачи VS Code
Добавьте в `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Конвертировать Revit в Excel",
      "type": "shell",
      "command": "C:\\DDC\\RvtExporter.exe",
      "args": ["${file}", "complete", "bbox"],
      "problemMatcher": []
    }
  ]
}
```

#### 🔹 ИИ-ассистенты для программирования (Claude Code, Cursor, Copilot, Windsurf, Aider, Cline)

ИИ-ассистенты с доступом к терминалу могут напрямую выполнять конвертеры DDC и строить полноценные рабочие процессы:

```bash
# Пример: ИИ выполняет эту команду, когда вы спрашиваете "конвертируй мой файл Revit в Excel"
RvtExporter.exe "C:\Projects\Model.rvt" complete bbox schedule
```

**Реальные сценарии рабочих процессов с ИИ:**

| Вы говорите ИИ | ИИ делает |
|----------------|-----------|
| *"Конвертируй Building.rvt в Excel со всеми данными"* | Запускает `RvtExporter.exe Building.rvt complete bbox room` |
| *"Обработай все файлы Revit в этой папке"* | Пишет цикл PowerShell, выполняет конвертер для каждого файла |
| *"Экспортируй в формат IFC 4.3"* | Запускает `RVT2IFCconverter.exe` с правильным пресетом |
| *"Создай оценку стоимости из этой модели"* | Конвертирует в Excel → парсит данные → рассчитывает стоимость |
| *"Проверь качество данных BIM"* | Конвертирует → анализирует XLSX → генерирует отчёт валидации |
| *"Построй дашборд из данных проекта"* | Конвертирует → обрабатывает pandas → создаёт визуализацию |

**Поддерживаемые ИИ-инструменты:**
- **Claude Code** — полный доступ к терминалу, может запускать конвертеры и анализировать результаты
- **Cursor** — IDE с ИИ, который может выполнять shell-команды
- **GitHub Copilot CLI** — ИИ-ассистент командной строки
- **Windsurf** — IDE на базе ИИ с интеграцией терминала
- **Aider** — парное программирование с ИИ в терминале
- **Cline** — расширение VS Code с доступом к shell
- **Open Interpreter** — ИИ, который запускает код локально
- **AutoGPT / AgentGPT** — автономные ИИ-агенты

**Совет профессионала:** Поделитесь этим README со своим ИИ-ассистентом, чтобы он понял полный синтаксис CLI и мог автономно строить сложные пайплайны.

#### 🔹 n8n (узел Execute Command)
```javascript
// В узле Execute Command в n8n
C:\DDC\RvtExporter.exe "{{ $json.filePath }}" complete bbox
```

#### 🔹 Python Subprocess
```python
import subprocess

result = subprocess.run([
    r"C:\DDC\RvtExporter.exe",
    r"C:\Projects\Building.rvt",
    "complete", "bbox", "schedule"
], capture_output=True, text=True)

print(result.stdout)
```

#### 🔹 Node.js / JavaScript
```javascript
const { execSync } = require('child_process');

const output = execSync(
  'C:\\DDC\\RvtExporter.exe "C:\\Projects\\Building.rvt" complete bbox'
);
console.log(output.toString());
```

#### 🔹 Make / Makefile
```makefile
CONVERTER = C:/DDC/RvtExporter.exe

convert:
	$(CONVERTER) "$(INPUT)" complete bbox schedule
```

#### 🔹 GitHub Actions / CI/CD
```yaml
- name: Конвертировать Revit в Excel
  run: |
    C:\DDC\RvtExporter.exe "${{ github.workspace }}\model.rvt" complete bbox
```

#### 🔹 Docker (Windows Container)
```dockerfile
COPY DDC_Converters_Windows_Packages/DDC_CONVERTER_Revit /app/DDC
RUN C:\app\DDC\RvtExporter.exe "C:\data\model.rvt"
```

---

## 🚀 Интеграция с ИИ — Идеальное топливо для AI-продуктов

<p align="center">
  <b>Просто клонируйте репозиторий и опишите, что вам нужно — ИИ сделает остальное</b>
</p>

Конвертеры DDC — это не просто инструменты, это **готовое топливо для AI-приложений**. Создавайте боты для оценки стоимости, автоматизируйте строительные воркфлоу или создавайте интеллектуальных ассистентов — данные работают из коробки с современными ИИ-инструментами.

### Почему DDC идеален для ИИ

| Функция | Преимущество |
|---------|--------------|
| **Структурированный вывод** | Excel/JSON формат, который ИИ может сразу анализировать |
| **CLI-интерфейс** | ИИ-ассистенты могут напрямую вызывать конвертеры |
| **Интеграция с DDC CWICR** | 55 000+ позиций работ с готовыми эмбеддингами для семантического поиска |
| **Мультиформатный ввод** | Revit, IFC, DWG, DGN — один интерфейс для всех форматов |

### 🛠️ Работает с

<table>
<tr>
<td align="center" width="14%">
<img src="https://img.shields.io/badge/Claude_Code-000000?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code"/><br/>
<b>Claude Code</b>
</td>
<td align="center" width="14%">
<img src="https://img.shields.io/badge/Google_Antigravity-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Antigravity"/><br/>
<b>Google Antigravity</b>
</td>
<td align="center" width="14%">
<img src="https://img.shields.io/badge/Cursor-000000?style=for-the-badge&logo=cursor&logoColor=white" alt="Cursor"/><br/>
<b>Cursor</b>
</td>
<td align="center" width="14%">
<img src="https://img.shields.io/badge/GitHub_Copilot-000000?style=for-the-badge&logo=github&logoColor=white" alt="Copilot"/><br/>
<b>Copilot</b>
</td>
<td align="center" width="14%">
<img src="https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white" alt="n8n"/><br/>
<b>n8n</b>
</td>
<td align="center" width="14%">
<img src="https://img.shields.io/badge/Dify-1677FF?style=for-the-badge&logo=openai&logoColor=white" alt="Dify"/><br/>
<b>Dify</b>
</td>
<td align="center" width="14%">
<img src="https://img.shields.io/badge/Windsurf-6366F1?style=for-the-badge&logoColor=white" alt="Windsurf"/><br/>
<b>Windsurf</b>
</td>
</tr>
</table>

---

### 💻 Claude Code & Google Antigravity — ИИ-ассистенты для программирования

Самый быстрый способ работы с конвертерами DDC. Просто откройте репозиторий и задавайте вопросы на естественном языке.

**Начало работы:**
```bash
# Клонируйте репозиторий
git clone https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN.git

# Откройте с Claude Code
cd cad2data-Revit-IFC-DWG-DGN
claude
```

**Примеры промптов:**

| Задача | Промпт |
|--------|--------|
| **Конвертация** | "Конвертируй все .rvt файлы в папке C:\Projects в Excel с bounding boxes" |
| **Анализ данных** | "Проанализируй полученный XLSX и покажи все типы стен с их объёмами" |
| **Построение пайплайна** | "Создай Python-скрипт, который конвертирует Revit → парсит Excel → генерирует отчёт по стоимости" |
| **Валидация BIM** | "Проверь качество данных BIM и сгенерируй отчёт о заполненности параметров" |
| **Оценка стоимости** | "Используя DDC CWICR, оцени стоимость бетонных работ из этой модели" |
| **CI/CD интеграция** | "Напиши GitHub Action, который автоматически конвертирует .rvt при пуше" |

**Советы профессионала:**
- Указывайте ИИ на конкретные файлы: *"Проанализируй Parquet файл и покажи распределение стоимости"*
- Просите объяснения: *"Объясни, как работает ресурсная методология ценообразования"*
- Запрашивайте модификации: *"Модифицируй воркфлоу n8n, добавив уведомления по email"*

---

⭐ <b>Если вы находите наши инструменты полезными и хотите видеть больше подобных приложений для строительной отрасли, пожалуйста, поставьте звезду нашим репозиториям.</b>
Поставьте звезду DDC workflow на GitHub и получайте мгновенные уведомления о новых релизах.
<p align="center">
  <br>
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/GitHub%20Star%20DDC.gif" width="100%"/>
  <br></br>
</p>

---

### 📂 Папка AI_AGENTS_INSTRUCTIONS — Готовый контекст для ИИ-ассистентов

Репозиторий содержит специальную папку **[AI_AGENTS_INSTRUCTIONS](AI_AGENTS_INSTRUCTIONS/)** со всем необходимым для эффективной работы ИИ-ассистентов с этими инструментами.

**Что внутри:**

| Файл | Назначение |
|------|------------|
| **INSTRUCTIONS.md** | Основной обзор: философия репозитория, форматы ввода/вывода, примеры CLI |
| **CLAUDE.md** | Инструкции для Claude Code с детальным синтаксисом CLI |
| **OPENCODE.md** | Инструкции для Opencode |
| **ANTIGRAVITY.md** | Инструкции для Google Antigravity с примерами интеграции GCP |
| **TOOLS_OVERVIEW.md** | Полный справочник по всем конвертерам и логике процессов |
| **DATA_DRIVEN_CONSTRUCTION_BOOK.txt** | Книга "Data-Driven Construction" — руководящая философия автоматизации строительства |

**Почему это важно:**
- ИИ-ассистенты могут читать эти файлы для понимания полного контекста
- Содержит синтаксис CLI, паттерны интеграции и лучшие практики
- Книга служит "компасом" для принятия решений по автоматизации в строительстве
- n8n воркфлоу документированы как **визуальные шаблоны логики процессов** — не финальное решение, а основа для реализации на любом языке (Python, JavaScript, C#, Go, Rust)

**Как использовать:**
```bash
# ИИ-ассистенты автоматически читают AI_AGENTS_INSTRUCTIONS при работе с репозиторием
# Или направьте их напрямую:
"Прочитай AI_AGENTS_INSTRUCTIONS/CLAUDE.md и помоги создать пайплайн пакетной конвертации"
```

---

## 🎯 DDC Skills — 196 Готовых ИИ-Автоматизаций

> **Новинка!** [DDC Skills для ИИ-агентов в строительстве](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction) — полный набор инструментов автоматизации для строительных компаний.

<p align="center">
  <a href="https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction">
    <img src="https://img.shields.io/badge/DDC_Skills-196_ИИ_Автоматизаций-blue?style=for-the-badge&logo=robot" alt="DDC Skills">
  </a>
</p>

### Как это работает

```
1. Клонируйте репозиторий Skills
2. Откройте в Claude Code, Cursor или GitHub Copilot
3. Опишите, что хотите автоматизировать — ИИ проведёт вас шаг за шагом
```

Программирование не требуется. ИИ-ассистент читает определения скиллов и проводит вас через весь процесс автоматизации.

### Скиллы для CAD/BIM-процессов

| Категория | Возможности |
|-----------|-------------|
| **Обработка BIM** | Парсинг IFC, извлечение данных Revit, конвертация DWG/DGN |
| **Автоматизация QTO** | Подсчёт объёмов, ведомости материалов, связка с расценками |
| **Валидация** | Проверка моделей, отчёты о качестве данных, заполненность параметров |
| **Отчётность** | Ежедневные отчёты, фотоотчёты, отслеживание прогресса |
| **Сметы** | Автоматические сметы с базой данных DDC CWICR |
| **Интеграция** | Воркфлоу n8n, синхронизация Excel, API-подключения |

### Экономия времени

| Процесс | Сокращение |
|---------|------------|
| Поиск расценок | 99% (15 мин → 10 сек) |
| Ежедневные отчёты | 92% |
| Сметы | 87% |
| Контроль бюджета | 87% |

Репозиторий Skills объединяет **этот пайплайн CAD2Data** с **базой данных расценок CWICR** — сквозная автоматизация от модели до сметы.

**→ [Изучить 196 DDC Skills](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)**

---

## Быстрый старт с n8n

### Требования

1. **Установите Node.js** с [nodejs.org](https://nodejs.org/).
2. **Запустите n8n** в командной строке:
   ```
   npx n8n
   ```
   Доступ по адресу `http://localhost:5678`.
3. **Скачайте этот репозиторий с GitHub**
   - Нажмите зелёную кнопку "Code" → "Download ZIP"
   - Распакуйте папку
4. **Запустите воркфлоу**
     - Вы готовы. Просто нажмите **Execute Workflow** в n8n, чтобы начать обработку ваших файлов CAD-BIM
<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/07/Install-Nodejs-and-n8n.png" alt="Обзор пайплайна" width="100%"/>
  <br></br>
</p>

---

## Воркфлоу n8n для работы с данными CAD/BIM

### ⚡️ 1. Базовая конвертация Revit, IFC, DWG, DGN
**Файл**: `n8n_1_Revit_IFC_DWG_Conversation_simple.json`

Конвертирует файлы CAD/BIM (`.rvt`, `.ifc`, `.dwg`, `.dgn`) в Excel (XLSX) и Collada (DAE) для файлов Revit/IFC. Минимальная конфигурация для быстрой настройки.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Revit_IFC_DWG_Conversation_simple-1.jpg" alt="Базовая конвертация" width="100%"/>
</p>

#### Установка
1. Импортируйте `n8n_1_Revit_IFC_DWG_Conversation_simple.json` в n8n через **Workflows > Import from File**.
2. Обновите узел **Set Variables**:
   ```
   # Revit
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   path_project_file: C:\Projects\Model.rvt

   # Revit в IFC
   path_to_converter: C:\Converters\datadrivenlibs\RVT2IFCconverter.exe
   path_project_file: C:\Projects\Model.rvt

   # IFC
   path_to_converter: C:\Converters\datadrivenlibs\IfcExporter.exe
   path_project_file: C:\Projects\Model.ifc

   # DWG
   path_to_converter: C:\Converters\datadrivenlibs\DwgExporter.exe
   path_project_file: C:\Projects\Plan.dwg

   # DGN
   path_to_converter: C:\Converters\datadrivenlibs\DgnExporter.exe
   path_project_file: C:\Projects\Bridge.dgn
   ```
3. Убедитесь, что конвертер находится в папке `datadrivenlibs`, например, `C:\Converters\datadrivenlibs\XxxExporter.exe`.

#### Использование
1. Запустите воркфлоу через **Manual Trigger**.
2. Проверьте выходную папку на наличие файлов XLSX, DAE и PDF.
3. Мониторьте логи для статуса конвертации.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Set Variables];
    B --> C[Execute Pipeline];
    C --> D[Output XLSX + DAE + PDF];
```



### ⚡️ 2. Конвертация Revit с расширенными настройками
**Файл**: `n8n_2_All_Settings_Revit_IFC_DWG_Conversation_simple.json`

Конвертирует файлы CAD/BIM с настраиваемыми режимами экспорта (basic: 309 категорий, standard: 724 категории, complete: все 1209 категорий) и опциональными выводами, такими как bounding box, спецификации Revit или PDF-чертежи.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_All_Settings_Revit_IFC_DWG_Conversation_simple-1.jpg" alt="Базовая конвертация" width="100%"/>
</p>

#### Установка
1. Импортируйте `n8n_2_All_Settings_Revit_IFC_DWG_Conversation_simple.json` в n8n через **Workflows > Import from File**.
2. Обновите узел **Set Variables** с путями конвертера и файлов (так же, как в базовой конвертации).
3. Настройте опции экспорта:
   ```
   export_mode: basic | standard | complete
   bbox: true | false
   schedule: true | false
   sheets2pdf: true | false
   no-xlsx: true | false
   no-collada: true | false
   ```

#### Использование
1. Запустите воркфлоу через **Manual Trigger**.
2. Проверьте выходную папку на наличие файлов XLSX, DAE, спецификаций или PDF в зависимости от настроек.
3. Мониторьте логи для статуса конвертации.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Set Variables];
    B --> C[Execute Pipeline];
    C --> D{Export Options};
    D -->|Standard| F[XLSX + DAE];
    D -->|+BBox| G[XLSX + DAE + BBox];
    D -->|+Schedules| H[XLSX + DAE + Schedules];
    D -->|+PDF| I[XLSX + DAE + PDF];
```



### ⚡️ 3. Пакетная конвертация Revit, IFC, DWG с валидацией и отчётами
**Файл**: `n8n_3_CAD-BIM-Batch-Converter-Pipeline.json`

Автоматизирует пакетную конвертацию файлов Revit (`.rvt`) в Excel (XLSX) и Collada (DAE), валидирует выходные данные, отслеживает время обработки и генерирует HTML-отчёт с метриками, ссылками на файлы и деталями конфигурации.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/CAD-BIM-Batch-Converter-Pipeline-1.jpg" alt="Расширенная конвертация" width="100%"/>
</p>

#### Установка
1. Импортируйте `n8n_3_CAD-BIM-Batch-Converter-Pipeline.json` в n8n через **Workflows > Import from File**.
2. Обновите узел **Set Configuration Parameters**:
   ```
   converter_path: C:\Converters\datadrivenlibs\RvtExporter.exe
   source_folder: C:\Sample_Projects
   output_folder: C:\Output
   include_subfolders: true
   file_extension: .rvt
   ```
3. Убедитесь, что `RvtExporter.exe` находится в `C:\Converters\datadrivenlibs\` и файлы `.rvt` находятся в исходной папке.

#### Использование
1. Запустите воркфлоу через **Manual Trigger**.
2. Мониторьте логи для обнаружения файлов и прогресса конвертации.
3. Просмотрите HTML-отчёт (автоматически открывается в браузере) с:
   - Метриками (обработанные файлы, успешность, время, размеры).
   - Таблицами успешных/неудачных конвертаций со ссылками на файлы.
4. Проверьте выходную папку на наличие файлов XLSX и DAE.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Set Config];
    B --> C[Scan Files];
    C --> D[Batch Convert];
    D --> E[Validate Outputs];
    E --> F[Track Metrics];
    F --> G[Generate HTML Report];
    G --> H[Save & Open Report];
```



### ⚡️ 4. Мультиформатная валидация CAD (BIM) для Revit, IFC, DWG, DGN
**Файлы**: `n8n_4_Validation_CAD_BIM_Revit_IFC_DWG.json`, `DDC_BIM_Requirements_Table_for_Revit_IFC_DWG.xlsx`

Валидирует данные CAD/BIM по предопределённым правилам, генерируя цветокодированные отчёты Excel с метриками качества данных.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Validation_CAD_BIM_Revit_IFC_DWG-1.jpg" alt="Пайплайн валидации" width="100%"/>
</p>

#### Установка
1. Импортируйте `n8n_3_Validation_CAD_BIM_Revit_IFC_DWG.json` в n8n через **Workflows > Import from File**.
2. Обновите узел **Setup Paths**:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   validation_rules_path: C:\Validation\DDC_Revit_IFC_Validation_Table.xlsx
   ```
3. Убедитесь, что конвертер и файл правил валидации доступны.

#### Использование
1. Запустите воркфлоу через **Manual Trigger**.
2. Проверьте выходную папку на наличие цветокодированного XLSX-отчёта.
3. Просмотрите метрики качества данных (заполненность, уникальные значения, паттерны).
4. Мониторьте логи для статуса валидации.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Setup Paths];
    B --> C{File Exists?};
    C -->|No| D[Convert to Structured];
    C -->|Yes| E[Load Data];
    D --> E;
    E --> F[Load Rules];
    F --> G[Validate Data];
    G --> H[Calculate Metrics];
    H --> I[Generate Report];
    I --> J[Save & Open];
```

### ⚡️ 5. Универсальная классификация BIM/CAD с ИИ и RAG для Revit, IFC, DWG, DGN
**Файл**: `n8n_5_CAD_BIM_Automatic_Classification_with_LLM_and_RAG.json`

🔗 **Улучшено с базой данных DDC CWICR**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
Этот воркфлоу использует векторную базу данных DDC CWICR (Qdrant), содержащую **55 719 позиций работ** с предварительно вычисленными эмбеддингами OpenAI (3072d). Пайплайн RAG выполняет семантический поиск на 9 языках, сопоставляя элементы BIM со стандартизированными описаниями строительных работ. База данных охватывает весь спектр строительных работ — от земляных работ и бетона до специализированных инженерных систем — обеспечивая точную классификацию по любому стандарту (Omniclass, Uniclass, MasterFormat или пользовательские системы).

Интеллектуально классифицирует строительные элементы из файлов CAD/BIM с использованием ИИ и ЛЮБОЙ системы классификации — международных стандартов (Omniclass, Uniclass и т.д.) или ваших пользовательских/проприетарных классификаций. Поддерживает автоматическое извлечение словарей из файлов маппинга.

#### Ключевые функции
- **Универсальная классификация**: Работает с ЛЮБОЙ системой классификации — стандартной или пользовательской
- **Классификация на базе ИИ**: Использует LLM для классификации элементов с оценкой уверенности
- **Умный маппинг**: Автоматически извлекает словари из файлов Excel, CSV, PDF
- **Автоматическая фильтрация**: Отделяет строительные элементы от чертежей/аннотаций
- **Иерархическая поддержка**: Обрабатывает как плоские, так и иерархические структуры классификации
- **Профессиональные отчёты**: Интерактивные HTML-дашборды + многолистовой Excel
- **Технология RAG**: Retrieval-Augmented Generation для точной классификации

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/Auto-classification-CAD-BIM.jpg" alt="Универсальная классификация" width="100%"/>
</p>

#### Установка
1. Импортируйте `n8n_5_CAD_BIM_Automatic_Classification_with_LLM_and_RAG.json` в n8n
2. Настройте учётные данные ИИ (OpenAI/Anthropic/OpenRouter/Gemini/xAI)
3. Обновите узел **Setup - Define file paths**:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   group_by: Type Name
   classification_name: [Любое название классификации]
   optional_mapping_file: C:\Classifications\[your_classification].xlsx
   optional_help_prompt: "Дополнительный контекст для ИИ"
   ```

#### Гибкость классификации
Этот пайплайн работает с **ЛЮБОЙ системой классификации**:
- ✅ Международные стандарты (Omniclass, Uniclass, MasterFormat и т.д.)
- ✅ Национальные стандарты (DIN, NF, BS и т.д.)
- ✅ Корпоративные классификации
- ✅ Пользовательские проектные классификации
- ✅ Проприетарные системы кодирования
- ✅ Любая структурированная классификация в формате Excel/CSV/PDF

#### Как это работает
1. **С файлом маппинга**: Предоставьте ваш словарь классификации (Excel/CSV/PDF) — ИИ извлечёт коды и применит их точно
2. **Без файла маппинга**: ИИ использует свои знания для классификации по указанному вами стандарту
3. **Гибридный режим**: Комбинируйте файл маппинга с интеллектом ИИ для лучших результатов

**⏱️ Время обработки:** 3-10 секунд на группу элементов (зависит от модели LLM)

```mermaid
graph LR;
    A[Файл CAD/BIM] --> B[Конвертация в Excel];
    B --> C[Фильтрация элементов];
    C --> D{Файл маппинга?};
    D -->|Да| E[Извлечение словаря];
    D -->|Нет| F[Прямая классификация ИИ];
    E --> G[Классификация ИИ с RAG];
    F --> G;
    G --> H[Оценка уверенности];
    H --> I[Профессиональные отчёты];
```



### ⚡️ 6. Пайплайны оценки стоимости строительства

🔗 **На базе базы данных DDC CWICR**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)

Воркфлоу оценки стоимости подключаются к базе данных DDC CWICR, содержащей **55 719 позиций работ** и **27 672 ресурса** с детальной разбивкой цен по 10+ региональным рынкам. Ресурсная методология отделяет физические нормы (человеко-часы, количества материалов, время оборудования) от волатильных цен, обеспечивая прозрачные и проверяемые сметы.

📦 **Загрузки базы данных**: [DDC CWICR Releases](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR/releases) — Excel, Parquet, CSV, снапшоты Qdrant
🌐 **Демо**: [openconstructionestimate.com](https://openconstructionestimate.com) — исследуйте базу данных и семантический поиск

---

#### ⚡️ 6.1 Пайплайн оценки стоимости строительства для Revit и IFC с LLM (ИИ)
**Файл:** `n8n_6_Construction_Price_Estimation_Pipeline.json`

Автоматизирует оценку стоимости строительных элементов из файлов CAD/BIM. Использует ИИ для классификации материалов, поиска рыночных цен и генерации комплексных отчётов о стоимости.

##### Ключевые функции
- **Классификация ИИ**: Материалы по стандартам EU/DE/US
- **Умное ценообразование**: Региональные базы данных с резервными вариантами
- **Анализ стоимости**: Общая стоимость, стоимость за единицу, топ-10 групп
- **Мультиформатный вывод**: Рабочая книга Excel + HTML-отчёт с графиками

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Construction_Price_Estimation_with_LLM_for_Revt_and_IFC-2.jpg" alt="Оценка стоимости" width="100%"/>
</p>

##### Установка
1. Импортируйте `Construction_Price_Estimation_Pipeline.json` в n8n
2. Настройте учётные данные ИИ (OpenAI/Anthropic)
3. Обновите узел **Set Parameters**:
   ```
   input_file_path: C:\Output\Project_Elements.xlsx
   grouping_parameter: Type Name
   country: Germany
   ```
- Параметр группировки (group_by, например 'Type Name', 'IfcType' для IFC или другой)
- Страна (country для расчёта значений, например 'Germany' или 'Brazil')

**⏱️ Время обработки:** 5-15 секунд на группу элементов (зависит от скорости LLM)

```mermaid
graph LR;
    A[CAD/BIM Excel] --> B[Группировка элементов];
    B --> C[Классификация ИИ];
    C --> D[Поиск цен];
    D --> E[Расчёт стоимости];
    E --> F[Отчёты: Excel + HTML];
```

---

#### ⚡️ 6.2 Пайплайн оценки стоимости CAD (BIM) 4D/5D с DDC CWICR
**Файл:** `n8n_4_CAD_(BIM)_Cost_Estimation_Pipeline_4D_5D_with_DDC_CWICR.json`

🔗 **Репозиторий воркфлоу**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)

Автоматическая оценка стоимости из моделей Revit/IFC/DWG. Извлекает данные BIM, классифицирует элементы, декомпозирует в позиции работ и генерирует 4D/5D оценки с полной разбивкой ресурсов.

<p align="left">
  <a href="https://datadrivenconstruction.io">
    <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/CAD%20(Revit)%20to%205D-4D%20Cost%20and%20Time%20Estimate.jpg" alt="CAD в 5D-4D оценку стоимости" width="100%">
  </a>
</p>

##### Этапы пайплайна

| Этап    | Название             | Описание                                                          |
|---------|----------------------|-------------------------------------------------------------------|
| **0**   | Сбор данных BIM      | Извлечение элементов из Revit через DDC Converter                 |
| **1**   | Определение проекта  | ИИ определяет тип проекта (Жилой, Коммерческий и т.д.)           |
| **2**   | Генерация фаз        | ИИ создаёт строительные фазы                                      |
| **3**   | Назначение элементов | ИИ сопоставляет типы BIM с фазами                                |
| **4**   | Декомпозиция работ   | ИИ разбивает типы на позиции работ ("Кирпичная стена" → кладка, раствор) |
| **5**   | Векторный поиск      | Поиск совпадающих расценок в DDC CWICR через Qdrant              |
| **6**   | Маппинг единиц       | Конвертация единиц BIM в единицы расценок                        |
| **7**   | Расчёт стоимости     | Кол-во × Цена за единицу для каждой позиции работ                |
| **7.5** | Валидация            | Проверка CTO на полноту и дубликаты                              |
| **8**   | Агрегация            | Суммирование по фазам и категориям                               |
| **9**   | Генерация отчёта     | Создание HTML и Excel выходных файлов                            |

```mermaid
flowchart TB
    subgraph INPUT["📁 ВВОД<br/><i>CAD • фото • текстовое описание</i>"]
        CAD["📐 Вход проекта<br/>(текст • фото • RVT / IFC / DWG)"]
    end

    subgraph EXTRACT["⚙️ ИЗВЛЕЧЕНИЕ"]
        CONV["RvtExporter.exe / CAD Export / ETL"]
        XLSX["📊 .XLSX<br/>(Сырые элементы)"]
    end

    subgraph PREP["🔧 ПОДГОТОВКА ДАННЫХ"]
        PREP_AI["🤖 ИИ: Очистка и классификация<br/><i>заголовки • типы • категории</i>"]
    end

    subgraph STAGE_PLAN["📋 ЭТАПЫ 1–3: Планирование"]
        PLAN["🤖 Определение проекта и фаз<br/><i>новое / реконструкция / демонтаж</i><br/><i>малый / средний / крупный</i><br/><i>элементы → строительные фазы</i>"]
    end

    subgraph STAGE4["🔨 ЭТАП 4: Декомпозиция"]
        S4["🤖 Декомпозиция типов в работы<br/><i>'Кирпичная стена 240мм' → кладка, раствор, штукатурка</i>"]
    end

    subgraph STAGE5["💰 ЭТАП 5: Ценообразование"]
        S5["🤖 Ценообразование через Vector DB<br/><i>OpenAI embeddings + Qdrant</i><br/><i>код расценки, ед. стоимость, ресурсы</i>"]
    end

    subgraph STAGE75["✅ ЭТАП 7.5: Валидация"]
        S75["🤖 Проверка CTO<br/><i>полнота • дубликаты • пропущенные работы</i>"]
    end

    subgraph OUTPUT["📤 ВЫВОД"]
        HTML["📄 HTML отчёт"]
        XLS["📊 XLS отчёт"]
    end

    CAD --> CONV --> XLSX
    XLSX --> PREP_AI --> PLAN --> S4 --> S5 --> S75
    S75 --> HTML & XLS

    style INPUT fill:#f4f4f5,stroke:#d4d4d8,color:#18181b
    style EXTRACT fill:#e0f2fe,stroke:#bae6fd,color:#0f172a
    style PREP fill:#ede9fe,stroke:#ddd6fe,color:#1e1b4b
    style STAGE_PLAN fill:#ecfdf5,stroke:#bbf7d0,color:#064e3b
    style STAGE4 fill:#fef9c3,stroke:#fef3c7,color:#78350f
    style STAGE5 fill:#fee2e2,stroke:#fecaca,color:#7f1d1d
    style STAGE75 fill:#e0f2f1,stroke:#bae5e1,color:#134e4a
    style OUTPUT fill:#eef2ff,stroke:#e0e7ff,color:#111827
```

##### Ключевые функции
- **Полная интеграция BIM**: Нативная поддержка Revit, IFC, DWG через DDC Converter
- **Декомпозиция на базе ИИ**: Разбивает сложные типы BIM на составляющие позиции работ
- **Семантическое ценообразование**: Векторный поиск Qdrant с 55 719 предварительно встроенными позициями работ
- **Поддержка мультиLLM**: OpenAI GPT-4o, Claude, Gemini 2.5 Pro, xAI Grok, DeepSeek
- **Валидация CTO**: Этап проверки ИИ на полноту и дубликаты
- **9 языков**: AR, DE, EN, ES, FR, HI, PT, RU, ZH с региональным ценообразованием

##### Требования

| Компонент | Требование | Описание |
|-----------|------------|----------|
| **n8n** | v1.0+ (self-hosted) | Платформа автоматизации воркфлоу |
| **Qdrant** | Cloud или self-hosted | Векторная база данных для семантического поиска |
| **OpenAI API** | `text-embedding-3-large` | Генерирует эмбеддинги для сопоставления |
| **LLM API** | OpenAI / Claude / Gemini / Grok | ИИ-модели для классификации |
| **DDC Converter** | `RvtExporter.exe` | Извлекает данные BIM в Excel |

##### Поддерживаемые языки и уровни цен

| Код   | Язык        | Уровень цен     | Валюта | Коллекция Qdrant    |
|-------|-------------|-----------------|--------|---------------------|
| `AR`  | Арабский    | Дубай           | AED    | `ddc_cwicr_ar`      |
| `DE`  | Немецкий    | Берлин          | EUR    | `ddc_cwicr_de`      |
| `EN`  | Английский  | Торонто         | CAD    | `ddc_cwicr_en`      |
| `ES`  | Испанский   | Барселона       | EUR    | `ddc_cwicr_es`      |
| `FR`  | Французский | Париж           | EUR    | `ddc_cwicr_fr`      |
| `HI`  | Хинди       | Мумбаи          | INR    | `ddc_cwicr_hi`      |
| `PT`  | Португальский| Сан-Паулу      | BRL    | `ddc_cwicr_pt`      |
| `RU`  | Русский     | Санкт-Петербург | RUB    | `ddc_cwicr_ru`      |
| `ZH`  | Китайский   | Шанхай          | CNY    | `ddc_cwicr_zh`      |

##### Выходные файлы

Отчёты сохраняются в папку проекта:
```
project_YYYY-MM-DD.html   ← Интерактивный отчёт (открывается в браузере)
project_YYYY-MM-DD.xls    ← Excel-совместимая таблица
```

<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/The%20generated%20report%20includes.jpg" width="100%"/>
</p>

##### Выбор модели LLM

Воркфлоу поддерживает несколько ИИ-провайдеров. Включите предпочитаемую модель:

| Модель           | Статус       |
|------------------|--------------|
| OpenAI GPT-4o    | ✅ По умолчанию |
| Claude Opus 4    | Отключено    |
| Gemini 2.5 Pro   | Отключено    |
| xAI Grok         | Отключено    |
| DeepSeek         | Отключено    |

Для переключения моделей: **Включите** нужный узел модели и **Отключите** остальные.

**⏱️ Время обработки:** Варьируется в зависимости от размера проекта и модели LLM



### ⚡️ 7. Калькулятор углеродного следа CO2 для Revit и IFC с LLM (ИИ)

**Файл:** `n8n_7_Carbon_Footprint_CO2_Estimator_for_Revit_and_IFC.json`

🔗 **Интегрирован с базой данных DDC CWICR**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
Этот воркфлоу использует детальные классификации материалов DDC CWICR и декомпозицию ресурсов для расчёта воплощённого углерода (этапы жизненного цикла A1-A3). База данных предоставляет точные количества материалов на позицию работ — объёмы бетона, тоннаж стали, площади утепления — которые затем сопоставляются с коэффициентами выбросов CO₂e. С данными на 9 языках и по множеству региональных стандартов (EU/DE/US) пайплайн обеспечивает точные оценки устойчивости для международных проектов.

Рассчитывает выбросы воплощённого углерода для строительных проектов. Анализирует материалы, применяет коэффициенты выбросов и генерирует профессиональные отчёты по устойчивости.

#### Ключевые функции
- **Анализ воплощённого углерода**: Этапы жизненного цикла A1-A3
- **Классификация материалов**: Стандарты EU/DE/US с данными о плотности
- **Коэффициенты выбросов**: Отраслевые стандартные коэффициенты CO2e для материалов
- **Оценка воздействия**: Категоризация Критический/Высокий/Средний/Низкий
- **Профессиональные отчёты**: HTML в стиле McKinsey + многолистовой Excel

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Carbon_Footprint_CO2_Estimator_for_Revit-and_IFC-1.jpg" alt="Калькулятор CO2" width="100%"/>
</p>

#### Установка
1. Импортируйте `n8n_6_Carbon_Footprint_CO2_Estimator_for_Revit_and_IFC.json` в n8n
2. Настройте учётные данные ИИ (OpenAI/Anthropic)
3. Обновите узел **Setup - Define file paths**:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   group_by: Type Name (Category или другой)
   country: Germany (страна для расчёта значений, например 'Germany' или 'Brazil')
   ```

**⏱️ Время обработки:** 5-15 секунд на группу элементов (зависит от скорости LLM)


```mermaid
graph LR;
    A[Файл Revit/IFC] --> B[Конвертация в Excel];
    B --> C[Группировка элементов];
    C --> D[ИИ анализ материалов];
    D --> E[Расчёт CO2];
    E --> F[Генерация отчётов];
    F --> G[Вывод Excel + HTML];
```




### ⚡️ 8. Простой ETL для LLM-задач для Revit, IFC, DWG, DGN
**Файл**: `n8n_8_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.json`

Конвертирует файл Revit в Excel, генерирует имя файла XLSX и парсит данные для задач автоматизации на базе LLM.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX-1.jpg" alt="QTO генератор" width="100%"/>
</p>

#### Установка
1. Импортируйте `n8n_4_Revit_IFC_DWG_Conversation_EXTRACT_Phase_with_Parse_XLSX.json` в n8n через **Workflows > Import from File**.
2. Обновите узел **Setup Paths**:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   ```
3. Убедитесь, что конвертер доступен.

#### Использование
1. Запустите воркфлоу через **Manual Trigger**.
2. Проверьте выходную папку на наличие файла XLSX.
3. Используйте распарсенные данные для LLM-задач (например, передайте JSON в Claude или ChatGPT).
4. Мониторьте логи для статуса конвертации и парсинга.




### ⚡️ 9. Revit и IFC в HTML-отчёт по объёмам
**Файл**: `n8n_9_CAD_BIM_Quantity_TakeOff_HTML_Report_Generatorn.json`

Анализирует данные стен Revit, рассчитывает объёмы по типам и генерирует интерактивные HTML-отчёты со сводной статистикой.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/08/n8n_CAD_BIM_Quantity_TakeOff_HTML_Report_Generator-2.jpg" alt="QTO генератор" width="100%"/>
</p>

#### Установка
1. Импортируйте `n8n_5_CAD_BIM_Quantity_TakeOff_HTML_Report_Generatorn.json` в n8n через **Workflows > Import from File**.
2. Обновите узел **Setup Paths**:
   ```
   path_to_converter: C:\Converters\datadrivenlibs\RvtExporter.exe
   project_file: C:\Projects\Model.rvt
   ```
3. Убедитесь, что конвертер доступен.

#### Использование
1. Запустите воркфлоу через **Manual Trigger**.
2. Проверьте выходную папку на наличие HTML-отчёта.
3. Просмотрите отчёт (автоматически открывается в браузере) для объёмов стен и статистики.
4. Мониторьте логи для статуса обработки.

```mermaid
graph LR;
    A[Manual Trigger] --> B[Setup Paths];
    B --> C[Запуск конвертера];
    C --> D{Успех?};
    D -->|Нет| E[Сообщение об ошибке];
    D -->|Да| F[Чтение Excel];
    F --> G[Парсинг данных];
    G --> H[Фильтрация стен];
    H --> I[Очистка данных];
    I --> J[Группировка & сумма];
    J --> K[Генерация HTML];
    K --> L[Сохранение отчёта];
    L --> M[Успех];
```



## Устранение неполадок

### Отсутствует узел Execute Command (n8n 2.0+)

**Симптомы:**
- Узлы показаны со знаком вопроса (?)
- Ошибка: `Unrecognized node type: n8n-nodes-base.executeCommand`
- Execute Command не появляется в поиске узлов

**Решение:** Добавьте переменную окружения перед запуском n8n:
```cmd
set NODES_EXCLUDE=[] && npx n8n
```
Или создайте файл `.env` в `C:\Users\ВАШ_ПОЛЬЗОВАТЕЛЬ\.n8n\.env` с содержимым `NODES_EXCLUDE=[]`

Смотрите [⚠️ Настройка n8n 2.0+](#️-настройка-n8n-20) для деталей.

### Ошибка блокировки модуля 'os'
В версиях n8n 1.98.0–1.101.x модуль `os` заблокирован, что влияет на библиотеки типа pandas. Решение: Используйте последнюю версию с `npx n8n@latest`.


## Что такое DataFrames?

Форматы CAD/BIM, такие как `.rvt`, `.ifc`, `.dwg` или `.dgn`, сложны и проприетарны. Конвертация их в **DataFrames** — табличные структуры со строками (элементами) и столбцами (свойствами) — обеспечивает эффективную обработку данных. Популяризированные библиотекой pandas Python, DataFrames широко используются благодаря совместимости с инструментами автоматизации, аналитики и ИИ (только одна из библиотек Python, pandas, скачивается 12 миллионов раз в день). Они упрощают задачи фильтрации, группировки и визуализации, что делает их идеальными для дашбордов, подсчёта объёмов и валидации.

<p align="center">
  <img src="https://datadrivenconstruction.io/wp-content/uploads/2025/06/n8n-pipeline-11.jpg" alt="Пример DataFrame" width="100%"/>
</p>


Назад к истокам "BIM". Потерянная идентичность: от базы данных к маркетинговому слову.
Изначально BIM никогда не был о модных словах или бесконечных дебатах о совместимости. Его фундаментом всегда были базы данных.

🔹 1974. Чарльз Истман представил Building Description System (BDS). В его статье слово «база данных» появилось 43 раза.
🔹 2000. ADSK опубликовала whitepaper, подчёркивающий ценность прямого доступа к «базе данных CAD». Нейтральные трансляторы типа STEP/IFC считались вторичными.
💬 "Возможность нативного обмена данными – приложения должны обращаться напрямую к основной базе данных CAD, чтобы не терять детали и точность."
🔹 2002. После приобретения Revit-BOM, whitepaper BIM от ADSK снова поставил базу данных в центр (23 упоминания термина).
🔹 2003. В последний раз ADSK официально связала BIM с ИТ и базами данных. После этого база данных исчезла из нарратива — заменённая чистым маркетингом.

<p align="center">
  <img src="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/blob/main/DDC_in_additon/DDC_readme_content/CAD%20database.jpg" width="100%"/>
</p>

В реальности BIM всегда был прост: база данных элементов проекта, каждый со своими параметрами. Всё остальное — маркетинговые надстройки.
Может быть, пора вернуться к сути: открытым, структурированным и доступным данным.


**Узнать больше:**
- [Python Pandas – незаменимый инструмент](https://datadrivenconstruction.io/2025/06/048-python-pandas-an-indispensable-tool-for-working-with-data/)
- [DataFrame – универсальный табличный формат данных](https://datadrivenconstruction.io/2025/06/049-dataframe-universal-tabular-data-format/)
- [Структурированные данные в строительстве](https://datadrivenconstruction.io/2025/06/025-structured-data/)


## Excel в Revit. Обновление проекта из Excel

После преобразования и обогащения ваших данных Excel вы можете легко отправить изменённые данные обратно в ваш проект Revit. Наш специализированный инструмент **[ImportExcelToRevit](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN/tree/main/DDC_Converters_Windows_Packages/DDC_Update_Revit_from_Excel)** делает этот процесс бесшовным, напрямую импортируя обновлённые листы Excel в параметры и семейства Revit.

> **Упростите ваш BIM-воркфлоу:** Revit ➡️ Excel ➡️ Преобразование ➡️ Excel ➡️ Revit.

![enter image description here](https://datadrivenconstruction.io/wp-content/uploads/2024/07/project-data-3.gif)



## 🗃️ DDC CWICR - База данных строительных расценок

Для высококачественной оценки строительных затрат этот репозиторий интегрируется с **[OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)** — открытой мультиязычной базой данных строительных расценок.

### Почему DDC CWICR?

DDC CWICR (Construction Work Items, Components & Resources) обеспечивает основу для точной, прозрачной и проверяемой оценки стоимости:

- **55 719 позиций работ** — полный охват строительных работ
- **27 672 ресурса** — материалы, труд и оборудование с детальной разбивкой
- **9 языков** — арабский, китайский, немецкий, английский, испанский, французский, хинди, португальский, русский
- **85 полей данных** — полная ресурсная структура стоимости на позицию работ
- **Семантический поиск** — векторная база данных Qdrant с эмбеддингами OpenAI (3072d) для запросов на естественном языке

### Преимущества базы данных

| Функция | Преимущество |
|---------|--------------|
| **Ресурсная методология** | Физические нормы (человеко-часы, количества материалов) отделены от волатильных цен |
| **Полная прозрачность** | Полная разбивка каждой стоимостной компоненты — без скрытых наценок |
| **Мультиформатный экспорт** | Excel, Parquet, CSV, снапшоты Qdrant для любого сценария интеграции |
| **Готовность к ИИ** | Предвычисленные эмбеддинги обеспечивают RAG-пайплайны и LLM-оценку |

### Демо и ресурсы

🌐 **Демо**: [openconstructionestimate.com](https://openconstructionestimate.com) — исследуйте базу данных и семантический поиск в действии

📦 **Репозиторий**: [github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)

Воркфлоу в этом репозитории (особенно **Воркфлоу 5, 6 и 7**) используют DDC CWICR для классификации, ценообразования и расчёта углеродного следа, обеспечивая профессиональное качество оценки.



## Участие в разработке

Мы приветствуем участие! Не стесняйтесь:
- Сообщать об ошибках
- Предлагать функции
- Отправлять pull requests
- Улучшать документацию


## Поддержка

🌐 **Сайт**: [DataDrivenConstruction.io](https://datadrivenconstruction.io)
💬 **Issues**: [GitHub Issues](https://github.com/datadrivenconstruction/Revit-IFC-DWG-DGN-Converter-in-n8n-with-QTO/issues)
📧 **Email**: info@datadrivenconstruction.io


## Консалтинг и обучение

Мы работаем с ведущими строительными, инженерными, консалтинговыми агентствами и технологическими компаниями по всему миру, помогая им внедрять принципы открытых данных, автоматизировать обработку CAD/BIM и строить надёжные ETL-пайплайны.

Если вы хотите протестировать это решение на своих данных или заинтересованы в адаптации воркфлоу к реальным проектным задачам, не стесняйтесь связаться с нами.

Наша команда проводит практические воркшопы, предоставляет стратегический консалтинг и разрабатывает прототипы, адаптированные к реальным проектным процессам. Мы активно поддерживаем организации, ищущие практические решения для цифровой трансформации и интероперабельности, фокусируясь на проблемах качества данных и классификации, и продвигая внедрение открытых и автоматизированных воркфлоу.

Свяжитесь с нами для бесплатной консультации, где мы обсудим ваши задачи и продемонстрируем, как автоматизация n8n может трансформировать ваши операции. Обращайтесь по Email [@DataDrivenConstruction](mailto: info@datadrivenconstruction.io) или посетите наш сайт [datadrivenconstruction.io](https://datadrivenconstruction.io), чтобы узнать больше о наших услугах.

---
 <!-- Социальные ссылки -->
  <a href="https://x.com/datadrivenconst" target="_blank">
    <img src="https://img.shields.io/twitter/follow/datadrivenconst?logo=X&style=flat&color=%23f5f5f5" alt="Подписаться в X">
  </a>
  <a href="https://www.youtube.com/@datadrivenconstruction" target="_blank">
    <img src="https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white" alt="Подписаться на YouTube">
  </a>
  <a href="https://www.linkedin.com/company/78381569" target="_blank">
    <img src="https://custom-icon-badges.demolab.com/badge/LinkedIn-0A66C2?logo=linkedin-white&logoColor=fff" alt="Связаться в LinkedIn">
  </a>
</p>


<p align="left">

  <a href="https://datadrivenconstruction.io">
    <img src="https://datadrivenconstruction.io/wp-content/uploads/2023/07/DataDrivenConstruction-1-1.png" alt="DDC Logo" width="200"/>
  </a>
  <br>
   <b>   Раскройте силу данных в строительстве</b>
   <br>
     🚀 Перейдите к полному циклу управления данными, где остаются только унифицированные <br /> структурированные данные и процессы, и где 🔓 ваши данные принадлежат вам
</p>

---

## Товарные знаки

Autodesk®, Revit®, AutoCAD® и DWG™ являются зарегистрированными товарными знаками или товарными знаками Autodesk, Inc. MicroStation® и DGN™ являются товарными знаками Bentley Systems, Incorporated. IFC является товарным знаком buildingSMART International Ltd. OmniClass® и MasterFormat® являются товарными знаками Construction Specifications Institute (CSI). Все прочие названия брендов, продуктов или товарные знаки принадлежат их соответствующим владельцам.

Данный проект не связан, не одобрен и не спонсируется компаниями Autodesk, Bentley Systems, buildingSMART или любыми другими упомянутыми выше владельцами товарных знаков.
