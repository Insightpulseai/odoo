# BIR filing runbook

Execution guide for Bureau of Internal Revenue (BIR) tax filings in the Philippines. Covers the 6 primary forms, filing process, penalty calculations, and audit defense.

---

## Primary BIR forms

| Form | Name | Frequency | Deadline |
|------|------|-----------|----------|
| **1601-C** | Monthly remittance return of income taxes withheld on compensation | Monthly | 10th of the following month |
| **0619-E** | Monthly remittance form for creditable income taxes withheld (expanded) | Monthly | 10th of the following month |
| **2550Q** | Quarterly VAT return | Quarterly | 25th of the month following the quarter |
| **1601-EQ** | Quarterly remittance return of creditable income taxes withheld (expanded) | Quarterly | Last day of the month following the quarter |
| **1601-FQ** | Quarterly remittance return of final income taxes withheld | Quarterly | Last day of the month following the quarter |
| **1702-RT** | Annual income tax return (regular rate) | Annual | April 15 |
| **1604-E** | Annual information return of income taxes withheld on compensation | Annual | January 31 |

---

## Multi-agency compliance

| Agency | Filing requirement |
|--------|--------------------|
| BIR | Tax returns, withholding remittances, information returns |
| SEC | Annual financial statements (AFS), general information sheet (GIS) |
| SSS | Monthly employer contributions (R-5) |
| PhilHealth | Monthly employer remittance (RF-1) |
| Pag-IBIG | Monthly employer remittance |
| DOLE | Annual company report |
| LGU | Business permit renewal, local business tax |
| AMLC | Covered and suspicious transaction reports |

---

## Progressive tax table (compensation income)

Effective January 1, 2023 onward (TRAIN law, as amended):

| Taxable income bracket (PHP) | Tax rate |
|------------------------------|----------|
| ≤ 250,000 | 0% |
| 250,001 – 400,000 | 15% of excess over 250,000 |
| 400,001 – 800,000 | 22,500 + 20% of excess over 400,000 |
| 800,001 – 2,000,000 | 102,500 + 25% of excess over 800,000 |
| 2,000,001 – 8,000,000 | 402,500 + 30% of excess over 2,000,000 |
| > 8,000,000 | 2,202,500 + 35% of excess over 8,000,000 |

!!! note "Minimum wage earners"
    Statutory minimum wage earners are exempt from income tax on their compensation income, including holiday pay, overtime pay, night differential, and hazard pay.

---

## Expanded withholding tax (EWT) rate table

| ATC code | Description | Rate |
|----------|-------------|:----:|
| WI010 | Professional fees — individual (≤ PHP 3M gross income) | 5% |
| WI011 | Professional fees — individual (> PHP 3M gross income) | 10% |
| WI020 | Professional fees — juridical (corporations) | 10% |
| WI040 | Income payments to partners of GPP | 10%/15% |
| WI050 | Rent — real property | 5% |
| WI060 | Rent — personal property | 5% |
| WI070 | Cinematographic film rentals | 5% |
| WI080 | Income payments to sub-contractors | 2% |
| WI100 | Government money payments to suppliers | 1%/2%/5% |
| WI120 | Tolling fees | 5% |
| WI150 | Income payments to suppliers of goods | 1% |
| WI157 | Income payments to suppliers of services | 2% |
| WI160 | Commission payments | 5%/10% |

---

## Per-form execution steps

### BIR 1601-C — Monthly WHT on compensation

??? abstract "Step-by-step"
    1. **Extract payroll data** from Odoo:

        ```sql
        SELECT
            employee_id,
            SUM(amount) AS gross_compensation,
            SUM(CASE WHEN category = 'WHT' THEN amount ELSE 0 END) AS tax_withheld
        FROM hr_payslip_line
        WHERE slip_id IN (
            SELECT id FROM hr_payslip
            WHERE date_from >= '2026-03-01' AND date_to <= '2026-03-31'
            AND state = 'done'
        )
        GROUP BY employee_id;
        ```

    2. **Calculate total remittance**: Sum all WHT on compensation for the period.
    3. **Populate form fields** in eBIRForms or `ipai_bir_filing`:
        - Schedule 1: Tax withheld per employee category
        - Total taxes withheld for remittance
        - Prior month adjustments (if any)
    4. **Validate**: Total WHT = sum of individual payslip WHT lines.
    5. **Submit** via eBIRForms + pay via AAB.

