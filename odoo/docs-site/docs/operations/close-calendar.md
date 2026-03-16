# Close calendar and phases

The financial close cycle follows a 5-phase structure with defined gates and performance targets. This page covers the close calendar, current state gaps, and approval workflow.

---

## Performance targets

| Metric | Target |
|--------|--------|
| Monthly close | ≤ 5 business days |
| Quarterly close | ≤ 7 business days |
| Annual close | ≤ 15 business days |
| Task completion rate | ≥ 95% |
| Reconciliation accuracy | ≥ 90% |

## Current state gaps

The platform targets reducing close cycle time from 15 to 5 business days and BIR compliance effort from 480–560 hours/year to under 100 hours/year.

| Area | Readiness score | Key gap |
|------|:-:|---|
| Task management | 86% | Manual tracking, no automated dependency resolution |
| Multi-subsidiary | 95% | Minor intercompany elimination gaps |
| Reconciliation | 88% | Bank reconciliation partially manual |
| Financial reporting | 60% | Custom reports not yet migrated to Odoo BI |
| Compliance (BIR) | 85% | Some forms still require eBIRForms desktop app |

---

## 5-phase close cycle

### Phase 1 — Pre-close (days -5 to -1)

Prepare the close before the period ends.

| Activity | Description |
|----------|-------------|
| Outstanding items review | Clear pending POs, invoices, and receipts |
| Cut-off communication | Notify departments of submission deadlines |
| Bank statement collection | Retrieve all bank statements for the period |
| System readiness check | Verify Odoo period status, access controls |
| Preliminary trial balance | Generate and review for obvious anomalies |

### Phase 2 — Close execution (days 1–3)

Execute core close activities.

| Activity | Description |
|----------|-------------|
| Transaction cut-off | Lock AP/AR entries for prior period |
| Bank reconciliation | Auto-match via `account_reconcile_oca`, resolve exceptions |
| GL reconciliation | Reconcile balance sheet accounts (AR, AP, inventory, fixed assets) |
| Adjusting journal entries | Post accruals, deferrals, depreciation, FX adjustments |
| WHT reconciliation | Match withholding tax entries to BIR 1601-C requirements |

### Phase 3 — Review and reconciliation (days 4–5)

Validate accuracy and completeness.

| Activity | Description |
|----------|-------------|
| Trial balance validation | Compare to prior period, investigate variances > 5% |
| Financial statement draft | Generate P&L, balance sheet, cash flow |
| Variance analysis | Document explanations for material variances |
| Intercompany reconciliation | Eliminate intercompany balances |
| BIR form preparation | Prepare 1601-C, 0619-E, or quarterly forms as applicable |

### Phase 4 — Approval and lock (days 6–7)

Secure approvals and lock the period.

| Activity | Description |
|----------|-------------|
| Management review | CFO/Controller reviews financial package |
| Approval signatures | Obtain required sign-offs per approval matrix |
| Period lock | Lock period in Odoo (`account.period` lock date) |
| Archive and backup | Archive working papers, back up database |

### Phase 5 — Reporting and audit (day 8+)

Distribute results and support external processes.

| Activity | Description |
|----------|-------------|
| Stakeholder distribution | Send financial package to management |
| BIR filing submission | File applicable forms via eBIRForms or eFPS |
| Audit support | Provide working papers and schedules to auditors |
| Lessons learned | Document process improvements for next cycle |

---

## Approval gates

Four gates must pass before the period locks.

| Gate | Approver | Criteria |
|------|----------|----------|
| **1. Reconciliation** | Senior Accountant | All BS accounts reconciled, exceptions documented |
| **2. Journal entries** | Accounting Manager | All adjusting entries reviewed, supporting docs attached |
| **3. Financial statements** | Controller / CFO | Trial balance ties, variance explanations complete |
| **4. BIR compliance** | Tax Manager | All applicable forms prepared, calculations verified |

!!! warning "Gate failure"
    If any gate fails, the close timeline extends. Document the blocker in the close tracker and escalate within 4 hours.

---

## Critical path and bottleneck management

The critical path runs through bank reconciliation → GL reconciliation → adjusting entries → trial balance → approval.

**Common bottlenecks:**

| Bottleneck | Mitigation |
|------------|------------|
| Late bank statements | Set up automated feeds via `account_bank_statement_import_ofx` |
| Missing vendor invoices | Enforce AP cut-off 2 days before period end |
| Intercompany mismatches | Reconcile weekly, not just at close |
| BIR form errors | Validate tax computations against GL before form generation |
| Approval delays | Pre-schedule review meetings in close calendar |

!!! tip "Automation opportunities"
    Use Odoo scheduled actions (`ir.cron`) to auto-generate recurring accruals and depreciation entries on Day 1 of the close. This removes 2–3 tasks from the critical path.
