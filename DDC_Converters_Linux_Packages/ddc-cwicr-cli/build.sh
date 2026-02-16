#!/bin/bash
#
# Build ddc-cwicr-cli .deb package
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$(dirname "$SCRIPT_DIR")/dist"
VERSION="1.0.0"
BUILD_DIR="$(mktemp -d)"

trap "rm -rf $BUILD_DIR" EXIT

echo "=== Building ddc-cwicr-cli ${VERSION} ==="

cp -r "$SCRIPT_DIR/root" "$BUILD_DIR/pkg"

# Set permissions
chmod 755 "$BUILD_DIR/pkg/usr/bin/ddc-search"
chmod 644 "$BUILD_DIR/pkg/etc/ddc-cwicr/config"
chmod 644 "$BUILD_DIR/pkg/DEBIAN/control"

# Build .deb
mkdir -p "$DIST_DIR"
DEB_FILE="$DIST_DIR/ddc-cwicr-cli_${VERSION}_all.deb"
dpkg-deb --build --root-owner-group "$BUILD_DIR/pkg" "$DEB_FILE"

echo "Built: $DEB_FILE"
echo "Size:  $(du -sh "$DEB_FILE" | cut -f1)"
