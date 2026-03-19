#!/usr/bin/env bash
# create-app-from-manifest.sh
# One-time GitHub App creation via GitHub Manifest Conversion API.
#
# Usage:
#   scripts/github/create-app-from-manifest.sh <app-slug> [options]
#
# Modes:
#   (default)                  Interactive: opens browser, waits for code paste
#   --dry-run                  Print what would happen without touching GitHub or Vault
#   --exchange-code <code>     Non-interactive: skip browser, use supplied code
#
# Examples:
#   scripts/github/create-app-from-manifest.sh ipai-integrations
#   scripts/github/create-app-from-manifest.sh ipai-integrations --dry-run
#   scripts/github/create-app-from-manifest.sh ipai-integrations --exchange-code Ab1Cd2Ef3
#
# What it does:
#   1. Reads infra/github/apps/<slug>/manifest.json
#   2. Opens a browser to GitHub's manifest conversion URL (skipped in --exchange-code)
#   3. Exchanges the code for App credentials via GitHub API
#   4. Stores secrets in Supabase Vault via supabase CLI
#   5. Writes .artifacts/github-apps/<slug>/credentials.json (app_id + client_id + vault refs,
#      NO raw secrets in artifact)
#   6. Prints exact SSOT update instructions
#
# Prerequisites:
#   - gh CLI authenticated (gh auth status)
#   - supabase CLI linked to project (supabase link --project-ref ...)
#   - python3 (stdlib only)
#
# SSOT:    ssot/integrations/github_apps.yaml
# Runbook: docs/runbooks/GITHUB_APP_PROVISIONING.md
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Parse args ────────────────────────────────────────────────────────────────

APP_SLUG="${1:-}"
DRY_RUN=false
EXCHANGE_CODE=""

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true; shift ;;
    --exchange-code)
      EXCHANGE_CODE="${2:-}"; shift 2 ;;
    *)
      echo "Unknown option: $1"; exit 1 ;;
  esac
done

ORG_NAME="${GITHUB_ORG:-Insightpulseai}"
MANIFEST_FILE="infra/github/apps/${APP_SLUG}/manifest.json"
ARTIFACT_DIR=".artifacts/github-apps/${APP_SLUG}"
ARTIFACT_FILE="${ARTIFACT_DIR}/credentials.json"

# ── Validate inputs ───────────────────────────────────────────────────────────

if [[ -z "$APP_SLUG" ]]; then
  echo "Usage: $0 <app-slug> [--dry-run | --exchange-code <code>]"
  echo "Example: $0 ipai-integrations"
  echo "         $0 ipai-integrations --dry-run"
  echo "         $0 ipai-integrations --exchange-code Ab1Cd2Ef3"
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

# ── Dry-run mode ──────────────────────────────────────────────────────────────

if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "┌──────────────────────────────────────────────────────────────────────┐"
  echo "│  DRY RUN — no GitHub or Supabase calls will be made                  │"
  echo "└──────────────────────────────────────────────────────────────────────┘"
  echo ""
  echo "  App slug:       ${APP_SLUG}"
  echo "  Org:            ${ORG_NAME}"
  echo "  Manifest:       ${MANIFEST_FILE}"
  echo "  Artifact out:   ${ARTIFACT_FILE}"
  echo ""
  echo "  Steps that would run:"
  echo "    1. Open https://github.com/organizations/${ORG_NAME}/settings/apps/new?manifest=..."
  echo "    2. Wait for code from redirect"
  echo "    3. POST https://api.github.com/app-manifests/<code>/conversions"
  echo "    4. supabase secrets set GITHUB_APP_ID=..."
  echo "    4. supabase secrets set GITHUB_APP_WEBHOOK_SECRET=..."
  echo "    4. supabase secrets set GITHUB_PRIVATE_KEY=<base64>"
  echo "    4. supabase secrets set GITHUB_CLIENT_SECRET=..."
  echo "    5. Write ${ARTIFACT_FILE} (non-secret IDs + vault refs)"
  echo ""
  echo "  Manifest contents:"
  python3 -m json.tool "${MANIFEST_FILE}" 2>/dev/null || cat "${MANIFEST_FILE}"
  echo ""
  echo "STATUS=DRY_RUN (no changes made)"
  exit 0
