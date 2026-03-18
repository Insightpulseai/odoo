#!/usr/bin/env bash
set -euo pipefail

: "${VERCEL_TOKEN:?Set VERCEL_TOKEN}"
TEAM_QS=""
if [ -n "${VERCEL_TEAM_ID:-}" ]; then
  TEAM_QS="&teamId=${VERCEL_TEAM_ID}"
fi

OUT_JSON="${1:-out/vercel_audit.json}"
mkdir -p "$(dirname "$OUT_JSON")"

api() {
  local path="$1"
  curl -sS "https://api.vercel.com${path}" \
    -H "Authorization: Bearer ${VERCEL_TOKEN}"
}

# Inventory: projects + integrations are separate concepts; this grabs projects + env summary hooks.
projects="$(api "/v9/projects?limit=100${TEAM_QS}")"

# Basic distillation
python3 - <<'PY' "$OUT_JSON" <<<"$projects"
import json, sys
out_path=sys.argv[1]
data=json.load(sys.stdin)
proj=data.get("projects", [])
dist={
  "project_count": len(proj),
  "projects": [
    {
      "name": p.get("name"),
      "id": p.get("id"),
      "framework": p.get("framework"),
      "createdAt": p.get("createdAt"),
      "updatedAt": p.get("updatedAt"),
      "link": p.get("link"),
      "targets": p.get("targets"),
    } for p in proj
  ],
  "raw": data
}
with open(out_path,"w",encoding="utf-8") as f:
  json.dump(dist, f, indent=2)
print(f"Wrote {out_path}")
PY
