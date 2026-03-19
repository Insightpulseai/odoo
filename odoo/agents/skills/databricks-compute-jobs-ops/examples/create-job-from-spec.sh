#!/usr/bin/env bash
# Example: Create a job from a JSON specification
set -euo pipefail

cat > /tmp/job-spec.json <<'SPEC'
{
  "name": "ipai-etl-daily",
  "tasks": [
    {
      "task_key": "ingest",
      "notebook_task": {
        "notebook_path": "/Repos/ipai/lakehouse/notebooks/ingest_daily"
      },
      "new_cluster": {
        "spark_version": "15.4.x-scala2.12",
        "num_workers": 2,
        "node_type_id": "Standard_DS3_v2"
      }
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 6 * * ?",
    "timezone_id": "Asia/Manila"
  }
}
SPEC

echo "=== Create job ==="
databricks jobs create --json @/tmp/job-spec.json --output json

echo "=== List jobs ==="
databricks jobs list --output json | python3 -c "import sys,json; [print(f'{j[\"job_id\"]}: {j[\"settings\"][\"name\"]}') for j in json.load(sys.stdin)['jobs']]"
