#!/usr/bin/env bash
# =============================================================================
# scripts/vercel/set_ops_console_env.sh
# =============================================================================
# Set all required env vars on the odooops-console Vercel project.
# Skips the Supabase↔Vercel native integration UI entirely.
#
# Usage:
#   export VERCEL_TOKEN=...
#   export SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
#   export SUPABASE_ANON_KEY=...
#   export SUPABASE_SERVICE_ROLE_KEY=...
#   export SUPABASE_MANAGEMENT_API_TOKEN=...
#   export OPS_INTERNAL_TOKEN=...        # x-ops-internal-token guard
#   # Optional:
#   export ANTHROPIC_AUTH_TOKEN=...
#   export VERCEL_API_TOKEN=...
#   export DIGITALOCEAN_API_TOKEN=...
#   ./scripts/vercel/set_ops_console_env.sh
#
# Idempotent: removes existing value before setting (safe to re-run).
# Never prints secret values.
# =============================================================================
set -euo pipefail

TEAM_SLUG="${VERCEL_TEAM_SLUG:-tbwa}"
PROJECT_NAME="${VERCEL_PROJECT_NAME:-odooops-console}"
PROJECT_REF="spdtwktxdalcfigzeqrz"

require() {
  [[ -n "${!1:-}" ]] || { echo "❌ Missing required env: $1" >&2; exit 1; }
}

require VERCEL_TOKEN
require SUPABASE_URL
require SUPABASE_ANON_KEY
require SUPABASE_SERVICE_ROLE_KEY
require SUPABASE_MANAGEMENT_API_TOKEN
require OPS_INTERNAL_TOKEN

: "${ANTHROPIC_BASE_URL:=https://ai-gateway.vercel.sh}"
: "${SUPABASE_ALLOWED_PROJECT_REFS:=${PROJECT_REF}}"

echo "🔗 Linking to Vercel project: ${PROJECT_NAME} (team: ${TEAM_SLUG})"
VERCEL_TOKEN="${VERCEL_TOKEN}" vercel link \
  --yes --project "${PROJECT_NAME}" --scope "${TEAM_SLUG}" >/dev/null

# Idempotent set: rm (best-effort) then add, for all three environments
set_env() {
  local name="$1" value="$2"
  for target in production preview development; do
    VERCEL_TOKEN="${VERCEL_TOKEN}" vercel env rm "${name}" "${target}" \
      --yes --scope "${TEAM_SLUG}" >/dev/null 2>&1 || true
    printf "%s" "${value}" | VERCEL_TOKEN="${VERCEL_TOKEN}" vercel env add \
      "${name}" "${target}" --scope "${TEAM_SLUG}" >/dev/null
    echo "  ✅ ${name} → ${target}"
  done
}

echo ""
echo "📦 Public (NEXT_PUBLIC) vars..."
set_env NEXT_PUBLIC_SUPABASE_URL         "${SUPABASE_URL}"
set_env NEXT_PUBLIC_SUPABASE_ANON_KEY    "${SUPABASE_ANON_KEY}"
set_env NEXT_PUBLIC_SUPABASE_PROJECT_REF "${PROJECT_REF}"

echo ""
echo "🔒 Server-only vars..."
set_env SUPABASE_SERVICE_ROLE_KEY        "${SUPABASE_SERVICE_ROLE_KEY}"
set_env SUPABASE_MANAGEMENT_API_TOKEN    "${SUPABASE_MANAGEMENT_API_TOKEN}"
set_env SUPABASE_ALLOWED_PROJECT_REFS    "${SUPABASE_ALLOWED_PROJECT_REFS}"
set_env OPS_INTERNAL_TOKEN               "${OPS_INTERNAL_TOKEN}"

echo ""
echo "⚙️  Optional vars..."
if [[ -n "${ANTHROPIC_AUTH_TOKEN:-}" ]]; then
  set_env ANTHROPIC_AUTH_TOKEN  "${ANTHROPIC_AUTH_TOKEN}"
  set_env ANTHROPIC_BASE_URL    "${ANTHROPIC_BASE_URL}"
  set_env ANTHROPIC_API_KEY     ""
else
  echo "  ⏭️  ANTHROPIC_AUTH_TOKEN not set — skipping"
fi
if [[ -n "${VERCEL_API_TOKEN:-}" ]]; then
  set_env VERCEL_API_TOKEN "${VERCEL_API_TOKEN}"
else
  echo "  ⏭️  VERCEL_API_TOKEN not set — skipping"
fi
if [[ -n "${DIGITALOCEAN_API_TOKEN:-}" ]]; then
  set_env DIGITALOCEAN_API_TOKEN "${DIGITALOCEAN_API_TOKEN}"
else
  echo "  ⏭️  DIGITALOCEAN_API_TOKEN not set — skipping"
fi

echo ""
echo "✅ Done. Trigger a redeploy:"
echo "   VERCEL_TOKEN=\$VERCEL_TOKEN vercel redeploy --scope ${TEAM_SLUG}"
