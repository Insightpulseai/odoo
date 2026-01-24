#!/usr/bin/env bash
# validate_github_app.sh - Validate GitHub App configuration
# Usage: ./scripts/ci/validate_github_app.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$REPO_ROOT/packages/github-app/GITHUB_APP_CONFIG.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "GitHub App Configuration Validator"
echo "============================================"
echo ""

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq not installed, using basic validation${NC}"
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Check config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}ERROR: Configuration file not found: $CONFIG_FILE${NC}"
    exit 1
fi

echo "Config file: $CONFIG_FILE"
echo ""

if $JQ_AVAILABLE; then
    APP_ID=$(jq -r '.app_id' "$CONFIG_FILE")
    CLIENT_ID=$(jq -r '.client_id' "$CONFIG_FILE")
    HOMEPAGE_URL=$(jq -r '.urls.homepage' "$CONFIG_FILE")
    CALLBACK_URL=$(jq -r '.urls.callback' "$CONFIG_FILE")
    WEBHOOK_URL=$(jq -r '.urls.webhook' "$CONFIG_FILE")

    echo "Expected GitHub App Settings:"
    echo "----------------------------------------------"
    echo "  App ID:       $APP_ID"
    echo "  Client ID:    $CLIENT_ID"
    echo "  Homepage URL: $HOMEPAGE_URL"
    echo "  Callback URL: $CALLBACK_URL"
    echo "  Webhook URL:  $WEBHOOK_URL"
    echo ""
fi

# Validate URLs are reachable (basic check)
echo "URL Reachability Check:"
echo "----------------------------------------------"

check_url() {
    local url=$1
    local name=$2
    local expected_code=${3:-200}

    # Skip if URL contains placeholder or is null
    if [[ "$url" == "null" ]] || [[ "$url" == *"your_"* ]]; then
        echo -e "  ${YELLOW}SKIP${NC} $name (not configured)"
        return 0
    fi

    # Only check HTTPS URLs
    if [[ "$url" != https://* ]]; then
        echo -e "  ${YELLOW}SKIP${NC} $name (not HTTPS)"
        return 0
    fi

    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")

    if [[ "$code" == "000" ]]; then
        echo -e "  ${RED}FAIL${NC} $name - Connection failed"
        return 1
    elif [[ "$code" -ge 200 ]] && [[ "$code" -lt 400 ]]; then
        echo -e "  ${GREEN}PASS${NC} $name - HTTP $code"
        return 0
    else
        echo -e "  ${YELLOW}WARN${NC} $name - HTTP $code"
        return 0
    fi
}

if $JQ_AVAILABLE; then
    check_url "$HOMEPAGE_URL" "Homepage URL" || true
    check_url "$CALLBACK_URL" "Callback URL" || true
    check_url "$WEBHOOK_URL" "Webhook URL" || true
fi

# Check Supabase Edge Function
SUPABASE_FUNC="https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/github-app-auth"
check_url "$SUPABASE_FUNC" "Supabase Edge Function" || true

# Check n8n webhooks
N8N_BASE="https://n8n.insightpulseai.net"
check_url "$N8N_BASE" "n8n Base URL" || true

echo ""
echo "Environment Variables Check:"
echo "----------------------------------------------"

check_env() {
    local var=$1
    local required=$2

    if [[ -n "${!var:-}" ]]; then
        echo -e "  ${GREEN}SET${NC}  $var"
    elif [[ "$required" == "true" ]]; then
        echo -e "  ${RED}MISS${NC} $var (required)"
    else
        echo -e "  ${YELLOW}MISS${NC} $var (optional)"
    fi
}

# Check key environment variables
check_env "APP_ID" "true"
check_env "WEBHOOK_SECRET" "true"
check_env "PRIVATE_KEY" "true"
check_env "GITHUB_CLIENT_ID" "false"
check_env "GITHUB_CLIENT_SECRET" "false"
check_env "SUPABASE_URL" "false"
check_env "SUPABASE_SERVICE_KEY" "false"

echo ""
echo "============================================"
echo "Configuration Summary"
echo "============================================"
echo ""

if $JQ_AVAILABLE; then
    echo "To configure the GitHub App correctly, update these settings"
    echo "at https://github.com/settings/apps/pulser-hub:"
    echo ""
    echo "  Homepage URL:  $HOMEPAGE_URL"
    echo "  Callback URL:  $CALLBACK_URL"
    echo "  Webhook URL:   $WEBHOOK_URL"
    echo ""
    echo "Webhook events to enable:"
    jq -r '.webhook_events[]' "$CONFIG_FILE" | while read -r event; do
        echo "  - $event"
    done
    echo ""
    echo "Permissions required:"
    jq -r '.permissions | to_entries[] | "  - \(.key): \(.value)"' "$CONFIG_FILE"
fi

echo ""
echo "Done."
