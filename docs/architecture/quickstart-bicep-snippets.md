# Quick-Deploy Bicep Snippets — BOM Production Gap Closure

> **Purpose:** Copy-paste-deployable AVM-based Bicep snippets for the 4 production-readiness gaps identified vs Microsoft's `Deploy-Your-AI-Application-In-Production` reference.
>
> **Pin policy:** All AVM module versions verified against `mcr.microsoft.com` registry on 2026-04-14 (latest available).
>
> **Pattern:** Every snippet uses Azure Verified Modules (`br/public:avm/res/*`) per `CLAUDE.md` § Engineering Execution Doctrine — reuse upstream first, build only the thin delta.

---

## Gap inventory

| # | Gap | ADO Issue | Iteration | AVM module |
|---|---|---|---|---|
| 1 | Azure AI Search | #624 | R3 | `avm/res/search/search-service@0.9.2` |
| 2 | Action Group + alerts | #625 | R3 | `avm/res/insights/action-group@0.8.0` |
| 3 | Microsoft Purview | #627 | R3 | `avm/res/purview/account@0.9.2` |
| 4 | Private Endpoints + DNS | #626 | R3 | `avm/res/network/private-endpoint@0.9.1` + `avm/res/network/private-dns-zone@0.8.1` |

---

## Reference repos (canonical Microsoft sources)

| Repo | Purpose | Use |
|---|---|---|
| **`microsoft/Deploy-Your-AI-Application-In-Production`** | Full AI Landing Zone deployment wrapper (azd up) | End-to-end blueprint; **too heavy** for IPAI's incremental approach |
| **`Azure/bicep-ptn-aiml-landing-zone`** | AI Landing Zone Bicep pattern (the substrate DYAIP wraps) | Reference for VNet/subnet model + Foundry pattern |
| **`Azure/bicep-registry-modules`** | AVM source — all individual resource modules | **Primary source** — IPAI consumes per snippet below |
| **`Azure-Samples/azure-search-openai-demo`** | AI Search + Foundry RAG reference | Index schema patterns |

**Decision:** IPAI uses **per-resource AVM modules** (snippets below) instead of importing the full landing zone wrapper. Each gap deploys independently with `az deployment group create`. No subnet redesign required for R3.

---

## Snippet 1 — Azure AI Search (Issue #624)

**File:** `infra/azure/modules/ai-search.bicep` (review existing or rewrite)

```bicep
// =====================================================
// Azure AI Search — RAG backbone for Plane B agents
// AVM: avm/res/search/search-service@0.9.2
// =====================================================
targetScope = 'resourceGroup'

param prefix     string
param env        string
param location   string
param tags       object
param sku        string = 'standard'           // 'basic' for dev, 'standard' for prod
param replicaCount int  = 1
param partitionCount int = 1

@description('Storage account resource ID for indexing artifacts.')
param storageAccountResourceId string

@description('Log Analytics workspace resource ID for diagnostics.')
param logAnalyticsWorkspaceId string

@description('Pulser agents managed identity principal ID (Search Index Data Reader).')
param pulserAgentsPrincipalId string

var searchName = 'srch-${prefix}-${env}-sea'

module aiSearch 'br/public:avm/res/search/search-service:0.9.2' = {
  name: 'avm-search-${searchName}'
  params: {
    name:              searchName
    location:          location
    tags:              tags
    sku:               sku
    replicaCount:      replicaCount
    partitionCount:    partitionCount
    publicNetworkAccess: 'Enabled'   // Set to 'Disabled' when private endpoint added (R3 hardening)
    managedIdentities:   { systemAssigned: true }
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspaceId
        logCategoriesAndGroups: [{ categoryGroup: 'allLogs' }]
        metricCategories: [{ category: 'AllMetrics' }]
      }
    ]
    roleAssignments: [
      {
        principalId:       pulserAgentsPrincipalId
        roleDefinitionIdOrName: 'Search Index Data Reader'
      }
    ]
  }
}

output searchServiceId   string = aiSearch.outputs.resourceId
output searchServiceName string = aiSearch.outputs.name
output searchPrincipalId string = aiSearch.outputs.systemAssignedMIPrincipalId
```

