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

<p align="center"><sub>Downloads lentos ou GitHub bloqueado? Use o espelho: <a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a> (mesmos arquivos, mesmas somas SHA-256).</sub></p>

<h1 align="center">cad2data — conversores DDC para arquivos RVT, IFC e DWG</h1>

<p align="center">
  <b>Transforme arquivos CAD/BIM em dados abertos e estruturados — localmente, offline, sem licenças de CAD.</b><br>
  .rvt / .rfa → GLB · glTF · OBJ · IFC4 · JSONL/CSV &nbsp;|&nbsp; .ifc → Excel · JSONL · SQLite &nbsp;|&nbsp; .dwg → Excel · CSV · JSONL · DXF · SVG
</p>

<p align="center">
  <a href="https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest"><img src="https://img.shields.io/github/v/release/datadrivenconstruction/cad2data-Revit-IFC-DWG?label=release" alt="Última versão"></a>
  <img src="https://img.shields.io/badge/input-.rvt%20.rfa%20.ifc%20.ifczip%20.dwg-blue" alt="Formatos de entrada">
  <img src="https://img.shields.io/badge/output-.xlsx%20.csv%20.jsonl%20.glb%20.ifc%20.dxf%20.svg-green" alt="Formatos de saída">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="Windows x64; Linux x64 e arm64; macOS arm64 e x64">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT%20(workflows%2C%20docs)%20%2B%20non-commercial%20EULA%20(converters)-blue" alt="Licença"></a>
</p>

<p align="center">
  <img src="docs/images/data-viewer-3d-grouped.png" alt="DDC Data Viewer: tabela agrupada por categoria e nível com o modelo 3D vinculado" width="100%">
</p>

---

<a id="whats-new-in-ddc-converters-20"></a>
## Novidades no DDC Converters 2.0

O DDC Converters 2.0 é a versão de outubro de 2026 de toda a linha: RVT Converter 2.0, RVT to IFC 2.0,
IFC to Excel 2.0, CAD Drawing to Excel 2.0, Data Viewer 2.0 e Excel Add-in 2.0.
A versão atual do RVT Converter e do RVT to IFC é a [2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2).

- **Uma ferramenta por família de formatos.** `.rvt` / `.rfa` para GLB, glTF, OBJ, IFC4 e tabelas JSONL / CSV / SQLite;
  `.ifc` / `.ifczip` para Excel, JSONL e SQLite; `.dwg` para Excel, CSV, JSONL, DXF e SVG.
- Arquivos do **Revit 2016–2027** são lidos diretamente, sem precisar de uma instalação do Revit.
- **Exportação IFC4 a partir do Revit** com conjuntos de propriedades, quantidades, classificação e materiais, e os perfis
  `full`, `coordination` e `geometry`; opções de unidades, origem, categoria e fase na linha de comando.
- **Ids de elemento em todo lugar.** Cada nó de geometria mantém o id nativo do elemento, de modo que tabelas e 3D se relacionam por `ElementId`.
- **Um relatório a cada execução.** `report.json` / `summary.json` listam o que foi lido e o que foi ignorado, com contagens.
- **Aplicativos de desktop e linha de comando** para cada conversor, códigos de saída adequados para lotes e status JSON de uma linha para scripts.
- **DDC Data Viewer 2.0:** visualizador gratuito de tabelas e 3D com vínculo bidirecional entre linhas e elementos.
- **Offline e portátil.** Windows 10/11 x64, nada a instalar além do pacote (instalador ou zip portátil).
  Os conversores de linha de comando e o Data Viewer para Linux (x64, arm64) e macOS (arm64, x64) estão em [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1) (veja [DDC_LINUX_Converters](DDC_LINUX_Converters/README.md)).

