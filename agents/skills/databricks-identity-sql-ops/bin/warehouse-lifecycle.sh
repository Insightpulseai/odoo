#!/usr/bin/env bash
# databricks-identity-sql-ops: SQL warehouse lifecycle
# Usage: warehouse-lifecycle.sh <list|get|start|stop> [--id <id>]
set -euo pipefail

ACTION="${1:?Usage: warehouse-lifecycle.sh <list|get|start|stop> [--id <id>]}"
shift

case "${ACTION}" in
  list)
    databricks warehouses list --output json "$@"
    ;;
  get)
    databricks warehouses get "$@" --output json
    ;;
  start)
    databricks warehouses start "$@"
    echo "Warehouse start requested"
    ;;
  stop)
    databricks warehouses stop "$@"
    echo "Warehouse stop requested"
    ;;
  *)
    echo "Unknown action: ${ACTION}. Use list|get|start|stop"
    exit 1
    ;;
esac
