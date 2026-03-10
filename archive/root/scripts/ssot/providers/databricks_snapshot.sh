#!/usr/bin/env bash
# shellcheck disable=SC2086
set -euo pipefail
###############################################################################
# Databricks Snapshot Provider
#
# Collects workspace metadata from Databricks via REST API.
# Requires: DATABRICKS_HOST, DATABRICKS_TOKEN environment variables.
#
# Output: ssot/databricks/*.snapshot.json (gitignored, CI artifacts only)
#
# Usage:
#   bash scripts/ssot/providers/databricks_snapshot.sh
#   bash scripts/ssot/providers/databricks_snapshot.sh --clusters-only
#   bash scripts/ssot/providers/databricks_snapshot.sh --jobs-only
###############################################################################

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT_DIR="${REPO_ROOT}/ssot/databricks"
mkdir -p "${OUT_DIR}"

# ── Pre-flight ──────────────────────────────────────────────────────────────
if [[ -z "${DATABRICKS_HOST:-}" ]]; then
  echo "SKIP: DATABRICKS_HOST not set — Databricks snapshot disabled"
  echo '{"skipped":true,"reason":"DATABRICKS_HOST not set"}' > "${OUT_DIR}/workspace.snapshot.json"
  exit 0
fi

if [[ -z "${DATABRICKS_TOKEN:-}" ]]; then
  echo "SKIP: DATABRICKS_TOKEN not set — Databricks snapshot disabled"
  echo '{"skipped":true,"reason":"DATABRICKS_TOKEN not set"}' > "${OUT_DIR}/workspace.snapshot.json"
  exit 0
fi

HOST="${DATABRICKS_HOST}"
AUTH="Authorization: Bearer ${DATABRICKS_TOKEN}"

FLAG="${1:-all}"

dbx_api() {
  local endpoint="$1"
  local out_file="$2"
  echo "  → GET ${endpoint}"
  if ! curl -sf -H "${AUTH}" "${HOST}/api/2.0/${endpoint}" -o "${out_file}" 2>/dev/null; then
    echo "    WARN: ${endpoint} failed or empty"
    echo '{"error":"API call failed","endpoint":"'"${endpoint}"'"}' > "${out_file}"
  fi
}

# ── Clusters ────────────────────────────────────────────────────────────────
if [[ "${FLAG}" == "all" || "${FLAG}" == "--clusters-only" ]]; then
  echo "Layer 1: Clusters"
  dbx_api "clusters/list" "${OUT_DIR}/clusters.snapshot.json"
fi

# ── Jobs ────────────────────────────────────────────────────────────────────
if [[ "${FLAG}" == "all" || "${FLAG}" == "--jobs-only" ]]; then
  echo "Layer 2: Jobs"
  dbx_api "jobs/list?limit=100" "${OUT_DIR}/jobs.snapshot.json"
fi

# ── Workspace (notebooks/folders) ──────────────────────────────────────────
if [[ "${FLAG}" == "all" ]]; then
  echo "Layer 3: Workspace"
  dbx_api "workspace/list?path=/" "${OUT_DIR}/workspace.snapshot.json"
fi

# ── SQL Warehouses ──────────────────────────────────────────────────────────
if [[ "${FLAG}" == "all" ]]; then
  echo "Layer 4: SQL Warehouses"
  dbx_api "sql/warehouses" "${OUT_DIR}/sql-warehouses.snapshot.json"
fi

# ── Unity Catalog schemas ───────────────────────────────────────────────────
if [[ "${FLAG}" == "all" ]]; then
  echo "Layer 5: Unity Catalog"
  dbx_api "unity-catalog/catalogs" "${OUT_DIR}/catalogs.snapshot.json"
fi

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "Databricks snapshot complete."
echo "Files written to: ${OUT_DIR}/"
ls -la "${OUT_DIR}/"*.snapshot.json 2>/dev/null | wc -l | xargs -I{} echo "  {} snapshot files"
