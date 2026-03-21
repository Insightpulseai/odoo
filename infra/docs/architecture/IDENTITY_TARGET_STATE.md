# Identity Target State

> Version: 2.0.0
> Last updated: 2026-03-21
> Canonical repo: `infra`

## Purpose

Define the target identity architecture for InsightPulseAI across all offerings.

## Current State (as of 2026-03-21)

- Entra tenant: `ceoinsightpulseai.onmicrosoft.com` (Free tier)
- Primary domain: `insightpulseai.com`
- Users: 4 (Emergency Admin, Platform Admin, Jake Tolentino, 1 guest)
- Groups: 12
- App registrations: 4
- Devices: 0
- Service principal: `sp-ipai-azdevops` (Contributor)
- MFA methods enabled: Authenticator, Passkey/FIDO2, TAP, Software OATH, Email OTP
- MFA methods disabled: SMS, Voice, Hardware OATH, Certificate-based, QR code
- Hybrid identity: None (cloud-native)
- Migration alert: converged Authentication Methods policy migration outstanding

## Target State

### Control Planes (Non-Optional)

| Plane | Authority | Authorization Model |
|-------|-----------|-------------------|
| Identity | Microsoft Entra ID | OIDC/SAML sign-in |
| Secrets / Keys / Certificates | Azure Key Vault | Azure RBAC |
| Resource access | Azure RBAC | Least-privilege role assignments |

### Break-Glass Accounts

Two cloud-only emergency access accounts, permanently assigned Global Administrator, not used for daily operations. Both accounts must be documented and tested quarterly.

### Authentication Methods Baseline

| Method | Target Status |
|--------|-------------|
| Microsoft Authenticator | **Required** |
| Passkey / FIDO2 | **Required** |
| Temporary Access Pass | **Required** |
| Software OATH tokens | **Required** |
| Email OTP | Allowed (if justified) |
| SMS | **Disabled** (weak channel) |
| Voice call | **Disabled** (weak channel) |

Legacy MFA/SSPR policy remnants must be fully migrated to the converged Authentication Methods model.

### Hybrid Identity

Cloud Sync is **conditional** — only required when an on-prem AD forest exists. Current posture is cloud-native. Do not model Cloud Sync as required baseline.

### Human Identity

| Role | Identity Provider | MFA | Conditional Access |
|------|------------------|-----|-------------------|
| Platform admin | Entra ID | Required (Authenticator/passkey) | Admin policy |
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
