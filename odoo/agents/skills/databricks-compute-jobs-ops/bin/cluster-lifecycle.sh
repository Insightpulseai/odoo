#!/usr/bin/env bash
# databricks-compute-jobs-ops: Cluster lifecycle operations
# Usage: cluster-lifecycle.sh <list|get|start|stop> [--cluster-id <id>]
set -euo pipefail

ACTION="${1:?Usage: cluster-lifecycle.sh <list|get|start|stop> [--cluster-id <id>]}"
shift

case "${ACTION}" in
  list)
    databricks clusters list --output json "$@"
    ;;
  get)
    databricks clusters get "$@" --output json
    ;;
  start)
    CLUSTER_ID="${1:?--cluster-id required}"
    databricks clusters start --cluster-id "${CLUSTER_ID}"
    echo "Start requested for cluster ${CLUSTER_ID}"
    ;;
  stop)
    CLUSTER_ID="${1:?--cluster-id required}"
    databricks clusters delete --cluster-id "${CLUSTER_ID}"
    echo "Stop requested for cluster ${CLUSTER_ID}"
    ;;
  *)
    echo "Unknown action: ${ACTION}. Use list|get|start|stop"
    exit 1
    ;;
esac
