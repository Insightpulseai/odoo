# Target-State Authentication Architecture

**Audit Date**: 2026-03-27 12:30 PHT
**Status**: Canonical target -- all remediation work converges here

---

## Principles

1. **Microsoft Entra ID is the workforce identity provider.** All human login flows terminate at Entra.
2. **Azure Managed Identity is the service identity provider.** All service-to-service flows use system-assigned managed identity.
3. **Azure Key Vault is the sole secret store.** No credentials in git, no credentials in `ir.config_parameter`, no credentials in config files.
4. **Break-glass is local Odoo password login**, restricted to named admin accounts only.
5. **Identity flows are layered**: mailbox host identity (Gmail/Outlook) is distinct from ERP identity (Odoo user). The bridge layer translates between them.

---

## 1. Mailbox Host Authentication (Gmail Add-on to Odoo)

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

**Required modules:**
- `ipai_mail_plugin` -- Odoo controller implementing `/ipai/mail_plugin/*` endpoints
- `ipai_auth_oidc` -- Entra OIDC provider configuration with PKCE

**Auth flow (target):**
1. User clicks "Continue with Microsoft" in Gmail sidebar
2. Add-on generates nonce via `buildAuthStateNonce()`, opens `https://erp.insightpulseai.com/web/login?state={nonce}&redirect=/ipai/mail_plugin/auth_complete`
3. Odoo login page renders Entra OAuth button
4. User authenticates with Entra, Entra redirects to `/auth_oauth/signin`
5. Odoo creates session, redirects to `/ipai/mail_plugin/auth_complete` which displays a one-time auth code
6. User pastes auth code into Gmail sidebar "Complete sign-in" form
7. Add-on calls `/ipai/mail_plugin/provider_session` with code + nonce
8. Backend validates nonce (mandatory -- empty nonce is rejected), exchanges code for session token, returns token
9. Token stored in PropertiesService, sidebar reloads as connected

**Current gap:** Backend endpoints do not exist (finding C-1). The nonce system is implemented client-side but validation is optional (finding M-3). Both must be resolved together.

---

## 2. Odoo Workforce Authentication

### Primary: Microsoft Entra OIDC

| Component | Target State |
|-----------|-------------|
| IdP | Microsoft Entra ID (`ceoinsightpulseai.onmicrosoft.com`) |
| Auth flow | Authorization Code + PKCE |
| Token validation | RS256, issuer check (`https://login.microsoftonline.com/{tenant}/v2.0`), audience check |
| User provisioning | JIT: first login creates `res.users` record, matches by email |
| Group sync | Entra security groups mapped to Odoo `group_ids` |
| Session management | Odoo `session_id` cookie, back-channel logout support |
| MFA | Enforced by Entra Conditional Access policies (not Odoo-side) |

**App registration:** `ipai-odoo-login-prod` (client_id: `07bd9669-1eca-4d93-8880-fd3abb87f812`)
**Redirect URI:** `https://erp.insightpulseai.com/auth_oauth/signin`
**Module:** `auth_oauth` (stock Odoo) + `ipai_auth_oidc` (custom PKCE + RS256 validation + JIT provisioning)
**Secrets:** Azure Key Vault (`entra-odoo-login-client-id`, `entra-odoo-login-client-secret`)

**Current gap:** Module `ipai_auth_oidc` is planned but not built (finding C-2). App registration exists. Spec exists at `spec/entra-identity-migration/`.

### Secondary: Google OAuth (w9studio.net)

| Component | Target State |
|-----------|-------------|
| Provider | Google OAuth 2.0 (internal consent screen) |
| Hosted domain | `w9studio.net` (restricts to Workspace accounts) |
| Redirect URI | `https://erp.insightpulseai.com/auth_oauth/signin` |
| Secret management | Client ID + secret in Azure Key Vault, injected as env vars |
| Odoo config | `auth.oauth.provider` record provisioned by `ipai_auth_oidc` data file (not DB-injected via Settings action) |
| User provisioning | JIT with email matching, portal group assignment |

**Key change from current state:** Move provider configuration from DB-injected (`action_apply_google_oauth()` in `ipai_enterprise_bridge`) to module-managed data file (`data/auth_oauth_provider.xml` in `ipai_auth_oidc`). Move client_secret from `ir.config_parameter` to Key Vault (finding H-5).

### Break-glass: Local Password

| Component | Target State |
|-----------|-------------|
| Scope | Named admin accounts only (max 3: `admin`, plus 2 named ops accounts) |
| MFA | Not available (Odoo CE limitation) |
| Use case | Entra outage, initial bootstrap, emergency access |
| Governance | `auditlog` module records all local login events |
| Configuration | `local_password: break_glass_only` per OIDC SSOT |

---

## 3. Entra / Workload Identity (Service-to-Service)

All Azure Container App services use **system-assigned managed identity** for Key Vault access and inter-service auth.

