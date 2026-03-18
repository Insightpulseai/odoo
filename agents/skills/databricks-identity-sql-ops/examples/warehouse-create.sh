#!/usr/bin/env bash
# Example: Create a SQL warehouse
set -euo pipefail

cat > /tmp/warehouse-spec.json <<'SPEC'
{
  "name": "ipai-analytics",
  "cluster_size": "2X-Small",
  "min_num_clusters": 1,
  "max_num_clusters": 2,
  "auto_stop_mins": 30,
  "warehouse_type": "PRO",
  "enable_serverless_compute": false,
  "tags": {
    "custom_tags": [
      {"key": "team", "value": "ipai"},
      {"key": "env", "value": "dev"}
    ]
  }
}
SPEC

echo "=== Create SQL warehouse ==="
databricks warehouses create --json @/tmp/warehouse-spec.json --output json

echo "=== List warehouses ==="
databricks warehouses list --output json
