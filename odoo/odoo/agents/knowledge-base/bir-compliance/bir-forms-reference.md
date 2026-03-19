---
title: "BIR Forms Complete Reference"
kb_scope: "bir-compliance"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# BIR Forms Complete Reference

## Overview

This document provides a comprehensive reference of Bureau of Internal Revenue (BIR) forms commonly used by Philippine businesses. Each form entry includes its purpose, filing frequency, deadline, and how the supporting data is generated from Odoo CE 19.0.

---

## Registration Forms

### BIR Form 1901 — Application for Registration (Self-Employed / Mixed Income)

- **Purpose**: Register as a taxpayer for self-employed individuals, professionals, and mixed-income earners
- **When Filed**: Before commencing business or practice of profession
- **Requirements**: Valid government ID, proof of business address, DTI registration (for sole proprietors)
- **Odoo Relevance**: N/A — this is a one-time registration form

### BIR Form 1903 — Application for Registration (Corporations / Partnerships)

- **Purpose**: Register a corporation or partnership with the BIR
- **When Filed**: Within 30 days after SEC registration
- **Requirements**: SEC Certificate of Registration, Articles of Incorporation, Board resolution
- **Odoo Relevance**: Company TIN from this registration is entered in Odoo settings

### BIR Form 1905 — Application for Registration Information Update

- **Purpose**: Update taxpayer registration information (address, business activity, RDO transfer, closure)
- **When Filed**: Within 30 days of any change
- **Common Uses**: Change of registered address, change of business name, adding new business line, closure of branch
- **Odoo Relevance**: Update company information in Settings after BIR approves the change

### BIR Form 2303 — Certificate of Registration (COR)

- **Purpose**: Proof of BIR registration showing TIN, registered business name, tax types, and filing obligations
- **Issued By**: BIR upon successful registration
- **Display Requirement**: Must be displayed conspicuously at the principal place of business
- **Odoo Relevance**: Reference for configuring tax types and filing frequencies in Odoo

### BIR Form 0605 — Annual Registration Fee

- **Purpose**: Payment of annual registration fee (PHP 500 per business establishment)
- **Deadline**: January 31 of each year
- **Payment**: Per establishment/branch, not per taxpayer
- **Odoo Relevance**: Record as prepaid expense or registration fee expense

---

## Income Tax Forms

### BIR Form 1700 — Annual Income Tax Return (Individuals — Compensation Only)

- **Purpose**: Annual income tax return for individuals earning purely compensation income
- **Deadline**: April 15 of the following year
- **Who Files**: Employees with only one employer and no other source of income (optional; 2316 can serve as substitute)
- **Odoo Relevance**: HR Payroll generates the underlying data. Form 2316 is the typical substitute.

### BIR Form 1701 — Annual Income Tax Return (Individuals — Self-Employed / Mixed Income)

- **Purpose**: Annual ITR for self-employed individuals, professionals, and mixed-income earners
- **Deadline**: April 15 of the following year
- **Schedules**: Includes schedules for gross sales/receipts, cost of sales, operating expenses
- **Odoo Relevance**: Income statement data from Odoo for business income portion

### BIR Form 1702 — Annual Income Tax Return (Corporations)

- **Purpose**: Annual corporate income tax return
- **Deadline**: April 15 of the following year
- **Variants**:
  - **1702-RT**: Regular tax rate (25% or 20%)
  - **1702-EX**: Exempt or subject to special/preferential rate
  - **1702-MX**: Mixed income (regular + special rate)
- **Key Computations**:
  - Gross income from operations
  - Allowable deductions (itemized or optional standard deduction of 40%)
  - Taxable income
  - Regular corporate income tax (RCIT) at 25% (or 20% for small companies)
  - Minimum corporate income tax (MCIT) at 1% of gross income
  - Tax due = higher of RCIT or MCIT (starting 4th year)
  - Less: quarterly tax payments, creditable withholding taxes
  - Tax payable or overpayment
- **Odoo Relevance**: Income statement and balance sheet from `account_financial_report` and `mis_builder`. Tax adjustments computed manually or via custom schedule.

### BIR Form 1702Q — Quarterly Income Tax Return (Corporations)

- **Purpose**: Quarterly corporate income tax return
- **Deadline**: 60 days after the end of the quarter
- **Filed For**: Q1, Q2, Q3 only (Q4 is covered by the annual return)
- **Odoo Relevance**: Quarterly income statement from MIS Builder

---

## VAT Forms

### BIR Form 2550M — Monthly VAT Return

- **Purpose**: Monthly declaration and payment of VAT
- **Deadline**: 25th of the following month
- **Filed For**: Non-quarter-ending months (Jan, Feb, Apr, May, Jul, Aug, Oct, Nov)
- **Key Lines**:
  - Output VAT on taxable sales
  - Input VAT on domestic purchases and imports
  - Excess input VAT carried forward
  - Net VAT payable
