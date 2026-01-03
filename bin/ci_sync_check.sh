#!/bin/bash
set -e

echo "=== CI Sync Check ==="
echo "Ensuring all generated artifacts are in sync with their sources."

# 1. Finance Close Seed Drift
echo "--- [1/2] Checking Finance Close Seed Drift ---"
# Regenerate seed to temp path or in-place? 
# Usually in-place and check for git changes.
python3 scripts/seed_finance_close_from_xlsx.py

if [ -n "$(git status --porcelain addons/ipai/ipai_finance_close_seed)" ]; then
    echo "FAIL: Drift detected in ipai_finance_close_seed!"
    echo "Run 'python3 scripts/seed_finance_close_from_xlsx.py' and commit changes."
    git status addons/ipai/ipai_finance_close_seed
    exit 1
fi

# 2. Copilot Index Drift
echo "--- [2/2] Checking Copilot Index Drift ---"
./bin/copilot_drift_check.sh

echo "✅ All Sync Checks Passed."
