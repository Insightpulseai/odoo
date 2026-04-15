# PH Close + BIR Compliance — Boards-Ready Backlog Pack

> **Locked:** 2026-04-15
> **Pair with:** [`docs/ops/azure-boards-operating-guide.md`](../ops/azure-boards-operating-guide.md) (taxonomy + fields + cadence)
> **Evidence anchors:**
> - Memory `project_monthly_close_checklist.md` (Odoo 18 close checklist)
> - Memory `project_bir_eservices_matrix.md` (eBIRForms/eFPS/ePAY/eAFS)
> - Memory `project_tax_guru_copilot.md` (Tax Guru sub-agent, 7 packages)
> - Memory `project_taxpulse_ph_pack_positioning.md` (TaxPulse-PH-Pack)
> - `addons/ipai/ipai_bir_2307/`, `ipai_bir_2307_automation/`, `ipai_bir_tax_compliance/`, `ipai_bir_returns/`, `ipai_bir_slsp/`

---

## Initiative

**Regulatory-Grade Close & BIR Compliance Operations**

Covers two intertwined recurring programs:
1. **Monthly close** — Odoo 18 GL/AP/AR/Bank/Inventory/Payroll close cadence
2. **PH BIR compliance** — monthly/quarterly/annual filings + submission + evidence

Both are **recurring** work patterns — the Boards model must support instantiation per period (month, quarter, year), not one-time creation.

---

## Cadence model (how recurring work maps to Boards)

Boards doesn't do cron natively, so IPAI uses:

```
Master templates:     "Work Item Templates" in ADO (saved queries + template bodies)
Instance generator:   Azure Function (or ADO Extension) runs on 1st of each period
                      Creates Feature + child Stories from template,
                      links to the period's Iteration
Iteration scope:      One sprint per month = close+compliance fits 2-week sprint cadence
                      (monthly = 2 sprints; quarterly = 6 sprints; annual = rolling)
Tags:                 cadence:monthly | quarterly | annual
                      compliance_scope:bir-ph | bsp-ph | psa-ph
                      filing_form:1601-c | 2550-m | 1702-q | 1604-cf | etc.
Evidence link:        Each story links to docs/evidence/<YYYYMM>/<form>/
```

The **template definitions live in repo** (this file + `ssot/close/` + `ssot/bir-compliance/`). The **instantiation** creates actual Work Items in ADO per period.

---

## Epic 1 — Monthly Close Cadence (12 instances/year) `[P0]`

Recurs every month. Target close by **Day 5** of the following month (GL lock), Day 10 (financial reports), Day 15 (management pack).

### Feature 1.1 — Pre-close data quality

- **ISSUE-MC-001** Verify all AP bills posted for period
- **ISSUE-MC-002** Verify all AR invoices issued for period
- **ISSUE-MC-003** Verify expense liquidation submissions closed
- **ISSUE-MC-004** Verify payroll cutoff processed
- **ISSUE-MC-005** Verify inventory movements posted
- **ISSUE-MC-006** Run `ipai_finance_ap_ar` data quality checks

### Feature 1.2 — AP/AR close

- **ISSUE-MC-007** Reconcile AR aging report
- **ISSUE-MC-008** Reconcile AP aging report
- **ISSUE-MC-009** Post AR accruals (services rendered not yet billed)
- **ISSUE-MC-010** Post AP accruals (goods received not yet invoiced)
- **ISSUE-MC-011** Bad debt provision review

### Feature 1.3 — Bank reconciliation

- **ISSUE-MC-012** Reconcile all bank accounts
- **ISSUE-MC-013** Investigate unreconciled items > 7 days
- **ISSUE-MC-014** Reconcile Xendit / PayPal / PayMongo payment provider statements
- **ISSUE-MC-015** Lock bank statement period (Odoo)

### Feature 1.4 — Payroll close

