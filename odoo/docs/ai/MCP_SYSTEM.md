# MCP System
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## MCP Servers

**Architecture:**
```
Claude Desktop / VS Code / Agents
        |
MCP Coordinator (port 8766)
    |                    |
External MCPs       Custom MCPs
(Supabase, GitHub)  (Odoo, DO, Superset)
```

**Configuration:** `.claude/mcp-servers.json`

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

### Custom MCP Servers (in `mcp/servers/`)

| Server | Purpose | Location |
|--------|---------|----------|
| `odoo-erp-server` | Odoo CE accounting, BIR compliance | `mcp/servers/odoo-erp-server/` |
| `digitalocean-mcp-server` | Droplets, apps, deployments | `mcp/servers/digitalocean-mcp-server/` |
| `superset-mcp-server` | Dashboards, charts, datasets | `mcp/servers/superset-mcp-server/` |
| `vercel-mcp-server` | Projects, deployments, logs | `mcp/servers/vercel-mcp-server/` |
| `pulser-mcp-server` | Agent orchestration | `mcp/servers/pulser-mcp-server/` |
| `speckit-mcp-server` | Spec bundle enforcement | `mcp/servers/speckit-mcp-server/` |
| `mcp-jobs` | **Canonical Jobs & Observability Backend** | `mcp/servers/mcp-jobs/` |
| `agent-coordination-server` | Multi-agent coordination | `mcp/servers/agent-coordination-server/` |
| `memory-mcp-server` | Persistent agent memory | `mcp/servers/memory-mcp-server/` |

### Server Groups

- `core`: supabase, github, dbhub, odoo-erp
- `design`: figma, notion
- `infra`: digitalocean, vercel
- `automation`: pulser, speckit
- `agents`: agent-coordination, memory, mcp-jobs

### Building Custom Servers

```bash
cd mcp/servers/<server-name>
npm install
npm run build
```

---

## MCP Jobs System -- Canonical Jobs & Observability Backend

**Repository**: `git@github.com:jgtolentino/mcp-jobs.git` (standalone service)
**Submodule**: `mcp/servers/mcp-jobs/` (integrated into odoo)
**Deployed**: https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/
**Purpose**: Shared job orchestration + observability service for all MCP-enabled apps (Odoo, n8n, Vercel apps, Supabase Edge Functions)

### Architecture

```
MCP-Enabled Apps (Odoo, n8n, Vercel, Edge Functions)
    | HTTP POST /api/jobs/enqueue
v0 Next.js App (mcp-jobs UI)
    | Supabase Client
Supabase PostgreSQL (mcp_jobs schema)
    |-- jobs (queue + state machine)
    |-- job_runs (execution history)
    |-- job_events (detailed logs)
    |-- dead_letter_queue (failed jobs after max retries)
    +-- metrics (aggregated stats)
```

### Core Components

**Database Schema** (`mcp_jobs`):
- **jobs**: Main job queue with state machine (queued -> processing -> completed | failed | cancelled)
- **job_runs**: Execution history for each run/retry
- **job_events**: Detailed event log (started, progress, completed, failed)
- **dead_letter_queue**: Failed jobs after max retries exhausted
- **metrics**: Aggregated job metrics per hour

**RPCs** (Supabase functions):
- `enqueue_job()`: Add new job to queue
- `claim_next_job()`: Worker claims next available job (atomic with SKIP LOCKED)
- `complete_job()`: Mark job as completed
- `fail_job()`: Mark job as failed, retry or move to DLQ

**API Routes** (Next.js v0 app):
- POST `/api/jobs/enqueue` - Enqueue new job
- GET `/api/jobs/list` - List jobs with filters (source, jobType, status)
- GET `/api/jobs/[id]` - Get job details with runs and events
- DELETE `/api/jobs/[id]` - Cancel queued job

**TypeScript Client** (`lib/supabaseJobsClient.ts`):
- Type-safe interfaces for Job, JobRun, JobEvent
- Helper functions: `enqueueJob()`, `listJobs()`, `getJob()`, `getJobStats()`

### Integration Patterns