- **Odoo Source**: Tax Balance report filtered by VAT accounts for the month

### BIR Form 2550Q — Quarterly VAT Return

- **Purpose**: Quarterly declaration and payment of VAT
- **Deadline**: 25th of the month following the quarter
- **Filed For**: Quarter-ending months (Mar, Jun, Sep, Dec)
- **Additional Schedules**:
  - Schedule of domestic sales (taxable, zero-rated, exempt)
  - Schedule of export sales
  - Schedule of domestic purchases
  - Schedule of importations
  - Schedule of government payments with VAT withheld
- **Odoo Source**: Sales and purchase journals grouped by tax type for the quarter

### BIR Form 2551M — Monthly Percentage Tax Return

- **Purpose**: Monthly percentage tax return for non-VAT registered taxpayers
- **Deadline**: 20th of the following month
- **Rate**: 3% of gross sales/receipts (reduced from 3% — check latest RR for current rate)
- **Who Files**: Non-VAT registered persons with gross sales/receipts not exceeding PHP 3,000,000 per year
- **Odoo Source**: Total sales for the month from the sales journal

---

## Withholding Tax Forms

### BIR Form 1601-C — Monthly Remittance of Withholding Tax on Compensation

- **Purpose**: Remit taxes withheld from employee compensation
- **Deadline**: 10th of the following month (15th for eFPS)
- **Content**: Total compensation paid, total tax withheld, number of employees
- **Odoo Source**: Payroll summary from the HR module

### BIR Form 0619-E — Monthly Remittance of Expanded Withholding Tax

- **Purpose**: Remit expanded withholding tax (EWT) on payments to vendors and professionals
- **Deadline**: 10th of the following month (15th for eFPS)
- **Content**: Total EWT withheld, broken down by tax rate (1%, 2%, 5%, 10%, 15%)
- **Odoo Source**: Tax Balance report filtered by EWT tax accounts

### BIR Form 0619-F — Monthly Remittance of Final Withholding Tax

- **Purpose**: Remit final withholding tax on interest, dividends, royalties, etc.
- **Deadline**: 10th of the following month (15th for eFPS)
- **Content**: Total FWT withheld by income type
- **Odoo Source**: Tax Balance report filtered by FWT tax accounts

### BIR Form 1601-EQ — Quarterly Remittance of Expanded Withholding Tax

- **Purpose**: Quarterly summary remittance of EWT with alphalist of payees
- **Deadline**: Last day of the month following the quarter
- **Attachments**: Alphabetical list of payees (MAP/EWT) showing:
  - Payee TIN, name, and address
  - Nature of income payment
  - Amount of income
  - Amount of tax withheld
- **Odoo Source**: Partner ledger filtered by EWT accounts, grouped by vendor

### BIR Form 1601-FQ — Quarterly Remittance of Final Withholding Tax

- **Purpose**: Quarterly summary remittance of FWT with alphalist of payees
- **Deadline**: Last day of the month following the quarter
- **Attachments**: Alphabetical list of payees (MAP/FWT)
- **Odoo Source**: Partner ledger filtered by FWT accounts, grouped by payee

---

## Annual Information Returns

### BIR Form 1604-CF — Annual Information Return (Compensation and Final WT)

- **Purpose**: Annual summary of all compensation paid and final taxes withheld
- **Deadline**: January 31 of the following year
- **Attachments**:
  - Alphabetical list of employees with compensation and tax data
  - Individual BIR Form 2316 for each employee
- **Odoo Source**: HR Payroll annual summary

### BIR Form 1604-E — Annual Information Return (Expanded WT)

- **Purpose**: Annual summary of all expanded withholding taxes
- **Deadline**: March 1 of the following year
- **Attachments**: Alphabetical list of payees showing total income and EWT per payee
- **Odoo Source**: Annual partner ledger filtered by EWT accounts

---

## Tax Certificates

### BIR Form 2307 — Certificate of Creditable Tax Withheld at Source

- **Purpose**: Certificate issued to vendors/payees showing EWT withheld from their payments
- **Issued By**: The payor (your company)
- **Issued To**: The payee (vendor/professional)
- **Frequency**: Quarterly (or upon request)
- **Deadline**: Within 20 days after end of each quarter
- **Content**:
  - Payor name, TIN, address
  - Payee name, TIN, address
  - Nature of income payment
  - Period covered
  - Amount of income
  - Tax rate and amount withheld
- **Odoo Source**: Withholding tax report by vendor for the quarter

### BIR Form 2306 — Certificate of Final Tax Withheld at Source

- **Purpose**: Certificate for income subject to final withholding tax
- **Issued By**: The payor
- **Issued To**: The payee
- **Use Case**: Interest payments, dividends, royalties to non-residents
- **Odoo Source**: FWT transaction detail by payee

