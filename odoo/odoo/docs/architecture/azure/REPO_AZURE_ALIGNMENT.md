# Canonical Repo to Azure Alignment Matrix

> SSOT for mapping InsightPulseAI GitHub repositories to Azure resource groups,
> managed identities, and CI/CD ownership boundaries.
>
> Machine-readable twin: `ssot/governance/repo-azure-alignment.yaml`
>
> Last updated: 2026-03-14

---

## 1. Repo to Azure Resource Mapping

| # | Repo | Canonical Purpose | Azure Resource Family | Managed Identity | CI/CD Owner | Forbidden Overlap |
|---|------|-------------------|----------------------|------------------|-------------|-------------------|
| 1 | `odoo` | Odoo CE 19 ERP: modules, config, deployment | `rg-ipai-dev` (ipai-odoo-dev-web, ipai-odoo-dev-worker, ipai-odoo-dev-cron, ipaiodoodevacr, ipai-odoo-dev-pg) | `mi-ipai-odoo-dev` / `mi-ipai-odoo-prod` | GitHub Actions | Must not deploy non-Odoo containers; must not own Front Door config |
| 2 | `agents` | Agent runtime metadata, contracts, and orchestration definitions | `rg-ipai-agents-dev` (odoo-web, odoo-init job, vm-ipai-supabase-dev) | `id-ipai-agents-dev` | GitHub Actions | Must not contain plugin marketplace code or MCP server implementations |
| 3 | `ops-platform` | Platform operations: monitoring, alerting, runbooks, SRE tooling | `rg-ipai-shared-dev` (App Insights, WAF policies), `rg-ipai-devops` (ipai-devcenter, ipai-build-pool) | `mi-ipai-platform-dev` / `mi-ipai-platform-prod` | GitHub Actions | Must not own application container definitions; must not duplicate infra IaC |
| 4 | `infra` | IaC: Azure-native platform, Cloudflare DNS/edge, Terraform, Bicep | `rg-ipai-shared-dev` (Front Door ipai-fd-dev, Key Vaults), `rg-ipai-shared-prod`, `rg-ipai-shared-staging` | N/A (deploys identities, does not consume one) | GitHub Actions + Terraform Cloud | Must not contain application code or runtime configs |
| 5 | `web` | Public website and marketing (Next.js) | `rg-ipai-dev` (ipai-website-dev) | N/A (Vercel-hosted, Azure for preview only) | Vercel + GitHub Actions | Must not contain Odoo website modules or ERP views |
| 6 | `lakehouse` | Databricks lakehouse: medallion pipelines, notebooks, jobs, SQL, and analytics deployment assets | `rg-ipai-ai-dev` (dbw-ipai-dev, stipaidevlake), `rg-dbw-managed-ipai-dev` | `mi-ipai-lakehouse-dev` / `mi-ipai-lakehouse-prod` | GitHub Actions + Databricks Asset Bundles | Must not contain application containers; Databricks workspace is execution surface, this repo is Git SSOT |
| 7 | `automations` | n8n workflows, Supabase Edge Functions, webhook definitions | N/A (Supabase-hosted, n8n self-hosted) | N/A | GitHub Actions | Must not contain Odoo server actions or Databricks jobs |
| 8 | `.github` | Org-wide GitHub config: profile, default workflows, issue templates | N/A | N/A | N/A | Must not contain deployable code or IaC |
| 9 | `templates` | Cookiecutter/scaffolding templates for new repos and modules | N/A | N/A | N/A | Must not contain live infrastructure or deployable services |
| 10 | `design-system` | Shared UI components, tokens, and style guides | N/A | N/A | GitHub Actions (npm publish) | Must not contain backend logic or Azure resource definitions |

---

## 2. Azure Resource Group Inventory

### rg-ipai-dev (Application Runtime)

| Resource | Type | Owning Repo |
|----------|------|-------------|
| `ipai-odoo-dev-web` | Container App | `odoo` |
| `ipai-odoo-dev-worker` | Container App | `odoo` |
| `ipai-odoo-dev-cron` | Container App | `odoo` |
| `ipai-crm-dev` | Container App | `odoo` |
| `ipai-plane-dev` | Container App | `ops-platform` |
| `ipai-shelf-dev` | Container App | `ops-platform` |
| `ipai-auth-dev` | Container App | `infra` (Keycloak config) |
| `ipai-mcp-dev` | Container App | `agents` |
| `ipai-ocr-dev` | Container App | `agents` |
| `ipai-superset-dev` | Container App | `lakehouse` |
| `ipai-website-dev` | Container App | `web` |
| `ipaiwebacr` | Container Registry | `infra` |
| `ipaiodoodevacr` | Container Registry | `odoo` |
| `ipai-odoo-dev-pg` | PostgreSQL Flexible Server | `odoo` |

