#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${ROOT}/artifacts/parity"
mkdir -p "$OUT"

echo "== validate schemas =="
node "${ROOT}/scripts/validate_json_schema.mjs" "${ROOT}/kb/parity/capability_schema.json" || true
node "${ROOT}/scripts/validate_json_schema.mjs" "${ROOT}/kb/parity/parity_matrix.schema.json" || true

echo "== run contract tests (placeholder) =="
# TODO: plug real tests: odoo rpc, erpnext endpoints, superset api, n8n webhooks, mattermost api, supabase pg
echo "{\"run_id\":\"$(date +%Y%m%d%H%M%S)\",\"result\":\"noop\"}" > "${OUT}/run.json"
echo "OK"