**Deploy:**
```bash
az deployment group create \
  --resource-group rg-ipai-dev-ai-sea \
  --template-file infra/azure/modules/ai-search.bicep \
  --parameters prefix=ipai env=dev location=southeastasia \
    storageAccountResourceId=$(az storage account show -n stdevipai -g rg-ipai-dev-data-sea --query id -o tsv) \
    logAnalyticsWorkspaceId=$(az monitor log-analytics workspace show -n log-ipai-dev-sea -g rg-ipai-dev-mon-sea --query id -o tsv) \
    pulserAgentsPrincipalId=$(az identity show -n id-ipai-dev -g rg-ipai-dev-security-sea --query principalId -o tsv) \
    tags='{"org":"ipai","env":"dev","platform":"pulser-odoo","plane":"data","workload":"agent-rag"}'
```

---

## Snippet 2 — Action Group + baseline alerts (Issue #625)

**File:** `infra/azure/modules/action-group.bicep` (NEW — does not exist yet)

```bicep
// =====================================================
// Azure Monitor Action Group — alert routing baseline
// AVM: avm/res/insights/action-group@0.8.0
// =====================================================
targetScope = 'resourceGroup'

param prefix      string
param env         string
param location    string = 'global'                 // Action Groups are global resources
param tags        object
@description('Email recipients for alerts.')
param emailRecipients array = [
  { name: 'ops', emailAddress: 'ops@insightpulseai.com' }
]
@description('Slack webhook URL (stored in Key Vault, retrieved at deploy time).')
@secure()
param slackWebhookUrl string

var agName = 'ag-${prefix}-${env}-sea'

module actionGroup 'br/public:avm/res/insights/action-group:0.8.0' = {
  name: 'avm-ag-${agName}'
  params: {
    name:        agName
    location:    location
    tags:        tags
    groupShortName: 'ipai-${env}'
    enabled:     true
    emailReceivers: [
      for r in emailRecipients: {
        name:                 r.name
        emailAddress:         r.emailAddress
        useCommonAlertSchema: true
      }
    ]
    webhookReceivers: [
      {
        name:               'slack-ipai-alerts'
        serviceUri:         slackWebhookUrl
        useCommonAlertSchema: true
      }
    ]
  }
}

output actionGroupId   string = actionGroup.outputs.resourceId
output actionGroupName string = actionGroup.outputs.name
```

**Companion alert rules** (separate file `infra/azure/modules/baseline-alerts.bicep`):
- ACA app errors > threshold (Log Analytics scheduled query rule)
- PostgreSQL connection saturation (metric alert)
- Front Door 5xx rate spike (metric alert)
- Resource deletion in production RG (activity log alert)
- Service Health alert (activity log alert)
- Cost budget threshold (subscription budget)

**Deploy:**
```bash
SLACK_WEBHOOK=$(az keyvault secret show --vault-name kv-ipai-dev-sea --name slack-webhook-alerts --query value -o tsv)
az deployment group create \
  --resource-group rg-ipai-dev-mon-sea \
  --template-file infra/azure/modules/action-group.bicep \
  --parameters prefix=ipai env=dev slackWebhookUrl="$SLACK_WEBHOOK" \
    tags='{"org":"ipai","env":"dev","platform":"pulser-odoo","plane":"observability","workload":"alerting"}'
```

---

## Snippet 3 — Microsoft Purview (Issue #627)

**File:** `infra/azure/modules/purview.bicep` (NEW)

