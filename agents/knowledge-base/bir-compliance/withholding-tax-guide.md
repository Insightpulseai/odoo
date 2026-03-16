---
title: "Withholding Tax Guide"
kb_scope: "bir-compliance"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Withholding Tax Guide

## Overview

Withholding tax is a mechanism where the payer deducts tax from payments made to vendors, contractors, employees, and other payees, and remits the withheld amount to the BIR. This guide covers the three types of withholding tax in the Philippine tax system and their implementation in Odoo CE 19.0.

**Legal Basis**: NIRC Sections 57-58, as amended by TRAIN Law (RA 10963) and Revenue Regulations No. 11-2018.

---

## Types of Withholding Tax

### 1. Withholding Tax on Compensation (WTC)

Tax withheld by employers from employee salaries, wages, and other compensation.

### 2. Expanded Withholding Tax (EWT)

Tax withheld by the income payor on certain income payments to resident payees (individuals and corporations).

### 3. Final Withholding Tax (FWT)

Tax withheld that constitutes the final tax on the income. The payee no longer includes this income in the annual return.

---

## Withholding Tax on Compensation

### Tax Table (TRAIN Law, Effective January 1, 2023 Onwards)

| Annual Taxable Income | Tax Rate |
|:----------------------|:---------|
| PHP 0 — PHP 250,000 | 0% |
| PHP 250,001 — PHP 400,000 | 15% of excess over PHP 250,000 |
| PHP 400,001 — PHP 800,000 | PHP 22,500 + 20% of excess over PHP 400,000 |
| PHP 800,001 — PHP 2,000,000 | PHP 102,500 + 25% of excess over PHP 800,000 |
| PHP 2,000,001 — PHP 8,000,000 | PHP 402,500 + 30% of excess over PHP 2,000,000 |
| Over PHP 8,000,000 | PHP 2,202,500 + 35% of excess over PHP 8,000,000 |

### Non-Taxable Compensation

The following are excluded from taxable compensation:

1. **13th Month Pay and Other Benefits**: Exempt up to PHP 90,000 per year
   - 13th month pay
   - Other benefits (Christmas bonus, productivity incentives, etc.)
   - De minimis benefits

2. **De Minimis Benefits** (exempt amounts per Revenue Regulations):
   - Monetized unused vacation leave: 10 days or less
   - Medical cash allowance: PHP 1,500/month
   - Rice subsidy: PHP 2,000/month or 1 sack of 50kg rice/month
   - Uniform allowance: PHP 6,000/year
   - Actual medical benefits: PHP 10,000/year
   - Laundry allowance: PHP 300/month
   - Employee achievement awards: PHP 10,000/year
   - Christmas gift: PHP 5,000
   - Daily meal allowance for overtime: 25% of basic minimum wage

3. **Mandatory Contributions** (employee share):
   - SSS contributions
   - PhilHealth contributions
   - Pag-IBIG contributions

### BIR Form 1601-C — Monthly Remittance

**Filing**: 10th of the following month (15th for eFPS filers)

**Content**: Total compensation paid, total tax withheld for the month

**Odoo Preparation**:
1. Process payroll for the month via HR > Payroll
2. Review the payroll summary showing gross pay, deductions, and net pay
3. The withholding tax computation is automatic based on the tax table
4. Extract total compensation and total tax withheld for the 1601-C form

### BIR Form 2316 — Annual Certificate

Issued to each employee by January 31 of the following year.

Contains:
- Employee's name, TIN, and address
- Total compensation for the year
- Non-taxable compensation breakdown
- Taxable compensation
- Tax withheld
- Tax due (showing if there is a refund or amount still due)

The 2316 serves as the employee's substitute income tax return if the employee has no other income.

---

## Expanded Withholding Tax (EWT)

### EWT Rate Table

| Income Payment | Rate |
|:--------------|:-----|
| **Professional fees** | |
| - Individual (gross income < PHP 3M/year) | 5% |
| - Individual (gross income >= PHP 3M/year) | 10% |
| - Corporate (all) | 10% |
| - Juridical (non-individual) | 15% |
| **Rental payments** | |
| - Real property (to individual) | 5% |
| - Real property (to corporation) | 5% |
| - Personal property (to all) | 5% |
| **Purchase of goods** | |
| - From regular supplier (any amount) | 1% |
| **Purchase of services** | |
| - From regular supplier (any amount) | 2% |
| **Commissions and fees** | |
| - Insurance agents/brokers | 10% / 15% |
| - Customs brokers | 10% / 15% |
| - Advertising agencies | 2% |
| **Income payments to contractors** | |
| - General engineering contractors | 2% |
| - General building contractors | 2% |
| - Specialty contractors | 2% |
| **Management and consultancy fees** | 10% / 15% |
| **Director's fees** | 10% / 15% |
| **Tolling fees** | 5% |
| **Income payments to partners of GPPs** | 10% / 15% |

