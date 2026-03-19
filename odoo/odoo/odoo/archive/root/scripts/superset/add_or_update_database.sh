#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"

require_env SUPERSET_BASE_URL SUPERSET_USERNAME SUPERSET_PASSWORD DB_NAME DB_URI

EXPOSE_IN_SQL_LAB="${EXPOSE_IN_SQL_LAB:-true}"
ALLOW_CSV_UPLOAD="${ALLOW_CSV_UPLOAD:-false}"
ALLOW_DML="${ALLOW_DML:-false}"

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

token="$(superset_login "$tmp")"
csrf="$(superset_csrf "$token" "$tmp")"

# Query by database_name
resp="$(api_get "$token" "$csrf" "/api/v1/database/?q=%7B%22filters%22:%5B%7B%22col%22:%22database_name%22,%22opr%22:%22eq%22,%22value%22:%22${DB_NAME}%22%7D%5D%7D" "$tmp")"
db_id="$(python - <<'PY' <<<"$resp"
import json,sys
j=json.load(sys.stdin)
res=j.get("result",[])
print(res[0]["id"] if res else "")
PY
)"

payload="$(cat <<JSON
{
  "database_name": "${DB_NAME}",
  "sqlalchemy_uri": "${DB_URI}",
  "expose_in_sqllab": ${EXPOSE_IN_SQL_LAB},
  "allow_csv_upload": ${ALLOW_CSV_UPLOAD},
  "allow_dml": ${ALLOW_DML},
  "extra": "{\n  \"metadata_cache_timeout\": 300,\n  \"engine_params\": {},\n  \"metadata_params\": {}\n}"
}
JSON
)"

if [[ -n "$db_id" ]]; then
  echo "Updating DB: ${DB_NAME} id=${db_id}"
  api_put "$token" "$csrf" "/api/v1/database/${db_id}" "$payload" "$tmp" >/dev/null
else
  echo "Creating DB: ${DB_NAME}"
  create="$(api_post "$token" "$csrf" "/api/v1/database/" "$payload" "$tmp")"
  db_id="$(python - <<'PY' <<<"$create"
import json,sys
j=json.load(sys.stdin)
print(j.get("id") or j.get("result",{}).get("id") or "")
PY
)"
fi

echo "DB_ID=${db_id}"
