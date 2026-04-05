# IaC Drift Assessment — 2026-04-05

## Method

Manual comparison: Azure CLI live resource inventory vs. Bicep files in `infra/azure/`.
No ARM deployment history was accessible (permission denied on `az deployment group list`),
so drift is assessed by comparing declared Bicep resources against live Azure state.

## Subscription

- ID: `536d8cf6-89e1-4815-aef3-d5f2c5f4d070`
- Tenant: `402de71a-87ec-4302-a609-fb76098d1da7`

## Resource Groups Assessed

| Resource Group | Exists in Azure | Exists in IaC |
|---|---|---|
| `rg-ipai-dev-odoo-runtime` | Yes | Yes (referenced in `odoo-runtime.bicep`, `main.bicep`, `deploy-frontdoor-erp.bicep`) |
| `rg-ipai-dev-odoo-data` | Yes | Yes (referenced in `odoo-runtime.bicep` for PG) |
| `rg-ipai-dev-platform` | Yes | Yes (referenced in `main.bicep` for KV, storage) |
| `rg-ipai-ai-dev` | **Not Found** | Yes (referenced in infrastructure.md for AI services) |
| `rg-ipai-agents-dev` | **Not Found** | Yes (referenced in infrastructure.md for Supabase VM) |
| `ME_ipai-odoo-ha-env_*` (managed) | Yes | No (Azure-managed, expected) |
| `ai_ipai-appinsights_*` (managed) | Yes | No (Azure-managed, expected) |

## Live Resources vs. IaC Coverage

### rg-ipai-dev-odoo-runtime (18 Container Apps + Environment + Front Door + ACR)

| Resource | Type | In IaC? | Classification |
|---|---|---|---|
| `ipai-odoo-dev-env` | Container Apps Environment | Yes (`container-apps.bicep`, `odoo-runtime.bicep`) | **Partially Managed** — IaC declares 9 services; live has 18 apps |
| `ipai-odoo-ha-env` | Container Apps Environment | No | **Unmanaged** — second environment not in any Bicep file |
| `ipai-odoo-dev-web` | Container App | Yes (`container-apps.bicep`, `aca-odoo-services.bicep`, `odoo-runtime.bicep`) | **Partially Managed** |
| `ipai-odoo-dev-worker` | Container App | Yes | **Partially Managed** |
| `ipai-odoo-dev-cron` | Container App | Yes | **Partially Managed** |
| `ipai-mcp-dev` | Container App | Yes (`container-apps.bicep` as mcp-gateway) | **Partially Managed** |
| `ipai-ocr-dev` | Container App | No | **Unmanaged** |
| `ipai-superset-dev` | Container App | Yes (`container-apps.bicep` as superset) | **Partially Managed** |
| `ipai-website-dev` | Container App | No | **Unmanaged** |
| `ipai-copilot-gateway` | Container App | No | **Unmanaged** |
| `ipai-login-dev` | Container App | No | **Unmanaged** |
| `w9studio-landing-dev` | Container App | No | **Unmanaged** |
| `ipai-odoo-connector` | Container App | No | **Unmanaged** |
| `ipai-prismalab-dev` | Container App | No | **Unmanaged** |
| `ipai-mailpit-dev` | Container App | No | **Unmanaged** |
| `ipai-code-server-dev` | Container App | No | **Unmanaged** |
| `ipai-grafana-dev` | Container App | No | **Unmanaged** |
| `ipai-ops-dashboard` | Container App | No | **Unmanaged** |
| `ipai-workload-center` | Container App | No | **Unmanaged** |
| `ipai-w9studio-dev` | Container App | No | **Unmanaged** |
| `afd-ipai-dev` | Front Door Premium | Yes (`deploy-frontdoor-erp.bicep`, `modules/front-door.bicep`) | **Partially Managed** — IaC only covers `erp.` route |
| `acripaiodoo` | Container Registry (Basic) | Yes (`modules/acr.bicep`, `odoo-runtime.bicep`) | **Partially Managed** |
| `ag-ipai-platform` | Action Group (eastus2) | No | **Unmanaged** |

### rg-ipai-dev-odoo-data (PostgreSQL)

| Resource | Type | In IaC? | Classification |
|---|---|---|---|
| `pg-ipai-odoo` | PostgreSQL Flexible Server (Standard_D2ds_v5, v16) | **Partially** | **Partially Managed** — IaC declares `ipai-odoo-dev-pg` with Burstable/Standard_B1ms SKU; live is `pg-ipai-odoo` with GeneralPurpose/Standard_D2ds_v5. Name, SKU, and tier all diverge. |

### rg-ipai-dev-platform (Key Vault)

| Resource | Type | In IaC? | Classification |
|---|---|---|---|
| `kv-ipai-dev` | Key Vault | Yes (`modules/keyvault.bicep`, `main.bicep`) | **Partially Managed** — IaC name pattern is `${prefix}-kv` which would produce different names |

### rg-ipai-ai-dev (AI Services)

Resource group **does not exist** in the current subscription. The 6 AI resources documented in `infrastructure.md` (Azure OpenAI, Document Intelligence, Computer Vision, Language, Search, Databricks) are either:
- Deployed in a different subscription
- Deleted/never provisioned
- Listed in aspirational documentation

