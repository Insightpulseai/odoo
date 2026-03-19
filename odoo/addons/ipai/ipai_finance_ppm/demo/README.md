# Finance PPM Demo Data

## What this creates

When installed with demo data enabled (`--without-demo=False`), this module seeds:

### Projects
- **Finance PPM - Month-End Close** — 4-phase month-end close with 69 tasks
- **Finance PPM - BIR Tax Filing** — 4-phase BIR tax filing with 26 tasks

### Task Stages
- Preparation → Review → Approval → Filed

### Task Structure
Tasks use a parent/child hierarchy where each phase is a parent task containing ordered subtasks.

## What this does NOT create
- No real user assignments — all tasks are unassigned
- No real budget amounts — set to 0.00
- No real deadlines — set per-tenant after install
- No real cost center codes — uses placeholder codes (FIN-CORE, TAX-CORE)

## For production use
Real tenant data should come from:
1. The **PPM Import Wizard** (Settings > Technical > PPM Import)
2. Manual project/task creation
3. CSV import using the template at `static/examples/ipai_finance_ppm_month_end_close_template.csv`

## Phase structure

### Month-End Close (D+1 to D+5)
| Phase | Day | Tasks | Focus |
|-------|-----|-------|-------|
| I. Initial & Compliance | D+1 | 15 | Pre-close validation, bank recon, compliance |
| II. Accruals & Adj. | D+2 | 18 | Accruals, depreciation, provisions, reclassifications |
| III. WIP & IC | D+3 | 18 | WIP review, IC elimination, analytical review, FS prep |
| IV. Final Close | D+4-5 | 18 | Approval, period lock, filing, reporting |

### BIR Tax Filing
| Phase | Tasks | Focus |
|-------|-------|-------|
| 1. Preparation | 7 | Data extraction, SLSP, TIN validation, 2307 prep |
| 2. Computation | 7 | VAT, EWT, FWT, DST computation and form prep |
| 3. Review | 5 | SFM/FD review and filing readiness |
| 4. Filing | 7 | eFPS filing, payment, archival, 2307 distribution |

## Philippine accounting context
Task descriptions reference:
- **PFRS** (Philippine Financial Reporting Standards)
- **PAS** (Philippine Accounting Standards)
- **BIR** forms and eFPS (electronic filing)
- **CREATE law** tax rates
- **SSS, PhilHealth, Pag-IBIG** statutory deductions
- **BSP** (Bangko Sentral ng Pilipinas) FX rates
