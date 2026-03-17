#!/usr/bin/env bash
# databricks-ml-serving-ops: Serving endpoint lifecycle
# Usage: serving-endpoint-lifecycle.sh <list|get|query|delete> [--name <name>] [--json <input>]
set -euo pipefail

ACTION="${1:?Usage: serving-endpoint-lifecycle.sh <list|get|query|delete> [--name <name>]}"
shift

case "${ACTION}" in
  list)
    databricks serving-endpoints list --output json "$@"
    ;;
  get)
    databricks serving-endpoints get "$@" --output json
    ;;
  query)
    databricks serving-endpoints query "$@"
    ;;
  delete)
    NAME="${2:?--name required for delete}"
    echo "WARNING: Deleting serving endpoint ${NAME}"
    databricks serving-endpoints delete --name "${NAME}"
    echo "Deleted endpoint ${NAME}"
    ;;
  *)
    echo "Unknown action: ${ACTION}. Use list|get|query|delete"
    exit 1
    ;;
esac
