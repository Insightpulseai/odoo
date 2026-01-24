# Odoo-Supabase Master Pattern

> **GitHub as Control Plane** | **Supabase as State/Event Bus** | **n8n as Orchestrator + MCP Host** | **Odoo as ERP** | **Docker as Runtime** | **Vercel as UI Surface**

---

## Overview

This document describes the canonical integration pattern for combining Odoo CE, Supabase, Docker, Vercel, MCP, and GitHub CI/CD into a cohesive automation platform.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MASTER PATTERN ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│   │   GitHub    │────▶│    n8n      │────▶│   Odoo CE   │                   │
│   │  (Control)  │     │ (Orchestr)  │     │   (ERP)     │                   │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                   │
│          │                   │                   │                          │
│          ▼                   ▼                   ▼                          │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│   │   Vercel    │     │  Supabase   │     │   Docker    │                   │
│   │ (UI/Preview)│     │ (State/Bus) │     │  (Runtime)  │                   │
│   └─────────────┘     └─────────────┘     └─────────────┘                   │
│                              │                                              │
│                              ▼                                              │
│                       ┌─────────────┐                                       │
│                       │  MCP Tools  │                                       │
│                       │  (Agents)   │                                       │
│                       └─────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### A) GitHub = Control Plane

**Role**: CI/CD orchestration, policy enforcement, release management

**High-Value Patterns**:
1. **PR Preview Stack**: Vercel Preview + Supabase Preview Branch + n8n smoke tests
2. **Branch Protection as Policy**: Tests, spec-kit gates, secret scanning, module install tests
3. **Patch Pipeline**: Hotfix PRs → CI gates → release → deploy → verify → audit log

**Key Workflows**:
| Workflow | Purpose |
|----------|---------|
| `ci.yml` | Unified CI with all quality gates |
| `patch-release.yml` | Hotfix → gates → release → deploy → verify |
| `ops-ci-router.yml` | Health scoring + Mattermost routing |

### B) Supabase = State + Audit + Job Queue

**Role**: Platform database, event bus, observability backend

**High-Value Patterns**:
1. **ops schema**: runs, run_events, artifacts, approvals, environment locks
2. **RLS**: Hard separation by schema boundary (prod data vs ops logs)
3. **Preview branches**: Schema-only by default; seed controlled test fixtures

**Key Tables** (`mcp_jobs` schema):
| Table | Purpose |
|-------|---------|
| `jobs` | Main queue with state machine |
| `job_runs` | Execution history per run |
| `job_events` | Detailed event logs |
| `dead_letter_queue` | Failed jobs after retries |
| `metrics` | Hourly aggregates |

### C) n8n = Orchestrator + MCP Tool Host

**Role**: Workflow automation, ChatOps, agent tool provider

**High-Value Patterns**:
1. **ChatOps**: `/deploy`, `/hotfix`, `/backfill`, `/reindex` → approvals → pipelines
2. **MCP Server**: Expose safe tools to agents (create PR, run tests, deploy, rollback)
3. **System Glue**: Odoo ↔ Supabase ↔ GitHub ↔ Vercel ↔ Slack

**Key Workflows**:
| Workflow | Purpose |
|----------|---------|
| `github-router.json` | Route GitHub events to appropriate handlers |
| `chatops-hotfix.json` | `/hotfix <issue>` → PR → gates → deploy |
| `n8n_tenant_provisioning.json` | Multi-step tenant setup |

### D) Odoo = Business System-of-Record

**Role**: ERP, CRM, accounting, business workflows

**High-Value Patterns**:
1. **CDC/ETL**: Scheduled extracts (contacts/opportunities/invoices) → Supabase gold views
2. **Automation In**: Create leads/opportunities/tasks from web/app events
3. **Module Gating**: CI installs addon set on clean DB + runs smoke flows

**MCP Integration**:
- Odoo ERP Server exposes 13 tools via XML-RPC
- Accounting: journal entries, AP aging, journals list
- BIR Compliance: 1601-C forms, deadlines, batch generate

