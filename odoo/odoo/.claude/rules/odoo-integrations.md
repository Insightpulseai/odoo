---
paths:
  - "mcp/**"
  - "n8n/**"
  - "apps/mcp-jobs/**"
---

# Integrations: MCP, n8n, Slack, Claude, Figma

> MCP servers catalog, MCP Jobs system, n8n automation, Slack ChatOps, Claude integration, Figma.

---

## MCP Servers

### Architecture

```
Claude Desktop / VS Code / Agents
        |
MCP Coordinator (port 8766)
    |                    |
External MCPs       Custom MCPs
(Supabase, GitHub)  (Odoo, Superset)
```

**Configuration:** `.mcp.json` (repo root -- canonical project-scoped config)

### External MCP Servers (install via npx)

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

### Custom MCP Servers (Audited 2026-03-08)

| Server | Purpose | Location | Status |
|--------|---------|----------|--------|
| `plane` | Plane.so project management integration | `mcp/servers/plane/` | **Live** |

> Previously documented servers not found in codebase (confirmed missing 2026-03-08):
> odoo-erp-server, digitalocean-mcp-server, superset-mcp-server, vercel-mcp-server,
> pulser-mcp-server, speckit-mcp-server, mcp-jobs. These are **planned** but not yet implemented.
> The `mcp-jobs` app exists in `apps/mcp-jobs/` as a Next.js app, not as an MCP server.

---

## MCP Jobs System

**Repository**: `git@github.com:jgtolentino/mcp-jobs.git` (standalone service)
**Submodule**: `mcp/servers/mcp-jobs/` (integrated into odoo-ce)
**Deployed**: https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/
**Purpose**: Shared job orchestration + observability for all MCP-enabled apps

### Architecture

```
MCP-Enabled Apps (Odoo, n8n, Vercel, Edge Functions)
    | HTTP POST /api/jobs/enqueue
v0 Next.js App (mcp-jobs UI)
    | Supabase Client
Supabase PostgreSQL (mcp_jobs schema)
    +-- jobs (queue + state machine)
    +-- job_runs (execution history)
    +-- job_events (detailed logs)
    +-- dead_letter_queue (failed jobs after max retries)
    +-- metrics (aggregated stats)
```

### Core Components

**Database Schema** (`mcp_jobs`):
- **jobs**: Main job queue (queued -> processing -> completed | failed | cancelled)
- **job_runs**: Execution history for each run/retry
- **job_events**: Detailed event log
- **dead_letter_queue**: Failed jobs after max retries exhausted
- **metrics**: Aggregated job metrics per hour

**RPCs** (Supabase functions):
- `enqueue_job()`, `claim_next_job()` (atomic with SKIP LOCKED), `complete_job()`, `fail_job()`

**API Routes** (Next.js):
- POST `/api/jobs/enqueue`, GET `/api/jobs/list`, GET `/api/jobs/[id]`, DELETE `/api/jobs/[id]`

### Integration Patterns

**From Odoo** (Python):
```python
import os, requests
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def enqueue_discovery_job(source: str, payload: dict):
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/enqueue_job",
        headers={
            'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        json={'p_source': source, 'p_job_type': 'discovery', 'p_payload': payload, 'p_priority': 5}
    )
    response.raise_for_status()
    return response.json()
```

**From n8n** (HTTP Request node): Use `{{ $env.SUPABASE_URL }}/rest/v1/rpc/enqueue_job` with headerAuth.

**From Vercel App**: Use `enqueueJob()` from `@/lib/supabaseJobsClient`.

### Monitoring

**Alert Thresholds**:
- **Critical**: Queue depth >100 jobs, DLQ >10 unresolved, success rate <80%
- **Warning**: Queue depth >50 jobs, DLQ >5 unresolved, success rate <90%

**Documentation**: `docs/infra/MCP_JOBS_SYSTEM.md`, `docs/infra/VERCEL_AI_GATEWAY_INTEGRATION.md`

---

## n8n Automation Layer

```
n8n.insightpulseai.com
  GitHub Webhooks (via pulser-hub app)
  +-- Push to main -> Deploy to erp.insightpulseai.com
  +-- PR opened -> Odoo task + Slack notification
  +-- Issue labeled "ai" -> Claude Code agent workflow
  +-- @claude comment -> Queue for AI processing
  +-- CI failure -> Immediate Slack alert

  Scheduled Jobs
  +-- Daily: Export Actions logs -> Supabase audit_logs
  +-- Weekly: Dependency update digest -> Email
  +-- Monthly: Compliance report -> Superset snapshot
```

### Event Routing

```javascript
const event = headers['x-github-event'];
switch(event) {
  case 'push':
    if (payload.ref === 'refs/heads/main') return { action: 'deploy' };
    break;
  case 'pull_request':
    return { action: 'create_odoo_task', pr: payload.pull_request };
  case 'issue_comment':
    if (payload.comment.body.includes('@claude'))
      return { action: 'queue_claude', issue: payload.issue };
    break;
}
```

---

## Slack ChatOps

- Slack workspace for team communication
- Claude installed in Slack for AI assistance
- Webhooks for alerts and notifications
- AI assistant integrations

---

## Claude Integration

### Claude in Slack
- Direct chat: Message Claude in Apps section
- Channel mentions: @Claude in channels
- Combined with GitHub: @claude in PR comments -> n8n -> processing

### Claude Code MCP
```bash
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx \
  -- npx -y @anthropic-ai/mcp-server-github
```

---

## Figma Dev Mode Access

**Prerequisites:** Dev seat or Full seat on a paid Figma plan.

| Seat Type | Dev Mode | Variables API | Code Connect |
|-----------|----------|---------------|--------------|
| Full      | Yes      | Enterprise    | Yes          |
| Dev       | Yes      | Enterprise    | Yes          |
| Collab    | No       | No            | No           |
| View-only | No       | No            | No           |

**Setup Commands:**
```bash
export FIGMA_ACCESS_TOKEN=figd_xxxxxxxxxxxxx
export FIGMA_FILE_KEY=your_file_key_here
./scripts/figma/verify_dev_mode_access.sh
npm install --global @figma/code-connect@latest
npx figma connect publish --token="$FIGMA_ACCESS_TOKEN"
./scripts/figma/figma_export_variables.sh  # Enterprise only
```

**Hotkey:** Toggle Dev Mode with `Shift + D`

---

*Last updated: 2026-03-16*
