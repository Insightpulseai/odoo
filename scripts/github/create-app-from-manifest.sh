#!/usr/bin/env bash
# create-app-from-manifest.sh
# One-time GitHub App creation via GitHub Manifest Conversion API.
#
# Usage:
#   scripts/github/create-app-from-manifest.sh <app-slug>
#
# Where <app-slug> is a directory under infra/github/apps/:
#   scripts/github/create-app-from-manifest.sh ipai-integrations
#
# What it does:
#   1. Reads infra/github/apps/<slug>/manifest.json
#   2. Opens a browser to GitHub's manifest conversion URL
#      (interactive step — user approves the App creation)
#   3. After redirect, GitHub returns a temporary code; user pastes it here
#   4. Exchanges the code for App credentials via GitHub API
#   5. Writes a machine-readable JSON artifact to .artifacts/github-apps/<slug>/credentials.json
#      (NO secrets in the artifact — only app_id, client_id, and Vault *refs*)
#   6. Prints Supabase CLI commands to store secrets in Vault
#
# Prerequisites:
#   - gh CLI authenticated (gh auth status)
#   - ORG_NAME: GitHub org (default: Insightpulseai)
#   - python3 (stdlib only)
#
# SSOT:    ssot/integrations/github_apps.yaml
# Runbook: docs/runbooks/GITHUB_APP_PROVISIONING.md
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

APP_SLUG="${1:-}"
ORG_NAME="${GITHUB_ORG:-Insightpulseai}"
MANIFEST_FILE="infra/github/apps/${APP_SLUG}/manifest.json"
ARTIFACT_DIR=".artifacts/github-apps/${APP_SLUG}"
ARTIFACT_FILE="${ARTIFACT_DIR}/credentials.json"

# ── Validate inputs ───────────────────────────────────────────────────────────

if [[ -z "$APP_SLUG" ]]; then
  echo "Usage: $0 <app-slug>"
  echo "Example: $0 ipai-integrations"
  exit 1
fi

if [[ ! -f "$MANIFEST_FILE" ]]; then
  echo "ERROR: manifest not found at $MANIFEST_FILE"
  exit 1
fi

if ! command -v gh &>/dev/null; then
  echo "ERROR: gh CLI not installed. Run: brew install gh && gh auth login"
  exit 1
fi

if ! gh auth status &>/dev/null; then
  echo "ERROR: gh CLI not authenticated. Run: gh auth login"
  exit 1
fi

# ── Step 1: Open browser for App creation ────────────────────────────────────

echo ""
echo "┌──────────────────────────────────────────────────────────────────────┐"
echo "│  GitHub App Manifest Conversion — ${APP_SLUG}"
echo "│  Org: ${ORG_NAME}"
echo "└──────────────────────────────────────────────────────────────────────┘"
echo ""
echo "Opening GitHub App creation page for org ${ORG_NAME} ..."
echo ""
echo "  [MANUAL] The browser will open. Review and click 'Create GitHub App'."
echo "           After creation, GitHub redirects to the callback URL."
echo "           Copy the 'code' query parameter from the redirect URL."
echo ""

MANIFEST_URL="https://github.com/organizations/${ORG_NAME}/settings/apps/new"
MANIFEST_CONTENT="$(cat "${MANIFEST_FILE}")"

