# InsightPulse AI — Access Model

> **Version:** 1.0.0 | **Last Updated:** 2026-03-18 | **Owner:** Jake Tolentino
> **Tenant:** `ceoinsightpulseai.onmicrosoft.com` (`402de71a-87ec-4302-a609-fb76098d1da7`)
> **Domain:** `insightpulseai.com` (verified, default)
> **Architecture:** Six-plane Azure-first
>
> Machine-readable SSOT: `ssot/security/` directory
> Cross-references:
> - `ssot/architecture/platform-boundaries.yaml`
> - `ssot/architecture/data-flows.yaml`
> - `infra/entra/app-roles-manifest.json`
> - `infra/entra/role-tool-mapping.yaml`
> - `spec/wholesale-saas-erp-azure/constitution.md`

---

## 1. Executive Summary

This document defines the complete identity, access, RBAC, authentication, and authorization model for the InsightPulse AI platform. The model governs six architectural planes, three truth authorities, and seven canonical systems across a single Azure subscription (`536d8cf6-89e1-4815-aef3-d5f2c5f4d070`).

The current operating model has one accountable human (platform owner) with delegated maker/judge agents. The access model is designed for this reality while encoding clean separation of duties that scales to a small team without refactoring.

Key design decisions:

- **Entra ID is the canonical identity plane.** Keycloak (`ipai-auth-dev`) is transitional. All new integrations federate to Entra.
- **Managed Identity first** for all Azure workloads. No long-lived secrets for service-to-service auth.
- **15 application roles** already defined in the Entra app registration. This model maps those to Entra groups, Azure RBAC, and per-system authorization.
- **Emergency access** via two cloud-only Global Admin accounts with phishing-resistant MFA.
- **No broad Owner/Global Admin sprawl.** The platform owner operates day-to-day as a scoped admin, escalating only when needed.

---

## 2. Assumptions and Scope

### In Scope

- All six architectural planes (governance, identity, business, data intelligence, agent/AI, experience)
- All three environments (dev, staging, prod)
- All canonical systems: Odoo CE 19, Databricks, Foundry, Azure DevOps, GitHub, APIM, Key Vault
- Human and workload identities
- Application-level authorization (Odoo RBAC, Databricks ACLs, Unity Catalog, Foundry permissions)
- Four target verticals: marketing, retail media, entertainment, financial services

### Out of Scope

- Detailed Odoo module-level permission XML (handled per-module in `addons/ipai/`)
- Network security rules (NSGs, VNet peering) — covered by `infra/` IaC
- Detailed Key Vault access policies — covered by `infra/keyvault/`
- End-user onboarding UX flows

### Assumptions

1. **Entra ID Free tier** (M365 Business Premium not yet redeemed). Conditional Access, PIM, and Access Reviews require P1/P2 and are marked as target-state.
2. **One human operator** today. The model uses Entra groups for future team scaling.
3. **Security Defaults are disabled.** This is a risk — re-enable or deploy Conditional Access when P1 is available.
4. **Keycloak is transitional.** No new integrations should federate to Keycloak. Migration gates defined in section 14.

---

## 3. Identity Classes

The platform recognizes four identity classes. Every principal must belong to exactly one class.

| Class | Description | Entra Object Type | Auth Method | Lifecycle |
|-------|-------------|-------------------|-------------|-----------|
| **Human — Internal** | Platform team members with `@insightpulseai.com` mailboxes | Member user | Entra ID + MFA (phishing-resistant target) | HR-driven provisioning |
| **Human — External** | Partners, contractors, client stakeholders | Guest user (`#EXT#`) | Entra B2B + home tenant MFA | Sponsor-driven, time-bounded |
| **Workload — Managed** | Azure services authenticating to other Azure services | User-assigned Managed Identity | Token from IMDS (no secret) | Terraform/IaC lifecycle |
| **Workload — App** | CI/CD pipelines, GitHub Actions, external SaaS | Service Principal + Federated Credential | Workload Identity Federation (no secret) | Pipeline/IaC lifecycle |

### Current Principals

| Principal | Class | Entra UPN / Object | Status |
|-----------|-------|---------------------|--------|
| `admin@insightpulseai.com` | Human — Internal | Member, Global Admin | Active (native cloud-only) |
| `emergency-admin@insightpulseai.com` | Human — Internal | Member, Global Admin | Active (break-glass) |
| `ceo@insightpulseai.com` | Human — External | Guest (`#EXT#`), Global Admin | Active (daily operator) |
| `id-ipai-agents-dev` | Workload — Managed | User-assigned MI, `rg-ipai-shared-dev` | Active |
| `id-ipai-aca-dev` | Workload — Managed | User-assigned MI, `rg-ipai-agents-dev` | Active |
| `id-ipai-databricks-dev` | Workload — Managed | User-assigned MI, `rg-ipai-ai-dev` | Active |
| `dbmanagedidentity` | Workload — Managed | User-assigned MI, `rg-dbw-managed-ipai-dev` | Active |
| `InsightPulse AI - Odoo ERP` | Workload — App | App Registration `3605a67d-7135-44a0-8640-03a9b4225923` | Active |
| `sc-azure-dev-platform` | Workload — App | Service Connection (WIF) | Active |
| `sc-azure-dev-lakehouse` | Workload — App | Service Connection (WIF) | Active |

