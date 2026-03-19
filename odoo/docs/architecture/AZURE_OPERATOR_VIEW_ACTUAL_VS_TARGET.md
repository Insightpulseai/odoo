# Azure Operator View — Actual vs Target

## Purpose

Map the current live Azure/operator view to the canonical target grouping defined in:
- `docs/architecture/AZURE_WORKSPACE_TARGET_GROUPING.md`
- `ssot/azure/workspace_target_grouping.yaml`

This document is the reconciliation layer between:
- actual live resources
- current VS Code Azure pane grouping
- target operator grouping
- required cleanup actions

## Canonical target

Top-level groups:
- `insightpulseai-shared`
- `insightpulseai-dev`
- `insightpulseai-staging`
- `insightpulseai-prod`

## Actual current state summary

The current operator view has these issues:

- **10 resource groups** with no environment-first grouping — resources are split by
  functional concern (`rg-ipai-dev`, `rg-ipai-ai-dev`, `rg-ipai-agents-dev`,
  `rg-ipai-data-dev`, `rg-ipai-shared-dev`, etc.) rather than by environment
- **Mixed shared + workload resources** in `rg-ipai-shared-dev` (Key Vault, monitoring,
  ACR live alongside workload-specific resources)
- **Legacy container apps** (`odoo-web` in `rg-ipai-agents-dev`) still visible alongside
  canonical apps
- **Ambiguous runtime naming**: some resources use role-explicit names (`ipai-odoo-dev-web`)
  while others don't (`odoo-web`)
- **No staging or prod workload RGs** — only `rg-ipai-shared-staging` and
  `rg-ipai-shared-prod` exist (secrets/shared only)
- **Foundry-managed resources** use auto-generated names (`aifoundrkeyvault67125c7c`,
  `aifoundrstorage6ff030454`) that are opaque in the operator view
- **Databricks-managed RG** (`rg-dbw-managed-ipai-dev`) appears at the same level as
  workload RGs

## Reconciliation table

### Shared / Platform resources

| Actual resource | Current RG | Target group | Target category | Lifecycle | Action | Notes |
|---|---|---|---|---|---|---|
| `ipai-fd-dev` (Front Door) | `rg-ipai-shared-dev` | `insightpulseai-shared` | edge | canonical | regroup | move to shared view |
| `ipaiDevWafPolicy` (WAF) | `rg-ipai-shared-dev` | `insightpulseai-shared` | edge | canonical | regroup | move to shared view |
| Cloudflare DNS | external | `insightpulseai-shared` | edge / dns-integration | canonical | keep | external, operator-view only |
| Keycloak → Entra migration | n/a | `insightpulseai-shared` | identity / entra | transitional | plan | Keycloak is transitional; target is Entra |
| `mi-ipai-*` (managed identities) | per-env | `insightpulseai-shared` | identity | canonical | regroup | cross-env identity plane |
| `kv-ipai-dev` | `rg-ipai-shared-dev` | `insightpulseai-shared` | secrets | canonical | regroup | |
| `kv-ipai-staging` | `rg-ipai-shared-staging` | `insightpulseai-shared` | secrets | canonical | regroup | |
| `kv-ipai-prod` | `rg-ipai-shared-prod` | `insightpulseai-shared` | secrets | canonical | regroup | |
| `appi-ipai-dev` (App Insights) | `rg-ipai-shared-dev` | `insightpulseai-shared` | observability | canonical | regroup | |
| `law-ipai-dev` (Log Analytics) | `rg-ipai-shared-dev` | `insightpulseai-shared` | observability | canonical | regroup | |
| `vnet-ipai-databricks` | `rg-ipai-ai-dev` | `insightpulseai-shared` | network | canonical | regroup | cross-env networking |
| `nsg-dbw-ipai-dev`, `nsg-cae-ipai-dev`, `nsg-pg-ipai-dev` | various | `insightpulseai-shared` | network | canonical | regroup | |
| `privatelink.postgres.database.azure.com` | n/a | `insightpulseai-shared` | network / private-dns | canonical | regroup | |
| `cripaidev` (shared ACR) | `rg-ipai-shared-dev` | `insightpulseai-shared` | (registry) | canonical | regroup | shared container images |

### Dev workload resources

