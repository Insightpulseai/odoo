# Tasks — Entra Identity Migration

> Spec bundle: `spec/entra-identity-migration/`
> Status: Active
> Created: 2026-03-22
> Last updated: 2026-03-30

---

## Phase 0 — Foundation (Pre-Migration)

- [ ] P0 | Human | Create break-glass emergency access account in Entra ID
- [ ] P0 | Human | Store break-glass credentials (Key Vault + physical safe)
- [ ] P0 | Human | Test break-glass account login (must bypass CA)
- [ ] P0 | Human | Create CA-001: MFA for all admins (`SG-IPAI-Admin`)
- [ ] P0 | Human | Create CA-003: Block high-risk sign-ins (all users)
- [ ] P0 | Human | Enroll all admin accounts in MFA (Authenticator or FIDO2)
- [ ] P0 | Human | Create Entra security groups: `SG-IPAI-Admin`, `SG-IPAI-Finance-Manager`, `SG-IPAI-Finance-User`, `SG-IPAI-Project-Manager`, `SG-IPAI-Project-User`, `SG-IPAI-BIR-Approver`
- [ ] P0 | Human | Assign admin users to `SG-IPAI-Admin`
- [ ] P0 | Agent | Produce evidence artifact: CA policy export + MFA enrollment proof + break-glass test

---

## Phase 1 — Odoo ERP (P1)

### App Registration

- [x] P1 | Human | Register `IPAI Odoo ERP` enterprise app in Entra admin center — **DONE**: app `07bd9669-1eca-4d93-8880-fd3abb87f812` registered as `InsightPulseAI Odoo Login` (2026-03-23)
- [ ] P1 | Human | Configure OIDC: redirect URI `https://erp.insightpulseai.com/auth_oauth/signin` — **NEXT**: redirect URI must be added to app registration
- [ ] P1 | Human | Configure token claims: groups, email, preferred_username
- [ ] P1 | Human | Store client secret in Azure Key Vault (`kv-ipai-dev`) as `entra-odoo-login-client-secret`

### Module Development

- [x] P1 | Agent | Create `addons/ipai/ipai_auth_oidc/__manifest__.py` (depends: `base`, `auth_oauth`, `mail`) — **DONE**: v19.0.1.0.0 shipped
- [x] P1 | Agent | Implement OIDC Authorization Code Flow — **DONE**: uses `auth_oauth` core with `id_token_code` flow
- [x] P1 | Agent | Implement user provisioning (JIT create on first login, email-based matching) — **DONE**: `res_users.py` `_jit_provision_entra_user`
- [x] P1 | Agent | Add `ir.config_parameter` settings: `ipai.auth.oidc.entra.client_id`, `ipai.auth.oidc.entra.tenant_id`, `ipai.auth.oidc.entra.enabled` — **DONE**: seeded in `data/entra_provider.xml`
- [x] P1 | Agent | Create login button on Odoo `/web/login` page — **DONE**: `auth.oauth.provider` record with `body="Sign in with Microsoft"`, `css_class="fa fa-fw fa-windows"`
- [x] P1 | Agent | Create `security/ir.model.access.csv` — **DONE**: read for users, full CRUD for admins
- [x] P1 | Agent | Create settings UI in General Settings — **DONE**: `views/res_config_settings_views.xml`
- [x] P1 | Agent | Write smoke tests — **DONE**: `tests/test_auth_oidc.py` (6 tests: install, provider, config params, placeholder, settings fields, JIT method)
- [ ] P1 | Agent | Implement RS256 token validation (issuer, audience, expiry) — **NOT STARTED**: currently relies on `auth_oauth` built-in validation
- [ ] P1 | Agent | Implement group-to-role sync (Entra group claim → Odoo `group_ids`) — **NOT STARTED**: JIT creates base user only, no group sync from claims
- [ ] P1 | Agent | Implement session management (token refresh, back-channel logout) — **NOT STARTED**
- [ ] P1 | Agent | Write integration tests: `test_oidc_token_validation.py`, `test_oidc_user_provisioning.py`, `test_oidc_group_sync.py` — **NOT STARTED**: only smoke tests exist

### Runtime Activation

