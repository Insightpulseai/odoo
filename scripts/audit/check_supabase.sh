#!/usr/bin/env bash
set -euo pipefail

# Two modes:
# - CLI mode (preferred) if supabase CLI is installed + project is linked
# - API mode if SUPABASE_ACCESS_TOKEN + SUPABASE_PROJECT_REF set

OUT_JSON="${1:-out/supabase_audit.json}"
mkdir -p "$(dirname "$OUT_JSON")"

if command -v supabase >/dev/null 2>&1; then
  # CLI inventory (non-secret)
  funcs="$(supabase functions list --output json 2>/dev/null || echo '[]')"
  migs="$(ls -1 supabase/migrations 2>/dev/null | wc -l | tr -d ' ')"
  python3 - <<'PY' "$OUT_JSON" "$migs" <<<"$funcs"
import json, sys
out_path=sys.argv[1]
migs=int(sys.argv[2])
funcs=json.load(sys.stdin) if sys.stdin.readable() else []
dist={"mode":"cli","migrations_count":migs,"functions":funcs}
open(out_path,"w",encoding="utf-8").write(json.dumps(dist, indent=2))
print(f"Wrote {out_path} (CLI mode)")
PY
  exit 0
fi

: "${SUPABASE_ACCESS_TOKEN:?Set SUPABASE_ACCESS_TOKEN or install supabase CLI}"
: "${SUPABASE_PROJECT_REF:?Set SUPABASE_PROJECT_REF}"

# Management API (surface-level)
projects="$(curl -sS "https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json")"

python3 - <<'PY' "$OUT_JSON" <<<"$projects"
import json, sys
out_path=sys.argv[1]
data=json.load(sys.stdin)
dist={
  "mode":"management_api",
  "id": data.get("id"),
  "name": data.get("name"),
  "region": data.get("region"),
  "created_at": data.get("inserted_at"),
  "db_host": data.get("db_host"),
  "api_url": data.get("api_url") or data.get("rest_url"),
  "status": data.get("status"),
  "raw": data,
}
with open(out_path,"w",encoding="utf-8") as f:
  json.dump(dist, f, indent=2)
print(f"Wrote {out_path} (Management API mode)")
PY
