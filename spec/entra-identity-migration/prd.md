# PRD — Entra Identity Migration

## Objective

Migrate the IPAI platform identity provider from self-hosted Keycloak (`ipai-auth-dev`) to Microsoft Entra ID, achieving enterprise-grade identity governance with Conditional Access, MFA enforcement, workload identities, and a future path to Entra Agent ID for AI agent governance.

## Non-Goals

- Replacing Odoo as the transactional authority (Odoo remains relying party)
- Implementing Entra Agent ID in this migration (Preview-gated, separate workstream)
- Migrating to Entra External ID / CIAM (all users are internal/workforce)
- Adopting Azure AD B2C (deprecated naming, not applicable)

## Current State

| Component | Status |
|-----------|--------|
| Keycloak (`ipai-auth-dev`) | Deployed but **never operationalized** — no apps authenticating through it |
| App authentication | Basic Odoo login / no SSO for most apps |
| Break-glass admin | Presence established, CA enforcement not evidenced |
| MFA | Methods available (Authenticator, OATH, TAP), enrollment not enforced |
| Conditional Access | Not yet configured for platform apps |
| App registrations in Entra | Not started |
| Managed identities | Active for ACA containers (independent of IdP) |

## Target State

| Component | Target |
|-----------|--------|
| Human identity | Entra ID with OIDC, MFA enforced via CA |
| Admin identity | Entra ID with MFA + Conditional Access + break-glass |
| Service identity | Azure Managed Identities (system-assigned on ACA) |
| Agent identity | Entra Agent ID (when GA/Frontier access confirmed) |
| Keycloak | Decommissioned after all gates pass |

## Apps to Migrate

| App | FQDN | Auth Type | Priority | Complexity |
|-----|------|-----------|----------|------------|
| Odoo ERP | `erp.insightpulseai.com` | OIDC (custom `ipai_auth_oidc` module) | P1 | High — custom module, group/role sync |
| Plane | `plane.insightpulseai.com` | OIDC (native) | P2 | Low — standard OIDC config |
| Superset | `superset.insightpulseai.com` | OIDC (Flask-OIDC) | P2 | Low — standard OIDC config |
| n8n | `n8n.insightpulseai.com` | OIDC (community) | P3 | Low — external auth config |
| Shelf | `shelf.insightpulseai.com` | OIDC | P3 | Low — standard web app |
| CRM | `crm.insightpulseai.com` | OIDC | P3 | Low — standard web app |

## Odoo OIDC Integration (P1 — Highest Complexity)

### Module: `ipai_auth_oidc`

Required capabilities:
- OIDC Authorization Code Flow with PKCE
- Token validation (RS256, issuer check, audience check)
- User provisioning: create Odoo user on first login if not exists
- User matching: email-based lookup against `res.users`
- Group/role sync: map Entra ID group claims to Odoo `group_ids`
- Session management: Odoo session tied to Entra token lifecycle
- Logout: back-channel or front-channel logout to Entra

### Entra App Registration for Odoo

| Field | Value |
|-------|-------|
| Name | `IPAI Odoo ERP` |
| Supported account types | Single tenant (this org only) |
| Redirect URI | `https://erp.insightpulseai.com/auth/oidc/callback` |
| Logout URL | `https://erp.insightpulseai.com/web/session/logout` |
| API permissions | `openid`, `profile`, `email`, `User.Read` |
| Token configuration | Groups claim (security groups), `preferred_username` |
| Client secret | Stored in Azure Key Vault (`kv-ipai-dev`) |

### Group-to-Role Mapping

| Entra Group | Odoo Group | Description |
|-------------|------------|-------------|
| `SG-IPAI-Admin` | `base.group_system` | System administrators |
| `SG-IPAI-Finance-Manager` | `account.group_account_manager` | Finance managers |
| `SG-IPAI-Finance-User` | `account.group_account_invoice` | Finance users |
| `SG-IPAI-Project-Manager` | `project.group_project_manager` | Project managers |
| `SG-IPAI-Project-User` | `project.group_project_user` | Project users |
| `SG-IPAI-BIR-Approver` | `group_ipai_bir_approver` | BIR tax approvers |

## Conditional Access Policies

### CA-001: MFA for All Admins

| Field | Value |
|-------|-------|
| Users | `SG-IPAI-Admin` group |
| Target resources | All cloud apps |
| Grant | Require MFA |
| Session | Sign-in frequency: 12 hours |

### CA-002: MFA for Finance Operations

| Field | Value |
|-------|-------|
| Users | `SG-IPAI-Finance-Manager`, `SG-IPAI-BIR-Approver` |
| Target resources | Odoo ERP app |
| Grant | Require MFA |

### CA-003: Block High-Risk Sign-Ins

| Field | Value |
|-------|-------|
| Users | All users |
| Conditions | Sign-in risk: High |
| Grant | Block access |

### CA-004: Require Compliant Device for Admin

| Field | Value |
|-------|-------|
| Users | `SG-IPAI-Admin` |
| Target resources | All cloud apps |
| Grant | Require MFA + compliant device |

## Entra Agent ID (Future — Preview-Gated)

When Frontier program access is confirmed:

| Entra Agent ID Concept | IPAI Mapping |
|------------------------|-------------|
| Agent Identity Blueprint | Agent Factory passport template |
| Agent Identity (instance) | Individual agent runtime identity |
| Owner + Sponsor | Passport `owner` field |
| Access Packages | Agent scopes + policies (time-bound) |
| Conditional Access for agents | Stage gate controls, risk-based |
| ID Protection for agents | Risk detection, anomaly response |
| Agent Registry | Centralized metadata, MCP/A2A discovery |
| Network controls | API/MCP filtering, prompt injection blocking |

## Success Criteria

1. All 6 apps authenticate via Entra ID OIDC
2. Keycloak `ipai-auth-dev` decommissioned
3. CA policies CA-001 through CA-004 active and evidenced
4. Break-glass account tested and secured
5. All admin accounts MFA-enrolled
6. Group/role mapping validated per app
7. Zero authentication outages during migration (dual-IdP rollback path)
8. Evidence artifacts for all gates in `docs/evidence/`

## Risks

| Risk | Mitigation |
|------|-----------|
| Odoo OIDC module bugs during cutover | Rollback to basic Odoo login (no Keycloak dependency) |
| Group claim size exceeds token limit | Use group filtering or app roles instead of groups |
| Entra Agent ID not GA in time | Managed identities as fallback for agent workloads |
| Frontier program access not available | Agent ID workstream deferred, no blocker for human identity |
| MFA enrollment friction for users | TAP for initial enrollment, Authenticator push for ongoing |
