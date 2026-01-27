# MCP Quick Start: 5-Minute Setup

**Goal:** Get unified MCP working across Claude Code, Claude Desktop, and Cursor.

## 1. Generate Adapters (30 seconds)

```bash
cd /Users/tbwa/odoo-ce
python3 scripts/gen_mcp_adapters.py
```

**Output:**
```
✅ Generated adapters/claude-code/mcp-servers.json
✅ Generated adapters/claude-desktop/claude_desktop_config.json
✅ Generated adapters/cursor/.cursor-mcp.json
```

## 2. Install Adapters (1 minute)

```bash
# Claude Desktop
cp adapters/claude-desktop/claude_desktop_config.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Claude Code CLI
cp adapters/claude-code/mcp-servers.json \
   ~/.claude/mcp-servers.json

# Cursor (project-level)
cp adapters/cursor/.cursor-mcp.json \
   .cursor-mcp.json
```

## 3. Configure Secrets (2 minutes)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Supabase
export SUPABASE_ACCESS_TOKEN="sbp_..."
export SUPABASE_PROJECT_REF="spdtwktxdalcfigzeqrz"

# GitHub
export GITHUB_TOKEN="ghp_..."

# Vercel
export VERCEL_TOKEN="..."

# DigitalOcean
export DIGITALOCEAN_API_TOKEN="dop_v1_..."
```

Reload shell:
```bash
source ~/.zshrc
```

## 4. Verify (1 minute)

```bash
# Check capability inventory
python3 scripts/probe_capabilities.py
```

Expected output:
```
📊 MCP Server Inventory:
  Total: 7
  Available: 4  # External servers only (npx available)
  Unavailable: 3  # Custom servers need build

✅ All required MCP servers available
```

## 5. Test in Claude Code

```bash
# Ask Claude Code to use MCP
echo "Use the Supabase MCP server to list databases" | claude-code
```

## Done! 🎉

All interfaces now use the **same MCP registry**.

**Next Steps:**
- Read [UNIFIED_MCP_STRATEGY.md](./UNIFIED_MCP_STRATEGY.md) for full details
- Add custom servers to `mcp/registry/servers.yaml`
- Run `gen_mcp_adapters.py` after registry changes