---

## 4. Human Role Catalog

### 4.1 Platform Owner

| Attribute | Value |
|-----------|-------|
| **Purpose** | Single accountable human for all platform decisions |
| **Current holder** | `ceo@insightpulseai.com` (guest) / `admin@insightpulseai.com` (native) |
| **Scope** | All planes, all environments, all systems |
| **Allowed** | Full Azure RBAC, Entra admin, DevOps org admin, GitHub org owner, Databricks workspace admin, Foundry admin, Odoo Settings access, Key Vault admin, APIM admin |
| **Prohibited** | Using Global Admin for daily operations (use scoped roles instead); deploying without pipeline; modifying OCA source |
| **Day-to-day role** | Operates as scoped admin; escalates to Global Admin only for identity policy changes |
| **Target state** | Moves from Global Admin daily use to PIM-eligible just-in-time elevation (requires P2) |

### 4.2 Emergency Admin

| Attribute | Value |
|-----------|-------|
| **Purpose** | Break-glass access when primary admin is locked out |
| **Holders** | `admin@insightpulseai.com`, `emergency-admin@insightpulseai.com` |
| **Scope** | Entra ID Global Admin, Azure subscription Owner |
| **Allowed** | Password reset, Conditional Access override, subscription recovery |
| **Prohibited** | Daily operations, code deployment, data access |
| **Auth** | Cloud-only accounts, FIDO2 security key (target), password + MFA (current) |
| **Monitoring** | Sign-in alerts, audit log forwarding to Log Analytics |

### 4.3 Developer / Engineer (future)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Build, test, deploy platform features |
| **Scope** | Dev environment full access; staging read + deploy; prod deploy via pipeline only |
| **Allowed** | GitHub repo write, DevOps pipeline run, dev RG Contributor, Databricks dev workspace user, Key Vault Secret User (dev only) |
| **Prohibited** | Prod direct access, Global Admin, identity policy changes, Key Vault admin, Odoo prod Settings |

### 4.4 Data Engineer (future)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Build and maintain ETL pipelines, lakehouse schemas |
| **Scope** | Databricks workspace, ADLS, Unity Catalog |
| **Allowed** | Databricks SQL/notebook execution, Unity Catalog schema management, ADLS read/write (bronze/silver/gold), dbt model authoring |
| **Prohibited** | Odoo direct database access, Key Vault admin, identity policy changes, prod Odoo Settings |

### 4.5 Finance Operator (future)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Execute financial close, manage invoices, BIR compliance |
| **Scope** | Odoo finance modules, finance dashboards |
| **Allowed** | Odoo Invoicing/Accounting user, finance close operations, BIR filing, finance dashboard viewing |
| **Prohibited** | Settings access, user management, code deployment, Databricks admin, infrastructure changes |

### 4.6 Analyst / Viewer (future)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Consume dashboards, reports, and analytics outputs |
| **Scope** | BI surfaces, Databricks SQL (read-only), Odoo read-only |
| **Allowed** | Dashboard viewing, SQL query execution (gold layer), Odoo record read |
| **Prohibited** | Any write operation, settings access, infrastructure access |

### 4.7 Client Stakeholder (future, external)

| Attribute | Value |
|-----------|-------|
| **Purpose** | External client accessing their vertical's data |
| **Scope** | Single vertical, read-only, scoped to their tenant/company |
| **Allowed** | Vertical-specific dashboards, exported reports |
| **Prohibited** | Cross-vertical access, any write, infrastructure, settings |

---

## 5. Entra Group Design

Groups follow a naming convention: `sg-ipai-{scope}-{role}` for security groups, `rl-ipai-{scope}-{role}` for role-assignable groups.

