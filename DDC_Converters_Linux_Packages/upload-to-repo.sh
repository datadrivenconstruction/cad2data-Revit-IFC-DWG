#!/bin/bash
#
# Upload built .deb packages to DDC APT repository (Cloudflare R2)
# and regenerate the Packages/Release index files.
#
# Prerequisites:
#   - wrangler CLI installed and authenticated
#   - CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID set
#   - Packages built in dist/ (run build-all.sh first)
#
# Usage: ./upload-to-repo.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
BUCKET="ddc-packages"
JURISDICTION="eu"
REPO_PREFIX="pool/main/d"
WORK_DIR="$(mktemp -d)"

trap "rm -rf $WORK_DIR" EXIT

# Verify wrangler is available
if ! command -v wrangler &>/dev/null && ! command -v npx &>/dev/null; then
    echo "Error: wrangler CLI not found. Install with: npm install -g wrangler"
    exit 1
fi

WRANGLER="${WRANGLER_CMD:-npx wrangler}"

echo "╔══════════════════════════════════════════════╗"
echo "║   DDC APT Repository Uploader                ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# --- Upload .deb files ---
echo "=== Uploading .deb packages to R2 ==="
echo ""

for DEB_FILE in "$DIST_DIR"/*.deb; do
    [ -f "$DEB_FILE" ] || continue

    FILENAME="$(basename "$DEB_FILE")"
    PKG_NAME="$(echo "$FILENAME" | sed 's/_.*$//')"

    R2_KEY="${REPO_PREFIX}/${PKG_NAME}/${FILENAME}"

    echo "  Uploading: ${FILENAME}"
    echo "  -> s3://${BUCKET}/${R2_KEY}"

    $WRANGLER r2 object put "${BUCKET}/${R2_KEY}" \
        --file "$DEB_FILE" \
        --content-type "application/vnd.debian.binary-package" \
        --jurisdiction "$JURISDICTION" \
        2>/dev/null

    echo "  Done."
    echo ""
done

# --- Regenerate Packages index ---
echo "=== Generating APT repository index ==="
echo ""

# Download existing Packages file (to merge with new entries)
echo "Downloading current Packages index..."
PACKAGES_FILE="$WORK_DIR/Packages"
curl -sf "https://pkg.datadrivenconstruction.io/dists/stable/main/binary-amd64/Packages" \
    -o "$PACKAGES_FILE" 2>/dev/null || touch "$PACKAGES_FILE"

# Remove old entries for packages we're uploading
for DEB_FILE in "$DIST_DIR"/*.deb; do
    [ -f "$DEB_FILE" ] || continue
    PKG_NAME="$(dpkg-deb -f "$DEB_FILE" Package)"

    # Remove existing entry for this package name
    python3 -c "
import sys
blocks = open('$PACKAGES_FILE').read().split('\n\n')
filtered = [b for b in blocks if b.strip() and not any(
    line.startswith('Package: $PKG_NAME') for line in b.split('\n')
)]
with open('$PACKAGES_FILE', 'w') as f:
    f.write('\n\n'.join(filtered))
    if filtered:
        f.write('\n\n')
" 2>/dev/null || true
done

# Generate new entries for uploaded packages
for DEB_FILE in "$DIST_DIR"/*.deb; do
    [ -f "$DEB_FILE" ] || continue

    FILENAME="$(basename "$DEB_FILE")"
    PKG_NAME="$(echo "$FILENAME" | sed 's/_.*$//')"
    R2_KEY="${REPO_PREFIX}/${PKG_NAME}/${FILENAME}"

    # Extract control info
    dpkg-deb -f "$DEB_FILE" >> "$PACKAGES_FILE"
    echo "Filename: ${R2_KEY}" >> "$PACKAGES_FILE"
    echo "Size: $(stat -c %s "$DEB_FILE")" >> "$PACKAGES_FILE"
    echo "SHA256: $(sha256sum "$DEB_FILE" | cut -d' ' -f1)" >> "$PACKAGES_FILE"
    echo "SHA1: $(sha1sum "$DEB_FILE" | cut -d' ' -f1)" >> "$PACKAGES_FILE"
    echo "MD5sum: $(md5sum "$DEB_FILE" | cut -d' ' -f1)" >> "$PACKAGES_FILE"
    echo "" >> "$PACKAGES_FILE"

    echo "  Added to index: ${PKG_NAME}"
done

# Also generate arm64 Packages (for arch:all packages)
PACKAGES_ARM64="$WORK_DIR/Packages.arm64"
curl -sf "https://pkg.datadrivenconstruction.io/dists/stable/main/binary-arm64/Packages" \
    -o "$PACKAGES_ARM64" 2>/dev/null || touch "$PACKAGES_ARM64"

# Add arch:all packages to arm64 index too
for DEB_FILE in "$DIST_DIR"/*_all.deb; do
    [ -f "$DEB_FILE" ] || continue

    FILENAME="$(basename "$DEB_FILE")"
    PKG_NAME="$(echo "$FILENAME" | sed 's/_.*$//')"
    R2_KEY="${REPO_PREFIX}/${PKG_NAME}/${FILENAME}"

    # Remove old entry
    python3 -c "
import sys
blocks = open('$PACKAGES_ARM64').read().split('\n\n')
filtered = [b for b in blocks if b.strip() and not any(
    line.startswith('Package: $PKG_NAME') for line in b.split('\n')
)]
with open('$PACKAGES_ARM64', 'w') as f:
    f.write('\n\n'.join(filtered))
    if filtered:
        f.write('\n\n')
" 2>/dev/null || true

    dpkg-deb -f "$DEB_FILE" >> "$PACKAGES_ARM64"
    echo "Filename: ${R2_KEY}" >> "$PACKAGES_ARM64"
    echo "Size: $(stat -c %s "$DEB_FILE")" >> "$PACKAGES_ARM64"
    echo "SHA256: $(sha256sum "$DEB_FILE" | cut -d' ' -f1)" >> "$PACKAGES_ARM64"
    echo "SHA1: $(sha1sum "$DEB_FILE" | cut -d' ' -f1)" >> "$PACKAGES_ARM64"
    echo "MD5sum: $(md5sum "$DEB_FILE" | cut -d' ' -f1)" >> "$PACKAGES_ARM64"
    echo "" >> "$PACKAGES_ARM64"
done

# Compress Packages
gzip -9 -k "$PACKAGES_FILE"
gzip -9 -k "$PACKAGES_ARM64"

echo ""

# --- Upload Packages index files ---
echo "=== Uploading index files ==="

for ARCH_DIR in "binary-amd64" "binary-arm64"; do
    if [ "$ARCH_DIR" = "binary-amd64" ]; then
        SRC="$PACKAGES_FILE"
    else
        SRC="$PACKAGES_ARM64"
    fi

    $WRANGLER r2 object put "${BUCKET}/dists/stable/main/${ARCH_DIR}/Packages" \
        --file "$SRC" \
        --content-type "text/plain" \
        --jurisdiction "$JURISDICTION" \
        2>/dev/null

    $WRANGLER r2 object put "${BUCKET}/dists/stable/main/${ARCH_DIR}/Packages.gz" \
        --file "${SRC}.gz" \
        --content-type "application/gzip" \
        --jurisdiction "$JURISDICTION" \
        2>/dev/null

    echo "  Updated: dists/stable/main/${ARCH_DIR}/Packages"
done

# --- Generate and upload Release file ---
echo ""
echo "=== Generating Release file ==="

RELEASE_FILE="$WORK_DIR/Release"
cat > "$RELEASE_FILE" << EOF
Origin: DataDrivenConstruction
Label: DDC Package Repository
Suite: stable
Codename: stable
Architectures: amd64 arm64
Components: main
Description: Data Driven Construction Linux packages
Date: $(date -u '+%a, %d %b %Y %H:%M:%S UTC')
EOF

# Add checksums
for ARCH_DIR in "binary-amd64" "binary-arm64"; do
    if [ "$ARCH_DIR" = "binary-amd64" ]; then
        SRC="$PACKAGES_FILE"
    else
        SRC="$PACKAGES_ARM64"
    fi

    echo "SHA256:" >> "$RELEASE_FILE"
    echo " $(sha256sum "$SRC" | cut -d' ' -f1) $(stat -c %s "$SRC") main/${ARCH_DIR}/Packages" >> "$RELEASE_FILE"
    echo " $(sha256sum "${SRC}.gz" | cut -d' ' -f1) $(stat -c %s "${SRC}.gz") main/${ARCH_DIR}/Packages.gz" >> "$RELEASE_FILE"
done

$WRANGLER r2 object put "${BUCKET}/dists/stable/Release" \
    --file "$RELEASE_FILE" \
    --content-type "text/plain" \
    --jurisdiction "$JURISDICTION" \
    2>/dev/null

echo "  Updated: dists/stable/Release"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Upload Complete                            ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Repository: https://pkg.datadrivenconstruction.io"
echo ""
echo "Users can now install:"
echo "  sudo apt update"
echo "  sudo apt install ddc-cwicr-en"
echo ""
