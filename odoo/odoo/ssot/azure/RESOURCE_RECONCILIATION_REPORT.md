# Azure Resource Reconciliation Report

> **Date**: 2026-03-11
> **Source**: Azure portal export (57 resources) vs previous SSOT (`resources.yaml` v1.0, `PLATFORM_TARGET_STATE.md` v1.4.1)
> **Scope**: Inventory reconciliation only. No Bicep/Terraform renames.

---

## 1. Confirmed Resources Missing from Previous SSOT

These resources exist in the Azure portal but were **not documented** in the previous `resources.yaml` (v1.0, which only covered ~20 Databricks/AI core resources).

| Resource | Type | RG | Owner Domain |
|---|---|---|---|
| ipai-odoo-dev-web | Container App | rg-ipai-dev | odoo |
| ipai-odoo-dev-worker | Container App | rg-ipai-dev | odoo |
| ipai-odoo-dev-cron | Container App | rg-ipai-dev | odoo |
| ipai-crm-dev | Container App | rg-ipai-dev | odoo |
| ipai-plane-dev | Container App | rg-ipai-dev | platform |
| ipai-shelf-dev | Container App | rg-ipai-dev | platform |
| odoo-web | Container App | rg-ipai-agents-dev | odoo |
| ipai-odoo-dev-wave1 | Container App Job | rg-ipai-dev | odoo |
| ipai-odoo-install | Container App Job | rg-ipai-dev | odoo |
| odoo-init | Container App Job | rg-ipai-agents-dev | odoo |
| ipai-odoo-dev-env | Container Apps Env | rg-ipai-dev | odoo |
| cae-ipai-dev | Container Apps Env | rg-ipai-agents-dev | platform |
| debug-odoo-ep | Container Instances | rg-ipai-agents-dev | odoo |
| cripaidev | Container Registry | rg-ipai-shared-dev | infra |
| ipaiodoodevacr | Container Registry | rg-ipai-dev | odoo |
| ipai-odoo-dev-pg | PG Flexible Server | rg-ipai-dev | odoo |
| ipai-fd-dev | Front Door | rg-ipai-shared-dev | infra |
| ipaiDevWafPolicy | WAF Policy | rg-ipai-shared-dev | infra |
| ipai-odoo-dev-kv | Key Vault | rg-ipai-dev | odoo |
| id-ipai-aca-dev | Managed Identity | rg-ipai-agents-dev | odoo |
| vm-ipai-supabase-dev | Virtual Machine | rg-ipai-agents-dev | platform |
| vm-ipai-supabase-dev_OsDisk_1_* | Disk | rg-ipai-agents-dev | platform |
| vm-ipai-supabase-devNSG | NSG | rg-ipai-agents-dev | platform |
| vm-ipai-supabase-devPublicIP | Public IP | rg-ipai-agents-dev | platform |
| vm-ipai-supabase-devVMNic | NIC | rg-ipai-agents-dev | platform |
| vm-ipai-supabase-devVNET | VNet | rg-ipai-agents-dev | platform |
| nsg-cae-ipai-dev | NSG | rg-ipai-ai-dev | infra |
| nsg-pg-ipai-dev | NSG | rg-ipai-ai-dev | lakehouse |
| privatelink.postgres.database.azure.com | Private DNS Zone | rg-ipai-ai-dev | infra |
| capp-svc-lb | Load Balancer | ME_cae-ipai-dev_* | infra |
| appi-ipai-dev | Application Insights | rg-ipai-shared-dev | infra |
| Application Insights Smart Detection | Action Group | rg-ipai-shared-dev | infra |
| law-ipai-dev | Log Analytics | rg-ipai-shared-dev | infra |
| managed-appi-ipai-dev-ws | Log Analytics | *_managed | infra |
| data-intel-ph-resource | Foundry | rg-data-intel-ph | ai |
| data-intel-ph | Foundry Project | rg-data-intel-ph | ai |
| insightpulseai | Azure DevOps Org | * | devops |
| ipai-build-pool | Managed DevOps Pool | rg-ipai-devops | devops |
| ipai-devcenter | Dev Center | rg-ipai-devops | devops |
| ipai-devcenter-project | Dev Center Project | rg-ipai-devops | devops |

