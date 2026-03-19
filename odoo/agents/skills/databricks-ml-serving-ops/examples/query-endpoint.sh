#!/usr/bin/env bash
# Example: Query a serving endpoint for inference
set -euo pipefail

ENDPOINT_NAME="ipai-classifier-v1"

cat > /tmp/query-input.json <<'INPUT'
{
  "dataframe_records": [
    {"feature_1": 0.5, "feature_2": "category_a", "feature_3": 100}
  ]
}
INPUT

echo "=== Query endpoint ==="
databricks serving-endpoints query --name "${ENDPOINT_NAME}" --json @/tmp/query-input.json
