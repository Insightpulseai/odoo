# Agent-to-Agent Orchestration & Task Bus

> Domain: `orchestration` / `agents`
> Last validated: 2026-03-15

---

## What this skill is for

Agents that need to coordinate with other agents, enqueue work, delegate tasks,
or participate in multi-agent workflows use this skill to understand the IPAI
orchestration primitives and choose the right communication pattern.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    Agent Orchestration Layer                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │ Claude  │    │  n8n    │    │ Codex   │    │ Slack   │      │
│  │ Code    │    │ Worker  │    │ Agent   │    │ Bot     │      │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘      │
│       │              │              │              │            │
│       ▼              ▼              ▼              ▼            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Supabase (Message Bus)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │   │
│  │  │ mcp_jobs.jobs │  │ ops.task_    │  │ ops.platform_ │  │   │
│  │  │ (job queue)   │  │ queue        │  │ events        │  │   │
│  │  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │   │
│  │         │                 │                   │          │   │
│  │         ▼                 ▼                   ▼          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │   │
│  │  │ run-executor │  │ Pulser       │  │ Realtime      │  │   │
│  │  │ (Edge Fn)    │  │ Connector    │  │ Subscribers   │  │   │
│  │  └──────────────┘  └──────────────┘  └───────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│       │                                        │                │
│       ▼                                        ▼                │
│  ┌─────────┐                            ┌───────────┐          │
│  │  Odoo   │                            │ Dashboard │          │
│  │ (exec)  │                            │ (observe) │          │
│  └─────────┘                            └───────────┘          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Communication Patterns

### Pattern 1: Job Queue (mcp_jobs) — Async, Durable

**When**: Agent needs to enqueue work for another agent/worker with retry, DLQ, and observability.

```
Producer → mcp_jobs.jobs → run-executor (Edge Fn) → Handler → Result
```

**Components**:
- Schema: `mcp_jobs` (Supabase)
- Tables: `jobs`, `job_runs`, `job_events`, `dead_letter_queue`, `metrics`
- RPCs: `enqueue_job()`, `claim_next_job()`, `complete_job()`, `fail_job()`
- Worker: `supabase/functions/run-executor/index.ts`
- UI: MCP Jobs dashboard (`web/apps/mcp-jobs/`)

**Enqueue from any surface**:

```typescript
// TypeScript (Next.js, Edge Functions)
import { enqueueJob } from '@ipai/taskbus'
const jobId = await enqueueJob('claude-agent', 'code-review', {
  pr_number: 42,
  repo: 'Insightpulseai/odoo'
})
```

```python
# Python (Odoo, scripts)
import requests, os
requests.post(
    f"{os.getenv('SUPABASE_URL')}/rest/v1/rpc/enqueue_job",
    headers={
        'Authorization': f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}",
        'Content-Type': 'application/json'
    },
    json={
        'p_source': 'odoo-copilot',
        'p_job_type': 'module-audit',
        'p_payload': {'module': 'ipai_helpdesk'},
        'p_priority': 5
    }
)
```

```json
// n8n HTTP Request node
{
  "url": "{{ $env.SUPABASE_URL }}/rest/v1/rpc/enqueue_job",
  "method": "POST",
  "body": {
    "p_source": "n8n",
    "p_job_type": "sync",
    "p_payload": "{{ $json }}"
  }
}
```

**State machine**:
```
queued → processing → completed
                    → failed → (retry?) → queued
                                        → dead_letter_queue
```

### Pattern 2: Pulser Intent Bus (ops.taskbus_intents) — Command/Response

**When**: Slack/API user issues a command that Odoo (or another agent) must execute.

```
Pulser (Slack) → ops.taskbus_intents → ipai_pulser_connector (Odoo cron) → Execute → Write result
```

**Components**:
- Table: `ops.taskbus_intents` (Supabase)
- Connector: `addons/ipai/ipai_pulser_connector/` (Odoo module)
- MCP Server: `agents/mcp/servers/pulser-mcp-server/`
- Contract: `docs/contracts/C-PULSER-ODOO-01.md`

**Supported intents** (read-only MVP):
- `healthcheck` — Odoo health status
- `modules.status` — Installed module list
- `config.snapshot` — Configuration snapshot

### Pattern 3: Realtime Events (ops.platform_events) — Pub/Sub

**When**: Multiple agents need to react to the same event (fan-out, observability).

```
Any agent → INSERT ops.platform_events → Supabase Realtime → All subscribers
```

**Components**:
- Table: `ops.platform_events` (append-only, never truncate)
- Subscriber: Supabase Realtime channel
- Function: `ops.record_event()`

```typescript
// Subscribe to all platform events
supabase
  .channel('platform-events')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'ops', table: 'platform_events' },
    (payload) => handleEvent(payload.new)
  )
  .subscribe()

// Emit an event
await supabase.rpc('record_event', {
  p_event_type: 'agent.task.completed',
  p_source: 'claude-code',
  p_payload: { task_id: 'xyz', result: 'success' }
})
```

### Pattern 4: A2A Coordination Server — Multi-Agent Handoff

**When**: Complex task requires decomposition across multiple specialized agents.

**Status**: Planned/Scaffolded at `agents/mcp/servers/agent-coordination-server/`

```
Orchestrator Agent
    ↓ HandoffRequest
A2A Coordinator (MCP Server)
    ├── Delegate to Agent A (specialist)
    ├── Delegate to Agent B (specialist)
    └── Aggregate results → Return to orchestrator
```

