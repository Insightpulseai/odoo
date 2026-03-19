# Plan — SAP Joule + SAP Concur + Odoo on Azure

> Implementation plan for the Azure-native integration surface.

---

## Architecture

```
SAP Joule / SAP apps
        │
        │ conversational + workflow requests
        ▼
Azure integration plane
(Entra ID, API mediation, orchestration, AI/runtime, observability)
        │
        ├── SAP Concur connectors / ingestion
        └── Odoo on Azure bounded APIs + posting workflows
```

---

## Phase 1 — Contract and Topology

### Deliverables

| Artifact | Purpose |
|----------|---------|
| `docs/contracts/SAP_JOULE_CONCUR_ODOO_AZURE_CONTRACT.md` | Hard runtime decisions and boundary rules |
| `ssot/integrations/sap-joule-concur-odoo-azure.yaml` | Machine-readable integration catalog |
| Bounded context map | Which system owns which domain |
| Identity model | Entra SSO + service-to-service auth topology |

### Bounded Context Map

| Domain | System of Record | Consumers |
|--------|------------------|-----------|
| Expense reports, travel bookings | SAP Concur | Odoo (via draft import) |
| Journal entries, posted accounting | Odoo | Reporting, Superset, BIR compliance |
| Project/budget/analytic | Odoo | Joule (read-only), Superset |
| Employee/person master | Odoo (`hr.employee`) | Concur (mapping), Joule (context) |
| Vendor master | Odoo (`res.partner`) | Concur (mapping) |
| User identity, roles, SSO | Microsoft Entra ID | All systems |
| Secrets, certificates | Azure Key Vault | All services |
| Conversational UX | SAP Joule | Odoo (bounded API) |

### Integration Catalog

| Flow ID | Type | Source | Target | Mediation | Write Mode |
|---------|------|--------|--------|-----------|------------|
| `concur_expense_to_odoo_draft` | `document_exchange` | Concur | Odoo | Azure | draft_only |
| `joule_query_odoo_context` | `event_orchestration` | Joule | Odoo | Azure | read_only |
| `joule_bounded_action` | `event_orchestration` | Joule | Odoo | Azure | bounded_write |
| `entra_sso_concur` | `identity_access` | Azure | Concur | none | — |
| `entra_sso_odoo` | `identity_access` | Azure | Odoo | none | — |
| `employee_master_sync` | `master_data_sync` | Odoo | Concur | Azure | reference |
| `vendor_master_sync` | `master_data_sync` | Odoo | Concur | Azure | reference |

---

## Phase 2 — Read-Only Foundation

### Concur Inbound Read Models

- Define Concur API client (approved expense reports endpoint)
- Map Concur expense report schema to Odoo draft document model
- Implement employee/vendor/cost-center lookup tables
- Handle currency conversion and tax code mapping

### Odoo Reference Data Exposure

- Expose bounded read APIs for:
  - Project status and budget summary
  - Analytic account balances
  - Approval workflow state
  - Employee/vendor reference data
- APIs are read-only, authenticated via Entra service principal

### Azure Wiring

- Key Vault secrets for Concur API credentials
- Managed identity for Odoo service-to-service calls
- Application Insights instrumentation for all API calls
- Dead-letter queue (Azure Service Bus or Storage Queue)

### Observability

- Structured log schema for sync operations
- Correlation ID propagation across Concur → Azure → Odoo
- Health endpoints for each integration flow
- Alert rules for failure rate thresholds

---

## Phase 3 — Controlled Finance Sync

### Draft Expense Documents

- Concur approved reports → Odoo `account.move` (draft state)
- Fields mapped:
  - `partner_id` ← Concur employee mapping
  - `journal_id` ← expense journal
  - `line_ids` ← expense line items (account, amount, tax, analytic)
  - `ref` ← Concur report ID (idempotency key)

### Approval and Reconciliation

- Draft documents enter Odoo approval workflow
- Finance manager reviews, adjusts if needed, approves
- Approved documents posted to journal
- Reconciliation report: Concur reports vs. Odoo posted entries

### Posting and Rollback

- Post operation is Odoo-internal (`account.move.action_post`)
- Failed postings logged with full error context
- Rollback = revert to draft state (Odoo native `button_draft`)

### Idempotency

- Sync key: `concur_report_id` stored in `account.move.ref`
- Before creating draft: check if `ref` already exists
- If exists and draft: update. If exists and posted: skip. If missing: create.

---

## Phase 4 — Joule-Facing API Surface

### Read/Query Endpoints

| Endpoint | Returns | Auth |
|----------|---------|------|
| `/api/v1/projects/summary` | Project list with budget/actual/variance | Entra service principal |
| `/api/v1/expenses/status/{report_id}` | Concur report processing status in Odoo | Entra service principal |
| `/api/v1/approvals/pending` | Pending approval items for a user | Entra user token |
| `/api/v1/budget/analytic/{account_id}` | Analytic account balance summary | Entra service principal |

### Bounded Action APIs

| Endpoint | Action | Guard |
|----------|--------|-------|
| `/api/v1/approvals/{id}/request` | Request approval for a draft document | Must be document owner |
| `/api/v1/expenses/{id}/status` | Query processing status | Read-only |

### Audit

- Every API request logged with: timestamp, caller, endpoint, parameters, response code
- Joule interaction logs correlated with Odoo audit trail
- No PII in log payloads (employee IDs only, not names/emails)

---

## Phase 5 — Production Hardening

### Alerting

- Sync failure rate > 5% → alert
- Dead-letter queue depth > 10 → alert
- API latency p95 > 5s → alert
- SSO failure → immediate alert

### DR and Replay

- Dead-letter messages retained for 30 days
- Replay endpoint for failed sync operations
- Idempotency ensures replay safety

### Performance

- Load test: 1000 expense reports/hour sync throughput
- API response time: p95 < 2s for read endpoints
- Batch sync: daily reconciliation run completes < 30 minutes

### Security Review

- Entra token validation on all endpoints
- No direct database access from external systems
- Rate limiting on all public-facing APIs
- OWASP top-10 review for custom API endpoints

### Evidence Pack

- Sync operation audit logs
- Reconciliation reports (Concur vs. Odoo)
- API access logs with correlation IDs
- Security scan results

---

## Delivery Policy

- Repo-first: all interfaces described in machine-readable SSOT
- Every sync path must declare: source-of-record, keying strategy,
  retry policy, and evidence output
- No console-only or dashboard-only configurations
- Contract doc and SSOT YAML must exist before implementation begins
