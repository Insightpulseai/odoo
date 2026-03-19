# CLI Surface Selection Skill (Judge)

## Purpose

Judge skill that decides which CLI surface owns a given task. Returns DATABRICKS_CLI, ODOO_CLI, AZURE_CLI, AZD, or OTHER with reasoning. Rejects cross-platform misuse.

## Owner

platform-cli-judge

## Type

Judge — this skill does NOT execute CLI commands. It routes tasks to the correct specialist skill.

## Decision Matrix

| Task Pattern | Surface | Delegate Skill |
|-------------|---------|----------------|
| Workspace artifacts (notebooks, repos, files) | DATABRICKS_CLI | databricks-workspace-ops |
| Secrets (Databricks scope) | DATABRICKS_CLI | databricks-workspace-ops |
| Clusters, instance pools | DATABRICKS_CLI | databricks-compute-jobs-ops |
| Jobs, pipelines, runs | DATABRICKS_CLI | databricks-compute-jobs-ops |
| ML experiments, models, serving | DATABRICKS_CLI | databricks-ml-serving-ops |
| Databricks identity (users/groups/SPs) | DATABRICKS_CLI | databricks-identity-sql-ops |
| SQL warehouses, queries, dashboards | DATABRICKS_CLI | databricks-identity-sql-ops |
| Odoo server start/stop/config | ODOO_CLI | odoo-server-ops |
| Odoo database create/backup/restore | ODOO_CLI | odoo-db-ops |
| Odoo shell/debugging | ODOO_CLI | odoo-shell-ops |
| Odoo module scaffold | ODOO_CLI | odoo-module-scaffold-ops |
| Odoo test execution | ODOO_CLI | odoo-test-runner-ops |
| Odoo data neutralize/populate | ODOO_CLI | odoo-dataset-neutralize-populate-ops |
| Odoo code metrics (cloc) | ODOO_CLI | odoo-code-metrics-ops |
| Azure resource provisioning | AZURE_CLI | azure-cli-safe |
| Container image build/push | AZURE_CLI | azure-cli-safe |
| Azure Developer CLI (project init, deploy) | AZD | azure-deployment-ops |
| Deprecated tool (odo, etc.) | REJECTED | deprecated-cli-assessment |
| Unknown/ambiguous | OTHER | Requires manual classification |

## Rejection Rules

- Databricks CLI must NOT be used for Odoo operations
- Odoo CLI must NOT be used for Databricks operations
- Azure CLI must NOT be used for Databricks workspace operations
- odo and other deprecated tools are always REJECTED
- If a task spans multiple surfaces, decompose into sub-tasks

## Output Format

```json
{
  "surface": "DATABRICKS_CLI | ODOO_CLI | AZURE_CLI | AZD | OTHER | REJECTED",
  "delegate_skill": "<skill-id>",
  "delegate_persona": "<persona-id>",
  "reasoning": "<why this surface was chosen>",
  "sub_tasks": [
    {"surface": "...", "task": "..."}
  ]
}
```

## Verification

- Routing decision matches the task domain
- No cross-platform misuse in the delegation
- Deprecated tools are always rejected