### rg-ipai-shared-dev (Shared Platform)

| Resource | Type | Owning Repo |
|----------|------|-------------|
| `ipai-fd-dev` | Front Door | `infra` |
| `kv-ipai-dev` | Key Vault | `infra` |
| App Insights | Monitoring | `ops-platform` |
| WAF Policy | Security | `infra` |
| `mi-ipai-platform-dev` | Managed Identity | `ops-platform` |
| `mi-ipai-lakehouse-dev` | Managed Identity | `lakehouse` |
| `mi-ipai-odoo-dev` | Managed Identity | `odoo` |
| `id-ipai-agents-dev` | Managed Identity | `agents` |

### rg-ipai-shared-prod / rg-ipai-shared-staging

| Resource | Type | Owning Repo |
|----------|------|-------------|
| `kv-ipai-prod` / `kv-ipai-staging` | Key Vault | `infra` |
| `mi-ipai-platform-*` | Managed Identity | `ops-platform` |
| `mi-ipai-odoo-*` | Managed Identity | `odoo` |
| `mi-ipai-lakehouse-*` | Managed Identity | `lakehouse` |

### rg-ipai-ai-dev (AI and Data)

| Resource | Type | Owning Repo |
|----------|------|-------------|
| `dbw-ipai-dev` | Databricks Workspace | `lakehouse` (execution surface) |
| `aifoundry-ipai-dev` | AI Foundry | `agents` |
| `proj-ipai-claude` | AI Foundry Project | `agents` |
| `oai-ipai-dev` | Azure OpenAI | `agents` |
| `docai-ipai-dev` | Document Intelligence | `agents` |
| `vision-ipai-dev` | Computer Vision | `agents` |
| `lang-ipai-dev` | Language Service | `agents` |
| `srch-ipai-dev` | AI Search | `agents` |
| `stipaidevlake` | Storage Account (Data Lake) | `lakehouse` |
| VNets / NSGs | Networking | `infra` |

### rg-ipai-data-dev

| Resource | Type | Owning Repo |
|----------|------|-------------|
| `pg-ipai-dev` | PostgreSQL | `infra` (provisioned), `ops-platform` (consumed) |

### rg-ipai-agents-dev

| Resource | Type | Owning Repo |
|----------|------|-------------|
| `odoo-web` | Container App | `agents` |
| `odoo-init` | Container App Job | `agents` |
| `vm-ipai-supabase-dev` | Virtual Machine | `automations` |
| `id-ipai-aca-dev` | Managed Identity | `agents` |

### rg-ipai-devops

| Resource | Type | Owning Repo |
|----------|------|-------------|
| `ipai-devcenter` | Dev Center | `ops-platform` |
| `ipai-build-pool` | Build Pool | `ops-platform` |

### rg-data-intel-ph

| Resource | Type | Owning Repo |
|----------|------|-------------|
| `data-intel-ph-resource` | AI Foundry | `lakehouse` |

### rg-dbw-managed-ipai-dev

Databricks-managed resources. Not directly owned by any repo -- managed by the Databricks control plane for `dbw-ipai-dev`.

---

## 3. Current vs Target Alignment

### Misalignments to Resolve

| Issue | Current State | Target State | Action |
|-------|--------------|--------------|--------|
| `rg-ipai-agents-dev` contains `odoo-web` | Container named `odoo-web` lives in agents RG | Rename to `ipai-agents-web` or migrate to `rg-ipai-dev` | Rename container app to avoid Odoo namespace confusion |
| Databricks workspace vs repo boundary | Notebooks may be edited in-workspace without Git sync | All notebooks, jobs, and pipelines authored in `lakehouse` repo, deployed via Databricks Asset Bundles | Enforce Repos integration + CI deployment |
| Front Door config split | Front Door IaC may exist in multiple repos | `infra` repo is sole owner of Front Door Bicep/Terraform | Audit and consolidate |
| Superset ownership | Superset container in `rg-ipai-dev` | Owning repo should be `lakehouse` (analytics surface) | Update CI/CD pipeline ownership |
| Key Vault access policies | May have ad-hoc access grants | Each managed identity gets least-privilege access via `infra` repo IaC | Audit KV access policies |

