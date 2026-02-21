#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Deploying DDC Package Analytics ==="
echo ""

# Deploy Worker
echo "1. Deploying Worker..."
cd "$ROOT_DIR/worker"
npm install
wrangler deploy
echo "   Worker deployed to pkg.datadrivenconstruction.io"
echo ""

# Deploy Dashboard
echo "2. Deploying Dashboard..."
cd "$ROOT_DIR/dashboard"
npm install
wrangler pages deploy public --project-name ddc-pkg-dashboard
echo "   Dashboard deployed."
echo ""

echo "=== Deployment Complete ==="
echo ""
echo "Worker:    https://pkg.datadrivenconstruction.io"
echo "Dashboard: https://ddc-pkg-dashboard.pages.dev"
echo ""
echo "To set/update dashboard API token:"
echo "  wrangler pages secret put API_TOKEN --project-name ddc-pkg-dashboard"