| Group Name | Type | Role-Assignable | Purpose | Initial Members |
|------------|------|-----------------|---------|----------------|
| `sg-ipai-platform-owners` | Security | Yes | Platform owner role — full admin | `admin@insightpulseai.com`, `ceo@insightpulseai.com` |
| `sg-ipai-emergency-admins` | Security | Yes | Break-glass accounts | `admin@insightpulseai.com`, `emergency-admin@insightpulseai.com` |
| `sg-ipai-developers` | Security | No | Engineers — dev full, staging deploy, prod pipeline | (empty — future) |
| `sg-ipai-data-engineers` | Security | No | Databricks + ADLS operators | (empty — future) |
| `sg-ipai-finance-operators` | Security | No | Odoo finance close + BIR | (empty — future) |
| `sg-ipai-analysts` | Security | No | Read-only BI consumers | (empty — future) |
| `sg-ipai-vertical-marketing` | Security | No | Marketing vertical access | (empty — future) |
| `sg-ipai-vertical-retail-media` | Security | No | Retail media vertical access | (empty — future) |
| `sg-ipai-vertical-entertainment` | Security | No | Entertainment vertical access | (empty — future) |
| `sg-ipai-vertical-finserv` | Security | No | Financial services vertical access | (empty — future) |
| `sg-ipai-workload-agents` | Security | No | Managed identities for agent workloads | `id-ipai-agents-dev` |
| `sg-ipai-workload-aca` | Security | No | Managed identities for Container Apps | `id-ipai-aca-dev` |
| `sg-ipai-workload-databricks` | Security | No | Managed identities for Databricks | `id-ipai-databricks-dev`, `dbmanagedidentity` |
| `sg-ipai-workload-cicd` | Security | No | Service principals for CI/CD | `sc-azure-dev-platform`, `sc-azure-dev-lakehouse` |
| `sg-ipai-app-copilot-advisory` | Security | No | App role: `copilot.advisory` | (dynamic — assigned via app role) |
| `sg-ipai-app-copilot-action` | Security | No | App role: `copilot.action` | (dynamic — assigned via app role) |
| `sg-ipai-app-ops-admin` | Security | No | App role: `ops.admin` | `sg-ipai-platform-owners` (nested) |

Machine-readable SSOT: `ssot/security/entra_groups.yaml`

---

## 6. Azure RBAC Matrix by Scope

### 6.1 Subscription Level (`536d8cf6-89e1-4815-aef3-d5f2c5f4d070`)

| Principal / Group | Role | Justification |
|-------------------|------|---------------|
| `sg-ipai-emergency-admins` | Owner | Break-glass recovery |
| `sg-ipai-platform-owners` | Contributor + User Access Administrator | Day-to-day operations without Owner sprawl |
| `sg-ipai-workload-cicd` | Reader | Pipeline resource discovery |

### 6.2 Resource Group Level

| Resource Group | Principal / Group | Role | Justification |
|---------------|-------------------|------|---------------|
| `rg-ipai-dev` | `sg-ipai-platform-owners` | Contributor | Odoo, Plane, Shelf, CRM management |
| `rg-ipai-dev` | `sg-ipai-developers` | Contributor | Dev environment full access |
| `rg-ipai-dev` | `sg-ipai-workload-aca` | Contributor | Container Apps self-management |
| `rg-ipai-dev` | `sg-ipai-workload-cicd` | Contributor | Pipeline deployments |
| `rg-ipai-ai-dev` | `sg-ipai-platform-owners` | Contributor | AI/ML resource management |
| `rg-ipai-ai-dev` | `sg-ipai-data-engineers` | Contributor | Databricks, ADLS, AI services |
| `rg-ipai-ai-dev` | `sg-ipai-workload-databricks` | Contributor | Databricks managed identity access |
| `rg-ipai-agents-dev` | `sg-ipai-platform-owners` | Contributor | Agent runtime management |
| `rg-ipai-agents-dev` | `sg-ipai-workload-agents` | Contributor | Agent workload self-management |
| `rg-ipai-shared-dev` | `sg-ipai-platform-owners` | Contributor | Shared services management |
| `rg-ipai-shared-dev` | `sg-ipai-developers` | Reader | Observability access |
| `rg-ipai-devops` | `sg-ipai-platform-owners` | Contributor | DevOps pool management |
| `rg-ipai-data-dev` | `sg-ipai-platform-owners` | Contributor | Platform data management |
| `rg-ipai-data-dev` | `sg-ipai-data-engineers` | Reader | Read access to platform DB config |
| `rg-dbw-managed-ipai-dev` | `sg-ipai-workload-databricks` | Contributor | Databricks managed resources |
| `rg-data-intel-ph` | `sg-ipai-platform-owners` | Contributor | AI Foundry management |

### 6.3 Resource-Level RBAC

| Resource | Principal / Group | Role | Justification |
|----------|-------------------|------|---------------|
| `kv-ipai-dev` | `sg-ipai-platform-owners` | Key Vault Administrator | Full secret management |
| `kv-ipai-dev` | `sg-ipai-developers` | Key Vault Secrets User | Read secrets for dev |
| `kv-ipai-dev` | `sg-ipai-workload-aca` | Key Vault Secrets User | Runtime secret access |
| `kv-ipai-dev` | `sg-ipai-workload-agents` | Key Vault Secrets User | Agent secret access |
| `kv-ipai-dev` | `sg-ipai-workload-cicd` | Key Vault Secrets User | Pipeline secret access |
| `ipai-odoo-dev-kv` | `sg-ipai-platform-owners` | Key Vault Administrator | Odoo secret management |
| `ipai-odoo-dev-kv` | `sg-ipai-workload-aca` | Key Vault Secrets User | Odoo runtime secrets |
| `stipaidevlake` | `sg-ipai-data-engineers` | Storage Blob Data Contributor | ADLS read/write |
| `stipaidevlake` | `sg-ipai-workload-databricks` | Storage Blob Data Contributor | Databricks ADLS access |
| `stipaidevlake` | `sg-ipai-analysts` | Storage Blob Data Reader | Read-only gold layer |
| `cripaidev` | `sg-ipai-platform-owners` | AcrPush | Image push |
| `cripaidev` | `sg-ipai-workload-cicd` | AcrPush | Pipeline image push |
| `cripaidev` | `sg-ipai-workload-aca` | AcrPull | Container image pull |
| `appi-ipai-dev` | `sg-ipai-developers` | Monitoring Reader | Telemetry access |
| `appi-ipai-dev` | `sg-ipai-platform-owners` | Monitoring Contributor | Telemetry management |

