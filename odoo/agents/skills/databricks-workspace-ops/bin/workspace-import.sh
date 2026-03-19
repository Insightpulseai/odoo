#!/usr/bin/env bash
# databricks-workspace-ops: Import a local file/notebook to workspace
# Usage: workspace-import.sh <local-path> <remote-path> [--profile <profile>]
set -euo pipefail

LOCAL_PATH="${1:?Usage: workspace-import.sh <local-path> <remote-path>}"
REMOTE_PATH="${2:?Usage: workspace-import.sh <local-path> <remote-path>}"
shift 2

databricks workspace import "${LOCAL_PATH}" "${REMOTE_PATH}" --overwrite "$@"
echo "Imported ${LOCAL_PATH} -> ${REMOTE_PATH}"

# Verify
databricks workspace ls "$(dirname "${REMOTE_PATH}")" --output json | grep -q "$(basename "${REMOTE_PATH}")" \
  && echo "VERIFY: OK" || echo "VERIFY: FAIL — object not found after import"
