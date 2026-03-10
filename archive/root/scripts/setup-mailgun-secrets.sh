#!/usr/bin/env bash
# setup-mailgun-secrets.sh — Add Mailgun secrets to GitHub repository
# Run this script locally where gh CLI is authenticated
#
# Usage: ./scripts/setup-mailgun-secrets.sh
#
# Prerequisites:
#   - gh CLI installed and authenticated
#   - Repository write access

set -euo pipefail

REPO="${GITHUB_REPOSITORY:-jgtolentino/odoo-ce}"

echo "=== Setting Mailgun secrets for $REPO ==="

# Prompt for secrets (don't hardcode sensitive values)
read -sp "Enter MAILGUN_API_KEY (Odoo key): " MAILGUN_API_KEY
echo
read -sp "Enter MAILGUN_WEBHOOK_SIGNING_KEY: " MAILGUN_WEBHOOK_SIGNING_KEY
echo
read -sp "Enter MAILGUN_SMTP_PASSWORD: " MAILGUN_SMTP_PASSWORD
echo

# Non-sensitive config (can be set directly)
MAILGUN_DOMAIN="mg.insightpulseai.com"
MAILGUN_SMTP_SERVER="smtp.mailgun.org"
MAILGUN_SMTP_PORT="587"
MAILGUN_SMTP_USER="postmaster@mg.insightpulseai.com"

echo "Setting GitHub secrets..."

# Set secrets
echo "$MAILGUN_API_KEY" | gh secret set MAILGUN_API_KEY --repo "$REPO"
echo "$MAILGUN_WEBHOOK_SIGNING_KEY" | gh secret set MAILGUN_WEBHOOK_SIGNING_KEY --repo "$REPO"
echo "$MAILGUN_SMTP_PASSWORD" | gh secret set MAILGUN_SMTP_PASSWORD --repo "$REPO"
echo "$MAILGUN_DOMAIN" | gh secret set MAILGUN_DOMAIN --repo "$REPO"
echo "$MAILGUN_SMTP_SERVER" | gh secret set MAILGUN_SMTP_SERVER --repo "$REPO"
echo "$MAILGUN_SMTP_PORT" | gh secret set MAILGUN_SMTP_PORT --repo "$REPO"
echo "$MAILGUN_SMTP_USER" | gh secret set MAILGUN_SMTP_USER --repo "$REPO"

echo "=== GitHub secrets configured ==="
gh secret list --repo "$REPO" | grep -i mailgun || true

echo ""
echo "Secrets added:"
echo "  - MAILGUN_API_KEY"
echo "  - MAILGUN_WEBHOOK_SIGNING_KEY"
echo "  - MAILGUN_SMTP_PASSWORD"
echo "  - MAILGUN_DOMAIN"
echo "  - MAILGUN_SMTP_SERVER"
echo "  - MAILGUN_SMTP_PORT"
echo "  - MAILGUN_SMTP_USER"
