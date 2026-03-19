# Cloud Adoption Framework Status

## Current Position

**We are in CAF Ready, moving into Adopt, with Strategy and Plan mostly complete.**

---

## Stage Assessment

| CAF Stage | Status | Approx % |
|-----------|--------|----------|
| **Strategy** | Largely complete | 90-95% |
| **Plan** | Mostly complete | 75-85% |
| **Ready** | **Current primary stage** | 45-55% |
| **Adopt** | Early / beginning | 25-35% |
| **Govern** | Partially active | 35-45% |
| **Secure** | Partially active | 35-45% |
| **Manage** | Started, not mature | 20-30% |

---

## Strategy (90-95%)

Completed:

- Six-plane target architecture
- Authority model (Boards / GitHub / Pipelines / Resource Graph / Foundry / SSOT)
- Canonical repo direction
- Target capability mapping with keep/adapt/defer decisions
- Odoo / Databricks / Foundry role split
- Platform doctrine and boundaries
- Supabase, n8n, Power BI positioning
- Fluent UI design system adoption
- Vertical capability families (marketing, retail, entertainment, financial services)

## Plan (75-85%)

Completed:

- Azure Boards backlog structure (POC, Finance PPM, Expense, Copilot, Integration)
- IAM/RBAC model with 7 roles, 17 Entra groups, separation of duties
- Agent capability audit (50+ items classified)
- Azure service mapping (30+ services, 8 capability lanes)
- Implementation sequencing (Phase 0 through Phase 4)
- Go-live checklist

Remaining:

- OCA 56-module hydration plan
- Databricks activation plan
- Foundry agent runtime plan
- Revenue/GTM packaging plan

## Ready (45-55%)

Completed:

- Native Entra admins created (`admin@`, `emergency-admin@insightpulseai.com`)
- Custom domain `insightpulseai.com` verified and set as default
- Odoo App Registration with 15 roles, secrets in Key Vault
- Bicep modules: VNet, Log Analytics, Azure Files, diagnostics
- ACA environment and Odoo runtime active (web, worker, cron)
- PostgreSQL Flexible Server live (`ipai-odoo-dev-pg`)
- CI/CD pipeline authored (`.azure/pipelines/ci-cd.yml`)
- Public endpoint SSOT documented
- Duplicate container apps retired

In progress:

- Azure Front Door routing (parameter file ready, deployment pending)
- Azure Files storage mount to ACA
- Database-per-tenant validation
- OCA baseline module configuration
- Security Defaults re-enablement
- Azure DevOps Boards import

Not started:

- Production VNet injection for Databricks
- APIM provisioning
- Full environment promotion gates (dev/staging/prod)

## Adopt (25-35%)

Active:

- Odoo CE 19 running on Azure Container Apps
- Azure Boards operationalization underway
- Databricks activation tracked in backlog
- POC workstreams defined (8 issues, 47 tasks)
- Expense, Copilot, and Integration backlogs authored

Pending:

- First end-to-end POC demonstration
- First `AB#`-linked commit/PR
- First pipeline deploy with release evidence
- Databricks workspace activation
- Foundry agent runtime activation

## Govern (35-45%)

Active:

- SSOT governance files in `ssot/` (architecture, security, agents, capabilities, network)
- Access model with RBAC matrix and separation of duties
- Azure service mapping with prohibited misuse rules
- Platform boundaries YAML with truth authorities
- Spec bundle governance (`spec/`)

Pending:

- Azure Policy for unmanaged resource prevention
- Resource Graph drift detection queries
- Automated compliance checks in CI

## Secure (35-45%)

Active:

- Entra ID with native admins and MFA
- Key Vault for all secrets
- App Registration with role-based access
- Emergency access accounts documented
- IAM/RBAC SSOT with 14 separation-of-duties rules

Pending:

- M365 Business Premium / Conditional Access
- Security Defaults re-enablement
- Front Door WAF activation
- VNet injection for Databricks
- Keycloak-to-Entra cutover

## Manage (20-30%)

Active:

- Application Insights and Log Analytics provisioned
- Container App logs accessible
- PostgreSQL metrics available

Pending:

- Centralized observability dashboard
- Alert policies for Odoo, PostgreSQL, Databricks
- Incident response runbook
- DR testing (PostgreSQL PITR, ACA failover)
- Backup/restore validation

---

## Next Gates to Move Forward

To advance from **Ready** into full **Adopt**:

1. Import Azure Boards backlogs and begin tracked execution
2. Complete Azure Front Door deployment and DNS routing
3. Deploy Azure Files and wire ACA storage mount
4. Validate database-per-tenant Odoo routing
5. Run first end-to-end pipeline deploy with release evidence
6. Fix Odoo cron/job drift (broken `analytic_account_id` server action)
7. Activate Databricks workspace and Unity Catalog governance
8. Produce POC evidence pack

---

## One-Liner

> We are currently in CAF Ready, with Strategy and Plan mostly complete, and we are beginning Adopt through live Odoo-on-Azure, governance activation, and POC execution.
