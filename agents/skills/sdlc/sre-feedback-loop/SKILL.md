# Skill: SRE Feedback Loop

## Metadata

| Field | Value |
|-------|-------|
| **id** | `sre-feedback-loop` |
| **domain** | `sdlc` |
| **source** | Microsoft Agentic SDLC pattern (Phase 5) |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, automations, infra |
| **tags** | sre, observability, incident-response, sub-agents, day-2-ops |

---

## Pattern

An SRE agent continuously watches production telemetry. When anomalies or incidents are detected, it creates structured specs/issues that feed back into the coding agent loop — closing the SDLC circle without human intervention for routine fixes.

---

## Architecture

```
Azure Monitor / OTLP
        ↓ telemetry stream
SRE Agent (primary)
        ↓ detects anomaly
        ├── GitHub Sub-Agent → creates issue with structured context
        ├── Triage Sub-Agent → classifies severity + blast radius
        └── Runbook Sub-Agent → checks if automated fix exists
                ↓
        ops.incidents (Supabase SSOT)
                ↓
        GitHub issue (auto-created)
                ↓
        Coding Agent (PR with fix)
                ↓
        Quality Gate → Deploy → Monitor
                ↓
        Loop closes
```

---

## Sub-Agent Pattern

The SRE agent delegates to narrow-context sub-agents. Each sub-agent has:

- **Single responsibility** — one task, one output
- **Scoped context** — only receives relevant telemetry/logs, not everything
- **Bounded execution time** — timeout after N seconds, escalate to human
- **Externalized state** — all state in `ops.run_events`, never in the agent

### Sub-Agents

| Sub-Agent | Input | Output | IPAI Location |
|-----------|-------|--------|---------------|
| GitHub issue creator | Anomaly context | GitHub issue URL | `agents/subagents/git-expert/` |
| Severity classifier | Error logs + metrics | Severity enum + blast radius | `agents/subagents/devops-expert/` |
| Runbook matcher | Incident type | Matching runbook or "none" | `agents/runbooks/` |
| Fix validator | PR diff + test results | Pass/fail + evidence | CI quality gate |

---

## Incident Schema (ops.incidents)

```sql
CREATE TABLE IF NOT EXISTS ops.incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES ops.tenants(id),
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL DEFAULT 'low'
        CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'investigating', 'mitigating', 'resolved', 'closed')),
    source TEXT NOT NULL DEFAULT 'manual'
        CHECK (source IN ('manual', 'sre_agent', 'monitor_alert', 'user_report')),
    telemetry_context JSONB DEFAULT '{}',
    github_issue_number INTEGER,
    spec_id UUID REFERENCES ops.specs(id),
    resolution_pr_number INTEGER,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_incidents_status ON ops.incidents(status);
CREATE INDEX idx_incidents_severity ON ops.incidents(severity);
CREATE INDEX idx_incidents_source ON ops.incidents(source);
```

---

## Telemetry Sources (IPAI Stack)

| Source | Signal | Collection |
|--------|--------|------------|
| Azure Container Apps | HTTP logs, container restarts, scaling events | Azure Monitor → `ops.platform_events` |
| Odoo application | Error logs, slow queries, cron failures | Sentry → `ops.platform_events` |
| PostgreSQL | Query performance, connection pool, locks | Azure PG metrics → `ops.platform_events` |
| Supabase Edge Functions | Invocation errors, latency, cold starts | Supabase logs → `ops.platform_events` |
| n8n workflows | Execution failures, timeout, credential errors | n8n webhook → `ops.platform_events` |

---

## Escalation Matrix

| Severity | Auto-fix? | Human required? | SLA |
|----------|-----------|-----------------|-----|
| Critical | No — human only | Yes, page immediately | 15 min response |
| High | If runbook exists | Yes, notify | 1 hour response |
| Medium | Yes, if confidence > 90% | Review PR before merge | 4 hour response |
| Low | Yes, auto-merge if tests pass | No | Next business day |

---

## n8n Integration Workflow

```yaml
# automations/n8n/workflows/sre-incident-to-issue.json
trigger: webhook (from Azure Monitor alert)
steps:
  1. Parse alert payload → extract service, error, severity
  2. Query ops.incidents for duplicate (dedup window: 30 min)
  3. If new: INSERT INTO ops.incidents
  4. Create GitHub issue via gh CLI
  5. If severity <= medium AND runbook exists:
     - Trigger coding agent workflow
  6. Post to Slack #ops-alerts
```

---

## Runbook Directory

Runbooks live in `agents/runbooks/` and are matched by incident type:

| Incident Type | Runbook | Auto-fixable? |
|---------------|---------|---------------|
| Container restart loop | `container-restart.md` | Yes (scale + rollback) |
| Database connection exhaustion | `pg-connection-pool.md` | Yes (kill idle, scale pool) |
| Cron job timeout | `cron-timeout.md` | Yes (extend timeout, retry) |
| Edge function cold start spike | `edge-function-cold-start.md` | No (requires code change) |
| Certificate expiry | `cert-renewal.md` | Yes (trigger renewal) |

---

## Related Skills

- [agentic-sdlc-msft-pattern](../agentic-sdlc-msft-pattern/SKILL.md) — Full pattern overview
- [spec-driven-development](../spec-driven-development/SKILL.md) — How incidents become specs
