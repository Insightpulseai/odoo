# Azure Resource Inventory — Live Estate

> 63 resources on Microsoft Azure Sponsorship (`eba824fb`).
> Snapshot: 2026-04-18. Source: Azure Portal → All Resources.

---

## Summary

| Category | Count |
|----------|-------|
| Container Apps + Environment | 5 |
| Container Registry | 1 |
| Managed Identities | 6 |
| Storage Accounts | 7 |
| Log Analytics Workspaces | 4 |
| Application Insights | 3 |
| Private Endpoints + NICs | 6 |
| Private DNS Zones | 8 |
| DNS Zones | 2 |
| Databases | 1 (PostgreSQL Flexible) |
| AI Services | 4 (Foundry, Databricks, Doc Intelligence, AI Search) |
| Security | 3 (Key Vault, Backup Vault, Purview) |
| Networking | 3 (VNet, NSG, Network Watcher) |
| Realtime | 3 (Redis, SignalR, Communication Services) |
| Other | 7 (Action Groups, Event Hubs, Access Connector) |
| **Total** | **63** |

---

## Resource Groups

| Resource Group | Purpose | Resources |
|----------------|---------|-----------|
| `rg-ipai-dev-odoo-sea` | Transaction plane — Odoo runtime | ACA Env, 4 Container Apps |
| `rg-ipai-dev-ai-sea` | Intelligence plane — AI/ML | Foundry project, Databricks, Doc Intelligence, AI Search |
| `rg-ipai-data-sea` | Data plane — persistence | PostgreSQL, 6 Storage Accounts |
| `rg-ipai-dev-security-sea` | Security — identity + secrets | Key Vault, 5 MIs, Backup Vault |
| `rg-ipai-dev-net-sea` | Networking — zero-trust | VNet, PEs, Private DNS, DNS Zones |
| `rg-ipai-dev-mon-sea` | Observability | 3 App Insights, 4 Log Analytics, 2 Action Groups |
| `rg-ipai-dev-realtime` | Real-time services | Redis, SignalR, Communication Services |
| `rg-ipai-shared` | Shared infrastructure | Container Registry |
| `rg-ipai-dev-dbw-managed` | Databricks managed (auto) | Access Connector, Storage, VNet, NSG, Event Hubs |
| `managed-rg-pv-ipai-dev-sea` | Purview managed (auto) | Event Hubs, Storage |
| `NetworkWatcherRG` | Azure default | Network Watcher |

---

## Transaction Plane

| Resource | Type | RG | Region |
|----------|------|-----|--------|
| `acae-ipai-dev-sea` | Container Apps Environment | rg-ipai-dev-odoo-sea | Southeast Asia |
| `ipai-odoo-dev` | Container App | rg-ipai-dev-odoo-sea | Southeast Asia |
| `ipai-prismalab` | Container App | rg-ipai-dev-odoo-sea | Southeast Asia |
| `ipai-w9studio` | Container App | rg-ipai-dev-odoo-sea | Southeast Asia |
| `ipai-website` | Container App | rg-ipai-dev-odoo-sea | Southeast Asia |
| `acripaiodoo` | Container Registry | rg-ipai-shared | Southeast Asia |

---

## Intelligence Plane

| Resource | Type | RG | Region |
|----------|------|-----|--------|
| `ipai-copilot-resource` | Foundry | rg-ipai-dev-ai-sea | East US 2 |
| `ipai-copilot` | Foundry Project | rg-ipai-dev-ai-sea | East US 2 |
| `dbw-ipai-dev` | Azure Databricks Service | rg-ipai-dev-ai-sea | Southeast Asia |
| `docai-ipai-dev` | Document Intelligence | rg-ipai-dev-ai-sea | Southeast Asia |
| `srch-ipai-dev-sea` | Search Service | rg-ipai-dev-ai-sea | Southeast Asia |

---

## Data Plane

| Resource | Type | RG | Region |
|----------|------|-----|--------|
| `pg-ipai-odoo` | PostgreSQL Flexible Server | rg-ipai-data-sea | Southeast Asia |
| `stdevipai` | Storage Account | rg-ipai-dev-data-sea | Southeast Asia |
| `stipaidevagent` | Storage Account (agent) | rg-ipai-dev-data-sea | Southeast Asia |
| `stipaidevbkp` | Storage Account (backup) | rg-ipai-dev-data-sea | Southeast Asia |
| `stipaidevlake` | Storage Account (lake) | rg-ipai-dev-data-sea | Southeast Asia |
| `stipaidevlogs` | Storage Account (logs) | rg-ipai-dev-data-sea | Southeast Asia |
| `stlkipaidev` | Storage Account (lakehouse) | rg-ipai-dev-data-sea | Southeast Asia |

---

## Security Plane

