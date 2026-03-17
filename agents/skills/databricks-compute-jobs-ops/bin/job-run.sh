#!/usr/bin/env bash
# databricks-compute-jobs-ops: Trigger a job and wait for completion
# Usage: job-run.sh <job-id> [--timeout <seconds>]
set -euo pipefail

JOB_ID="${1:?Usage: job-run.sh <job-id> [--timeout <seconds>]}"
TIMEOUT="${3:-600}"

echo "Triggering job ${JOB_ID}..."
RUN_ID=$(databricks jobs run-now --job-id "${JOB_ID}" --output json | python3 -c "import sys,json; print(json.load(sys.stdin)['run_id'])")
echo "Run started: ${RUN_ID}"

ELAPSED=0
while [ "${ELAPSED}" -lt "${TIMEOUT}" ]; do
  STATE=$(databricks runs get --run-id "${RUN_ID}" --output json | python3 -c "import sys,json; d=json.load(sys.stdin)['state']; print(d['life_cycle_state'])")
  if [ "${STATE}" = "TERMINATED" ]; then
    RESULT=$(databricks runs get --run-id "${RUN_ID}" --output json | python3 -c "import sys,json; print(json.load(sys.stdin)['state']['result_state'])")
    echo "Run ${RUN_ID} completed: ${RESULT}"
    [ "${RESULT}" = "SUCCESS" ] && exit 0 || exit 1
  fi
  echo "State: ${STATE} (${ELAPSED}s elapsed)"
  sleep 15
  ELAPSED=$((ELAPSED + 15))
done

echo "TIMEOUT: Run ${RUN_ID} did not complete within ${TIMEOUT}s"
exit 2
