# PPM Clarity — Implementation Plan

> Technical plan for Plane.so + Odoo 19 CE integration with SSOT governance.

---

## Architecture Overview

```
┌─────────────┐    webhook     ┌──────────┐    XML-RPC    ┌──────────┐
│  Plane.so   │───────────────▶│   n8n    │──────────────▶│  Odoo 19 │
│ (self-host) │◀───────────────│ workflows│◀──────────────│   CE     │
└─────────────┘   MCP/REST     └────┬─────┘   cron poll   └──────────┘
                                    │
                               ┌────▼─────┐
                               │ Supabase │
                               │   ops.*  │
                               └──────────┘
```

**Transport**: Plane MCP Server (Stdio) for outbound, webhooks for inbound.
**Orchestration**: n8n workflows for event routing and retry logic.
**SSOT**: Supabase `ops.work_item_links` + `ops.work_item_events`.

---

## Phases

### Phase 1: Spec Bundle (CURRENT)
- Create constitution, PRD, plan, tasks
- Establish governance framework

### Phase 2: Supabase Schema
- Migration: `ops.work_item_links`, `ops.work_item_events`
- RPC functions: `upsert_work_item_link`, `append_work_item_event`, `get_sync_conflicts`
- RLS policies: service_role only

### Phase 3: Integration Clients
- `scripts/ppm/odoo_client.py` — Odoo XML-RPC client
- `scripts/ppm/plane_mcp_client.py` — Plane MCP wrapper (calls `uvx plane-mcp-server`)
- `scripts/ppm/sync_engine.py` — Deterministic sync with field ownership
- `scripts/ppm/slack_notifier.py` — Slack notifications (reuses Pulser patterns)

### Phase 4: n8n Workflows
- `ppm-clarity-plane-to-odoo.json` — Webhook handler for Plane events
- `ppm-clarity-odoo-to-plane.json` — Cron-based Odoo completion sync
- `ppm-clarity-reconciliation.json` — Nightly drift repair
- `ppm-clarity-slack-commands.json` — Slash command handlers

### Phase 5: CI Guardrails
- `ppm-clarity-lint.yml` — Schema and spec validation
- `ppm-clarity-integration-test.yml` — Mocked integration tests
- Test coverage: field ownership, idempotency, conflicts, hash determinism

### Phase 6: Documentation
- `docs/ops/PPM_CLARITY_PLANE_ODOO.md` — Operational guide
- Slack integration section
- Troubleshooting runbook

---

## Critical Files (23 total)

| # | Path | Purpose |
|---|------|---------|
| 1 | `spec/ppm-clarity-plane-odoo/constitution.md` | Governance |
| 2 | `spec/ppm-clarity-plane-odoo/prd.md` | Requirements |
| 3 | `spec/ppm-clarity-plane-odoo/plan.md` | This file |
| 4 | `spec/ppm-clarity-plane-odoo/tasks.md` | Task breakdown |
| 5 | `supabase/migrations/20260305_create_ppm_clarity_schema.sql` | SSOT tables |
| 6 | `scripts/ppm/odoo_client.py` | Odoo RPC client |
| 7 | `scripts/ppm/plane_mcp_client.py` | Plane MCP wrapper |
| 8 | `scripts/ppm/sync_engine.py` | Sync with field ownership |
| 9 | `scripts/ppm/slack_notifier.py` | Slack notifications |
| 10 | `scripts/ppm/requirements.txt` | Python dependencies |
| 11-14 | `automations/n8n/workflows/ppm-clarity-*.json` | n8n workflows |
| 15-16 | `.github/workflows/ppm-clarity-*.yml` | CI guardrails |
| 17-21 | `scripts/ppm/tests/test_*.py` | Test suite |
| 22 | `.env.example` | Env var documentation |
| 23 | `docs/ops/PPM_CLARITY_PLANE_ODOO.md` | Ops guide |

---

## Verification Checklist

- [ ] Plane project creation → Odoo project provisioned
- [ ] Plane issue → In Progress → Odoo task created + link row
- [ ] Odoo task → Done → Plane state updated + event logged
- [ ] Duplicate event → idempotent (no duplicate tasks)
- [ ] Drift reconciliation → resolves per field ownership
- [ ] 100% event ledger coverage
- [ ] Slack notifications: success, failure, conflict, daily report
- [ ] Slack commands: `/ppm-retry`, `/ppm-resolve`, `/ppm-status`
- [ ] Interactive conflict resolution buttons work
- [ ] CI tests pass with >95% coverage