```bicep
// =====================================================
// Microsoft Purview — governance, lineage, DSPM
// AVM: avm/res/purview/account@0.9.2
// =====================================================
targetScope = 'resourceGroup'

param prefix    string
param env       string
param location  string
param tags      object

@description('Public network access. Disable for production (private endpoint required).')
param publicNetworkAccess string = 'Enabled'   // Switch to 'Disabled' when PE added

@description('Admin user/group object IDs for Purview Collection Admin role.')
param collectionAdmins array = []

var purviewName = 'pv-${prefix}-${env}-sea'

module purview 'br/public:avm/res/purview/account:0.9.2' = {
  name: 'avm-purview-${purviewName}'
  params: {
    name:                 purviewName
    location:             location
    tags:                 tags
    publicNetworkAccess:  publicNetworkAccess
    managedIdentities:    { systemAssigned: true }
    roleAssignments: [
      for admin in collectionAdmins: {
        principalId:            admin
        roleDefinitionIdOrName: 'Purview Data Curator'
      }
    ]
  }
}

output purviewAccountId   string = purview.outputs.resourceId
output purviewAccountName string = purview.outputs.name
output purviewPrincipalId string = purview.outputs.systemAssignedMIPrincipalId
```

**Post-deploy steps (NOT Bicep — portal/CLI):**
1. Create collections (`ipai → plane → workload`)
2. Register data sources (ADLS x3, PostgreSQL, Databricks, Foundry)
3. Configure scan rule sets + classifications
4. First scan run

**Deploy:**
```bash
az deployment group create \
  --resource-group rg-ipai-dev-security-sea \
  --template-file infra/azure/modules/purview.bicep \
  --parameters prefix=ipai env=dev location=southeastasia \
    collectionAdmins='["<admin-object-id>"]' \
    tags='{"org":"ipai","env":"dev","platform":"pulser-odoo","plane":"governance","workload":"purview"}'
```

---

## Snippet 4 — Private Endpoint + Private DNS Zone pattern (Issue #626)

**File:** `infra/azure/modules/private-endpoint-pattern.bicep` (NEW reusable pattern)

```bicep
// =====================================================
// Reusable Private Endpoint + DNS Zone pattern
// AVM: avm/res/network/private-endpoint@0.9.1
//      avm/res/network/private-dns-zone@0.8.1
// =====================================================
targetScope = 'resourceGroup'

param prefix             string
param env                string
param location           string
param tags               object

@description('Target resource ID to expose privately (e.g., Key Vault, Storage, Search).')
param targetResourceId string

@description('groupId / sub-resource for the target service. e.g. "vault" for KV, "blob" for Storage, "searchService" for Search.')
param groupId string

@description('Private DNS zone name for the service. e.g. "privatelink.vaultcore.azure.net".')
param privateDnsZoneName string

@description('Subnet resource ID for the private endpoint (must be in PE-dedicated subnet).')
param peSubnetResourceId string

@description('VNet resource ID to link the private DNS zone to.')
param vnetResourceId string

var peName = 'pe-${prefix}-${env}-${groupId}'

// Private DNS zone (idempotent — create once per zone name across all PE deploys)
module dnsZone 'br/public:avm/res/network/private-dns-zone:0.8.1' = {
  name: 'avm-dns-${replace(privateDnsZoneName, '.', '-')}'
  params: {
    name:    privateDnsZoneName
    tags:    tags
    virtualNetworkLinks: [
      {
        registrationEnabled:    false
        virtualNetworkResourceId: vnetResourceId
      }
    ]
  }
}

// Private endpoint
module pe 'br/public:avm/res/network/private-endpoint:0.9.1' = {
  name: 'avm-pe-${peName}'
  params: {
    name:     peName
    location: location
    tags:     tags
    subnetResourceId: peSubnetResourceId
    privateLinkServiceConnections: [
      {
        name: '${peName}-conn'
        properties: {
          privateLinkServiceId: targetResourceId
          groupIds:             [groupId]
        }
      }
    ]
    privateDnsZoneGroup: {
      privateDnsZoneGroupConfigs: [
        {
          name:                'config1'
          privateDnsZoneResourceId: dnsZone.outputs.resourceId
        }
      ]
    }
  }
}

output peId      string = pe.outputs.resourceId
output dnsZoneId string = dnsZone.outputs.resourceId
```

