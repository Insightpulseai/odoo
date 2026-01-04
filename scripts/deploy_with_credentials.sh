#!/usr/bin/env bash
# ==============================================================================
# SECURE DEPLOYMENT WITH STORED CREDENTIALS
# ==============================================================================
# Uses credentials from .env.smtp file for secure deployment
#
# Usage: ./scripts/deploy_with_credentials.sh
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$REPO_ROOT/.env.smtp"

echo "=================================================="
echo "SECURE DEPLOYMENT WITH STORED CREDENTIALS"
echo "=================================================="
echo ""

# === Load credentials from .env.smtp ===
if [[ -f "$ENV_FILE" ]]; then
    echo "✓ Loading credentials from .env.smtp"
    source "$ENV_FILE"
else
    echo "❌ ERROR: .env.smtp file not found"
    echo ""
    echo "Create .env.smtp from template:"
    echo "  cp .env.smtp.example .env.smtp"
    echo "  nano .env.smtp  # Edit with your credentials"
    echo ""
    exit 1
fi

# === Validate credentials loaded ===
if [[ -z "${GMAIL_USER:-}" ]] || [[ -z "${GMAIL_APP_PASSWORD:-}" ]]; then
    echo "❌ ERROR: GMAIL_USER or GMAIL_APP_PASSWORD not set in .env.smtp"
    exit 1
fi

# Clean app password (remove spaces)
CLEAN_APP_PASSWORD=$(echo "$GMAIL_APP_PASSWORD" | tr -d ' ')

echo "Gmail Account: $GMAIL_USER"
echo "App Password:  ${CLEAN_APP_PASSWORD:0:4}****${CLEAN_APP_PASSWORD: -4}"
echo ""

# === Run complete deployment ===
if [[ -f "$SCRIPT_DIR/deploy_complete_fix.sh" ]]; then
    echo "Starting deployment..."
    echo ""
    bash "$SCRIPT_DIR/deploy_complete_fix.sh" "$GMAIL_USER" "$CLEAN_APP_PASSWORD"
else
    echo "❌ ERROR: deploy_complete_fix.sh not found"
    exit 1
fi
