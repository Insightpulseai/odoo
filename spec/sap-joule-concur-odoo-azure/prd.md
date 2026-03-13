# PRD — SAP Joule + SAP Concur + Odoo on Azure

> Product requirements for the Azure-native integration surface connecting
> SAP Joule, SAP Concur, and Odoo CE on Azure Container Apps.

---

## 1. Product Name

**SAP Joule + SAP Concur + Odoo on Azure**

## 2. Problem Statement

Enterprises operating across SAP and Odoo need:

- Joule-driven conversational workflows for user-facing operations
- Concur-driven expense/travel data flowing into Odoo for accounting
- Odoo-managed finance, project, and approval workflows
- Azure-native identity, security, and AI as the integration backbone

Without a structured integration contract, these become fragile custom
point-to-point connections with no audit trail, no idempotency, and no
clear system-of-record boundaries.

## 3. External Product Facts

- SAP describes Joule as an AI assistant spanning SAP and non-SAP workflows
  with documented bidirectional interaction with Microsoft 365 Copilot.
- SAP Concur documents broad integration availability and SAP-native
  integration patterns for expense, travel, and invoice data.
- Microsoft documents SAP Concur Travel and Expense integration with
  Entra ID for SSO.

---

## 4. Epics

### Epic A — Identity and Access

| Requirement | Detail |
|-------------|--------|
| Entra SSO for SAP Concur | SAML/OIDC federation between Entra ID and Concur tenant |
| Shared identity posture | Azure services and Odoo share Entra-backed authentication |
| Role mapping | Finance, approvers, travelers, project managers mapped from Entra groups to Odoo roles |
| Service-to-service auth | Managed identity → Key Vault → API tokens for system integrations |

### Epic B — Expense Ingestion

| Requirement | Detail |
|-------------|--------|
| Ingest approved Concur expenses | Approved expense reports flow from Concur → Azure → Odoo as draft documents |
| Employee mapping | Concur employee IDs mapped to Odoo `res.partner` / `hr.employee` records |
| Vendor mapping | Concur vendors mapped to Odoo `res.partner` (supplier) records |
| Cost center mapping | Concur cost centers mapped to Odoo analytic accounts |
| Tax/currency mapping | Concur tax codes and currencies mapped to Odoo fiscal positions and currency records |
| Draft-first posting | All ingested documents enter Odoo as drafts; posting requires Odoo-side approval |
| Idempotency | Concur report ID serves as deduplication key; re-sync is safe |

### Epic C — Joule-Assisted Operations

| Requirement | Detail |
|-------------|--------|
| Expose Odoo context to Joule | Controlled read-only APIs expose operational state (project status, budget, approvals) |
| Bounded action patterns | Joule may trigger specific bounded actions (e.g., request approval, query status) |
| No unmanaged writeback | Joule cannot directly modify Odoo models or bypass approval workflows |
| Prompt/context contract | Define exactly which Odoo data surfaces are available to Joule queries |

### Epic D — Azure-Native Integration Plane

| Requirement | Detail |
|-------------|--------|
| Orchestration | Azure-native event/message handling for all sync flows |
| API mediation | All external API calls routed through Azure infrastructure |
| Secret resolution | Key Vault + managed identity for all credential access |
| Structured logging | Every sync attempt logged to Azure Monitor / Application Insights |
| Retry and dead-letter | Failed operations queued for replay with exponential backoff |

### Epic E — Reconciliation and Audit

| Requirement | Detail |
|-------------|--------|
| Idempotent sync keys | Every document exchange uses a deterministic deduplication key |
| Posting traceability | Every Odoo journal entry traceable to source Concur report |
| Error queues | Failed sync operations stored in dead-letter queue with full payload |
| Replay capability | Any failed sync can be replayed from dead-letter without data loss |
| Evidence-grade logs | Audit logs sufficient for BIR compliance review and financial audit |

---

## 5. Non-Goals

- Replacing Joule with an Odoo-native chatbot
- Replacing Concur as the travel/expense user experience
- Storing secrets in Odoo database or configuration
- Direct unmanaged SAP-to-Odoo writes bypassing Azure mediation
- Building a custom Concur replacement in Odoo
- Real-time streaming (batch/event-driven is sufficient)

---

## 6. User Roles

| Role | System Access | Key Workflows |
|------|---------------|---------------|
| Finance Director | Odoo (approval), Concur (oversight) | Approve posted entries, review reconciliation |
| Finance Manager | Odoo (posting), Concur (review) | Review draft expenses, approve postings |
| Accountant | Odoo (data entry), Concur (view) | Reconcile drafts, process journal entries |
| Traveler/Employee | Concur (submit), Joule (query) | Submit expenses, query approval status via Joule |
| Project Manager | Odoo (project), Joule (query) | Query project budget status, review cost allocations |

---

## 7. Success Criteria

1. Approved Concur expense reports appear as draft documents in Odoo within SLA
2. Draft-to-posted workflow in Odoo produces traceable journal entries
3. Joule can query Odoo operational context via bounded read APIs
4. All sync operations are idempotent and replay-safe
5. Zero secrets stored in Odoo DB or Git-tracked files
6. Every sync attempt has a structured audit log entry
7. Entra SSO works for Concur users mapped to Odoo roles