Machine-readable SSOT: `ssot/security/azure_rbac_matrix.yaml`

---

## 7. Application Authorization Matrix

### 7.1 Odoo CE 19

Odoo uses its native RBAC model. Entra ID federates via OIDC (`ipai_auth_oidc` module). Group membership in Odoo maps from Entra claims.

| Odoo Group | Entra Group / App Role | Permissions |
|------------|----------------------|-------------|
| Administration / Settings | `sg-ipai-platform-owners` | Full Settings access, module install, user management |
| Accounting / Adviser | `finance.close.approver` | Journal entries, reconciliation, financial reports, approval |
| Accounting / Billing | `finance.close.operator` | Invoice creation, payment registration, close tasks |
| Accounting / Read-only | `finance.viewer` | Financial report viewing only |
| Sales / User | `retail.operator` | Sales order management, inventory |
| Marketing / User | `marketing.manager` | Campaign management |
| Project / User | `ops.admin` | Project and task management |
| Website / Restricted Editor | `product.operator` | Product catalog management |

**Prohibited**: No user should have both `Administration / Settings` and `Accounting / Adviser` in production (separation of duties for system config vs financial operations).

### 7.2 Azure Databricks (`dbw-ipai-dev`)

| Databricks Permission | Entra Group | Access Level |
|-----------------------|-------------|--------------|
| Workspace Admin | `sg-ipai-platform-owners` | Full workspace management |
| Can Manage (clusters) | `sg-ipai-data-engineers` | Create/manage compute |
| Can Use (SQL warehouses) | `sg-ipai-analysts` | Run SQL queries |
| Can Edit (notebooks) | `sg-ipai-data-engineers` | Author notebooks/jobs |
| Can View (dashboards) | `sg-ipai-analysts` | View dashboards only |

**Unity Catalog Grants:**

| Catalog/Schema | Principal | Grant |
|---------------|-----------|-------|
| `ipai_dev.bronze` | `sg-ipai-data-engineers` | ALL PRIVILEGES |
| `ipai_dev.silver` | `sg-ipai-data-engineers` | ALL PRIVILEGES |
| `ipai_dev.gold` | `sg-ipai-data-engineers` | ALL PRIVILEGES |
| `ipai_dev.gold` | `sg-ipai-analysts` | SELECT |
| `ipai_dev.gold` | `sg-ipai-workload-agents` | SELECT |
| `ipai_dev.ai` | `sg-ipai-data-engineers` | ALL PRIVILEGES |
| `ipai_dev.ai` | `sg-ipai-workload-agents` | SELECT |

### 7.3 Microsoft Foundry (`data-intel-ph-resource`)

| Foundry Role | Entra Group | Permissions |
|-------------|-------------|-------------|
| AI Project Owner | `sg-ipai-platform-owners` | Full project management, model deployment, evaluation config |
| AI Project Contributor | `sg-ipai-data-engineers` | Model training, prompt authoring, evaluation runs |
| AI Project Reader | `sg-ipai-analysts` | View traces, evaluation results, model metrics |
| Agent Runtime | `sg-ipai-workload-agents` | Execute agent tool calls, access serving endpoints |

### 7.4 Azure DevOps (`insightpulseai` org)

| DevOps Role | Entra Group | Scope |
|-------------|-------------|-------|
| Project Collection Admin | `sg-ipai-platform-owners` | Org-level administration |
| Project Admin (`ipai-platform`) | `sg-ipai-platform-owners` | Project settings, service connections |
| Build Admin | `sg-ipai-developers` | Pipeline creation and management |
| Contributors | `sg-ipai-developers` | Work item edit, repo access, pipeline run |
| Readers | `sg-ipai-analysts` | Board viewing, pipeline status |
| Environment Approver (staging) | `sg-ipai-platform-owners` | Manual approval gate |
| Environment Approver (prod) | `sg-ipai-platform-owners` | Manual approval gate |

**Service Connections:**

