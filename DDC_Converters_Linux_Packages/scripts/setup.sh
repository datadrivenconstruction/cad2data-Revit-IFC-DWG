#!/bin/bash
set -euo pipefail

echo "=== DDC Package Analytics Setup ==="
echo ""

# Step 1: Create D1 Database
echo "1. Creating D1 Database..."
wrangler d1 create ddc-pkg-analytics-db
echo ""
echo "   IMPORTANT: Copy the 'database_id' from above into:"
echo "   - worker/wrangler.toml"
echo "   - dashboard/wrangler.toml"
echo ""
read -p "   Press Enter after updating wrangler.toml files..."

# Step 2: Run migrations
echo "2. Running D1 Migrations..."
cd "$(dirname "$0")/../worker"
wrangler d1 migrations apply ddc-pkg-analytics-db --remote
echo "   Migrations applied successfully."

# Step 3: Install dependencies
echo "3. Installing Worker dependencies..."
npm install

echo "4. Installing Dashboard dependencies..."
cd ../dashboard
npm install

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Deploy the worker:     cd worker && wrangler deploy"
echo "  2. Deploy the dashboard:  cd dashboard && wrangler pages deploy public --project-name ddc-pkg-dashboard"
echo "  3. Set dashboard secret:  wrangler pages secret put API_TOKEN --project-name ddc-pkg-dashboard"
echo "  4. (Optional) Add custom domain: analytics.datadrivenconstruction.io"