Downloads: [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) (portátil, pronto para executar) e a
[página de Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (instaladores e pacotes).

<a id="contents"></a>
## Conteúdo

- [Conversores](#converters)
- [Capturas de tela](#screenshots)
- [Início rápido](#quick-start)
- [Linha de comando](#command-line)
- [Processamento em lote e automação](#batch-processing-and-automation)
- [DDC Data Viewer](#ddc-data-viewer)
- [Ferramentas gratuitas: verificação de dados, levantamento de quantitativos, Power BI e Excel](#free-tools-data-check-quantity-take-off-power-bi-and-excel)
- [Fluxos de trabalho n8n, notebooks e agentes de IA](#n8n-workflows-notebooks-and-ai-agents)
- [Escopo suportado e observações](#supported-scope-and-notes)
- [Estrutura do repositório](#repository-layout)
- [Licenciamento](#licensing)
- [Marcas registradas](#trademarks)

<a id="converters"></a>
## Conversores

| Pacote | Versão | Lê | Gera | Interface |
|---|---|---|---|---|
| **DDC RVT Converter** | 2.0 | `.rvt`, `.rfa` salvos pelo Revit 2016–2027 | GLB (padrão), glTF, OBJ, IFC4, tabela de elementos (`elements.xlsx`, `elements.csv`: categoria, família, tipo, nível, área, volume, comprimento, parâmetros), propriedades salvas em JSONL; o aplicativo de desktop também gera tabelas CSV e SQLite | Aplicativo de desktop + CLI `RVTconverter.exe` |
| **DDC RVT to IFC** | 2.0 | `.rvt`, `.rfa` | IFC4 com conjuntos de propriedades, quantidades, classificação, materiais; perfis `full`, `coordination`, `geometry` | Aplicativo de desktop (mesma linha de comando do RVT Converter) |
| **DDC IFC to Excel** | 2.0 | Arquivos STEP IFC2x3 / IFC4, `.ifczip` | `drawing.xlsx` (objetos, propriedades, quantidades), `data.jsonl`, `data.sqlite`, `result.json` | Aplicativo de desktop + linha de comando |
| **DDC CAD Drawing to Excel** | 2.0 | Desenhos `.dwg`, versões de formato R13–2018 | `.xlsx` (Entities, Summary, Layers, Blocks), `.csv`, `.jsonl`, `.dxf`, `.svg`, `report.json` | Aplicativo de desktop + CLI `dwg2excel.exe` |
| **DDC Data Viewer** | 2.0 | Tabelas `.xlsx`, `.csv`, `.jsonl`, `.parquet` + geometria `.glb` / `.dae` | visualizações filtradas para XLSX / CSV | Aplicativo de desktop (gratuito) |

Cada nó de geometria gravado pelo RVT Converter mantém o id nativo do elemento, de modo que tabelas e 3D podem ser
relacionados por `ElementId`. Todos os pacotes funcionam totalmente offline no Windows 10/11 x64 e não precisam de Excel
nem de instalação do Python. As versões de linha de comando para Linux e macOS estão na [versão v2026.10.1](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1).

<a id="screenshots"></a>
## Capturas de tela

Todas as capturas de tela abaixo vêm de execuções reais dos pacotes da versão atual. Elas usam modelos de exemplo abertos
do Revit (licença MIT), o edifício de exemplo sintético do visualizador e o exemplo IFC aberto em [`Sample_Projects/`](Sample_Projects/).

| | |
|---|---|
| ![RVT Converter 2.0.2: conversão concluída de dois modelos do Revit](docs/images/rvt-converter-done.png) | ![RVT to IFC 2.0.2: painel de opções de IFC](docs/images/rvt-to-ifc-options.png) |
| **DDC RVT Converter** — dois modelos do Revit convertidos; a pasta de resultado é listada por arquivo. | **DDC RVT to IFC** — unidade de comprimento, origem das coordenadas e as demais configurações de IFC em *More options*. |
| ![Data Viewer: seleção 3D vinculada às linhas da tabela](docs/images/data-viewer-3d-selection.png) | ![Saída do IFC to Excel no Data Viewer, agrupada por classe IFC](docs/images/ifc-to-excel-table.png) |
| **DDC Data Viewer** — um filtro em *Structural Columns* destaca em 3D os elementos vinculados; o painel de resumo soma área, volume e comprimento. | **DDC IFC to Excel** — `drawing.xlsx` do exemplo IFC aberto Duplex, agrupado por classe IFC (333 objetos, 23 classes). |
| ![Execução do RVTconverter na linha de comando](docs/images/cli-rvt-ifc.png) | ![Data Viewer no tema escuro](docs/images/data-viewer-dark.png) |
| **Linha de comando** — `RVTconverter.exe` grava GLB, IFC4, a tabela de elementos e os relatórios, e imprime um resumo de status. | **Tema escuro** — o Data Viewer no tema escuro, com o seletor de idioma da interface no canto superior direito. |

<a id="quick-start"></a>
## Início rápido

1. Abra a [versão 2.0.2](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2.0.2) (RVT Converter, RVT to IFC) ou a [página de Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases) (demais pacotes)
   e baixe o pacote desejado — um `*-Setup.exe` (instalador por usuário) ou um `*-portable.zip`.
2. Verifique o download com o arquivo `SHA256SUMS.txt` da mesma versão:
   ```powershell
   Get-FileHash .\DDC-RVT-Converter-*-portable.zip -Algorithm SHA256
   ```
3. Descompacte o pacote portátil em uma pasta de sua escolha, por exemplo `C:\DDC\RVT-Converter\`,
   `C:\DDC\IFC-to-Excel\`, `C:\DDC\DWG-to-Excel\`. Mantenha a estrutura de pastas como está.
4. Abra o aplicativo de desktop (`RVT Converter.exe`, `IFC to Excel.exe`, `DWG to Excel.exe`), arraste arquivos ou
   pastas para a janela e clique em *Convert* — ou use a linha de comando abaixo.
5. Abra o resultado no Excel, em Python/pandas ou no [DDC Data Viewer](#ddc-data-viewer).

O Windows SmartScreen pode pedir confirmação na primeira execução de um novo download; confira a soma SHA-256 da versão.

<a id="command-line"></a>
## Linha de comando

Os exemplos abaixo foram executados com os binários da versão atual. Os caminhos pressupõem que os pacotes
portáteis foram descompactados em `C:\DDC\`.

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

| Saída | Quando | Conteúdo |
|---|---|---|
| `native_graph.glb` | sempre | malhas 3D, um nó por elemento, nomeado pelo ElementId |
| `summary.json`, `report.json` | sempre | status, contagens, omissões e diagnósticos por elemento |
| `properties.jsonl`, `property_scopes.jsonl` (+ manifestos) | `--properties` | parâmetros salvos por elemento (um objeto JSON por linha) |
| `native_graph.ifc`, `ifc.manifest.json`, `ifc.settings.json` | `--ifc` | IFC4 (geometria tesselada, conjuntos de propriedades e de quantidades) |
| `native_graph.gltf` + `.bin`, `native_graph.obj` + `.mtl` | `--gltf`, `--obj` | mesma geometria do GLB; OBJ em metros, Y para cima |

Códigos de saída: `0` gravado sem lacunas reportadas, `2` gravado com lacunas reportadas (ou argumentos inválidos),
`1` falha de conversão ou de E/S. Execute `RVTconverter.exe --help` para ver todas as opções de IFC
(`--ifc-config`, `--ifc-phase`, `--ifc-design-options`, `--ifc-exclude-categories`, …).

### DDC IFC to Excel

A linha de comando do pacote portátil:

```powershell
C:\DDC\IFC-to-Excel\runtime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py `
    "C:\Models\Building.ifc" --output "C:\Out\Building"
```

O comando imprime uma linha JSON (`"status": "CONVERTED"`, `"CONVERTED_WITH_LIMITS"` ou `"FAILED"`)
e cria uma nova subpasta com `drawing.xlsx`, `data.jsonl`, `data.sqlite` e `result.json`.
Arquivos `.ifczip` são aceitos diretamente.

### DDC CAD Drawing to Excel — `dwg2excel.exe`

```powershell
# one or more drawings; a new sub-folder per drawing
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Drawings\Plan.dwg" -o "C:\Out"

# a whole folder: tables only, one JSON line per file for scripts
$dwg = (Get-ChildItem C:\Drawings -Filter *.dwg).FullName
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe @dwg -o C:\Out --no-dxf --no-svg --json
```

Cada pasta de desenho contém `<name>.xlsx`, `<name>.csv`, `<name>.jsonl`, `<name>.dxf`, `<name>.svg`,
`report.json` e `REPORT.txt`. A linha do console informa quantos registros foram decodificados, ignorados ou
são de um tipo não suportado. Outras opções: `--timeout`, `--memory-limit-mb`,
`--language en|ru`, `--version`.

<a id="batch-processing-and-automation"></a>
## Processamento em lote e automação

**PowerShell — todos os arquivos RVT de uma árvore de pastas:**

```powershell
$exe = "C:\DDC\RVT-Converter\cli\RVTconverter.exe"
Get-ChildItem "C:\Projects" -Recurse -Include *.rvt | ForEach-Object {
    & $exe $_.FullName -o (Join-Path "C:\Out" $_.BaseName) --properties --ifc
    "{0}: exit {1}" -f $_.Name, $LASTEXITCODE
}
```

**Python — carregar propriedades do RVT e tabelas do IFC com pandas:**

```python
import json, subprocess, pandas as pd

subprocess.run([r"C:\DDC\RVT-Converter\cli\RVTconverter.exe", r"C:\Models\Project.rvt",
                "-o", r"C:\Out\Project", "--properties"], check=False)
rows = [json.loads(line) for line in open(r"C:\Out\Project\properties.jsonl", encoding="utf-8")]
print(len(rows), "property records")

objects = pd.read_excel(r"C:\Out\Building\Building-<id>\drawing.xlsx", sheet_name="Objects")
print(objects.groupby("Category").size().sort_values(ascending=False))
```

**DWG em CI ou bots:** `dwg2excel.exe --json` imprime uma linha JSON por desenho; faça o parse dela para coletar
o status, a pasta de saída e as estatísticas de decodificação.

<a id="ddc-data-viewer"></a>
## DDC Data Viewer

Um visualizador de desktop gratuito para a saída dos conversores: grade virtualizada para mais de 100 mil linhas, busca, filtros,
agrupamento com somas, seletor de colunas, exportação da visualização atual para XLSX/CSV e um painel 3D que vincula
linhas e elementos nos dois sentidos (GLB ou DAE). Inglês, alemão e russo; tema claro e escuro.
Baixe `DDC-Data-Viewer-<version>-Setup.exe` ou o zip portátil da versão.

<a id="free-tools-data-check-model-diff-bcf-issues-quantity-take-off-power-bi-and-excel"></a>
<a id="free-tools-data-check-quantity-take-off-power-bi-and-excel"></a>
## Ferramentas gratuitas: verificação de dados, comparação de modelos, issues BCF, levantamento de quantitativos, Power BI e Excel

[`ddc-tools/`](ddc-tools/) (Python 3.9+, MIT, offline) trabalha com as tabelas gravadas pelos conversores
(XLSX, CSV, JSONL, SQLite, JSON):

- `ddc check` valida uma exportação com regras YAML (parâmetros obrigatórios, regex, unicidade, intervalos,
  valores permitidos) e grava um XLSX em semáforo com detalhes de ElementId / GlobalId, um relatório JSON e um
  código de saída para CI.
- `ddc diff` compara duas exportações de um modelo (saída do conversor de RVT, IFC ou DWG): elementos adicionados / removidos / modificados,
  valores antigos e novos por propriedade e quantidade, XLSX de registro de alterações, JSON, um GLB colorido pelo status da alteração e um código de saída para CI.
- `ddc bcf` grava os resultados de `ddc check` e `ddc diff` como arquivos de issues BCF 2.1 / 3.0 (componentes pelo GlobalId do IFC) e
  tabula qualquer arquivo BCF em XLSX. BCF é um formato aberto da buildingSMART; nenhuma certificação é alegada.
- `ddc qto` soma contagem, comprimento, área e volume por categoria, tipo e nível em um XLSX formatado e avisa
  sobre quantidades ausentes ou zeradas.
- [`ddc-tools/powerbi/`](ddc-tools/powerbi/) e [`ddc-tools/excel/`](ddc-tools/excel/): scripts do Power Query
  e uma pasta de trabalho do Excel que leem uma pasta de exportação inteira, sem precisar de Python
  ([passos](ddc-tools/docs/POWER_QUERY.md)).

```bash
pip install ./ddc-tools
ddc check Project.converted --rules ddc-tools/examples/rules_basic.yaml --xlsx check.xlsx
ddc qto Project.converted --xlsx qto.xlsx
ddc diff Model_v1.converted Model_v2.converted --xlsx changes.xlsx --glb diff.glb --bcf changes.bcf
```

Excel e Power BI são marcas registradas da Microsoft Corporation, usadas apenas para indicar com o que os arquivos funcionam.

<a id="n8n-workflows-notebooks-and-ai-agents"></a>
## Fluxos de trabalho n8n, notebooks e agentes de IA

- [`DDC_n8n_Workflows&Pipelines/`](DDC_n8n_Workflows&Pipelines/) — nove fluxos de trabalho n8n (conversão,
  validação em lote, classificação por IA, estimativa de custo e de CO2, relatórios de QTO).
- [`DDC_in_additon/DDC_python_pipelines/`](DDC_in_additon/DDC_python_pipelines/) — notebooks Jupyter para
  conversão, processamento em lote e análises.

> **Configuração:** os fluxos de trabalho e os notebooks chamam os conversores em [`DDC_WINDOWS_Converters/`](DDC_WINDOWS_Converters/) por meio de `ddc convert` /
> `ddc table` (ferramenta gratuita [`ddc-tools/`](ddc-tools/)), que monta a tabela plana (`<name>_rvt.xlsx`, planilha `Project_Data`:
> `ID`, `Category`, `Type Name`, `Level`, `Volume`, ...) a partir da saída de `properties.jsonl` / IFC / DWG; a geometria 3D é GLB.
> Configuração única: `pip install ddc-tools\`. O `README.md` ao lado dos fluxos de trabalho e dos notebooks diz o que foi verificado e o que
> não é coberto (por exemplo: as etapas de IA dos n8n 5-7 precisam das suas credenciais; agendamentos e PDFs de pranchas não têm
> equivalente; as quantidades do Revit vêm das quantidades do IFC ou da malha GLB).

- [`AI_AGENTS_INSTRUCTIONS/`](AI_AGENTS_INSTRUCTIONS/) — contexto pronto para agentes de programação
  (agentes de IA para programação) com as linhas de comando atuais. Abra o repositório no seu
  agente e peça, por exemplo, *"convert every .rvt in C:\Projects to IFC and summarise the reports"*.
- [DDC Skills for AI agents](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)
  — automações prontas para dados de construção.

<a id="supported-scope-and-notes"></a>
## Escopo suportado e observações

- **RVT:** texturas não são exportadas; a exportação IFC grava IFC4 tesselado. Os elementos que não podem ser
  representados são listados no relatório da execução.
- **IFC:** arquivos STEP IFC2x3 e IFC4 e `.ifczip`; IFCXML não é suportado. Os registros originais sempre permanecem em
  `data.jsonl` / `data.sqlite`.
- **DWG:** desenhos R13–2018. Alguns tipos de objeto (por exemplo, certas tabelas, multileaders, sólidos 3D,
  imagens) são listados como *unsupported* em `report.json` em vez de serem exportados incorretamente.
- **Plataformas:** Windows 10/11 x64. **Linux (x64, arm64) e macOS (arm64, x64): conversores de linha de comando e Data Viewer, veja [Releases](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1).**

Relatos de erros com um pequeno arquivo de exemplo são muito bem-vindos — use as
[GitHub Issues](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues) e não anexe
modelos confidenciais.

<a id="repository-layout"></a>
## Estrutura do repositório

| Caminho | Conteúdo |
|---|---|
| `docs/` | notas de versão, capturas de tela |
| `ddc-tools/` | verificação de dados, comparação de modelos, issues BCF, levantamento de quantitativos, kit de Power BI e Excel, tudo gratuito |
| `DDC_n8n_Workflows&Pipelines/` | arquivos JSON de fluxos de trabalho n8n |
| `DDC_in_additon/` | notebooks, apresentações, imagens |
| `AI_AGENTS_INSTRUCTIONS/` | instruções para agentes de IA para programação |
| `DDC_WINDOWS_Converters/` | conversores portáteis para Windows (RVT, RVT-to-IFC, IFC to Excel, CAD Drawing to Excel, Data Viewer), textos de licença e a documentação do add-in Excel → Revit; os instaladores estão na página de Releases |
| `DDC_LINUX_Converters/` | pacotes de dados CWICR, empacotamento do Qdrant e painel de telemetria |
| `Sample_Projects/` | arquivos IFC de exemplo abertos |

<a id="licensing"></a>
## Licenciamento

- **Fluxos de trabalho, notebooks, scripts, instruções para IA, documentação e `ddc-tools`** — [Licença MIT](LICENSE).
  Código aberto, uso comercial permitido.
- **Conversores DDC** (pacotes binários em Releases e em `DDC_WINDOWS_Converters/` / `DDC_LINUX_Converters/`) —
  software proprietário, **gratuito apenas para uso não comercial**. **O uso comercial exige uma licença sob consulta:**
  [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io). Termos: [EULA](EULA.md),
  [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) e [NOTICE](NOTICE). Os componentes de código aberto de terceiros
  e suas licenças estão listados em `licenses/` dentro de cada pacote.
- A licença MIT do `ddc-tools` não se estende aos conversores que ele chama.

**Uso comercial** significa qualquer uso por ou em nome de uma empresa, sociedade, profissional autônomo, órgão
público ou outra organização (incluindo seus funcionários ou contratados); em trabalhos ou serviços remunerados, incluindo
o processamento de arquivos para clientes; em um projeto que gera ou se destina a gerar receita; ou dentro de um
produto, serviço, pipeline ou oferta SaaS disponibilizada a terceiros. Redistribuição, OEM e integração SaaS
também estão incluídas.
**Uso não comercial** significa aprendizado pessoal e uso como hobby, pesquisa acadêmica, ensino e estudo por
estudantes e instrutores, e avaliação por organizações sem fins lucrativos, em cada caso sem pagamento, receita
ou finalidade empresarial.

Relatos de segurança: veja [SECURITY.md](SECURITY.md). Patentes, marcas e controle de exportação:
[PATENTS.md](PATENTS.md), [TRADEMARK.md](TRADEMARK.md), [EXPORT-COMPLIANCE.md](EXPORT-COMPLIANCE.md).

<a id="consulting-and-training"></a>
## Consultoria e treinamento

A DataDrivenConstruction ajuda empresas de construção, engenharia e tecnologia a automatizar o processamento
de dados CAD/BIM e a construir pipelines ETL abertos — workshops, consultoria e protótipos com os seus dados reais.
Entre em contato pelo e-mail [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io) ou visite
[datadrivenconstruction.io](https://datadrivenconstruction.io).

<p>
  <a href="https://x.com/datadrivenconst"><img src="https://img.shields.io/twitter/follow/datadrivenconst?logo=X&style=flat&color=%23f5f5f5" alt="Seguir no X"></a>
  <a href="https://www.youtube.com/@datadrivenconstruction"><img src="https://img.shields.io/badge/YouTube-FF0000?logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://www.linkedin.com/company/78381569"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?logoColor=white" alt="LinkedIn"></a>
</p>

Se estas ferramentas forem úteis para você, dê uma estrela ao repositório para ser notificado sobre novas versões.

<a id="trademarks"></a>
## Marcas registradas

Autodesk e Revit são marcas registradas da Autodesk, Inc. A DataDrivenConstruction é um software independente e não é afiliada nem endossada pela Autodesk, Inc. RVT, RFA, DWG, DXF e IFC são nomes de formatos de arquivo usados apenas para indicar quais arquivos são lidos.
