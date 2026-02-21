#!/bin/bash
#
# Build all DDC CWICR .deb packages
#
# Usage: ./build-all.sh [amd64|arm64]
#
# Output: packages/dist/
#   ddc-qdrant_1.16.3_{arch}.deb          (~27 MB)
#   ddc-cwicr-cli_1.0.0_all.deb           (~5 KB)
#   ddc-cwicr-en_0.1.0_all.deb            (~5 KB each)
#   ddc-cwicr-de_0.1.0_all.deb
#   ddc-cwicr-ru_0.1.0_all.deb
#   ddc-cwicr-fr_0.1.0_all.deb
#   ddc-cwicr-es_0.1.0_all.deb
#   ddc-cwicr-ar_0.1.0_all.deb
#   ddc-cwicr-zh_0.1.0_all.deb
#   ddc-cwicr-pt_0.1.0_all.deb
#   ddc-cwicr-hi_0.1.0_all.deb
#
set -euo pipefail

ARCH="${1:-amd64}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"

echo "╔══════════════════════════════════════════════╗"
echo "║   DDC CWICR Package Builder                  ║"
echo "║   Architecture: ${ARCH}                         ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Clean previous build
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# 1. Build ddc-qdrant
echo "━━━ Step 1/3: Qdrant server package ━━━"
bash "$SCRIPT_DIR/ddc-qdrant/build.sh" "$ARCH"
echo ""

# 2. Build ddc-cwicr-cli
echo "━━━ Step 2/3: CLI search tool ━━━"
bash "$SCRIPT_DIR/ddc-cwicr-cli/build.sh"
echo ""

# 3. Build all language data packages
echo "━━━ Step 3/3: Language data packages ━━━"
bash "$SCRIPT_DIR/ddc-cwicr-data/build.sh"
echo ""

# Summary
echo "╔══════════════════════════════════════════════╗"
echo "║   Build Complete                             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Packages in $DIST_DIR:"
echo ""
ls -lhS "$DIST_DIR"/*.deb 2>/dev/null | awk '{printf "  %-45s %s\n", $NF, $5}'
echo ""
echo "Total: $(ls "$DIST_DIR"/*.deb 2>/dev/null | wc -l) packages"
echo ""
echo "Next: ./upload-to-repo.sh"