- **ISSUE-MC-016** Post payroll journal for period
- **ISSUE-MC-017** Post 13th-month accrual (monthly 1/12 method)
- **ISSUE-MC-018** Post SSS / PhilHealth / HDMF employer share
- **ISSUE-MC-019** Post leave accruals

### Feature 1.5 — GL close

- **ISSUE-MC-020** FX revaluation (foreign-currency partner balances)
- **ISSUE-MC-021** Post depreciation for period (OCA `account_asset_management`)
- **ISSUE-MC-022** Post prepayment amortization
- **ISSUE-MC-023** Post accrual reversals for prior period
- **ISSUE-MC-024** Post inter-company eliminations
- **ISSUE-MC-025** Lock GL for period (set fiscal period to "closed")

### Feature 1.6 — Reporting

- **ISSUE-MC-026** Generate Trial Balance
- **ISSUE-MC-027** Generate Balance Sheet
- **ISSUE-MC-028** Generate P&L / Income Statement
- **ISSUE-MC-029** Generate Cash Flow Statement
- **ISSUE-MC-030** Generate management pack / variance analysis
- **ISSUE-MC-031** Post monthly flash memo to leadership

---

## Epic 2 — BIR Monthly Tax Compliance (12 instances/year) `[P0]`

Per `project_bir_eservices_matrix.md`. Filings due monthly.

### Feature 2.1 — Form 1601-C (Withholding on Compensation)

- **ISSUE-BM-001** Generate 1601-C from payroll data
- **ISSUE-BM-002** Validate compensation totals vs payroll GL
- **ISSUE-BM-003** Upload 1601-C to eBIRForms
- **ISSUE-BM-004** Pay via ePAY (BIR payment)
- **ISSUE-BM-005** File evidence pack (acknowledgment number + paid receipt)
- **Due:** Day 10 of following month

### Feature 2.2 — Form 0619-E (Expanded Withholding, monthly remittance)

- **ISSUE-BM-006** Generate 0619-E from `account.move.line` with EWT tax lines
- **ISSUE-BM-007** Validate totals per ATC code (1% services / 2% goods / 5% rentals / etc.)
- **ISSUE-BM-008** Upload to eFPS (if enrolled) or eBIRForms
- **ISSUE-BM-009** Pay via ePAY
- **ISSUE-BM-010** Evidence pack
- **Due:** Day 10 of following month

### Feature 2.3 — Form 2550-M (Monthly VAT)

- **ISSUE-BM-011** Generate 2550-M from VAT-subject sales and purchases
- **ISSUE-BM-012** Validate Output VAT vs Input VAT reconciliation
- **ISSUE-BM-013** Upload to eFPS / eBIRForms
- **ISSUE-BM-014** Pay via ePAY
- **ISSUE-BM-015** Evidence pack
- **Due:** Day 20 of following month

### Feature 2.4 — BIR Form 2307 Certificate Issuance

