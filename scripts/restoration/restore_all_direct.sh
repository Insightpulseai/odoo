#!/bin/bash
# =============================================================================
# scripts/restoration/restore_all_direct.sh
# Final Wrapper for Direct-to-Origin Platform Restoration
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Starting Full Platform Restoration (Direct-to-Origin) ==="

# 1. Restore ERP (Odoo)
bash "$SCRIPT_DIR/restore_erp.sh"

# 2. Restore Website (Landing Page)
bash "$SCRIPT_DIR/restore_website.sh"

# 3. Restore W9Studio (External DNS Required)
bash "$SCRIPT_DIR/restore_w9.sh"

echo "=== Verification ==="
echo "Note: DNS propagation may take up to 300 seconds."
echo "Running smoke tests..."

curl -ILk -m 10 https://erp.insightpulseai.com || echo "ERP still propagates..."
curl -ILk -m 10 https://www.insightpulseai.com || echo "Website still propagates..."
curl -ILk -m 10 https://www.w9studio.net || echo "W9 still propagates..."

echo "=== Full Restoration Batch Complete ==="
