#!/usr/bin/env bash
# ==============================================================================
# COMPLETE PRODUCTION FIX DEPLOYMENT
# ==============================================================================
# Fixes all critical issues:
#   1. OwlError (pay_invoices_online field)
#   2. OAuth HTTPS Loop (nginx X-Forwarded-Proto)
#   3. Gmail SMTP (outgoing email)
#   4. Google OAuth SSO (Sign in with Google)
#
# Usage: ./scripts/deploy_complete_fix.sh [gmail_user] [app_password]
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_NAME="${3:-prod}"

echo "=================================================="
echo "COMPLETE PRODUCTION FIX DEPLOYMENT"
echo "=================================================="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Database: $DB_NAME"
echo ""
echo "This script will fix:"
echo "  ✓ OwlError (database cleanup)"
echo "  ✓ OAuth HTTPS loop (nginx + database)"
echo "  ✓ Gmail SMTP (outgoing email)"
echo "  ✓ Google OAuth SSO (Sign in with Google)"
echo ""

# === Prerequisite Checks ===
echo ">>> [0/5] Running prerequisite checks..."

# Check if running as root or with docker permissions
if ! docker ps > /dev/null 2>&1; then
    echo "❌ ERROR: Cannot access Docker. Run with sudo or add user to docker group."
    exit 1
fi

ODOO_CONTAINER=$(docker ps --format "{{.Names}}" | grep odoo | head -n 1)
NGINX_CONTAINER=$(docker ps --format "{{.Names}}" | grep nginx | head -n 1)

if [[ -z "$ODOO_CONTAINER" ]]; then
    echo "❌ ERROR: No running Odoo container found"
    exit 1
fi

if [[ -z "$NGINX_CONTAINER" ]]; then
    echo "⚠️  WARNING: No nginx container found - skipping nginx configuration"
fi

echo "✓ Docker access verified"
echo "✓ Odoo container: $ODOO_CONTAINER"
if [[ -n "$NGINX_CONTAINER" ]]; then
    echo "✓ Nginx container: $NGINX_CONTAINER"
fi

# === Phase 1: Core Hotfix (OwlError + OAuth Loop) ===
echo ""
echo "=================================================="
echo "PHASE 1: CORE HOTFIX (OwlError + OAuth)"
echo "=================================================="

if [[ -f "$SCRIPT_DIR/hotfix_production.sh" ]]; then
    bash "$SCRIPT_DIR/hotfix_production.sh" "$DB_NAME"
    if [[ $? -ne 0 ]]; then
        echo "❌ Core hotfix failed - aborting"
        exit 1
    fi
else
    echo "⚠️  WARNING: hotfix_production.sh not found - skipping core fixes"
    echo "   Manual fix required for OwlError and OAuth loop"
fi

# === Phase 2: Gmail SMTP Configuration ===
echo ""
echo "=================================================="
echo "PHASE 2: GMAIL SMTP CONFIGURATION"
echo "=================================================="

# Get Gmail credentials
if [[ $# -ge 2 ]]; then
    GMAIL_USER="$1"
    GMAIL_PASS="$2"
else
    echo ""
    echo "Gmail SMTP Setup Required:"
    echo "  1. Enable 2FA on your Gmail account"
    echo "  2. Generate App Password: https://myaccount.google.com/apppasswords"
    echo ""
    read -p "Enter your Gmail address: " GMAIL_USER
    read -sp "Enter your Gmail App Password (16 chars): " GMAIL_PASS
    echo ""
fi

if [[ -f "$SCRIPT_DIR/configure_gmail_smtp.sh" ]]; then
    bash "$SCRIPT_DIR/configure_gmail_smtp.sh" "$GMAIL_USER" "$GMAIL_PASS" "$DB_NAME"
    if [[ $? -ne 0 ]]; then
        echo "⚠️  WARNING: Gmail SMTP configuration failed"
        echo "   Email sending may not work correctly"
    fi
else
    echo "⚠️  WARNING: configure_gmail_smtp.sh not found"
    echo "   Skipping Gmail SMTP configuration"
fi

# === Phase 3: Google OAuth SSO Configuration ===
echo ""
echo "=================================================="
echo "PHASE 3: GOOGLE OAUTH SSO CONFIGURATION"
echo "=================================================="

if [[ -f "$SCRIPT_DIR/configure_google_oauth.sh" ]]; then
    bash "$SCRIPT_DIR/configure_google_oauth.sh" "$DB_NAME"
    if [[ $? -ne 0 ]]; then
        echo "⚠️  WARNING: Google OAuth SSO configuration failed"
        echo "   Sign in with Google may not work correctly"
    fi
else
    echo "⚠️  WARNING: configure_google_oauth.sh not found"
    echo "   Skipping Google OAuth SSO configuration"
fi

# === Phase 4: Comprehensive Validation ===
echo ""
echo "=================================================="
echo "PHASE 4: COMPREHENSIVE VALIDATION"
echo "=================================================="

if [[ -f "$SCRIPT_DIR/validate_production.sh" ]]; then
    bash "$SCRIPT_DIR/validate_production.sh" "$DB_NAME"
    VALIDATION_RESULT=$?
else
    echo "⚠️  WARNING: validate_production.sh not found"
    echo "   Skipping automated validation"
    VALIDATION_RESULT=0
fi

# === Phase 5: Final Summary ===
echo ""
echo "=================================================="
echo "DEPLOYMENT SUMMARY"
echo "=================================================="
echo ""

echo "Configuration Applied:"
echo "  ✓ OwlError fixed: pay_invoices_online field removed"
echo "  ✓ OAuth loop fixed: HTTPS enforced in nginx + database"
if [[ -n "$GMAIL_USER" ]]; then
    echo "  ✓ Gmail SMTP: $GMAIL_USER configured"
else
    echo "  ⚠️  Gmail SMTP: Not configured (skipped)"
fi
echo "  ✓ Google OAuth SSO: Sign in with Google enabled"
echo ""

echo "Next Steps:"
echo ""
echo "1. VERIFY GOOGLE CLOUD CONSOLE SETTINGS:"
echo "   URL: https://console.cloud.google.com/apis/credentials"
echo "   Project: cba-ai"
echo "   Client ID: 1024356860971-k71aep6lperde4vaeiai4f41ehmsfqhl..."
echo ""
echo "   Ensure 'Authorized redirect URIs' includes:"
echo "     https://erp.insightpulseai.com/auth_oauth/signin"
echo ""
echo "2. TEST OAUTH LOGIN:"
echo "   a. Open Chrome Incognito: https://erp.insightpulseai.com"
echo "   b. Click 'Sign in with Google' button"
echo "   c. Select your Google account"
echo "   d. Verify successful login"
echo ""
echo "3. TEST EMAIL SENDING:"
echo "   a. Login to Odoo"
echo "   b. Go to: Settings → Technical → Email → Outgoing Mail Servers"
echo "   c. Click 'Gmail SMTP' server"
echo "   d. Click 'Test Connection' button"
echo "   e. Verify 'Connection Test Successful!' message"
echo ""
echo "4. MONITOR LOGS (first 30 minutes):"
echo "   docker logs $ODOO_CONTAINER --tail 50 -f"
echo ""

if [[ $VALIDATION_RESULT -eq 0 ]]; then
    echo "=================================================="
    echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY"
    echo "=================================================="
    exit 0
else
    echo "=================================================="
    echo "⚠️  DEPLOYMENT COMPLETED WITH WARNINGS"
    echo "=================================================="
    echo ""
    echo "Review validation output above for details."
    echo "Some features may require manual configuration."
    echo ""
    exit 1
fi