| Connection | Auth | Scope | Approvers |
|-----------|------|-------|-----------|
| `sc-azure-dev-platform` | Workload Identity Federation | `rg-ipai-dev`, `rg-ipai-shared-dev` | `sg-ipai-platform-owners` |
| `sc-azure-dev-lakehouse` | Workload Identity Federation | `rg-ipai-ai-dev`, `rg-ipai-data-dev` | `sg-ipai-platform-owners` |

### 7.5 GitHub (`Insightpulseai` org)

| GitHub Role | Entra Group Mapping | Permissions |
|-------------|-------------------|-------------|
| Org Owner | `sg-ipai-platform-owners` | Full org administration |
| Repo Admin (`odoo`) | `sg-ipai-platform-owners` | Branch protection, settings |
| Repo Write (`odoo`) | `sg-ipai-developers` | Push, PR creation, merge |
| Repo Read (`odoo`) | `sg-ipai-analysts` | Clone, view |
| GitHub Actions | `sg-ipai-workload-cicd` | Workflow execution |

**Branch Protection (`main`):**
- Required reviewers: 1 (from `sg-ipai-platform-owners` or CODEOWNERS)
- Required status checks: lint, typecheck, test, security scan
- No force push
- No deletion

### 7.6 Azure API Management (target)

| APIM Role | Entra Group | Permissions |
|-----------|-------------|-------------|
| Service Admin | `sg-ipai-platform-owners` | API definitions, policies, subscriptions |
| API Developer | `sg-ipai-developers` | API testing, dev portal |
| API Consumer (agents) | `sg-ipai-workload-agents` | Invoke APIs within rate limits |
| API Consumer (copilot) | App role `copilot.action` | Invoke Odoo APIs via copilot context |

Machine-readable SSOT: `ssot/security/app_authorization_matrix.yaml`

---

## 8. Workload Identity Design

Every Azure service authenticates using managed identity. No long-lived secrets for service-to-service auth.

### 8.1 Managed Identity Inventory

| Identity | Type | Resource Group | Assigned To | Accesses |
|----------|------|---------------|-------------|----------|
| `id-ipai-agents-dev` | User-assigned | `rg-ipai-shared-dev` | Agent Container Apps in `cae-ipai-dev` | Key Vault secrets, ADLS gold (read), Azure OpenAI, Foundry endpoints |
| `id-ipai-aca-dev` | User-assigned | `rg-ipai-agents-dev` | Odoo Container Apps (`ipai-odoo-dev-web/cron/worker`) | Key Vault secrets (Odoo), ACR pull, PostgreSQL (via connection string in KV) |
| `id-ipai-databricks-dev` | User-assigned | `rg-ipai-ai-dev` | Databricks workspace `dbw-ipai-dev` | ADLS (`stipaidevlake`), Key Vault secrets, Unity Catalog |
| `dbmanagedidentity` | User-assigned | `rg-dbw-managed-ipai-dev` | Databricks managed services | Unity Catalog access connector to ADLS |

### 8.2 Service Principal Inventory

| Service Principal | Auth Method | Used By | Accesses |
|-------------------|-------------|---------|----------|
| `InsightPulse AI - Odoo ERP` | Client secret (migrate to WIF) | Odoo OIDC integration | Entra ID token issuance, app role claims |
| `sc-azure-dev-platform` | Workload Identity Federation | Azure DevOps pipeline | `rg-ipai-dev`, `rg-ipai-shared-dev` Contributor |
| `sc-azure-dev-lakehouse` | Workload Identity Federation | Azure DevOps pipeline | `rg-ipai-ai-dev`, `rg-ipai-data-dev` Contributor |

### 8.3 Identity Flow Diagram

```
Human (Entra ID) ──OIDC──► Odoo CE 19 (ipai_auth_oidc)
Human (Entra ID) ──SSO───► Databricks (workspace login)
Human (Entra ID) ──SSO───► Azure DevOps (org login)
Human (Entra ID) ──SSO───► Azure Portal (subscription access)

id-ipai-aca-dev ──MI token──► Key Vault (secret read)
id-ipai-aca-dev ──MI token──► ACR (image pull)

id-ipai-agents-dev ──MI token──► Key Vault (secret read)
id-ipai-agents-dev ──MI token──► Azure OpenAI (inference)
id-ipai-agents-dev ──MI token──► ADLS gold (data read)
id-ipai-agents-dev ──MI token──► APIM (API invoke)

id-ipai-databricks-dev ──MI token──► ADLS (read/write)
id-ipai-databricks-dev ──MI token──► Key Vault (secret read)

dbmanagedidentity ──MI token──► ADLS via Unity Catalog connector

sc-azure-dev-* ──WIF token──► Azure RM (deployment)
```

Machine-readable SSOT: `ssot/security/workload_identities.yaml`

---

## 9. Environment and Plane Separation

### 9.1 Environment Model

