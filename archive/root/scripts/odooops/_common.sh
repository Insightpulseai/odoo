#!/usr/bin/env bash
set -euo pipefail

# Legacy API config (deprecated, kept for backward compatibility)
: "${ODOOOPS_API_BASE:=}"
: "${ODOOOPS_TOKEN:=}"
: "${ODOOOPS_PROJECT_ID:=}"

# Supabase config (new primary method)
: "${SUPABASE_URL:?missing SUPABASE_URL}"
: "${SUPABASE_ANON_KEY:?missing SUPABASE_ANON_KEY}"
: "${SUPABASE_SERVICE_ROLE_KEY:?missing SUPABASE_SERVICE_ROLE_KEY}"

# Legacy helper (deprecated)
hdr_auth() {
  if [[ -n "${ODOOOPS_TOKEN}" ]]; then
    printf "Authorization: Bearer %s" "$ODOOOPS_TOKEN"
  else
    echo "Warning: ODOOOPS_TOKEN not set, legacy API calls will fail" >&2
    printf "Authorization: Bearer invalid"
  fi
}

# JSON helper
json() {
  python - <<'PY' "$@"
import json,sys
print(json.dumps(sys.argv[1:]))
PY
}
