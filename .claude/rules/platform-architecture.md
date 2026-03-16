# Platform Architecture

> Architecture overview, cost philosophy, Docker setup, hosting, and integration points.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   InsightPulse AI Stack (Self-Hosted)                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Slack (SaaS) ◄──► n8n ◄──► Odoo CE 19 ◄──► PostgreSQL 16          │
│       │             │          (8069)                                │
│       │             │                                                │
│       │             └──────────► Supabase (external integrations)    │
│       │                                                              │
│       └───────────────────────► AI Agents (Pulser, Claude, Codex)   │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  Superset (BI)  │  Keycloak (SSO)  │  Azure (Hosting)               │
└─────────────────────────────────────────────────────────────────────┘
```

## Cost-Minimized Self-Hosted Philosophy

**We BUILD everything ourselves to minimize costs:**
- NO expensive SaaS subscriptions
- NO per-seat enterprise licensing

**Self-hosted stack:**
- **Hosting**: Azure Container Apps (behind Azure Front Door)
- **Database**: PostgreSQL 16 (Azure managed)
- **BI**: Apache Superset (free, self-hosted)
- **SSO**: Keycloak (free, self-hosted — transitional to Entra)
- **Automation**: n8n (self-hosted, not cloud)
- **Chat**: Slack (SaaS - replaces deprecated Mattermost)

---

## Docker Architecture

**Development Stack** (sandbox/dev):
- **Odoo CE 19**: Single container with EE parity (port 8069)
- **PostgreSQL 16**: Database backend (port 5433 external, 5432 internal)
- **Optional Tools**: pgAdmin (5050), Mailpit (8025) via `--profile tools`

**Production Stack** may include additional specialized containers per deployment environment.

---

## Integration Points

### n8n Workflows

- Located in `n8n/` directory
- Deploy with: `./scripts/deploy-n8n-workflows.sh`
- Activate with: `./scripts/activate-n8n-workflows.sh`

### Slack ChatOps

- Slack workspace for team communication
- Claude installed in Slack for AI assistance
- Webhooks for alerts and notifications
- AI assistant integrations

### MCP Servers

**Architecture:**
```
Claude Desktop / VS Code / Agents
        ↓
MCP Coordinator (port 8766)
    ↓                    ↓
External MCPs       Custom MCPs
(Supabase, GitHub)  (Odoo, DO, Superset)
```

**Configuration:** `.mcp.json` (repo root — canonical project-scoped config)

**External MCP Servers (install via npx):**

| Server | Purpose | Required Env |
|--------|---------|--------------|
| `@supabase/mcp-server` | Schema, SQL, functions | `SUPABASE_ACCESS_TOKEN` |
| `@modelcontextprotocol/server-github` | Repos, PRs, workflows | `GITHUB_TOKEN` |
| `dbhub-mcp-server` | Direct Postgres access | `POSTGRES_URL` |
| `@anthropic/figma-mcp-server` | Design tokens, components | `FIGMA_ACCESS_TOKEN` |
| `@notionhq/notion-mcp-server` | Workspace docs, PRDs | `NOTION_API_KEY` |
| `@anthropic/firecrawl-mcp-server` | Web scraping, ETL | `FIRECRAWL_API_KEY` |
| `@huggingface/mcp-server` | Models, datasets | `HF_TOKEN` |
| `@anthropic/playwright-mcp-server` | Browser automation | (none) |

**Custom MCP Servers (in `mcp/servers/`) — Audited 2026-03-08:**

| Server | Purpose | Location | Status |
|--------|---------|----------|--------|
| `plane` | Plane.so project management integration | `mcp/servers/plane/` | **Live** |

> **Previously documented servers not found in codebase** (confirmed missing 2026-03-08):
> odoo-erp-server, digitalocean-mcp-server, superset-mcp-server, vercel-mcp-server,
> pulser-mcp-server, speckit-mcp-server, mcp-jobs. These are **planned** but not yet implemented.
> The `mcp-jobs` app exists in `apps/mcp-jobs/` as a Next.js app, not as an MCP server.

---

*Last updated: 2026-03-16*
