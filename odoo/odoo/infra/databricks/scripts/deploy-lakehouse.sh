#!/usr/bin/env bash
# Deploy ipai-lakehouse DAB bundle to target environment
# Usage: ./scripts/deploy-lakehouse.sh [dev|staging|prod] [--run]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

TARGET="${1:-dev}"
RUN_AFTER="${2:-}"

# Check if databricks CLI is installed
if ! command -v databricks &> /dev/null; then
    echo "ERROR: databricks CLI not found. Install: brew tap databricks/tap && brew install databricks"
    exit 1
fi

# Check authentication
if [ -z "${DATABRICKS_HOST:-}" ] && [ -z "${DATABRICKS_TOKEN:-}" ]; then
    echo "INFO: DATABRICKS_HOST/TOKEN not set, using CLI profile..."
    databricks auth token -p DEFAULT > /dev/null 2>&1 || {
        echo "ERROR: No auth configured. Run: databricks auth login --host https://adb-7405610347978231.11.azuredatabricks.net"
        exit 1
    }
fi

# Validate
echo "==> Validating bundle (target: $TARGET)..."
databricks bundle validate --target "$TARGET"

# Deploy
echo "==> Deploying bundle (target: $TARGET)..."
databricks bundle deploy --target "$TARGET" --auto-approve

echo "==> Deploy complete."
databricks bundle summary --target "$TARGET"

# Optionally run JDBC extract + DLT pipeline
if [ "$RUN_AFTER" = "--run" ]; then
    echo ""
    echo "==> Running JDBC extract job..."
    databricks bundle run --target "$TARGET" odoo_jdbc_extract --no-wait

    echo "==> Triggering finance/BIR DLT pipeline..."
    databricks bundle run --target "$TARGET" finance_bir_pipeline --no-wait

    echo "==> Jobs triggered. Monitor in workspace."
fi
