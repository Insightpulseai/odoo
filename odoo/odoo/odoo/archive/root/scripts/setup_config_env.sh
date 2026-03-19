#!/bin/bash
# Auto-configure environment from existing ~/.zshrc secrets
# NO PROMPTS - reads what's already there

set -euo pipefail

echo "📋 Reading existing credentials from environment..."

# Mail (from .zshrc if exists)
export ODOO_SMTP_HOST="${ZOHO_SMTP_HOST:-smtp.zoho.com}"
export ODOO_SMTP_PORT="${ZOHO_SMTP_PORT:-587}"
export ODOO_SMTP_USER="${ZOHO_SMTP_USER:-business@insightpulseai.com}"
export ODOO_SMTP_PASS="${ZOHO_SMTP_PASS:-${MAIL_PASSWORD:-}}"
export ODOO_SMTP_TLS="true"

export ODOO_IMAP_HOST="${ZOHO_IMAP_HOST:-imap.zoho.com}"
export ODOO_IMAP_PORT="${ZOHO_IMAP_PORT:-993}"
export ODOO_IMAP_USER="$ODOO_SMTP_USER"
export ODOO_IMAP_PASS="$ODOO_SMTP_PASS"
export ODOO_IMAP_SSL="true"

# AI (from .zshrc)
export IPAI_AI_ENDPOINT_URL="${SUPABASE_URL:-https://spdtwktxdalcfigzeqrz.supabase.co}/functions/v1/docs-ai-ask"
export IPAI_AI_API_KEY="${SUPABASE_SERVICE_ROLE_KEY:-}"

# OCR (default to localhost PaddleOCR)
export IPAI_OCR_ENDPOINT_URL="${OCR_ENDPOINT_URL:-http://localhost:8000/ocr}"
export IPAI_OCR_API_KEY="${OCR_API_KEY:-}"

# Verify we have minimum required
if [ -z "$ODOO_SMTP_PASS" ]; then
  echo "⚠️  WARNING: ODOO_SMTP_PASS not set (check ~/.zshrc for ZOHO_SMTP_PASS or MAIL_PASSWORD)"
fi

if [ -z "$IPAI_AI_API_KEY" ]; then
  echo "⚠️  WARNING: IPAI_AI_API_KEY not set (check ~/.zshrc for SUPABASE_SERVICE_ROLE_KEY)"
fi

echo "✅ Environment configured from existing credentials"
echo "   SMTP: $ODOO_SMTP_USER @ $ODOO_SMTP_HOST"
echo "   AI:   ${IPAI_AI_ENDPOINT_URL}"
echo "   OCR:  ${IPAI_OCR_ENDPOINT_URL}"
