# Target State -- Integration & Authentication

**Audit Date**: 2026-03-27 12:30 PHT

---

## 1. Mailbox Host Authentication (Gmail Add-on -> Odoo)

**Target**: Provider-first, API-key-as-fallback

| Component | Target State |
|-----------|-------------|
| Primary auth | Microsoft Entra ID via Odoo native OAuth button |
| Secondary auth | Google Workspace OAuth (w9studio.net hosted domain) |
| Fallback auth | Odoo API key (collapsed, admin-only UX) |
| Session token | Custom Odoo session token issued by `/ipai/mail_plugin/provider_session` |
| Token storage | GAS `PropertiesService.getUserProperties()` (per-user, encrypted by Google) |
| Token lifetime | Server-controlled expiry (recommended: 8 hours) |
| Nonce/CSRF | `buildAuthStateNonce()` called before auth start, mandatory validation on exchange |
| Identity model | Gmail address = mailbox host surface. ERP identity = separate (Entra/Google/local). Never conflated. |

**Required modules**:
- `ipai_mail_plugin` -- Odoo controller implementing `/ipai/mail_plugin/*` endpoints
- `ipai_auth_oidc` -- Entra OIDC provider configuration with PKCE

**Auth flow (target)**:
1. User clicks "Continue with Microsoft" in Gmail sidebar
2. Add-on generates nonce, opens `https://erp.insightpulseai.com/web/login?state={nonce}&redirect=/ipai/mail_plugin/auth_complete`
3. Odoo login page renders Entra OAuth button
4. User authenticates with Entra, Entra redirects to `/auth_oauth/signin`
5. Odoo creates session, redirects to `/ipai/mail_plugin/auth_complete` which displays a one-time auth code
6. User pastes auth code into Gmail sidebar "Complete sign-in" form
7. Add-on calls `/ipai/mail_plugin/provider_session` with code + nonce
8. Backend validates nonce, exchanges code for session token, returns token
9. Token stored in PropertiesService, sidebar reloads as connected

---

## 2. Odoo Workforce Authentication (Microsoft Entra Primary)

**Target**: Entra OIDC as primary SSO, local password as break-glass only

| Component | Target State |
|-----------|-------------|
| Primary IdP | Microsoft Entra ID (`ceoinsightpulseai.onmicrosoft.com`) |
| Auth flow | Authorization Code + PKCE |
| Token validation | RS256, issuer validation, audience validation |
| User provisioning | JIT (create on first login, match by email) |
| Group sync | Entra security groups -> Odoo `group_ids` |
| Session management | Odoo `session_id` cookie, back-channel logout support |
| Local password | Break-glass/admin only (`local_password: break_glass_only` per OIDC SSOT) |
| MFA | Enforced by Entra Conditional Access (not Odoo-side) |

**App registration**: `ipai-odoo-login-prod` (client_id: `07bd9669-1eca-4d93-8880-fd3abb87f812`)
**Redirect URI**: `https://erp.insightpulseai.com/auth_oauth/signin`
**Module**: `auth_oauth` (stock) + `ipai_auth_oidc` (custom PKCE + validation + JIT)

---

## 3. Odoo Customer/Portal Authentication (Google Secondary)

**Target**: Google Workspace OAuth for w9studio.net users

| Component | Target State |
|-----------|-------------|
| Provider | Google OAuth 2.0 (internal consent screen) |
| Hosted domain | `w9studio.net` (restricts to Workspace accounts) |
| Redirect URI | `https://erp.insightpulseai.com/auth_oauth/signin` |
| Secret management | Client ID + secret in Azure Key Vault, injected as env vars |
| Odoo config | `auth.oauth.provider` record provisioned by `ipai_auth_oidc` module (not DB-injected via Settings action) |
| User provisioning | JIT with email matching, portal group assignment |

**Key change from current state**: Move provider configuration from DB-injected (`action_apply_google_oauth()`) to module-managed data file (`data/auth_oauth_provider.xml`).

---

## 4. Backend/Workload Identity (Managed Identity -> Key Vault)

**Target**: Azure Managed Identity for all service-to-service auth

