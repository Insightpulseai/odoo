# Expense Liquidation Agent - Constitution

## Vision
To provide a policy-governed, multi-channel expense and cash-advance liquidation capability that ensures 100% compliance with corporate financial obligations while minimizing employee friction.

## Problem / Scope
- **Current State**: Manual, paper-based, or friction-heavy digital expense submission often leads to delayed liquidations and uncollected corporate receivables.
- **Future State**: A multi-channel submission system (Telegram, n8n, Odoo UI) that automates the audit and reconciliation of cash advances and out-of-pocket reimbursements.
- **Scope**: Multi-channel expense capture and cash-advance liquidation within the Odoo ecosystem.

## In-Scope Channels
- **`telegram_bot`**: Primary mobile ingress for quick receipt capture and status updates.
- **`n8n_webhook_ingress`**: Orchestration and normalization layer for external submissions.
- **`odoo_ui`**: First-party fallback for manual adjustment, high-volume batch entry, and administrative oversight.

## Out of Scope
- **Full n8n Ecosystem**: We are not implementing every possible n8n/Odoo integration (e.g., Shopify, Slack) in v1.
- **n8n as a Database**: n8n must not be used as a system of record for financial transactions.
- **Agentic Autonomy (L5)**: The agent provides extraction and audit assist; final posting remains an authorized financial action.

## System of Record (SoR)
- **Odoo (ERP)**: Remains the absolute System of Record for liquidation records, approvals, balances, and formal accounting settlements.
- **n8n**: Orchestration and transient normalization only.
- **Azure Foundry / Document Intelligence**: Intelligence layer for extraction and policy-assist only.

## Guiding Principles
- **Idempotency first**: No duplicate transactions from unreliable mobile networks.
- **Fail-Closed**: If policy signals (Foundry/Audit) are unclear, the transaction blocks for human review.
- **Evidence-First**: Every settlement must be anchored to verifiable evidence (OCR results + attachments).
