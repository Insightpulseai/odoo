# PH/BIR Unified Finance — Cross-Domain QA Test Plan
**Scope**: AR + AP + Expenses + VAT + Withholding + BIR Outputs (Odoo 18 CE)
**Focus**: Cross-domain interactions only — individual domain plans are in separate files.
**Version**: 1.0 | **Date**: 2026-04-09 | **Status**: Active

---

## 1. Purpose and Scope

This plan tests flows that span two or more of: Accounts Receivable, Accounts Payable, and Employee Expenses. It does not re-test single-domain behavior already covered in:
- `PH_BIR_VENDOR_BILLS_AP_TEST_PLAN.md` — AP / EWT / 2307 per vendor bill
- `PH_BIR_EXPENSE_REIMBURSEMENT_TEST_PLAN.md` — Expense reimbursements
- `ODOO18_FULL_FINANCE_TEST_PLAN.md` — Full finance baseline

**In scope**: BIR forms 2307, SAWT, 1601-C, 1601-EQ, 2550Q, 2550M; period-close sequences; multi-currency consolidation; government counterparty scenarios; cross-domain data integrity.

---

## 2. Shared Test Data Design

All scenarios in this plan use the following canonical fixtures. Load once per test DB.

| ID | Entity | Type | VAT Reg | EWT ATC | Currency | Notes |
|----|--------|------|---------|---------|----------|-------|
| TD-01 | IPAI Corp | Self (company) | Y | — | PHP | Operating entity |
| TD-02 | PhilHealth | Gov vendor/customer | N | WI158 | PHP | Dual role: AP + AR |
| TD-03 | SSS | Gov vendor | N | WI158 | PHP | AP only |
| TD-04 | Acme Supplies Inc. | Private vendor | Y | WC158 | PHP | Appears in AP + Expenses |
| TD-05 | Global Services Ltd. | Foreign vendor | N | — | USD | Multi-currency AP |
| TD-06 | Metro Corp | Private customer | Y | — | PHP | Issues 2307 to IPAI |
| TD-07 | Rizal Province LGU | Gov customer | N | — | PHP | AR: government |
| TD-08 | Ana Santos | Employee | — | — | PHP | Expense claimant |
| TD-09 | Jose Reyes | Employee | — | — | PHP | Expense claimant, USD travel |
| TD-10 | Acme Supplies Inc. | Same as TD-04 | Y | WC158 | PHP | Cross-domain integrity check |

**Tax rates used**:
- VAT Output: 12% on taxable sales
- VAT Input: 12% on taxable purchases
- EWT WC158: 2% on professional services
- EWT WI158: 5% on government vendors
- EWT WI010: 1% on goods purchases

---

## 3. Scenario Matrix

Format: `UF-[Domain]-[Seq]` | P1=Critical, P2=High, P3=Medium | Auto=Y/N

### 3A. End-to-End Cross-Domain Flows

| ID | Scenario | Priority | Auto | Forms Tested |
|----|----------|----------|------|--------------|
| UF-A-001 | Vendor bill → EWT posted → 2307 generated → included in SAWT → feeds 2550Q VAT input | P1 | Y | 2307, SAWT, 2550Q |
| UF-A-002 | Customer invoice (VAT) → customer issues 2307 → received certificate matched → net AR recognized | P1 | Y | 2307 (inbound), AR aging |
| UF-A-003 | Expense claim (Acme Supplies) → AP reimbursement bill created → EWT WC158 applied → SAWT row added | P1 | Y | 2307, SAWT |
| UF-A-004 | Government vendor (PhilHealth) in AP + same entity as AR customer → separate EWT pools, no netting | P1 | N | 2307, AR/AP ledger |
| UF-A-005 | Full quarter: VAT output (AR) − VAT input (AP + Expenses) = 2550Q net VAT payable | P1 | Y | 2550Q |
| UF-A-006 | Monthly 2550M (month 1 + 2) → Q close: 2550Q reconciles to sum of 2550M + adjustments | P2 | Y | 2550M, 2550Q |
| UF-A-007 | Employee USD travel expense → AP reimbursement in USD → PHP conversion → VAT input at spot rate | P2 | Y | 2550Q, multi-currency |
| UF-A-008 | Period close sequence: lock AR → lock AP → generate 2307s → generate SAWT → generate 2550Q | P1 | N | All forms, lock dates |
| UF-A-009 | Salary-related AP (1601-C) separate from vendor EWT (1601-EQ) — no cross-contamination in filing | P1 | Y | 1601-C, 1601-EQ |
| UF-A-010 | AR credit note (VAT) + AP debit note (VAT) in same period → both hit 2550Q correctly | P2 | Y | 2550Q |

