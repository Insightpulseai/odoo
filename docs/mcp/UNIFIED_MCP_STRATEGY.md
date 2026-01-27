# Unified MCP Strategy: Single Source of Truth Across All Interfaces

**Last Updated:** 2026-01-27  
**Status:** ✅ Implemented

## Overview

This repository enforces a **single source of truth (SSOT)** for MCP server configuration across all AI interfaces:
- Claude Code CLI
- Claude Desktop
- Cursor IDE
- Antigravity (best-effort)
- Vercel/E2B Sandboxes

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Single Source of Truth                      │
│  mcp/registry/servers.yaml + secrets/schema.json             │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │  Adapter Generator    │
                │  gen_mcp_adapters.py  │
                └───────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌─────────────┐
│ Claude Code   │   │ Claude       │   │ Cursor      │
│ mcp-servers   │   │ Desktop      │   │ .cursor-mcp │
│ .json         │   │ config.json  │   │ .json       │
└───────────────┘   └──────────────┘   └─────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────┴────────┐
                    │ Capability     │
                    │ Prober         │
                    │ probe_caps.py  │
                    └────────────────┘
```

## Directory Structure

```
odoo-ce/
├── mcp/
│   ├── registry/
│   │   └── servers.yaml          # SSOT: All MCP servers + metadata
│   ├── policies/
│   │   └── safety.yaml           # Tool policies + allowlists
│   └── servers/                  # Custom MCP server implementations
│       ├── odoo-erp-server/
│       ├── superset-mcp-server/
│       └── pulser-mcp-server/
│
├── adapters/                     # Generated configs (DO NOT EDIT)
│   ├── claude-code/
│   │   └── mcp-servers.json
│   ├── claude-desktop/
│   │   └── claude_desktop_config.json
│   ├── cursor/
│   │   └── .cursor-mcp.json
│   ├── vercel-sandbox/
│   │   └── mcp-env.json
│   └── e2b/
│       └── mcp-config.json
│
├── secrets/
│   └── schema.json               # Secret names only (NO values)
│
├── capabilities/
│   └── current.json              # Capability inventory (CI-generated)
│
└── scripts/
    ├── gen_mcp_adapters.py       # Adapter generator
    └── probe_capabilities.py     # Capability prober
```

## Usage

### 1. Add New MCP Server

Edit `mcp/registry/servers.yaml`:

```yaml
external_servers:
  notion:
    type: remote
    transport: stdio
    package: "@notionhq/notion-mcp-server"
    command: "npx"
    args: ["-y", "@notionhq/notion-mcp-server"]
    tags: [docs, wiki, knowledge]
    env_required: [NOTION_API_KEY]
    documentation: "https://github.com/notionhq/notion-mcp-server"
```

### 2. Regenerate Adapters

```bash
python3 scripts/gen_mcp_adapters.py
```

This generates client-specific configs for:
- Claude Code CLI → `adapters/claude-code/mcp-servers.json`
- Claude Desktop → `adapters/claude-desktop/claude_desktop_config.json`
- Cursor → `adapters/cursor/.cursor-mcp.json`
- Vercel Sandbox → `adapters/vercel-sandbox/mcp-env.json`
- E2B Sandbox → `adapters/e2b/mcp-config.json`

### 3. Probe Capabilities

```bash
python3 scripts/probe_capabilities.py
```

Verifies all MCP servers are available and generates `capabilities/current.json`.

### 4. CI Enforcement

The `.github/workflows/mcp-capabilities.yml` workflow:
1. Validates YAML/JSON syntax
2. Regenerates adapters
3. Probes capabilities
4. Fails if required servers unavailable

## Secret Management

### Storage Priority (No Duplication)

1. **Primary:** Shell RC files (`~/.zshrc`, `~/.bashrc`)
2. **Backup:** Encrypted vault (1Password, SOPS, Doppler)
3. **CI/Sandbox:** Environment variables (GitHub Secrets, Vercel Env)

### Schema-Only Approach

`secrets/schema.json` contains **names and formats only**:

```json
{
  "required": {
    "github": {
      "GITHUB_TOKEN": {
        "description": "GitHub personal access token",
        "required_for": ["github"],
        "format": "ghp_... or github_pat_..."
      }
    }
  }
}
```

**Never commit actual tokens.**

## Client-Specific Behavior

| Interface | MCP Support | Config Location | Notes |
|-----------|-------------|-----------------|-------|
| Claude Code CLI | ✅ Full | `adapters/claude-code/mcp-servers.json` | All servers |
| Claude Desktop | ✅ Full | `adapters/claude-desktop/claude_desktop_config.json` | Local STDIO only |
| Cursor | ✅ Full | `adapters/cursor/.cursor-mcp.json` | Project-level MCP |
| Antigravity | ⚠️ Limited | (best-effort) | Community reports limitations |
| Claude.ai Web | ❌ Remote-only | N/A | Approved connectors only |
| Vercel Sandbox | ✅ Remote | `adapters/vercel-sandbox/mcp-env.json` | Execution substrate |
| E2B Sandbox | ✅ Remote | `adapters/e2b/mcp-config.json` | Docker MCP Gateway |

## Safety Policies

### Allowed Tool Combinations

See `mcp/policies/safety.yaml`:

```yaml
allowed_combinations:
  - [supabase, github]  # Safe: DB + VCS
  - [vercel, github]    # Safe: Deploy + VCS

dangerous_combinations:
  - [supabase, local-filesystem]  # Risk: DB + file access
  - [github, local-filesystem]    # CVE-2024-XXXXX
```

### Context-Based Restrictions

```yaml
contexts:
  production:
    allowed_servers: [supabase, github, vercel, digitalocean, odoo-erp, superset]
    forbidden_servers: [pulser]  # No agent orchestration in prod
```

## Troubleshooting

### Adapter Generation Fails

```bash
# Verify YAML syntax
python3 -c "import yaml; yaml.safe_load(open('mcp/registry/servers.yaml'))"

# Check for missing dependencies
pip install pyyaml
```

### Capability Probe Fails

```bash
# Check if npx is available
which npx || npm install -g npx

# Build custom servers
cd mcp/servers/odoo-erp-server && npm run build
cd mcp/servers/superset-mcp-server && npm run build
cd mcp/servers/pulser-mcp-server && npm run build
```

### Server Not Available in Client

1. Verify server in registry: `mcp/registry/servers.yaml`
2. Regenerate adapters: `python3 scripts/gen_mcp_adapters.py`
3. Copy adapter to client location:
   ```bash
   # Claude Desktop
   cp adapters/claude-desktop/claude_desktop_config.json \
      ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Claude Code
   cp adapters/claude-code/mcp-servers.json \
      ~/.claude/mcp-servers.json
   ```

## Best Practices

### ✅ Do

- Add new servers to `mcp/registry/servers.yaml` only
- Use `gen_mcp_adapters.py` to regenerate configs
- Commit generated adapters to repo
- Run capability probe in CI
- Store secrets in encrypted vaults

### ❌ Don't

- Edit `adapters/*/*.json` files manually
- Commit secrets to `secrets/` directory
- Duplicate server definitions across clients
- Skip capability probing in CI

## References

- [Model Context Protocol Docs](https://modelcontextprotocol.io/docs)
- [Claude Code MCP Guide](https://code.claude.com/docs/en/mcp)
- [Vercel MCP Server](https://vercel.com/docs/mcp/vercel-mcp)
- [Security Advisory: Git MCP Server](https://www.techradar.com/pro/security/anthropics-official-git-mcp-server-had-some-worrying-security-flaws)
