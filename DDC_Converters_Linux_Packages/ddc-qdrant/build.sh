#!/bin/bash
#
# Build ddc-qdrant .deb package
# Downloads official Qdrant binary from GitHub and packages it
#
# Usage: ./build.sh [amd64|arm64]
#
set -euo pipefail

QDRANT_VERSION="1.16.3"
ARCH="${1:-amd64}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$(dirname "$SCRIPT_DIR")/dist"
BUILD_DIR="$(mktemp -d)"

trap "rm -rf $BUILD_DIR" EXIT

echo "=== Building ddc-qdrant ${QDRANT_VERSION} (${ARCH}) ==="

# --- Download Qdrant binary ---
case "$ARCH" in
    amd64)
        TARBALL="qdrant-x86_64-unknown-linux-gnu.tar.gz"
        ;;
    arm64)
        TARBALL="qdrant-aarch64-unknown-linux-musl.tar.gz"
        ;;
    *)
        echo "Error: unsupported architecture '$ARCH' (use amd64 or arm64)"
        exit 1
        ;;
esac

DOWNLOAD_URL="https://github.com/qdrant/qdrant/releases/download/v${QDRANT_VERSION}/${TARBALL}"
echo "Downloading: ${DOWNLOAD_URL}"
curl -fSL "$DOWNLOAD_URL" -o "$BUILD_DIR/qdrant.tar.gz"

# Extract binary
tar xzf "$BUILD_DIR/qdrant.tar.gz" -C "$BUILD_DIR"

# --- Assemble package ---
cp -r "$SCRIPT_DIR/root" "$BUILD_DIR/pkg"

# Place binary
cp "$BUILD_DIR/qdrant" "$BUILD_DIR/pkg/usr/bin/qdrant"
chmod 755 "$BUILD_DIR/pkg/usr/bin/qdrant"

# Set correct architecture in control file
sed -i "s/ARCH_PLACEHOLDER/${ARCH}/" "$BUILD_DIR/pkg/DEBIAN/control"

# Set permissions
chmod 755 "$BUILD_DIR/pkg/DEBIAN/postinst"
chmod 755 "$BUILD_DIR/pkg/DEBIAN/prerm"
chmod 755 "$BUILD_DIR/pkg/DEBIAN/postrm"
chmod 644 "$BUILD_DIR/pkg/etc/qdrant/config.yaml"
chmod 644 "$BUILD_DIR/pkg/lib/systemd/system/qdrant.service"

# Calculate installed size (KB)
INSTALLED_SIZE=$(du -sk "$BUILD_DIR/pkg" | cut -f1)
echo "Installed-Size: ${INSTALLED_SIZE}" >> "$BUILD_DIR/pkg/DEBIAN/control"

# --- Build .deb ---
mkdir -p "$DIST_DIR"
DEB_FILE="$DIST_DIR/ddc-qdrant_${QDRANT_VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "$BUILD_DIR/pkg" "$DEB_FILE"

echo ""
echo "Built: $DEB_FILE"
echo "Size:  $(du -sh "$DEB_FILE" | cut -f1)"
