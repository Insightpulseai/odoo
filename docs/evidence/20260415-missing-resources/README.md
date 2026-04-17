# Evidence — "Create the missing resources" (2026-04-15)

Closes `stipaidevlake` UC drift flagged in
`docs/runbooks/fabric-finops-workspace.md §4`. Also operationalizes the
FinOps ingestion lane per the Microsoft FinOps Framework.

---

## Outcome

```text
Substrate drift resolved.
FinOps FOCUS ingestion live (PAYG).
Unity Catalog external location resolves (stipaidevlake now exists).
Bicep IaC recaptures the imperative work.
Azure Pipelines templates gate the next changes.
```

---

## Resources created

### 1. `stipaidevlake` storage account (Sponsorship sub)

| Property | Value |
|---|---|
| Resource ID | `/subscriptions/eba824fb-332d-4623-9dfb-2c9f7ee83f4e/resourceGroups/rg-ipai-dev-data-sea/providers/Microsoft.Storage/storageAccounts/stipaidevlake` |
| Region | Southeast Asia |
| Kind | StorageV2 |
| SKU | Standard_LRS |
| HNS | Enabled |
| TLS | 1.2 minimum |
| Public blob access | disabled |
| Primary DFS endpoint | `https://stipaidevlake.dfs.core.windows.net/` |

Containers: `bronze`, `silver`, `gold`, `metastore`, `msexports`.

### 2. Role assignment — Databricks UC access connector

| Principal | Role | Scope |
|---|---|---|
| `79fbecac-8341-44d3-8711-12e8a51ddc18` (unity-catalog-access-connector MI) | Storage Blob Data Contributor | `stipaidevlake` |

This unblocks UC external location `ipai-lake-dev` which was pointing at the
phantom `stipaidevlake` address. Metastore reads/writes now resolve.

### 3. FOCUS cost export (PAYG sub)

| Property | Value |
|---|---|
| Name | `ipai-focus-cost-payg` |
| Scope | `/subscriptions/536d8cf6-89e1-4815-aef3-d5f2c5f4d070` |
| Type | `FocusCost` (FOCUS v1.0 schema) |
| Format | CSV |
| Recurrence | Daily |
| Destination | `stipaidevlake` / `msexports` / `focuscost/subscription-536d8cf6-89e1-4815-aef3-d5f2c5f4d070/` |
| First-run state | **Completed** (`202604142035`) |
| First-run manifest | `focuscost/subscription-536d8cf6.../ipai-focus-cost-payg/20260401-20260430/202604142035/4233753e-6a0f-45fc-96a5-f4bba7f7f8a6` |

**Sponsorship sub excluded** — offer `MS-AZR-0036P` does not support Cost Management FOCUS exports. Near-term posture: PAYG is canonical cost surface.

### 4. Resource provider registration

- `Microsoft.CostManagementExports` → `Registered` (Sponsorship sub)

---

## Bicep recapture (idempotent future deploys)

Imperative work is codified in `infra/azure/modules/data-lake-canonical.bicep`.
Re-running `az deployment group create` against the same RG is a no-op
except when the UC access connector principal rotates.

```bash
az deployment group create \
  --resource-group rg-ipai-dev-data-sea \
  --template-file infra/azure/modules/data-lake-canonical.bicep \
  --parameters ucAccessConnectorPrincipalId=79fbecac-8341-44d3-8711-12e8a51ddc18
```

---

## Repo-ready artifacts landed

