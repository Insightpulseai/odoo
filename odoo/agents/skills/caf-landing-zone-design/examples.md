# Examples — caf-landing-zone-design

## Example 1: Single-subscription landing zone for small team

**Input**: Solo developer with single Azure subscription, 5 resource groups, ACA-based workloads.

**Output**:
- Management groups: Flat structure justified (single subscription, single operator)
- Subscriptions: 1 subscription with environment separation via resource groups
  - `rg-ipai-dev` — ACA workloads (dev)
  - `rg-ipai-data-dev` — Data services
  - `rg-ipai-ai-dev` — AI services
  - `rg-ipai-shared-dev` — Shared (Key Vault, container registry)
  - `rg-ipai-agents-dev` — Agent services
- Identity: Owner role on subscription, Contributor for CI/CD service principal
- Network: No hub-spoke needed (all services use public endpoints via Front Door)
- Automation: Bicep modules in `infra/azure/modules/`, deployed via GitHub Actions
- Shared services: Single Log Analytics workspace, Application Insights per service
- Gap: No tagging policy, no cost budget alerts — recommend adding both

## Example 2: Multi-environment landing zone expansion

**Input**: Growing to staging and production environments, need environment isolation.

**Output**:
- Management groups: Still flat (single subscription), but environment separation strengthened
- Subscriptions: Consider splitting to dev/staging/prod subscriptions for blast radius
- Resource groups: Mirror `rg-ipai-*-{env}` pattern across environments
- Identity: Separate service principals per environment, no dev credentials in prod
- Network: VNET per environment with peering for shared services
- Automation: Environment-parameterized Bicep, promotion pipeline (dev → staging → prod)
- Shared services: Separate Log Analytics per environment, shared Defender for Cloud
- Gap: Need subscription-level Azure Policy for each environment

## Example 3: Landing zone compliance audit

**Input**: Existing landing zone audit against CAF checklist.

**Output**:
- Management groups: N/A (single subscription) — ACCEPTABLE for current scale
- Identity: Managed identity on ACA apps — PASS; Keycloak as IdP — WARN (transition to Entra)
- Network: Public ingress via Front Door — PASS; No private endpoints for PG — WARN
- Automation: Bicep modules exist but not all resources are IaC-managed — PARTIAL
- Shared services: Application Insights enabled — PASS; No centralized Log Analytics — FAIL
- Tagging: No tagging policy — FAIL
- Cost management: No budgets or alerts — FAIL
- Blockers: [centralized logging, tagging policy, cost budgets]
- Remediation: 3 action items with estimated effort