- [ ] P1 | Human | Set tenant ID to `402de71a-...` (replace `common` placeholder) via Settings UI or `ir.config_parameter`
- [ ] P1 | Human | Set client ID to `07bd9669-...` (replace `ENTRA_CLIENT_ID_PLACEHOLDER`) via Settings UI or env var `ENTRA_ODOO_CLIENT_ID`
- [ ] P1 | Human | Run `action_apply_entra_provider` from Settings to update the OAuth provider endpoints with real tenant
- [ ] P1 | Human | Create client secret in Entra portal and store in Key Vault `kv-ipai-dev`

### Validation

- [ ] P1 | Human | Install `ipai_auth_oidc` on `odoo_dev`
- [ ] P1 | Human | Test: admin login via Entra → Odoo session → correct groups
- [ ] P1 | Human | Test: finance user login → correct finance groups
- [ ] P1 | Human | Test: rollback (disable OIDC provider, revert to basic login)
- [ ] P1 | Human | Create CA-002: MFA for finance operations on Odoo
- [ ] P1 | Agent | Produce evidence artifact: login screenshots, group mapping, rollback test

---

## Phase 2 — Plane + Superset (P2)

### Plane

- [ ] P2 | Human | Register `IPAI Plane` enterprise app in Entra
- [ ] P2 | Human | Configure OIDC redirect URI for Plane
- [ ] P2 | Human | Configure Plane instance OIDC settings (God Mode > Authentication)
- [ ] P2 | Human | Map Entra groups to Plane workspace roles
- [ ] P2 | Human | Test: login via Entra → workspace access with correct role
- [ ] P2 | Human | Disable Keycloak OIDC client for Plane

### Superset

- [ ] P2 | Human | Register `IPAI Superset` enterprise app in Entra
- [ ] P2 | Human | Configure OIDC redirect URI for Superset
- [ ] P2 | Agent | Update Superset config: Flask-OIDC / Authlib provider settings
- [ ] P2 | Human | Map Entra groups to Superset roles (Admin, Alpha, Gamma)
- [ ] P2 | Human | Test: login via Entra → dashboard access with correct role
- [ ] P2 | Human | Disable Keycloak OIDC client for Superset

### Validation

- [ ] P2 | Agent | Produce evidence artifact: Plane + Superset login flow proof

---

## Phase 3 — n8n + Shelf + CRM (P3)

- [ ] P3 | Human | Register `IPAI n8n` enterprise app in Entra
- [ ] P3 | Human | Register `IPAI Shelf` enterprise app in Entra
- [ ] P3 | Human | Register `IPAI CRM` enterprise app in Entra
- [ ] P3 | Human | Configure OIDC redirect URIs per app
- [ ] P3 | Human | Test login flow per app
- [ ] P3 | Human | Disable Keycloak OIDC clients per app
- [ ] P3 | Agent | Produce evidence artifact: login flow proof per app

---

## Phase 4 — Keycloak Cleanup (Never Operationalized — No Migration Gates Needed)

- [ ] P1 | Agent | Export Keycloak realm config as backup artifact (reference only)
- [ ] P1 | Human | Scale `ipai-auth-dev` to 0 replicas
- [ ] P1 | Human | Delete `ipai-auth-dev` container app
- [ ] P1 | Agent | Remove `auth.insightpulseai.com` from `infra/dns/subdomain-registry.yaml`
- [ ] P1 | Agent | Run `scripts/dns/generate-dns-artifacts.sh` and commit
- [ ] P1 | Agent | Update `~/.claude/rules/infrastructure.md` runtime truth table
- [ ] P1 | Agent | Update deprecated items table in `CLAUDE.md` (add Keycloak)
- [ ] P1 | Agent | Produce evidence artifact: deletion confirmation

---

## Phase 5 — Entra Agent ID (Future — Preview-Gated)

- [ ] P2 | Human | Verify Frontier program access in M365 admin center
- [ ] P2 | Human | Enable Entra Agent ID preview in tenant
- [ ] P2 | Agent | Register agent identity blueprints for: Advisory, Ops, Actions agents
- [ ] P2 | Agent | Map agent passports to Entra Agent ID instances
- [ ] P2 | Agent | Configure access packages for agent scopes (time-bound)
- [ ] P2 | Agent | Configure Conditional Access for agent workloads
- [ ] P2 | Agent | Test: agent auth via Entra Agent ID
- [ ] P2 | Agent | Test: agent risk detection and auto-remediation
- [ ] P2 | Agent | Document agent identity governance model
- [ ] P2 | Agent | Update `spec/ipai-odoo-copilot-azure/constitution.md` with Entra Agent ID binding

