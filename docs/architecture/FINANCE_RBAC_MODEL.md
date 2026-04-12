# Finance RBAC and Persona Model — Pulser for Odoo

Pulser for Odoo implements a 5-layer Finance RBAC architecture to ensure that every agentic interaction is governed by institutional authority, data visibility boundaries, and role-specific action permissions.

---

## 1. The 5-Layer Security Model (BOM 15)

The security posture for any Pulser session is determined by the intersection of these five layers:

### Layer 1: Business Role (Identity)
Mapping of the **Microsoft Entra ID** identity to one of the 12 canonical Pulser Finance Groups.
- *Examples*: `pulser_ap_manager`, `pulser_finance_head`.

### Layer 2: Approval Authority (Bands)
Allocation of an **Approval Band** defining the user's signature threshold for financial transactions.
- **Band A**: Preparer only; no approval rights.
- **Band B**: Reviewer; validation only.
- **Band C**: Active Approver (e.g., < 50k AP).
- **Band D**: Final Sign-off (e.g., Close/Tax).
- **Band E**: Platform Admin (Config only).

### Layer 3: Evidence Visibility (Scopes)
Governance of the **retrieval boundary** for grounded agent responses.
- **Self / Assigned**: Only records assigned to the specific user.
- **Team / Dept**: All records within the user's business unit.
- **Entity / Company**: All records within a specific Odoo company.
- **Consolidated**: Cross-entity visibility for group-level reporting.
- **Audit Read-Only**: Immutable visibility for external auditors.

### Layer 4: Agent Action Scope (Permissions)
Granular control over **what the agent can do** on behalf of the user.
- **summarize**, **draft**, **classify**, **reconcile**, **route**, **prepare_entry**, **approve**, **schedule_payment**, **generate_pack**, **publish**, **change_config**.

### Layer 5: UI Cockpit Assignment
Defining the **Primary Surface** and active widget set for the persona.
- **Cockpit First**: High-density dashboards (e.g., Close Cockpit).
- **Queue First**: Work-item streams (e.g., AP Queue).
- **Brief First**: Exec-level summaries.

## 2. Canonical Role Matrix

| Role | Primary Surface | Permissions | Band |
|------|-----------------|-------------|------|
| **Finance Head** | Close Cockpit | summarize, route, approve, publish | D |
| **Finance Manager** | Reconciliation Cockpit | summarize, draft, reconcile, approve | C |
| **AP Manager** | Source-to-Pay Cockpit | summarize, draft, route, approve | C |
| **AP Processor** | AP Work Queue | summarize, draft, reconcile, route | A |
| **Tax Lead** | BIR Compliance Cockpit | summarize, validate, generate_pack | D |
| **Treasury Manager** | Treasury Cockpit | summarize, schedule_payment | C |
| **Billing Lead** | Order-to-Cash Cockpit | summarize, draft, reconcile | C |
| **PPM Controller** | Profitability Cockpit | summarize, draft, reconcile | C |
| **Expense Reviewer** | Exception Cockpit | summarize, route | B |
| **Exec Viewer** | Finance Brief | summarize, publish | A |
| **Auditor** | Evidence Vault | summarize (read-only) | A |
| **Finance Admin** | Finance Ops Admin | change_config, audit | E |

## 3. Implementation Logic

- **RBAC Authority**: Pulser use **Entra ID Group Claims** as the primary source of truth for Role assignment.
- **Threshold Mapping**: Approval Bands and entity limits are stored in the **Tenant Admin Plane (TMP)** to allow tenant-specific overrides.
- **Agent Interceptor**: Every `tool_call` from the agent is intercepted by the **Action Guard**, which validates the request against the user's **Agent Action Scope**.

---

*Last updated: 2026-04-11*