### 3B. VAT Input/Output Netting

| ID | Scenario | Priority | Auto | Forms Tested |
|----|----------|----------|------|--------------|
| UF-B-001 | Pure service quarter: output VAT from AR only, input VAT from AP only → 2550Q net | P1 | Y | 2550Q |
| UF-B-002 | Expense VAT input included in 2550Q alongside AP VAT input | P1 | Y | 2550Q |
| UF-B-003 | VAT-exempt sale (gov customer TD-07) → no output VAT → input VAT still claimable | P2 | Y | 2550Q |
| UF-B-004 | Excess input VAT carried forward to next quarter | P2 | Y | 2550Q (Q1→Q2) |
| UF-B-005 | Mixed VAT / VAT-exempt / zero-rated lines in single invoice → apportionment in 2550Q | P2 | N | 2550Q |

### 3C. Withholding Tax Reconciliation

| ID | Scenario | Priority | Auto | Forms Tested |
|----|----------|----------|------|--------------|
| UF-C-001 | EWT withheld on AP (WC158) matches 2307 issued to vendor; SAWT total = sum of 2307s | P1 | Y | 2307, SAWT |
| UF-C-002 | Customer withholds EWT from IPAI (inbound 2307 received) → credited against IPAI income tax liability | P1 | N | 2307 (inbound) |
| UF-C-003 | Same vendor in AP + Expenses → combined EWT certificate (single 2307 per period per vendor) | P1 | Y | 2307 |
| UF-C-004 | EWT on partial payment: bill PHP 100k, paid PHP 60k → EWT computed on PHP 60k payment | P2 | Y | 2307, 1601-EQ |
| UF-C-005 | Reversal of vendor bill after 2307 issued → 2307 voided; SAWT recalculated | P1 | N | 2307, SAWT |
| UF-C-006 | Government vendor (WI158 5%) in AP → separate 1601-EQ bucket from private vendor (WC158 2%) | P1 | Y | 1601-EQ |

### 3D. Government Counterparty Spanning AR and AP

| ID | Scenario | Priority | Auto | Forms Tested |
|----|----------|----------|------|--------------|
| UF-D-001 | PhilHealth as AP vendor (premium remittance) + AR customer (capitation billing) → ledger separation | P1 | N | 2307, AR/AP |
| UF-D-002 | LGU (TD-07) AR invoice: VAT-exempt treatment → no 12% output VAT in 2550Q | P2 | Y | 2550Q |
| UF-D-003 | Government agency AP: EWT WI158 on goods (not services) → correct ATC selection | P2 | Y | 2307, 1601-EQ |

### 3E. Period-Close Sequences

| ID | Scenario | Priority | Auto | Forms Tested |
|----|----------|----------|------|--------------|
| UF-E-001 | Lock date set: attempt to post AR entry in locked period → rejected; BIR forms unaffected | P1 | Y | Lock dates |
| UF-E-002 | Correct filing order: 1601-C (10th) → 1601-EQ (last day of month after Q) → 2550M (20th) → 2550Q (25th) | P1 | N | All four forms |
| UF-E-003 | Late AP bill (prior period) posted after lock date using exception workflow → SAWT amendment flagged | P2 | N | SAWT, lock dates |
| UF-E-004 | Quarter-end: AP accruals reversed in new period → VAT input reversal reflected in next 2550Q | P2 | Y | 2550Q |

### 3F. Multi-Currency Consolidated Reporting

| ID | Scenario | Priority | Auto | Forms Tested |
|----|----------|----------|------|--------------|
| UF-F-001 | USD AP bill (Global Services TD-05) → PHP equivalent for BIR forms at BSP rate on posting date | P1 | Y | 2307, SAWT |
| UF-F-002 | USD expense reimbursement (Jose Reyes TD-09) → PHP conversion for VAT input in 2550Q | P2 | Y | 2550Q |
| UF-F-003 | FX revaluation of AP → unrealized gain/loss does not alter EWT base or VAT input | P2 | Y | 2307, 2550Q |

---

## 4. BIR Compliance Matrix

Maps each BIR form to the cross-domain scenarios that validate it.