| Component | Target State |
|-----------|-------------|
| ACA -> PostgreSQL | System-assigned managed identity -> Key Vault secrets (`pg-odoo-user`, `pg-odoo-password`) -> env vars |
| ACA -> Zoho SMTP | System-assigned managed identity -> Key Vault secrets (`zoho-smtp-user`, `zoho-smtp-password`) -> env vars |
| ACA -> Azure AI | System-assigned managed identity -> `DefaultAzureCredential` -> Foundry/Doc Intelligence |
| ACA -> Key Vault | System-assigned managed identity (RBAC: Key Vault Secrets User) |
| CI/CD -> Azure | Workload identity federation (preferred) or service principal certificate |
| Admin CLI -> Azure | Workload identity federation or certificate (rotate away from client secret) |

**Secret inventory (Azure Key Vault `kv-ipai-dev`)**:
- `pg-odoo-user`, `pg-odoo-password` -- PostgreSQL credentials
- `zoho-smtp-user`, `zoho-smtp-password` -- Zoho SMTP credentials
- `entra-odoo-login-client-id`, `entra-odoo-login-client-secret` -- Entra app for Odoo login
- `google-oauth-w9studio-client-id`, `google-oauth-w9studio-client-secret` -- Google OAuth for W9 Studio

---

## 5. Data-Plane Auth (Fabric Mirroring, Databricks)

**Target**: Managed Identity throughout the data pipeline

| Component | Target State |
|-----------|-------------|
| Fabric Mirroring | Azure PG system-assigned MI -> Fabric workspace (reader role) |
| Databricks workspace auth | Entra SSO for interactive users, MI for service accounts |
| Databricks SQL Warehouse | Entra token for Power BI connector, MI for ETL jobs |
| Power BI -> Databricks | Built-in Databricks connector with Entra SSO pass-through |

**Current blockers**: Fabric capacity not provisioned, Databricks SQL Warehouse not deployed, Power BI workspace not created.

---

## 6. Third-Party Integration Auth

| Integration | Target Auth | Secret Location |
|-------------|-------------|-----------------|
| Zoho SMTP | Username/password via env vars | Azure Key Vault |
| Wix CMS | Wix MCP OAuth (developer tool only) | Wix auth flow |
| GitHub | GitHub Copilot MCP OAuth / OIDC federation for CI | GitHub token / federated identity |
| Azure DevOps | PAT or OIDC federation | AzDO PAT (rotate to federated) |
| Cloudflare DNS | API token via Terraform | Azure Key Vault or CI secret |
| clasp (GAS deployment) | Google OAuth (developer tool only) | `~/.clasprc.json` |

---

## 7. Break-Glass/Admin Fallback

| Scenario | Method | Access |
|----------|--------|--------|
| Entra outage | Odoo local admin password (`admin` user, `list_db = False`) | Direct HTTPS to `erp.insightpulseai.com/web/login` |
| Gmail add-on provider failure | API key fallback (collapsed Advanced section) | Email + Odoo API key via `connectWithApiKey()` |
| Key Vault unavailable | ACA env vars cached at container start | Existing containers continue; new containers fail |
| Front Door outage | Direct ACA FQDN (`ipai-odoo-dev-web.salmontree-b7d27e19...`) | Requires DNS override or direct URL |
| PostgreSQL credential rotation | Key Vault secret update + ACA revision restart | Zero-downtime: new revision pulls updated secret |

---

## Architecture Diagram (Text)

```
                     Gmail Sidebar
                          |
                    [PropertiesService]
                          |
                  Bearer token / API key
                          |
                    Azure Front Door
                     (TLS + WAF)
                          |
                    ACA Odoo Web
                     (proxy_mode)
                      /       \
          /auth_oauth/signin   /ipai/mail_plugin/*
           (Entra/Google)       (session exchange)
                |                      |
          Entra ID / Google      ipai_mail_plugin
                                  (controller)
                                       |
                               Odoo Session Token
                                       |
                            PostgreSQL (via Key Vault MI)
                            Zoho SMTP (via Key Vault MI)
                            Azure AI Foundry (via MI)
```