| Environment | Azure Resources | Approval Gate | Human Access | Data Classification |
|-------------|----------------|---------------|--------------|---------------------|
| **Dev** | `*-dev` suffix resources | Automatic on push to `main` | Full (developers, platform owners) | Synthetic/anonymized |
| **Staging** | `*-staging` suffix (planned) | Manual approval by `sg-ipai-platform-owners` | Read + deploy (platform owners) | Anonymized prod copy |
| **Prod** | `*-prod` suffix (planned) | Manual approval by `sg-ipai-platform-owners` | Pipeline-only deploy; read via Databricks SQL | Real business data |

### 9.2 Plane x Environment Matrix

| Plane | Dev Resources | Staging Resources | Prod Resources |
|-------|--------------|-------------------|----------------|
| 1. Governance | Azure Boards (shared), GitHub (shared), ADO pipelines | Same (env-scoped) | Same (env-scoped) |
| 2. Identity/Security | `kv-ipai-dev`, Entra ID (shared), AFD (shared) | `kv-ipai-staging` | `kv-ipai-prod` |
| 3. Business Systems | `ipai-odoo-dev-web/cron/worker`, `ipai-odoo-dev-pg` | `ipai-odoo-staging-*` | `ipai-odoo-prod-*` |
| 4. Data Intelligence | `dbw-ipai-dev`, `stipaidevlake` | `dbw-ipai-staging`, `stipaistagingake` | `dbw-ipai-prod`, `stipaiprodlake` |
| 5. Agent/AI | `oai-ipai-dev`, `data-intel-ph-resource` | Shared (region-scoped) | Dedicated endpoints |
| 6. Experience | Ops console (dev), Slack (shared) | Staging preview | Production surfaces |

### 9.3 Cross-Environment Rules

- **No prod secrets in dev.** Key Vaults are environment-scoped.
- **No dev data in prod.** ETL pipelines are environment-aware.
- **Pipeline promotion only.** Code moves dev -> staging -> prod via Azure Pipelines. No manual deployment.
- **Environment-scoped service connections.** `sc-azure-dev-platform` cannot access staging/prod resources.

---

## 10. Vertical Capability Permission Model

The platform serves four target verticals. Each vertical gets an Entra group and a scoped set of app roles. Vertical groups are additive — a user can belong to multiple verticals.

### 10.1 Vertical x App Role Matrix

| App Role | Marketing | Retail Media | Entertainment | Financial Services |
|----------|-----------|-------------|--------------|-------------------|
| `product.viewer` | Yes | Yes | Yes | Yes |
| `product.operator` | No | Yes | No | No |
| `finance.viewer` | Yes | Yes | Yes | Yes |
| `finance.close.operator` | No | No | No | Yes |
| `finance.close.approver` | No | No | No | Yes |
| `marketing.manager` | Yes | No | Yes | No |
| `marketing.viewer` | Yes | Yes | Yes | No |
| `media.ops` | No | Yes | Yes | No |
| `retail.operator` | No | Yes | No | No |
| `analytics.viewer` | Yes | Yes | Yes | Yes |
| `analytics.admin` | No | No | No | No |
| `copilot.advisory` | Yes | Yes | Yes | Yes |
| `copilot.action` | No | No | No | No |
| `ops.admin` | No | No | No | No |
| `ops.viewer` | Yes | Yes | Yes | Yes |

### 10.2 Cross-Vertical Isolation

- **Unity Catalog**: Each vertical gets a schema namespace (`gold.marketing_*`, `gold.retail_*`, `gold.entertainment_*`, `gold.finserv_*`). Vertical groups have SELECT only on their namespace.
- **Odoo**: Multi-company model. Each vertical maps to an Odoo company. Record rules enforce company-scoped access.
- **APIM**: API subscriptions are vertical-scoped. Rate limits and allowed endpoints differ per vertical.
- **Dashboards**: Databricks dashboards use row-level security via Unity Catalog grants.

### 10.3 Anti-Pattern: Cross-Vertical Leakage

A user in `sg-ipai-vertical-marketing` must NOT see `gold.finserv_*` data. Enforcement points:

1. Unity Catalog GRANT — no SELECT on other vertical schemas
2. Odoo company_id record rules — Odoo enforces company isolation
3. APIM subscription scope — API keys are vertical-bound
4. Databricks row-level security — dashboard queries filtered by group membership

---

## 11. Separation of Duties

### 11.1 SoD Matrix

