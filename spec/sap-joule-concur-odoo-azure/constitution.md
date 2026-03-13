# Constitution — SAP Joule + SAP Concur + Odoo on Azure

> Immutable architectural rules for the integration between SAP Joule,
> SAP Concur, Odoo CE on Azure Container Apps, and the Azure runtime plane.

---

## Canonical Integration Posture

| System | Role | Owner |
|--------|------|-------|
| SAP Joule | User-facing AI/coprocessor surface in SAP/Microsoft ecosystem | SAP |
| SAP Concur | Expense/travel/invoice source system | SAP |
| Odoo on Azure | ERP, accounting, project, approval, posting, and operational control surface | InsightPulseAI |
| Azure | Runtime, identity, AI, integration, security, and observability backbone | Microsoft |

---

## Core Rules

### Rule 1: Azure-Native Only

All runtime, identity, secrets, observability, and AI execution must be
Azure-native. No direct point-to-point connections that bypass Azure
infrastructure.

- Runtime: Azure Container Apps (`cae-ipai-dev`)
- Identity: Microsoft Entra ID (SSO, service-to-service auth)
- Secrets: Azure Key Vault (`kv-ipai-dev`) + managed identity
- Observability: Azure Monitor / Application Insights
- AI: Azure AI Foundry (`aifoundry-ipai-dev`)

### Rule 2: Odoo is System of Record for ERP-Operational State

Odoo owns accounting entries, journal postings, project records, approval
workflows, and operational control state. Odoo is not the conversational
runtime — it is the transactional backend.

No external system may directly write to Odoo's database. All inbound data
flows through Azure-mediated APIs with idempotent contracts.

### Rule 3: Joule is Not Embedded into Odoo

SAP Joule remains an external SAP-side copilot/agent surface. It interacts
with Odoo-operational context only via controlled, Azure-mediated APIs.

- Joule may read Odoo operational context (bounded queries)
- Joule may trigger bounded actions (approval requests, status queries)
- Joule may NOT directly write to Odoo models or bypass approval workflows
- No Odoo-native chatbot replaces Joule on the SAP side

### Rule 4: Concur is Source of Truth for Expense/Travel Events

SAP Concur owns expense reports, travel bookings, and invoice data until
those records are explicitly posted/synchronized into Odoo.

- Concur data enters Odoo as **draft documents** (never direct postings)
- Draft-to-posted transition requires Odoo-side approval workflow
- Concur report ID is the canonical idempotency key for sync operations
- No Concur data is stored in Supabase or any non-Odoo system as SoR

### Rule 5: No Direct Point-to-Point Sprawl

Every integration path must be classified as exactly one of:

| Classification | Description |
|----------------|-------------|
| `event_orchestration` | Async event-driven flow with queue/retry semantics |
| `master_data_sync` | Periodic or triggered reference data synchronization |
| `document_exchange` | Structured document transfer with idempotency |
| `identity_access` | SSO, token exchange, role/permission mapping |

Unclassified integration paths are prohibited.

### Rule 6: Microsoft Entra ID is the Canonical Identity Plane

Where supported, Entra ID provides SSO and service-to-service authentication.
SAP Concur documents Entra SSO support for Travel and Expense.

- User authentication: Entra ID → SAML/OIDC → Concur, Odoo
- Service authentication: Entra managed identity → Key Vault → API tokens
- Role mapping: Entra groups → Odoo roles (finance, approver, traveler, PM)

### Rule 7: Secrets Never Stored in Odoo DB

All secrets (API keys, tokens, credentials) are resolved at runtime via:

- Azure Key Vault (`kv-ipai-dev`)
- Managed identity bindings
- Environment variable injection

Secrets must never appear in:

- Odoo `ir.config_parameter` or `ir_config_parameter` table
- Git-tracked configuration files
- CI/CD logs or debug output

### Rule 8: Every Sync Path Requires Audit Trail

Every data flow between systems must produce:

- Structured log entry (Azure Monitor / Application Insights)
- Idempotency key for replay safety
- Error queue entry on failure (dead-letter with replay capability)
- Evidence-grade output for compliance review

### Rule 9: Draft-First Posting

No external system may create posted (finalized) accounting entries in Odoo.
All inbound financial documents enter as drafts. The posting workflow is
Odoo-internal and requires explicit approval.

```
Concur → Azure mediation → Odoo draft document → Odoo approval → Posted entry
```

### Rule 10: Repo-First

All integration interfaces must be described in machine-readable SSOT
artifacts committed to the repository. Console-only or dashboard-only
configurations are prohibited per the platform SSOT rules.