| Resource | Type | RG | Region |
|----------|------|-----|--------|
| `kv-ipai-dev-sea` | Key Vault | rg-ipai-dev-security-sea | Southeast Asia |
| `id-ipai-dev` | Managed Identity (platform) | rg-ipai-dev-security-sea | Southeast Asia |
| `id-ipai-dev-agent` | Managed Identity (agent) | rg-ipai-dev-security-sea | Southeast Asia |
| `id-ipai-dev-data` | Managed Identity (data) | rg-ipai-dev-security-sea | Southeast Asia |
| `id-ipai-dev-pipeline` | Managed Identity (pipeline) | rg-ipai-dev-security-sea | Southeast Asia |
| `id-ipai-dev-runtime` | Managed Identity (runtime) | rg-ipai-dev-security-sea | Southeast Asia |
| `bvault-ipai-dev-sea` | Backup Vault | rg-ipai-dev-security-sea | Southeast Asia |
| `pv-ipai-dev-sea` | Microsoft Purview | rg-ipai-dev-security-sea | Southeast Asia |

---

## Networking Plane

| Resource | Type | RG | Region |
|----------|------|-----|--------|
| `vnet-ipai-dev-sea` | Virtual Network | rg-ipai-dev-net-sea | Southeast Asia |
| `insightpulseai.com` | DNS Zone | rg-ipai-dev-net-sea | Global |
| `w9studio.net` | DNS Zone | rg-ipai-dev-net-sea | Global |
| `pe-ipai-dev-kv` | Private Endpoint (Key Vault) | rg-ipai-dev-net-sea | Southeast Asia |
| `pe-ipai-dev-pg` | Private Endpoint (PostgreSQL) | rg-ipai-dev-net-sea | Southeast Asia |
| `pe-ipai-dev-search` | Private Endpoint (AI Search) | rg-ipai-dev-net-sea | Southeast Asia |

### Private DNS Zones

| Zone | Purpose |
|------|---------|
| `privatelink.applicationinsights.azure.com` | App Insights |
| `privatelink.azurecr.io` | Container Registry |
| `privatelink.blob.core.windows.net` | Blob Storage |
| `privatelink.cognitiveservices.azure.com` | AI Services |
| `privatelink.postgres.database.azure.com` | PostgreSQL |
| `privatelink.search.windows.net` | AI Search |
| `privatelink.servicebus.windows.net` | Service Bus |
| `privatelink.vaultcore.azure.net` | Key Vault |

---

## Observability Plane

| Resource | Type | RG | Region |
|----------|------|-----|--------|
| `appi-ipai-dev` | Application Insights (platform) | rg-ipai-dev-mon-sea | Southeast Asia |
| `appi-ipai-dev-agent-sea` | Application Insights (agent) | rg-ipai-dev-mon-sea | Southeast Asia |
| `appi-ipai-dev-runtime-sea` | Application Insights (runtime) | rg-ipai-dev-mon-sea | Southeast Asia |
| `log-ipai-dev-sea` | Log Analytics (platform) | rg-ipai-dev-mon-sea | Southeast Asia |
| `log-ipai-dev-agent-sea` | Log Analytics (agent) | rg-ipai-dev-mon-sea | Southeast Asia |
| `log-ipai-dev-data-sea` | Log Analytics (data) | rg-ipai-dev-mon-sea | Southeast Asia |
| `log-ipai-dev-runtime-sea` | Log Analytics (runtime) | rg-ipai-dev-mon-sea | Southeast Asia |
| `ag-ipai-dev-sea` | Action Group | rg-ipai-dev-mon-sea | Global |
| `Application Insights Smart Detection` | Action Group | rg-ipai-dev-mon-sea | Global |

---

## Realtime Plane

| Resource | Type | RG | Region |
|----------|------|-----|--------|
| `redis-ipai-dev-sea` | Azure Cache for Redis | rg-ipai-dev-realtime | Southeast Asia |
| `sigr-ipai-dev-sea` | SignalR | rg-ipai-dev-realtime | Southeast Asia |
| `acs-ipai-dev-sea` | Communication Services | rg-ipai-dev-realtime | Global |

---

## Databricks Managed (Auto-provisioned)

| Resource | Type | RG |
|----------|------|-----|
| `unity-catalog-access-connector` | Access Connector for Databricks | rg-ipai-dev-dbw-managed |
| `dbstorageqba5raeuajc6u` | Storage Account | rg-ipai-dev-dbw-managed |
| `dbmanagedidentity` | Managed Identity | rg-ipai-dev-dbw-managed |
| `workers-vnet` | Virtual Network | rg-ipai-dev-dbw-managed |
| `workers-sg` | Network Security Group | rg-ipai-dev-dbw-managed |
| `Atlas-e613d16b-...` | Event Hubs Namespace | managed-rg-pv-ipai-dev-sea |
| `scansoutheastasia...` | Storage Account (Purview scan) | managed-rg-pv-ipai-dev-sea |

---

## Naming Convention Compliance

All resources follow `{type}-ipai-{env}-{purpose?}-{region}` pattern per [azure-naming-convention.md](azure-naming-convention.md). Exceptions are auto-provisioned Databricks/Purview managed resources which follow Azure defaults.

---

*Snapshot: 2026-04-18 | Source: Azure Portal All Resources (63 results)*