| Service | Identity Type | Key Vault Role | Secrets Consumed |
|---------|--------------|----------------|------------------|
| `ipai-odoo-dev-web` | System MI | Key Vault Secrets User | PG creds, SMTP creds, OAuth secrets |
| `ipai-odoo-dev-worker` | System MI | Key Vault Secrets User | PG creds, SMTP creds |
| `ipai-odoo-dev-cron` | System MI | Key Vault Secrets User | PG creds |
| `ipai-copilot-gateway` | System MI | Key Vault Secrets User | Foundry API keys |
| `ipai-ocr-dev` | System MI | Key Vault Secrets User | Doc Intelligence keys |

**Platform admin CLI:**
- App registration: `ipai-platform-admin-cli-prod` (client_id: `b0172e9f-b179-4abe-9281-d3b56eda4489`)
- Current state: client secret, flagged `rotate_required` (finding H-1)
- Target: migrate to workload identity federation or certificate
- Rotation policy: 90-day max secret lifetime

**CI/CD identity:**
- Target: Azure DevOps service connection with workload identity federation
- Current: service principal with secret (`azure-ipai` service connection)

---

## 4. Backend-to-Backend Auth

| Flow | Source | Target | Auth Mechanism | Secret Source |
|------|--------|--------|---------------|--------------|
| Odoo to PostgreSQL | ACA containers | `pg-ipai-odoo` | Username/password via env vars | KV: `pg-odoo-user`, `pg-odoo-password` |
| Odoo to Zoho SMTP | ACA containers | `smtppro.zoho.com:587` | SMTP AUTH (STARTTLS) | KV: `zoho-smtp-user`, `zoho-smtp-password` |
| Odoo to AI Foundry | ACA containers | `oai-ipai-dev` | Managed Identity (`DefaultAzureCredential`) | Azure platform (no stored secret) |
| Odoo to Doc Intelligence | ACA containers | `docai-ipai-dev` | Managed Identity or API key | KV (if API key), Azure platform (if MI) |
| Front Door to ACA | Azure Front Door | ACA ingress | Network-level trust | Azure infrastructure |

**Front Door proxy handling:** `ipai_aca_proxy` module patches `X-Forwarded-Host` injection (finding L-2). This is architecturally correct for the ACA constraint and should be monitored during Odoo version upgrades.

**Future target for PG auth:** Migrate from username/password to Entra-managed PostgreSQL authentication (Azure AD auth for PostgreSQL Flexible Server). This eliminates stored DB credentials entirely. Blocked by: PostgreSQL Flexible Server Entra admin configuration.

**Secret inventory (Azure Key Vault `kv-ipai-dev`):**
- `pg-odoo-user`, `pg-odoo-password` -- PostgreSQL credentials
- `zoho-smtp-user`, `zoho-smtp-password` -- Zoho SMTP credentials
- `entra-odoo-login-client-id`, `entra-odoo-login-client-secret` -- Entra app for Odoo login
- `google-oauth-w9studio-client-id`, `google-oauth-w9studio-client-secret` -- Google OAuth for W9 Studio

---

## 5. Data-Plane Auth

| Data Service | Auth Mechanism | Identity Authority | Secret Source | Status |
|-------------|---------------|-------------------|--------------|--------|
| Fabric Mirroring (PG to Fabric) | System-assigned Managed Identity | Azure AD | Azure platform (no stored secret) | Source ready, target pending Fabric capacity |
| Databricks workspace | Entra SSO (users), MI or PAT (services) | Microsoft Entra ID | KV for PAT, Entra for SSO | Planned, not deployed |
| Databricks SQL Warehouse | Entra token for Power BI, MI for ETL | Microsoft Entra ID | Entra token | Planned |
| PostgreSQL (`pg-ipai-odoo`) | Username/password via env vars | PostgreSQL native | KV: `pg-odoo-user`, `pg-odoo-password` | Active |
| Power BI (via Databricks) | Entra SSO pass-through | Microsoft Entra ID | Entra token | Planned |

**Current blockers:** Fabric capacity not provisioned, Databricks SQL Warehouse not deployed, Power BI workspace not created.

**Target:** All data-plane services authenticate via Entra. PATs are transitional and subject to 90-day rotation policy.

---

## 6. Editor / Runtime Control-Surface Auth

Developer workstation surfaces delegate authentication to their respective identity providers. No cross-extension credential sharing.

| Surface | Identity Provider | Auth Mechanism | Credential Storage |
|---------|------------------|---------------|-------------------|
| VS Code Azure ML (`proj-ipai-claude`) | Microsoft Entra ID | Azure CLI (`az login`) | OS keychain via Azure CLI |
| VS Code GitHub extension | GitHub | GitHub OAuth | OS keychain via GitHub CLI |
| VS Code Docker extension | Local OS | Docker socket permission | Docker daemon socket (local) |
| Azure DevOps MCP server | Azure DevOps | PAT or OAuth | Environment variable |
| GitHub MCP server | GitHub | Copilot OAuth | GitHub token |
| Azure MCP server | Microsoft Entra ID | Azure CLI auth | Azure CLI credential cache |
| clasp (GAS deployment) | Google | Google OAuth | `~/.clasprc.json` (user home, not tracked) |

