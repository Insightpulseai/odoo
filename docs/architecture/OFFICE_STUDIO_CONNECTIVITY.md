# Office Studio Connectivity — Pulser for Odoo

This document formalizes high-fidelity Office connectivity for specialized finance-operations tasks, defining the functional requirements for the Pulser Office Studios.

---

## 1. Office Capability Matrix (BOM 4, 14)

Pulser delivers specialized capabilities through the Office suite, anchored in the **Pulser Core authority** (Odoo/Foundry).

### Excel Studio (Reconciliation & Analysis)
- **ODATA v4 Sync**: Native high-fidelity data pulling for Trial Balances, AR/AP aging, and General Ledger entries.
- **Reconciliation Templates**: Pre-configured workbooks for Month-End close tasks, supporting calculated variances and variance explanations.
- **Draft Proposal**: (Open Question: Review required) Support for generating "Draft Adjustment Proposals" back to the Core Hub for human approval.

### Outlook Studio (Collections & AR)
- **Context-aware Sidebar**: Retrieving Customer AR aging, credit limits, and recent invoice history directly in the task pane.
- **AI-assisted Collections**: Generating professional collection emails with embedded links to the Customer Portal (Odoo/Pulser) and secure payment gateways.

### PowerPoint & Word Studio (Board Reporting)
- **Automated Reporting Packs**: assembly of Board and Management decks from Odoo profitability and project metadata.
- **Evidence Persistence**: Retention of grounding citations and evidence source links (Odoo Documents) within the document metadata to support auditability.

## 2. The "Office Shell" Interaction Pattern (BOM 5)

Office Studios are implemented as **Stateless Spokes** within the Enterprise Shell:
- **Hosting**: Native Office Add-ins (Excel/Outlook/Word).
- **Authentication**: Mandatory **Microsoft Entra ID (OIDC)** handoff. No local storage of ERP credentials.
- **State**: No persistent business data is stored within the Office environment; all state is anchored in Odoo.

## 3. Integration Delivery (BOM 10.4)

Office connectivity is mapped to the **Productivity Layer** of the Integration Capability Matrix:
- **Primary Data Path**: ODATA v4 for bulk analytical sync.
- **Primary Context Path**: Contextual JSON-RPC for sidebar retrieval.
- **Primary Auth Path**: Entra ID OIDC tokens.

---

*Last updated: 2026-04-11*