**Total newly documented**: 40 resources

---

## 2. Target-State Resources Not Yet Deployed

These resources appear in `PLATFORM_TARGET_STATE.md` §2 as "Active" but do **not exist** in the Azure portal. They are aspirational/planned.

### Resource Group: `rg-ipai-network` (entire RG — 6 resources)

| Resource | Type | Status |
|---|---|---|
| vnet-ipai-hub | Virtual Network | Planned |
| vnet-ipai-spoke-dev | Virtual Network | Planned |
| peer-hub-spoke-dev | VNet Peering | Planned |
| peer-spoke-dev-hub | VNet Peering | Planned |
| bastion-ipai-dev | Azure Bastion | Planned |
| nsg-ipai-spoke-dev | NSG | Planned |

### Resource Group: `rg-ipai-monitoring` (entire RG — 6 resources)

| Resource | Type | Status |
|---|---|---|
| grafana-ipai-dev | Managed Grafana | Planned |
| prom-ipai-dev | Azure Monitor (Prometheus) | Planned |
| ag-ipai-dev | Action Group | Planned |
| alert-cpu-high | Metric Alert | Planned |
| alert-error-rate | Metric Alert | Planned |
| alert-pg-connections | Metric Alert | Planned |

### Resource Group: `rg-ipai-backup` (entire RG — 5 resources)

| Resource | Type | Status |
|---|---|---|
| rsv-ipai-dev | Recovery Services Vault | Planned |
| policy-daily-30d | Backup Policy | Planned |
| policy-weekly-90d | Backup Policy | Planned |
| st-ipai-backup | Storage Account (Cool) | Planned |
| lock-ipai-backup | Resource Lock | Planned |

### Resource Group: `rg-ipai-data` (aspirational extras — 7 resources)

| Resource | Type | Status |
|---|---|---|
| adf-ipai-dev | Data Factory | Planned |
| evh-ipai-dev | Event Hub Namespace | Planned |
| cosmos-ipai-dev | Cosmos DB | Planned |
| purview-ipai-dev | Microsoft Purview | Planned |
| synapse-ipai-dev | Synapse Analytics | Planned |
| ml-ipai-dev | ML Workspace | Planned |
| st-ml-ipai-dev / cr-ml-ipai-dev | ML Storage/Registry | Planned |

### Resource Group: `rg-ipai-dev` (aspirational extras — 7 resources)

| Resource | Type | Status |
|---|---|---|
| plan-ipai-dev | App Service Plan | Planned |
| app-ipai-health | App Service | Planned |
| func-ipai-dev | Function App | Planned |
| insights-dashboard-* | Container App | Planned |
| scout-dashboard-* | Container App | Planned |
| juicer-dashboard-* | Container App | Planned |
| retail-advisor-* / pulser-poc-* | Container App | Planned |

**Total aspirational (not yet deployed)**: ~31 resources

---

## 3. Naming Mismatches

Portal names that deviate from the `{type}-ipai-{env}` convention.

| Portal Name (Actual) | Expected Convention | Type | Severity |
|---|---|---|---|
| `ipai-fd-dev` | `fd-ipai-dev` | Front Door | Low (prefix order) |
| `ipaiDevWafPolicy` | `waf-ipai-dev` | WAF Policy | Medium (camelCase) |
| `cripaidev` | `acr-ipai-dev` | Container Registry | Medium (no separators) |
| `ipaiodoodevacr` | `acr-ipai-odoo-dev` | Container Registry | Medium (no separators) |
| `dbmanagedidentity` | N/A (managed) | Managed Identity | N/A (Databricks-controlled) |
| `dbstoragew6tn3uhg4bluy` | N/A (managed) | Storage Account | N/A (Databricks-controlled) |
| `capp-svc-lb` | N/A (managed) | Load Balancer | N/A (ACA-controlled) |
| `vm-ipai-supabase-dev*` | Mixed conventions | VM + associated | Low (acceptable for VM resources) |

