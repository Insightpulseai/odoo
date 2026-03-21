# Entra Identity Baseline for Copilot

> Version: 2.0.0
> Last updated: 2026-03-21
> Source: Azure Entra portal screenshots (2026-03-21)
> Parent: `agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md` (C-30)

## Current Tenant State

| Property | Value |
|----------|-------|
| Tenant name | Default Directory |
| Primary domain | `insightpulseai.com` |
| Onmicrosoft domain | `ceoinsightpulseai.onmicrosoft.com` |
| License tier | Microsoft Entra ID Free |
| Users | 4 (Emergency Admin, Platform Admin, Jake Tolentino, 1 guest) |
| Groups | 12 |
| App registrations | 4 |
| Devices | 0 |
| Entra Connect | Not enabled (cloud-only) |
| Hybrid identity | None — Cloud Sync not required (no on-prem AD) |

### Authentication Methods (Enabled)

| Method | Status |
|--------|--------|
| Microsoft Authenticator | Enabled (all users) |
| Passkey / FIDO2 | Enabled (all users) |
| Temporary Access Pass | Enabled (all users) |
| Software OATH tokens | Enabled (all users) |
| Email OTP | Enabled (all users) |

### Authentication Methods (Disabled)

SMS, Voice call, Hardware OATH tokens, Certificate-based authentication, QR code — all disabled.

## Identity Maturity Assessment

**Current level: Established / Partly Hardened** — strong auth method selection, not yet fully hardened.

| Dimension | State | Risk |
|-----------|-------|------|
| Auth methods | Strong — Authenticator/passkey/TAP/OATH enabled, SMS/voice disabled | OK |
| Auth methods policy | Legacy — converged policy migration outstanding | MEDIUM |
| Break-glass accounts | Emergency Admin exists — need to confirm 2nd account + documentation | MEDIUM |
| App registrations | 4 exist — viable for service principal model | OK |
| Conditional Access | Available but not configured | MEDIUM |
| Audit logging | Basic (Free tier) | LOW for now |
| Cloud-only posture | Yes (no hybrid) | OK — simplifies auth model |
| Key Vault integration | Exists but RBAC enforcement not verified | MEDIUM |

## Gaps (Remaining)

### GAP-1: Converged Authentication Methods Policy (MEDIUM)

The portal warns about migrating from legacy MFA/SSPR policy to the converged Authentication methods policy.

**Impact on copilot:** Legacy policy fragmentation makes it harder to enforce consistent auth controls across human and service identities.

**Required action:**
- Migrate to converged Authentication methods policy
- Priority: before Stage 2 promotion

### GAP-2: Break-Glass Account Documentation (MEDIUM)

Microsoft recommends two cloud-only emergency access accounts permanently assigned Global Administrator. One (Emergency Admin) is visible. Second must be confirmed, role-assigned, and documented.

**Required action:**
- Confirm both accounts exist and are permanently assigned Global Administrator
- Document both in `access_model.yaml` under `emergency_admin` role
- Neither account should be used for daily operations
- Priority: before Stage 2 promotion

### GAP-3: Key Vault RBAC Enforcement (MEDIUM)

Azure Key Vault must use Azure RBAC as the default authorization model. Current authorization model (access policy vs RBAC) not verified.

**Required action:**
- Verify all vaults use Azure RBAC authorization
- Migrate any access-policy vaults to RBAC
- Priority: before Stage 2 promotion

## Identity Model for Copilot

### Human Identity (Entra users)

| Role | Auth Method | MFA | Access Scope |
|------|------------|-----|-------------|
| Platform admin | Entra user + password | Required | Azure portal, Foundry, Odoo admin |
| Odoo user | Odoo session (local auth) | Optional (Odoo-side) | Copilot chat via Discuss / HTTP API |
| Docs visitor | Anonymous | N/A | Copilot chat via docs widget (rate-limited) |

### Workload Identity (service principals / managed identities)