| Actual resource | Current RG | Target group | Target service name | Lifecycle | Action | Notes |
|---|---|---|---|---|---|---|
| `ipai-odoo-dev-web` | `rg-ipai-dev` | `insightpulseai-dev` | `odoo-web` | canonical | keep | already role-explicit |
| `ipai-odoo-dev-worker` | `rg-ipai-dev` | `insightpulseai-dev` | `odoo-worker` | canonical | keep | already role-explicit |
| `ipai-odoo-dev-cron` | `rg-ipai-dev` | `insightpulseai-dev` | `odoo-cron` | canonical | keep | already role-explicit |
| `ipai-odoo-dev-pg` | `rg-ipai-dev` | `insightpulseai-dev` | (database) | canonical | keep | Odoo PostgreSQL |
| `ipai-odoo-dev-kv` | `rg-ipai-dev` | `insightpulseai-dev` | (secrets) | canonical | keep | Odoo-specific secrets |
| `ipai-auth-dev` (Keycloak) | `rg-ipai-dev` | `insightpulseai-dev` | `auth` | transitional | keep | transitional → Entra |
| `ipai-plane-dev` | `rg-ipai-dev` | `insightpulseai-dev` | `plane` | canonical | keep | |
| `ipai-mcp-dev` | `rg-ipai-dev` | `insightpulseai-dev` | `mcp-coordinator` | canonical | keep | |
| `ipai-ocr-dev` | `rg-ipai-dev` | `insightpulseai-dev` | `ocr` | canonical | keep | |
| `ipai-superset-dev` | `rg-ipai-dev` | `insightpulseai-dev` | `superset` | canonical | keep | |
| `ipai-crm-dev` | `rg-ipai-dev` | `insightpulseai-dev` | `crm` | canonical | keep | |
| `ipai-shelf-dev` | `rg-ipai-dev` | `insightpulseai-dev` | `shelf` | canonical | keep | |
| `ipai-website-dev` | `rg-ipai-dev` | `insightpulseai-dev` | `website` | canonical | keep | |
| `vm-ipai-supabase-dev` | `rg-ipai-agents-dev` | `insightpulseai-dev` | `supabase` | canonical | regroup | exception: VM, not ACA |
| `ipaiodoodevacr` | `rg-ipai-dev` | `insightpulseai-dev` | (registry) | canonical | keep | Odoo images |
| `ipaiwebacr` | `rg-ipai-dev` | `insightpulseai-dev` | (registry) | canonical | keep | Web images |

### Intelligence plane (dev)

| Actual resource | Current RG | Target group | Target surface | Lifecycle | Action | Notes |
|---|---|---|---|---|---|---|
| `dbw-ipai-dev` (Databricks) | `rg-ipai-ai-dev` | `insightpulseai-dev` | `databricks-access` | canonical | regroup | access/runtime surface only |
| `stipaidevlake` (ADLS Gen2) | `rg-ipai-ai-dev` | `insightpulseai-dev` | (storage) | canonical | regroup | lakehouse storage |
| `pg-ipai-dev` (platform PG) | `rg-ipai-data-dev` | `insightpulseai-dev` | (database) | canonical | regroup | platform data |
| `srch-ipai-dev` (AI Search) | `rg-ipai-ai-dev` | `insightpulseai-dev` | (search) | canonical | regroup | |
| `dbstoragew6tn3uhg4bluy` | `rg-dbw-managed-ipai-dev` | n/a | n/a | canonical | hide | Databricks-managed; not operator-visible |
| `rg-dbw-managed-ipai-dev` | n/a | n/a | n/a | canonical | hide | Databricks-managed RG; exclude from view |

### Agent plane (dev)

| Actual resource | Current RG | Target group | Target surface | Lifecycle | Action | Notes |
|---|---|---|---|---|---|---|
| `aifoundry-ipai-dev` (Foundry hub) | `rg-ipai-ai-dev` | `insightpulseai-dev` | `foundry-runtime` | canonical | regroup | access/runtime surface only |
| `proj-ipai-claude` | `rg-ipai-ai-dev` | `insightpulseai-dev` | (foundry project) | canonical | regroup | |
| `data-intel-ph` | `rg-data-intel-ph` | `insightpulseai-dev` | (foundry project) | canonical | regroup | |
| `oai-ipai-dev` (Azure OpenAI) | `rg-ipai-ai-dev` | `insightpulseai-dev` | (model deployment) | canonical | regroup | |
| `docai-ipai-dev` (Doc Intelligence) | `rg-ipai-ai-dev` | `insightpulseai-dev` | (document service) | canonical | regroup | |
| `vision-ipai-dev` | `rg-ipai-ai-dev` | `insightpulseai-dev` | (vision service) | canonical | regroup | |
| `lang-ipai-dev` | `rg-ipai-ai-dev` | `insightpulseai-dev` | (language service) | canonical | regroup | |
| `aifoundrkeyvault67125c7c` | `rg-ipai-ai-dev` | n/a | n/a | canonical | hide | Foundry-managed; not operator-visible |
| `aifoundrstorage6ff030454` | `rg-ipai-ai-dev` | n/a | n/a | canonical | hide | Foundry-managed; not operator-visible |

### Legacy / retire candidates

| Actual resource | Current RG | Target group | Lifecycle | Action | Notes |
|---|---|---|---|---|---|
| `odoo-web` | `rg-ipai-agents-dev` | none | retire | delete | legacy deployment; superseded by `ipai-odoo-dev-web` |
| `odoo-init` | `rg-ipai-agents-dev` | none | retire | delete | legacy init container; no longer needed |
| `cae-ipai-dev` (legacy CAE) | `rg-ipai-agents-dev` | none | retire | delete (after VM/legacy cleanup) | legacy Container Apps Environment |
| `rg-ipai-agents-dev` (entire RG) | n/a | none | retire | delete (after Supabase VM relocated or decommissioned) | only contains legacy apps + Supabase VM exception |

### DevOps infrastructure

