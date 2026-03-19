#!/usr/bin/env bash
# Example: Pipeline (DLT/SDP) operations
set -euo pipefail

echo "=== List pipelines ==="
databricks pipelines list --output json

echo "=== Get pipeline details ==="
# databricks pipelines get --pipeline-id <id> --output json
# Uncomment with actual pipeline ID

echo "=== Start pipeline update ==="
# databricks pipelines start --pipeline-id <id>
# Uncomment with actual pipeline ID