**ACR auth (`acripaiodoo`):** Separate from Docker Desktop socket auth. Requires `az acr login --name acripaiodoo` (uses Azure CLI / Entra token). Not bound to Docker Desktop context.

**Docker Desktop context:** `docker-desktop` context, `default` profile. Local-only runtime. No remote registry auth in this context.

---

## 7. Third-Party Integration Auth

| Integration | Auth Mechanism | Secret Source | Runtime Context |
|-------------|---------------|--------------|-----------------|
| Zoho SMTP | Username/password (SMTP AUTH over STARTTLS:587) | KV: `zoho-smtp-user`, `zoho-smtp-password` | ACA production. Standard `ir.mail_server` transport. |
| Wix CMS | Wix MCP OAuth (per-session) | Wix auth flow | Developer tooling only. Not production. |
| GitHub | Copilot OAuth (MCP), OIDC federation (CI) | GitHub token / federated identity | Dev + CI |
| Azure DevOps | PAT or OIDC federation | AzDO PAT (rotate to federated) | CI/CD |
| Google APIs (GAS, clasp) | Google OAuth | `~/.clasprc.json` (user home) | Dev tooling. Script ID: `1QaH14jbBl7PcvjLXgkzZogh6SzqS_kXoTJ_MzzmavW6CRLMANG24Ko4q` |
| Google OAuth (w9studio.net) | OAuth2 Authorization Code | KV: `google-oauth-w9studio-client-id`, `google-oauth-w9studio-client-secret` | ACA production |
| Cloudflare DNS | API token via Terraform | Azure Key Vault or CI secret | IaC deployment |

---

## 8. Break-Glass / Admin Fallback

| Scenario | Method | Access | Governance |
|----------|--------|--------|-----------|
| Entra outage | Odoo local admin password (`admin` user, `list_db = False`) | Direct HTTPS to `erp.insightpulseai.com/web/login` | `auditlog` records all local logins |
| Gmail add-on provider failure | API key fallback (collapsed Advanced section) | Email + Odoo API key via `connectWithApiKey()` | API key per-user, stored in GAS PropertiesService |
| Key Vault unavailable | ACA env vars cached at container start | Existing containers continue; new containers fail | Alert on container restart loop |
| Front Door outage | Direct ACA FQDN | `ipai-odoo-dev-web.salmontree-b7d27e19.southeastasia.azurecontainerapps.io` | Emergency only, requires DNS override |
| PostgreSQL credential rotation | Key Vault secret update + ACA revision restart | Zero-downtime via revision management | New revision pulls updated secret |

---

## Architecture Diagram (Logical)

```
                     +------------------+
                     | Microsoft Entra  |
                     |  (Workforce IdP) |
                     +--------+---------+
                              |
               +--------------+--------------+
               |              |              |
         Odoo Login    Databricks SSO   Power BI SSO
         (OIDC+PKCE)   (Entra SSO)     (Entra SSO)
               |
      +--------+--------+
      |                  |
   Browser           Gmail Add-on
   (session cookie)  (Bearer token via
                      ipai_mail_plugin)

                     +------------------+
                     | Azure Managed    |
                     |  Identity (MI)   |
                     +--------+---------+
                              |
          +-------------------+-------------------+
          |           |           |               |
     Key Vault    AI Foundry   Doc Intel    Fabric Mirroring
     (GET)        (inference)  (OCR)        (PG replication)

                     +------------------+
                     | Azure Key Vault  |
                     |  (Secret Store)  |
                     +--------+---------+
                              |
          +-------------------+-------------------+
          |           |           |               |
     PG creds     SMTP creds   OAuth secrets   API keys
```

---

## Decommissioned Identity Surfaces (Never Reintroduce)

| Surface | Replacement | Date |
|---------|------------|------|
| Keycloak (`auth.insightpulseai.com`) | Microsoft Entra ID | 2026-03-25 |
| Supabase Auth (all instances) | Microsoft Entra ID | 2026-03-26 |
| Mailgun SMTP (`mg.insightpulseai.com`) | Zoho SMTP | 2026-03-11 |
| n8n webhook auth | Decommissioned (no replacement) | 2026-03-25 |
| Plane API token | Decommissioned (no replacement) | 2026-03-25 |

---

## Convergence Criteria

This target-state is achieved when:

1. `ipai_auth_oidc` module is installed and Entra login works at `erp.insightpulseai.com/web/login`
2. `ipai_mail_plugin` module is installed and Gmail add-on can exchange provider sessions
3. All OAuth secrets are in Azure Key Vault, zero secrets in `ir.config_parameter`
4. Front Door routes reference only active services
5. All CLAUDE.md files agree on DNS authority
6. No hardcoded credentials exist in any tracked file
7. Platform admin CLI credential is on a 90-day rotation schedule
8. MCP configs reference only active services