| Actual resource | Current RG | Target group | Lifecycle | Action | Notes |
|---|---|---|---|---|---|
| `ipai-devcenter` | `rg-ipai-devops` | (delivery) | experimental | keep | Phase 2 Dev Center; not operator runtime |
| `ipai-build-pool` | `rg-ipai-devops` | (delivery) | legacy | retire | offline self-hosted pool; hosted agents are default |
| Azure Pipelines (2 pipelines) | AzDO | (delivery) | canonical | keep | delivery governance, not runtime tree |
| GitHub Actions | GitHub | (delivery) | canonical | keep | CI, not runtime tree |

## Action classes

### Keep
Resources/services already aligned with target naming and placement:
`ipai-odoo-dev-web`, `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron`, `ipai-plane-dev`,
`ipai-mcp-dev`, `ipai-ocr-dev`, `ipai-superset-dev`, `ipai-crm-dev`, `ipai-shelf-dev`,
`ipai-website-dev`, `ipai-odoo-dev-pg`

### Rename
No active resources require renaming — current Azure resource names are role-explicit.
The operator view aliases (`odoo-web`, `odoo-worker`, etc.) are label-level, not resource-level.

### Move / regroup
Resources that belong under a different top-level group in the operator view:
- All `rg-ipai-shared-*` resources → `insightpulseai-shared`
- All `rg-ipai-ai-dev` resources → `insightpulseai-dev` (as access surfaces)
- All `rg-ipai-data-dev` resources → `insightpulseai-dev`
- `vm-ipai-supabase-dev` → `insightpulseai-dev`

### Retire
- `odoo-web` (legacy Container App in `rg-ipai-agents-dev`)
- `odoo-init` (legacy init container)
- `ipai-build-pool` (offline self-hosted agent pool)
- `cae-ipai-dev` (legacy Container Apps Environment)
- `rg-ipai-agents-dev` (after Supabase VM decommissioned)

### Hide (managed / internal)
Resources managed by platform services that should not appear in the operator view:
- `rg-dbw-managed-ipai-dev` (Databricks-managed)
- `dbstoragew6tn3uhg4bluy` (Databricks-managed storage)
- `aifoundrkeyvault67125c7c` (Foundry-managed Key Vault)
- `aifoundrstorage6ff030454` (Foundry-managed storage)

### Mark experimental
- `ipai-devcenter` (Phase 2; not operational yet)

## Environment completion gaps

### dev
- All target services present in live Azure
- `mcp-plane` not yet deployed as separate resource (currently part of `ipai-mcp-dev`)
- Missing explicit `foundry-runtime` label in operator view (resource exists as `aifoundry-ipai-dev`)
- Missing explicit `databricks-access` label (resource exists as `dbw-ipai-dev`)

### staging
- **No workload RG exists** — only `rg-ipai-shared-staging` (Key Vault only)
- None of the target services deployed: no Odoo, no auth, no Supabase, no Superset
- Full provisioning required for staging environment

### prod
- **No workload RG exists** — only `rg-ipai-shared-prod` (Key Vault only)
- None of the target services deployed
- Full provisioning required for production environment

### shared
- Edge (Front Door, WAF): exists in `rg-ipai-shared-dev` ✓
- Secrets (Key Vault): exists per-env ✓
- Observability (App Insights, Log Analytics): exists in `rg-ipai-shared-dev` ✓
- Network (VNet, NSGs, Private DNS): exists in `rg-ipai-ai-dev` ✓
- Identity (Entra): not yet active — Keycloak is transitional
- Managed identities: exist per-env ✓
- Missing: workload-identity federation, Entra app registrations

## Operator view rules

- no duplicate top-level platform trees
- no mixed shared + workload buckets
- no ambiguous runtime labels like `odoo`
- only canonical and approved transitional services appear in the main operator view
- legacy/experimental resources must be labeled and excluded from the canonical default view
- Databricks/Foundry-managed resources hidden from operator view
- delivery surfaces (Pipelines, Actions) excluded from runtime tree

## Recommended execution order

1. Classify all currently visible nodes/resources with lifecycle labels
2. Eliminate duplicate top-level groupings (if any exist in VS Code pane)
3. Rename ambiguous runtime services (label-level, not resource-level)
4. Regroup shared substrate services under `insightpulseai-shared` view
5. Complete environment-specific workload groupings
6. Remove or hide legacy/experimental resources from canonical operator view
7. Retire `odoo-web`, `odoo-init`, `cae-ipai-dev` in `rg-ipai-agents-dev`
8. Provision staging workload RG + minimal services
9. Provision production workload RG + minimal services

## Completion criteria

The operator view is considered aligned when:
- only `shared`, `dev`, `staging`, and `prod` top-level groups remain
- all Odoo runtimes are role-explicit (`odoo-web`, `odoo-worker`, `odoo-cron`)
- Databricks and Foundry appear only as access/runtime surfaces
- duplicate platform trees are gone
- shared substrate resources are isolated from workload runtime services
- legacy resources (`odoo-web`, `odoo-init`, `cae-ipai-dev`) are retired
- staging and production environments are provisioned with at minimum: Odoo (web/worker/cron), auth, PostgreSQL
