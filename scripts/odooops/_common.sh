#!/usr/bin/env bash
set -euo pipefail

: "${ODOOOPS_API_BASE:?missing ODOOOPS_API_BASE}"
: "${ODOOOPS_TOKEN:?missing ODOOOPS_TOKEN}"
: "${ODOOOPS_PROJECT_ID:?missing ODOOOPS_PROJECT_ID}"

hdr_auth() { printf "Authorization: Bearer %s" "$ODOOOPS_TOKEN"; }
json() { python - <<'PY' "$@"
import json,sys
print(json.dumps(sys.argv[1:]))
PY
}