---

## 4. Repo Description Updates Required

| Repo | Current Description | Target Description |
|------|--------------------|--------------------|
| `infra` | IaC -- Azure, DigitalOcean, Cloudflare, Terraform, Bicep | IaC -- Azure-native platform, Cloudflare DNS/edge, Terraform, Bicep |
| `lakehouse` | Intelligence / Analytics pipelines (Databricks, Medallion) | Databricks lakehouse: medallion pipelines, notebooks, jobs, SQL, and analytics deployment assets |
| `agents` | (verify current) | Agent runtime metadata, contracts, and orchestration definitions (not plugin-era artifacts) |

DigitalOcean references must be removed. The platform is Azure-native. See deprecated items in project CLAUDE.md.

---

## 5. Archived Repos to Delete (Post-Salvage)

These repos are from a prior architecture era and must be archived then deleted after any useful artifacts are salvaged into their successor repos.

| Repo | Reason | Salvage Target |
|------|--------|----------------|
| `template-factory` | Superseded by `templates` repo | `templates` |
| `plugin-marketplace` | Plugin architecture abandoned | `agents` (contracts only) |
| `plugin-agents` | Merged into `agents` | `agents` |
| `learn` | No active use; internal docs moved to Notion | N/A |
| `mcp-core` | MCP coordination moved to `agents` + `ops-platform` | `agents` |

Process: (1) audit for unreplicated code, (2) copy to successor, (3) archive via GitHub settings, (4) delete after 30-day hold.

---

## 6. Managed Identity Alignment

Each managed identity binds exactly one repo's workload to Azure resources. No identity should be shared across repos.

| Managed Identity | Bound Repo | Resource Group | Purpose |
|------------------|-----------|----------------|---------|
| `mi-ipai-odoo-dev` | `odoo` | `rg-ipai-shared-dev` | Odoo container apps access to KV, ACR, PG |
| `mi-ipai-odoo-prod` | `odoo` | `rg-ipai-shared-prod` | Production Odoo workload identity |
| `mi-ipai-odoo-staging` | `odoo` | `rg-ipai-shared-staging` | Staging Odoo workload identity |
| `mi-ipai-lakehouse-dev` | `lakehouse` | `rg-ipai-shared-dev` | Databricks, storage, Superset access |
| `mi-ipai-lakehouse-prod` | `lakehouse` | `rg-ipai-shared-prod` | Production lakehouse workload identity |
| `mi-ipai-lakehouse-staging` | `lakehouse` | `rg-ipai-shared-staging` | Staging lakehouse workload identity |
| `mi-ipai-platform-dev` | `ops-platform` | `rg-ipai-shared-dev` | Platform tooling, monitoring, Dev Center |
| `mi-ipai-platform-prod` | `ops-platform` | `rg-ipai-shared-prod` | Production platform workload identity |
| `mi-ipai-platform-staging` | `ops-platform` | `rg-ipai-shared-staging` | Staging platform workload identity |
| `id-ipai-agents-dev` | `agents` | `rg-ipai-shared-dev` | Agent containers, AI services access |
| `id-ipai-aca-dev` | `agents` | `rg-ipai-agents-dev` | ACA-specific identity for agent jobs |

---

## 7. Key Alignment Rules

1. **One repo, one domain**: Each repo owns a distinct functional domain. No two repos deploy the same container or manage the same Azure resource.

2. **Databricks rule**: The Databricks workspace (`dbw-ipai-dev`) is an execution surface. The `lakehouse` repo is the Git SSOT for all notebooks, jobs, SQL, and pipeline definitions. In-workspace editing without Git sync is prohibited.

3. **IaC ownership**: Only the `infra` repo provisions shared infrastructure (Front Door, Key Vaults, VNets, NSGs, managed identities). Application repos consume these resources but never define them.

4. **Identity isolation**: Each managed identity is bound to exactly one repo. Cross-repo identity sharing is prohibited. If a workload needs access to another repo's resources, use federated credentials or cross-identity RBAC grants defined in `infra`.

5. **Container registry rule**: `ipaiodoodevacr` is for Odoo images only (owned by `odoo` repo). `ipaiwebacr` is for all other platform images (owned by `infra`, consumed by multiple repos).

6. **No DigitalOcean**: All references to DigitalOcean are deprecated. Azure Container Apps is the canonical compute surface.