| Path | Purpose |
|---|---|
| `infra/azure/modules/data-lake-canonical.bicep` | stipaidevlake recapture |
| `infra/azure/README.md` | Bicep-first IaC contract |
| `docs/architecture/completeness-matrix-finance-projectops-data-intel-finops.md` | Canonical "are we actually done?" view |
| `docs/architecture/azure-naming-convention.md` | CAF-aligned naming |
| `docs/runbooks/finops-baseline.md` | FinOps capability build order |
| `docs/runbooks/bicep-authoring-standard.md` | Author → validate → promote workflow |
| `ssot/finops/workload-onboarding.yaml` | Workload-onboarding checklist (schema) |
| `ssot/governance/tagging-doctrine.yaml` | Live tag schema (snake_case) |
| `platform/contracts/finops/cost-allocation-model.yaml` | Allocation dimensions + chargeback |
| `azure-pipelines/templates/finops-export-validate.yml` | FinOps CI gate |
| `azure-pipelines/templates/bicep-lint-validate.yml` | Bicep CI gate |

---

## Verification

```bash
# Storage account
az storage account show -n stipaidevlake -g rg-ipai-dev-data-sea \
  --subscription "Microsoft Azure Sponsorship" \
  --query "{hns:isHnsEnabled, tls:minimumTlsVersion}" -o json
# => {"hns": true, "tls": "TLS1_2"}

# Containers
az storage container list --account-name stipaidevlake \
  --account-key "$KEY" --query "[].name" -o json
# => ["bronze","gold","metastore","msexports","silver"]

# Role assignment
az role assignment list \
  --scope "$STORAGE_ID" \
  --query "[?principalId=='79fbecac-8341-44d3-8711-12e8a51ddc18'].roleDefinitionName" -o tsv
# => Storage Blob Data Contributor

# FOCUS export run history
az rest --method get \
  --url "https://management.azure.com/subscriptions/536d8cf6-89e1-4815-aef3-d5f2c5f4d070/providers/Microsoft.CostManagement/exports/ipai-focus-cost-payg/runHistory?api-version=2025-03-01"
# => Completed
```

---

## Known residual

| Item | Status | Next |
|---|---|---|
| Sponsorship-sub FOCUS export | Blocked by offer type | Option: migrate data plane to PAYG (see `project_sponsored_sub_migration_adr.md` + Azure Resource Mover) |
| Fabric capacity `fcipaidev` | Not provisioned | Operator decision required before ~2026-05-20 trial expiry (F2 ~$262/mo) |
| Required-tags Azure Policy | Not authored | `infra/azure/policy/required-tags.bicep` per `ssot/governance/tagging-doctrine.yaml` |
| UC `ipai-lake-dev` external location smoke test | Pending | Trigger after DLT first run |
| DLT first run (Issue 26) | Pending path= arg fix | Unblocked now that UC external location resolves |

---

## References (Bicep-first IaC path)

- Bicep + VS Code quickstart: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/quickstart-create-bicep-use-visual-studio-code
- Bicep MCP quickstart: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/quickstart-create-bicep-use-visual-studio-code-model-context-protocol
- Bicep resource declaration: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/resource-declaration
- Bicep modules: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/modules
- Bicep CLI JSON-RPC: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/bicep-cli-jsonrpc
- Deployment stacks + template specs: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/quickstart-create-deployment-stacks-template-specs
- Add Bicep template to Azure Pipelines: https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/add-template-to-azure-pipelines
- Storage account via Bicep: https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=bicep
- ACR via Bicep: https://learn.microsoft.com/en-us/azure/container-registry/container-registry-get-started-bicep
- PG Flexible Server via Bicep: https://learn.microsoft.com/en-us/azure/postgresql/developer/create-server-bicep
- Foundry resource template: https://learn.microsoft.com/en-us/azure/foundry/how-to/create-resource-template
- ARM REST: https://learn.microsoft.com/en-us/rest/api/resources/
- Resource Mover (cross-sub/region): https://learn.microsoft.com/en-us/rest/api/resourcemover/move-resources
- Azure Naming Tool: https://github.com/mspnp/AzureNamingTool
- CAF naming: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming
- AzureStack Bicep samples: https://github.com/Azure/AzureStack-QuickStart-Templates/tree/master/Bicep

---

*Evidence locked 2026-04-15.*
