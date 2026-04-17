# Runbook — Bicep authoring standard

> Canonical rules for authoring, validating, and promoting Bicep IaC in this repo.
> Confirms Microsoft's preferred workflow: VS Code authoring → Azure CLI validation → Azure Pipelines promotion.
> Reference:
>   https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/quickstart-create-bicep-use-visual-studio-code
>   https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/quickstart-create-bicep-use-visual-studio-code-model-context-protocol
>   https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/add-template-to-azure-pipelines
>   https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/bicep-cli-jsonrpc
>   https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/modules
> Locked 2026-04-15.

---

## 1. Doctrine

```text
Author in VS Code with the Bicep extension.
Validate with Azure CLI locally.
Promote with Azure Pipelines only.
Use Bicep MCP only as an assistive authoring surface, not as authority.
Do not use portal-only resource creation as the canonical path.
```

Bicep is the default Azure IaC language for this repo. Terraform is retained **only** where the upstream we reuse ships Terraform (e.g., `microsoft/unified-data-foundation`). New IPAI-authored IaC is Bicep.

---

## 2. Roles of each surface

| Surface | Role | When to use |
|---|---|---|
| **VS Code + Bicep extension 0.40.2+** | Primary human authoring | All new or edited `.bicep` / `.bicepparam` |
| **Bicep MCP server** (auto-installed with extension 0.40.2+) | AI-assisted authoring (optional) | Getting latest API versions, param-file generation, deployment snapshots |
| **Azure CLI** | Local validation + ad-hoc deploy | `az bicep build`, `az deployment group validate`, `az deployment group what-if` |
| **Azure Pipelines** | Promotion authority (sole CI/CD path) | All deploys to dev / staging / prod |
| **Portal** | Read-only / discovery / debug | Never as canonical creation path |

---

## 3. Required file layout

Every Azure deployment follows this shape:

```
infra/azure/
├── README.md                           # repo contract (below)
├── main.bicep                          # subscription-scope composition (where relevant)
├── modules/
│   ├── <module>.bicep                  # reusable module
│   └── <module>.bicepparam             # per-env parameter file (optional)
├── parameters/
│   └── <env>.bicepparam                # environment-specific overrides
└── examples/
    └── <scenario>/                     # minimal runnable samples for docs
```

Rule — every Azure resource definition should have:
- a `main.bicep` or module-level `.bicep` entrypoint
- a `.bicepparam` file where environment values differ
- no portal-only drift accepted as canonical

---

## 4. Authoring workflow

1. Open repo in VS Code (Bicep extension 0.40.2+ installed; see devcontainer).
2. Create or open the target `.bicep` under `infra/azure/`.
3. Lean on IntelliSense for resource shapes, API versions, type safety.
4. Optionally invoke Bicep MCP:
   - `"Update API versions to the latest."`
   - `"Create a Bicep parameters file with all the parameters defined in the Bicep file."`
   - `"Get a snapshot of the deployment."`
5. Validate locally:
   ```bash
   az bicep build --file infra/azure/modules/<name>.bicep
   az deployment group validate \
     --resource-group <rg> \
     --template-file infra/azure/modules/<name>.bicep \
     --parameters infra/azure/parameters/<env>.bicepparam
   az deployment group what-if \
     --resource-group <rg> \
     --template-file infra/azure/modules/<name>.bicep \
     --parameters infra/azure/parameters/<env>.bicepparam
   ```
6. Commit + PR. CI runs `azure-pipelines/templates/bicep-lint-validate.yml` on every touched Bicep file.

---

## 5. Promotion (Azure Pipelines only)

All deploys go through Azure Pipelines. Never via:
- GitHub Actions (forbidden per CLAUDE.md 2026-04-14)
- Portal (not canonical)
- Local `az deployment ... create` from developer workstation (emergency only; must record drift)

The canonical deploy template is `azure-pipelines/templates/bicep-lint-validate.yml` followed by a deploy stage in the parent pipeline:

```yaml
- template: templates/bicep-lint-validate.yml
  parameters:
    serviceConnection: ipai-azure-sub
    resourceGroup: rg-ipai-dev-data-sea
    templateFile: infra/azure/modules/data-lake-canonical.bicep
    parameterFile: infra/azure/parameters/dev.bicepparam

- task: AzureCLI@2
  displayName: Deploy
  inputs:
    azureSubscription: ipai-azure-sub
    scriptType: bash
    scriptLocation: inlineScript
    inlineScript: |
      az deployment group create \
        --resource-group rg-ipai-dev-data-sea \
        --template-file infra/azure/modules/data-lake-canonical.bicep \
        --parameters infra/azure/parameters/dev.bicepparam
```

---

## 6. Deployment stacks + template specs (optional patterns)

Per https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/quickstart-create-deployment-stacks-template-specs — use deployment stacks where:
- A set of resources must be created/destroyed together
- Deny assignments are needed (prevent accidental modification)
- Unmanage actions need explicit semantics (`detachAll` vs `deleteAll`)

Our default for new infra is a **resource-group deployment** (`az deployment group create`). Promote to a **deployment stack** (`az stack group create`) when the lifecycle grouping benefit outweighs the review overhead.

Template specs are useful when a team wants to publish a reusable deployment artifact to a shared scope. We defer adopting template specs until a second consumer team exists.

---

## 7. Naming + tagging cross-references

- Naming convention: `docs/architecture/azure-naming-convention.md` (CAF-aligned)
- Tagging doctrine: `ssot/governance/tagging-doctrine.yaml` (snake_case, live schema)
- Required tags enforced via `infra/azure/policy/required-tags.bicep` (to author)

Every Bicep module must emit `tags` parameters and pass them to each Microsoft.* resource.

---

## 8. Module philosophy

Per https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/modules:
- **Public registry** (`br:mcr.microsoft.com/bicep/...`) — prefer for commodity building blocks (e.g., AVM modules)
- **Local modules** (`infra/azure/modules/*.bicep`) — for IPAI-specific compositions
- **Private registry** — not yet in scope; revisit when >3 teams consume our modules

Do not fork upstream Bicep modules. If an Azure Verified Module (AVM) exists, prefer it and wrap it thinly.

---

## 9. Common commands

```bash
# Lint
az bicep build --file infra/azure/modules/data-lake-canonical.bicep

# Upgrade CLI's Bicep
az bicep upgrade

# Validate against a resource group
az deployment group validate \
  --resource-group rg-ipai-dev-data-sea \
  --template-file infra/azure/modules/data-lake-canonical.bicep \
  --parameters ucAccessConnectorPrincipalId=79fbecac-8341-44d3-8711-12e8a51ddc18

# Preview impact
az deployment group what-if \
  --resource-group rg-ipai-dev-data-sea \
  --template-file infra/azure/modules/data-lake-canonical.bicep \
  --parameters ucAccessConnectorPrincipalId=79fbecac-8341-44d3-8711-12e8a51ddc18

# Deploy
az deployment group create \
  --resource-group rg-ipai-dev-data-sea \
  --template-file infra/azure/modules/data-lake-canonical.bicep \
  --parameters ucAccessConnectorPrincipalId=79fbecac-8341-44d3-8711-12e8a51ddc18
```

---

## 10. Do-not-do list

- ❌ Create resources via portal without then codifying them in Bicep.
- ❌ Commit `.bicepparam` files containing secrets (use Key Vault references or pipeline variables).
- ❌ Use GitHub Actions for Azure deployments.
- ❌ Hand-maintain JSON ARM templates — always author `.bicep` and let the compiler emit JSON.
- ❌ Fork Azure Verified Modules — wrap them instead.
- ❌ Skip `what-if` before a production deploy.

---

*Runbook locked 2026-04-15. Next refresh when Bicep extension ships a breaking change OR we adopt a private module registry.*