| Form | Purpose | Filing Deadline | Scenarios | Must-Pass IDs |
|------|---------|-----------------|-----------|---------------|
| **2307** | Certificate of Creditable EWT | Issued on payment | UF-A-001, UF-C-001, UF-C-003, UF-C-004, UF-C-005, UF-F-001 | UF-A-001, UF-C-001 |
| **SAWT** | Summary Alphalist of WHT | With 1601-EQ | UF-A-001, UF-A-003, UF-C-001, UF-C-005, UF-E-003 | UF-A-001, UF-C-001 |
| **1601-C** | Compensation withholding | 10th of following month | UF-A-009 | UF-A-009 |
| **1601-EQ** | EWT quarterly return | Last day of month after Q | UF-A-009, UF-C-004, UF-C-006, UF-D-003 | UF-C-006 |
| **2550M** | Monthly VAT declaration | 20th of following month | UF-A-006 | UF-A-006 |
| **2550Q** | Quarterly VAT return | 25th of month after Q | UF-A-001, UF-A-005, UF-A-006, UF-B-001–005, UF-F-001 | UF-A-005, UF-B-001 |

**Blocking criteria**: Any P1 scenario in the Must-Pass column that fails blocks release.

---

## 5. Regression Suite (10 Cases)

Run on every merge to `main` that touches `account_*`, `ipai_finance_*`, or `ipai_bir_*` modules.

| Reg-ID | Name | Covers | Pass Criteria |
|--------|------|--------|---------------|
| REG-01 | 2307 amount = EWT tax line on bill | UF-A-001 | `account.move` tax amount == 2307 `wtax_amount` |
| REG-02 | SAWT row count = distinct vendor-EWT combinations | UF-C-001 | SAWT line count matches DB query |
| REG-03 | 2550Q output VAT = sum of AR tax lines (period) | UF-A-005 | Within PHP 1.00 tolerance |
| REG-04 | 2550Q input VAT = AP tax lines + approved expense tax lines | UF-B-002 | Within PHP 1.00 tolerance |
| REG-05 | Expense AP bill carries same vendor record as direct AP bill | UF-C-003 | `res.partner.id` identical |
| REG-06 | 1601-C and 1601-EQ totals are mutually exclusive | UF-A-009 | No `move.line` appears in both reports |
| REG-07 | FX AP bill: 2307 amount in PHP, not source currency | UF-F-001 | `currency_id` on 2307 == PHP |
| REG-08 | Locked period rejects new AP posting | UF-E-001 | `UserError` raised; no journal entry created |
| REG-09 | Credit note reversal decrements 2550Q output VAT | UF-A-010 | 2550Q re-run shows lower output VAT |
| REG-10 | Government vendor EWT uses WI158 ATC, not WC158 | UF-C-006 | `l10n_ph_atc` = `WI158` on tax line |

**Automation**: All 10 run via `./scripts/odoo_test.sh test_bir_unified` on DB `test_bir_unified`.

---

## 6. Top-15 Cross-Domain Failure Scenarios (Ranked by BIR Penalty Risk)

| Rank | Failure | Root Cause | Detection | BIR Risk |
|------|---------|-----------|-----------|----------|
| 1 | 2307 issued but not in SAWT | Missing link between `account.move` and SAWT generator | REG-02 | Surcharge + compromise penalty |
| 2 | Expense EWT excluded from 1601-EQ | Expense AP bills not flagged as EWT-bearing | REG-06 | Under-remittance penalty |
| 3 | 2550Q VAT input understated (expense VAT missing) | Expense reimbursement bills use wrong journal | REG-04 | VAT assessment |
| 4 | Same vendor gets two 2307s (AP + Expense) instead of one | `res.partner` deduplication failure | REG-05 | Over-remittance; vendor confusion |
| 5 | FX bill EWT computed in USD, not PHP | `currency_id` misconfiguration on tax | REG-07 | Incorrect 2307 amount |
| 6 | Government customer AR invoice generates output VAT | Missing VAT-exempt fiscal position | UF-D-002 | Over-declared VAT |
| 7 | 2550M month 1+2 do not reconcile to 2550Q | Rounding or line exclusions differ between monthly/quarterly | UF-A-006 | BIR reconciliation query |
| 8 | Accrual reversal includes VAT; next 2550Q double-counts input | Reversal tax lines not excluded | UF-E-004 | VAT over-claim |
| 9 | PhilHealth AP and AR entries share same account | Account misconfiguration for dual-role party | UF-D-001 | Financial statement error |
| 10 | Lock date bypass via expense validation | Expense `account_date` not checked against lock | UF-E-001 | Audit integrity failure |
| 11 | 1601-C picks up vendor EWT from AP | Compensation vs. expanded WHT filter broken | UF-A-009 | Wrong BIR form filing |
| 12 | Partial payment EWT basis wrong (full bill amount used) | EWT trigger on bill post vs. payment | UF-C-004 | Over-withholding, vendor dispute |
| 13 | Voided 2307 not removed from SAWT | Soft-delete not propagating to alphalist | UF-C-005 | Inflated SAWT |
| 14 | Inbound customer 2307 not recorded as creditable tax | Manual-only workflow; no structured entry | UF-A-002 | Lost tax credit |
| 15 | Multi-currency VAT input at invoice rate, not BSP rate | `currency_rate` source misconfigured | UF-F-002 | BIR disputes rate basis |

