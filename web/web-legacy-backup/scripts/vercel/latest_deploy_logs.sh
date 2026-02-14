#!/usr/bin/env bash
set -euo pipefail

: "${VERCEL_TOKEN:?Set VERCEL_TOKEN (Vercel Personal Token)}"

TEAM_ID="${TEAM_ID:-team_wphKJ7lHA3QiZu6VgcotQBQM}"
PROJECT_ID="${PROJECT_ID:-prj_PFdFRARO9YQ0CRBkuwp5jAbfKYwe}"
LIMIT="${LIMIT:-3}"

api() {
  curl -fsS \
    -H "Authorization: Bearer ${VERCEL_TOKEN}" \
    -H "Content-Type: application/json" \
    "$@"
}

echo "[1/4] List recent deployments"
api "https://api.vercel.com/v13/deployments?projectId=${PROJECT_ID}&teamId=${TEAM_ID}&limit=${LIMIT}" > /tmp/vercel_deployments.json

# pick newest deployment
DPL_ID="$(node -e '
const fs=require("fs");
const j=JSON.parse(fs.readFileSync("/tmp/vercel_deployments.json","utf8"));
const d=(j.deployments||[])[0];
if(!d){ process.exit(2); }
console.log(d.uid || d.id);
')"

echo "[2/4] Deployment id: ${DPL_ID}"

echo "[3/4] Get deployment details (to discover build id)"
api "https://api.vercel.com/v13/deployments/${DPL_ID}?teamId=${TEAM_ID}" > /tmp/vercel_deployment.json

# heuristic: first build id if present; otherwise empty
BUILD_ID="$(node -e '
const fs=require("fs");
const d=JSON.parse(fs.readFileSync("/tmp/vercel_deployment.json","utf8"));
const b=(d.builds||d.build||[]);
const first=Array.isArray(b)? b[0] : b;
console.log((first && (first.id || first.uid || first)) || "");
')"

echo "[4/4] Fetch deployment events (build logs). Build id: ${BUILD_ID:-<none>}"
# The events endpoint returns build logs when name=<buildId> (and builds=1).
if [ -n "${BUILD_ID}" ]; then
  api "https://api.vercel.com/v3/deployments/${DPL_ID}/events?teamId=${TEAM_ID}&builds=1&direction=forward&limit=200&name=${BUILD_ID}" \
    > /tmp/vercel_events.json
else
  api "https://api.vercel.com/v3/deployments/${DPL_ID}/events?teamId=${TEAM_ID}&builds=1&direction=forward&limit=200" \
    > /tmp/vercel_events.json
fi

# print only stderr/fatal/exit lines to console
node -e '
const fs=require("fs");
const ev=JSON.parse(fs.readFileSync("/tmp/vercel_events.json","utf8"));
for (const e of ev||[]) {
  const t=e.type;
  const txt=(e.payload && e.payload.text) ? e.payload.text : "";
  if (["stderr","fatal","exit","command","deployment-state"].includes(t)) {
    console.log(`--- ${t} ---`);
    if (txt) console.log(txt.trim());
  }
}
'
echo "Saved: /tmp/vercel_deployments.json /tmp/vercel_deployment.json /tmp/vercel_events.json"
