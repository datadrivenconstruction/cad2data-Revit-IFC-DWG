# DDC Linux and macOS Packages

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

> **Licence: free for non-commercial use only.** Commercial use of the DDC converters requires a licence on
> request: [info@datadrivenconstruction.io](mailto:info@datadrivenconstruction.io). Commercial use means use by or
> for a business or organisation, in paid work or services (including processing files for clients), in
> revenue-generating projects, or inside a product, service or SaaS offered to others. Personal learning,
> research, teaching and non-profit evaluation are non-commercial. Terms: [EULA](../EULA.md) and
> [LICENSE-PROPRIETARY](../LICENSE-PROPRIETARY). The MIT-licensed `ddc-tools` and the documentation are a separate, open-source licence.

## Converters: Linux and macOS (x64, arm64)

DDC Converters 2.0 for Linux (x64, arm64) and macOS (Apple Silicon arm64, Intel x64) are published as binaries in
[GitHub Releases, v2026.10.1](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG/releases/tag/v2026.10.1)
(Windows builds: [DDC_WINDOWS_Converters](../DDC_WINDOWS_Converters/README.md)).

| Product | Version | Linux / macOS file |
|---|---|---|
| DDC RVT Converter (command line `rvt-decode`) | 2.0.1 | `rvt-decode-2.0.1-<platform>.tar.gz` |
| DDC IFC to Excel (`ifc2excel`) | 2.0.1 | `ifc2excel-2.0.1-<platform>.tar.gz` |
| DDC CAD Drawing to Excel (`dwg2excel`) | 2.0.0 | `dwg2excel-2.0.0-<platform>.tar.gz` |
| DDC Data Viewer | 2.0.0 | `ddc-data-viewer-2.0.0-<platform>.AppImage` / `.deb` (Linux), `.dmg` / `.app.tar.gz` (macOS) |

`<platform>` is one of `linux-x64`, `linux-arm64`, `macos-arm64`, `macos-x64`.

```bash
tar xzf ifc2excel-2.0.1-linux-x64.tar.gz
./ifc2excel-2.0.1-linux-x64/ifc2excel Building.ifc --output out
./dwg2excel-2.0.0-linux-x64/dwg2excel Plan.dwg --output out
```

- **Linux:** glibc 2.35 or newer (Ubuntu 22.04 or newer, Debian 12 or newer). The Data Viewer needs WebKitGTK 4.1.
- **macOS:** the binaries are signed ad hoc and not notarized. Clear the download quarantine flag once after unpacking:
  `xattr -dr com.apple.quarantine <unpacked folder or .app>`.
- **Verify:** `sha256sum -c SHA256SUMS-linux-macos.txt` (macOS: `shasum -a 256 -c`). The file is signed with keyless
  cosign (`SHA256SUMS-linux-macos.txt.cosign.bundle`); build provenance is attested by the public workflow in
  [ddc-release-builds](https://github.com/datadrivenconstruction/ddc-release-builds).
- Licence: free for non-commercial use only, see the notice above and the EULA included in each package.

### Open-source components, sources and replacing libraries

- The Linux **AppImage** of the Data Viewer bundles shared libraries of Ubuntu 22.04 (GTK, GLib, WebKitGTK and others),
  many under the GNU LGPL, unchanged. Inside the AppImage: `usr/share/doc/ddc-data-viewer/THIRD_PARTY_NOTICES-linux.txt`
  (every library with package, version, licence and SHA-256), the full licence texts in
  `usr/share/doc/ddc-data-viewer/licenses/` (GPL-2, GPL-3, LGPL-2, LGPL-2.1, LGPL-3, MPL-2.0, Apache-2.0, BSD ...) and the
  copyright file of each package in `usr/share/doc/<package>/copyright`. The list is also a release asset
  (`THIRD_PARTY_NOTICES-linux-<arch>.txt`).
- The **corresponding source code** of exactly the bundled versions is a release asset:
  `ddc-data-viewer-2.0.0-linux-<arch>-third-party-sources.tar.xz` (see `SOURCE-OFFER-linux-<arch>.txt`; valid for at least
  three years, contact info@datadrivenconstruction.io).
- **Using your own library version:** `./ddc-data-viewer-2.0.0-linux-x64.AppImage --appimage-extract`, copy your build of the
  library over the file of the same name in `squashfs-root/usr/lib/`, then run `squashfs-root/AppRun` (or put your
  libraries first with `LD_LIBRARY_PATH`). The libraries are loaded dynamically and can be replaced by any compatible
  version.
- `libjbig0` (GPL-2+, no linking exception) is **not bundled**; it stays a system library.
- `.deb`: `/usr/share/doc/ddc-data-viewer/THIRD_PARTY_NOTICES.txt`; macOS app: `Contents/Resources/licenses/THIRD_PARTY_NOTICES.txt`.
- Command-line archives: `licenses/` holds the licence texts of the bundled Python runtime parts (OpenSSL, libffi, mpdecimal,
  HACL*) and, on Linux, the copyright file of each shared library taken from the distribution. `rvt-decode` ships
  `EULA.txt`, `NOTICE.txt`, `THIRD_PARTY_CRATES.txt` and `licenses/THIRD-PARTY-NOTICES.txt`.

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

Documentation and scripts: MIT, see [LICENSE](../LICENSE). DDC binaries: proprietary, free for non-commercial use only; commercial use requires a licence on request (info@datadrivenconstruction.io), see [EULA](../EULA.md).
