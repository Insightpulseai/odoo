#!/usr/bin/env bash
# databricks-identity-sql-ops: Identity operations (users, groups, service principals)
# Usage: identity-ops.sh <users|groups|service-principals> <list|get> [--id <id>]
set -euo pipefail

ENTITY="${1:?Usage: identity-ops.sh <users|groups|service-principals> <list|get> [--id <id>]}"
ACTION="${2:?Usage: identity-ops.sh <entity> <list|get> [--id <id>]}"
shift 2

case "${ENTITY}" in
  users)
    databricks users "${ACTION}" "$@" --output json
    ;;
  groups)
    databricks groups "${ACTION}" "$@" --output json
    ;;
  service-principals)
    databricks service-principals "${ACTION}" "$@" --output json
    ;;
  *)
    echo "Unknown entity: ${ENTITY}. Use users|groups|service-principals"
    exit 1
    ;;
esac
