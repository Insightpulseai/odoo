#!/usr/bin/env bash
# =============================================================================
# scripts/vercel/claim_domain.sh
# =============================================================================
# Attach ops.insightpulseai.com to the odooops-console Vercel project via API.
# Fetches the required verification TXT token and prints a ready-to-paste
# YAML snippet for infra/dns/subdomain-registry.yaml.
#
# Turns "attach domain in Vercel dashboard" into a deterministic repo step:
#   run script → paste token into SSOT → PR → merge → DNS CI passes → deploy
#
# Usage:
#   export VERCEL_TOKEN=...
#   ./scripts/vercel/claim_domain.sh
#
# Optional overrides:
#   VERCEL_TEAM_SLUG=tbwa                        (default)
#   VERCEL_PROJECT_NAME=odooops-console          (default)
#   DOMAIN=ops.insightpulseai.com                (default)
# =============================================================================
set -euo pipefail

TEAM_SLUG="${VERCEL_TEAM_SLUG:-tbwa}"
PROJECT_NAME="${VERCEL_PROJECT_NAME:-odooops-console}"
DOMAIN="${DOMAIN:-ops.insightpulseai.com}"
API="https://api.vercel.com"

require() { [[ -n "${!1:-}" ]] || { echo "❌ Missing: $1" >&2; exit 1; }; }
require VERCEL_TOKEN

AUTH="Authorization: Bearer ${VERCEL_TOKEN}"

# ── 1. Resolve team ID ────────────────────────────────────────────────────────
echo "🔍 Resolving team: ${TEAM_SLUG}..."
TEAM_ID=$(curl -sf -H "${AUTH}" \
  "${API}/v2/teams?slug=${TEAM_SLUG}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['teams'][0]['id'])")
echo "   Team ID: ${TEAM_ID}"

# ── 2. Resolve project ID ─────────────────────────────────────────────────────
echo "🔍 Resolving project: ${PROJECT_NAME}..."
PROJECT_ID=$(curl -sf -H "${AUTH}" \
  "${API}/v9/projects/${PROJECT_NAME}?teamId=${TEAM_ID}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['id'])")
echo "   Project ID: ${PROJECT_ID}"

# ── 3. Add domain to project ──────────────────────────────────────────────────
echo ""
echo "🌐 Attaching ${DOMAIN} to project ${PROJECT_NAME}..."
RESPONSE=$(curl -sf -X POST -H "${AUTH}" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"${DOMAIN}\"}" \
  "${API}/v10/projects/${PROJECT_ID}/domains?teamId=${TEAM_ID}" 2>&1) || {
    # 409 = domain already added; fetch existing config instead
    echo "   Domain may already be attached — fetching existing config..."
    RESPONSE=$(curl -sf -H "${AUTH}" \
      "${API}/v10/projects/${PROJECT_ID}/domains/${DOMAIN}?teamId=${TEAM_ID}")
}

# ── 4. Extract verification token ─────────────────────────────────────────────
VERIFIED=$(echo "${RESPONSE}" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(str(d.get('verified', False)).lower())
")

if [[ "${VERIFIED}" == "true" ]]; then
  echo ""
  echo "✅ Domain already verified — no TXT token needed."
  echo ""
  echo "SSOT update (flip lifecycle to active):"
  cat <<YAML

    # In infra/dns/subdomain-registry.yaml, update ops entry:
    lifecycle: active
    status: active
    provider_claim:
      provider: vercel
      status: claimed
      claimed_at: "$(date -u +%Y-%m-%d)"
      claim_ref: "vercel:${PROJECT_ID}"
YAML
  exit 0
fi

# ── 5. Extract TXT record details ─────────────────────────────────────────────
TXT_NAME=$(echo "${RESPONSE}" | python3 -c "
import sys, json
d = json.load(sys.stdin)
v = d.get('verification', [])
txt = next((x for x in v if x.get('type') == 'TXT'), None)
print(txt['domain'] if txt else 'NOT_FOUND')
")

TXT_VALUE=$(echo "${RESPONSE}" | python3 -c "
import sys, json
d = json.load(sys.stdin)
v = d.get('verification', [])
txt = next((x for x in v if x.get('type') == 'TXT'), None)
print(txt['value'] if txt else 'NOT_FOUND')
")

echo ""
if [[ "${TXT_NAME}" == "NOT_FOUND" ]]; then
  echo "⚠️  No TXT verification record returned. Raw response:"
  echo "${RESPONSE}" | python3 -m json.tool
  exit 1
fi

# ── 6. Print SSOT patch snippet ───────────────────────────────────────────────
echo "📋 TXT verification required:"
echo "   Name:  ${TXT_NAME}"
echo "   Value: ${TXT_VALUE}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Paste into infra/cloudflare/zones/insightpulseai.com/records.yaml:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat <<YAML

  - type: TXT
    name: ${TXT_NAME%.insightpulseai.com}
    content: "${TXT_VALUE}"
    proxied: false
    ttl: 3600
    comment: "Vercel domain verification for ops.insightpulseai.com"
YAML

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Update infra/dns/subdomain-registry.yaml (ops entry):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat <<YAML

    verification_txt: "${TXT_VALUE}"
    provider_claim:
      provider: vercel
      status: claimed
      claimed_at: "$(date -u +%Y-%m-%d)"
      claim_ref: "vercel:${PROJECT_ID}"
YAML

echo ""
echo "Next steps:"
echo "  1. Add TXT record to records.yaml (above)"
echo "  2. Update subdomain-registry.yaml: replace placeholder + flip lifecycle → active"
echo "  3. Open PR → merge → DNS CI applies TXT → Vercel auto-verifies"
echo "  4. Redeploy: VERCEL_TOKEN=\$VERCEL_TOKEN vercel redeploy --scope ${TEAM_SLUG}"