fi

# ── Step 1: Open browser for App creation (skipped if --exchange-code) ────────

echo ""
echo "┌──────────────────────────────────────────────────────────────────────┐"
echo "│  GitHub App Manifest Conversion — ${APP_SLUG}"
echo "│  Org: ${ORG_NAME}"
echo "└──────────────────────────────────────────────────────────────────────┘"

MANIFEST_CONTENT="$(cat "${MANIFEST_FILE}")"

# Percent-encode the manifest JSON for the redirect URL
ENCODED_MANIFEST=$(python3 -c "
import json, urllib.parse, sys
m = json.loads(sys.stdin.read())
print(urllib.parse.quote(json.dumps(m)))
" <<< "${MANIFEST_CONTENT}")

CREATION_URL="https://github.com/organizations/${ORG_NAME}/settings/apps/new?manifest=${ENCODED_MANIFEST}"

if [[ -z "${EXCHANGE_CODE}" ]]; then
  echo ""
  echo "Opening GitHub App creation page for org ${ORG_NAME} ..."
  echo ""
  echo "  [MANUAL] The browser will open. Review and click 'Create GitHub App'."
  echo "           After creation, GitHub redirects to the callback URL."
  echo "           Copy the 'code' query parameter from the redirect URL."
  echo "           URL format: https://…/oauth/github-app/installed?code=<CODE>&state=…"
  echo ""

  if command -v open &>/dev/null; then
    open "${CREATION_URL}" 2>/dev/null || true
  elif command -v xdg-open &>/dev/null; then
    xdg-open "${CREATION_URL}" 2>/dev/null || true
  else
    echo "  Could not open browser automatically. Visit:"
    echo "  ${CREATION_URL}"
  fi

  read -r -p "  Paste the code parameter here: " EXCHANGE_CODE

  if [[ -z "${EXCHANGE_CODE}" ]]; then
    echo "ERROR: no code provided. Aborting."
    exit 1
  fi
else
  echo ""
  echo "  Using supplied code (--exchange-code mode): ${EXCHANGE_CODE:0:8}…"
fi

# ── Step 2: Exchange code for credentials ─────────────────────────────────────

echo ""
echo "  Exchanging code for App credentials ..."

RESPONSE=$(curl -s -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/app-manifests/${EXCHANGE_CODE}/conversions")

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

# ── Step 3: Store secrets in Supabase Vault via CLI ──────────────────────────

echo ""
echo "  Storing secrets in Supabase Vault ..."

supabase secrets set "GITHUB_APP_ID=${APP_ID}"
supabase secrets set "GITHUB_APP_WEBHOOK_SECRET=${WEBHOOK_SECRET}"
supabase secrets set "GITHUB_PRIVATE_KEY=$(echo "${PRIVATE_KEY}" | base64)"

if [[ -n "${CLIENT_SECRET}" ]]; then
  supabase secrets set "GITHUB_CLIENT_SECRET=${CLIENT_SECRET}"
fi

echo "  ✅ Secrets stored in Supabase Vault"

# ── Step 4: Write machine-readable artifact (no secrets) ─────────────────────

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

print(f"  \u2705 Artifact written: ${ARTIFACT_FILE}")
PYEOF

# ── Step 5: Print SSOT update instructions ───────────────────────────────────

echo ""
echo "┌──────────────────────────────────────────────────────────────────────┐"
echo "│  NEXT: Update SSOT with non-secret identifiers                       │"
echo "└──────────────────────────────────────────────────────────────────────┘"
echo ""
echo "  Edit ssot/integrations/github_apps.yaml:"
echo "    apps[0].app_id:    ${APP_ID}"
echo "    apps[0].client_id: ${CLIENT_ID}"
echo "    apps[0].status:    active"
echo ""
echo "  Then commit:"
echo "    git add ssot/integrations/github_apps.yaml"
echo "    git commit -m 'chore(ssot): record ipai-integrations app_id + client_id, status→active'"
echo ""
echo "  Then deploy:"
echo "    supabase functions deploy ops-github-webhook-ingest --project-ref spdtwktxdalcfigzeqrz"
echo ""
echo "  Artifact: ${ARTIFACT_FILE}"
echo ""
echo "STATUS=COMPLETE"