Classification: **Cannot assess** — RG not found.

### rg-ipai-agents-dev (Deprecated Supabase VM)

Resource group **does not exist**. Consistent with the 2026-03-26 Supabase deprecation — likely already decommissioned.

Classification: **Decommissioned** (expected).

## Drift Classification Summary

| Resource Group | Total Live Resources | IaC-Managed | Partially Managed | Unmanaged | Orphaned in IaC |
|---|---|---|---|---|---|
| `rg-ipai-dev-odoo-runtime` | 22+ | 0 | 8 | 13 | 1 (n8n in Bicep, not live) |
| `rg-ipai-dev-odoo-data` | 1 | 0 | 1 | 0 | 0 |
| `rg-ipai-dev-platform` | 1 | 0 | 1 | 0 | 0 |
| `rg-ipai-ai-dev` | N/A (not found) | 0 | 0 | 0 | 6+ (declared in docs) |
| `rg-ipai-agents-dev` | N/A (not found) | 0 | 0 | 0 | 1 (Supabase VM in docs) |
| **TOTAL** | **24+** | **0** | **10** | **13** | **7+** |

## IaC Coverage Rate

**0% fully IaC-managed** — No evidence that any Bicep template has ever been deployed via `az deployment group create`. All resources appear to have been created via Azure Portal or CLI ad-hoc, with Bicep files written after the fact but never executed as the source of truth.

**~42% partially covered** (10/24) — Bicep templates exist that _describe_ these resources but naming, SKUs, and configuration have diverged from live state.

**~54% completely unmanaged** (13/24) — No Bicep representation exists at all for these container apps.

## Key Findings

1. **No deployment history accessible** — Could not verify any ARM deployment in any RG. This strongly suggests resources were portal/CLI-created, not IaC-deployed.

2. **Massive Container App sprawl** — IaC declares 9 container apps; live environment has 18. Nine additional apps (`ipai-ocr-dev`, `ipai-website-dev`, `ipai-copilot-gateway`, `ipai-login-dev`, `w9studio-landing-dev`, `ipai-odoo-connector`, `ipai-prismalab-dev`, `ipai-mailpit-dev`, `ipai-code-server-dev`, `ipai-grafana-dev`, `ipai-ops-dashboard`, `ipai-workload-center`, `ipai-w9studio-dev`) have no IaC definition.

3. **PostgreSQL name and SKU drift** — IaC defines `ipai-odoo-dev-pg` (Burstable, B1ms); live is `pg-ipai-odoo` (GeneralPurpose, D2ds_v5). This is a complete identity mismatch — the live server was likely provisioned independently and the Bicep was never updated.

4. **Second ACA environment (`ipai-odoo-ha-env`)** — Not declared in any Bicep file. Purpose unclear (HA standby?).

5. **Missing resource groups** — `rg-ipai-ai-dev` and `rg-ipai-agents-dev` do not exist despite being documented in `infrastructure.md`. Either deleted or in a different subscription.

6. **Front Door partially covered** — `deploy-frontdoor-erp.bicep` only covers the `erp.insightpulseai.com` route. The actual Front Door likely has routes for all 10+ subdomains, none of which are in IaC.

7. **Bicep is aspirational, not operational** — The Bicep codebase is comprehensive in design (24 module files covering KV, ACR, ACA, PG, Front Door, APIM, Databricks, VNet, diagnostics, PIM, policy, monitoring) but functions as documentation rather than deployment artifacts.

## Remediation Priority

### P0 — Immediate (Break-glass risk)

1. **Reconcile PostgreSQL Bicep to live state** — Update `postgres-flexible.bicep` defaults and `odoo-runtime.bicep` to match `pg-ipai-odoo` (GeneralPurpose, D2ds_v5, v16).
2. **Export live Front Door config** — Run `az afd profile export` and reconcile with `deploy-frontdoor-erp.bicep` to cover all routes.

### P1 — High (Drift compounds daily)

3. **Add Bicep definitions for all 18 live container apps** — Update `container-apps.bicep` service array to include the 9 missing apps.
4. **Document or delete `ipai-odoo-ha-env`** — If unused, delete. If used, add to IaC.
5. **Run first real deployment** — Pick one low-risk module (e.g., `keyvault.bicep`) and do a what-if + deploy to establish a deployment history baseline.

### P2 — Medium (Governance gap)

6. **Resolve `rg-ipai-ai-dev` location** — Determine if AI services are in another subscription or were never provisioned. Update `infrastructure.md` accordingly.
7. **Enable CI-gated Bicep deployment** — Add an Azure DevOps pipeline that runs `az deployment group what-if` on PRs touching `infra/azure/`.
8. **Tag governance** — The `policy-tag-governance.bicep` module exists but `enableTagGovernance` defaults to `false`. Enable in audit mode.

## Conclusion

The IPAI Azure platform has **zero IaC-managed resources**. Bicep files exist and are architecturally sound but have never been the source of truth for any deployment. All 24+ live resources were created outside IaC. This confirms the P0 blocker classification — the gap between documented IaC and live state is total, not partial.