### BIR Form 2316 — Certificate of Compensation Payment/Tax Withheld

- **Purpose**: Annual certificate of compensation and taxes for each employee
- **Issued By**: Employer
- **Issued To**: Employee
- **Deadline**: January 31 of the following year
- **Substitute Return**: For employees with single employer and no other income, 2316 serves as the annual income tax return (substitute filing)
- **Content**:
  - Employee personal information and TIN
  - Compensation breakdown (basic, overtime, holiday, 13th month, bonuses)
  - Non-taxable compensation (de minimis, mandatory contributions, 13th month < PHP 90k)
  - Taxable compensation
  - Tax due and tax withheld
  - Excess withholding refunded or adjustment
- **Odoo Source**: HR Payroll > Annual Tax Certificate per employee

---

## Documentary Stamp Tax

### BIR Form 2000 — Documentary Stamp Tax Return

- **Purpose**: Pay documentary stamp tax (DST) on specified documents and transactions
- **Deadline**: Within 5 days after close of the month when the document was signed/issued
- **Common DST-Liable Transactions**:
  - Debt instruments (promissory notes, bonds): PHP 1.50 per PHP 200
  - Shares of stock (original issuance): PHP 2.00 per PHP 200 of par value
  - Bank checks: PHP 3.00 per check
  - Insurance policies: varying rates
  - Lease agreements: varying rates based on rent
  - Real property transfers: PHP 15.00 per PHP 1,000
- **Odoo Relevance**: Track DST payments as a tax expense. May require manual journal entry.

---

## Miscellaneous Forms

### BIR Form 1914 — Application for Tax Credits/Refunds

- **Purpose**: Apply for refund or issuance of tax credit certificate for excess tax payments
- **Common Use Cases**:
  - Excess input VAT on zero-rated sales (refundable within 2 years)
  - Overpayment of income tax
  - Erroneously paid taxes
- **Deadline**: Within 2 years from date of payment or close of taxable quarter
- **Odoo Relevance**: Track refund applications and status

### BIR Form 1906 — Application for Authority to Print Receipts/Invoices

- **Purpose**: Request BIR authority to print official receipts and sales invoices
- **When Filed**: Before printing receipts/invoices from a new accredited printer
- **Validity**: Each ATP covers a specific range of serial numbers
- **Odoo Relevance**: Ensure invoice numbering in Odoo matches the ATP-authorized range

### BIR Form 2000-OT — Documentary Stamp Tax (One-Time Transactions)

- **Purpose**: DST payment for one-time transactions not covered by the monthly 2000
- **When Filed**: Within 5 days of the transaction
- **Odoo Relevance**: Record as a one-time tax expense

---

## Quick Reference: Filing Deadlines by Form

| Form | Frequency | Deadline |
|:-----|:----------|:---------|
| 0605 | Annual | January 31 |
| 0619-E | Monthly | 10th (15th eFPS) |
| 0619-F | Monthly | 10th (15th eFPS) |
| 1601-C | Monthly | 10th (15th eFPS) |
| 1601-EQ | Quarterly | Last day of month following quarter |
| 1601-FQ | Quarterly | Last day of month following quarter |
| 1604-CF | Annual | January 31 |
| 1604-E | Annual | March 1 |
| 1700 | Annual | April 15 |
| 1701 | Annual | April 15 |
| 1702 | Annual | April 15 |
| 1702Q | Quarterly | 60 days after quarter end |
| 2000 | Monthly | 5th of following month |
| 2307 | Quarterly | 20 days after quarter end |
| 2316 | Annual | January 31 |
| 2550M | Monthly | 25th (non-quarter months) |
| 2550Q | Quarterly | 25th of month following quarter |
| 2551M | Monthly | 20th |

---

## Odoo Data Sources Summary

| BIR Form | Odoo Module / Report |
|:---------|:---------------------|
| 2550M/Q | Accounting > Tax Balance (VAT accounts) |
| 1601-C | HR Payroll > Monthly Tax Summary |
| 0619-E | Accounting > Tax Balance (EWT accounts) |
| 0619-F | Accounting > Tax Balance (FWT accounts) |
| 1601-EQ | Accounting > Partner Ledger (EWT accounts, quarterly) |
| 1601-FQ | Accounting > Partner Ledger (FWT accounts, quarterly) |
| 1604-CF | HR Payroll > Annual Compensation Summary |
| 1604-E | Accounting > Annual EWT Summary by Payee |
| 1702/1702Q | Accounting > Income Statement (MIS Builder) |
| 2307 | Accounting > WT Certificate Report (per vendor, per quarter) |
| 2316 | HR Payroll > Annual Tax Certificate (per employee) |