**Decision D-002**: Accepted temporary divergence. Actual names documented as-is. Rename deferred.

---

## 4. Resource Group Mismatches

Where `PLATFORM_TARGET_STATE.md` documented a different RG structure than reality.

| SSOT Target RG | Actual Portal RG | Delta |
|---|---|---|
| `rg-ipai-shared` | `rg-ipai-shared-dev` | `-dev` suffix in actual |
| `rg-ipai-data` | `rg-ipai-data-dev` | `-dev` suffix in actual |
| `rg-ipai-network` | — | Does not exist (planned) |
| `rg-ipai-monitoring` | — | Does not exist (planned) |
| `rg-ipai-backup` | — | Does not exist (planned) |
| — | `rg-ipai-agents-dev` | Not in target state |
| — | `rg-ipai-devops` | Not in target state |
| — | `rg-data-intel-ph` | Not in target state |
| — | `NetworkWatcherRG` | Azure-managed |
| — | `ai_appi-..._managed` | App Insights-managed |

---

## 5. Managed / Auto-Created Resources

Resources created automatically by Azure services. These should NOT have their names normalized.

| Resource | Type | Managed By |
|---|---|---|
| dbmanagedidentity | Managed Identity | Databricks |
| dbstoragew6tn3uhg4bluy | Storage Account | Databricks |
| unity-catalog-access-connector | Access Connector | Databricks |
| capp-svc-lb | Load Balancer | Container Apps |
| vm-ipai-supabase-dev_OsDisk_1_* | Disk | Azure Compute |
| Application Insights Smart Detection | Action Group | Application Insights |
| managed-appi-ipai-dev-ws | Log Analytics | Application Insights |
| NetworkWatcher_southeastasia | Network Watcher | Azure Platform |

**Total managed**: 8 resources

---

## 6. High-Risk Ambiguities

### EXC-001: Dual Odoo Deployment

**Risk**: HIGH

Two complete Odoo deployment surfaces exist:

| Aspect | Deployment A (rg-ipai-agents-dev) | Deployment B (rg-ipai-dev) |
|---|---|---|
| Container Apps Env | cae-ipai-dev | ipai-odoo-dev-env |
| Web | odoo-web | ipai-odoo-dev-web |
| Worker | — | ipai-odoo-dev-worker |
| Cron | — | ipai-odoo-dev-cron |
| Init Job | odoo-init | ipai-odoo-install |
| Database | pg-ipai-dev (shared) | ipai-odoo-dev-pg (dedicated) |
| Registry | cripaidev (shared) | ipaiodoodevacr (dedicated) |
| Key Vault | — | ipai-odoo-dev-kv |

**Canonical status**: UNKNOWN. Tracked in `exceptions/dual-odoo-deployment.yaml`.

### Dual PostgreSQL Servers

Two PG Flexible Servers with overlapping purpose:
- `pg-ipai-dev` (rg-ipai-data-dev) — shared, used by Deployment A
- `ipai-odoo-dev-pg` (rg-ipai-dev) — dedicated, used by Deployment B

### Dual Container Registries

Two ACRs:
- `cripaidev` (rg-ipai-shared-dev) — shared
- `ipaiodoodevacr` (rg-ipai-dev) — Odoo-specific

---

## 7. Summary Counts

| Category | Count |
|---|---|
| Portal confirmed resources | 57 |
| Previously documented in resources.yaml | ~17 |
| Newly documented | 40 |
| Managed/auto-created | 8 |
| Target-state aspirational (not deployed) | ~31 |
| Naming mismatches (non-managed) | 4 |
| Unresolved exceptions | 1 (EXC-001: dual Odoo) |
| Resource groups (actual) | 10 (8 owned + 2 managed) |
| Resource groups (planned, not deployed) | 3 |
