# Tasks — SAP Joule + SAP Concur + Odoo on Azure

> Task breakdown for the Azure-native integration surface.
> Each task is independently committable.

---

## T1 — Spec and Contract

- [x] **T1.1** Create spec bundle `spec/sap-joule-concur-odoo-azure/`
- [x] **T1.2** Create `docs/contracts/SAP_JOULE_CONCUR_ODOO_AZURE_CONTRACT.md`
- [x] **T1.3** Create `ssot/integrations/sap-joule-concur-odoo-azure.yaml`
- [ ] **T1.4** Register contract in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`

## T2 — Identity

- [ ] **T2.1** Define Entra SSO contract for Concur (SAML/OIDC config)
- [ ] **T2.2** Define service-to-service auth contract (managed identity → Key Vault → API tokens)
- [ ] **T2.3** Define Odoo role mapping from Entra groups
  - Finance Director, Finance Manager, Accountant, Traveler, Project Manager
- [ ] **T2.4** Document Entra app registrations required

## T3 — Canonical Data Model

- [ ] **T3.1** Employee/person mapping (Concur employee → Odoo `hr.employee` / `res.partner`)
- [ ] **T3.2** Vendor mapping (Concur vendor → Odoo `res.partner` supplier)
- [ ] **T3.3** Project/cost center mapping (Concur cost center → Odoo `account.analytic.account`)
- [ ] **T3.4** Tax/currency mapping (Concur tax codes → Odoo fiscal positions; currencies)
- [ ] **T3.5** Document/status model (Concur report states → Odoo `account.move` states)

## T4 — Odoo Integration Surfaces

- [ ] **T4.1** Expense import endpoint/service
  - Concur approved report → Odoo `account.move` (draft)
  - Idempotency key: `concur_report_id` → `account.move.ref`
- [ ] **T4.2** Draft posting workflow
  - Draft → review → approval → posted
  - Odoo-native `account.move` state machine
- [ ] **T4.3** Reconciliation model
  - Concur reports vs. Odoo posted entries
  - Mismatch detection and reporting
- [ ] **T4.4** Audit/event log model
  - Sync operation log (source, target, key, status, timestamp)
  - Error details for failed operations

## T5 — Azure Integration Surfaces

- [ ] **T5.1** Secret resolution (Key Vault bindings for Concur API credentials)
- [ ] **T5.2** Retry/dead-letter (queue for failed sync operations with replay)
- [ ] **T5.3** Structured logs (Application Insights with correlation IDs)
- [ ] **T5.4** Health endpoints (per-flow health check returning last sync status)

## T6 — Joule Interaction Model

- [ ] **T6.1** Read-only use cases
  - Project summary, expense status, budget balance, pending approvals
- [ ] **T6.2** Bounded write use cases
  - Approval request trigger, status query
- [ ] **T6.3** Approval boundaries
  - Which actions Joule may trigger vs. which require human approval
- [ ] **T6.4** Prompt/context contract
  - Which Odoo data surfaces are exposed to Joule queries
  - Data classification (public, internal, restricted)

## T7 — Validation

- [ ] **T7.1** Sandbox smoke tests (Concur test tenant → Odoo dev)
- [ ] **T7.2** Idempotency tests (re-sync same report → no duplicate)
- [ ] **T7.3** Reconciliation tests (known data set → expected Odoo state)
- [ ] **T7.4** Failure injection tests (simulate Concur API down → dead-letter → replay)
- [ ] **T7.5** Security tests (unauthorized access, token expiry, rate limiting)

---

## Status Key

- [x] = complete (shipped in this spec creation pass)
- [ ] = pending (requires implementation work)

## Dependency Map

```
T1 (spec/contract) ──► T2 (identity) + T3 (data model)
T2 + T3 ──► T4 (Odoo surfaces) + T5 (Azure surfaces)
T4 + T5 ──► T6 (Joule interaction)
T4 + T5 + T6 ──► T7 (validation)
```
