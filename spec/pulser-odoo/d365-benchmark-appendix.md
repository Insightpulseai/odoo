# Appendix — D365 Autonomous Agents Benchmark

**Source:** Dynamics 365 Autonomous Agents product documentation  
**Purpose:** Validate Pulser's Finance PPM scope against Microsoft's reference implementations

## Mapping

| D365 Agent | Domain | Pulser Equivalent | Status |
|---|---|---|---|
| Financial Reconciliation Agent | Period close data prep and cleansing | `bir-close-workflow` | Spec'd → **Implement** |
| Account Reconciliation Agent | Subledger ↔ GL matching and clearing | `payment-reconcile-workflow` | Spec'd → **Implement** |
| Time and Expense Agent | Time entry, expense tracking, approvals | `expense-liquidation-workflow` | Spec'd → **Implement** |
| Customer Intent Agent | Discover intents from conversations | Pulser skill router (simpler) | Enhance |
| Customer Knowledge Mgmt Agent | Keep KB articles current | Pulser grounding from Odoo Documents | Implement |
| Sales Qualification Agent | Lead scoring, outreach | Not in scope (finance-first) | N/A |
| Sales Order Agent (BC) | Order intake | Not in scope | N/A |
| Supplier Communications Agent | PO confirmation with vendors | Not in scope (no procurement lane) | Future |
| Case Management Agent | Case lifecycle automation | Not in scope | N/A |
| Scheduling Operations Agent | Field service dispatch | Not in scope | N/A |

## Three directly applicable to IPAI Finance PPM

### 1. Financial Reconciliation Agent → `bir-close-workflow`

D365 description: "Prepares and cleanses data sets to simplify the most labor-intensive part
of period close." This is the exact scope of Pulser's Record-to-Report close sequence.

IPAI implementation: MAF `SequentialWorkflow` — Record → Reconcile → Close → Report → Tax.
Human-in-the-loop gate at Close (CKVC must approve period lock before posting).

### 2. Account Reconciliation Agent → `payment-reconcile-workflow` (SC-PH-27)

D365 description: "Automates matching and clearing transactions between subledgers and GL."
IPAI scope: bank statement lines ↔ `account.move.line`, AR ageing, intercompany clearing
(Dataverse ↔ TBWA\SMP Invoice No. 0001 WHT matching).

IPAI implementation: MAF `HandoffWorkflow` with `FileCheckpointStorage` — durable, spans
multiple sessions, resumes when new bank statement data arrives.

### 3. Time and Expense Agent → `expense-liquidation-workflow` (SC-PH-07/08/09)

D365 description: "Autonomously manages time entry, expense tracking, and approval workflows."
IPAI scope: HR timesheet completeness alerts, expense report submission, cash advance
liquidation (Odoo HR module + `hr.expense` + `hr.timesheet`).

IPAI implementation: MAF `SequentialWorkflow` — expense submission requires
`approval_mode="always_require"` on any tool that posts expense entries to Odoo.

## Architecture patterns adopted (not domain specifics)

D365 uses a "constellation of agents" pattern — specialist agents per domain, orchestrated
by an orchestrator. Pulser already follows this:

```
Pulser orchestrator (copilot_gateway.py)
  ├── bir-close-workflow      (Financial Reconciliation Agent analog)
  ├── payment-reconcile-workflow  (Account Reconciliation Agent analog)
  └── expense-liquidation-workflow (Time and Expense Agent analog)
```

D365 guardrails: "maker-defined instructions, knowledge, and actions" → Pulser's
constitution (`agents/system/pulser.system.md`) + policy layer + `approval_mode`.

## Validation

The D365 benchmark confirms that Pulser's three finance-critical lanes (close, reconciliation,
expense/liquidation) are the correct starting scope. These match the lanes Microsoft's own
ERP finance agents target. The implementation gap is execution, not design.