**Note**: The 10% vs 15% distinction for professional services depends on whether the payee is an individual (10%) or a juridical person/corporation (15%).

### When to Withhold

EWT must be withheld at the time of payment or at the time the income becomes payable (accrual), whichever comes first.

**Practical rule**: Withhold when you record the vendor bill or when you make the payment, whichever is earlier. In Odoo, the withholding is typically computed when the vendor bill is posted.

### EWT in Odoo

#### Tax Configuration

Create EWT tax codes in Odoo for each applicable rate:

| Tax Name | Rate | Type | Account |
|----------|:----:|------|---------|
| EWT - 1% Goods | -1% | Purchase | 211010 (EWT Payable) |
| EWT - 2% Services | -2% | Purchase | 211010 (EWT Payable) |
| EWT - 5% Professional (Individual) | -5% | Purchase | 211010 (EWT Payable) |
| EWT - 10% Professional (Individual High) | -10% | Purchase | 211010 (EWT Payable) |
| EWT - 10% Professional (Corporate) | -10% | Purchase | 211010 (EWT Payable) |
| EWT - 15% Professional (Juridical) | -15% | Purchase | 211010 (EWT Payable) |
| EWT - 5% Rental | -5% | Purchase | 211010 (EWT Payable) |

**Important**: EWT taxes are negative amounts because they reduce the amount payable to the vendor. The withheld amount is recorded as a liability (payable to BIR).

#### Vendor Bill Processing

1. Create the vendor bill as normal
2. On each bill line, apply the appropriate purchase tax:
   - VAT 12% (Input) — for the VAT component
   - EWT at the applicable rate — for the withholding component
3. The bill total shows:
   - Gross amount (VAT-exclusive)
   - Plus: Input VAT (12%)
   - Less: EWT (at applicable rate, on the VAT-exclusive amount)
   - = Net amount payable to vendor

**Example**:
- Service fee: PHP 100,000 (VAT-exclusive)
- Input VAT (12%): PHP 12,000
- EWT (2% on services): PHP 2,000
- Amount payable to vendor: PHP 100,000 + PHP 12,000 - PHP 2,000 = PHP 110,000
- Amount payable to BIR (EWT): PHP 2,000

#### Fiscal Position Mapping

Use fiscal positions to automatically apply the correct EWT rate based on the vendor's profile:

- **Vendor - Goods Supplier**: Maps to 1% EWT
- **Vendor - Service Provider**: Maps to 2% EWT
- **Vendor - Professional (Individual)**: Maps to 5% or 10% EWT
- **Vendor - Professional (Corporate)**: Maps to 10% EWT
- **Vendor - Rental**: Maps to 5% EWT

Assign the fiscal position on the vendor's partner record (Contacts > Vendor > Sales & Purchases tab > Fiscal Position).

### BIR Form 0619-E — Monthly Remittance

**Filing**: 10th of the following month (15th for eFPS)

**Content**: Total EWT withheld during the month, broken down by tax rate

**Odoo Preparation**:
1. Run the Tax Balance report filtered to EWT tax accounts
2. Group by tax type (1%, 2%, 5%, 10%, 15%)
3. Extract totals for each rate

### BIR Form 1601-EQ — Quarterly Remittance

**Filing**: Last day of the month following the quarter

**Content**: Summary of EWT for the quarter with alphalist of payees

The 1601-EQ includes an alphabetical list of all payees from whom EWT was withheld, showing:
- Payee name and TIN
- Nature of income payment
- Amount of income
- Amount of tax withheld

### BIR Form 2307 — Certificate of Creditable Tax Withheld

Issued to each vendor/payee, showing the total EWT withheld from their payments during the quarter.

**Issuance deadline**: Within 20 days after the end of each quarter.

**Odoo Generation**:
1. Navigate to Accounting > Reporting > Withholding Tax Report (custom)
2. Filter by quarter and vendor
3. Generate BIR Form 2307 for each vendor

The vendor uses Form 2307 to claim the withheld tax as a credit against their income tax.

---

## Final Withholding Tax (FWT)

### Common FWT Rates

