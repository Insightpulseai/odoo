# Azure Bill of Materials — Target State

> **Locked:** 2026-04-15
> **Authority:** [`ssot/azure/bill-of-materials.yaml`](../../ssot/azure/bill-of-materials.yaml)
> **Tag contract:** [`ssot/azure/tagging-standard.yaml`](../../ssot/azure/tagging-standard.yaml)
> **Bicep module:** [`infra/azure/tags/main.bicep`](../../infra/azure/tags/main.bicep)
>
> **Doctrine:** A tight target-state contract — not "whatever is in the subscription."

---

## TL;DR — Blunt desired BOM

```
1 subscription
7 canonical resource groups
1 Key Vault, 1 ACR, 1 Postgres Flex
1 Foundry resource + 1 project
1 Databricks workspace, 1 AI Search
1 primary VNet boundary
1 observability stack per major lane
Bicep-managed tags and policy everywhere
Azure Pipelines-only delivery
```

---

## 1. Governance / control-plane BOM

Mandatory first. Everything downstream assumes this is enforced.

| Layer | Target | Status |
|---|---|---|
| Subscription | 1 active Sponsorship sub (`eba824fb-…`) | ✅ |
| Resource groups | 7 canonical RGs (not 12+ ad-hoc) | ⚠️ consolidate |
| Tags | Canonical tag object applied via Bicep at sub/RG/resource | ⚠️ enforce via `infra/azure/tags/main.bicep` |
| Policy | `tag-compliance` + `allowed-locations` + `allowed-skus` + `deny-risky-drift` | ⚠️ add |
| RBAC | Entra groups + MI, least privilege | ⚠️ audit |
| Key management | 1 Key Vault (`kv-ipai-dev`) as canonical secrets authority | ✅ |

---

## 2. Canonical resource-group map (target)

```
rg-ipai-shared               # ACR, shared KV, shared identities
rg-ipai-dev-network          # VNet, private DNS, NSG, private endpoints
rg-ipai-dev-observability    # Log Analytics, App Insights, action groups, alerts
rg-ipai-dev-odoo-runtime     # ACA env, Odoo apps/jobs
rg-ipai-dev-odoo-data        # Postgres, runtime storage
rg-ipai-dev-agent-ai         # Foundry, AI Search, Doc Intel
rg-ipai-dev-data-intel       # Databricks, access connector, Purview, lake storage
```

Current state: **12+ ad-hoc RGs.** Consolidation action is in [`ssot/azure/bill-of-materials.yaml` → `resource_groups.rationalize`](../../ssot/azure/bill-of-materials.yaml).

---

## 3. Odoo transaction plane BOM

| Layer | Target | Canonical |
|---|---|---|
| ACA env | 1 | `ipai-odoo-dev-env-v2` |
| Odoo web | 1 | `ipai-odoo-dev-web` |
| Jobs | 1–3 | init/migration + optional workers |
| Registry | 1 | `acripaiodoo.azurecr.io` (`rg-ipai-shared`) |
| Database | 1 | `pg-ipai-odoo` (PG Flex 16, `rg-ipai-dev-odoo-data`) |
| Storage | 1–2 | runtime file artifacts only |
| Network | 1 | canonical VNet + private DNS, PEs where needed |
| Monitoring | 1 App Insights + 1 LA | scope = odoo lane |

Rule: **thin.** Not multiple overlapping runtime islands.

---

## 4. Agent / Foundry plane BOM

| Layer | Target | State |
|---|---|---|
| Foundry resource | 1 | `ipai-copilot-resource` ✅ (moved to sponsored 2026-04-14) |
| Foundry project | 1 | `proj-ipai-copilot` — pending create |
| Model deployments | pinned | `gpt-4.1`, `text-embedding-3-small`, `w9-pulser (gpt-4o-mini)` ✅; `claude-sonnet-4-6` pending quota |
| Connections | App Insights, AI Search, Storage | add in order |
| Tools | Per-agent enablement, never global | 5 canonical MCPs |
| Durable state | **Defer** until justified | — |
| Redis cache | **Defer** until justified | — |

---

## 5. Data-intelligence plane BOM

