#!/usr/bin/env bash
set -euo pipefail
# Usage: ./scripts/report_stale_branches.sh [DAYS]
# Lists branches that haven't been updated in N days (default: 14)

DAYS="${1:-14}"

# Fetch latest refs
git fetch origin --prune

# Calculate cutoff timestamp safely (cross-platform)
cutoff="$(date -u -d "$DAYS days ago" +%s 2>/dev/null || python3 - <<PY
import datetime
print(int((datetime.datetime.utcnow()-datetime.timedelta(days=int("$DAYS"))).timestamp()))
PY
)"

echo "=== Stale Branches Report (Older than $DAYS days) ==="
echo "Cutoff Timestamp: $cutoff"
echo "----------------------------------------------------"

# List branches older than cutoff
git for-each-ref --format='%(committerdate:unix) %(refname:short)' refs/remotes/origin \
  | awk -v c="$cutoff" '$1 < c {print $0}' \
  | sed 's|refs/remotes/origin/||' \
  | rg -v '^(origin/main|origin/HEAD|main|HEAD)$' \
  | sort -n

echo "----------------------------------------------------"
