#!/usr/bin/env bash
# Example: verification after any operation
set -euo pipefail

# Replace with actual health/status check
STATUS=$(TOOL_NAME=mycli ./bin/tool-safe status --output json | jq -r '.state')

if [[ "$STATUS" = "healthy" ]]; then
  echo "PASS: resource is healthy"
  exit 0
else
  echo "FAIL: resource state is '$STATUS'" >&2
  exit 1
fi
