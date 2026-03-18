# SessionStart Hook - Web Session Initialization

This hook runs when Claude Code starts a web session (Codespaces, cloud sandbox).
It ensures the environment has full CLI parity.

## Trigger
- Session start in Codespaces
- Session start in cloud sandbox
- Manual invocation via `/session-start`

## Actions

### 1. Environment Verification
```bash
# Check required tools
command -v supabase || echo "WARN: Supabase CLI not installed"
command -v gh || echo "WARN: GitHub CLI not installed"
command -v docker || echo "WARN: Docker not available"
command -v pnpm || npm install -g pnpm
```

### 2. Load Credentials
```bash
# Load from .env.local if exists
if [ -f ".env.local" ]; then
    set -a && source .env.local && set +a
    echo "Loaded credentials from .env.local"
fi

# Check Codespaces secrets
[ -n "$SUPABASE_SERVICE_ROLE_KEY" ] && echo "✓ Supabase credentials available"
[ -n "$ANTHROPIC_API_KEY" ] && echo "✓ Anthropic API key available"
[ -n "$GITHUB_TOKEN" ] && echo "✓ GitHub token available"
```

### 3. Link Supabase Project
```bash
if [ -n "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    supabase link --project-ref spdtwktxdalcfigzeqrz 2>/dev/null || true
    echo "✓ Supabase project linked"
fi
```

### 4. Initialize SuperClaude
```bash
superclaude doctor 2>/dev/null || pip install superclaude
superclaude install 2>/dev/null || true
```

### 5. Build MCP Servers (if needed)
```bash
# Build custom MCP servers if not built
for server in odoo-erp digitalocean superset vercel pulser speckit memory agent-coordination; do
    SERVER_DIR="mcp/servers/${server}-server"
    if [ -d "$SERVER_DIR" ] && [ ! -d "$SERVER_DIR/dist" ]; then
        echo "Building $server MCP server..."
        (cd "$SERVER_DIR" && npm install && npm run build) 2>/dev/null || true
    fi
done
```

### 6. Database Connection Test
```bash
# Test PostgreSQL if available
if [ -n "$POSTGRES_URL" ]; then
    psql "$POSTGRES_URL" -c "SELECT 1" >/dev/null 2>&1 && echo "✓ Database connected"
fi
```

### 7. Print Capabilities
```bash
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  IPAI Claude Code Web Session Ready                      ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Supabase: $(supabase --version 2>/dev/null || echo 'not installed')     ║"
echo "║  GitHub CLI: $(gh --version 2>/dev/null | head -1 || echo 'not installed') ║"
echo "║  Docker: $(docker --version 2>/dev/null | cut -d' ' -f3 || echo 'not available') ║"
echo "║  SuperClaude: $(superclaude version 2>/dev/null || echo 'not installed') ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Available commands:"
echo "  /plan              - Create implementation plan"
echo "  /implement         - Execute plan"
echo "  /verify            - Run verification"
echo "  /ship              - Full workflow"
echo "  /sc:research       - Deep research (SuperClaude)"
echo "  /sc:pm             - Project management"
echo ""
```

## Verification Checklist
- [ ] Supabase CLI installed and linked
- [ ] GitHub CLI authenticated
- [ ] PostgreSQL connection working
- [ ] MCP servers built
- [ ] SuperClaude commands available
- [ ] Docker available for builds

## Troubleshooting

### Missing Credentials
Set in Codespaces secrets:
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_ANON_KEY`
- `ANTHROPIC_API_KEY`

### Supabase Not Linked
```bash
supabase login
supabase link --project-ref spdtwktxdalcfigzeqrz
```

### MCP Server Build Failed
```bash
cd mcp/servers/<server-name>
npm install
npm run build
```
