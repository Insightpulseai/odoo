#!/usr/bin/env bash
# =============================================================================
# MINT-GHAPP-TOKEN.SH - GitHub App Installation Access Token Generator
# =============================================================================
# Generates an installation access token for the pulser-hub GitHub App.
# Uses JWT authentication to request short-lived installation tokens.
#
# PREREQUISITES:
#   - openssl (for JWT signing)
#   - curl (for API calls)
#   - jq (for JSON parsing)
#
# REQUIRED ENVIRONMENT VARIABLES:
#   GITHUB_APP_ID              - GitHub App ID (2191216 for pulser-hub)
#   GITHUB_APP_PRIVATE_KEY_B64 - Base64-encoded private key (.pem file)
#   OR
#   GITHUB_APP_PRIVATE_KEY_PATH - Path to private key file
#
# OPTIONAL ENVIRONMENT VARIABLES:
#   GITHUB_APP_INSTALLATION_ID - Skip auto-discovery if set
#   GITHUB_ORG                 - Organization for installation lookup (default: Insightpulseai-net)
#
# USAGE:
#   # Set required env vars, then:
#   export GITHUB_TOKEN=$(./scripts/github/mint-ghapp-token.sh)
#
#   # Or with explicit installation ID:
#   export GITHUB_APP_INSTALLATION_ID=12345678
#   export GITHUB_TOKEN=$(./scripts/github/mint-ghapp-token.sh)
#
# OUTPUT:
#   Prints installation access token to stdout (for use in GITHUB_TOKEN)
#   All logs go to stderr to avoid polluting token output
#
# TOKEN LIFECYCLE:
#   - JWT: Valid for 10 minutes (per GitHub spec)
#   - Installation token: Valid for 1 hour (per GitHub spec)
#   - Tokens are NOT cached - call this script each time you need a fresh token
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
GITHUB_API_BASE="https://api.github.com"
GITHUB_ORG="${GITHUB_ORG:-Insightpulseai-net}"
JWT_EXPIRY_SECONDS=600  # 10 minutes (maximum per GitHub spec)

