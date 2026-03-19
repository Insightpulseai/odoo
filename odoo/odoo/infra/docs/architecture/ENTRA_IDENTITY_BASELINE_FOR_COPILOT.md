# Entra Identity Baseline for Copilot

> Version: 1.1.0
> Last updated: 2026-03-14
> Source: Azure Entra + Foundry portal screenshots (2026-03-14)
> Parent: `agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md` (C-30)

## Current Tenant State

| Property | Value |
|----------|-------|
| Tenant name | Default Directory |
| Primary domain | `ceoinsightpulseai.onmicrosoft.com` |
| License tier | Microsoft Entra ID Free |
| Users | 2 |
| Groups | 12 |
| App registrations | 3 |
| Devices | 0 |
| Entra Connect | Not enabled (cloud-only) |
| Hybrid identity | None |

## Identity Maturity Assessment

**Current level: Startup / Explore** — usable for controlled prototype, not yet hardened for broad production.

| Dimension | State | Risk |
|-----------|-------|------|
| MFA enforcement | Not fully enforced (100+ sign-ins lacking MFA in last 7 days) | HIGH |
| Auth methods policy | Legacy — needs migration to converged policy | MEDIUM |
| App registrations | 3 exist — viable for service principal model | OK |
| Conditional Access | Available but not configured | MEDIUM |
| Audit logging | Basic (Free tier) | LOW for now |
| Cloud-only posture | Yes (no hybrid) | OK — simplifies auth model |

## Immediate Gaps

### GAP-1: MFA Not Enforced (HIGH)

The Entra portal shows MFA enforcement is required but not complete. 100+ sign-ins in the last 7 days lacked MFA.

**Impact on copilot:** Any admin accessing Azure portal, Foundry, or Odoo admin without MFA creates a credential-theft risk that could compromise the copilot's backend.

**Required action:**
- Enable Security Defaults or create Conditional Access policy requiring MFA for all users
- Priority: before Stage 2 promotion

### GAP-2: Legacy Authentication Methods Policy (MEDIUM)

The portal warns about migrating from legacy MFA/SSPR policy to the converged Authentication methods policy.

**Impact on copilot:** Legacy policy fragmentation makes it harder to enforce consistent auth controls across human and service identities.

**Required action:**
- Migrate to converged Authentication methods policy
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

### Stage 1 (Current) — Explore

- [x] Entra tenant exists and is usable
- [x] App registrations available for service principal model
- [x] Cloud-only posture (no hybrid complexity)
- [x] Service principal exists (`sp-ipai-azdevops`, Contributor role)
- [x] Azure AI Search connected to Foundry project (`srch-ipai-dev`)
- [ ] MFA enforcement — **not yet complete** (acceptable for prototype, must fix before Stage 2)

### Stage 2 — Expand

- [ ] MFA enforced for all admin/privileged users
- [ ] Converged Authentication methods policy active
- [ ] Foundry access via managed identity or `sp-ipai-azdevops` (not API key)
- [x] Service principal registered for CI/CD pipeline — **`sp-ipai-azdevops` confirmed**
- [ ] Conditional Access policy for admin operations
- [ ] Audit logging sufficient for identity troubleshooting

### Stage 3 — Hardened

- [ ] CAE for workload identities enabled
- [ ] Conditional Access for protected actions (copilot mode changes)
- [ ] API keys fully retired from all environments
- [ ] Identity monitoring/alerting in place
- [ ] Formal identity governance review completed