---

## Cross-Cutting

- [ ] P0 | Agent | Create `ssot/identity/entra_ca_policies.yaml` — all CA policies
- [ ] P1 | Agent | Create `ssot/identity/entra_group_mapping.yaml` — Entra group → app role mapping
- [ ] P1 | Agent | Update `spec/plane-unified-docs/tasks.md` Phase 3 Keycloak tasks to reference this spec
- [ ] P1 | Agent | Update `spec/ipai-odoo-copilot-azure/constitution.md` authority model with Entra reference
- [x] P0 | Agent | Create `ssot/identity/entra_rbac_roles.yaml` — 7 RBAC role definitions
- [x] P0 | Agent | Create `ssot/identity/schema_sync_map.yaml` — cross-app data sync architecture
- [x] P0 | Agent | Create `ssot/entra/app_registrations.azure_native.yaml` — canonical app registration SSOT (4 registrations)
- [x] P0 | Agent | Create `ssot/identity/entra_app_registrations.yaml` — pointer file to paired SSOT
- [ ] P1 | Human | Create `ssot/identity/entra_branding.yaml` design assets (6 images per spec)
- [ ] P1 | Human | Apply Entra company branding in admin center (Entra ID → Custom Branding)
- [ ] P1 | Human | Configure Home Realm Discovery (`whr=insightpulseai.com`) in all app redirect URIs

---

## Next 5 Actionable Tasks (Priority Queue)

> These are the highest-impact tasks that can be executed now, given the current state.
> Prerequisites: Entra tenant bootstrapped, app registration exists, `ipai_auth_oidc` module deployed.

| # | Task | Type | Runbook |
|---|------|------|---------|
| 1 | **Verify and configure redirect URI** on app `07bd9669`: add `https://erp.insightpulseai.com/auth_oauth/signin` | Human (Azure CLI) | `docs/runbooks/entra-activation-next-steps.md` Step 1-2 |
| 2 | **Create client secret** for app `07bd9669` and store in Key Vault `kv-ipai-dev` as `entra-odoo-login-client-secret` | Human (Azure CLI) | `docs/runbooks/entra-activation-next-steps.md` Step 3 |
| 3 | **Set real tenant ID and client ID** on `ipai_auth_oidc` provider config (replace `common` → `402de71a`, replace `ENTRA_CLIENT_ID_PLACEHOLDER` → `07bd9669`) | Human (Odoo Settings UI or CLI) | `docs/runbooks/entra-activation-next-steps.md` Step 4 |
| 4 | **Configure optional token claims** (groups, email, preferred_username) on the app registration | Human (Azure CLI) | `docs/runbooks/entra-activation-next-steps.md` Step 5 |
| 5 | **Test end-to-end login flow** on `odoo_dev`: click "Sign in with Microsoft" → Entra login → JIT provisioning → Odoo session | Human (Browser) | `docs/runbooks/entra-activation-next-steps.md` Step 6 |

---

## Summary

| Phase | Total | Done | Remaining |
|-------|-------|------|-----------|
| Phase 0: Foundation | 9 | 0 | 9 |
| Phase 1: Odoo ERP | 26 | 8 | 18 |
| Phase 2: Plane + Superset | 13 | 0 | 13 |
| Phase 3: n8n + Shelf + CRM | 7 | 0 | 7 |
| Phase 4: Keycloak Decommission | 8 | 0 | 8 |
| Phase 5: Entra Agent ID | 10 | 0 | 10 |
| Cross-Cutting | 11 | 4 | 7 |
| **Total** | **84** | **12** | **72** |

---

## Dependency Map

```
Phase 0 (Foundation)
  ├── Phase 1 (Odoo) ──────┐
  ├── Phase 2 (Plane/SS) ──┤
  └── Phase 3 (n8n/etc.) ──┤
                            ▼
                    Phase 4 (Keycloak Decommission)

Phase 5 (Agent ID) ── independent, gated by Frontier program
```

**Critical path for Odoo activation (Phase 0 can run in parallel)**:
```
Verify app reg → Add redirect URI → Create client secret → Set config in Odoo → Test login
```
