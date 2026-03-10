#!/usr/bin/env bash
# Start an Azure Container App Job and poll until completion
set -euo pipefail

: "${RG:?RG required}"
: "${JOB_NAME:?JOB_NAME required}"

MAX_POLLS="${MAX_POLLS:-24}"
POLL_INTERVAL="${POLL_INTERVAL:-15}"

# Start the job
EXEC=$(az containerapp job start -n "$JOB_NAME" -g "$RG" --query name -o tsv)
echo "Started execution: $EXEC"

# Poll until terminal state
for i in $(seq 1 "$MAX_POLLS"); do
  STATUS=$(az containerapp job execution show \
    -n "$JOB_NAME" -g "$RG" \
    --job-execution-name "$EXEC" \
    --query "properties.status" -o tsv 2>/dev/null || echo "Unknown")

  echo "$(date +%H:%M:%S) Poll $i/$MAX_POLLS: $STATUS"

  case "$STATUS" in
    Succeeded)
      echo "PASS: job completed successfully"
      exit 0
      ;;
    Failed)
      echo "FAIL: job failed — check logs:" >&2
      echo "  az containerapp job logs show -n $JOB_NAME -g $RG --execution $EXEC" >&2
      exit 1
      ;;
  esac

  sleep "$POLL_INTERVAL"
done

echo "FAIL: timed out after $((MAX_POLLS * POLL_INTERVAL))s" >&2
exit 1