---

## 7. Test Execution Order (Period-Close Sequence)

The following sequence must complete in order without failure before any BIR filing assertion:

```
1. Post all AR invoices for the period         → validates output VAT pool
2. Post all AP bills for the period            → validates input VAT + EWT pool
3. Validate and post expense reimbursements    → merges into AP; EWT + VAT input updated
4. Run 2307 generation                         → one per vendor per period
5. Run SAWT                                    → must match 2307 sum
6. Run 2550M (months 1 and 2 of quarter)       → intermediate VAT declarations
7. Set accounting lock date (end of period)    → no further postings in period
8. Run 2550Q                                   → must reconcile to 2550M sum ± adjustments
9. Run 1601-EQ                                 → must match EWT in SAWT
10. Run 1601-C                                 → compensation only; no overlap with 1601-EQ
```

**Failure at any step halts subsequent steps.** Steps 7–10 are gated on step 6 passing.

---

## 8. Automation Strategy

| Layer | Tool | Target |
|-------|------|--------|
| Unit (tax line assertions) | Odoo `TransactionCase` | REG-01 to REG-10 |
| Integration (form output) | `AccountTestMixin` + XML-RPC | UF-A-001, UF-A-005, UF-A-009, UF-B-001 |
| E2E UI (filing sequence) | Playwright (headless) | UF-E-002 (manual-assist), UF-A-008 |
| Manual (dual-role entity) | Test runbook + screenshot | UF-D-001, UF-C-002 |

All automated tests run on DB `test_bir_unified` (disposable). CI command:
```bash
./scripts/odoo_test.sh --db test_bir_unified --module ipai_bir_unified --tags cross_domain
```

---

## 9. Gaps and Assumptions

| # | Item | Type | Status |
|---|------|------|--------|
| G-01 | Inbound 2307 (customer-issued) has no native Odoo CE model — manual journal entry required | Gap | Needs `ipai_bir_inbound_cert` module or OCA equivalent |
| G-02 | SAWT generation is OCA `l10n_ph` extension — not baseline CE 18. Must verify OCA module is installed. | Assumption | Verify in `odoo_dev` before test run |
| G-03 | 2550M → 2550Q reconciliation is currently manual in CE; no automated carry-forward | Gap | Planned in `ipai_bir_vat_quarterly` |
| G-04 | BSP reference rate feed not automated — FX rate must be manually updated before period close | Gap | Azure Function rate sync planned Q2-2026 |
| G-05 | Government fiscal position (VAT-exempt) must be pre-configured per LGU/agency | Assumption | Test data setup must include fiscal position assignment |
| G-06 | 1601-C generation for payroll requires `hr_payroll` and `l10n_ph_payroll` OCA modules | Assumption | Out of scope for UF-A-009 if payroll not installed; test skipped |
| G-07 | EWT on partial payments depends on `account_tax_on_payment` OCA behavior | Assumption | Verify OCA version compatibility with Odoo 18 CE |

---

## 10. Entry / Exit Criteria

**Entry (before any scenario runs)**:
- `test_bir_unified` DB created and seeded with TD-01 through TD-10
- OCA `l10n_ph` installed and ATC codes loaded
- Chart of accounts includes separate accounts for EWT payable, VAT output, VAT input
- Fiscal positions configured for government entities (TD-02, TD-03, TD-07)

**Exit (plan considered complete)**:
- All P1 scenarios: PASS
- All 10 regression cases: PASS
- Zero open P1 blockers
- Evidence saved to `docs/evidence/<YYYYMMDD-HHMM>/bir_unified/`

---

*Cross-reference: `PH_BIR_VENDOR_BILLS_AP_TEST_PLAN.md`, `PH_BIR_EXPENSE_REIMBURSEMENT_TEST_PLAN.md`, `ODOO18_FULL_FINANCE_TEST_PLAN.md`*
