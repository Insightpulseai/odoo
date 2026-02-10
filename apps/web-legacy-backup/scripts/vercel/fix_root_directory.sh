#!/usr/bin/env bash
set -euo pipefail

: "${VERCEL_TOKEN:?Set VERCEL_TOKEN (Vercel Personal Token)}"

TEAM_ID="${TEAM_ID:-team_wphKJ7lHA3QiZu6VgcotQBQM}"
PROJECT_ID="${PROJECT_ID:-prj_PFdFRARO9YQ0CRBkuwp5jAbfKYwe}"
ROOT_DIR="${ROOT_DIR:-apps/web}"

api() {
  curl -fsS \
    -H "Authorization: Bearer ${VERCEL_TOKEN}" \
    -H "Content-Type: application/json" \
    "$@"
}

echo "[1/2] PATCH project rootDirectory -> ${ROOT_DIR}"
api -X PATCH "https://api.vercel.com/v9/projects/${PROJECT_ID}?teamId=${TEAM_ID}" \
  -d "{\"rootDirectory\":\"${ROOT_DIR}\"}" >/tmp/vercel_patch_project.json

echo "[2/2] GET project to confirm"
api "https://api.vercel.com/v9/projects/${PROJECT_ID}?teamId=${TEAM_ID}" >/tmp/vercel_get_project.json

# best-effort confirmation output
node -e '
const fs=require("fs");
const p=JSON.parse(fs.readFileSync("/tmp/vercel_get_project.json","utf8"));
console.log("project:", p.name || p.id);
console.log("rootDirectory:", p.rootDirectory || "(missing field in response)");
'
echo "OK"
