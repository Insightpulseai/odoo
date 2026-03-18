# Contract — SAP Joule + SAP Concur + Odoo on Azure

> Hard runtime decisions for the Azure-native integration surface.
> Spec bundle: `spec/sap-joule-concur-odoo-azure/`
> SSOT artifact: `ssot/integrations/sap-joule-concur-odoo-azure.yaml`

---

## System Boundaries

| Decision | Value |
|----------|-------|
| Canonical runtime | Azure (Container Apps, Front Door, Key Vault, Monitor) |
| Canonical ERP system of record | Odoo CE 19 on Azure Container Apps |
| Canonical travel/expense source | SAP Concur |
| Canonical copilot surface (SAP side) | SAP Joule |
| Canonical identity plane | Microsoft Entra ID (where supported) |
| Secret storage | Azure Key Vault (`kv-ipai-dev`) only |

## Hard Rules

1. No direct SAP Joule → Odoo write path without Azure mediation
2. No direct Concur → Odoo posting without idempotent contract + audit trail
3. No secrets in Odoo DB, `ir.config_parameter`, or Git-tracked config
4. No unclassified integration paths (must be one of: `event_orchestration`, `master_data_sync`, `document_exchange`, `identity_access`)
5. All inbound financial documents enter Odoo as drafts, never as posted entries
6. Concur report ID is the canonical idempotency key for expense sync
7. Every sync operation must produce a structured audit log entry

## Integration Flows

### Flow 1: Concur Expense → Odoo Draft

```
SAP Concur (approved report)
    → Azure integration plane (API mediation, auth, logging)
    → Odoo API (create draft account.move)
    → Odoo approval workflow (review → approve → post)
```

- **Type**: `document_exchange`
- **Idempotency key**: `concur_report_id` → `account.move.ref`
- **Write mode**: draft_only
- **Audit**: required

### Flow 2: Joule → Odoo Query

```
SAP Joule (query request)
    → Azure integration plane (auth, rate limit, logging)
    → Odoo bounded read API (project, budget, approval status)
    → Response to Joule
```

- **Type**: `event_orchestration`
- **Write mode**: read_only
- **Audit**: required

### Flow 3: Joule → Odoo Bounded Action

```
SAP Joule (action request)
    → Azure integration plane (auth, validation, logging)
    → Odoo bounded action API (request approval, query status)
    → Response to Joule
```

- **Type**: `event_orchestration`
- **Write mode**: bounded_write (approval requests only)
- **Audit**: required

### Flow 4: Entra SSO → Concur

```
User login
    → Microsoft Entra ID (SAML/OIDC)
    → SAP Concur (federated auth)
```

- **Type**: `identity_access`
- **Audit**: required

### Flow 5: Entra SSO → Odoo

```
User login
    → Microsoft Entra ID (OIDC)
    → Odoo (ipai_auth_oidc or Keycloak federation)
```

- **Type**: `identity_access`
- **Audit**: required

## Data Ownership

| Data Domain | System of Record | Sync Direction |
|-------------|------------------|----------------|
| Expense reports | SAP Concur | Concur → Odoo (draft import) |
| Travel bookings | SAP Concur | Concur → Odoo (reference) |
| Journal entries | Odoo | Odoo-internal (no outbound) |
| Employee master | Odoo | Odoo → Concur (reference mapping) |
| Vendor master | Odoo | Odoo → Concur (reference mapping) |
| Project/budget | Odoo | Odoo → Joule (read-only) |
| User identity | Microsoft Entra ID | Entra → all systems |
| Secrets | Azure Key Vault | Key Vault → all services |

## Failure Handling

| Failure Mode | Response |
|--------------|----------|
| Concur API unavailable | Queue request → dead-letter → retry with exponential backoff |
| Odoo API unavailable | Queue request → dead-letter → retry with exponential backoff |
| Duplicate sync attempt | Idempotency check → skip if already exists and posted |
| Invalid mapping (unknown employee/vendor) | Log error → dead-letter → manual resolution |
| Posting fails in Odoo | Document stays in draft → error logged → alert |

## Compliance

- All sync audit logs retained for 7 years (BIR compliance requirement)
- Reconciliation reports generated monthly (Concur reports vs. Odoo postings)
- No PII in structured logs (employee IDs only, not names/emails in log payloads)