**Deploy per service** (Key Vault example):
```bash
KV_ID=$(az keyvault show -n kv-ipai-dev-sea -g rg-ipai-dev-security-sea --query id -o tsv)
VNET_ID=$(az network vnet show -n vnet-ipai-dev-sea -g rg-ipai-dev-network-sea --query id -o tsv)
PE_SUBNET=$(az network vnet subnet show -n pe-subnet --vnet-name vnet-ipai-dev-sea -g rg-ipai-dev-network-sea --query id -o tsv)

az deployment group create \
  --resource-group rg-ipai-dev-security-sea \
  --template-file infra/azure/modules/private-endpoint-pattern.bicep \
  --parameters prefix=ipai env=dev location=southeastasia \
    targetResourceId="$KV_ID" \
    groupId=vault \
    privateDnsZoneName=privatelink.vaultcore.azure.net \
    peSubnetResourceId="$PE_SUBNET" \
    vnetResourceId="$VNET_ID" \
    tags='{"org":"ipai","env":"dev","platform":"pulser-odoo","plane":"security","workload":"private-endpoint"}'
```

**8 PE deployments needed** (per Issue #626):

| Service | groupId | DNS zone |
|---|---|---|
| Key Vault | `vault` | `privatelink.vaultcore.azure.net` |
| Storage (×3) | `blob` | `privatelink.blob.core.windows.net` |
| PostgreSQL | `postgresqlServer` | `privatelink.postgres.database.azure.com` |
| Container Registry | `registry` | `privatelink.azurecr.io` |
| AI Search | `searchService` | `privatelink.search.windows.net` |
| App Insights | `azuremonitor` | `privatelink.applicationinsights.azure.com` |
| Service Bus | `namespace` | `privatelink.servicebus.windows.net` |
| Foundry (cross-sub) | `account` | `privatelink.cognitiveservices.azure.com` |

---

## Deployment order (R3 hardening — recommended sequence)

| Phase | Action | Risk | Issue |
|---|---|---|---|
| **R3 W1** | Deploy Action Group + 6 baseline alerts (no infra change) | LOW | #625 |
| **R3 W1** | Deploy AI Search standalone (additive, public access) | LOW | #624 |
| **R3 W2** | Define Foundry connection record for AI Search | LOW | #624 |
| **R3 W3** | Deploy Purview account (additive, public access) | LOW | #627 |
| **R3 W3** | Register Purview source connections | MED | #627 |
| **R3 W4** | Add PE-only subnet to existing VNet | LOW | #626 |
| **R3 W4** | Deploy private DNS zones (8) — additive | LOW | #626 |
| **R3 W5** | Deploy private endpoints for KV / Storage / PG (one-by-one + verify) | MED | #626 |
| **R3 W6** | Lock down public access on KV / Storage / PG | **HIGH** | #626 |
| **R3 W7** | Repeat PE pattern for Search / ACR / Service Bus / Foundry | MED | #626 |
| **R3 W8** | ACA recreate with `internal=true` + Front Door Premium upgrade | **HIGH** | #626 |

---

## Validation per snippet

Each snippet must pass:

```bash
# Bicep syntax
az bicep build --file <snippet>.bicep

# What-if dry-run before deploy
az deployment group what-if \
  --resource-group <target-rg> \
  --template-file <snippet>.bicep \
  --parameters @<snippet>.bicepparam

# Post-deploy: verify resource health
az resource show --ids <new-resource-id> --query "properties.provisioningState"
```

---

## Anchors

- ADO Issues: #624 (AI Search), #625 (Action Group), #626 (PE+DNS), #627 (Purview)
- AVM source: [`Azure/bicep-registry-modules`](https://github.com/Azure/bicep-registry-modules)
- Reference architecture: [`microsoft/Deploy-Your-AI-Application-In-Production`](https://github.com/microsoft/Deploy-Your-AI-Application-In-Production)
- AI Landing Zone: [`Azure/bicep-ptn-aiml-landing-zone`](https://github.com/Azure/bicep-ptn-aiml-landing-zone)
- Adoption register: `ssot/governance/upstream-adoption-register.yaml` (`Azure/bicep-registry-modules` = consume_directly)
- BOM: `ssot/azure/bom.yaml` (R3 prereq trajectory)
- CLAUDE.md § Engineering Execution Doctrine