**Key types** (from `coordinator.ts`):
- `AgentMessage` — Inter-agent message envelope
- `HandoffRequest` — Transfer task to another agent
- `DelegationRequest` — Decompose and delegate subtasks
- `AgentResponse` — Standardized response format

### Pattern 5: n8n Workflow Orchestration — Visual, Event-Driven

**When**: Cross-domain coordination with visual workflow builder.

```
GitHub webhook → n8n → (Odoo + Supabase + Slack) in parallel
```

**Live workflows**:
- `plane-odoo-sync.json` — Bi-directional Plane ↔ Odoo task sync
- `github-webhook-router.json` — Route GitHub events to appropriate handlers
- `figma-webhook-receiver.json` — Ingest Figma design changes

---

## Decision Matrix: Which Pattern to Use

| Need | Pattern | Why |
|------|---------|-----|
| Durable async job with retry | Job Queue (mcp_jobs) | Built-in retry, DLQ, metrics |
| Slack command → Odoo execution | Pulser Intent Bus | Claim/execute contract |
| Fan-out notifications | Realtime Events | Append-only, multiple subscribers |
| Multi-agent task decomposition | A2A Coordinator | Handoff/delegation protocol |
| Cross-domain event chain | n8n Workflow | Visual, webhook-triggered |
| Simple request/response | Direct Supabase RPC | Lowest latency, no queue overhead |

---

## TypeScript Packages

### @ipai/taskbus (`web/packages/taskbus/`)

Core task bus framework. Enqueue, idempotency, policy guardrails.

```typescript
import { TaskBus } from '@ipai/taskbus'

const bus = new TaskBus({ supabaseUrl, supabaseKey })
await bus.enqueue({
  source: 'agent-a',
  jobType: 'analyze',
  payload: { target: 'helpdesk-tickets' },
  priority: 5,
  maxRetries: 3
})
```

### @ipai/agents (`web/packages/agents/`)

Agent registry and handlers. Registers agent capabilities and routes jobs.

```typescript
import { AgentRegistry } from '@ipai/agents'

const registry = new AgentRegistry()
registry.register('code-reviewer', {
  handler: async (job) => {
    // Execute code review
    return { approved: true, comments: [] }
  },
  capabilities: ['code-review', 'lint-check']
})
```

---

## Observability

### MCP Jobs Dashboard

**URL**: https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/

**React hook** (for embedding in control room):
```typescript
import { useMCPJobs, useMCPJobStats } from '@/hooks/useMCPJobs'

function JobsDashboard() {
  const { data: jobs } = useMCPJobs({ status: 'processing' })
  const { data: stats } = useMCPJobStats()
  // stats: { queued, processing, completed, failed, dlqCount }
}
```

### Key Metrics

```sql
-- Queue depth by source
SELECT source, status, COUNT(*) FROM mcp_jobs.jobs
WHERE status IN ('queued', 'processing')
GROUP BY source, status;

-- Success rate (7-day)
SELECT source,
  COUNT(*) FILTER (WHERE status = 'completed') AS ok,
  COUNT(*) FILTER (WHERE status = 'failed') AS fail,
  ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'completed') / COUNT(*), 1) AS rate
FROM mcp_jobs.jobs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY source;

-- Dead letter queue
SELECT source, job_type, error_message, created_at
FROM mcp_jobs.dead_letter_queue
WHERE NOT resolved
ORDER BY created_at DESC;
```

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Queue depth | >50 | >100 |
| DLQ unresolved | >5 | >10 |
| Success rate | <90% | <80% |
| Job age (processing) | >5min | >15min |

---

## SSOT/SOR Mapping

| Entity | SOR | SSOT | Notes |
|--------|-----|------|-------|
| `mcp_jobs.jobs` | Supabase | Supabase | Job queue state machine |
| `ops.taskbus_intents` | Supabase | Supabase | Pulser command queue |
| `ops.platform_events` | Supabase | Supabase | Append-only event log |
| Agent registry | Code (`@ipai/agents`) | Code | Agent capabilities |
| n8n workflows | n8n JSON exports | Repo (`infra/n8n/workflows/`) | Exported back to git |

---

## Anti-Patterns

1. **Direct Odoo-to-Odoo RPC for async work** — Use the job queue instead. Odoo cron is not a reliable message bus.
2. **Storing agent state in Odoo** — Agent coordination state lives in Supabase. Odoo is the execution surface, not the orchestrator.
3. **Polling Supabase from Odoo in a loop** — Use the cron-based claim pattern (`ipai_pulser_connector`) instead.
4. **Skipping the DLQ** — All job failures must flow through the dead letter queue for post-mortem.
5. **Hardcoding agent URLs** — Use the agent registry (`@ipai/agents`) for capability-based routing.
6. **n8n as the sole orchestrator** — n8n handles event-driven cross-domain flows. For agent-to-agent coordination, use the A2A Coordinator or job queue.

---

## When to use this skill

- Building a new agent that needs to talk to other agents
- Adding a new job type to the mcp_jobs queue
- Implementing Pulser intent handling in Odoo
- Setting up Realtime event subscriptions
- Designing multi-agent workflows
- Debugging job queue issues (stuck jobs, DLQ growth)

## When NOT to use this skill

- Single-agent tasks (no coordination needed)
- Odoo-internal workflows (use Odoo stages/activities)
- ETL pipeline orchestration → use `databricks-data-engineering` skill
- CI/CD pipeline coordination → use `azure-pipelines` skill