Per existing `addons/ipai/ipai_bir_2307/` module (memory #4495).

- **ISSUE-BM-016** Run BIR 2307 generator for all period EWT transactions
- **ISSUE-BM-017** Review generated 2307 PDFs
- **ISSUE-BM-018** Dispatch 2307 to vendors (email via Zoho SMTP)
- **ISSUE-BM-019** Track 2307 delivery acknowledgments
- **ISSUE-BM-020** Store 2307 dispatch log for audit trail
- **Due:** Day 20 of following month

### Feature 2.5 — Monthly submission & reconciliation

- **ISSUE-BM-021** Reconcile BIR-filed totals vs GL closing balances
- **ISSUE-BM-022** Flag any variance > tolerance threshold
- **ISSUE-BM-023** File amendment if required
- **ISSUE-BM-024** Update BIR compliance register (per `ipai_bir_tax_compliance`)

---

## Epic 3 — BIR Quarterly Tax Compliance (4 instances/year) `[P0]`

### Feature 3.1 — Form 2550-Q (Quarterly VAT)

- **ISSUE-BQ-001** Aggregate monthly 2550-M into quarterly
- **ISSUE-BQ-002** Generate 2550-Q
- **ISSUE-BQ-003** Upload to eFPS / eBIRForms
- **ISSUE-BQ-004** Pay any true-up
- **ISSUE-BQ-005** Evidence pack
- **Due:** Day 25 of month following quarter end

### Feature 3.2 — Form 1601-FQ (Final Withholding, Quarterly)

- **ISSUE-BQ-006** Generate 1601-FQ from FWT transactions (dividends, royalties, etc.)
- **ISSUE-BQ-007** Validate ATC code totals
- **ISSUE-BQ-008** Upload to eFPS / eBIRForms
- **ISSUE-BQ-009** Pay
- **ISSUE-BQ-010** Evidence pack
- **Due:** Last day of month following quarter end

### Feature 3.3 — Form 1702-Q (Quarterly Income Tax, corporations)

- **ISSUE-BQ-011** Generate 1702-Q from GL income data
- **ISSUE-BQ-012** Apply quarterly CIT rate (currently 25% or 20% MSME)
- **ISSUE-BQ-013** Validate tax-exempt / deductible items
- **ISSUE-BQ-014** Upload to eFPS
- **ISSUE-BQ-015** Pay
- **ISSUE-BQ-016** Evidence pack
- **Due:** 60 days after quarter end

### Feature 3.4 — SLSP (Summary List of Sales/Purchases)

Per `addons/ipai/ipai_bir_slsp/`.

- **ISSUE-BQ-017** Generate SLSP via `ipai_bir_slsp`
- **ISSUE-BQ-018** Validate against 2550-Q totals
- **ISSUE-BQ-019** Submit to eFPS
- **ISSUE-BQ-020** Evidence pack
- **Due:** Day 25 of month following quarter end

---

## Epic 4 — BIR Annual Tax Compliance (1 instance/year) `[P0]`

### Feature 4.1 — Form 1702 / 1702-RT / 1702-EX (Annual Corporate Income Tax)

- **ISSUE-BA-001** Close fiscal year in Odoo
- **ISSUE-BA-002** Generate audited P&L / BS / Cash Flow
- **ISSUE-BA-003** Apply annual adjustments (NOLCO, tax holidays, MCIT)
- **ISSUE-BA-004** Generate 1702 via `ipai_bir_returns`
- **ISSUE-BA-005** Attach supporting schedules
- **ISSUE-BA-006** External CPA certification
- **ISSUE-BA-007** Upload to eFPS
- **ISSUE-BA-008** Pay annual true-up
- **ISSUE-BA-009** Evidence pack
- **Due:** April 15 of following year

### Feature 4.2 — Form 2316 (Certificate of Compensation)

- **ISSUE-BA-010** Generate per-employee 2316 from payroll
- **ISSUE-BA-011** Distribute 2316 to employees
- **ISSUE-BA-012** Archive signed acknowledgments
- **Due:** January 31

### Feature 4.3 — Form 1604-CF (Annual Alphalist, Employees)

- **ISSUE-BA-013** Generate alphalist DAT file
- **ISSUE-BA-014** Upload to eFPS with 1604-CF
- **ISSUE-BA-015** Evidence pack
- **Due:** January 31

### Feature 4.4 — Form 1604-EC (Annual Alphalist, Non-Employees)

- **ISSUE-BA-016** Generate 1604-EC from EWT data
- **ISSUE-BA-017** Upload alphalist DAT
- **ISSUE-BA-018** Evidence pack
- **Due:** March 1

### Feature 4.5 — eAFS (Electronic Audited Financial Statements)

- **ISSUE-BA-019** Prepare AFS bundle (BS, P&L, CF, notes)
- **ISSUE-BA-020** CPA sign-off
- **ISSUE-BA-021** Upload via eAFS portal
- **ISSUE-BA-022** Evidence pack
- **Due:** April 15 (with 1702)

### Feature 4.6 — BIR Registration Renewal

- **ISSUE-BA-023** Pay annual Registration Fee (BIR Form 0605, ₱500)
- **ISSUE-BA-024** Book of Accounts registration/stamping
- **ISSUE-BA-025** Evidence pack
- **Due:** January 31

---

## Epic 5 — Recurring Calendar Automation `[P1]`

### Feature 5.1 — Template definitions

- **ISSUE-AUT-001** Save Work Item Templates per Feature (Epic 1–4)
- **ISSUE-AUT-002** Define template variables (period, fiscal year, due date)
- **ISSUE-AUT-003** Document template catalog in `ssot/close/templates.yaml`
- **ISSUE-AUT-004** Document BIR filing calendar in `ssot/bir-compliance/calendar.yaml`

### Feature 5.2 — Azure Boards automation

- **ISSUE-AUT-005** Build Azure Function: `close-period-instantiator` (runs 1st of each month)
  - Reads `ssot/close/templates.yaml`
  - Creates Feature + child Stories for the new period
  - Assigns Iteration Path to month's sprint
  - Sets Due Date per template
- **ISSUE-AUT-006** Build Azure Function: `bir-period-instantiator` (runs 1st of month, quarter, year)
- **ISSUE-AUT-007** Build Azure Function: `overdue-escalation-notifier` (runs daily, pages on overdue BIR filings)

### Feature 5.3 — Pulser Tax Guru integration

Per memory `project_tax_guru_copilot.md` (Tax Guru sub-agent, 7 packages).

- **ISSUE-AUT-008** Wire Tax Guru agent to pre-populate BIR form values from GL data
- **ISSUE-AUT-009** Wire Tax Guru to produce per-filing advisory notes
- **ISSUE-AUT-010** Wire Tax Guru to flag unusual variances

---

## Epic 6 — Evidence Capture & Audit Trail `[P0]`

### Feature 6.1 — Per-filing evidence pack

- **ISSUE-EVI-001** Define evidence folder structure: `docs/evidence/<YYYYMM>/<form>/`
- **ISSUE-EVI-002** Each Story's Closed state requires: filed PDF + acknowledgment number + payment receipt + GL reconciliation
- **ISSUE-EVI-003** Auto-link evidence folder to Story via Attachments tab

### Feature 6.2 — BIR compliance register

- **ISSUE-EVI-004** Use `addons/ipai/ipai_bir_tax_compliance` register as canonical ledger
- **ISSUE-EVI-005** Every filing event recorded with: form, period, amount, status, acknowledgment
- **ISSUE-EVI-006** Boards Story links to register record via `Related` link type

### Feature 6.3 — Audit trail queries

- **ISSUE-EVI-007** Shared Query: "Pending BIR filings this month" (tag `compliance_scope:bir-ph` + State ≠ Closed + Due ≤ today+10)
- **ISSUE-EVI-008** Shared Query: "Overdue BIR filings" (tag + State ≠ Closed + Due < today)
- **ISSUE-EVI-009** Shared Query: "Month-end close status" (tag `cadence:monthly` + scope `close` + current Iteration)
- **ISSUE-EVI-010** Pin all 3 queries to "Plane Health — transaction" dashboard

---

## Sprint cut per period

### Monthly sprint (2-week sprint during close month)

```
Sprint N (weeks 1–2 of new month):
  MC-001 to MC-031           (close)
  BM-001 to BM-020           (monthly BIR due days 10–20)
```

### Quarterly overlay (in first month after quarter end)

```
+ BQ-001 to BQ-020           (quarterly BIR)
+ MC extras for period-end consolidation
```

### Annual overlay (January + April)

```
January:  BA-010 to BA-018, BA-023 to BA-025   (2316, 1604-CF, 1604-EC, registration renewal)
February: BA-010 cleanup                        (employee 2316 follow-up)
March:    BA-016 to BA-018 finalize             (1604-EC)
April:    BA-001 to BA-009, BA-019 to BA-022    (annual 1702 + eAFS)
```

---

## Tag contract (per Boards Operating Guide)

Every Story in this backlog carries:

| Tag key | Values |
|---|---|
| `environment` | `prod` (this is live compliance work) |
| `plane` | `transaction` (finance) |
| `cadence` | `monthly` / `quarterly` / `annual` |
| `compliance_scope` | `bir-ph` (mostly) or `bsp-ph` / `psa-ph` / `close` |
| `filing_form` | `1601-c` / `2550-m` / `2550-q` / `1702-q` / `1702` / `1604-cf` / `1604-ec` / `2307` / `0619-e` / `slsp` / `eafs` |
| `fiscal_period` | e.g. `2026-04` / `2026-Q2` / `FY2026` |

Pinned queries use these tags to filter.

---

## Pulser integration (per memory `project_tax_guru_copilot.md`)

Each filing Story can invoke Tax Guru sub-agent via:

```
Story → Tasks → "Run Tax Guru preflight"
     → Pulser tool call: pulser.tax_guru.preflight(form=<filing_form>, period=<fiscal_period>)
     → Returns: pre-filled form values + anomaly flags + BIR regulation citations
     → Attach output JSON to Story as Attachment
     → Engineer/Finance reviews, edits, submits
```

This keeps human-in-the-loop but speeds preparation. Per `feedback_d365_displacement_not_development.md` — IPAI displaces D365 Finance for PH customers.

---

## Azure Boards dashboard widgets (per reporting guide)

Add to "Plane Health — transaction" dashboard:

| Widget | Query |
|---|---|
| **Chart for work items** (count of pending BIR filings by form) | "Pending BIR filings this month" query, stacked bar, group by `filing_form` |
| **Chart for work items** (monthly close progress) | "Month-end close status" query, pie, group by State |
| **Query tile: Overdue BIR filings** | count + click-through |
| **Cycle time** | Average cycle time for close Stories, filtered by plane `transaction` |
| **Markdown widget** | BIR filing calendar (static, updated annually) |

---

## Anti-patterns

- Don't create 60+ Stories per period manually — use template instantiation (Feature 5.2)
- Don't close a filing Story without the evidence pack linked
- Don't skip the GL reconciliation acceptance criterion
- Don't file past due date without escalation + comment on Story
- Don't duplicate filings as GH Issues — these are business-critical, stay in ADO
- Don't relax `[P0]` Priority on BIR filings — non-compliance = penalties

---

## References

- `addons/ipai/ipai_bir_2307/` — 2307 generator
- `addons/ipai/ipai_bir_2307_automation/` — automation
- `addons/ipai/ipai_bir_tax_compliance/` — compliance register
- `addons/ipai/ipai_bir_returns/` — return forms
- `addons/ipai/ipai_bir_slsp/` — SLSP generator
- `addons/ipai/ipai_finance_ap_ar/` — AP/AR parity module
- `ssot/close/` (to be created) — close templates
- `ssot/bir-compliance/calendar.yaml` (to be created) — regulatory calendar
- Memory `project_monthly_close_checklist.md`
- Memory `project_bir_eservices_matrix.md`
- Memory `project_tax_guru_copilot.md`
- Memory `project_taxpulse_ph_pack_positioning.md`
- Memory `project_ph_grounding_hierarchy.md`
- [eBIRForms](https://ebirforms.bir.gov.ph)
- [eFPS](https://efps.bir.gov.ph)
- Companions: [`docs/ops/azure-boards-operating-guide.md`](../ops/azure-boards-operating-guide.md), [`docs/ops/azure-boards-reporting.md`](../ops/azure-boards-reporting.md)

---

*Last updated: 2026-04-15*
