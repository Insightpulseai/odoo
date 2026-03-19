#!/usr/bin/env bash
# databricks-ml-serving-ops: Model registry operations
# Usage: model-registry-ops.sh <list|get|versions> [--full-name <catalog.schema.model>]
set -euo pipefail

ACTION="${1:?Usage: model-registry-ops.sh <list|get|versions> [--full-name <name>]}"
shift

case "${ACTION}" in
  list)
    databricks registered-models list --output json "$@"
    ;;
  get)
    databricks registered-models get "$@" --output json
    ;;
  versions)
    databricks model-versions list "$@" --output json
    ;;
  *)
    echo "Unknown action: ${ACTION}. Use list|get|versions"
    exit 1
    ;;
esac
