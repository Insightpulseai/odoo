# Identity Target State

> Version: 1.0.0
> Last updated: 2026-03-14
> Canonical repo: `infra`

## Purpose

Define the target identity architecture for InsightPulseAI across all offerings.

## Current State

- Entra tenant: `ceoinsightpulseai.onmicrosoft.com` (Free tier)
- Users: 2
- App registrations: 3
- Service principal: `sp-ipai-azdevops` (Contributor)
- MFA: Not fully enforced
- Conditional Access: Not configured

## Target State

### Human Identity

| Role | Identity Provider | MFA | Conditional Access |
|------|------------------|-----|-------------------|
| Platform admin | Entra ID | Required | Admin policy |
| Odoo admin | Entra ID + Odoo session | Required | Admin policy |
| Odoo user | Odoo local auth | Optional | N/A |
| Docs visitor | Anonymous | N/A | N/A |

### Workload Identity

| Workload | Identity Type | Auth Method | Scope |
|----------|--------------|-------------|-------|
| Odoo Container App | Managed identity | DefaultAzureCredential | Foundry project, Key Vault |
| CI/CD pipeline | Service principal (`sp-ipai-azdevops`) | Client credentials | Foundry, Azure resources |
| Docs Express proxy | App registration | Client credentials | Foundry threads/runs API |
| n8n automations | Service principal or managed identity | Client credentials | Odoo API, Supabase |

### Auth Flow Target

```
Human → Entra MFA → Azure Portal / Foundry
Odoo User → Odoo Session → Copilot → Managed Identity → Foundry
Docs Widget → Anonymous → Express Proxy → Service Principal → Foundry
CI/CD → Service Principal → Foundry / Azure Resources
```

## Migration Path

### Phase 1 (Current) — API Key Bootstrap
- API key for Foundry access in non-prod
- MFA not enforced
- Legacy auth methods policy

### Phase 2 — Managed Identity
- Managed identity for Odoo Container App
- Service principal for docs proxy
- MFA enforced for all admins
- Converged auth methods policy
- Conditional Access for admin operations

### Phase 3 — Hardened
- All API keys retired
- Private networking where required
- CAE for workload identities
- Identity governance review complete
- Formal SLA for identity operations

## App Registration Inventory

| App Name | Client ID | Purpose | Status |
|----------|-----------|---------|--------|
| (to be inventoried) | — | — | Pending |
| (to be inventoried) | — | — | Pending |
| (to be inventoried) | — | — | Pending |

See `docs/operations/ENTRA_APP_REGISTRATIONS.md` for detailed inventory.

## Dependencies

- `ENTRA_IDENTITY_BASELINE_FOR_COPILOT.md` — current gap analysis
- `FOUNDRY_ODOO_AUTH_AND_ENDPOINT_POLICY.md` — auth preference order
- `COPILOT_RUNTIME_STAGE_POLICY.md` — stage-gated requirements