### E) Vercel = UI Surface + Previews

**Role**: Frontend hosting, preview deployments, edge functions

**High-Value Patterns**:
1. **Preview per PR**: Env vars pinned to matching Supabase branch
2. **Bot Management/WAF**: Edge rate-limiting for auth endpoints
3. **Release Immutability**: Rollback = redeploy prior build

### F) MCP = Agent Interface Standard

**Role**: Standardized tool interface for AI agents

**High-Value Patterns**:
1. **Tools over Direct DB**: Agents call tools, not production DB directly
2. **Approval-Required Actions**: Merge, deploy, join channel, bulk updates
3. **Audit Trail**: Each tool call writes to `ops.run_events`

---

## Quick Start

### 1) Start Platform Stack (Docker)

```bash
# Start Odoo + n8n + PostgreSQL
docker compose -f odoo/compose/docker-compose.platform.yml up -d

# Verify health
curl -fsS http://localhost:5678/healthz  # n8n
curl -fsS http://localhost:8069/web/health  # Odoo
```

### 2) Configure GitHub Webhook

Point GitHub webhook to n8n:
- URL: `https://your-n8n.example.com/webhook/github/router`
- Events: `push`, `pull_request`, `release`
- Secret: Store in GitHub Secrets as `WEBHOOK_SECRET`

### 3) Configure Supabase

```bash
# Link project
npx supabase link --project-ref spdtwktxdalcfigzeqrz

# Apply migrations
npx supabase db push

# Deploy edge functions
for fn in supabase/functions/*/; do
  npx supabase functions deploy "$(basename "$fn")"
done
```

### 4) Import n8n Workflows

```bash
# Via n8n API
curl -X POST "http://localhost:5678/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @n8n/workflows/github-router.json

curl -X POST "http://localhost:5678/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @n8n/workflows/chatops-hotfix.json
```

---

## ChatOps Commands

### Hotfix (Highest ROI)

```
/hotfix <issue_number> [--base=branch]
```

**Flow**:
1. n8n receives command
2. Validates issue exists
3. Creates hotfix branch from base
4. Opens draft PR with labels
5. Logs to Supabase `ops.run_events`
6. Notifies Mattermost
7. CI gates run on push
8. On approval → `patch-release.yml` deploys

**Example**:
```
/hotfix 123
```

Returns:
```
✅ Hotfix PR Created

Issue: #123
PR: https://github.com/jgtolentino/odoo-ce/pull/456
Branch: hotfix/issue-123

→ PR is in draft mode. Ready for fixes!
```

### Deploy

```
/deploy <version> [--target=staging|production]
```

### Backfill

```
/backfill <domain> --from=2026-01-01 --to=2026-01-24
```

---

## MCP Tools Reference

Tools available to AI agents via MCP protocol:

| Tool | Category | Approval |
|------|----------|----------|
| `deploy_release` | deployment | ✅ Required |
| `rollback_release` | deployment | ✅ Required |
| `create_hotfix_pr` | hotfix | No |
| `run_tests` | testing | No |
| `smoke_test` | testing | No |
| `run_migration` | database | ✅ Required |
| `seed_data` | database | No |
| `backfill_data` | database | ✅ Required |
| `odoo_install_module` | odoo | ✅ Required |
| `odoo_create_task` | odoo | No |
| `create_pr` | github | No |
| `dispatch_workflow` | github | ✅ Required |
| `get_health_status` | observability | No |
| `get_job_status` | observability | No |
| `list_recent_jobs` | observability | No |

Full specification: `mcp/tools/n8n-tools.yaml`

---

## CI/CD Gates

### Unified CI (ci.yml)

Runs on every push/PR:

1. **Policy Check**: Validate repo structure
2. **Supabase Migrations**: Order validation, SQL lint
3. **Odoo Module Install**: Smoke test with `--stop-after-init`
4. **Web Build**: Node.js lint, test, build

### Patch Release (patch-release.yml)

