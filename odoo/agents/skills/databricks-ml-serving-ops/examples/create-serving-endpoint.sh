#!/usr/bin/env bash
# Example: Create a model serving endpoint
set -euo pipefail

cat > /tmp/endpoint-spec.json <<'SPEC'
{
  "name": "ipai-classifier-v1",
  "config": {
    "served_entities": [
      {
        "entity_name": "main.ml.ipai_classifier",
        "entity_version": "1",
        "workload_size": "Small",
        "scale_to_zero_enabled": true
      }
    ],
    "traffic_config": {
      "routes": [
        {
          "served_model_name": "ipai_classifier-1",
          "traffic_percentage": 100
        }
      ]
    }
  }
}
SPEC

echo "=== Create serving endpoint ==="
databricks serving-endpoints create --json @/tmp/endpoint-spec.json --output json

echo "=== Check endpoint readiness ==="
# Poll until ready
# databricks serving-endpoints get --name ipai-classifier-v1 --output json | jq '.state.ready'
