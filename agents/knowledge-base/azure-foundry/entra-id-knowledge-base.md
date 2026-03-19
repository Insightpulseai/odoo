# Microsoft Entra ID -- Canonical Knowledge Base

> **Purpose**: Comprehensive reference for the InsightPulse AI platform's migration from Keycloak to Microsoft Entra ID.
> **Last researched**: 2026-03-19
> **Sources**: Microsoft Learn official documentation (40+ pages synthesized)
> **Scope**: Product family, integration patterns, migration checklist, security baseline, IaC patterns, Graph API reference

---

## Table of Contents

1. [Entra ID Product Family Map](#1-entra-id-product-family-map)
2. [Integration Matrix](#2-integration-matrix)
3. [Keycloak to Entra Migration Checklist](#3-keycloak-to-entra-migration-checklist)
4. [Service Principal Topology](#4-service-principal-topology)
5. [Conditional Access Policy Templates](#5-conditional-access-policy-templates)
6. [Graph API Quick Reference](#6-graph-api-quick-reference)
7. [Terraform / Bicep Patterns](#7-terraform--bicep-patterns)
8. [Security Baseline](#8-security-baseline)
9. [Licensing Reference](#9-licensing-reference)

---

## 1. Entra ID Product Family Map

Microsoft Entra is a family of identity and network access products organized across four maturity stages of Zero Trust access.

### 1.1 Core Products

| Product | What It Is | License | Relevance to IPAI |
|---------|-----------|---------|-------------------|
| **Microsoft Entra ID** (formerly Azure AD) | Cloud IAM: authentication, SSO, Conditional Access, MFA, directory services | Free / P1 / P2 | **Primary IdP** -- replaces Keycloak |
| **Microsoft Entra ID Governance** | Entitlement management, access reviews, lifecycle workflows, PIM | ID Governance add-on | Access recertification, JIT admin |
| **Microsoft Entra ID Protection** | Risk-based sign-in detection, compromised credential detection | P2 | Risk policies for Conditional Access |
| **Microsoft Entra Workload ID** | Identity for apps, services, containers (service principals + managed identities) | Workload ID license | Service-to-service auth across ACA apps |
| **Microsoft Entra External ID** | B2B collaboration + CIAM for customer-facing apps | Included / MAU-based | Guest access for partners, future CIAM |
| **Microsoft Entra Verified ID** | Decentralized identity, verifiable credentials (W3C DID standards) | Included | Not immediate priority |
| **Microsoft Entra Domain Services** | Managed AD DS (Kerberos, NTLM, LDAP, Group Policy) | Standalone | Not needed (no legacy on-prem apps) |
| **Microsoft Entra Private Access** | ZTNA replacement for VPN | Suite | Future consideration |
| **Microsoft Entra Internet Access** | Secure web gateway, SaaS access control | Suite | Future consideration |
| **Microsoft Entra Permissions Management** | CIEM -- multicloud permissions visibility | Standalone | Azure RBAC audit |

### 1.2 Product Relationships

```
Microsoft Entra ID (Core)
    |
    +-- Conditional Access (Zero Trust policy engine, requires P1)
    |       |
    |       +-- ID Protection (risk signals, requires P2)
    |       +-- MFA (authentication strength)
    |       +-- Device compliance
    |
    +-- Enterprise Apps / App Registrations
    |       |
    |       +-- SSO (SAML, OIDC, password, linked)
    |       +-- SCIM provisioning
    |       +-- Application Proxy (on-prem)
    |
    +-- Managed Identities (system-assigned / user-assigned)
    |       |
    |       +-- Key Vault access
    |       +-- PostgreSQL auth
    |       +-- Storage access
    |
    +-- Workload Identities
    |       |
    |       +-- Service Principals
    |       +-- Workload Identity Federation (GitHub Actions, K8s)
    |       +-- Conditional Access for workloads
    |
    +-- ID Governance
    |       |
    |       +-- PIM (just-in-time privileged access)
    |       +-- Access Reviews
    |       +-- Entitlement Management
    |       +-- Lifecycle Workflows
    |
    +-- External ID
    |       |
    |       +-- B2B Collaboration (guest users)
    |       +-- B2B Direct Connect (Teams shared channels)
    |       +-- External Tenants (CIAM)
    |
    +-- Hybrid Identity
            |
            +-- Azure AD Connect / Cloud Sync
            +-- Password Hash Sync / Pass-through Auth / Federation
```

### 1.3 Key Concepts

**Application Object vs Service Principal**: The application object is the global template (lives in home tenant). The service principal is the local instance per tenant. Creating an app registration automatically creates both in the home tenant. In multi-tenant scenarios, a service principal is created in each consuming tenant upon consent.

**Three types of Service Principals**:
1. **Application** -- local representation of a registered app
2. **Managed Identity** -- special type tied to Azure resource lifecycle, no credentials to manage
3. **Legacy** -- pre-app-registration era, no associated app object

**Managed Identity Types**:
- **System-assigned**: Tied to a single Azure resource lifecycle. Deleted when resource is deleted.
- **User-assigned** (recommended): Independent lifecycle, can be shared across multiple resources.

---

## 2. Integration Matrix

### 2.1 Platform Service Integration Map

| Platform Service | Auth Method | Entra Feature | Protocol | Provisioning | Priority |
|-----------------|-------------|---------------|----------|-------------|----------|
| **Odoo CE 19** (erp.) | SAML SSO or OIDC | Enterprise App (non-gallery) | SAML 2.0 or OIDC | Manual (no SCIM) | **P0** |
| **Azure Container Apps** (all) | Built-in auth + Managed Identity | Built-in auth provider + MI | OIDC | N/A (infra) | **P0** |
| **Azure Database for PostgreSQL** | Managed Identity | Entra Authentication for PG | Token-based (JWT) | Role mapping | **P0** |
| **Azure Key Vault** | Managed Identity | RBAC / Access Policy | Token-based | N/A | **P0** |
| **Apache Superset** (superset.) | OIDC SSO | Enterprise App (non-gallery) | OAuth 2.0 / OIDC | Manual | **P1** |
| **Azure Databricks** (dbw.) | SSO + SCIM | Gallery App | OIDC + SCIM 2.0 | Automatic (SCIM) | **P1** |
| **n8n** (n8n.) | OIDC SSO | Enterprise App (non-gallery) | OIDC | Manual | **P1** |
| **Plane** (plane.) | OIDC SSO | Enterprise App (non-gallery) | OIDC | Manual | **P2** |
| **Shelf** (shelf.) | OIDC SSO | Enterprise App (non-gallery) | OIDC | Manual | **P2** |
| **CRM** (crm.) | OIDC SSO | Enterprise App (non-gallery) | OIDC | Manual | **P2** |
| **MCP Coordinator** (mcp.) | Managed Identity | MI on ACA | Token-based | N/A | **P1** |
| **OCR Service** (ocr.) | Managed Identity | MI on ACA | Token-based | N/A | **P2** |
| **GitHub Actions** | Workload Identity Federation | Federated credential on App Reg | OIDC | N/A | **P1** |
| **Azure AI Services** (OpenAI, Doc Intel) | Managed Identity | MI RBAC | Token-based | N/A | **P1** |

### 2.2 Odoo CE 19 Integration Details

Odoo does not appear in the Entra gallery. Integration requires a **non-gallery SAML or OIDC application**.

**SAML approach** (recommended for Odoo):
1. Create Enterprise App (non-gallery) in Entra admin center
2. Configure SAML SSO with:
   - Identifier (Entity ID): `https://erp.insightpulseai.com`
   - Reply URL (ACS): `https://erp.insightpulseai.com/auth_saml/signin`
   - Sign-on URL: `https://erp.insightpulseai.com/web/login`
3. Map attributes: NameID = user.userprincipalname, email, displayname
4. Install OCA `auth_saml` module in Odoo (from `OCA/server-auth`)
5. Configure SAML provider in Odoo with Entra metadata URL

**OIDC approach** (alternative):
1. Register App in Entra (App Registrations)
2. Configure redirect URI: `https://erp.insightpulseai.com/auth_oauth/signin`
3. Use OCA `auth_oauth` module with Entra's OIDC endpoints
4. Client ID + Client Secret stored in Azure Key Vault

### 2.3 Azure Container Apps Authentication

ACA has a **built-in authentication feature** (formerly Easy Auth) that provides:
- Automatic app registration with Microsoft identity platform
- Sign-in/sign-out endpoints under `/.auth/` route prefix
- Token validation and user claims injection via headers
- Support for multiple identity providers (Microsoft, Google, Facebook, custom OIDC)

**Configuration for IPAI ACA apps**:
- Redirect URI pattern: `https://<APP>.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io/.auth/login/aad/callback`
- Issuer URL: `https://login.microsoftonline.com/<TENANT-ID>/v2.0`
- Client secret stored as ACA secret (or Key Vault reference)
- `X-MS-TOKEN-AAD-ID-TOKEN` header exposes the ID token to app code

**Daemon/service-to-service calls**: Use OAuth 2.0 client credentials grant. Register a daemon app, create app roles on the target app, grant Application permissions + admin consent.

### 2.4 PostgreSQL Entra Authentication

Azure Database for PostgreSQL Flexible Server supports Entra authentication natively:
- Set an Entra admin on the PG server (user, group, service principal, or managed identity)
- Applications authenticate using JWT access tokens instead of passwords
- Managed identities can connect without storing any credentials
- Role mapping: PG roles map to Entra users, groups, service principals, or managed identities

**For IPAI** (`ipai-odoo-dev-pg`):
- Set Odoo ACA managed identity as PG Entra admin or create a PG role mapped to the MI
- Odoo connects using token from MI instead of static db_password secret
- Eliminates the secret rotation problem that caused the 2026-03-18 production outage

### 2.5 Apache Superset + Entra ID

Superset uses Flask-AppBuilder's built-in OAuth support:

```python
# superset_config.py
AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [{
    'name': 'azure',
    'icon': 'fa-windows',
    'token_key': 'access_token',
    'remote_app': {
        'client_id': os.environ.get('AZURE_CLIENT_ID'),
        'client_secret': os.environ.get('AZURE_CLIENT_SECRET'),
        'api_base_url': 'https://graph.microsoft.com/v1.0/',
        'client_kwargs': {'scope': 'openid profile email User.Read'},
        'access_token_url': f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token',
        'authorize_url': f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize',
        'server_metadata_url': f'https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration',
    }
}]
```

Requires: Enterprise App (non-gallery), redirect URI `https://superset.insightpulseai.com/oauth-authorized/azure`.

### 2.6 Azure Databricks + Entra ID

Databricks is a **gallery app** in Entra with native support:
- SSO: Automatic via OIDC (Databricks + Entra are both Microsoft)
- SCIM: Account-level provisioning syncs users/groups from Entra to Databricks
- For accounts created after Aug 2025: automatic identity management (no SCIM setup needed)
- Premium plan required for SCIM provisioning

### 2.7 n8n + Entra ID

n8n supports OIDC SSO in self-hosted mode:
- Register App in Entra (App Registrations)
- Configure redirect URI: `https://n8n.insightpulseai.com/rest/oauth2-credential/callback`
- Set environment variables: `N8N_AUTH_OIDC_CLIENT_ID`, `N8N_AUTH_OIDC_CLIENT_SECRET`, `N8N_AUTH_OIDC_ISSUER`
- Issuer: `https://login.microsoftonline.com/<TENANT_ID>/v2.0`

---

## 3. Keycloak to Entra Migration Checklist

### 3.1 Migration Strategy: Parallel Run with Per-App Cutover

The recommended approach is **not** a big-bang migration. Instead:
1. Stand up Entra ID as the new IdP
2. Keep Keycloak running during transition
3. Cut over apps one at a time
4. Decommission Keycloak after all apps migrate

### 3.2 Pre-Migration Gates

| # | Gate | Status | Evidence |
|---|------|--------|----------|
| 1 | Microsoft 365 Business Premium or Entra P1/P2 license active | Pending | License confirmation |
| 2 | Custom domain `insightpulseai.com` verified in Entra tenant | Pending | DNS TXT record |
| 3 | At least 2 break-glass Global Admin accounts created (cloud-only, no MFA) | Not started | Account names documented |
| 4 | User inventory exported from Keycloak (UPN, email, groups, roles) | Not started | CSV export |
| 5 | Application inventory (all apps using Keycloak for auth) | Not started | Spreadsheet |
| 6 | Entra Conditional Access policies drafted (report-only mode) | Not started | Policy JSON |
| 7 | Service principal topology designed (see Section 4) | Not started | Diagram |
| 8 | Managed identity assignments planned for all ACA apps | Not started | YAML |
| 9 | Key Vault access policies migrated to RBAC model | Not started | Bicep |
| 10 | DNS CNAME for `auth.insightpulseai.com` plan (redirect or decommission) | Not started | DNS YAML |

### 3.3 Migration Phases

**Phase 1: Foundation (Week 1-2)**
- [ ] Verify custom domain in Entra tenant
- [ ] Create user accounts (manual or CSV import via Graph API)
- [ ] Create security groups matching Keycloak roles
- [ ] Set up break-glass admin accounts
- [ ] Enable Security Defaults (or Conditional Access if P1)
- [ ] Configure MFA registration for all users

**Phase 2: Infrastructure Identity (Week 2-3)**
- [ ] Create user-assigned managed identity for Odoo ACA apps
- [ ] Assign MI to `ipai-odoo-dev-web`, `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron`
- [ ] Configure PG Entra authentication with MI
- [ ] Test Odoo DB connection via MI token (no password)
- [ ] Configure Key Vault RBAC for MI (replace access policies)
- [ ] Set up MI for Azure AI services access

**Phase 3: App SSO Migration (Week 3-6)**

Per-app cutover order:
1. **Odoo** (P0) -- SAML via `auth_saml` OCA module
2. **Superset** (P1) -- OIDC via Flask-AppBuilder
3. **Databricks** (P1) -- Gallery app, auto-SSO
4. **n8n** (P1) -- OIDC SSO
5. **Plane** (P2) -- OIDC SSO
6. **Shelf** (P2) -- OIDC SSO
7. **CRM** (P2) -- OIDC SSO

For each app:
- [ ] Register Enterprise App or App Registration in Entra
- [ ] Configure SSO (SAML or OIDC)
- [ ] Test with pilot user
- [ ] Configure user/group assignment
- [ ] Update app configuration to use Entra endpoints
- [ ] Verify SSO flow end-to-end
- [ ] Remove Keycloak dependency from app config
- [ ] Monitor sign-in logs for 48 hours

**Phase 4: CI/CD Identity (Week 4-5)**
- [ ] Configure GitHub Actions Workload Identity Federation
- [ ] Replace service account credentials with federated credentials
- [ ] Update Azure DevOps pipeline identity

**Phase 5: Governance (Week 5-7)**
- [ ] Enable PIM for privileged roles (if P2)
- [ ] Configure access reviews for Enterprise Apps
- [ ] Set up lifecycle workflows for user onboarding/offboarding
- [ ] Enable ID Protection risk policies

**Phase 6: Decommission Keycloak (Week 7-8)**
- [ ] Verify all apps have zero sign-ins via Keycloak (7-day window)
- [ ] Remove `ipai-auth-dev` ACA app
- [ ] Update DNS: remove `auth.insightpulseai.com` CNAME (or redirect to Entra)
- [ ] Archive Keycloak configuration for reference
- [ ] Update all documentation

### 3.4 Keycloak-to-Entra Concept Mapping

| Keycloak Concept | Entra Equivalent | Notes |
|-----------------|------------------|-------|
| Realm | Tenant | 1 realm = 1 tenant (IPAI has 1 workforce tenant) |
| Client | App Registration + Enterprise App | App Reg = template, Enterprise App = service principal |
| Client ID / Secret | Application (client) ID / Client Secret | Same concept, different UI location |
| Roles (realm) | Entra Directory Roles | Global Admin, User Admin, etc. |
| Roles (client) | App Roles | Defined in app manifest, assigned to users/groups |
| Groups | Security Groups / M365 Groups | Groups can be role-assignable (P1) |
| Identity Providers | External Identity Providers | B2B collaboration or External ID |
| User Federation | Hybrid Identity (Azure AD Connect) | Not needed for cloud-only |
| OIDC Discovery URL | `https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration` | Standard OIDC |
| SAML Metadata URL | `https://login.microsoftonline.com/{tenant}/federationmetadata/2007-06/federationmetadata.xml` | Or use v2: `https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration` |
| Service Account | Service Principal + Client Credentials | Or Managed Identity (preferred) |
| Token Exchange | On-behalf-of flow / Client credentials | Graph API supports OBO flow |
| Admin Console | Microsoft Entra admin center (`entra.microsoft.com`) | |
| Account Console | My Apps (`myapps.microsoft.com`) / My Account (`myaccount.microsoft.com`) | |

---

## 4. Service Principal Topology

### 4.1 Recommended Layout for IPAI Platform

```
Tenant: insightpulseai.com
|
+-- User-Assigned Managed Identities
|   |
|   +-- mi-ipai-odoo          (shared across web, worker, cron ACA apps)
|   |   Roles: Key Vault Secrets User, PG Entra Auth, Storage Blob Reader
|   |
|   +-- mi-ipai-ai            (shared across AI service consumers)
|   |   Roles: Cognitive Services OpenAI User, Doc Intel User
|   |
|   +-- mi-ipai-mcp           (MCP coordinator ACA)
|   |   Roles: Key Vault Secrets User
|   |
|   +-- mi-ipai-superset      (Superset ACA)
|   |   Roles: Key Vault Secrets User, PG Entra Auth
|
+-- App Registrations (SSO)
|   |
|   +-- app-ipai-odoo-sso     (SAML SSO for Odoo web UI)
|   |   Type: Non-gallery SAML app
|   |   Redirect: https://erp.insightpulseai.com/auth_saml/signin
|   |
|   +-- app-ipai-superset-sso (OIDC SSO for Superset)
|   |   Type: Non-gallery OIDC app
|   |   Redirect: https://superset.insightpulseai.com/oauth-authorized/azure
|   |
|   +-- app-ipai-n8n-sso      (OIDC SSO for n8n)
|   |   Type: Non-gallery OIDC app
|   |   Redirect: https://n8n.insightpulseai.com/rest/oauth2-credential/callback
|   |
|   +-- app-ipai-plane-sso    (OIDC SSO for Plane)
|   +-- app-ipai-shelf-sso    (OIDC SSO for Shelf)
|   +-- app-ipai-crm-sso      (OIDC SSO for CRM)
|
+-- App Registrations (Service-to-Service)
|   |
|   +-- app-ipai-github-cicd  (Workload Identity Federation for GitHub Actions)
|   |   Federated credential: GitHub org/repo, branch filter
|   |
|   +-- app-ipai-copilot-api  (Odoo Copilot backend API)
|   |   Client credentials grant for service-to-service
|
+-- Gallery Enterprise Apps
|   |
|   +-- Azure Databricks      (auto-provisioned gallery app)
|       SCIM provisioning enabled
|
+-- Security Groups
    |
    +-- sg-ipai-admins         (Global Admin eligible via PIM)
    +-- sg-ipai-developers     (App-level access)
    +-- sg-ipai-finance        (Odoo finance module access)
    +-- sg-ipai-all-staff      (Dynamic group: all active employees)
    +-- sg-ipai-sso-odoo       (Assigned to Odoo Enterprise App)
    +-- sg-ipai-sso-superset   (Assigned to Superset Enterprise App)
    +-- sg-ipai-sso-n8n        (Assigned to n8n Enterprise App)
```

### 4.2 Managed Identity Best Practices

1. **Prefer user-assigned MI** over system-assigned for resources that share identity (e.g., Odoo web/worker/cron all need the same PG access)
2. **One MI per trust boundary**, not per resource -- reduces role assignment sprawl
3. **Use MI as Federated Identity Credential** on App Registrations when an Entra App is required (e.g., for client credentials flow) -- eliminates secrets entirely
4. **Never store MI credentials** -- they are automatically managed by Azure; use Azure.Identity SDK or MSAL
5. **Limit MI RBAC scope** -- assign roles at resource level, not resource group or subscription

### 4.3 App Registration vs Enterprise App Decision Tree

```
Do you need SSO for a web app?
  YES --> Enterprise App (may auto-create App Registration)
    Is the app in the Entra gallery?
      YES --> Gallery app (SAML/OIDC pre-configured)
      NO  --> Non-gallery app (manual SAML/OIDC config)

Do you need service-to-service auth?
  YES --> App Registration + Service Principal
    Can the caller run on Azure compute?
      YES --> Managed Identity (preferred, no secrets)
      NO  --> App Registration + Client Credentials
        Is the caller in a supported external platform (GitHub, K8s)?
          YES --> Workload Identity Federation (no secrets)
          NO  --> Client Secret or Certificate (rotate regularly)
```

---

## 5. Conditional Access Policy Templates

### 5.1 Recommended Policies for IPAI

All policies should be deployed in **report-only mode** first, then enabled after 7-day monitoring.

**Policy 1: Require MFA for All Users**
```
Name: CA001-Require-MFA-AllUsers
Assignments:
  Users: All users (exclude break-glass accounts)
  Cloud apps: All cloud apps
Conditions:
  (none -- applies universally)
Grant:
  Require: Authentication strength (MFA)
State: Report-only --> Enabled
```

**Policy 2: Block Legacy Authentication**
```
Name: CA002-Block-LegacyAuth
Assignments:
  Users: All users
  Cloud apps: All cloud apps
Conditions:
  Client apps: Exchange ActiveSync clients, Other clients
Grant:
  Block access
State: Enabled (immediate -- no report-only needed)
```

**Policy 3: Require MFA for Admin Roles**
```
Name: CA003-Require-MFA-Admins
Assignments:
  Users: Directory roles (Global Admin, User Admin, App Admin, Security Admin, etc.)
  Cloud apps: All cloud apps
Conditions:
  (none)
Grant:
  Require: Authentication strength (Phishing-resistant MFA)
State: Enabled
```

**Policy 4: Require Compliant Device for Azure Management**
```
Name: CA004-CompliantDevice-AzureMgmt
Assignments:
  Users: All users
  Cloud apps: Microsoft Azure Management
Conditions:
  (none)
Grant:
  Require: Device to be marked as compliant OR MFA
State: Report-only --> Enabled
```

**Policy 5: Block High-Risk Sign-ins (requires P2)**
```
Name: CA005-Block-HighRisk-SignIn
Assignments:
  Users: All users (exclude break-glass)
  Cloud apps: All cloud apps
Conditions:
  Sign-in risk: High
Grant:
  Block access
State: Enabled
```

**Policy 6: Require MFA for Medium-Risk Sign-ins (requires P2)**
```
Name: CA006-MFA-MediumRisk-SignIn
Assignments:
  Users: All users
  Cloud apps: All cloud apps
Conditions:
  Sign-in risk: Medium
Grant:
  Require: MFA
State: Report-only --> Enabled
```

**Policy 7: Named Location -- Restrict to PH + Trusted IPs**
```
Name: CA007-GeoRestrict-PH-Trusted
Assignments:
  Users: All users (exclude break-glass)
  Cloud apps: Odoo, Superset, n8n (sensitive apps)
Conditions:
  Locations:
    Include: All locations
    Exclude: Philippines, Trusted office IPs
Grant:
  Require: MFA + compliant device
State: Report-only --> Enabled
```

**Policy 8: Conditional Access for Workload Identities**
```
Name: CA008-Workload-LocationRestrict
Assignments:
  Users: Workload identities (service principals)
  Cloud apps: All cloud apps
Conditions:
  Locations:
    Include: All locations
    Exclude: Azure datacenter IPs
Grant:
  Block access
State: Report-only --> Enabled
```

### 5.2 Break-Glass Account Policy

- 2 cloud-only accounts with permanent Global Admin
- Excluded from ALL Conditional Access policies
- Use long, complex passwords (stored in physical safe or secure vault)
- Monitor sign-ins via Azure Monitor alerts
- Test quarterly to ensure they still work

---

## 6. Graph API Quick Reference

### 6.1 Key Endpoints

| Operation | Endpoint | Permission Required |
|-----------|----------|-------------------|
| List users | `GET /v1.0/users` | `User.Read.All` |
| Create user | `POST /v1.0/users` | `User.ReadWrite.All` |
| Delete user | `DELETE /v1.0/users/{id}` | `User.ReadWrite.All` |
| List groups | `GET /v1.0/groups` | `Group.Read.All` |
| Create group | `POST /v1.0/groups` | `Group.ReadWrite.All` |
| Add member to group | `POST /v1.0/groups/{id}/members/$ref` | `Group.ReadWrite.All` |
| List app registrations | `GET /v1.0/applications` | `Application.Read.All` |
| Create app registration | `POST /v1.0/applications` | `Application.ReadWrite.All` |
| List service principals | `GET /v1.0/servicePrincipals` | `Application.Read.All` |
| Create service principal | `POST /v1.0/servicePrincipals` | `Application.ReadWrite.All` |
| List directory roles | `GET /v1.0/directoryRoles` | `RoleManagement.Read.Directory` |
| Assign directory role | `POST /v1.0/directoryRoles/{id}/members/$ref` | `RoleManagement.ReadWrite.Directory` |
| List Conditional Access policies | `GET /v1.0/identity/conditionalAccess/policies` | `Policy.Read.All` |
| Create CA policy | `POST /v1.0/identity/conditionalAccess/policies` | `Policy.ReadWrite.ConditionalAccess` |
| List audit logs | `GET /v1.0/auditLogs/directoryAudits` | `AuditLog.Read.All` |
| List sign-in logs | `GET /v1.0/auditLogs/signIns` | `AuditLog.Read.All` |
| Get user's app role assignments | `GET /v1.0/users/{id}/appRoleAssignments` | `AppRoleAssignment.ReadWrite.All` |

### 6.2 Permission Types

| Permission | Delegated | Application | Admin Consent |
|-----------|-----------|-------------|---------------|
| `User.Read` | Yes | No | No |
| `User.Read.All` | Yes | Yes | Yes |
| `User.ReadWrite.All` | Yes | Yes | Yes |
| `Group.Read.All` | Yes | Yes | Yes |
| `Group.ReadWrite.All` | Yes | Yes | Yes |
| `Application.Read.All` | Yes | Yes | Yes |
| `Application.ReadWrite.All` | Yes | Yes | Yes |
| `Application.ReadWrite.OwnedBy` | No | Yes | Yes |
| `RoleManagement.Read.Directory` | Yes | Yes | Yes |
| `RoleManagement.ReadWrite.Directory` | Yes | Yes | Yes |
| `Policy.Read.All` | Yes | Yes | Yes |
| `Policy.ReadWrite.ConditionalAccess` | Yes | Yes | Yes |
| `AuditLog.Read.All` | Yes | Yes | Yes |
| `Directory.Read.All` | Yes | Yes | Yes |

### 6.3 Authentication Endpoints

| Endpoint | URL |
|----------|-----|
| Authorization | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize` |
| Token | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token` |
| OIDC Discovery | `https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration` |
| SAML Metadata | `https://login.microsoftonline.com/{tenant}/federationmetadata/2007-06/federationmetadata.xml` |
| Graph API | `https://graph.microsoft.com/v1.0/` |
| Graph API Beta | `https://graph.microsoft.com/beta/` |
| Admin Center | `https://entra.microsoft.com` |
| My Apps Portal | `https://myapps.microsoft.com` |
| My Account | `https://myaccount.microsoft.com` |

### 6.4 CLI Quick Reference

```bash
# Azure CLI -- Entra ID operations
az login
az ad user list --output table
az ad user create --display-name "John Doe" --user-principal-name john@insightpulseai.com --password "<temp>"
az ad group list --output table
az ad group create --display-name "sg-ipai-admins" --mail-nickname "sg-ipai-admins"
az ad group member add --group "sg-ipai-admins" --member-id "<user-object-id>"
az ad app list --output table
az ad app create --display-name "app-ipai-odoo-sso"
az ad sp list --output table
az ad sp create --id "<app-id>"

# Microsoft Graph PowerShell
Connect-MgGraph -Scopes "User.ReadWrite.All","Group.ReadWrite.All"
Get-MgUser -All
New-MgUser -DisplayName "John Doe" -UserPrincipalName "john@insightpulseai.com" ...
Get-MgGroup -All
New-MgGroup -DisplayName "sg-ipai-admins" -SecurityEnabled -MailEnabled:$false -MailNickname "sg-ipai-admins"
```

---

## 7. Terraform / Bicep Patterns

### 7.1 Terraform AzureAD Provider

The `hashicorp/azuread` provider manages Entra ID resources via Microsoft Graph API.

**Provider configuration**:
```hcl
terraform {
  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
  }
}

provider "azuread" {
  # Authenticates via: az login, managed identity, service principal, or OIDC
}
```

**App Registration + Service Principal**:
```hcl
# App Registration for Odoo SSO
resource "azuread_application" "odoo_sso" {
  display_name = "app-ipai-odoo-sso"
  sign_in_audience = "AzureADMyOrg"

  web {
    redirect_uris = [
      "https://erp.insightpulseai.com/auth_saml/signin",
    ]
    implicit_grant {
      id_token_issuance_enabled = true
    }
  }

  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph
    resource_access {
      id   = "e1fe6dd8-ba31-4d61-89e7-88639da4683d" # User.Read
      type = "Scope"
    }
  }

  app_role {
    allowed_member_types = ["User"]
    description          = "Odoo User"
    display_name         = "Odoo User"
    id                   = "<generate-uuid>"
    value                = "OdooUser"
    enabled              = true
  }
}

resource "azuread_service_principal" "odoo_sso" {
  client_id = azuread_application.odoo_sso.client_id
  app_role_assignment_required = true
}

# Assign security group to the app
resource "azuread_app_role_assignment" "odoo_users" {
  app_role_id         = azuread_application.odoo_sso.app_role[0].id
  principal_object_id = azuread_group.odoo_users.object_id
  resource_object_id  = azuread_service_principal.odoo_sso.object_id
}
```

**User-Assigned Managed Identity**:
```hcl
resource "azurerm_user_assigned_identity" "odoo" {
  name                = "mi-ipai-odoo"
  resource_group_name = "rg-ipai-dev"
  location            = "southeastasia"
}

# Assign to Container App
resource "azurerm_container_app" "odoo_web" {
  # ... other config ...
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.odoo.id]
  }
}

# Grant Key Vault Secrets User role
resource "azurerm_role_assignment" "odoo_kv" {
  scope                = azurerm_key_vault.ipai.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.odoo.principal_id
}
```

**Security Groups**:
```hcl
resource "azuread_group" "admins" {
  display_name     = "sg-ipai-admins"
  security_enabled = true
  assignable_to_role = true  # Required for PIM role-assignable groups
}

resource "azuread_group" "odoo_users" {
  display_name     = "sg-ipai-sso-odoo"
  security_enabled = true
}
```

**Workload Identity Federation (GitHub Actions)**:
```hcl
resource "azuread_application" "github_cicd" {
  display_name = "app-ipai-github-cicd"
}

resource "azuread_application_federated_identity_credential" "github" {
  application_id = azuread_application.github_cicd.id
  display_name   = "github-actions-main"
  description    = "GitHub Actions for Insightpulseai/odoo main branch"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:Insightpulseai/odoo:ref:refs/heads/main"
}
```

### 7.2 Bicep Patterns

**User-Assigned Managed Identity**:
```bicep
resource miOdoo 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'mi-ipai-odoo'
  location: 'southeastasia'
}
```

**Role Assignment (Key Vault Secrets User)**:
```bicep
resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, miOdoo.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: miOdoo.properties.principalId
    principalType: 'ServicePrincipal'
  }
}
```

**Container App with MI**:
```bicep
resource odooWeb 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'ipai-odoo-dev-web'
  location: 'southeastasia'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${miOdoo.id}': {}
    }
  }
  properties: {
    // ... container config ...
  }
}
```

### 7.3 Conditional Access Policies via Graph API (IaC Alternative)

Conditional Access policies are **not supported in Bicep/ARM**. Use Microsoft Graph API or Terraform `azuread_conditional_access_policy` resource:

```hcl
resource "azuread_conditional_access_policy" "require_mfa" {
  display_name = "CA001-Require-MFA-AllUsers"
  state        = "enabledForReportingButNotEnforced"

  conditions {
    users {
      included_users = ["All"]
      excluded_users = [azuread_user.breakglass1.object_id, azuread_user.breakglass2.object_id]
    }
    applications {
      included_applications = ["All"]
    }
    client_app_types = ["all"]
  }

  grant_controls {
    operator          = "OR"
    built_in_controls = ["mfa"]
  }
}
```

---

## 8. Security Baseline

### 8.1 Zero Trust Principles Applied

| Principle | Implementation |
|-----------|---------------|
| **Verify explicitly** | Conditional Access evaluates user, device, location, risk on every access |
| **Use least privilege** | PIM for JIT admin access, scoped role assignments, MI with minimal RBAC |
| **Assume breach** | ID Protection risk detection, continuous access evaluation (CAE), audit logging |

### 8.2 Authentication Methods (Priority Order)

1. **Passkeys / FIDO2 security keys** -- phishing-resistant, strongest
2. **Microsoft Authenticator (push + number matching)** -- phishing-resistant
3. **Windows Hello for Business** -- device-bound biometric
4. **Certificate-based authentication** -- strong, enterprise
5. **OATH hardware tokens** -- legacy but acceptable
6. **SMS / Voice** -- weakest, avoid if possible

### 8.3 Privileged Identity Management (PIM) Best Practices

| Rule | Detail |
|------|--------|
| Max 5 permanent Global Admins | 2 break-glass + up to 3 operational (prefer 0 operational permanent) |
| All privileged roles via PIM | Eligible assignment, not permanent (except break-glass) |
| Require approval for Global Admin activation | At least 1 approver outside the admin team |
| Require MFA for all role activations | Enforced by PIM role settings |
| Maximum activation duration: 8 hours | Forces re-justification |
| Access reviews for privileged roles | Quarterly, auto-remove if not renewed |

### 8.4 Monitoring and Audit

| Signal | Where | Alert |
|--------|-------|-------|
| Sign-in logs | Entra admin center > Monitoring > Sign-in logs | High-risk sign-ins |
| Audit logs | Entra admin center > Monitoring > Audit logs | Privileged role changes |
| PIM activation logs | Entra admin center > ID Governance > PIM > Audit | Unusual activations |
| Service principal sign-ins | Entra admin center > Monitoring > Sign-in logs (Service principal tab) | Credential leak |
| Diagnostic settings | Stream to Log Analytics / SIEM | All of above + custom alerts |

**Recommended Azure Monitor Alert Rules**:
- Global Admin role activated outside business hours
- New app registration with high-privilege permissions
- Conditional Access policy modified or disabled
- Break-glass account sign-in (any occurrence)
- Bulk user creation or deletion
- Service principal credential added

### 8.5 Security Defaults vs Conditional Access

| Feature | Security Defaults (Free) | Conditional Access (P1+) |
|---------|-------------------------|--------------------------|
| MFA for admins | Yes | Yes (customizable) |
| MFA for all users | Yes (on demand) | Yes (granular control) |
| Block legacy auth | Yes | Yes |
| Risk-based policies | No | Yes (P2) |
| Named locations | No | Yes |
| Device compliance | No | Yes |
| App-specific policies | No | Yes |
| Report-only mode | No | Yes |
| Custom controls | No | Yes |

**Recommendation**: Use Conditional Access (requires P1). Security Defaults is a good starting point but too inflexible for enterprise use.

---

## 9. Licensing Reference

### 9.1 Feature-to-License Mapping

| Feature | Free | P1 | P2 | Governance | Suite |
|---------|------|----|----|------------|-------|
| SSO (unlimited apps) | Yes | Yes | Yes | Yes | Yes |
| MFA (Security Defaults) | Yes | Yes | Yes | Yes | Yes |
| Conditional Access | - | Yes | Yes | Yes | Yes |
| Custom roles | - | Yes | Yes | Yes | Yes |
| Role-assignable groups | - | Yes | Yes | Yes | Yes |
| Dynamic groups | - | Yes | Yes | Yes | Yes |
| ID Protection (risk) | - | - | Yes | Yes | Yes |
| PIM | - | - | Yes | Yes | Yes |
| Access reviews | - | - | Yes | Yes | Yes |
| Entitlement management | - | - | - | Yes | Yes |
| Lifecycle workflows | - | - | - | Yes | Yes |
| Private Access (ZTNA) | - | - | - | - | Yes |
| Internet Access (SWG) | - | - | - | - | Yes |

### 9.2 License Included With

- **Microsoft 365 Business Premium**: Includes Entra ID P1 + Conditional Access
- **Microsoft 365 E3**: Includes Entra ID P1
- **Microsoft 365 E5**: Includes Entra ID P2
- **Enterprise Mobility + Security E3**: Includes Entra ID P1
- **Enterprise Mobility + Security E5**: Includes Entra ID P2
- **Standalone**: Entra ID P1 ($6/user/month), P2 ($9/user/month)

### 9.3 IPAI Recommendation

Given the current M365 Business Premium license:
- **Entra ID P1 is included** -- Conditional Access, custom roles, dynamic groups available
- **P2 features** (PIM, ID Protection, access reviews) require upgrade or standalone add-on
- **ID Governance** requires separate license for entitlement management, lifecycle workflows
- **Workload ID** license needed for Conditional Access on service principals (optional, can defer)

---

## Sources

### Core Documentation
- [What is Microsoft Entra?](https://learn.microsoft.com/en-us/entra/fundamentals/what-is-entra)
- [What is application management?](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/what-is-application-management)
- [Managed identities overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Microsoft identity platform overview](https://learn.microsoft.com/en-us/entra/identity-platform/v2-overview)
- [Conditional Access overview](https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview)
- [MFA overview](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-mfa-howitworks)
- [RBAC overview](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/custom-overview)
- [Hybrid identity](https://learn.microsoft.com/en-us/entra/identity/hybrid/whatis-hybrid-identity)
- [Verified ID overview](https://learn.microsoft.com/en-us/entra/verified-id/decentralized-identifier-overview)
- [ID Governance overview](https://learn.microsoft.com/en-us/entra/id-governance/identity-governance-overview)
- [Workload identities overview](https://learn.microsoft.com/en-us/entra/workload-id/workload-identities-overview)
- [External ID overview](https://learn.microsoft.com/en-us/entra/external-id/external-identities-overview)

### Integration Guides
- [ACA + Entra ID authentication](https://learn.microsoft.com/en-us/azure/container-apps/authentication-entra)
- [Plan app migration to Entra ID](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/migrate-adfs-apps-phases-overview)
- [Apps and service principals](https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals)
- [PostgreSQL Entra authentication](https://learn.microsoft.com/en-us/azure/postgresql/security/security-entra-concepts)
- [PostgreSQL managed identity connection](https://learn.microsoft.com/en-us/azure/postgresql/security/security-connect-with-managed-identity)
- [Databricks SCIM provisioning](https://learn.microsoft.com/en-us/azure/databricks/admin/users-groups/scim/aad)
- [Superset Entra ID OAuth2 login](https://learn.microsoft.com/en-us/azure/hdinsight-aks/trino/configure-azure-active-directory-login-for-superset)
- [Configure OIDC SSO](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/add-application-portal-setup-oidc-sso)
- [SAML-based SSO configuration](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/migrate-adfs-saml-based-sso)

### Security and Governance
- [PIM overview](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)
- [PIM deployment plan](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-deployment-plan)
- [Best practices for Entra roles](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/best-practices)
- [Zero Trust identity](https://learn.microsoft.com/en-us/security/zero-trust/deploy/identity)
- [Graph API permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference)

### IaC
- [Terraform AzureAD provider](https://registry.terraform.io/providers/hashicorp/azuread/latest/docs)
- [Terraform azuread_application](https://registry.terraform.io/providers/hashicorp/azuread/latest/docs/resources/application)
- [Terraform azuread_service_principal](https://registry.terraform.io/providers/hashicorp/azuread/latest/docs/resources/service_principal)
- [Terraform azuread_application_federated_identity_credential](https://registry.terraform.io/providers/hashicorp/azuread/latest/docs/resources/application_federated_identity_credential)