# Colors for stderr logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# -----------------------------------------------------------------------------
# Logging (all to stderr to keep stdout clean for token output)
# -----------------------------------------------------------------------------
log_info()  { echo -e "${BLUE}[INFO]${NC} $1" >&2; }
log_pass()  { echo -e "${GREEN}[PASS]${NC} $1" >&2; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# -----------------------------------------------------------------------------
# Dependency Check
# -----------------------------------------------------------------------------
check_dependencies() {
    local missing=()

    command -v openssl >/dev/null 2>&1 || missing+=("openssl")
    command -v curl >/dev/null 2>&1 || missing+=("curl")
    command -v jq >/dev/null 2>&1 || missing+=("jq")

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing[*]}"
        log_error "Install with: brew install ${missing[*]}"
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Environment Validation
# -----------------------------------------------------------------------------
validate_environment() {
    # App ID is required
    if [[ -z "${GITHUB_APP_ID:-}" ]]; then
        log_error "GITHUB_APP_ID is required"
        exit 1
    fi

    # Need either private key file or base64-encoded key
    if [[ -z "${GITHUB_APP_PRIVATE_KEY_B64:-}" && -z "${GITHUB_APP_PRIVATE_KEY_PATH:-}" ]]; then
        log_error "Either GITHUB_APP_PRIVATE_KEY_B64 or GITHUB_APP_PRIVATE_KEY_PATH is required"
        exit 1
    fi

    # If path provided, verify file exists
    if [[ -n "${GITHUB_APP_PRIVATE_KEY_PATH:-}" && ! -f "${GITHUB_APP_PRIVATE_KEY_PATH}" ]]; then
        log_error "Private key file not found: ${GITHUB_APP_PRIVATE_KEY_PATH}"
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Get Private Key
# -----------------------------------------------------------------------------
get_private_key() {
    if [[ -n "${GITHUB_APP_PRIVATE_KEY_B64:-}" ]]; then
        # Decode base64-encoded key
        echo "${GITHUB_APP_PRIVATE_KEY_B64}" | base64 -d
    else
        # Read from file
        cat "${GITHUB_APP_PRIVATE_KEY_PATH}"
    fi
}

# -----------------------------------------------------------------------------
# Base64 URL Encoding (no padding)
# -----------------------------------------------------------------------------
base64url_encode() {
    openssl base64 -e -A | tr '+/' '-_' | tr -d '='
}

# -----------------------------------------------------------------------------
# Generate JWT
# -----------------------------------------------------------------------------
generate_jwt() {
    local private_key="$1"
    local now
    local exp

    now=$(date +%s)
    exp=$((now + JWT_EXPIRY_SECONDS))

    # JWT Header
    local header='{"alg":"RS256","typ":"JWT"}'
    local header_b64
    header_b64=$(echo -n "${header}" | base64url_encode)

    # JWT Payload
    local payload
    payload=$(cat <<EOF
{
  "iat": ${now},
  "exp": ${exp},
  "iss": "${GITHUB_APP_ID}"
}
EOF
)
    local payload_b64
    payload_b64=$(echo -n "${payload}" | base64url_encode)

    # Create signature
    local unsigned="${header_b64}.${payload_b64}"
    local signature
    signature=$(echo -n "${unsigned}" | openssl dgst -sha256 -sign <(echo "${private_key}") | base64url_encode)

    echo "${unsigned}.${signature}"
}

# -----------------------------------------------------------------------------
# Get Installation ID
# -----------------------------------------------------------------------------
get_installation_id() {
    local jwt="$1"

    # If explicitly set, use it
    if [[ -n "${GITHUB_APP_INSTALLATION_ID:-}" ]]; then
        log_info "Using explicit installation ID: ${GITHUB_APP_INSTALLATION_ID}"
        echo "${GITHUB_APP_INSTALLATION_ID}"
        return
    fi

    log_info "Auto-discovering installation ID for org: ${GITHUB_ORG}"

    # Get all installations
    local response
    response=$(curl -sS -H "Authorization: Bearer ${jwt}" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "${GITHUB_API_BASE}/app/installations")

    # Check for error
    if echo "${response}" | jq -e '.message' >/dev/null 2>&1; then
        local error_msg
        error_msg=$(echo "${response}" | jq -r '.message')
        log_error "Failed to list installations: ${error_msg}"
        exit 1
    fi

    # Find installation for our org
    local installation_id
    installation_id=$(echo "${response}" | jq -r --arg org "${GITHUB_ORG}" \
        '.[] | select(.account.login == $org) | .id')

    if [[ -z "${installation_id}" || "${installation_id}" == "null" ]]; then
        # Try case-insensitive match
        installation_id=$(echo "${response}" | jq -r --arg org "${GITHUB_ORG}" \
            '.[] | select(.account.login | ascii_downcase == ($org | ascii_downcase)) | .id')
    fi

    if [[ -z "${installation_id}" || "${installation_id}" == "null" ]]; then
        log_error "No installation found for org: ${GITHUB_ORG}"
        log_error "Available installations:"
        echo "${response}" | jq -r '.[].account.login' >&2
        exit 1
    fi

    log_pass "Found installation ID: ${installation_id}"
    echo "${installation_id}"
}

# -----------------------------------------------------------------------------
# Get Installation Access Token
# -----------------------------------------------------------------------------
get_installation_token() {
    local jwt="$1"
    local installation_id="$2"

    log_info "Requesting installation access token..."

    local response
    response=$(curl -sS -X POST \
        -H "Authorization: Bearer ${jwt}" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "${GITHUB_API_BASE}/app/installations/${installation_id}/access_tokens")

    # Check for error
    if echo "${response}" | jq -e '.message' >/dev/null 2>&1; then
        local error_msg
        error_msg=$(echo "${response}" | jq -r '.message')
        log_error "Failed to get installation token: ${error_msg}"
        exit 1
    fi

    # Extract token
    local token
    token=$(echo "${response}" | jq -r '.token')

    if [[ -z "${token}" || "${token}" == "null" ]]; then
        log_error "No token in response"
        exit 1
    fi

    # Log expiry (to stderr)
    local expires_at
    expires_at=$(echo "${response}" | jq -r '.expires_at')
    log_pass "Token generated, expires at: ${expires_at}"

    # Log permissions (to stderr)
    local permissions
    permissions=$(echo "${response}" | jq -r '.permissions | keys | join(", ")')
    log_info "Permissions: ${permissions}"

    # Output token to stdout
    echo "${token}"
}

# -----------------------------------------------------------------------------
# Verify Token Works
# -----------------------------------------------------------------------------
verify_token() {
    local token="$1"

    log_info "Verifying token with API call..."

    local response
    response=$(curl -sS -H "Authorization: Bearer ${token}" \
        -H "Accept: application/vnd.github+json" \
        "${GITHUB_API_BASE}/orgs/${GITHUB_ORG}")

    if echo "${response}" | jq -e '.message' >/dev/null 2>&1; then
        local error_msg
        error_msg=$(echo "${response}" | jq -r '.message')
        log_warn "Token verification failed: ${error_msg}"
        return 1
    fi

    local org_name
    org_name=$(echo "${response}" | jq -r '.login')
    log_pass "Token verified for org: ${org_name}"
    return 0
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
    log_info "=== GitHub App Token Minting ==="
    log_info "App ID: ${GITHUB_APP_ID:-not set}"

    # Check dependencies
    check_dependencies

    # Validate environment
    validate_environment

    # Get private key
    log_info "Loading private key..."
    local private_key
    private_key=$(get_private_key)

    # Generate JWT
    log_info "Generating JWT..."
    local jwt
    jwt=$(generate_jwt "${private_key}")

    # Get installation ID
    local installation_id
    installation_id=$(get_installation_id "${jwt}")

    # Get installation access token
    local token
    token=$(get_installation_token "${jwt}" "${installation_id}")

    # Optional: Verify token
    if [[ "${VERIFY_TOKEN:-false}" == "true" ]]; then
        verify_token "${token}"
    fi

    log_info "=== Token Ready ==="

    # Output only the token to stdout
    echo "${token}"
}

# Run main
main "$@"
