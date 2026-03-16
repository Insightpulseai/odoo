#!/bin/bash
# =============================================================================
# Web Session Initialization Script
# =============================================================================
# Run this at the start of a Claude Code web session (Codespaces/sandbox)
# to ensure full CLI parity with local development.
#
# Usage:
#   ./scripts/web_session_init.sh
#   source ./scripts/web_session_init.sh  # To export vars to current shell
# =============================================================================

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_ok() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_fail() { echo -e "${RED}✗${NC} $1"; }

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      IPAI Claude Code Web Session Initialization             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# =============================================================================
# 1. Load Credentials
# =============================================================================
log_info "Loading credentials..."

if [ -f ".env.local" ]; then
    set -a
    source .env.local
    set +a
    log_ok "Loaded .env.local"
elif [ -f ".env" ]; then
    set -a
    source .env
    set +a
    log_ok "Loaded .env"
else
    log_warn "No .env file found - using environment variables"
fi

# Check critical env vars
CREDS_OK=true
[ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ] && log_ok "SUPABASE_SERVICE_ROLE_KEY" || { log_warn "SUPABASE_SERVICE_ROLE_KEY missing"; CREDS_OK=false; }
[ -n "${SUPABASE_ANON_KEY:-}" ] && log_ok "SUPABASE_ANON_KEY" || log_warn "SUPABASE_ANON_KEY missing"
[ -n "${GITHUB_TOKEN:-}" ] && log_ok "GITHUB_TOKEN" || log_warn "GITHUB_TOKEN missing"
[ -n "${POSTGRES_URL:-}" ] && log_ok "POSTGRES_URL" || log_warn "POSTGRES_URL missing"

# =============================================================================
# 2. Check Required Tools
# =============================================================================
echo ""
log_info "Checking tools..."

check_tool() {
    if command -v "$1" &>/dev/null; then
        VERSION=$("$1" --version 2>/dev/null | head -1 || echo "installed")
        log_ok "$1: $VERSION"
        return 0
    else
        log_warn "$1: not found"
        return 1
    fi
}

check_tool git
check_tool gh || log_info "Install: sudo apt install gh"
check_tool supabase || log_info "Install: npm install -g supabase"
check_tool docker || log_info "Docker not available in this environment"
check_tool pnpm || { log_info "Installing pnpm..."; npm install -g pnpm 2>/dev/null || true; }
check_tool python3
check_tool node

# =============================================================================
# 3. Link Supabase Project
# =============================================================================
echo ""
log_info "Linking Supabase project..."

export SUPABASE_PROJECT_REF="${SUPABASE_PROJECT_REF:-spdtwktxdalcfigzeqrz}"
export SUPABASE_URL="${SUPABASE_URL:-https://spdtwktxdalcfigzeqrz.supabase.co}"

if command -v supabase &>/dev/null && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
    supabase link --project-ref "$SUPABASE_PROJECT_REF" 2>/dev/null && log_ok "Supabase linked" || log_warn "Supabase link failed"
else
    log_warn "Skipping Supabase link (CLI or credentials missing)"
fi

# =============================================================================
# 4. Install SuperClaude
# =============================================================================
echo ""
log_info "Setting up SuperClaude..."

if command -v superclaude &>/dev/null; then
    superclaude doctor 2>/dev/null && log_ok "SuperClaude healthy"
    superclaude install 2>/dev/null && log_ok "SuperClaude commands installed" || true
else
    log_info "Installing SuperClaude..."
    pip install superclaude 2>/dev/null || true
    superclaude install 2>/dev/null || true
fi

# =============================================================================
# 5. Test Database Connection
# =============================================================================
echo ""
log_info "Testing database connection..."

if [ -n "${POSTGRES_URL:-}" ]; then
    if psql "$POSTGRES_URL" -c "SELECT 1" >/dev/null 2>&1; then
        log_ok "Database connected"

        # Check migration count
        MIGRATION_COUNT=$(psql "$POSTGRES_URL" -t -A -c "SELECT COUNT(*) FROM supabase_migrations.schema_migrations" 2>/dev/null || echo "0")
        log_info "Applied migrations: $MIGRATION_COUNT"
    else
        log_warn "Database connection failed"
    fi
else
    log_warn "No POSTGRES_URL - skipping database check"
fi

# =============================================================================
# 6. Build MCP Servers (if needed)
# =============================================================================
echo ""
log_info "Checking MCP servers..."

MCP_SERVERS=("odoo-erp-server" "memory-mcp-server" "agent-coordination-server")
for server in "${MCP_SERVERS[@]}"; do
    SERVER_DIR="mcp/servers/$server"
    if [ -d "$SERVER_DIR" ]; then
        if [ -d "$SERVER_DIR/dist" ]; then
            log_ok "$server: built"
        else
            log_info "Building $server..."
            (cd "$SERVER_DIR" && npm install && npm run build) 2>/dev/null && log_ok "$server: built" || log_warn "$server: build failed"
        fi
    fi
done

# =============================================================================
# 7. Verify Repository Health
# =============================================================================
echo ""
log_info "Running repository health check..."

if [ -x "./scripts/repo_health.sh" ]; then
    ./scripts/repo_health.sh 2>/dev/null && log_ok "Repository healthy" || log_warn "Health check had warnings"
else
    log_warn "repo_health.sh not found or not executable"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Session Ready                             ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  Slash Commands:                                             ║"
echo "║    /plan           - Create implementation plan              ║"
echo "║    /implement      - Execute plan                            ║"
echo "║    /verify         - Run verification                        ║"
echo "║    /ship           - Full workflow                           ║"
echo "║                                                              ║"
echo "║  SuperClaude:                                                ║"
echo "║    /sc:research    - Deep research                           ║"
echo "║    /sc:implement   - Code implementation                     ║"
echo "║    /sc:pm          - Project management                      ║"
echo "║                                                              ║"
echo "║  Supabase:                                                   ║"
echo "║    supabase db push        - Push migrations                 ║"
echo "║    supabase functions deploy - Deploy edge functions         ║"
echo "║    supabase status         - Check project                   ║"
echo "║                                                              ║"
echo "║  Scripts:                                                    ║"
echo "║    ./scripts/verify_supabase_full.sh - Full verification     ║"
echo "║    ./scripts/deploy_production.sh    - Production deploy     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Export key variables for the session
export IPAI_SESSION_INITIALIZED=true
export IPAI_SESSION_TIME=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