| Identity | Type | Role | Access Scope |
|----------|------|------|-------------|
| Odoo Container App | Managed identity | (to be assigned) | Foundry project endpoint |
| `sp-ipai-azdevops` | **Service principal (confirmed)** | Contributor (inherited at subscription) | Foundry project, CI/CD |
| Docs Express proxy | App identity (future) | (to be assigned) | Foundry threads/runs API |

> `sp-ipai-azdevops` was confirmed in Foundry project admin (2026-03-14). This is the machine identity for CI/CD and can serve as the Stage 2 auth path for automated deployments and Foundry API access.

### Service-to-Service Auth

| Path | Current Auth | Target Auth |
|------|-------------|-------------|
| Docs proxy → Foundry | API key (env var) | Managed identity (Stage 2) |
| Docs proxy → Odoo | `X-Copilot-Service-Key` header | Same (sufficient for service-to-service) |
| Odoo → Foundry | API key + IMDS fallback | Managed identity only (Stage 2) |
| Discuss bot → Foundry | Via `foundry_service.py` (same as above) | Same as above |

## Monitoring Surfaces Available Now

The current tenant already exposes these monitoring and diagnostics surfaces:

| Surface | Purpose |
|---------|---------|
| Sign-in logs | Track who authenticated, when, how, from where |
| Audit logs | Identity object changes (user/group/app modifications) |
| Provisioning logs | App provisioning activity |
| Health | Tenant health status |
| Log Analytics | Query-based investigation of identity events |
| Diagnostic settings | Forward identity logs to external sinks |
| Workbooks | Pre-built and custom identity dashboards |
| Usage & insights | Authentication method adoption, app usage patterns |
| Bulk operation results (Preview) | Status of bulk identity operations |

These should be treated as the canonical Entra monitoring surfaces for the copilot identity/control-plane baseline. As maturity increases (Stage 2+), diagnostic forwarding should be enabled to capture identity events alongside runtime telemetry.

## Relevant Preview Features

These Entra preview features are visible in the tenant and relevant to future stages:

| Feature | Relevance | When to Enable |
|---------|-----------|---------------|
| Continuous Access Evaluation (CAE) for Workload Identities | Revoke tokens in near-real-time if service principal is compromised | Stage 3 |
| Conditional Access for protected actions | Gate destructive operations (e.g. `full_access` mode) on stronger auth | Stage 2 |
| Enhanced audit logs | Better visibility into identity-related events | Stage 2 |
| Scenario Monitoring | Track authentication patterns and anomalies | Stage 3 |

## Stage-Gated Identity Requirements

### Stage 1 (Current) — Established

- [x] Entra tenant exists and is usable
- [x] App registrations available for service principal model (4 registered)
- [x] Cloud-only posture (no hybrid complexity)
- [x] Service principal exists (`sp-ipai-azdevops`, Contributor role)
- [x] Azure AI Search connected to Foundry project (`srch-ipai-dev`)
- [x] Strong auth methods enabled (Authenticator, passkey, TAP, Software OATH)
- [x] Weak auth methods disabled (SMS, voice)
- [x] Emergency Admin account exists
- [ ] Converged auth methods policy migration — **outstanding**
- [ ] Second break-glass account confirmed and documented
- [ ] Key Vault RBAC authorization model verified

### Stage 2 — Expand

- [x] Strong auth methods enforced for all admin/privileged users
- [ ] Converged Authentication methods policy active (migrated from legacy)
- [ ] Foundry access via managed identity or `sp-ipai-azdevops` (not API key)
- [x] Service principal registered for CI/CD pipeline — **`sp-ipai-azdevops` confirmed**
- [ ] Conditional Access policy for admin operations
- [ ] Audit logging sufficient for identity troubleshooting
- [ ] Two break-glass accounts documented and tested
- [ ] Key Vault RBAC enforced across all vaults

### Stage 3 — Hardened

- [ ] CAE for workload identities enabled
- [ ] Conditional Access for protected actions (copilot mode changes)
- [ ] API keys fully retired from all environments
- [ ] Identity monitoring/alerting in place
- [ ] Formal identity governance review completed
