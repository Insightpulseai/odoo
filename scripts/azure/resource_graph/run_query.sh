#!/usr/bin/env bash
# =============================================================================
# Run an Azure Resource Graph query from the catalog
# =============================================================================
# Usage:
#   ./scripts/azure/resource_graph/run_query.sh <query-name> [--output json|table|csv]
#
# Examples:
#   ./scripts/azure/resource_graph/run_query.sh 00_all_resources
#   ./scripts/azure/resource_graph/run_query.sh 20_containerapps_inventory --output json
#   ./scripts/azure/resource_graph/run_query.sh 70_tag_compliance --output csv
#
# Query files are .kql files in queries/ subdirectory.
# Catalog: ssot/runtime/resource-graph-query-catalog.yaml
# Contract: docs/contracts/azure-resource-graph-contract.md (C-36)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
EVIDENCE_DIR="$REPO_ROOT/docs/evidence/$(date +%Y%m%d-%H%M)/resource-graph"

QUERY_NAME="${1:?Usage: $0 <query-name> [--output json|table|csv]}"
OUTPUT_FORMAT="${3:-table}"

# Handle --output flag
if [[ "${2:-}" == "--output" ]]; then
    OUTPUT_FORMAT="${3:-table}"
fi

KQL_FILE="$SCRIPT_DIR/queries/${QUERY_NAME}.kql"

if [[ ! -f "$KQL_FILE" ]]; then
    echo "ERROR: Query file not found: $KQL_FILE"
    echo "Available queries:"
    ls "$SCRIPT_DIR"/queries/*.kql 2>/dev/null | xargs -I{} basename {} .kql
    exit 1
fi

# Check az CLI is available
if ! command -v az &>/dev/null; then
    echo "ERROR: az CLI not found. Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check login status
if ! az account show &>/dev/null; then
    echo "ERROR: Not logged in. Run: az login"
    exit 1
fi

# Read the KQL query
QUERY=$(cat "$KQL_FILE")

echo "=== Running Resource Graph query: $QUERY_NAME ==="
echo "Output format: $OUTPUT_FORMAT"
echo ""

# Execute query
RESULT=$(az graph query -q "$QUERY" --first 1000 -o "$OUTPUT_FORMAT" 2>&1)

echo "$RESULT"

# Optionally save to evidence
if [[ "${SAVE_EVIDENCE:-false}" == "true" ]]; then
    mkdir -p "$EVIDENCE_DIR"
    EVIDENCE_FILE="$EVIDENCE_DIR/${QUERY_NAME}.${OUTPUT_FORMAT}"
    echo "$RESULT" > "$EVIDENCE_FILE"
    echo ""
    echo "Evidence saved to: $EVIDENCE_FILE"
fi
