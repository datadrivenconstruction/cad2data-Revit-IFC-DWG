<p align="center">
  <a href="README.md">English</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.pt-BR.md">Português (Brasil)</a> •
  <a href="README.zh.md">中文</a> •
  <a href="README.ja.md">日本語</a> •
  <a href="README.ar.md">العربية</a>
</p>

<p align="center"><sub>GitHub lento ou bloqueado? Use o espelho: <a href="https://cadbimconverter.com/download/">cadbimconverter.com/download</a> (mesmos arquivos, mesmas somas SHA-256).</sub></p>

# cad2data — conversores DDC para arquivos RVT, IFC e DWG

Autodesk®, Revit® e AutoCAD® são marcas registradas da Autodesk, Inc. IFC e buildingSMART® são marcas da buildingSMART International Ltd. Os nomes de formatos de arquivo (RVT, RFA, DWG, DXF) são usados apenas para identificar formatos. A DataDrivenConstruction não é afiliada, endossada, patrocinada nem certificada pela Autodesk, Inc.

> Este é um guia de início rápido em português do Brasil. A documentação completa, as notas de versão e o histórico de alterações estão em [inglês](README.md). Os nomes de botões e comandos permanecem como na interface.

**Transforme arquivos CAD/BIM em dados abertos e estruturados — localmente, offline, sem licenças de CAD.**

| Conversor | Lê | Gera |
|---|---|---|
| DDC RVT Converter | `.rvt`, `.rfa` (Revit 2019–2027) | GLB, glTF, OBJ, IFC4, tabelas JSONL / CSV / SQLite |
| DDC RVT to IFC | `.rvt`, `.rfa` | IFC4 com conjuntos de propriedades, quantidades, classificação e materiais |
| DDC IFC to Excel | `.ifc`, `.ifczip` (IFC2x3 / IFC4) | `drawing.xlsx`, `data.jsonl`, `data.sqlite` |
| DDC CAD Drawing to Excel | `.dwg` (R13–2018) | `.xlsx`, `.csv`, `.jsonl`, `.dxf`, `.svg` |
| DDC Data Viewer | `.xlsx`, `.csv`, `.jsonl`, `.parquet` + `.glb` | tabela filtrável ligada ao modelo 3D |

## Início rápido

1. Abra a [última versão (release)](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/latest)
   e baixe o pacote desejado: um instalador `*-Setup.exe` (por usuário, sem administrador) ou um `*-portable.zip`.
   Se o GitHub estiver lento ou inacessível, baixe pelo [espelho](https://cadbimconverter.com/download/).
2. Verifique o download com o arquivo `SHA256SUMS.txt` da mesma versão:
   ```powershell
   Get-FileHash .\DDC-RVT-Converter-*-portable.zip -Algorithm SHA256
   ```
3. Descompacte o pacote portátil em uma pasta, por exemplo `C:\DDC\RVT-Converter\`. Mantenha a estrutura de pastas.
   Caminhos com acentos, espaços ou `&` (por exemplo `C:\Projetos\Edifício São Paulo & Cia\`) são aceitos.
4. Abra o aplicativo (`RVT Converter.exe`, `IFC to Excel.exe`, `DWG to Excel.exe`), arraste arquivos ou pastas
   para a janela e clique em *Convert* — ou use a linha de comando abaixo.
5. Abra o resultado no Excel, em Python/pandas ou no DDC Data Viewer.

Os pacotes ainda não são assinados digitalmente; o Windows SmartScreen pode pedir confirmação na primeira execução.
Requisitos: Windows 10/11 x64. Linux e macOS: em breve. Funciona totalmente offline e não precisa de Autodesk, Excel ou Python.

## Linha de comando

```powershell
# GLB + relatórios na pasta "Projeto.converted" ao lado do arquivo
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Modelos\Projeto.rvt"

# pasta de saída própria, propriedades salvas (JSONL) e um arquivo IFC4
C:\DDC\RVT-Converter\cli\RVTconverter.exe "C:\Modelos\Projeto.rvt" -o "C:\Saida\Projeto" --properties --ifc

# IFC em milímetros
C:\DDC\IFC-to-Excel\runtime\python.exe C:\DDC\IFC-to-Excel\sources\ifc-excel\converter.py "C:\Modelos\Predio.ifc" --output "C:\Saida\Predio"

# desenhos DWG
C:\DDC\DWG-to-Excel\cli\dwg2excel.exe "C:\Desenhos\Planta.dwg" -o "C:\Saida"
```

Códigos de saída do RVT Converter: `0` sucesso, `2` gravado com lacunas relatadas (ou argumentos inválidos), `1` falha.
Todas as opções: `RVTconverter.exe --help`.

## Ferramentas gratuitas (ddc-tools, Python 3.9+, MIT)

```powershell
pip install ./ddc-tools
ddc table Projeto.converted --xlsx tabela.xlsx --csv tabela.csv --delimiter semicolon
```

- `--csv` grava UTF-8 com BOM (o Excel mostra corretamente acentos, cirílico, chinês e árabe); números sempre com ponto decimal.
- `--delimiter semicolon` (ou `auto`) gera CSV com ponto e vírgula, como o Excel em português do Brasil espera.
- `--unit-headers` acrescenta unidades aos cabeçalhos: `Area [m2]`, `Volume [m3]`.
- `ddc classify` — colunas de classificação (Uniclass, OmniClass, MasterFormat, DIN 276, GESN/KSR, GB/T 51269, NL-SfB, CCI): [documentação](ddc-tools/docs/CLASSIFICATION.md).

## Licenças

Fluxos de trabalho, notebooks, scripts e documentação: [MIT](LICENSE). Pacotes dos conversores: gratuitos para uso privado e comercial
conforme o EULA incluído em cada pacote (`EULA.txt`); veja também [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) e [NOTICE](NOTICE).
Segurança: [SECURITY.md](SECURITY.md). Marcas: [TRADEMARK.md](TRADEMARK.md).

Contato e treinamentos: [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io) · [datadrivenconstruction.io](https://datadrivenconstruction.io).
Problemas e sugestões (sem anexar modelos confidenciais): [GitHub Issues](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/issues).