# Use Python to percent-encode the manifest JSON for the redirect
ENCODED_MANIFEST=$(python3 -c "
import json, urllib.parse, sys
m = json.loads(sys.stdin.read())
print(urllib.parse.quote(json.dumps(m)))
" <<< "${MANIFEST_CONTENT}")

CREATION_URL="${MANIFEST_URL}?manifest=${ENCODED_MANIFEST}"

# Open browser (macOS: open; Linux: xdg-open)
if command -v open &>/dev/null; then
  open "${CREATION_URL}" 2>/dev/null || true
elif command -v xdg-open &>/dev/null; then
  xdg-open "${CREATION_URL}" 2>/dev/null || true
else
  echo "Could not open browser automatically. Visit:"
  echo "  ${CREATION_URL}"
fi

# ── Step 2: Get code from user ────────────────────────────────────────────────

echo ""
echo "After approving the App, copy the 'code' value from the redirect URL."
echo "The URL looks like: https://…/oauth/github-app/installed?code=<CODE>&state=…"
echo ""
read -r -p "Paste the code parameter here: " GITHUB_CODE

if [[ -z "${GITHUB_CODE}" ]]; then
  echo "ERROR: no code provided. Aborting."
  exit 1
fi

# ── Step 3: Exchange code for credentials ─────────────────────────────────────

echo ""
echo "Exchanging code for App credentials ..."

RESPONSE=$(curl -s -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/app-manifests/${GITHUB_CODE}/conversions")

# Parse response
APP_ID=$(echo "${RESPONSE}"         | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id',''))")
CLIENT_ID=$(echo "${RESPONSE}"      | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('client_id',''))")
APP_NAME=$(echo "${RESPONSE}"       | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('name',''))")
WEBHOOK_SECRET=$(echo "${RESPONSE}" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('webhook_secret',''))")
CLIENT_SECRET=$(echo "${RESPONSE}"  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('client_secret',''))")
PRIVATE_KEY=$(echo "${RESPONSE}"    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('pem',''))")

if [[ -z "${APP_ID}" ]]; then
  echo "ERROR: code exchange failed. GitHub response:"
  echo "${RESPONSE}" | python3 -m json.tool 2>/dev/null || echo "${RESPONSE}"
  exit 1
fi

echo "  ✅ App created: ${APP_NAME} (app_id=${APP_ID}, client_id=${CLIENT_ID})"

# ── Step 4: Store secrets in Supabase Vault via CLI ──────────────────────────

echo ""
echo "Storing secrets in Supabase Vault ..."

supabase secrets set "GITHUB_APP_ID=${APP_ID}"
supabase secrets set "GITHUB_APP_WEBHOOK_SECRET=${WEBHOOK_SECRET}"
supabase secrets set "GITHUB_PRIVATE_KEY=$(echo "${PRIVATE_KEY}" | base64)"

if [[ -n "${CLIENT_SECRET}" ]]; then
  supabase secrets set "GITHUB_CLIENT_SECRET=${CLIENT_SECRET}"
fi

echo "  ✅ Secrets stored in Supabase Vault"

# ── Step 5: Write machine-readable artifact (no secrets) ─────────────────────

mkdir -p "${ARTIFACT_DIR}"

python3 - <<PYEOF
import json, datetime

artifact = {
    "_schema": "github_app_credentials.v1",
    "_note": "Non-secret identifiers only. Secrets stored in Supabase Vault.",
    "app_slug": "${APP_SLUG}",
    "app_name": "${APP_NAME}",
    "app_id": "${APP_ID}",
    "client_id": "${CLIENT_ID}",
    "org": "${ORG_NAME}",
    "provisioned_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "ssot": "ssot/integrations/github_apps.yaml",
    "secret_refs": {
        "GITHUB_APP_ID":             "supabase_vault:GITHUB_APP_ID",
        "GITHUB_APP_WEBHOOK_SECRET": "supabase_vault:GITHUB_APP_WEBHOOK_SECRET",
        "GITHUB_PRIVATE_KEY":        "supabase_vault:GITHUB_PRIVATE_KEY",
        "GITHUB_CLIENT_SECRET":      "supabase_vault:GITHUB_CLIENT_SECRET"
    }
}

with open("${ARTIFACT_FILE}", "w") as f:
    json.dump(artifact, f, indent=2)
    f.write("\n")

print(f"  ✅ Artifact written: ${ARTIFACT_FILE}")
PYEOF

# ── Step 6: Print SSOT update instructions ───────────────────────────────────

echo ""
echo "┌──────────────────────────────────────────────────────────────────────┐"
echo "│  NEXT: Update SSOT with non-secret identifiers                       │"
echo "└──────────────────────────────────────────────────────────────────────┘"
echo ""
echo "  Edit ssot/integrations/github_apps.yaml:"
echo "    apps[0].app_id:   ${APP_ID}"
echo "    apps[0].client_id: ${CLIENT_ID}"
echo "    apps[0].status:   active"
echo ""
echo "  Then commit:"
echo "    git add ssot/integrations/github_apps.yaml"
echo "    git commit -m 'chore(ssot): record ipai-integrations app_id + client_id, status→active'"
echo ""
echo "  Then deploy:"
echo "    supabase functions deploy ops-github-webhook-ingest"
echo ""
echo "  Artifact at: ${ARTIFACT_FILE}"
echo ""
echo "STATUS=COMPLETE"
