#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/_common.sh"

: "${ENV_ID:?missing ENV_ID}"

# TODO: align endpoint to your actual OdooOps implementation
curl -fsS -X POST \
  -H "$(hdr_auth)" \
  "${ODOOOPS_API_BASE}/envs/${ENV_ID}/destroy" >/dev/null

echo "destroyed:${ENV_ID}"
