# Finance Domain Target State

## Benchmark basis

This target state follows the benchmark pattern:

- governed domain data models
- business templates built on those models
- agent experiences built on top of both

## Canonical stack

1. Odoo and other source systems remain transactional SoR
2. Finance semantic products are the governed analytical contract
3. Finance templates are the reusable presentation/decision layer
4. Pulser / Odoo Copilot / Tax Guru are grounded consumers, not the semantic authority

## Required semantic products

- finance_gl
- finance_ap
- finance_ar
- finance_profitability

## Required finance templates

- Trial Balance
- YTD Trial Balance
- YTD Financial Statement
- Profitability Analysis
- AP Aging
- AP Payment Trends
- AP Supplier Balances
- AR Aging
- AR Customer Balances

## Agent boundaries

### Pulser Finance Assistant

Explain and summarize governed finance outputs.

### Odoo Copilot Finance

Guide and execute bounded finance workflows using governed contracts.

### Tax Guru

Operate only within declared tax/domain boundaries and escalate unsupported or uncertain scenarios.
