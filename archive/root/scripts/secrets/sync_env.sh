#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Environment-scoped Supabase Edge secret sync
#
# Usage:
#   ENVIRONMENT=staging ./scripts/secrets/sync_env.sh
#   ENVIRONMENT=prod ./scripts/secrets/sync_env.sh
#
# Requirements:
#   - ENVIRONMENT: must be 'staging' or 'prod'
#   - SUPABASE_PROJECT_REF: Supabase project reference
#   - STAGE__* or PROD__* env vars matching registry entries
# =============================================================================

ENVIRONMENT="${ENVIRONMENT:-}"
if [[ -z "${ENVIRONMENT}" ]]; then
  echo "ERROR: ENVIRONMENT must be set to 'staging' or 'prod'" >&2
  echo "Usage: ENVIRONMENT=staging ./scripts/secrets/sync_env.sh" >&2
  exit 2
fi

case "${ENVIRONMENT}" in
  staging|stage) PREFIX="STAGE__" ;;
  prod|production) PREFIX="PROD__" ;;
  *)
    echo "ERROR: ENVIRONMENT must be 'staging' or 'prod' (got: ${ENVIRONMENT})" >&2
    exit 2
    ;;
esac

: "${SUPABASE_PROJECT_REF:?set SUPABASE_PROJECT_REF}"

# Validate registry structure (must exist in your repo already)
if [[ -x "./scripts/secrets/validate_registry.py" ]]; then
  echo "==> Validating registry structure"
  ./scripts/secrets/validate_registry.py >/dev/null
else
  echo "ERROR: missing scripts/secrets/validate_registry.py" >&2
  exit 3
fi

# Extract supabase_edge secrets from registry matching the prefix.
# NOTE: Requires PyYAML (should already be installed for validator)
echo "==> Extracting ${PREFIX} secrets from registry"
SECRETS="$(
python3 - <<'PY'
import os, sys
try:
    import yaml
except Exception as e:
    print("ERROR: PyYAML not available (pip install pyyaml)", file=sys.stderr)
    sys.exit(4)

prefix=os.environ["PREFIX"]
path="infra/secrets/registry.yaml"
data=yaml.safe_load(open(path,"r",encoding="utf-8")) or {}
items=data.get("secrets", []) or []
out=[]
for s in items:
    name=(s or {}).get("name","")
    store=(s or {}).get("store","")
    if store=="supabase_edge_secrets" and name.startswith(prefix):
        out.append(name)
print("\n".join(out))
PY
)"

if [[ -z "${SECRETS}" ]]; then
  echo "ERROR: No supabase_edge secrets found in registry for prefix ${PREFIX}" >&2
  exit 5
fi

echo "==> Syncing Supabase Edge secrets for ENVIRONMENT=${ENVIRONMENT} (prefix=${PREFIX})"
echo ""

SUCCESS_COUNT=0
TOTAL_COUNT=0

while IFS= read -r key; do
  [[ -z "${key}" ]] && continue
  ((TOTAL_COUNT++))

  val="${!key:-}"
  if [[ -z "${val}" ]]; then
    echo "  ❌ ${key}: env var not set"
    continue
  fi

  # Never print the value; suppress stdout.
  if supabase secrets set "${key}=${val}" --project-ref "${SUPABASE_PROJECT_REF}" >/dev/null 2>&1; then
    echo "  ✅ ${key}"
    ((SUCCESS_COUNT++))
  else
    echo "  ❌ ${key}: sync failed"
  fi
done <<< "${SECRETS}"

echo ""
echo "==> Summary: ${SUCCESS_COUNT}/${TOTAL_COUNT} secrets synced successfully"

if [[ "${SUCCESS_COUNT}" -ne "${TOTAL_COUNT}" ]]; then
  echo "ERROR: Some secrets failed to sync" >&2
  exit 6
fi

echo "==> Done."
