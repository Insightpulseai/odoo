# Azure DevOps / GitHub Wiring Runbook

> Operational steps to connect Azure DevOps Boards, harden PAT policy, and create service connections.
> Azure DevOps org: `https://dev.azure.com/insightpulseai` | Project: `InsightPulseAI`
> GitHub org: `Insightpulseai` | Primary repo: `Insightpulseai/odoo`

---

## 1. Install Azure Boards App for GitHub

### 1a. Install from GitHub Marketplace

1. Open <https://github.com/marketplace/azure-boards>
2. Select **Set up a plan** (Free).
3. Grant access to the `Insightpulseai` GitHub org.
4. Select repositories: `Insightpulseai/odoo` (add others as needed).
5. Complete OAuth flow -- authenticate to `dev.azure.com/insightpulseai`.

### 1b. Connect Azure DevOps project

1. In Azure DevOps: **Project Settings > Boards > GitHub connections**.
2. Click **Connect your GitHub account** (or **Add GitHub connection**).
3. Authorize the `Insightpulseai` org.
4. Select `Insightpulseai/odoo`.

### 1c. Verify AB# linking

Create a test work item in Azure Boards, note its ID (e.g., `42`).

```bash
# Create a branch and PR referencing the work item
git checkout -b test/ab-link-verify
git commit --allow-empty -m "test: verify AB#42 linking"
git push -u origin test/ab-link-verify
gh pr create --title "test: verify AB#42 linking" \
  --body "Linked to AB#42 for wiring verification." \
  --base main
```

Confirm in Azure Boards that work item 42 shows the GitHub PR link under **Development**.
Clean up after verification:

```bash
gh pr close --delete-branch
```

---

## 2. PAT Policy Hardening

Navigate to: **Organization Settings > Policies** at `https://dev.azure.com/insightpulseai/_settings/policy`.

| Setting | Value | Purpose |
|---------|-------|---------|
| Restrict creation of global (all-org) PATs | **ON** | Force project-scoped tokens |
| Restrict creation of full-scoped PATs | **ON** | Require explicit scope selection |
| Enforce maximum PAT lifespan | **30 days** | Limit blast radius of leaked tokens |

### Verify

1. Go to **User Settings > Personal Access Tokens > New Token**.
2. Attempt to set **Organization: All accessible organizations** -- must be blocked.
3. Attempt to set **Scopes: Full access** -- must be blocked.
4. Set expiration beyond 30 days -- must be rejected or capped.

---

## 3. Service Connection for Databricks CI

### 3a. Create ARM service connection (Workload Identity Federation)

1. Navigate to: **Project Settings > Service connections > New service connection**.
2. Select **Azure Resource Manager**.
3. Authentication: **Workload Identity federation (automatic)** (preferred).
4. Scope level: **Resource Group**.
   - Subscription: select the subscription containing `rg-ipai-ai-dev`.
   - Resource group: `rg-ipai-ai-dev`.
5. Service connection name: `azdo-sc-databricks-dev`.
6. **Uncheck** "Grant access permission to all pipelines".
7. Save.

### 3b. Authorize pipeline explicitly

```bash
# Via Azure DevOps CLI (install: az extension add --name azure-devops)
az devops configure --defaults organization=https://dev.azure.com/insightpulseai project=InsightPulseAI

# List service connections to get the ID
az devops service-endpoint list --query "[?name=='azdo-sc-databricks-dev'].{id:id,name:name}" -o table

# Authorize a specific pipeline (replace <endpoint-id> and <pipeline-id>)
az devops service-endpoint update --id <endpoint-id> --enable-for-all false
az pipelines run --name <pipeline-name>  # First run triggers manual authorization prompt
```

### 3c. Verify

```bash
az devops service-endpoint show --id <endpoint-id> \
  --query "{name:name,type:type,isReady:isReady}" -o table
```

Expected: `isReady = True`, `type = azurerm`.

---

## 4. Verification Checklist

| # | Step | Expected Result | Status |
|---|------|-----------------|--------|
| 1 | Azure Boards GitHub app installed on `Insightpulseai` org | App visible at GitHub org > Settings > Installed GitHub Apps | [ ] |
| 2 | GitHub connection active in Azure DevOps project | `Insightpulseai/odoo` listed under Boards > GitHub connections | [ ] |
| 3 | `AB#<id>` in PR body creates link in Azure Boards work item | Work item shows PR under Development section | [ ] |
| 4 | Global PAT creation blocked | "All accessible organizations" option disabled/rejected | [ ] |
| 5 | Full-scope PAT creation blocked | "Full access" scope option disabled/rejected | [ ] |
| 6 | PAT lifespan capped at 30 days | Expiration beyond 30 days rejected | [ ] |
| 7 | `azdo-sc-databricks-dev` service connection created | Shows `isReady=True` in service endpoint list | [ ] |
| 8 | Service connection scoped to `rg-ipai-ai-dev` | Resource group matches in connection details | [ ] |
| 9 | Pipeline authorization is explicit (not all pipelines) | `isShared=false` on the service endpoint | [ ] |

---

*SSOT reference: `odoo/ssot/azure/azure_devops.yaml`*
*Last updated: 2026-03-23*