### BIR 0619-E — Monthly expanded WHT remittance

??? abstract "Step-by-step"
    1. **Extract EWT data** from Odoo (vendor payments with WHT):

        ```sql
        SELECT
            tax.name AS atc_code,
            SUM(aml.debit) AS tax_base,
            SUM(aml.credit) AS tax_withheld
        FROM account_move_line aml
        JOIN account_tax tax ON aml.tax_line_id = tax.id
        WHERE aml.date BETWEEN '2026-03-01' AND '2026-03-31'
          AND tax.tax_group_id = (
              SELECT id FROM account_tax_group WHERE name = 'EWT'
          )
        GROUP BY tax.name;
        ```

    2. **Group by ATC code** and compute totals.
    3. **Populate 0619-E** form with total amount of taxes withheld.
    4. **Cross-check** to GL WHT payable account balance for the period.
    5. **Submit** via eBIRForms + pay via AAB.

### BIR 2550Q — Quarterly VAT return

??? abstract "Step-by-step"
    1. **Extract output VAT** (sales) and **input VAT** (purchases) from Odoo:

        ```sql
        -- Output VAT
        SELECT SUM(aml.credit) AS output_vat
        FROM account_move_line aml
        JOIN account_tax tax ON aml.tax_line_id = tax.id
        WHERE tax.name LIKE '%Output VAT%'
          AND aml.date BETWEEN '2026-01-01' AND '2026-03-31';

        -- Input VAT
        SELECT SUM(aml.debit) AS input_vat
        FROM account_move_line aml
        JOIN account_tax tax ON aml.tax_line_id = tax.id
        WHERE tax.name LIKE '%Input VAT%'
          AND aml.date BETWEEN '2026-01-01' AND '2026-03-31';
        ```

    2. **Calculate VAT payable**: Output VAT - Input VAT.
    3. **Prepare quarterly summary**: Sales by VAT category (vatable, zero-rated, exempt).
    4. **Populate 2550Q** with quarterly totals and monthly breakdown.
    5. **Submit** via eBIRForms + pay via AAB.
    6. **Attach** Summary List of Sales (SLS) and Summary List of Purchases (SLP).

### BIR 1601-EQ — Quarterly expanded WHT return

??? abstract "Step-by-step"
    1. Summarize all EWT for the quarter from the monthly 0619-E data.
    2. Consolidate by ATC code, payee TIN, and payee name.
    3. Prepare Schedule 1 (QAP — quarterly alphabetical list of payees).
    4. Populate form in eBIRForms.
    5. Validate: total on 1601-EQ = sum of 3 monthly 0619-E filings.
    6. Submit + attach QAP as a `.dat` file.

### BIR 1702-RT — Annual income tax return

