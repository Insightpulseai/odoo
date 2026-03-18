#!/usr/bin/env bash
set -euo pipefail

# ========================================
# Deploy Edge Secrets to Supabase
# ========================================
# Pushes runtime secrets needed by Edge Functions
# Idempotent: safe to re-run (overwrites existing)

echo "🔐 Deploying Edge Secrets to Supabase..."

# Verify prerequisites
: "${SUPABASE_PROJECT_REF:?Error: SUPABASE_PROJECT_REF not set}"
: "${OPENAI_API_KEY:?Error: OPENAI_API_KEY not set}"
: "${ANTHROPIC_API_KEY:?Error: ANTHROPIC_API_KEY not set}"

# OCR variables - use OCR_HTTP_URL from .env.platform.local, make API key optional
OCR_BASE_URL="${OCR_BASE_URL:-${OCR_HTTP_URL:-}}"
OCR_API_KEY="${OCR_API_KEY:-none}"
: "${OCR_BASE_URL:?Error: OCR_BASE_URL or OCR_HTTP_URL not set}"

# Login and link (idempotent)
echo "→ Linking to Supabase project ${SUPABASE_PROJECT_REF}..."
supabase projects list >/dev/null 2>&1 || supabase login
supabase link --project-ref "$SUPABASE_PROJECT_REF" >/dev/null 2>&1 || true

# Derive service URLs from env or use defaults
N8N_BASE_URL="${N8N_BASE_URL:-https://n8n.insightpulseai.com}"
SUPERSET_BASE_URL="${SUPERSET_BASE_URL:-http://localhost:8088}"
MCP_BASE_URL="${MCP_BASE_URL:-https://mcp.insightpulseai.com}"

# Set secrets (overwrites if exists)
echo "→ Setting Edge Secrets..."
supabase secrets set \
  OPENAI_API_KEY="$OPENAI_API_KEY" \
  ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  OCR_BASE_URL="$OCR_BASE_URL" \
  OCR_API_KEY="$OCR_API_KEY" \
  N8N_BASE_URL="$N8N_BASE_URL" \
  SUPERSET_BASE_URL="$SUPERSET_BASE_URL" \
  MCP_BASE_URL="$MCP_BASE_URL"

echo "✅ Edge Secrets deployed successfully"
echo ""
echo "Next steps:"
echo "  1. Deploy secret-smoke function: supabase functions deploy secret-smoke"
echo "  2. Test health check: supabase functions invoke secret-smoke"
