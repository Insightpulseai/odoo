# Azure Startup Evidence Contract

> Defines the evidence requirements for Phase 0 (Landing Zone) completion.
> All Azure deployment tasks must produce evidence per this contract.

---

## Scope

This contract covers Phase 0 of `spec/azure-target-state/plan.md`:
- T0.1: Resource Group hierarchy
- T0.2: Key Vault (RBAC mode)
- T0.3: Log Analytics Workspace + Application Insights
- T0.4: Managed Identities (platform + ACA)
- T0.5: VNet + NSGs

---

## Evidence Path

```
web/docs/evidence/<YYYYMMDD-HHMM+0800>/azure-phase0/
├── logs/
│   ├── deploy.log          # az deployment output
│   ├── verify.log          # post-deployment verification
│   └── ssot-update.log     # git diff of ssot/azure/resources.yaml
└── summary.json            # structured completion record
```

Timezone: Asia/Manila (UTC+08:00).

---

## Required Evidence Fields (summary.json)

```json
{
  "status": "COMPLETE | PARTIAL | BLOCKED",
  "phase": 0,
  "tasks_completed": ["T0.1", "T0.2"],
  "deployment": {
    "name": "<az deployment name>",
    "subscription_id": "<subscription UUID>",
    "location": "southeastasia",
    "template": "infra/azure/platform/main.bicep",
    "timestamp": "<ISO8601+0800>"
  },
  "resources": {
    "resource_groups": [
      "rg-ipai-platform-dev",
      "rg-ipai-agents-dev",
      "rg-ipai-integration-dev"
    ],
    "key_vault": {
      "name": "kv-ipai-platform-dev",
      "resource_group": "rg-ipai-platform-dev"
    },
    "log_analytics": {
      "workspace_id": "<LAW resource ID>",
      "name": "law-ipai-dev"
    },
    "app_insights": {
      "name": "appi-ipai-dev",
      "connection_string_ref": "kv-ipai-platform-dev/appinsights-connection-string"
    },
    "managed_identities": {
      "platform": {
        "name": "id-ipai-platform-dev",
        "principal_id": "<UUID>"
      },
      "aca": {
        "name": "id-ipai-aca-dev",
        "principal_id": "<UUID>"
      }
    }
  },
  "commit_sha": "<git SHA>",
  "evidence_path": "web/docs/evidence/<stamp>/azure-phase0/"
}
```

---

## Acceptance Criteria

Phase 0 is complete when ALL of the following are true:

1. All 3 resource groups exist in Azure (`az group show` succeeds)
2. Key Vault `kv-ipai-platform-dev` exists with RBAC access model
3. Log Analytics Workspace `law-ipai-dev` exists and accepts writes
4. Application Insights `appi-ipai-dev` connected to LAW
5. Managed identities `id-ipai-platform-dev` and `id-ipai-aca-dev` exist with correct role assignments
6. All Phase 0 resources in `ssot/azure/resources.yaml` updated from `source: pending` to `source: confirmed`
7. Evidence bundle committed at canonical path with `summary.json` status = `COMPLETE`

---

## Verification Commands

```bash
# T0.1: Resource Groups
az group show --name rg-ipai-platform-dev --query "properties.provisioningState" -o tsv
az group show --name rg-ipai-agents-dev --query "properties.provisioningState" -o tsv
az group show --name rg-ipai-integration-dev --query "properties.provisioningState" -o tsv

# T0.2: Key Vault
az keyvault show --name kv-ipai-platform-dev --query "properties.enableRbacAuthorization" -o tsv

# T0.3: Log Analytics + App Insights
az monitor log-analytics workspace show --resource-group rg-ipai-platform-dev --workspace-name law-ipai-dev --query "customerId" -o tsv
az monitor app-insights component show --app appi-ipai-dev --resource-group rg-ipai-platform-dev --query "connectionString" -o tsv

# T0.4: Managed Identities
az identity show --name id-ipai-platform-dev --resource-group rg-ipai-platform-dev --query "principalId" -o tsv
az identity show --name id-ipai-aca-dev --resource-group rg-ipai-agents-dev --query "principalId" -o tsv
```

---

## SSOT Update Rule

After successful deployment, update `ssot/azure/resources.yaml`:
- Change `source: pending` → `source: confirmed` for each verified resource
- Add `confirmed_date: <YYYY-MM-DD>` field
- Commit the SSOT update in the same PR as the evidence bundle
