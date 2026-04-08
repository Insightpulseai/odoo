# Odoo Expense App Review & AI Agent Proposal

## Current State Analysis

### 1. Standard Odoo `hr_expense`
- **Models**: `hr.expense` (Individual lines), `hr.expense.sheet` (Reports).
- **Workflow**: `draft` -> `submitted` -> `approved` -> `posted` -> `paid`.
- **Limitation**: Primarily focused on reimbursement of employee out-of-pocket expenses. Lacks structured "Cash Advance Liquidation" (where money is given *before* spending).

### 2. IPAI Custom Extension (`ipai_hr_expense_liquidation`)
- **Focus**: Adds "Liquidation" logic common in enterprise domains (Concur-style).
- **Key Modes**: Cash Advance, Reimbursement, Petty Cash.
- **Workflow**: 8-state high-integrity flow (`draft` -> `submitted` -> `manager_approved` -> `finance_approved` -> `released` -> `in_liquidation` -> `liquidated` -> `closed`).
- **Policy Engine**: Built-in rules for amount limits, receipt requirements, and categories.

## AI Agent Opportunity: The "Expense Liquidation Agent"

### Core Capabilities
1.  **Autonomous Liquidator**: Automatically matches uploaded receipts to open Cash Advances.
2.  **Policy Auditor**: Scans every expense line (via Foundry/OCR) against the `hr.expense.policy.rule` set.
3.  **Liquidation Drafter**: Generates the settlement (Return of funds or additional reimbursement) based on the balance.
4.  **Anomaly Detection**: Flags duplicate receipts or split-transaction attempts (smurfing).

### Integration Pattern
- **Authority**: Platform Engine (Sanitization + Gating).
- **SoR**: Odoo (transactional records).
- **Bridge**: `ipai_foundry` (OCR and Reasoning).

## Recommendation
Initialize the **Expense Liquidation Agent Spec Kit** (Phase 29) to productize the skeleton and align it with the V2 Governance as Code framework.
