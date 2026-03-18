# Month-End Close Task Mapping (Odoo + Supabase + Analytics)

## Overview

Authoritative mapping for Month-End Close workflow across:
- **Odoo** (System of Record - execution + compliance)
- **Supabase** (Control Plane - status, SLA, audit, rollups)
- **Analytics** (Local/Regional/Global KPI reporting)

**Source**: Month-end Closing Task.xlsx
**Last Updated**: 2026-02-12

---

## SSOT Boundaries

### 1. Odoo = System of Record (Execution + Compliance)

**Rule:** If it is *performed, approved, or audited* → Odoo owns it.

| Excel Sheet | Odoo Model | Purpose |
|------------|------------|---------|
| `Closing Task` | `project.task` | Actual close checklist execution |
| `Closing Procedures` | `knowledge.article` or `project.task` templates | SOP / procedures |
| `Tax Filing` | `account.move` + `account.tax` | VAT/withholding filings |
| `Required Modules` | `ir.module.module` refs | Ensure module coverage |
| `Odoo Import (project.task)` | **Direct import spec** | Canonical task import |

### 2. Supabase = Control Plane (Status, SLA, Audit, Rollups)

**Rule:** If it is *status, aggregation, SLA, or audit trail* → Supabase owns it.

| Excel Sheet | Supabase Table | Why |
|------------|----------------|-----|
| `Supabase Logframe CSV` | `analytics.kpi_points` | KPI rollups |
| `Summary Dashboard` | `analytics.kpi_points` (derived) | Read-only BI |
| `QA Pivot - Odoo Export` | `ops.build_events` / `audit.events` | Close QA + sign-off |
| `Data Validation` | `audit.events` | Deterministic checks |
| `Go-Live Checklist` | `ops.backups` + `audit.events` | Cutover readiness |
| `Integration Architecture` | docs only | Non-runtime |

### 3. SQLite = Local Agent Cache

**Not SSOT**. May cache:
- Task embeddings
- SOP text embeddings
- Last-run close state for agents

---

## Database Schemas

### A) Supabase Analytics (Local / Regional / Global)

**Table:** `analytics.kpi_points`

```sql
create table analytics.kpi_points (
  org_id uuid not null references registry.orgs(id),
  ts timestamptz not null default now(),
  geo_scope text not null check (geo_scope in ('local', 'regional', 'global')),
  geo_dim_id uuid,  -- references to region/country/entity
  metric_key text not null,  -- e.g. 'month_close_days', 'vat_filed'
  value numeric,
  unit text,
  dims jsonb not null default '{}'::jsonb,  -- {"month":"2026-01", "entity":"PH_MAIN"}
  created_at timestamptz not null default now()
);

create index on analytics.kpi_points (org_id, metric_key, geo_scope, ts);
```

**Mapping from Excel:**
- `Summary Dashboard` → `metric_key` values
- `Closing Task` → completion % calculations
- `Tax Filing` → compliance flag metrics

### B) Supabase Audit (Deterministic Close)

**Table:** `audit.events`

```sql
create table audit.events (
  id uuid primary key default gen_random_uuid(),
  org_id uuid references registry.orgs(id),
  actor_user_id uuid references auth.users(id),
  action text not null,  -- 'month_close.step.completed'
  target jsonb not null default '{}'::jsonb,  -- {"task_id":"...", "period":"2026-01"}
  metadata jsonb not null default '{}'::jsonb,  -- evidence refs, Odoo IDs
  created_at timestamptz not null default now()
);
```

**Rule:** Every close step completion writes **one immutable audit row**.

---

## Import Pipelines

### 1) Import Close Tasks → Odoo

**Source:** Excel sheet `Odoo Import (project.task)`

#### Step 1: Convert Excel → CSV

```bash
python3 - <<'PY'
import pandas as pd

df = pd.read_excel("Month-end Closing Task.xlsx", sheet_name="Odoo Import (project.task)")
df.to_csv("closing_tasks.csv", index=False)
print("✅ Wrote closing_tasks.csv")
PY
```

#### Step 2: Import via Odoo Shell

```bash
./odoo-bin shell -d odoo_prod <<'PY'
import csv
from odoo import api, SUPERUSER_ID

env = api.Environment(cr, SUPERUSER_ID, {})

with open("closing_tasks.csv") as f:
    reader = csv.DictReader(f)
    for r in reader:
        env['project.task'].create({
            'name': r['name'],
            'project_id': int(r['project_id']),
            'user_id': int(r['user_id']) if r['user_id'] else False,
            'date_deadline': r['date_deadline'],
        })

env.cr.commit()
print("✅ Tasks imported")
PY
```

### 2) Emit Close Status → Supabase (from Odoo)

**Method:** Edge Function or server job