**From Odoo** (Python XML-RPC):
```python
import os
import requests

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def enqueue_discovery_job(source: str, payload: dict):
    """Enqueue infrastructure discovery job"""
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/enqueue_job",
        headers={
            'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        json={
            'p_source': source,
            'p_job_type': 'discovery',
            'p_payload': payload,
            'p_priority': 5
        }
    )
    response.raise_for_status()
    return response.json()
```

**From n8n Workflow** (HTTP Request node):
```json
{
  "nodes": [{
    "parameters": {
      "url": "={{ $env.SUPABASE_URL }}/rest/v1/rpc/enqueue_job",
      "authentication": "headerAuth",
      "sendBody": true,
      "bodyParameters": {
        "parameters": [
          { "name": "p_source", "value": "n8n" },
          { "name": "p_job_type", "value": "sync" },
          { "name": "p_payload", "value": "={{ $json }}" }
        ]
      }
    },
    "name": "Enqueue Job",
    "type": "n8n-nodes-base.httpRequest"
  }]
}
```

**From Vercel App** (Next.js API route):
```typescript
import { enqueueJob } from '@/lib/supabaseJobsClient'

export async function POST(req: Request) {
  const body = await req.json()
  const jobId = await enqueueJob(body.source, body.jobType, body.payload)
  return NextResponse.json({ ok: true, jobId })
}
```

### Vercel AI Gateway Integration

All LLM calls from MCP Jobs workers **MUST** route through Vercel AI Gateway for centralized model management. See `docs/infra/VERCEL_AI_GATEWAY_INTEGRATION.md` for complete integration strategy.

**Job Classification** (OpenAI GPT-4o-mini):
```typescript
import { generateText } from 'ai'

export async function classifyJobType(payload: unknown): Promise<JobType> {
  const result = await generateText({
    model: 'openai/gpt-4o-mini',
    prompt: `Classify this job payload: ${JSON.stringify(payload)}`
  })
  return result.text.trim() as JobType
}
```

**Failure Analysis** (Anthropic Claude Sonnet 4.5):
```typescript
export async function analyzeJobFailure(
  job: Job,
  error: string
): Promise<{ shouldRetry: boolean; reason: string }> {
  const result = await generateObject({
    model: 'anthropic/claude-sonnet-4.5',
    schema: z.object({
      shouldRetry: z.boolean(),
      reason: z.string()
    }),
    prompt: `Analyze this job failure: ${error}`
  })
  return result.object
}
```

### Deployment

**Supabase Schema**:
```bash
psql "$POSTGRES_URL" -f supabase/migrations/20260120_mcp_jobs_schema.sql
# OR
supabase db push
```

**Vercel App** (already deployed):
- URL: https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/
- Environment: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `NEXT_PUBLIC_SUPABASE_URL`

**Test Endpoints**:
```bash
# Enqueue test job
curl -X POST "https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/api/jobs/enqueue" \
  -H "Content-Type: application/json" \
  -d '{"source": "test", "jobType": "discovery", "payload": {"test": true}}'

# List jobs
curl "https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/api/jobs/list?limit=10"
```

### Monitoring

**Key Metrics** (SQL queries):
```sql
-- Job queue depth by source
SELECT source, status, COUNT(*) as count
FROM mcp_jobs.jobs
WHERE status IN ('queued', 'running')
GROUP BY source, status;

-- Success rate by source
SELECT source, job_type,
  COUNT(*) FILTER (WHERE status = 'completed') as completed,
  COUNT(*) FILTER (WHERE status = 'failed') as failed
FROM mcp_jobs.jobs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY source, job_type;

-- Dead letter queue (unresolved failures)
SELECT source, job_type, COUNT(*) as count
FROM mcp_jobs.dead_letter_queue
WHERE NOT resolved
GROUP BY source, job_type;
```

**Alert Thresholds**:
- **Critical**: Queue depth >100 jobs, DLQ >10 unresolved, success rate <80%
- **Warning**: Queue depth >50 jobs, DLQ >5 unresolved, success rate <90%

### Documentation

- **Complete System Docs**: `docs/infra/MCP_JOBS_SYSTEM.md`
- **AI Gateway Strategy**: `docs/infra/VERCEL_AI_GATEWAY_INTEGRATION.md`
- **Spec Kit**: `mcp/servers/mcp-jobs/spec/mcp-jobs/` (constitution, prd, plan, tasks)
