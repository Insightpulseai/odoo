# Month-End Close Implementation Guide (Dashboard + Agent + BIR Compliance)

## Overview

Complete implementation for Month-End Close automation with:
- **Dashboard** (Odoo.sh-inspired UI with local/regional/global scoping)
- **Automated Agent** (Pulser/Codex for deterministic close execution)
- **BIR Compliance** (Philippines VAT/Withholding tax tracking)

**References:**
- [Bureau of Internal Revenue - Forms](https://www.bir.gov.ph/bir-forms)
- [Grant Thornton - VAT Guidance](https://www.grantthornton.com.ph/alerts-and-publications/technical-alerts/tax-alert/2023/optional-filing-and-payment-of-monthly-vat-returns-now-allowed/)
- Source workbook: `Month-end Closing Task.xlsx`

---

## 1. Dashboard Wireframe

### 1.1 Navigation Structure

```
Ops Console (ops.insightpulseai.com)
├── Projects
├── Month-End Close ← (main section)
│   ├── Overview (/app/close)
│   ├── Tasks (/app/close/tasks)
│   ├── Compliance (/app/close/compliance)
│   └── Audit (/app/close/audit)
├── Compliance (BIR)
├── Monitoring
└── Audit
```

### 1.2 Page: `/app/close` (Overview)

**Header Section:**
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Month-End Close · Period: 2026-01 (D+0..D+10)   Scope: [Local▼] [Region▼]     │
│ Org: TBWA\SMP   Entity: PH_MAIN   Status: ON TRACK   Lock Date: 2026-02-05    │
└──────────────────────────────────────────────────────────────────────────────┘
```

**KPI Cards:**
```
┌───────────────┬───────────────┬───────────────┬───────────────┬─────────────┐
│ Tasks Done %   │ Critical Open │ BIR Due Soon   │ VAT Payable   │ Close Days  │
│  61%           │  7            │  2             │ ₱ 1,240,000   │  6.0        │
└───────────────┴───────────────┴───────────────┴───────────────┴─────────────┘
```

**Timeline & Compliance:**
```
┌──────────────────────────────┬──────────────────────────────────────────────┐
│ Close Timeline (D+ buckets)   │ Compliance Heatmap (by form)                 │
│ D+0  D+1  D+2  ...  D+10      │ 1601-C  0619-E  2550Q  SLSP ...              │
│ [█████░░░░░░░░░░] 61%         │ [🟢]     [🟡]    [🟢]   [🔴]                  │
└──────────────────────────────┴──────────────────────────────────────────────┘
```

**Workstream Lanes:**
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Workstream Lanes (from Closing Task / Logframe)                              │
│  [Payroll]  [Tax & Provisions]  [Bank Recon]  [AP/AR]  [Accruals]  [Review]  │
│  Each lane shows: Prep → Review → Approval (your sheet's 3-stage split)      │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Exceptions/Blockers:**
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Exceptions / Blockers                                                         │
│  - Missing attachment on 12 vendor bills (AP)                                │
│  - 2 unreconciled bank lines > 7 days                                        │
│  - SLSP draft not generated (VAT)                                            │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Page: `/app/close/tasks` (Task Execution)

**Filters:**
```
[Category▼] [Assignee▼] [Stage: Prep/Review/Approval] [Due Range] [Tag]
```

**Task Table:**
```
Task (Odoo project.task) | Category | Stage | Assignee | Due | Status | Evidence | SLA
- ipai_task_close_0001   | Payroll  | Prep  | Rey      | ... | Open   | 0/1      | D+2
- ipai_task_close_0002   | Payroll  | Rev   | Rey      | ... | Open   | 0/1      | D+3
- ipai_task_close_0003   | Payroll  | Appr  | Khalil   | ... | Pending| 0/1      | D+3
```

### 1.4 Page: `/app/close/compliance` (BIR Form Board)

**Quarter/Month Selector + Scope Selector**

**Form Cards (from Tax Filing sheet):**
```
┌─────────────────────────────────────────────────────────────┐
│ 2550Q · Quarterly VAT Return                                 │
│ Period: Q1 2026   Deadline: 2026-04-25 (example)             │
│ State: Draft → For Review → For Payment → Filed             │
│ KPIs: days_to_file, variance_vs_last_qtr, penalties_risk     │
│ Evidence: attachment count, payment ref, eFPS receipt        │
└─────────────────────────────────────────────────────────────┘
```

### 1.5 Page: `/app/close/audit` (Immutable Timeline)

**Events:**
- `month_close.opened`
- `month_close.step.completed` (per task)
- `bir.form.prepared` / `approved` / `paid` / `filed`
- `lock_dates.set`
- `close.completed`

---

## 2. Automated Close Agent (Pulser/Codex)

### 2.1 Repo Placement (SSOT)

- **Supabase SSOT**: `ipai-ops-platform/supabase/**`
- **Console**: `ipai-ops-console/src/app/close/**`
- **Agent Runner**: `ipai-mcp-core` (CLI) + `ipai-ops-platform` (Edge Function executor hook)

### 2.2 Agent Phases (Deterministic)

**Phase A — Bootstrap Period**
1. Determine target period (e.g., previous month) from config
2. Create/ensure `month_close_run` row (idempotent)

**Phase B — Sync Tasks**
1. Load "close tasks" from Supabase logframe table (derived from `Supabase Logframe CSV` sheet)
2. Ensure corresponding **Odoo `project.task`** exist (upsert by `task_code`)
3. Emit audit `month_close.tasks.synced`

**Phase C — Execute Checks + Collect Evidence**
1. Pull Odoo states: unreconciled bank items, draft bills, lock dates, tax report readiness
2. Upload artifacts (CSV exports, PDFs, receipts) to Supabase Storage
3. Emit audit `month_close.evidence.updated`

**Phase D — Compute KPIs**
1. Write `analytics.kpi_points` for local/regional/global rollups
2. Update "close dashboard" materialized view (or cached JSON in `ops.*`)

**Phase E — Notify**
1. Slack (if available) + Zoho email summaries
2. Optionally create issues in GitHub if failures breach SLA

### 2.3 Implementation Files

#### A) CLI Entrypoint: `scripts/month_close/run.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${SUPABASE_URL:?}"
: "${SUPABASE_SERVICE_ROLE_KEY:?}"   # server-only
: "${ODOO_URL:?}"
: "${ODOO_DB:?}"
: "${ODOO_API_KEY:?}"                # or session creds in vault

PERIOD="${1:-$(date -u -d "$(date +%Y-%m-01) -1 day" +%Y-%m)}"  # YYYY-MM previous month
SCOPE="${2:-local}"  # local|regional|global

node scripts/month_close/run.mjs "$PERIOD" "$SCOPE"
```

#### B) Node Runner: `scripts/month_close/run.mjs`

```javascript
import process from "node:process";

const [period, scope] = process.argv.slice(2);
if (!period) throw new Error("period required (YYYY-MM)");

const SUPABASE_URL = process.env.SUPABASE_URL;
const SRK = process.env.SUPABASE_SERVICE_ROLE_KEY;
const ODOO_URL = process.env.ODOO_URL;

async function supabaseRpc(fn, args) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/${fn}`, {
    method: "POST",
    headers: {
      "apikey": SRK,
      "Authorization": `Bearer ${SRK}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(args),
  });
  if (!res.ok) throw new Error(`${fn} failed: ${res.status} ${await res.text()}`);
  return res.json();
}

async function main() {
  // 1) open or load run
  const run = await supabaseRpc("ops.month_close_open", { p_period: period });

  // 2) sync tasks to Odoo (RPC will call Edge Function / webhook executor)
  await supabaseRpc("ops.month_close_sync_tasks", { p_run_id: run.id });

  // 3) compute KPIs
  await supabaseRpc("analytics.month_close_compute_kpis", {
    p_run_id: run.id,
    p_geo_scope: scope
  });

  // 4) emit summary
  await supabaseRpc("audit.append_event", {
    p_action: "month_close.completed.tick",
    p_target: { run_id: run.id, period },
    p_metadata: { scope, odoo_url: ODOO_URL }
  });

  console.log(JSON.stringify({ ok: true, run_id: run.id, period, scope }, null, 2));
}

main().catch((e) => { console.error(e); process.exit(1); });
```

### 2.4 Supabase RPC Contracts

The agent depends on these RPCs (implement in `ipai-ops-platform`):

- `ops.month_close_open(p_period)` → returns `{id, period, status}`
- `ops.month_close_sync_tasks(p_run_id)` → `{ok:true, created:N, updated:N}`
- `analytics.month_close_compute_kpis(p_run_id, p_geo_scope)` → `{ok:true, points:N}`
- `audit.append_event(p_action, p_target, p_metadata)` → `{ok:true}`

---

## 3. BIR Compliance (Philippines VAT/Withholding)

### 3.1 Forms to Model (Minimum Set)

**From official BIR listings and common compliance cycles:**

**Withholding:**
- **1601-C**: Monthly Remittance Return of Income Taxes Withheld on Compensation
- **0619-E**: Monthly Remittance Return of Creditable Income Taxes Withheld (Expanded)
- **0619-F**: Monthly Remittance Return of Final Income Taxes Withheld
- **1601-FQ**: Quarterly Remittance Return of Final Income Taxes Withheld
- **1604-E**: Annual Information Return of Income Taxes Withheld on Compensation

**VAT:**
- **2550Q**: Quarterly VAT Return
- **2550M**: Monthly VAT Declaration (optional in some regimes)

**Schedules:**
- **SLSP**: Summary List of Sales and Purchases (quarterly submissions tied to VAT cycles)

### 3.2 KPI Definitions (analytics.kpi_points)

Each KPI emits **Local/Regional/Global** versions via `geo_scope`.

#### A) Filing Timeliness KPIs

| metric_key | Definition | Source |
|-----------|------------|--------|
| `bir.days_to_deadline` | `deadline - today` (days) per form | Supabase `tax.forms` |
| `bir.filed_on_time_rate` | % forms filed on/before deadline (per period) | `tax.filings` status |
| `bir.avg_lag_days` | avg days late for late filings | `tax.filings` |
| `bir.payment_approval_cycle_days` | approval→payment elapsed | 3-step workflow sheet |

#### B) VAT KPIs

| metric_key | Definition |
|-----------|------------|
| `vat.output_tax` | output VAT total (period) |
| `vat.input_tax` | input VAT total |
| `vat.payable` | output - input - credits |
| `vat.variance_vs_prev_qtr` | % change payable vs previous quarter |
| `vat.slsp_submitted_on_time` | boolean/ratio (quarter) - SLSP required for VAT |

#### C) Withholding KPIs

| metric_key | Definition |
|-----------|------------|
| `wht.total_compensation_withheld` | from payroll / 1601-C |
| `wht.total_expanded_withheld` | from 0619-E |
| `wht.total_final_withheld` | from 0619-F / 1601-FQ |
| `wht.unremitted_risk` | amount pending beyond internal SLA |

#### D) Penalty Risk KPIs (Operational)

| metric_key | Definition |
|-----------|------------|
| `bir.penalty_risk_score` | weighted score: late days, unpaid amount, missing attachments |
| `bir.missing_evidence_count` | missing receipts, eFPS confirmations, proof-of-payment |
| `bir.audit_event_coverage` | % of required steps with immutable `audit.events` |

### 3.3 Database Schema (Supabase)

#### Tax Compliance Tables

```sql
-- tax.* is business compliance tracking (not ops monitoring)
CREATE SCHEMA IF NOT EXISTS tax;

-- Form catalog (BIR forms reference)
CREATE TABLE IF NOT EXISTS tax.forms (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id uuid NOT NULL REFERENCES registry.orgs(id) ON DELETE CASCADE,
  form_code text NOT NULL,      -- '2550Q', '1601C', '0619E', 'SLSP'
  form_name text NOT NULL,
  frequency text NOT NULL,      -- monthly|quarterly|annual
  active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Filing records (actual submissions)
CREATE TABLE IF NOT EXISTS tax.filings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id uuid NOT NULL REFERENCES registry.orgs(id) ON DELETE CASCADE,
  period text NOT NULL,         -- '2026-01' or '2026-Q1'
  form_code text NOT NULL,
  deadline date NOT NULL,
  state text NOT NULL,          -- draft|for_review|for_payment|filed|paid|late|void
  filed_at timestamptz,
  paid_at timestamptz,
  payable numeric,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tax_filings_org_period
  ON tax.filings(org_id, period, form_code);

-- Form catalog data (seed BIR forms)
INSERT INTO tax.forms (org_id, form_code, form_name, frequency) VALUES
  -- Withholding forms
  ((SELECT id FROM registry.orgs LIMIT 1), '1601-C', 'Monthly Remittance Return of Income Taxes Withheld on Compensation', 'monthly'),
  ((SELECT id FROM registry.orgs LIMIT 1), '0619-E', 'Monthly Remittance Return of Creditable Income Taxes Withheld (Expanded)', 'monthly'),
  ((SELECT id FROM registry.orgs LIMIT 1), '0619-F', 'Monthly Remittance Return of Final Income Taxes Withheld', 'monthly'),
  ((SELECT id FROM registry.orgs LIMIT 1), '1601-FQ', 'Quarterly Remittance Return of Final Income Taxes Withheld', 'quarterly'),
  ((SELECT id FROM registry.orgs LIMIT 1), '1604-E', 'Annual Information Return of Income Taxes Withheld on Compensation', 'annual'),

  -- VAT forms
  ((SELECT id FROM registry.orgs LIMIT 1), '2550Q', 'Quarterly VAT Return', 'quarterly'),
  ((SELECT id FROM registry.orgs LIMIT 1), '2550M', 'Monthly VAT Declaration', 'monthly'),

  -- Schedules
  ((SELECT id FROM registry.orgs LIMIT 1), 'SLSP', 'Summary List of Sales and Purchases', 'quarterly')
ON CONFLICT DO NOTHING;
```

### 3.4 KPI Computation RPC

```sql
CREATE OR REPLACE FUNCTION analytics.month_close_compute_kpis(
  p_run_id uuid,
  p_geo_scope text
)
RETURNS jsonb AS $$
DECLARE
  v_org_id uuid;
  v_period text;
  v_points_inserted int := 0;
BEGIN
  -- Get org and period from run
  SELECT org_id, period INTO v_org_id, v_period
  FROM ops.month_close_runs
  WHERE id = p_run_id;

  -- Compute filing timeliness KPIs
  INSERT INTO analytics.kpi_points (
    org_id, ts, geo_scope, metric_key, value, unit, dims
  )
  SELECT
    v_org_id,
    now(),
    p_geo_scope,
    'bir.filed_on_time_rate',
    (COUNT(*) FILTER (WHERE filed_at <= deadline)::numeric / NULLIF(COUNT(*), 0)) * 100,
    'percentage',
    jsonb_build_object('period', v_period)
  FROM tax.filings
  WHERE org_id = v_org_id AND period = v_period;

  v_points_inserted := v_points_inserted + 1;

  -- Compute VAT payable KPI (example)
  INSERT INTO analytics.kpi_points (
    org_id, ts, geo_scope, metric_key, value, unit, dims
  )
  SELECT
    v_org_id,
    now(),
    p_geo_scope,
    'vat.payable',
    SUM(payable),
    'PHP',
    jsonb_build_object('period', v_period)
  FROM tax.filings
  WHERE org_id = v_org_id
    AND period = v_period
    AND form_code IN ('2550Q', '2550M');

  v_points_inserted := v_points_inserted + 1;

  RETURN jsonb_build_object('ok', true, 'points', v_points_inserted);
END;
$$ LANGUAGE plpgsql;
```

---

## 4. Execution

### 4.1 Create Directory Structure

```bash
mkdir -p scripts/month_close
mkdir -p ipai-ops-console/src/app/close/{overview,tasks,compliance,audit}
```

### 4.2 Create Agent Scripts

```bash
# Create CLI entrypoint
cat > scripts/month_close/run.sh <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

: "${SUPABASE_URL:?}"
: "${SUPABASE_SERVICE_ROLE_KEY:?}"
: "${ODOO_URL:?}"
: "${ODOO_DB:?}"
: "${ODOO_API_KEY:?}"

PERIOD="${1:-$(date -u -d "$(date +%Y-%m-01) -1 day" +%Y-%m)}"
SCOPE="${2:-local}"

node scripts/month_close/run.mjs "$PERIOD" "$SCOPE"
BASH

chmod +x scripts/month_close/run.sh

# Create Node runner (content shown in section 2.3B above)
# ... (see run.mjs content above)
```

### 4.3 Run Agent

```bash
# Set environment
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="***"
export ODOO_URL="https://erp.insightpulseai.com"
export ODOO_DB="odoo"
export ODOO_API_KEY="***"

# Run for previous month (local scope)
./scripts/month_close/run.sh

# Run for specific period and scope
./scripts/month_close/run.sh "2026-01" "regional"
```

---

## 5. Test / Verify

### 5.1 Verify BIR Forms Catalog

```bash
psql "$SUPABASE_DATABASE_URL" -c "
SELECT form_code, form_name, frequency
FROM tax.forms
WHERE active = true
ORDER BY form_code;
"
```

### 5.2 Verify KPI Points

```bash
psql "$SUPABASE_DATABASE_URL" -c "
SELECT metric_key, geo_scope, value, unit, dims
FROM analytics.kpi_points
WHERE metric_key LIKE 'bir.%' OR metric_key LIKE 'vat.%'
ORDER BY ts DESC
LIMIT 20;
"
```

### 5.3 Verify Audit Trail

```bash
psql "$SUPABASE_DATABASE_URL" -c "
SELECT action, target, metadata, created_at
FROM audit.events
WHERE action LIKE 'month_close.%'
ORDER BY created_at DESC
LIMIT 20;
"
```

---

## 6. Deploy / Rollback

### Deploy

```bash
git add scripts/month_close supabase/migrations docs/operations
git commit -m "feat(close): month-end close dashboard + agent + BIR compliance"
git push origin main
```

### Rollback

```bash
git revert --no-edit HEAD
git push origin main
```

---

## 7. Notes / Risks

1. **BIR Form Codes**: Treat as controlled vocabulary from official BIR list. Deadlines are data (from Tax Filing sheet + reference calendars).

2. **Compliance vs Ops**: Keep `tax.*` separate from `ops.*` to avoid mixing finance and infrastructure semantics.

3. **SLSP**: Model as its own compliance object tied to VAT quarters (operationally distinct from 2550Q).

4. **KPI Rollups**: Write 3 points per metric (local/regional/global) for instant dashboard scope switching.

5. **UI Computation**: UI reads RPC outputs only - never computes metrics client-side.

---

## 8. Next Steps

### UI Implementation
Reply with: **CONTINUE DETAILS ON CLOSE UI TSX FILE TREE + COMPONENT SKELETONS**

This will provide:
- Exact TSX component tree for `/app/close/*`
- Tailwind/shadcn card components
- Compliance board layout
- Timeline components

---

## Files

- `docs/operations/MONTH_END_CLOSE_IMPLEMENTATION.md` - This file
- `docs/operations/MONTH_END_CLOSE_MAPPING.md` - SSOT boundaries
- `scripts/month_close/run.sh` - Agent CLI
- `scripts/month_close/run.mjs` - Agent Node runner
- `supabase/migrations/2026XXXX_tax_compliance_schema.sql` - Tax schema
- `supabase/migrations/2026XXXX_month_close_rpcs.sql` - RPC functions

## References

- [Bureau of Internal Revenue - Forms](https://www.bir.gov.ph/bir-forms)
- [Grant Thornton - VAT Guidance](https://www.grantthornton.com.ph/alerts-and-publications/technical-alerts/tax-alert/2023/optional-filing-and-payment-of-monthly-vat-returns-now-allowed/)
- [BIR Tax Deadlines](https://www.facebook.com/birgovph/posts/bir-tax-deadlinejanuary-25-2026-sundaysubmission-quarterly-summary-list-of-sales/1239896274909528/)
