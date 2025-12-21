# BIR Tax Compliance - Product Requirements

## Overview

Philippine Bureau of Internal Revenue (BIR) tax compliance module for Odoo CE 18.
Covers all 36 eBIRForms with automated computation and filing support.

## User Stories

### As a Finance Manager
- I want to generate monthly VAT declarations (2550M) automatically
- I want to track all withholding tax obligations in one dashboard
- I want alerts 5 days before filing deadlines

### As a Payroll Officer
- I want compensation withholding (1601-C) computed from payroll data
- I want annual alphalist (1604-CF) generated automatically

### As CFO
- I want a compliance dashboard showing filing status across all tax types
- I want exception alerts when forms have validation errors

## Feature Requirements

### F1: VAT Compliance (Forms 2550M, 2550Q)
- Aggregate sales by VAT category (standard, zero-rated, exempt)
- Calculate VAT output from sales invoices
- Track VAT input from purchase invoices
- Compute net VAT payable/refundable
- Generate BIR Form 2550M (monthly) and 2550Q (quarterly)

### F2: Withholding Tax (Forms 1600, 1601-C, 1601-E, 1604-CF)
- Track withholding on compensation (payroll integration)
- Track expanded withholding (suppliers, contractors)
- Track final withholding (interest, dividends)
- Generate monthly remittance forms
- Generate annual information returns (alphalist)

### F3: Income Tax (Forms 1701, 1702)
- Compute taxable income (revenue - expenses)
- Apply correct tax brackets (individual vs corporate)
- Track quarterly estimates (1701Q, 1702Q)
- Generate annual returns

### F4: Excise Tax (Forms 2200A/P/T/M/AN)
- Track excisable products (alcohol, tobacco, petroleum, minerals)
- Compute per-unit excise tax
- Monitor stock movements of excisable goods
- Generate monthly returns

### F5: Filing Dashboard
- Calendar view of all filing deadlines
- Status indicators (draft, filed, confirmed)
- Exception alerts
- BIR reference number tracking

## Non-Functional Requirements

- Performance: Generate any form in < 5 seconds
- Accuracy: 100% match with BIR computation rules
- Availability: 99.5% uptime during filing windows
- Security: RLS by company, encrypted TIN storage