??? abstract "Step-by-step"
    See [year-end tasks](year-end-tasks.md#bir-form-1702-rt--annual-income-tax-return) for the calculation and filing process.

### BIR 1604-E — Annual WHT information return

??? abstract "Step-by-step"
    See [year-end tasks](year-end-tasks.md#bir-form-1604-e--annual-information-return-on-wht-compensation) for details.

---

## Filing process

### Submission channels

| Channel | Use case |
|---------|----------|
| **eBIRForms** | Desktop application — all form types, required for attachments |
| **eFPS** | Online portal — large taxpayers only, select forms |
| **RDO** | Revenue District Office — manual filing (last resort) |
| **AAB** | Authorized Agent Bank — tax payment (after form submission) |

### Standard filing workflow

```
1. Prepare data in Odoo
2. Generate form in eBIRForms (or ipai_bir_filing module)
3. Validate form totals against GL
4. Obtain Tax Manager approval
5. Submit via eBIRForms or eFPS
6. Pay via AAB (on or before deadline)
7. File BIR 2307 certificates with payees
8. Archive: confirmation receipt + form + payment proof
```

!!! warning "Filing vs. payment"
    Filing and payment are separate acts. A form filed on time but paid late still incurs interest. Always file AND pay before the deadline.

---

## Penalty calculations

### Late filing

| Penalty component | Calculation |
|-------------------|-------------|
| **Surcharge** | 25% of the tax due (or 50% for fraud/willful neglect) |
| **Interest** | 12% per annum on unpaid tax (from deadline to payment date) |
| **Compromise penalty** | Varies by BIR schedule (negotiated) |

### Formula

```
Total penalty = Tax due × 25% (surcharge)
              + Tax due × 12% × (days late / 365) (interest)
              + Compromise penalty (if applicable)
```

??? example "Penalty calculation example"
    A company owes PHP 100,000 in EWT and files 45 days late:

    ```
    Surcharge:  100,000 × 25%                    = PHP  25,000
    Interest:   100,000 × 12% × (45/365)         = PHP   1,479
    Compromise: (per BIR schedule, assume)        = PHP   1,000
    ─────────────────────────────────────────────────────────────
    Total penalty:                                  PHP  27,479
    Total amount due: 100,000 + 27,479            = PHP 127,479
    ```

---

## 2026 filing calendar

| Month | Deadline | Forms due |
|-------|----------|-----------|
| January | Jan 10 | 1601-C, 0619-E (Dec) |
| | Jan 25 | 2550Q (Q4 prev year) |
| | Jan 31 | 1604-E (annual), 1601-EQ (Q4), 1601-FQ (Q4) |
| February | Feb 10 | 1601-C, 0619-E (Jan) |
| March | Mar 10 | 1601-C, 0619-E (Feb) |
| April | Apr 10 | 1601-C, 0619-E (Mar) |
| | Apr 15 | 1702-RT (annual income tax) |
| | Apr 25 | 2550Q (Q1) |
| | Apr 30 | 1601-EQ (Q1), 1601-FQ (Q1) |
| May | May 10 | 1601-C, 0619-E (Apr) |
| June | Jun 10 | 1601-C, 0619-E (May) |
| July | Jul 10 | 1601-C, 0619-E (Jun) |
| | Jul 25 | 2550Q (Q2) |
| | Jul 31 | 1601-EQ (Q2), 1601-FQ (Q2) |
| August | Aug 10 | 1601-C, 0619-E (Jul) |
| September | Sep 10 | 1601-C, 0619-E (Aug) |
| October | Oct 10 | 1601-C, 0619-E (Sep) |
| | Oct 25 | 2550Q (Q3) |
| | Oct 31 | 1601-EQ (Q3), 1601-FQ (Q3) |
| November | Nov 10 | 1601-C, 0619-E (Oct) |
| December | Dec 10 | 1601-C, 0619-E (Nov) |

---

## Record keeping requirements

| Record type | Retention period |
|-------------|-----------------|
| Books of accounts | 10 years from last entry |
| Tax returns and attachments | 10 years from filing date |
| Receipts and invoices | 10 years from date of issuance |
| BIR 2307 certificates | 10 years |
| Payroll records | 3 years (DOLE requirement) |
| General ledger and journals | 10 years |

!!! info "Digital records"
    BIR Revenue Regulation No. 9-2024 allows electronic storage of source documents provided the taxpayer maintains a Computerized Accounting System (CAS) permit or uses a BIR-registered system.

---

## BIR audit defense protocol

??? abstract "Prepare for BIR examination"
    **When a Letter of Authority (LOA) is received:**

    1. **Verify the LOA**: Confirm authenticity with the issuing RDO.
    2. **Assign a point person**: Designate a Tax Manager or external tax counsel.
    3. **Prepare the standard audit file**:
        - Books of accounts (GL, SL)
        - Tax returns for the period under audit
        - Supporting invoices and receipts
        - Bank statements
        - Payroll records
        - Summary of related party transactions
    4. **Set up a dedicated workspace**: Provide auditors with a controlled environment — never give direct system access.
    5. **Document all interactions**: Keep a log of every document provided and question answered.
    6. **Review preliminary findings**: Before signing any waiver, review with tax counsel.
    7. **Respond within deadlines**: BIR imposes strict timelines — missed responses can result in adverse assessments.

    **Common audit triggers:**

    | Trigger | Mitigation |
    |---------|------------|
    | VAT refund claims | Maintain complete SLS/SLP documentation |
    | High deductions vs. revenue ratio | Document business purpose for all deductions |
    | WHT discrepancies (2307 vs. 1601-C) | Monthly reconciliation per close process |
    | Related party transactions | Transfer pricing documentation |
    | Unusual revenue fluctuations | Maintain variance analysis from close process |