| Income Payment | Rate |
|:--------------|:-----|
| Interest on bank deposits (peso) | 20% |
| Interest on bank deposits (foreign currency) | 15% |
| Royalties (books, literary works, musical compositions) | 10% |
| Royalties (other) | 20% |
| Prizes exceeding PHP 10,000 | 20% |
| Winnings (except PCSO and lotto) | 20% |
| Dividends from domestic corporation (to individuals) | 10% |
| Dividends from domestic corporation (to non-resident foreign corp) | 15% or treaty rate |
| Interest on any other debt instruments | 20% |
| Cash/property dividends to citizens and residents | 10% |
| Capital gains on sale of shares not traded in the stock exchange | 15% |
| Capital gains on sale of real property | 6% |
| Income of non-resident foreign corp (general) | 25% |
| Fringe benefits to managerial/supervisory employees | 35% grossed up |

### FWT on Non-Resident Payments

When paying non-resident individuals or foreign corporations:

1. **Non-resident alien not engaged in trade/business in PH**: 25% FWT on gross income
2. **Non-resident foreign corporation**: 25% on gross income (or treaty rate)
3. **Tax treaty relief**: If a tax treaty applies, the rate may be reduced. File a Certificate of Residence for Tax Treaty Relief Application (CORTT) Form with the BIR.

### BIR Form 0619-F — Monthly Remittance

**Filing**: 10th of the following month

**Content**: Total FWT withheld during the month

### BIR Form 1601-FQ — Quarterly Remittance

**Filing**: Last day of the month following the quarter

**Content**: Summary of FWT for the quarter with alphalist of payees

### BIR Form 2306 — Certificate of Final Tax Withheld

Issued to payees subject to FWT, showing the tax withheld at source.

---

## Odoo Implementation Summary

### Tax Groups Setup

| Tax Group | Purpose | Type |
|-----------|---------|------|
| VAT (Output) | Sales VAT | Sale |
| VAT (Input) | Purchase VAT | Purchase |
| EWT | Expanded withholding | Purchase (negative) |
| FWT | Final withholding | Purchase (negative) |
| WTC | Compensation withholding | Payroll |

### Account Mapping

| Account Code | Account Name | Purpose |
|:------------|:-------------|:--------|
| 114001 | Input VAT | Deferred input tax |
| 211001 | Output VAT | VAT collected on sales |
| 211002 | VAT Payable | Net VAT due to BIR |
| 211010 | EWT Payable | Expanded withholding payable |
| 211011 | FWT Payable | Final withholding payable |
| 211012 | WTC Payable | Compensation withholding payable |
| 114002 | Creditable Withholding Tax | EWT withheld by customers (asset) |

### Vendor Payment Flow

```
1. Vendor bill posted
   - Gross amount recorded as expense
   - Input VAT recorded as asset (114001)
   - EWT recorded as liability (211010)
   - Net payable = Gross + VAT - EWT

2. Payment made to vendor
   - Net amount paid from bank
   - Vendor bill marked as paid

3. Monthly BIR remittance (0619-E)
   - Total EWT liability remitted to BIR
   - Debit: EWT Payable (211010)
   - Credit: Bank (101001)

4. Quarterly certificate (2307)
   - Issued to each vendor
   - Vendor claims credit against their income tax
```

### Reporting Workflow

| Report | Frequency | Odoo Source |
|--------|-----------|-------------|
| EWT Summary by Rate | Monthly | Tax Balance Report > EWT group |
| EWT by Vendor | Quarterly | Partner Ledger > EWT accounts |
| FWT Summary | Monthly | Tax Balance Report > FWT group |
| Compensation WT Summary | Monthly | Payroll Module > Tax Report |
| WT Certificates (2307) | Quarterly | Custom print per vendor |
| WT Certificates (2316) | Annual | Payroll Module > Year-End |

---

## Common Withholding Tax Issues

| Issue | Resolution |
|-------|-----------|
| Vendor refuses to accept EWT deduction | EWT is mandatory by law. Explain that the 2307 certificate allows them to claim the credit. |
| Wrong EWT rate applied | Correct the vendor bill, recompute, and issue updated 2307 at quarter-end |
| Vendor has no TIN | Withhold at the highest applicable rate. Request TIN within 10 days. |
| EWT on advance payments | Withhold at the time of payment, even if the service has not been rendered |
| Accumulated creditable WT (2307 from customers) | Record as asset (114002). Apply as tax credit on quarterly ITR (1702Q). |
| Late remittance penalty | 25% surcharge + 12% interest. Remit immediately. |
