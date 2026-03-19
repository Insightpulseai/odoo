# Examples — caf-adoption-planning

## Example 1: Post-migration optimization plan

**Input**: Azure migration from DigitalOcean complete, now planning optimization and governance adoption.

**Output**:
- Digital estate: 11 Container Apps, 2 PostgreSQL servers, 3 container registries, 1 Front Door, 3 Key Vaults
- Wave plan:
  - Wave 1 (Week 1-2): Governance baseline — naming policy, cost budgets, tagging
  - Wave 2 (Week 3-4): Security hardening — managed identity audit, Key Vault binding verification
  - Wave 3 (Week 5-8): Operations baseline — monitoring, alerting, backup validation
  - Wave 4 (Week 9-12): Modernization — Keycloak to Entra ID migration
- Skills assessment: AZ-104 (current), AZ-305 (gap), AZ-500 (gap)
- Organizational model: Solo operator + AI agents, CCoE pattern simplified to decision log
- Success metrics: 100% resources tagged, cost budget alerts active, 99.9% uptime measured

## Example 2: Greenfield workload adoption plan

**Input**: Planning to add Databricks analytics workload to existing Azure environment.

**Output**:
- Digital estate addition: Databricks workspace, Unity Catalog, storage accounts, VNET integration
- Wave plan:
  - Wave 1 (Week 1): Foundation — Databricks workspace, managed identity, VNET peering
  - Wave 2 (Week 2-3): Data pipeline — Bronze layer ingestion from Odoo PostgreSQL
  - Wave 3 (Week 4-6): Analytics — Silver/Gold transformations, dashboard apps
  - Wave 4 (Week 7-8): Integration — Lakeflow Connect, Odoo bridge module
- Skills assessment: DP-203 (gap), Databricks certification (gap)
- Organizational model: Solo operator, Databricks managed by same team
- Success metrics: Pipeline running daily, data freshness < 1 hour, 3 dashboard apps deployed
