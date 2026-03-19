# Identity & Secrets

> Identity posture and secret management boundaries for the InsightPulse AI platform.
> **SSOT**: `ssot/governance/operating-model.yaml` § `devsecops_control_planes`
> **Ref**: [Enable DevSecOps with Azure and GitHub](https://learn.microsoft.com/en-us/devops/devsecops/enable-devsecops-azure-github)

---

## 1. Identity Plane

### Microsoft Entra ID

Entra ID is the identity plane for platform resources and human access.

| Principle | Rule |
|-----------|------|
| Named accounts | All admins use named accounts — no shared or generic accounts |
| MFA | Required for all platform admin accounts |
| Global Admin | Zero day-to-day usage — break-glass only |
| Managed identities | Preferred over service principals for service-to-service auth |
| Workload identity federation | OIDC for AzDo ↔ ARM (no long-lived secrets in service connections) |

### Current IdP Posture

- **Current**: Keycloak (`ipai-auth-dev`) — transitional
- **Target**: Microsoft Entra ID
- **Migration gates**: OIDC/SAML parity, group/role mapping, service-account replacement, break-glass admin, user provisioning, per-app cutover
- **Status**: Not started — do not delete `ipai-auth-dev` until all gates pass

### Azure RBAC

- Resource access governed by Azure RBAC role assignments
- Least-privilege principle: assign minimum role required
- Custom roles only when built-in roles are insufficient
- Role assignments tracked in IaC (`infra/`), not portal-only

## 2. Unified Sign-In Model

### Doctrine

Use **one identity plane** (Microsoft Entra) and **separate authorization planes** per app.

```
auth.insightpulseai.com
  → Azure Front Door
  → Unified branded sign-in (Entra Company Branding)
  → Microsoft Entra ID

Per-app surfaces (each with its own Entra app registration):
  erp.insightpulseai.com      → Odoo
  ops.insightpulseai.com      → Ops Console
  plane.insightpulseai.com    → Plane
  mcp.insightpulseai.com      → MCP / agent plane
  superset.insightpulseai.com → BI (Superset)
```

### Branded Sign-In

- Tenant-wide branded sign-in page via Entra Company Branding (logo, background, colors)
- Custom domain (`insightpulseai.com`) added to the Entra tenant
- `auth.insightpulseai.com` as the canonical auth/launcher entrypoint via Front Door

### Unified App View

- Each app published as an Enterprise Application in Entra
- Users/groups assigned per app — assigned apps appear in **My Apps** portal
- Alternative: custom launcher shell at `auth.insightpulseai.com` that reads token claims and renders accessible apps (UI layer only — auth stays in Entra)

## 3. App Registration Boundary Rules

### One Registration Per Major Surface

Each major app surface has its own Entra app registration / enterprise app:

| Surface | App Registration | Purpose |
|---------|-----------------|---------|
| Odoo ERP | `ipai-odoo` | ERP, finance, HR, CRM |
| Ops Console | `ipai-ops` | Platform operations |
| Plane | `ipai-plane` | Project management |
| MCP / Agent Plane | `ipai-mcp` | Agent coordination |
| Superset | `ipai-superset` | BI / analytics |
| n8n | `ipai-n8n` | Workflow automation |

**Never** collapse unrelated surfaces into one shared app registration. Separate registrations allow independent SSO configuration, assignment, app roles, consent, and audit.

### Group-Based Assignment

- Use Entra security groups for app access assignment
- Map group membership to app-side roles via token claims (`groups` or `roles` claim)
- No ad hoc per-user assignment in steady state — groups are the unit of access

### App Roles

- Define app roles on each registration (e.g., `Admin`, `User`, `ReadOnly`)
- Assign roles to groups, not individual users
- Each app checks role claims in its authorization layer

## 4. Authorization and Tenant Isolation

### Authentication vs Authorization

| Concern | Plane | Tool |
|---------|-------|------|
| Authentication (who are you?) | Entra ID | OIDC/SAML sign-in |
| Authorization (what can you do?) | Per-app | App roles, claims, backend logic |
| Tenant isolation (whose data?) | Per-app data layer | DB isolation, row filtering |

"Logged in" does NOT mean "can access everything." Each app independently validates:
1. Token is valid and from the correct Entra tenant
2. User has the required app role for the requested operation
3. Request is scoped to the correct tenant/company context

### Tenant vs User Identity

For multi-company or multi-workspace scenarios:

- **Tenant identity**: which company/workspace the request belongs to
- **User identity**: what role the user has within that tenant
- Authorization must consider both dimensions
- Odoo handles this natively via `res.company` and `ir.rule` (multi-company)

### Data Isolation

A unified sign-in page does NOT provide data isolation. Isolation is enforced in the data layer:

| Pattern | When | Isolation Level |
|---------|------|-----------------|
| Separate database per tenant | Highest isolation requirement | Strong |
| Separate schema per tenant | Moderate isolation, shared infra | Medium |
| Shared DB with row-level filtering | Cost-optimized, lower isolation | Acceptable with strict RLS |

Current model: single-tenant (one Odoo instance, one database per environment).
Multi-tenant isolation patterns are documented here for future scaling.

---

## 5. Secrets Authority

### Azure Key Vault (`kv-ipai-dev`)

Key Vault is the canonical secret store. All runtime secrets flow through Key Vault.

```
Managed Identity → Key Vault → Environment Variables → Application
```

### Secret Storage Rules

| Rule | Detail |
|------|--------|
| No secrets in code | Zero secrets in git-tracked files |
| No secrets in pipelines | AzDo variable groups reference Key Vault, not inline values |
| No secrets in images | Runtime injection only, never baked into container images |
| No secrets in logs | Secrets never echoed in CI logs, debug output, or evidence docs |
| GitHub Actions | Uses GitHub Secrets (scoped per repo/environment) |

### Key Vault Inventory

| Vault | Resource Group | Purpose |
|-------|---------------|---------|
| `kv-ipai-dev` | `rg-ipai-shared-dev` | Dev secrets |
| `kv-ipai-staging` | `rg-ipai-shared-staging` | Staging secrets |
| `kv-ipai-prod` | `rg-ipai-shared-prod` | Prod secrets |
| `ipai-odoo-dev-kv` | `rg-ipai-dev` | Odoo-specific secrets |

### Secret Rotation

| Secret | Rotation | Owner |
|--------|----------|-------|
| Zoho SMTP credentials | Quarterly | platform-lead |
| PostgreSQL passwords | Quarterly | platform-lead |
| API keys (OpenAI, etc.) | On compromise or quarterly | platform-lead |
| ACR credentials | Managed identity (no rotation needed) | N/A |

### Handling Missing Secrets

When a secret is required and missing, state exactly:
1. Which env var or Key Vault key is needed
2. Which vault it belongs in
3. Continue executing everything that does not require it

Never ask users to paste secret values. Never hardcode fallback values.

## 6. Service-to-Service Auth

| Pattern | When | How |
|---------|------|-----|
| Managed identity | ACA ↔ Key Vault, ACA ↔ PG, ACA ↔ ACR | System-assigned managed identity |
| Workload identity federation | AzDo ↔ ARM | OIDC token exchange (no long-lived secrets) |
| API key via Key Vault | External services (OpenAI, Zoho) | Key Vault → env var at container start |
| OAuth2 bearer token | Agent ↔ Odoo (FastAPI) | Token issued by IdP, validated by endpoint |

---

## Cross-References

- [devsecops_operating_model.md](devsecops_operating_model.md) — parent DevSecOps model
- [runtime_security.md](runtime_security.md) — runtime/container controls
- [platform_delivery_contract.md](platform_delivery_contract.md) — per-app registration delivery rule
- [AZURE_SECRET_AUDIT.md](azure/AZURE_SECRET_AUDIT.md) — secret audit findings

---

*Last updated: 2026-03-17*