| Layer | Target | Canonical |
|---|---|---|
| Databricks workspace | 1 | `dbw-ipai-dev` |
| Governance | Unity Catalog + catalogs/schemas | ✅ |
| Lake storage | 1 ADLS | bronze/silver/gold |
| Access connector | 1 | ✅ |
| AI Search | 1 | grounded retrieval |
| Purview | 1 *if actively used* | keep |
| Event Hubs | 1 *if streaming* | keep |
| Fabric / Power BI | Add when consumer path is real | ⚠️ PBI Pro trial expires ~2026-05-20 |

Rule: **no writeback into operational truth.** Lakehouse is read-only from operational perspective.

---

## 6. Observability BOM

| Layer | Target |
|---|---|
| Log Analytics | 1 per environment lane (not many random) |
| App Insights | 1 per major app surface (odoo, agent, web) |
| Action Groups | 1–2 standard |
| Alerts | budget, availability, queue/job failure, DB health, agent failure |

Current state: fragmented. Consolidate.

---

## 7. Delivery / IaC BOM

| Layer | Target |
|---|---|
| IaC language | **Bicep** (default) |
| Authoring | VS Code + Bicep extension |
| Validation | Azure CLI local (`az bicep build`, `az deployment group what-if`) |
| CI/CD | **Azure Pipelines only** |
| Contracts | [`ssot/azure/bill-of-materials.yaml`](../../ssot/azure/bill-of-materials.yaml), [`ssot/azure/tagging-standard.yaml`](../../ssot/azure/tagging-standard.yaml), [`ssot/foundry/runtime_inventory.yaml`](../../ssot/foundry/runtime_inventory.yaml) |
| Drift control | Azure Policy + what-if + tag validation + contract validation |

**Forbidden:**
- portal-only changes
- untagged resources
- resources outside canonical RGs
- GitHub Actions
- Vercel

---

## 8. Mandatory tag contract

Every resource, RG, and subscription carries these:

```yaml
environment: dev|staging|prod
plane: transaction|agent|data-intelligence|platform|observability|network|shared
system: odoo|pulser|fabric|databricks|shared|foundry|web
owner: jake
cost_center: ipai
managed_by: bicep
criticality: low|medium|high
data_classification: internal|restricted|confidential|public
lifecycle: experimental|active|legacy
```

Optional: `product`, `domain`, `workload`, `deployed`, `compliance_scope`.

Deprecated keys (normalize to canonical): `env→environment`, `costCenter→cost_center`, `data-classification→data_classification`, `app→system`.

---

## 9. Keep / rationalize / add next

### Keep
- Foundry resource + project
- Postgres Flexible Server
- ACR
- Databricks workspace
- AI Search
- Key Vault
- Core VNets / private DNS
- App Insights / Log Analytics
- Event Hubs / Purview / Service Bus *only if actively wired*

### Rationalize
- Too many storage accounts without a clear role
- Too many Log Analytics workspaces
- Duplicate or unclear runtime RGs
- Placeholder or failed ACA apps/jobs
- Any resource without a clear owner plane and tag set

### Add next
- Canonical Bicep tag module (`infra/azure/tags/main.bicep`) ✅
- Foundry connection inventory (`ssot/foundry/runtime_inventory.yaml`)
- Azure Pipelines validation for Bicep + tags + Foundry contract
- FinOps budget + anomaly + alerting layer

---

## 10. Migration posture (2026-04-15)

Migration from `Azure subscription 1` (`536d8cf6-…`) → **Microsoft Azure Sponsorship** (`eba824fb-…`).

| Resource | Status |
|---|---|
| Foundry `ipai-copilot-resource` | ✅ moved |
| DocAI `docai-ipai-dev` | ✅ moved |
| `ipai-website-dev` container app | ✅ redeployed on sponsored |
| `ipai-w9studio-dev` container app | ✅ redeployed on sponsored |
| `pg-ipai-odoo` (Postgres Flex) | ⏸ pending cutover |
| 13 other container apps | ⏸ pending redeploy |
| Key Vault move | ⏸ |
| AI Search, Storage moves | ⏸ |
| Private endpoints rebuild | ⏸ |
| Managed identities recreate | ⏸ |
| DNS CNAME flips | ⏸ |

---

## 11. Enforcement

- **Pipeline gate:** Azure Pipelines validates Bicep + tags + BOM contract before deploy.
- **Policy gate:** Azure Policy denies create if required tags missing.
- **Contract gate:** Pre-merge check that resources added match canonical RG + plane.
- **Drift gate:** `az deployment group what-if` against the live subscription; no portal-only drift.

---

*Last updated: 2026-04-15*
