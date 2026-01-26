#!/usr/bin/env bash
# pull_enterprise_audit.sh - Pull enterprise audit log events
# Usage: ./scripts/github/pull_enterprise_audit.sh [output_file]
# Requires: ENTERPRISE_SLUG, SINCE env vars
set -euo pipefail

: "${ENTERPRISE_SLUG:?set ENTERPRISE_SLUG environment variable}"
: "${SINCE:?set SINCE environment variable (e.g., 2026-01-01)}"

output_file="${1:-/tmp/gh_audit_$(date +%Y%m%d_%H%M%S).json}"

echo "==> Pulling enterprise audit log"
echo "    Enterprise: $ENTERPRISE_SLUG"
echo "    Since: $SINCE"
echo "    Output: $output_file"

# Pull audit events since date
# NOTE: Requires enterprise-admin scope on GH_TOKEN
if gh api "enterprises/$ENTERPRISE_SLUG/audit-log?phrase=created:>=$SINCE&per_page=100" \
  -H "Accept: application/vnd.github+json" \
  > "$output_file" 2>&1; then

  event_count="$(jq 'length' "$output_file" 2>/dev/null || echo "0")"
  echo "    ✓ Retrieved $event_count events"
  echo ""
  echo "Output written to: $output_file"

  # Show summary of event types
  if [[ "$event_count" -gt 0 ]]; then
    echo ""
    echo "Event type summary:"
    jq -r '.[].action' "$output_file" | sort | uniq -c | sort -rn | head -10
  fi
else
  echo "    ✗ Failed to pull audit log"
  echo "    Check that GH_TOKEN has enterprise-admin scope"
  exit 1
fi

echo ""
echo "OK: Audit log pulled successfully."
