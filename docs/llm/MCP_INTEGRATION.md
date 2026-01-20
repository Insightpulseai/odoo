# MCP Integration Guide

> **Purpose**: Model Context Protocol configuration for LLM agents.
> **Protocol**: MCP (Anthropic standard)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Desktop / VS Code                     │
│                              │                                   │
│                              ▼                                   │
│                    MCP Coordinator (:8766)                       │
│                    ┌─────────┴─────────┐                        │
│                    ▼                   ▼                         │
│            External MCPs         Custom MCPs                     │
│         ┌──────────────────┐  ┌──────────────────┐              │
│         │ @supabase/mcp    │  │ odoo-erp-server  │              │
│         │ @github/mcp      │  │ pulser-server    │              │
│         │ dbhub-mcp        │  │ speckit-server   │              │
│         └──────────────────┘  └──────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## MCP Server Registry

### External Servers (npm)

| Server | Package | Purpose |
|--------|---------|---------|
| Supabase | `@supabase/mcp-server` | Schema, SQL, functions |
| GitHub | `@modelcontextprotocol/server-github` | Repos, PRs, issues |
| DBHub | `dbhub-mcp-server` | Direct Postgres access |
| Figma | `@anthropic/figma-mcp-server` | Design tokens |
| Notion | `@notionhq/notion-mcp-server` | Workspace docs |
| Playwright | `@anthropic/playwright-mcp-server` | Browser automation |

### Custom Servers (in-repo)

| Server | Location | Purpose |
|--------|----------|---------|
| odoo-erp-server | `mcp/servers/odoo-erp-server/` | Odoo CE integration |
| digitalocean-mcp-server | `mcp/servers/digitalocean-mcp-server/` | DO infrastructure |
| superset-mcp-server | `mcp/servers/superset-mcp-server/` | BI dashboards |
| vercel-mcp-server | `mcp/servers/vercel-mcp-server/` | Deployments |
| pulser-mcp-server | `mcp/servers/pulser-mcp-server/` | Agent orchestration |
| speckit-mcp-server | `mcp/servers/speckit-mcp-server/` | Spec enforcement |

---

## Configuration

### Claude Desktop Config

Location: `~/.claude/mcp-servers.json` (also in `.claude/mcp-servers.json`)

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server"],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "odoo-erp": {
      "command": "node",
      "args": ["./mcp/servers/odoo-erp-server/dist/index.js"],
      "env": {
        "ODOO_URL": "https://erp.insightpulseai.net",
        "ODOO_DB": "odoo_core",
        "ODOO_API_KEY": "${ODOO_API_KEY}"
      }
    }
  }
}
```

---

## Server Groups

### Core Group (Always Active)

| Server | Capabilities |
|--------|-------------|
| supabase | `query`, `schema`, `functions` |
| github | `repos`, `issues`, `prs`, `actions` |
| dbhub | `sql`, `schema` |
| odoo-erp | `modules`, `records`, `reports` |

### Design Group (On-Demand)

| Server | Capabilities |
|--------|-------------|
| figma | `components`, `tokens`, `export` |
| notion | `pages`, `databases`, `search` |

### Infrastructure Group (On-Demand)

| Server | Capabilities |
|--------|-------------|
| digitalocean | `droplets`, `databases`, `spaces` |
| vercel | `projects`, `deployments`, `logs` |

### Automation Group (On-Demand)

| Server | Capabilities |
|--------|-------------|
| pulser | `agents`, `tasks`, `schedules` |
| speckit | `specs`, `validation`, `generation` |

---

## Available Tools by Server

### Supabase MCP

| Tool | Description |
|------|-------------|
| `query` | Execute SQL query |
| `schema` | Get table schema |
| `functions` | List/invoke edge functions |
| `storage` | Access storage buckets |

### GitHub MCP

| Tool | Description |
|------|-------------|
| `search_repos` | Search repositories |
| `get_file` | Read file contents |
| `create_issue` | Create new issue |
| `create_pr` | Create pull request |
| `get_workflows` | List GitHub Actions |

### Odoo ERP MCP

| Tool | Description |
|------|-------------|
| `search_read` | Search and read records |
| `create` | Create new record |
| `write` | Update existing record |
| `execute_kw` | Execute model method |
| `get_modules` | List installed modules |

---

## Memory Integration

### Agent Memory Flow

```
Agent Action
    │
    ▼
MCP Tool Call
    │
    ▼
Tool Result
    │
    ├──► agent_mem.events (logged)
    │
    └──► Response to Agent
```

### Logging Pattern

All MCP tool calls are logged to Supabase:

```sql
-- Recent tool calls
SELECT
  e.event_type,
  e.content->>'tool' as tool,
  e.content->>'result' as result,
  e.occurred_at
FROM agent_mem.events e
WHERE e.event_type = 'tool_call'
ORDER BY e.occurred_at DESC
LIMIT 20;
```

---

## Custom Server Development

### Server Template

```typescript
// mcp/servers/my-server/src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio';

const server = new Server({
  name: 'my-server',
  version: '1.0.0',
});

// Register tools
server.tool('my_tool', {
  description: 'My custom tool',
  inputSchema: {
    type: 'object',
    properties: {
      param: { type: 'string' }
    }
  },
  handler: async ({ param }) => {
    // Implementation
    return { result: 'success' };
  }
});

// Start server
const transport = new StdioServerTransport();
server.connect(transport);
```

### Build & Register

```bash
# Build server
cd mcp/servers/my-server
npm install
npm run build

# Add to config
# Edit .claude/mcp-servers.json
```

---

## Coordinator Configuration

The MCP Coordinator aggregates multiple servers:

```yaml
# mcp/coordinator/config.yml
coordinator:
  port: 8766
  servers:
    - name: supabase
      group: core
      priority: 1
    - name: github
      group: core
      priority: 2
    - name: odoo-erp
      group: core
      priority: 3
```

---

## Security

### Token Management

| Token | Storage | Rotation |
|-------|---------|----------|
| `SUPABASE_ACCESS_TOKEN` | Vault | 90 days |
| `GITHUB_TOKEN` | Vault | 90 days |
| `ODOO_API_KEY` | Vault | 180 days |

### RLS Enforcement

All Supabase queries through MCP respect RLS:

```sql
-- MCP sessions use auth context
SET request.jwt.claims = '{"sub": "mcp-agent", "role": "service_role"}';
```

---

## Troubleshooting

### Server Won't Start

```bash
# Check server logs
npx @supabase/mcp-server 2>&1

# Verify env vars
echo $SUPABASE_ACCESS_TOKEN | head -c 20

# Test server standalone
node ./mcp/servers/odoo-erp-server/dist/index.js
```

### Tool Call Failed

```bash
# Check MCP logs
tail -f ~/.claude/logs/mcp.log

# Test tool directly
curl -X POST http://localhost:8766/tools/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT 1"}'
```

### Connection Timeout

```bash
# Check coordinator
curl http://localhost:8766/health

# Restart coordinator
pm2 restart mcp-coordinator

# Check server health
curl http://localhost:8766/servers
```