Triggered manually or via ChatOps:

1. **Validate**: Version format check
2. **Test**: Module install + migration validation (skippable for emergency)
3. **Release**: Create Git tag + GitHub release
4. **Build**: Docker image → GHCR
5. **Deploy**: Supabase migrations + Edge functions + Vercel
6. **Verify**: Health checks + evidence to Supabase

---

## Data Engineering Parity

This stack provides Databricks/Cloudera-like capabilities through:

### Pipelines-as-Code
- n8n workflows stored in Git
- Promoted via PR with CI gates
- Version-controlled execution history

### Medallion Architecture

| Layer | Location | Purpose |
|-------|----------|---------|
| Bronze | Supabase `raw_*` | Landing zone (webhooks, extracts, file drops) |
| Silver | Supabase `clean_*` | Cleaned/normalized (SQL transforms) |
| Gold | Supabase `gold_*` | KPI views, materialized aggregates |

### Jobs + Observability
- n8n provides scheduling and retries
- Supabase `mcp_jobs` provides queue state machine
- `ops.run_events` provides lineage and audit trail
- Mattermost/Slack notifications for failures

---

## Verification Commands

### Local Platform Smoke

```bash
# Start stack
docker compose -f odoo/compose/docker-compose.platform.yml up -d

# Check health
curl -fsS http://localhost:5678/healthz || echo "n8n down"
curl -fsS http://localhost:8069/web/health || echo "Odoo down"

# View logs
docker compose -f odoo/compose/docker-compose.platform.yml logs --tail=50
```

### CI Verification (Local)

```bash
# Python compile check
python -m compileall addons/ipai/

# Odoo version check
docker run --rm odoo:18.0 --version

# Supabase migration order
ls -1 supabase/migrations | sort | diff -u - <(ls -1 supabase/migrations)
```

### Deploy via CLI

```bash
# Dispatch deploy workflow
gh api repos/jgtolentino/odoo-ce/dispatches \
  -f event_type='deploy' \
  -f client_payload='{"ref":"main"}'

# Trigger patch release
gh workflow run patch-release.yml -f version=v1.2.3 -f deploy_target=staging
```

---

## Rollback Strategy

| Component | Rollback Method |
|-----------|-----------------|
| Vercel | Redeploy previous build (pin deployment ID) |
| Supabase | Forward-fix migration (no down-migrations in prod) |
| Odoo | Redeploy previous container image tag |
| n8n | Restore previous workflow version from Git |

```bash
# Example: Rollback Odoo to previous version
docker pull ghcr.io/jgtolentino/odoo-ce:v1.2.2
docker compose -f deploy/docker-compose.prod.yml up -d
```

---

## Security Considerations

1. **Deploy Authority**: GitHub Actions performs deploys; n8n/ChatOps only requests
2. **Short-Lived Tokens**: All n8n↔GitHub and MCP tool calls use expiring tokens
3. **Audit Trail**: Every tool call logged to `ops.run_events`
4. **RLS Enforcement**: Supabase RLS separates prod data from ops logs
5. **Secret Management**: All secrets in GitHub Secrets, never in code

---

## Files Reference

| Path | Purpose |
|------|---------|
| `odoo/compose/docker-compose.platform.yml` | Reproducible platform stack |
| `.github/workflows/patch-release.yml` | Hotfix → release → deploy pipeline |
| `n8n/workflows/github-router.json` | GitHub event routing |
| `n8n/workflows/chatops-hotfix.json` | `/hotfix` ChatOps command |
| `mcp/tools/n8n-tools.yaml` | MCP tool registry |

---

## Related Documentation

- [MCP Jobs System](./MCP_JOBS_SYSTEM.md) - Job queue backend
- [Vercel AI Gateway](./VERCEL_AI_GATEWAY_INTEGRATION.md) - LLM routing
- [n8n Orchestrator Workflow](.github/workflows/n8n-orchestrator.yml) - Workflow sync

---

*Last Updated: 2026-01-24*