| Action | Authorized Role | Prohibited Role | Approval Required |
|--------|----------------|-----------------|-------------------|
| Deploy to production | `sg-ipai-platform-owners` (via pipeline) | Individual developer unilaterally | Yes — pipeline environment gate |
| Access prod data | Databricks SQL (read-only, gold layer) | Direct PostgreSQL access | No (read-only) |
| Manage secrets | `sg-ipai-platform-owners` (Key Vault Admin) | Developers, agents, CI/CD | No (but audited) |
| Change identity policy | Entra Global Admin (JIT via PIM — target) | Any non-admin | Yes — PIM activation (target) |
| Modify Azure Boards planned truth | `sg-ipai-platform-owners` | Agents, CI/CD pipelines | No (but audited) |
| Set agent policies | `sg-ipai-platform-owners` (Foundry Admin) | Agents themselves | No (but traced) |
| Approve financial close | `finance.close.approver` | `finance.close.operator` (same person) | Yes — Odoo approval workflow |
| Modify Odoo user permissions | Odoo Settings (`sg-ipai-platform-owners`) | Finance operators, analysts | No (but audited) |
| Push to `main` branch | `sg-ipai-platform-owners` / CODEOWNERS | Unreviewed contributors | Yes — PR review |
| Create/delete Entra groups | Entra Global Admin | Anyone else | No (but audited) |
| Modify Unity Catalog grants | Databricks workspace admin | Data engineers (target — catalog admin separation) | No (but audited) |

### 11.2 One-Person Team Accommodation

With one human operator, strict SoD is impractical for some actions. The model accommodates this by:

1. **Pipeline gates** enforce temporal separation — the same person deploys but must wait for CI checks.
2. **Audit logging** provides after-the-fact review capability.
3. **Separate accounts** for emergency vs daily operations.
4. **Agent judges** provide maker/checker pattern for routine operations (e.g., agent drafts, human approves).

When the team grows to 2+ humans, the following SoD pairs should be enforced:

- Identity policy admin != daily platform operator
- Financial close approver != financial close operator
- Code reviewer != code author (for production deployments)

Machine-readable SSOT: `ssot/security/separation_of_duties.yaml`

---

## 12. Emergency Access Model

### 12.1 Break-Glass Accounts

| Account | UPN | Type | MFA | Storage |
|---------|-----|------|-----|---------|
| Primary break-glass | `admin@insightpulseai.com` | Cloud-only member | Password + Authenticator (target: FIDO2) | Password in physical safe + Azure Key Vault `kv-ipai-prod` (target) |
| Secondary break-glass | `emergency-admin@insightpulseai.com` | Cloud-only member | Password + Authenticator (target: FIDO2) | Different physical location from primary |

### 12.2 Break-Glass Procedure

1. Attempt normal sign-in with `ceo@insightpulseai.com` first.
2. If locked out, use `admin@insightpulseai.com` from a known device.
3. If primary break-glass fails, use `emergency-admin@insightpulseai.com`.
4. After recovery: rotate break-glass passwords, review audit logs, file incident report.

### 12.3 Monitoring

- Sign-in events for break-glass accounts alert to Slack `#security-alerts` channel (via n8n + Azure Monitor).
- Target: Azure Monitor action group sends SMS + email on any break-glass sign-in.
- Break-glass accounts excluded from Conditional Access policies that could lock them out (when CA is deployed).

### 12.4 Current Risk: Security Defaults Disabled

Security Defaults are currently disabled. This means:
- MFA is not enforced for all users
- Legacy authentication protocols are not blocked
- Break-glass accounts may not require MFA

**Remediation**: Either re-enable Security Defaults or deploy Conditional Access (requires Entra ID P1). Until then, manually ensure all accounts have MFA configured.

---

## 13. Anti-Patterns and Risks

### 13.1 Current Risks

| Risk | Severity | Current State | Remediation |
|------|----------|--------------|-------------|
| `ceo@insightpulseai.com` is a guest with Global Admin | High | Active | Convert to member or remove GA; use scoped roles + PIM |
| Security Defaults disabled, no Conditional Access | High | Active | Redeem M365 Business Premium; deploy CA policies |
| M365 Business Premium not redeemed (Entra ID Free) | Medium | Active | Redeem license; enables CA, PIM, Access Reviews |
| Keycloak still active as IdP | Medium | Transitional | Complete Entra migration per gates in section 14 |
| No Conditional Access policies | High | Active | Deploy baseline CA policies after P1 license |
| Single ACR (`ipaiodoodevacr`) not consolidated | Low | Active | Migrate images to `cripaidev`; delete `ipaiodoodevacr` |
| `InsightPulse AI - Odoo ERP` app uses client secret | Medium | Active | Migrate to certificate or WIF |

### 13.2 Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Correct Approach |
|-------------|-------------|-----------------|
| Global Admin for daily operations | Overprivileged; audit noise; blast radius | Scoped roles (Contributor + UAA) + PIM for GA |
| Shared service principal secrets | Key rotation burden; blast radius | Managed Identity or Workload Identity Federation |
| Odoo admin password in environment variable | Leaked via container inspect | Key Vault secret reference |
| Direct PostgreSQL access from Databricks | Bypasses Odoo business logic; data authority violation | ETL via API extract to ADLS bronze |
| Agent with Key Vault Administrator | Agents should read secrets, not manage them | Key Vault Secrets User only |
| Single Entra group for all permissions | No granularity; can't revoke partial access | Role-specific groups per section 5 |
| Cross-environment secret sharing | Dev secrets in prod or vice versa | Environment-scoped Key Vaults |
| Guest user as sole Global Admin | Account dependent on external tenant | Cloud-only member accounts for admin |

