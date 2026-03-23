# Plan — Entra Identity Migration

## Phase 0: Foundation (Pre-Migration)

**Dependencies**: None
**Gate**: All items complete before any app cutover

- Configure break-glass emergency access account in Entra ID
- Store break-glass credentials securely (Key Vault + physical)
- Create Conditional Access policy CA-001 (MFA for admins)
- Create Conditional Access policy CA-003 (block high-risk sign-ins)
- Enroll all admin accounts in MFA
- Create Entra security groups: `SG-IPAI-Admin`, `SG-IPAI-Finance-Manager`, `SG-IPAI-Finance-User`, `SG-IPAI-Project-Manager`, `SG-IPAI-Project-User`, `SG-IPAI-BIR-Approver`
- Assign admin users to `SG-IPAI-Admin`
- Evidence: export CA policy config, screenshot MFA enrollment, break-glass test

## Phase 1: Odoo ERP (P1 — Highest Priority)

**Dependencies**: Phase 0 complete
**Gate**: Login flow + group sync + rollback tested

- Register `IPAI Odoo ERP` as enterprise app in Entra admin center
- Configure OIDC: redirect URI, logout URL, token claims (groups, email, preferred_username)
- Store client ID + client secret in Azure Key Vault (`kv-ipai-dev`)
- Develop `ipai_auth_oidc` module:
  - OIDC Authorization Code Flow with PKCE
  - Token validation (RS256, issuer, audience)
  - User provisioning (create on first login, email-based matching)
  - Group-to-role sync (Entra group claim → Odoo `group_ids`)
  - Session management (token refresh, logout)
- Install `ipai_auth_oidc` on `odoo_dev` database
- Test: admin login via Entra → Odoo session created → correct groups assigned
- Test: finance user login → correct finance groups assigned
- Test: rollback to Keycloak (disable OIDC, re-enable Keycloak client)
- Create CA-002 (MFA for finance operations on Odoo)
- Evidence: login flow screenshots, group mapping validation, rollback test

## Phase 2: Plane + Superset (P2)

**Dependencies**: Phase 0 complete (independent of Phase 1)
**Gate**: Login flow + role mapping tested per app

### Plane

- Register `IPAI Plane` as enterprise app in Entra
- Configure OIDC redirect URI: `https://plane.insightpulseai.com/`
- Configure Plane OIDC settings (Plane supports OIDC natively)
- Map Entra groups to Plane workspace roles
- Test: login via Entra → workspace access with correct role
- Disable Keycloak OIDC client for Plane

### Superset

- Register `IPAI Superset` as enterprise app in Entra
- Configure OIDC redirect URI: `https://superset.insightpulseai.com/oauth-authorized/entra`
- Configure Flask-OIDC / Authlib in Superset config
- Map Entra groups to Superset roles (Admin, Alpha, Gamma)
- Test: login via Entra → dashboard access with correct role
- Disable Keycloak OIDC client for Superset

## Phase 3: n8n + Shelf + CRM (P3)

**Dependencies**: Phase 0 complete
**Gate**: Login flow tested per app

- Register each app as enterprise app in Entra
- Configure OIDC per app:
  - n8n: `https://n8n.insightpulseai.com/rest/oauth2-credential/callback`
  - Shelf: `https://shelf.insightpulseai.com/auth/callback`
  - CRM: `https://crm.insightpulseai.com/auth/callback`
- Test login flow per app
- Disable Keycloak OIDC clients per app

## Phase 4: Keycloak Cleanup

**Dependencies**: None — Keycloak was never operationalized, no apps depend on it
**Gate**: Confirmation that no app references Keycloak endpoints

- Export Keycloak realm config as backup artifact (for reference only)
- Scale `ipai-auth-dev` container app to 0 replicas
- Delete `ipai-auth-dev` container app (no observation period needed — nothing depends on it)
- Remove `auth.insightpulseai.com` from `infra/dns/subdomain-registry.yaml`
- Run `scripts/dns/generate-dns-artifacts.sh` and commit
- Update `~/.claude/rules/infrastructure.md` runtime truth table
- Add Keycloak to deprecated items in `CLAUDE.md`
- Evidence: deletion confirmation

## Phase 5: Entra Agent ID (Future — Preview-Gated)

**Dependencies**: Frontier program access confirmed, M365 Copilot licensed
**Gate**: Preview features available in tenant

- Enable Frontier program in M365 admin center
- Register agent identity blueprints for Agent Factory agents
- Map existing agent passports to Entra Agent ID concepts
- Configure access packages for agent scopes (time-bound)
- Configure Conditional Access for agent workloads
- Test: agent authentication via Entra Agent ID
- Test: agent risk detection and auto-remediation
- Document agent identity governance model

## Evaluation Gates (per phase)

| Phase | Gate |
|-------|------|
| Phase 0 | Break-glass tested, CA policies active, all admins MFA-enrolled |
| Phase 1 | Odoo login + group sync + rollback validated |
| Phase 2 | Plane + Superset login + role mapping validated |
| Phase 3 | n8n + Shelf + CRM login validated |
| Phase 4 | 14-day zero-Keycloak-session observation, backup exported |
| Phase 5 | Agent identity lifecycle tested (Preview scope) |

## Rollback Strategy

Since Keycloak was never operationalized, rollback means reverting to pre-SSO state (not to Keycloak):
- Odoo: disable `ipai_auth_oidc` module, revert to basic Odoo login
- Plane/Superset/n8n: disable OIDC config, revert to local auth
- Rollback window: immediate (config change + restart)
- No dual-IdP complexity — each app goes from no-SSO directly to Entra
