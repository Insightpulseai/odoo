# Finance PPM — Implementation Plan

> **Module**: Finance PPM (Project Portfolio Management)
> **Spec bundle**: `spec/finance-ppm/`
> **Version**: 1.3.0
> **Updated**: 2026-02-24

---

## Overview

This plan covers the implementation strategy for Finance PPM v1 — 2 Odoo projects,
89 tasks, 6 Kanban stages, and the Supabase-first email notification pipeline that
routes around DigitalOcean's SMTP block.

---

## Phase 0: Seed Data & Team Setup

### 0.1 Team Directory

**Source**: `data/seed/finance_ppm/tbwa_smp/team_directory.csv`

1. Validate CSV against PRD invariants: `python scripts/finance/validate_team_directory.py`
2. Create Odoo users from CSV via `scripts/finance/import_team_directory.py`
3. Assign Finance PPM security group to all 9 users

**Gate**: `validate_team_directory.py` exits 0 before proceeding.

### 0.2 Kanban Stages

Create the 6 shared stages in this exact order:
```
1. To Do
2. In Preparation
3. Under Review
4. Pending Approval
5. Done
6. Cancelled
```

**Note**: Stages are shared across both projects. Create once, assign to both.

### 0.3 Tags (33)

Import `data/seed/finance_ppm/tbwa_smp/tags.csv` — phases I–V + 9 BIR form types +
category tags.

---

## Phase 1: Project Structure

### 1.1 IM1 — Finance PPM: Month-End Close

- **Source**: `data/seed/finance_ppm/tbwa_smp/tasks_month_end.csv`
- 39 tasks across 5 phases (I → V)
- Deadline model: Working Day (WD) offsets relative to period end
- Assign tasks per role mapping in PRD §Role→Approval Mapping

### 1.2 IM2 — Finance PPM: BIR Tax Filing

- **Source**: `data/seed/finance_ppm/tbwa_smp/tasks_bir_tax.csv`
- 50 tasks across 9 BIR form types
- Deadline model: Fixed BIR calendar dates (10th, 20th, 25th, etc.)
- Recurring: Monthly / Quarterly / Annual per form type

### 1.3 Milestones

Import `data/seed/finance_ppm/tbwa_smp/logframe.csv` — 11 logframe milestones mapped
to both projects.

---

## Phase 2: OCA Module Installation

Install in dependency order on the target Odoo 19 instance:

```bash
# OCA dependencies (verified 19.0 series)
project_task_dependency      # task predecessors/successors
project_timeline             # timeline bar view (read-only, NOT Gantt)
project_stage_closed         # Done/Cancelled distinction
```

**Parity map**: `spec/finance-ppm/parity_map.yaml`

---

## Phase 3: ipai_* Delta Modules

Install in dependency order:

```bash
ipai_enterprise_bridge       # safe EE stubs
ipai_finance_workflow        # role-based stage transitions
ipai_finance_ppm             # budget/forecast/variance + event emitter
ipai_bir_notifications       # filing deadline alerts
ipai_bir_tax_compliance      # 36 eBIRForms support
```

### Module: `ipai_finance_ppm` — Event Emitter

The `project_task_integration.py` model posts webhook events to Supabase
`webhook-ingest` on task lifecycle transitions:

| Odoo Event | Trigger |
|------------|---------|
| `finance_task.created` | Task assigned (user_ids set) |
| `finance_task.in_progress` | Stage → In Preparation |
| `finance_task.submitted` | Stage → Under Review |
| `finance_task.approved` | Stage → Pending Approval |
| `finance_task.filed` | Stage → Done |

**Payload** (added in v1.3.0):
```python
{
    "task_id": int,
    "task_name": str,
    "project_name": str,
    "new_stage": str,
    "assignee_emails": [str],   # required by email enqueue trigger
    "write_date_unix": int,
}
```

---

## Phase 4: Platform Bridges

### 4.1 Supabase Email Notification Pipeline (v1.3.0)

**Context**: DigitalOcean blocks outbound SMTP (ports 25/465/587) on all Droplets by
default. Email is routed through Supabase Edge Functions (unrestricted outbound TCP).

#### Database Migrations (apply in order)

| Migration | Purpose |
|-----------|---------|
| `supabase/migrations/20260225000001_email_notification_queue.sql` | `ops.email_notification_events` table + `claim_email_notifications()` RPC |
| `supabase/migrations/20260225000002_email_deliveries.sql` | `ops.email_deliveries` audit table |
| `supabase/migrations/20260225000003_email_enqueue_trigger.sql` | Trigger on `ops.webhook_events` → enqueues per-recipient rows |
| `supabase/migrations/20260225000004_email_rls.sql` | RLS: service-role only on both tables |

**Apply command**:
```bash
supabase db push --project-ref spdtwktxdalcfigzeqrz
```

**Verify**:
```sql
SELECT count(*) FROM ops.email_notification_events; -- 0, no error
SELECT count(*) FROM ops.email_deliveries;           -- 0, no error
```

#### Edge Functions (deploy)

| Function | Role |
|----------|------|
| `supabase/functions/email-dispatcher/` | Claim → render → send via zoho-mail-bridge → mark done/fail |
| `supabase/functions/tick/` | Orchestrator (already deploys jobs-worker; now also wakes email-dispatcher) |

**Deploy command**:
```bash
supabase functions deploy email-dispatcher --project-ref spdtwktxdalcfigzeqrz
supabase functions deploy tick --project-ref spdtwktxdalcfigzeqrz
```

#### Required Supabase Edge Function Secrets

Set via Supabase dashboard or CLI before deploying:

```bash
supabase secrets set BRIDGE_SHARED_SECRET=<value> --project-ref spdtwktxdalcfigzeqrz
supabase secrets set ZOHO_FROM_EMAIL=noreply@insightpulseai.com --project-ref spdtwktxdalcfigzeqrz
```

**Note**: `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`, `ZOHO_ACCOUNT_ID`
are already set (required by `zoho-mail-bridge`).

#### Architecture (Flow)

```
Odoo ipai_finance_ppm (project_task_integration.py)
  → send_ipai_event() ← payload includes assignee_emails, project_name, new_stage
  → POST https://spdtwktxdalcfigzeqrz.functions.supabase.co/functions/v1/webhook-ingest
  → INSERT ops.webhook_events (payload JSONB stores full event body)
  → TRIGGER ops.enqueue_email_notifications() AFTER INSERT
    → reads event_type from NEW.payload->>'event_type'  ← IMPORTANT: NOT NEW.event_type (NULL for Odoo)
    → reads inner task data from NEW.payload->'payload'
    → INSERT per-recipient rows into ops.email_notification_events
  → supabase/functions/tick (cron: every N minutes)
    → fire-and-forget → supabase/functions/email-dispatcher
      → claim_email_notifications(p_batch=10)
      → render template (task_assigned | task_stage_changed)
      → POST zoho-mail-bridge?action=send_email
        body: {from, to, subject, htmlBody}
        header: x-bridge-secret
      → mark sent / schedule retry / mark dead
      → INSERT ops.email_deliveries (audit)
  → Zoho Mail API → recipient inbox
```

#### Enqueue Trigger: Critical Implementation Note

`ops.webhook_events.event_type` is **NULL** for Odoo events. The `webhook-ingest`
function's `inferEventType()` reads `payload?.type ?? payload?.event`, not
`payload?.event_type`. The trigger reads the event type from the JSONB body:

```sql
v_event_type := NEW.payload->>'event_type';
```

Not from the column:
```sql
-- WRONG — always NULL for Odoo events:
-- v_event_type := NEW.event_type;
```

#### Smoke Test

```sql
-- 1. Insert test webhook event
INSERT INTO ops.webhook_events (integration, idempotency_key, payload)
VALUES (
  'odoo', 'test-email-001',
  '{"event_type":"finance_task.created","aggregate_type":"finance_task","aggregate_id":"1",
    "payload":{"task_id":1,"task_name":"Test Task","project_name":"Finance PPM",
               "new_stage":"In Preparation",
               "assignee_emails":["test@insightpulseai.com"],
               "write_date_unix":1740000000}}'
);

-- 2. Verify enqueue trigger fired
SELECT id, recipient_email, template, status
FROM ops.email_notification_events
WHERE idempotency_key LIKE 'email:%';
-- Expected: 1 row, status=pending

-- 3. Verify idempotency (re-insert same ikey → still 1 row)
-- (trigger uses ON CONFLICT DO NOTHING)

-- 4. Invoke dispatcher
-- supabase functions invoke email-dispatcher --project-ref spdtwktxdalcfigzeqrz

-- 5. Verify sent
SELECT status FROM ops.email_notification_events ORDER BY id DESC LIMIT 1;
-- Expected: sent

-- 6. Verify delivery audit
SELECT * FROM ops.email_deliveries ORDER BY id DESC LIMIT 1;
-- Expected: 1 row, provider=zoho, status=sent
```

### 4.2 n8n Recurrent Alerts

- **Trigger**: Cron 9AM + 5PM PHT
- **Purpose**: Due/overdue/handover Slack alerts
- **Location**: `automations/n8n/workflows/` (Finance PPM alert workflow)

### 4.3 BIR Form Generation

- **Trigger**: Weekly + Webhook
- **Purpose**: Generate `.dat` files for eBIRForms
- **Location**: `platform/bridges/bir-form-generation/`

### 4.4 Compliance Dashboard (Superset)

- **11 SQL views** in Superset covering operational + logframe KPIs
- Views 1–6: Operational (task summary, funnel, workload, timeline, tax calendar, team)
- Views 7–11: Logframe KPIs with RAG status (GREEN/AMBER/RED)
- **Location**: `platform/bridges/compliance-dashboard/`

---

## Phase 5: Validation

### 5.1 Quality Gates

Run in CI or locally before marking complete:

```bash
python scripts/finance/validate_team_directory.py
python scripts/finance/validate_seed_ssot.py
python scripts/policy/validate_parity_map.py
python scripts/validate_finance_ppm_data.py
bash scripts/test_finance_ppm_odoo19.sh
```

### 5.2 Logframe KPI Baseline

Verify RAG thresholds are reachable from current task data:

| KPI | GREEN | AMBER | Verify |
|-----|-------|-------|--------|
| On-time filing % | ≥95% | ≥80% | All IM2 tasks have deadline set |
| Avg delay | ≤1d | ≤3d | All IM1 tasks have WD offset set |
| TB reconciliation | ≥95% | ≥75% | IM1 Phase V tasks assigned to Director |
| BIR overdue | 0 | ≤2 | IM2 filing deadlines in BIR calendar |

---

## Known Gaps (v1)

| Gap | Status | ADR |
|-----|--------|-----|
| Critical path analysis | Not available in OCA 19.0 | `decisions/0006-critical-path-unavailable.md` |
| Resource leveling | Out of scope v1 | — |
| Interactive Gantt | Out of scope; OCA timeline is read-only | — |
| SMTP direct from Odoo | Blocked by DO Droplet policy (ticket pending) | Email pipeline above is the v1 workaround |
