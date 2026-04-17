# Azure Naming Convention — IPAI

> CAF-aligned naming for all Azure resources in the InsightPulse AI platform.
> Reference:
>   https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming
>   https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-abbreviations
>   https://github.com/mspnp/AzureNamingTool
> Locked 2026-04-15.

Names in Azure are mostly immutable and scoped (global vs RG vs resource). Tags
are for mutable/contextual metadata (see `ssot/governance/tagging-doctrine.yaml`).
Put only what is permanent in the name; put everything else in tags.

---

## 1. Components

```
{type}-{workload}-{env}-{region?}-{nnn?}
```

| Component | Meaning | Example |
|---|---|---|
| `type` | CAF abbreviation for the resource type | `rg`, `kv`, `app`, `srch`, `st` |
| `workload` | Product / workload family | `ipai`, `pulser`, `odoo`, `prismalab`, `w9`, `shared` |
| `env` | Lifecycle stage | `dev`, `staging`, `prod` |
| `region` | Azure region short code (omit for global) | `sea` (SEA), `eus2` (East US 2), `wus` (West US) |
| `nnn` | Instance counter (3 digits, start at 001) | `001` |

Delimiter = `-` for most resources. Storage, ACR, and other resources that
**don't allow hyphens** use concatenated snake-free lowercase: `stipaidevlake`,
`cripaidev`.

---

## 2. Canonical abbreviations (subset we use)

| Type | Abbrev | Scope | Example |
|---|---|---|---|
| Resource group | `rg` | Subscription | `rg-ipai-dev-data-sea` |
| Key Vault | `kv` | Global | `kv-ipai-dev` |
| Storage (with hyphens OK?) | **no** → `st` prefix, no hyphens | Global | `stipaidevlake`, `stipaidevagent` |
| Container Registry | `cr` | Global | `cripaidev` |
| Container Apps env | `cae` | RG | `cae-ipai-odoo-dev-sea` |
| Container App | `app` (or `ca`) | RG | `app-ipai-odoo-dev-sea-001` / `ipai-odoo-dev-web` (legacy) |
| AKS | `aks` | RG | `aks-ipai-prod-sea-001` |
| Databricks workspace | `dbw` | RG | `dbw-ipai-dev` |
| Databricks access connector | `unity-catalog-access-connector` (legacy) / `dbac` (new) | RG | `dbac-ipai-dev-sea` |
| Postgres Flexible Server | `pg` | Global | `pg-ipai-odoo`, `pg-ipai-dev` |
| Azure AI Search | `srch` | Global | `srch-ipai-dev`, `srch-ipai-dev-sea` |
| Azure AI Foundry resource | `fnd` (new) | Global | `fnd-ipai-copilot-dev-eus2` |
| Foundry project | `proj` | Resource | `proj-ipai-copilot` |
| Document Intelligence | `docai` | Global | `docai-ipai-dev` |
| Application Insights | `appi` | RG | `appi-ipai-dev-agent-sea` |
| Log Analytics | `la` | RG | `la-ipai-dev` |
| Front Door Standard | `afd` / `fd` | Global | `afd-ipai-dev`, `ipai-fd-dev` (legacy) |
| Azure DNS zone | `dns` | Global | `insightpulseai.com` (apex domain itself) |
| Managed Identity | `id` | RG | `id-ipai-copilot-dev-sea` |
| Action Group | `ag` | RG | `ag-ipai-dev-oncall` |
| Bot Service | `bot` | Global | `bot-ipai-dev` |
| Virtual Network | `vnet` | RG | `vnet-ipai-shared-sea` |
| Subnet | `snet` | VNet | `snet-ipai-apps-sea` |
| Private endpoint | `pe` | RG | `pe-ipai-kv-dev-sea` |
| Route table | `rt` | RG | `rt-ipai-shared-sea` |
| NSG | `nsg` | RG or subnet | `nsg-ipai-apps-sea` |

---

## 3. Region short codes we accept

| Region | Code | Primary use |
|---|---|---|
| Southeast Asia | `sea` | Default workload region |
| East US 2 | `eus2` | Foundry (`ipai-copilot-resource`) |
| East US | `eus` | Legacy OpenAI (`oai-ipai-dev`) |
| West US | `wus` | Future DR |

Global resources (most PaaS with public DNS) omit the region.

---

## 4. Scope rules (summary from CAF)

| Scope | Rule | Example |
|---|---|---|
| Global | Unique across all of Azure | `app-ipai-odoo-dev-sea-001.azurewebsites.net` |
| Resource group | Unique within the RG | `snet-ipai-apps-sea` |
| Resource | Unique within the parent | subnet within vnet |

---

## 5. Known legacy names we keep

Some names predate this doctrine and are retained for stability. Do not
rename without an ADR (resource renames are generally not supported by Azure):

| Legacy name | Type | Why retained |
|---|---|---|
| `aifoundry-ipai-dev` | Foundry hub (classic) | Resource model limitation; migrate to `fnd-*` when rebuilding |
| `oai-ipai-dev` | Azure OpenAI | Predates Foundry |
| `ipai-odoo-dev-web/-worker/-cron` | Container Apps | Legacy `ipai-odoo-dev-*` pattern; new ACA apps follow `app-*` |
| `ipai-auth-dev`, `ipai-mcp-dev`, etc. | Container Apps | Same; stable public hostnames |
| `unity-catalog-access-connector` | Databricks AC | Default Databricks name |
| `ipai-copilot-resource` | Foundry | Canonical per `feedback_foundry_reuse_doctrine` |
| `ipai-fd-dev` | Front Door | Existing edge name |

New resources follow this convention; renames happen only during full-stack re-provisioning events.

---

## 6. Resource Mover note

If we ever need to relocate resources across regions or RGs, use Azure Resource
Mover (https://learn.microsoft.com/en-us/rest/api/resourcemover/) rather than
delete + recreate. Resource Mover preserves resource IDs where supported. This
is the canonical path for sponsorship→PAYG migrations per ADR-002.

---

## 7. Validation

- `az bicep build` (type-checks names against allowed patterns for each resource)
- `azure-pipelines/templates/bicep-lint-validate.yml` (lint in CI)
- Azure Policy `Not allowed resource types` + naming-pattern policy (to author)

---

## 8. Examples

```
rg-ipai-dev-data-sea           # RG, ipai, dev, data plane, SEA
rg-ipai-dev-ai-sea             # RG, ipai, dev, AI plane, SEA
rg-ipai-dev-odoo-runtime       # RG, ipai, dev, odoo runtime (region implied SEA)
kv-ipai-dev                    # Key Vault (global scope; no region for global)
stipaidevlake                  # Storage, no hyphens, HNS-enabled lake
cripaidev                      # Container Registry, no hyphens
dbw-ipai-dev                   # Databricks workspace
pg-ipai-odoo                   # Postgres for Odoo
srch-ipai-dev                  # AI Search (global)
appi-ipai-dev-agent-sea        # App Insights for agent plane (SEA)
afd-ipai-dev                   # Front Door
id-ipai-copilot-dev-sea        # Managed Identity for copilot (SEA)
```