---

## 14. Bootstrap-to-Target Transition Plan

### Phase 0: Current State (Now)

- Entra ID Free tier
- Security Defaults disabled
- `ceo@insightpulseai.com` (guest) as primary Global Admin
- No Conditional Access
- Keycloak active as transitional IdP
- 15 app roles defined but not yet assigned to groups

### Phase 1: Foundation Security (Week 1-2)

1. **Redeem M365 Business Premium** — enables Entra ID P1
2. **Re-enable Security Defaults** (or deploy baseline Conditional Access)
3. **Create Entra security groups** per section 5
4. **Assign Azure RBAC** per section 6
5. **Configure break-glass monitoring** — sign-in alerts to Slack

### Phase 2: Application Federation (Week 3-4)

1. **Deploy `ipai_auth_oidc`** — Odoo OIDC federation to Entra ID
2. **Assign app roles to groups** — map `sg-ipai-*` groups to app roles
3. **Configure Databricks SCIM** — sync Entra groups to Databricks
4. **Wire APIM to Entra** — OAuth2 validation on all API endpoints

### Phase 3: Keycloak Retirement (Week 5-8)

Migration gates — all must pass before deleting `ipai-auth-dev`:

| Gate | Test | Status |
|------|------|--------|
| OIDC/SAML parity | All apps authenticate via Entra | Pending |
| Group/role mapping | All Keycloak groups mapped to Entra groups | Pending |
| Service account replacement | All Keycloak service accounts replaced by MI/SP | Pending |
| Break-glass admin functional | Emergency accounts work without Keycloak | Pending |
| User provisioning automated | New users provisioned via Entra (not Keycloak) | Pending |
| Per-app cutover verified | Odoo, Superset, Plane, n8n, Shelf, CRM tested | Pending |

### Phase 4: Advanced Security (Week 9-12)

1. **Conditional Access policies** — MFA enforcement, device compliance, location-based
2. **PIM deployment** — JIT elevation for Global Admin
3. **Access Reviews** — quarterly review of group memberships
4. **Workload Identity migration** — replace Odoo app client secret with WIF

### Phase 5: Multi-Tenant Readiness (Future)

1. **Per-tenant Entra groups** (dynamic membership based on company attribute)
2. **Per-tenant Key Vault access policies**
3. **Per-tenant Unity Catalog schemas**
4. **Per-tenant APIM subscriptions**

---

## 15. Machine-Readable SSOT Artifacts

All machine-readable artifacts live in `ssot/security/`:

| File | Content |
|------|---------|
| `ssot/security/access_model.yaml` | Master access model — identity classes, role catalog, auth methods |
| `ssot/security/entra_groups.yaml` | Entra group definitions, members, role-assignable flags |
| `ssot/security/azure_rbac_matrix.yaml` | RBAC assignments by scope |
| `ssot/security/app_authorization_matrix.yaml` | Per-app role/permission matrix |
| `ssot/security/workload_identities.yaml` | Managed identities, service principals |
| `ssot/security/separation_of_duties.yaml` | SoD matrix |

Cross-referenced artifacts:

| File | Content |
|------|---------|
| `infra/entra/app-roles-manifest.json` | 15 Entra app role definitions |
| `infra/entra/role-tool-mapping.yaml` | Role-to-tool mapping for copilot context |
| `ssot/architecture/platform-boundaries.yaml` | Six-plane system assignments |
| `ssot/architecture/data-flows.yaml` | Data flow governance |

---

## 16. Recommended Repo/Docs Patch Set

The following changes should be applied to align the existing codebase with this access model:

### New files (created by this commit)

| Path | Purpose |
|------|---------|
| `docs/security/ACCESS_MODEL.md` | This document |
| `ssot/security/access_model.yaml` | Master access model SSOT |
| `ssot/security/entra_groups.yaml` | Entra group definitions |
| `ssot/security/azure_rbac_matrix.yaml` | Azure RBAC assignments |
| `ssot/security/app_authorization_matrix.yaml` | Application authorization |
| `ssot/security/workload_identities.yaml` | Workload identity inventory |
| `ssot/security/separation_of_duties.yaml` | SoD matrix |

### Future patches (not in this commit)

| Path | Change | Reason |
|------|--------|--------|
| `infra/entra/conditional-access-policies.json` | Create | Baseline CA policies (requires P1) |
| `infra/entra/pim-config.yaml` | Create | PIM role assignments (requires P2) |
| `addons/ipai/ipai_auth_oidc/` | Create | Odoo OIDC module for Entra federation |
| `ssot/architecture/platform-boundaries.yaml` | Update | Add identity/security system details |
| `.github/workflows/rbac-drift-check.yml` | Create | CI gate for RBAC drift detection |
| `docs/contracts/IDENTITY_CONTRACT.md` | Create | Cross-boundary identity contract |

---

*Last updated: 2026-03-18*
