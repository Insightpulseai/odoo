# Year-end task template

38 additional tasks on top of the standard [44 month-end tasks](month-end-tasks.md), targeting completion in 10 business days. These cover inventory verification, tax provisions, external audit coordination, and annual statutory filings.

---

## Summary

| Phase | Days | Tasks | Focus |
|-------|------|:-----:|-------|
| 1. Inventory and asset verification | 1–3 | 10 | Physical counts, asset tagging, impairment |
| 2. Tax provisions and regulatory compliance | 3–5 | 10 | Income tax, BIR annual forms, deferred tax |
| 3. External audit coordination | 5–7 | 9 | Audit schedules, confirmations, adjustments |
| 4. Annual reporting and statutory filings | 7–10 | 9 | AFS, SEC, AMLC, BIR annual returns |

!!! note "Relationship to month-end"
    Complete all 44 month-end tasks first (Days 1–5), then execute these 38 year-end tasks (Days 1–10 of the extended close). Some tasks run in parallel.

---

## Phase 1 — Inventory and asset verification (days 1–3)

| # | Task | Responsible | Dependency | Deadline |
|:-:|------|-------------|------------|----------|
| Y1 | Plan physical inventory count (locations, teams, schedule) | Cost Accountant | None | Day 1 |
| Y2 | Execute physical inventory count | Warehouse + Finance | Y1 | Day 2 |
| Y3 | Reconcile physical count to Odoo inventory valuation | Cost Accountant | Y2 | Day 2 |
| Y4 | Investigate and resolve count variances > 1% | Cost Accountant | Y3 | Day 3 |
| Y5 | Post inventory adjustment entries | Cost Accountant | Y4 | Day 3 |
| Y6 | Verify fixed asset register completeness | Fixed Assets Clerk | None | Day 1 |
| Y7 | Perform physical asset verification (spot check ≥20%) | Fixed Assets Clerk | Y6 | Day 2 |
| Y8 | Assess asset impairment indicators | Senior Accountant | Y7 | Day 3 |
| Y9 | Post impairment entries (if applicable) | Senior Accountant | Y8 | Day 3 |
| Y10 | Reconcile CIP (construction in progress) and capitalize completed assets | Fixed Assets Clerk | Y6 | Day 3 |

## Phase 2 — Tax provisions and regulatory compliance (days 3–5)

| # | Task | Responsible | Dependency | Deadline |
|:-:|------|-------------|------------|----------|
| Y11 | Calculate annual income tax provision (RCIT vs. MCIT) | Tax Accountant | Month-end complete | Day 3 |
| Y12 | Calculate deferred tax assets/liabilities | Tax Accountant | Y11 | Day 4 |
| Y13 | Post income tax provision entries | Tax Accountant | Y12 | Day 4 |
| Y14 | Prepare BIR Form 1702-RT (annual income tax return) | Tax Accountant | Y13 | Day 4 |
| Y15 | Reconcile annual WHT summary for BIR 1604-E | Tax Accountant | Month-end complete | Day 4 |
| Y16 | Prepare BIR Form 1604-E (annual info return — WHT on compensation) | Tax Accountant | Y15 | Day 5 |
| Y17 | Validate VAT compliance — annual reconciliation of 2550Q filings | Tax Accountant | Month-end complete | Day 5 |
| Y18 | Review transfer pricing documentation (if applicable) | Tax Manager | None | Day 5 |
| Y19 | Assess contingent liabilities and provisions | Senior Accountant | Month-end complete | Day 5 |
| Y20 | Post year-end tax and provision adjustments | Tax Accountant | Y13, Y19 | Day 5 |

## Phase 3 — External audit coordination (days 5–7)

| # | Task | Responsible | Dependency | Deadline |
|:-:|------|-------------|------------|----------|
| Y21 | Prepare audit schedules (lead schedules + supporting) | Senior Accountant | Phase 2 | Day 5 |
| Y22 | Prepare bank confirmation letters | Treasury | None | Day 5 |
| Y23 | Prepare AR/AP confirmation letters | AR/AP Clerks | Month-end complete | Day 5 |
| Y24 | Prepare management representation letter | Controller | None | Day 6 |
| Y25 | Provide auditor access to Odoo (read-only audit role) | IT / Admin | None | Day 5 |
| Y26 | Respond to auditor inquiries — first round | Senior Accountant | Y21 | Day 6 |
| Y27 | Post audit adjustments (if any) | Senior Accountant | Y26 | Day 7 |
| Y28 | Obtain auditor sign-off on adjusted trial balance | Controller | Y27 | Day 7 |
| Y29 | Archive audit working papers | Senior Accountant | Y28 | Day 7 |

## Phase 4 — Annual reporting and statutory filings (days 7–10)

| # | Task | Responsible | Dependency | Deadline |
|:-:|------|-------------|------------|----------|
| Y30 | Prepare audited financial statements (AFS) | Controller | Y28 | Day 8 |
| Y31 | Prepare notes to financial statements | Controller | Y30 | Day 8 |
| Y32 | Board review and approval of AFS | CFO | Y31 | Day 9 |
| Y33 | File BIR 1702-RT (annual income tax return) | Tax Accountant | Y14, Y32 | Day 9 |
| Y34 | File BIR 1604-E (annual WHT information return) | Tax Accountant | Y16 | Day 9 |
| Y35 | File SEC Annual Financial Statements (GIS + AFS) | Corporate Secretary | Y32 | Day 10 |
| Y36 | File AMLC covered transaction report (if applicable) | Compliance Officer | Y30 | Day 10 |
| Y37 | Lock annual period in Odoo | Accounting Manager | Y32 | Day 10 |
| Y38 | Open new fiscal year periods in Odoo | Accounting Manager | Y37 | Day 10 |

---

## BIR annual forms

### BIR Form 1702-RT — Annual income tax return

??? info "Key details"
    - **Who files**: Corporations subject to regular corporate income tax
    - **Deadline**: April 15 of the following year (or within 15 days of the statutory audit completion)
    - **Tax rate**: 25% RCIT or 2% MCIT on gross income, whichever is higher
    - **Attachments**: AFS, ITR schedules, related party transaction summary

    ```
    RCIT = Taxable income x 25%
    MCIT = Gross income x 2%
    Tax due = MAX(RCIT, MCIT) - creditable WHT - quarterly payments
    ```

### BIR Form 1604-E — Annual information return on WHT (compensation)

??? info "Key details"
    - **Who files**: All employers
    - **Deadline**: January 31 of the following year
    - **Content**: Summary of all compensation paid and taxes withheld per employee
    - **Cross-reference**: Must reconcile to monthly 1601-C filings

---

## SEC and AMLC requirements

| Filing | Deadline | Requirement |
|--------|----------|-------------|
| SEC Annual Financial Statements | April 15 (or 120 days after fiscal year-end) | Audited FS + notes + auditor's report |
| SEC General Information Sheet (GIS) | January 30 | Corporate information update |
| AMLC Covered Transaction Report | Within 5 business days of transaction | Transactions ≥ PHP 500,000 |
| AMLC Suspicious Transaction Report | Within 5 business days of determination | Suspicious activity regardless of amount |

!!! warning "Late filing penalties"
    SEC late filing surcharge: PHP 200/day (GIS) or PHP 4,800/year (AFS). BIR penalties apply separately — see the [BIR filing runbook](bir-filing-runbook.md#penalty-calculations).
