# Agent Observability

> What gets traced, what never gets traced, and how to investigate failed runs.

---

## What Gets Traced

| Data | Traced | Example |
|------|--------|---------|
| Agent name | Yes | `governance-auditor` |
| Task class | Yes | `estate_audit`, `code_review`, `pipeline_trigger` |
| Repo path scope | Yes | `addons/ipai/ipai_auth_oidc/` |
| Evidence path | Yes | `docs/evidence/20260405-0641/go-live/` |
| Duration | Yes | `41300` (ms) |
| Outcome | Yes | `success` |
| Handoff target | Yes | `qa-evidence-runner` |
| Tool names (grouped) | Yes | `["Bash", "Read", "Write"]` |
| Start/end timestamps | Yes | ISO 8601 |
| Trace ID | Yes | UUID, correlates to evidence pack |

## What Never Gets Traced

| Data | Reason |
|------|--------|
| Prompt body / system prompt | Privacy, IP protection |
| File contents | Size, sensitivity |
| Secrets / passwords / tokens | Security policy (non-negotiable) |
| Environment variables matching `*_KEY`, `*_SECRET`, `*_TOKEN` | Secret patterns |
| Raw CLI output | Size, may contain secrets |
| User messages | Privacy |

## Trace Format

OTLP-compatible JSON written to `docs/evidence/<stamp>/<scope>/trace.json`:

```json
{
  "resource": {
    "service.name": "ipai-agent",
    "service.version": "1.0.0",
    "deployment.environment": "dev"
  },
  "spans": [
    {
      "traceId": "abc123...",
      "spanId": "span001",
      "name": "agent_run",
      "kind": "INTERNAL",
      "startTimeUnixNano": "...",
      "endTimeUnixNano": "...",
      "attributes": {
        "agent.name": "governance-auditor",
        "agent.task_class": "estate_audit",
        "agent.outcome": "success",
        "agent.evidence_path": "docs/evidence/20260405-0641/azure-estate/",
        "agent.duration_ms": 45000
      }
    }
  ]
}
```

## How Trace IDs Map to Evidence Packs

```
Trace ID (in trace.json)
    ↓
evidence_path attribute
    ↓
docs/evidence/<stamp>/<scope>/
    ├── trace.json         ← the trace itself
    ├── front-door-cutover.md
    ├── k6-baseline.md
    └── k6-baseline-results.json
```

Lookup directions:
- **Trace → Evidence**: read `agent.evidence_path` from span attributes
- **Evidence → Trace**: read `trace.json` in the same evidence directory

## Investigating Failed Runs

1. **Find the trace**: `docs/evidence/<stamp>/<scope>/trace.json`
2. **Check outcome**: `agent.outcome` = `failed` or `blocked`
3. **Check handoffs**: Did it delegate? Did the downstream agent also fail?
4. **Check evidence**: Is there a partial evidence file? What was the last successful step?
5. **Check git**: `git log --oneline -5` — was there a commit before failure?
6. **Check ADO**: If pipeline-related, check the build/run in Azure DevOps

## When Trace Export Is Required

Per `ssot/agents/execution_policy.yaml`:

| Run Type | Trace Required |
|----------|---------------|
| Write-capable runs | **Yes** |
| Pipeline triggering | **Yes** |
| Board mutation | **Yes** |
| Database operations | **Yes** |
| Read-only runs | Optional |
| Research queries | Optional |

---

*Policy: `ssot/agents/execution_policy.yaml`*
*Model: `docs/agents/AGENT_EXECUTION_MODEL.md`*
