# Examples — azd-vs-azure-cli-decision

## Example 1: Deploy new web app to ACA

**Task**: "Deploy a new Python web app to Azure Container Apps"
**Proposed tool**: Azure CLI (`az containerapp create`)

**Verdict**: AZD
**Reasoning**: App bootstrap and deployment is azd territory. Use `azd init` with an ACA template, then `azd up`.
**Anti-pattern**: Using `az containerapp create` for initial deployment bypasses the template-driven, reproducible workflow that azd provides.

---

## Example 2: Check Container App logs

**Task**: "View the last 100 log entries for ipai-odoo-dev-web"
**Proposed tool**: azd

**Verdict**: AZURE_CLI
**Reasoning**: Log queries are diagnostics — Azure CLI's `az containerapp logs show` is the correct tool.
**Anti-pattern**: azd does not have granular log query capabilities.

---

## Example 3: Deploy app then verify health

**Task**: "Deploy the updated service and verify health probes pass"
**Proposed tool**: None specified

**Verdict**: BOTH
**Reasoning**: Deployment via `azd deploy`, then health verification via `az containerapp show` to check probe status.
**Boundaries**: azd handles the deployment; Azure CLI handles the post-deployment verification query.

---

## Example 4: Scale Container App replicas

**Task**: "Scale ipai-odoo-dev-web to 3 minimum replicas"
**Proposed tool**: azd

**Verdict**: AZURE_CLI
**Reasoning**: Scaling is an operational maintenance task. Use `az containerapp update --min-replicas 3`.
**Anti-pattern**: azd manages the full provisioning topology, not individual resource scaling adjustments.

---

## Example 5: Set up GitHub Actions pipeline

**Task**: "Configure CI/CD pipeline for the project"
**Proposed tool**: Azure CLI

**Verdict**: AZD
**Reasoning**: CI/CD pipeline setup is `azd pipeline config` — it generates the workflow file with correct federated credentials.
**Anti-pattern**: Manually creating GitHub Actions workflows for azd-managed projects bypasses the integrated pipeline configuration.
