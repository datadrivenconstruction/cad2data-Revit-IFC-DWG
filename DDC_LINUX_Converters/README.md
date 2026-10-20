# DDC Linux Packages

Linux (.deb) packages for DataDrivenConstruction CWICR semantic search and supporting services.

> **Licensing notice — the DDC binaries in this folder are NOT MIT-licensed.**
> They are proprietary software licensed under the DataDrivenConstruction
> Proprietary Software License and the DataDrivenConstruction Terms of Use and
> EULA at <https://datadrivenconstruction.io/term-of-use-and-eula/>.
>
> See [LICENSE-PROPRIETARY.txt](./LICENSE-PROPRIETARY.txt) and [EULA.txt](./EULA.txt)
> in this folder, and [NOTICE](../NOTICE) at the repository root, for the full terms.
> The build / installation scripts and Markdown documentation in this folder are
> MIT-licensed under the [root LICENSE](../LICENSE).

## Converters: Linux / macOS status

DDC Converters 2.0 (DDC RVT Converter, DDC RVT to IFC, DDC IFC to Excel, DDC DWG to Excel, DDC Data Viewer)
are released for Windows 10/11 x64 through GitHub Releases:
<https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases>
(see [DDC_WINDOWS_Converters](../DDC_WINDOWS_Converters/README.md)).
**Linux and macOS builds are coming soon.**

## Available Packages

### Build-from-source — DDC CWICR (this directory)

| Package | Description |
|---------|-------------|
| `ddc-qdrant` | Qdrant 1.16.3 vector database as a systemd service |
| `ddc-cwicr-cli` | `ddc-search` CLI tool for semantic/keyword search |
| `ddc-cwicr-{lang}` | Language data packages (9 languages) |

---

## Quick Install — DDC CWICR Semantic Search

### 1. Install Qdrant database

```bash
sudo apt install ddc-qdrant
# Service starts automatically on port 6333
# Dashboard: http://localhost:6333/dashboard
```

### 2. Install language data

```bash
# English (Toronto, Canada — CAD currency)
sudo apt install ddc-cwicr-en

# German (Berlin, Germany — EUR)
sudo apt install ddc-cwicr-de

# Russian (St. Petersburg, Russia — RUB)
sudo apt install ddc-cwicr-ru
```

Available languages: `en`, `de`, `ru`, `fr`, `es`, `ar`, `zh`, `pt`, `hi`

Each package downloads ~1 GB of pre-computed OpenAI embeddings (3072 dimensions) during installation.

### 3. Install search CLI

```bash
sudo apt install ddc-cwicr-cli
```

### 4. Search

```bash
# Keyword search (no API key needed)
ddc-search --keyword "concrete foundation"

# Semantic search (requires OpenAI API key)
export OPENAI_API_KEY=sk-...
ddc-search "reinforced concrete foundation"

# List installed collections
ddc-search --list

# JSON output
ddc-search --json --limit 10 "floor tiles"

# Search in specific language
ddc-search --collection ddc_cwicr_de "Stahlbetonfundament"
```

### CWICR Data Coverage

| Language | Region | Currency | Work Items | Resources |
|----------|--------|----------|------------|-----------|
| English | Toronto, Canada | CAD | 55,719 | 27,672 |
| German | Berlin, Germany | EUR | 55,719 | 27,672 |
| Russian | St. Petersburg, Russia | RUB | 55,719 | 27,672 |
| French | Paris, France | EUR | 55,719 | 27,672 |
| Spanish | Barcelona, Spain | EUR | 55,719 | 27,672 |
| Arabic | Dubai, UAE | AED | 55,719 | 27,672 |
| Chinese | Shanghai, China | CNY | 55,719 | 27,672 |
| Portuguese | São Paulo, Brazil | BRL | 55,719 | 27,672 |
| Hindi | Mumbai, India | INR | 55,719 | 27,672 |

---

## Building CWICR Packages from Source

### Prerequisites

- Linux (amd64 or arm64)
- `dpkg-deb`, `curl`, `bash`
- For worker/dashboard: Node.js, `wrangler` CLI

### Build all .deb packages

```bash
cd DDC_Converters_Linux_Packages
./build-all.sh amd64    # or arm64
```

Output: `dist/` directory with all `.deb` files.

### Upload to APT repository

```bash
export CLOUDFLARE_API_TOKEN=your-token
export CLOUDFLARE_ACCOUNT_ID=your-account-id
./upload-to-repo.sh
```

---

## Directory Structure

```
DDC_Converters_Linux_Packages/
├── build-all.sh              # Build orchestration
├── upload-to-repo.sh         # Upload to Cloudflare R2 APT repo
├── ddc-qdrant/               # Qdrant vector DB package
│   ├── build.sh
│   └── root/                 # Package filesystem layout
│       ├── DEBIAN/           # control, postinst, prerm, postrm
│       ├── etc/qdrant/       # config.yaml
│       ├── lib/systemd/      # qdrant.service
│       └── usr/bin/          # qdrant binary (downloaded at build)
├── ddc-cwicr-cli/            # Search CLI package
│   ├── build.sh
│   └── root/
│       ├── DEBIAN/control
│       ├── etc/ddc-cwicr/config
│       └── usr/bin/ddc-search
├── ddc-cwicr-data/           # Language data packages (9 languages)
│   ├── build.sh
│   ├── languages.conf
│   └── template/DEBIAN/      # Templates for control, postinst, prerm
├── worker/                   # Cloudflare Worker (APT repo backend)
├── dashboard/                # Analytics dashboard
└── scripts/                  # Setup & deployment scripts
```

## Dependencies

| Package | Depends On |
|---------|-----------|
| `ddc-qdrant` | `libc6 (>= 2.31)`, `libssl3 \| libssl1.1`, `curl` |
| `ddc-cwicr-cli` | `python3 (>= 3.8)`, `ddc-qdrant` |
| `ddc-cwicr-{lang}` | `ddc-qdrant`, `curl` |

## Troubleshooting

**Qdrant not running:**
```bash
sudo systemctl status qdrant
sudo systemctl start qdrant
sudo journalctl -u qdrant -f
```

**Collection import failed (timeout):**
```bash
sudo systemctl start qdrant
sleep 30
sudo dpkg --configure ddc-cwicr-en
```

**Search returns no results:**
```bash
ddc-search --list              # Check installed collections
sudo apt install ddc-cwicr-en  # Install at least one language
```

## License

MIT — see [LICENSE](../LICENSE)
