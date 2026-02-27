#!/usr/bin/env bash
# =============================================================================
# scripts/infra/load_cloudflare_env.sh
#
# Loads Cloudflare credentials from macOS Keychain into environment variables.
#
# Exports:
#   CF_API_TOKEN     — scoped API token (Zone:DNS:Edit) used by Terraform / CI
#   CF_Key           — global API key used by acme.sh DNS-01 challenge
#   CF_Email         — Cloudflare account email (paired with CF_Key)
#   CF_ZONE_ID       — Zone ID for insightpulseai.com
#
# Keychain entries (create once per machine):
#   security add-generic-password -s cloudflare-api-token   -a default -w "<CF_DNS_EDIT_TOKEN>" -U
#   security add-generic-password -s cloudflare-global-api-key -a default -w "<CF_GLOBAL_API_KEY>" -U
#   security add-generic-password -s cloudflare-zone-id     -a insightpulseai.com -w "<ZONE_ID>" -U
#
# Usage:
#   source scripts/infra/load_cloudflare_env.sh        # export into current shell
#   . scripts/infra/load_cloudflare_env.sh             # POSIX equivalent
#
# SSOT: ssot/secrets/registry.yaml (cf_dns_edit_token, cloudflare_global_api_key, cloudflare_zone_id)
# =============================================================================
set -euo pipefail

# --------------------------------------------------------------------------
# Helper: read from macOS Keychain; exit 2 with actionable message if absent
# --------------------------------------------------------------------------
_keychain_get() {
  local service="$1"
  local account="$2"
  local env_var_name="$3"
  local add_command="$4"

  local value
  value="$(security find-generic-password -s "${service}" -a "${account}" -w 2>/dev/null || true)"

  if [ -z "${value}" ]; then
    echo "ERROR: Missing Keychain secret" >&2
    echo "  service=${service}  account=${account}" >&2
    echo "  (needed for env var: ${env_var_name})" >&2
    echo "" >&2
    echo "  Create it with:" >&2
    echo "    ${add_command}" >&2
    echo "" >&2
    exit 2
  fi

  printf '%s' "${value}"
}

# --------------------------------------------------------------------------
# CF_API_TOKEN — scoped DNS edit token (used by Terraform, cloudflare-dns-apply)
# --------------------------------------------------------------------------
CF_API_TOKEN="$(_keychain_get \
  "cloudflare-api-token" \
  "default" \
  "CF_API_TOKEN" \
  'security add-generic-password -s cloudflare-api-token -a default -w "<CF_DNS_EDIT_TOKEN>" -U'
)"
export CF_API_TOKEN
export TF_VAR_cloudflare_api_token="${CF_API_TOKEN}"  # Terraform var alias

# --------------------------------------------------------------------------
# CF_Key + CF_Email — global API key (used by acme.sh DNS-01)
# --------------------------------------------------------------------------
CF_Key="$(_keychain_get \
  "cloudflare-global-api-key" \
  "default" \
  "CF_Key" \
  'security add-generic-password -s cloudflare-global-api-key -a default -w "<CF_GLOBAL_API_KEY>" -U'
)"
export CF_Key

# Email is static — not a secret, but co-located here for acme.sh convenience
CF_Email="Jgtolentino.rn@gmail.com"
export CF_Email

# --------------------------------------------------------------------------
# CF_ZONE_ID — Zone ID for insightpulseai.com
# --------------------------------------------------------------------------
CF_ZONE_ID="$(_keychain_get \
  "cloudflare-zone-id" \
  "insightpulseai.com" \
  "CF_ZONE_ID" \
  'security add-generic-password -s cloudflare-zone-id -a insightpulseai.com -w "73f587aee652fc24fd643aec00dcca81" -U'
)"
export CF_ZONE_ID
export TF_VAR_cloudflare_zone_id="${CF_ZONE_ID}"  # Terraform var alias

echo "OK: CF credentials loaded from macOS Keychain"
echo "  CF_API_TOKEN   = ${CF_API_TOKEN:0:8}... (${#CF_API_TOKEN} chars)"
echo "  CF_Key         = ${CF_Key:0:8}... (${#CF_Key} chars)"
echo "  CF_Email       = ${CF_Email}"
echo "  CF_ZONE_ID     = ${CF_ZONE_ID:0:8}... (${#CF_ZONE_ID} chars)"
