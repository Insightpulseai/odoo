# CLI Surface Routing Examples

## Databricks CLI Tasks

| Task | Surface | Delegate |
|------|---------|----------|
| "List notebooks in /Repos/ipai/" | DATABRICKS_CLI | databricks-workspace-ops |
| "Start cluster for data processing" | DATABRICKS_CLI | databricks-compute-jobs-ops |
| "Deploy ML model to serving endpoint" | DATABRICKS_CLI | databricks-ml-serving-ops |
| "Create service principal for CI pipeline" | DATABRICKS_CLI | databricks-identity-sql-ops |
| "Start SQL warehouse for analytics" | DATABRICKS_CLI | databricks-identity-sql-ops |

## Odoo CLI Tasks

| Task | Surface | Delegate |
|------|---------|----------|
| "Start Odoo dev server with hot reload" | ODOO_CLI | odoo-server-ops |
| "Create test database for ipai_finance_ppm" | ODOO_CLI | odoo-db-ops |
| "Debug partner data via shell" | ODOO_CLI | odoo-shell-ops |
| "Scaffold new module ipai_hr_leave" | ODOO_CLI | odoo-module-scaffold-ops |
| "Run tests for ipai_ai_core" | ODOO_CLI | odoo-test-runner-ops |
| "Neutralize production database copy" | ODOO_CLI | odoo-dataset-neutralize-populate-ops |
| "Count lines of code in IPAI modules" | ODOO_CLI | odoo-code-metrics-ops |

## Azure CLI Tasks

| Task | Surface | Delegate |
|------|---------|----------|
| "Deploy container image to ACA" | AZURE_CLI | azure-cli-safe |
| "Build and push Docker image to ACR" | AZURE_CLI | azure-cli-safe |
| "Check Key Vault secret metadata" | AZURE_CLI | azure-cli-safe |

## Rejected Tasks

| Task | Surface | Reason |
|------|---------|--------|
| "Deploy using odo" | REJECTED | odo is deprecated by Red Hat |
| "Use odo to manage Kubernetes apps" | REJECTED | odo is deprecated — use ACA/AKS tooling |

## Multi-Surface Tasks (Decomposition Required)

| Task | Sub-tasks |
|------|-----------|
| "Deploy ML model from Databricks to Azure endpoint" | 1. DATABRICKS_CLI: export model, 2. AZURE_CLI: deploy container |
| "Test Odoo module that reads Databricks data" | 1. ODOO_CLI: run module tests, 2. DATABRICKS_CLI: verify data source |
