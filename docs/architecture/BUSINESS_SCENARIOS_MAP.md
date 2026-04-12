# Business Scenarios Capability Map — Pulser for Odoo

This document maps the Pulser for Odoo specialized capabilities to formal institutional business scenarios, ensuring that all agentic logic delivers measurable business-process outcomes.

---

## 1. Scenario Anchoring (BOM 2)

Pulser capabilities are anchored to the **Project to Profit (80)** and **Record to Report (90)** scenarios.

### Project to Profit (80)
- **Goal**: Win more deals, accelerate delivery, and maximize profitability.
- **Pulser Capabilities**:
    - **PPM Assistant**: OKR tracking, WBS status, and resource burn analysis.
    - **Margin Guru**: Real-time project profitability analysis (Budget vs. Actual).
    - **Resource Shell**: Sidebar for PMs to review team allocations during resourcing.
- **Core Modules**: `ipai_finance_ppm`, `project`.

### Record to Report (90)
- **Goal**: Maintain financial integrity and provide actionable insights.
- **Pulser Capabilities**:
    - **Close Assistant**: Monitoring close-task progress and exception handling.
    - **Tax Guru (PH)**: Grounded tax determination and BIR filing prep.
    - **Reconciliation Studio**: High-fidelity Excel ODATA sync for TB/Aging audits.
- **Core Modules**: `ipai_finance_close_seed`, `ipai_bir_tax_compliance`, `account`.

## 2. Accrual and Card Hygiene Benchmarks (BOM 14)

Pulser implements **SAP Concur-grade reporting** for outstanding liabilities and card security.

### Finance Accrual Visibility
Pulser provides visibility into transaction accruals to ensure month-end liability accuracy.
- **Accrual Report Logic**: Identify transactions (Invoices, Bills, T&E) that have been recorded in the system but are not yet assigned to an expense report or have not yet been paid.
- **Accrual by Date Range**: Temporal visibility into when liabilities were incurred vs. when they are expected to clear.

### Card Hygiene and Hygiene
Pulser monitors corporate card security and processing efficiency.
- **Unassigned Transactions**: Identify card swipes not yet linked to a business expense.
- **Unsubmitted Reports**: Identify card-linked reports that have not been submitted within the 10-day policy window.
- **Reminders**: (Open Question: Resolution) Authorization for automated employee reminders (Pending Review).

## 3. Specialist Capability Mapping

| Specialist Agent | Parent Scenario | Primary KPI |
|------------------|-----------------|-------------|
| AP Agent | Record to Report | AP Aging / Accrual Accuracy |
| Tax Guru (PH) | Record to Report | Filing Deadline Integrity |
| PPM Assistant | Project to Profit | Margin Variance |
| Reporting Agent | Both | artifact generation latency |

---

*Last updated: 2026-04-11*
