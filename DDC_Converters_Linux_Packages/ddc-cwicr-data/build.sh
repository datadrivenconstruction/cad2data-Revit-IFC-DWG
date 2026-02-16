#!/bin/bash
#
# Build all ddc-cwicr-{lang} data packages
# Each package is tiny (~5 KB) — the actual data is downloaded during install
#
# Usage: ./build.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$(dirname "$SCRIPT_DIR")/dist"
VERSION="0.1.0"

mkdir -p "$DIST_DIR"

echo "=== Building DDC CWICR data packages ==="
echo ""

# Read language configuration
while IFS='|' read -r LANG REGION CURRENCY COLLECTION SNAPSHOT; do
    # Skip comments and empty lines
    [[ "$LANG" =~ ^#.*$ ]] && continue
    [[ -z "$LANG" ]] && continue

    PKG_NAME="ddc-cwicr-${LANG}"
    BUILD_DIR="$(mktemp -d)"

    echo "Building: ${PKG_NAME} (${REGION})..."

    # Create package structure
    mkdir -p "$BUILD_DIR/pkg/DEBIAN"

    # Generate control file from template
    sed -e "s|__LANG__|${LANG}|g" \
        -e "s|__REGION__|${REGION}|g" \
        -e "s|__CURRENCY__|${CURRENCY}|g" \
        "$SCRIPT_DIR/template/DEBIAN/control.template" > "$BUILD_DIR/pkg/DEBIAN/control"

    # Generate postinst from template
    sed -e "s|__LANG__|${LANG}|g" \
        -e "s|__REGION__|${REGION}|g" \
        -e "s|__COLLECTION__|${COLLECTION}|g" \
        -e "s|__SNAPSHOT__|${SNAPSHOT}|g" \
        "$SCRIPT_DIR/template/DEBIAN/postinst.template" > "$BUILD_DIR/pkg/DEBIAN/postinst"
    chmod 755 "$BUILD_DIR/pkg/DEBIAN/postinst"

    # Generate prerm from template
    sed -e "s|__COLLECTION__|${COLLECTION}|g" \
        "$SCRIPT_DIR/template/DEBIAN/prerm.template" > "$BUILD_DIR/pkg/DEBIAN/prerm"
    chmod 755 "$BUILD_DIR/pkg/DEBIAN/prerm"

    # Build .deb
    DEB_FILE="$DIST_DIR/${PKG_NAME}_${VERSION}_all.deb"
    dpkg-deb --build --root-owner-group "$BUILD_DIR/pkg" "$DEB_FILE"

    echo "  -> $(du -sh "$DEB_FILE" | cut -f1)  ${DEB_FILE}"

    rm -rf "$BUILD_DIR"

done < "$SCRIPT_DIR/languages.conf"

echo ""
echo "=== All data packages built ==="
