#!/usr/bin/env bash
# shellcheck disable=SC2086
set -euo pipefail
###############################################################################
# Supabase Snapshot Provider
#
# Collects project metadata from Supabase Management API.
# Requires: SUPABASE_ACCESS_TOKEN environment variable.
#
# Output: ssot/supabase/*.snapshot.json (gitignored, CI artifacts only)
#
# Usage:
#   bash scripts/ssot/providers/supabase_snapshot.sh
#   bash scripts/ssot/providers/supabase_snapshot.sh --functions-only
###############################################################################

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT_DIR="${REPO_ROOT}/ssot/supabase"
SUPABASE_PROJECT_ID="${SUPABASE_PROJECT_ID:-spdtwktxdalcfigzeqrz}"
mkdir -p "${OUT_DIR}"

# ── Pre-flight ──────────────────────────────────────────────────────────────
if [[ -z "${SUPABASE_ACCESS_TOKEN:-}" ]]; then
  echo "SKIP: SUPABASE_ACCESS_TOKEN not set — Supabase snapshot disabled"
  echo '{"skipped":true,"reason":"SUPABASE_ACCESS_TOKEN not set"}' > "${OUT_DIR}/project.snapshot.json"
  exit 0
fi

API="https://api.supabase.com/v1"
AUTH="Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}"

FLAG="${1:-all}"

sb_api() {
  local endpoint="$1"
  local out_file="$2"
  echo "  → GET ${endpoint}"
  if ! curl -sf -H "${AUTH}" "${API}${endpoint}" -o "${out_file}" 2>/dev/null; then
    echo "    WARN: ${endpoint} failed or empty"
    echo '{"error":"API call failed","endpoint":"'"${endpoint}"'"}' > "${out_file}"
  fi
}

# ── Projects ────────────────────────────────────────────────────────────────
if [[ "${FLAG}" == "all" ]]; then
  echo "Layer 1: Projects"
  sb_api "/projects" "${OUT_DIR}/projects.snapshot.json"
fi

# ── Project details ─────────────────────────────────────────────────────────
if [[ "${FLAG}" == "all" ]]; then
  echo "Layer 2: Project details (${SUPABASE_PROJECT_ID})"

  # API keys (names only, not values — values are masked by API)
  sb_api "/projects/${SUPABASE_PROJECT_ID}/api-keys" "${OUT_DIR}/api-keys.snapshot.json"

  # Database settings
  sb_api "/projects/${SUPABASE_PROJECT_ID}/config/database/postgres" "${OUT_DIR}/db-config.snapshot.json"
fi

# ── Edge Functions ──────────────────────────────────────────────────────────
if [[ "${FLAG}" == "all" || "${FLAG}" == "--functions-only" ]]; then
  echo "Layer 3: Edge Functions"
  sb_api "/projects/${SUPABASE_PROJECT_ID}/functions" "${OUT_DIR}/functions.snapshot.json"
fi

# ── Auth config ─────────────────────────────────────────────────────────────
if [[ "${FLAG}" == "all" ]]; then
  echo "Layer 4: Auth config"
  sb_api "/projects/${SUPABASE_PROJECT_ID}/config/auth" "${OUT_DIR}/auth-config.snapshot.json"
fi

# ── Storage buckets ─────────────────────────────────────────────────────────
if [[ "${FLAG}" == "all" ]]; then
  echo "Layer 5: Storage buckets"
  # Use PostgREST endpoint for storage buckets
  SUPABASE_URL="https://${SUPABASE_PROJECT_ID}.supabase.co"
  if [[ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
    curl -sf \
      -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
      -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
      "${SUPABASE_URL}/storage/v1/bucket" \
      -o "${OUT_DIR}/storage-buckets.snapshot.json" 2>/dev/null || \
    echo '{"error":"Storage API failed"}' > "${OUT_DIR}/storage-buckets.snapshot.json"
  else
    echo '{"skipped":true,"reason":"SUPABASE_SERVICE_ROLE_KEY not set"}' > "${OUT_DIR}/storage-buckets.snapshot.json"
  fi
fi

# ── Table count (via Management API) ────────────────────────────────────────
if [[ "${FLAG}" == "all" ]]; then
  echo "Layer 6: Database schema summary"
  # The Management API doesn't expose table listing directly,
  # but we can get the PostgREST schema endpoint
  SUPABASE_URL="https://${SUPABASE_PROJECT_ID}.supabase.co"
  if [[ -n "${SUPABASE_ANON_KEY:-}" ]]; then
    curl -sf \
      -H "apikey: ${SUPABASE_ANON_KEY}" \
      "${SUPABASE_URL}/rest/v1/" \
      -o "${OUT_DIR}/schema-tables.snapshot.json" 2>/dev/null || \
    echo '{"error":"Schema endpoint failed"}' > "${OUT_DIR}/schema-tables.snapshot.json"
  else
    echo '{"skipped":true,"reason":"SUPABASE_ANON_KEY not set"}' > "${OUT_DIR}/schema-tables.snapshot.json"
  fi
fi

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "Supabase snapshot complete."
echo "Files written to: ${OUT_DIR}/"
ls -la "${OUT_DIR}/"*.snapshot.json 2>/dev/null | wc -l | xargs -I{} echo "  {} snapshot files"