```typescript
// When task completed in Odoo
await supabase.from("audit.events").insert({
  org_id,
  actor_user_id,
  action: "month_close.step.completed",
  target: {
    task_id,
    period: "2026-01"
  },
  metadata: {
    odoo_task_id,
    completed_at: new Date().toISOString()
  }
});
```

### 3) Roll-up KPIs (Local → Regional → Global)

**SQL Example:**

```sql
-- Insert KPI points for month-end close days
INSERT INTO analytics.kpi_points (
  org_id, ts, geo_scope, metric_key, value, unit, dims
) VALUES
  -- Local (Philippines Main)
  (:org, now(), 'local', 'month_close_days', 6, 'days',
   '{"entity":"PH_MAIN","period":"2026-01"}'::jsonb),

  -- Regional (Southeast Asia)
  (:org, now(), 'regional', 'month_close_days', 7, 'days',
   '{"region":"SEA","period":"2026-01"}'::jsonb),

  -- Global (All entities)
  (:org, now(), 'global', 'month_close_days', 8, 'days',
   '{"period":"2026-01"}'::jsonb);
```

---

## UI Queries

### Month-End Close Dashboard (3 Scopes)

**RPC Function:**

```sql
create or replace function analytics.ui_kpi_series(
  p_org_id uuid,
  p_metric_key text,
  p_geo_scope text,
  p_from timestamptz,
  p_to timestamptz
)
returns table (
  ts timestamptz,
  value numeric,
  unit text,
  dims jsonb
) as $$
begin
  return query
  select kp.ts, kp.value, kp.unit, kp.dims
  from analytics.kpi_points kp
  where kp.org_id = p_org_id
    and kp.metric_key = p_metric_key
    and kp.geo_scope = p_geo_scope
    and kp.ts between p_from and p_to
  order by kp.ts;
end;
$$ language plpgsql stable;
```

**TypeScript Client:**

```typescript
const { data, error } = await supabase.rpc("analytics.ui_kpi_series", {
  p_org_id: orgId,
  p_metric_key: "month_close_days",
  p_geo_scope: scope,  // 'local' | 'regional' | 'global'
  p_from: periodStart,
  p_to: periodEnd
});
```

**Fallback Strategy:**
1. Default: `local`
2. If empty → `regional`
3. If empty → `global`

---

## Key Metrics

### Month-End Close KPIs

| Metric Key | Description | Unit | Scopes |
|-----------|-------------|------|---------|
| `month_close_days` | Days to complete close | days | local, regional, global |
| `vat_filed` | VAT filing completion | boolean | local, regional |
| `close_tasks_completed` | % of tasks completed | percentage | local, regional, global |
| `reconciliation_variance` | Reconciliation variance | currency | local, regional |
| `approval_cycle_time` | Time from close to approval | hours | local, regional, global |

---

## Benefits

### ✅ Odoo executes and proves compliance
- Tasks tracked in `project.task`
- Tax filings in `account.move`
- Audit trail via Odoo's built-in mechanisms

### ✅ Supabase tracks SLA, readiness, and audit
- Immutable audit events for every close step
- KPI rollups for local/regional/global views
- Real-time status updates via Realtime

### ✅ One chart answers Local vs Regional vs Global
- Single RPC function serves all 3 scopes
- Consistent metric definitions across geographies
- Khalikl-ready analytics

### ✅ Deterministic, reproducible, agent-friendly
- Schema-based contracts
- Idempotent imports
- Clear SSOT boundaries

### ✅ Odoo.sh-grade ops visibility for finance
- Same patterns as Odoo.sh deployment tracking
- Proven information architecture
- Multi-tenant ready

---

## Next Steps

### 1. Month-End Close Dashboard Wireframe
- UI components for local/regional/global toggle
- KPI chart visualizations
- Task completion tracking

### 2. Automated Close Agent (Pulser/Codex)
- Agent workflow for close task execution
- Automatic status sync to Supabase
- Notification triggers

### 3. VAT/BIR-Specific KPIs (Philippines)
- BIR 1601-C filing deadlines
- Withholding tax compliance
- 2550Q quarterly reporting

---

## Files

- `docs/operations/MONTH_END_CLOSE_MAPPING.md` - This file
- `Month-end Closing Task.xlsx` - Source specification
- `scripts/import_close_tasks.sh` - Import automation
- `supabase/migrations/2026XXXX_month_end_close_schema.sql` - Schema migration

## References

- [Odoo Project Management](https://www.odoo.com/documentation/19.0/applications/services/project.html)
- [Supabase RPC Functions](https://supabase.com/docs/guides/database/functions)
- [Analytics KPI Schema](/Users/tbwa/Documents/GitHub/Insightpulseai/odoo/docs/arch/ANALYTICS_SCHEMA.md)
