# Azure Resource Normalization Checklist

## Goal
Normalize the current Azure Sponsorship subscription into a small, explicit set of canonical resources for Odoo ERP SaaS and supporting platform planes.

## 1. Subscription baseline
- [ ] Freeze `Microsoft Azure Sponsorship` as canonical
- [ ] Record subscription ID in SSOT
- [ ] Confirm this is the default target for new IaC deployments

## 2. Adopt confirmed canonical resources
- [ ] Adopt `pg-ipai-odoo` in place
- [ ] Adopt `acripaiodoo` in place
- [ ] Adopt current Key Vault rather than creating a duplicate
- [ ] Adopt one runtime Log Analytics workspace
- [ ] Adopt one runtime Application Insights component

## 3. Observability normalization
- [ ] Choose the canonical runtime workspace
- [ ] Choose the canonical runtime App Insights component
- [ ] Mark non-runtime workspaces/components as keep/review/retire
- [ ] Bind diagnostic settings to the canonical workspace

## 4. Identity normalization
- [ ] Preserve role-specific identities
- [ ] Review generic identities for overlap
- [ ] Remove or retire duplicates only after dependency validation

## 5. Networking normalization
- [ ] Preserve current private endpoints that protect KV/Search/Postgres/ACR
- [ ] Decide whether `workers-vnet` remains Databricks-only or can be retired
- [ ] Avoid parallel runtime VNets without a clear ownership reason

## 6. Storage normalization
- [ ] Classify each storage account:
  - runtime
  - logs
  - backups
  - lakehouse
  - managed-service residue
- [ ] Mark each as keep / adopt / retire
- [ ] Avoid creating new storage accounts until classification is complete

## 7. Odoo SaaS target state
- [ ] Keep `pg-ipai-odoo` as the canonical ERP database
- [ ] Keep `acripaiodoo` as the canonical image registry
- [ ] Standardize runtime names:
  - `odoo-web-dev`
  - `odoo-worker-dev`
  - `odoo-cron-dev`
  - `odoo-web-staging`
  - `odoo-worker-staging`
  - `odoo-cron-staging`
  - `odoo-web-production`
  - `odoo-worker-production`
  - `odoo-cron-production`

## 8. Governance
- [ ] Apply tag contract incrementally
- [ ] Keep deletion decisions separate from naming normalization
- [ ] Do not rename data-plane resources unless migration is explicit and reversible

---

## Keep / adopt / review summary

### Adopt in place

| Resource | Type |
|---|---|
| `pg-ipai-odoo` | PostgreSQL Flexible Server |
| `acripaiodoo` | Container Registry |
| `kv-ipai-dev-sea` | Key Vault |
| `dbw-ipai-dev` | Databricks |
| `srch-ipai-dev-sea` | AI Search |
| `pv-ipai-dev-sea` | Purview |
| `vnet-ipai-dev-sea` | Virtual Network |
| `pe-ipai-dev-kv` | Private Endpoint |
| `pe-ipai-dev-search` | Private Endpoint |

### Keep but normalize around

| Resource | Role |
|---|---|
| `log-ipai-dev-runtime-sea` | Preferred LA workspace |
| `appi-ipai-dev-runtime-sea` | Preferred App Insights |
| `ag-ipai-dev-sea` | Action group |
| `id-ipai-dev-runtime` | Runtime identity |
| `id-ipai-dev-data` | Data identity |
| `id-ipai-dev-pipeline` | Pipeline identity |

### Review for overlap / residue

| Resource | Reason |
|---|---|
| `log-ipai-dev-sea` | May overlap with runtime workspace |
| `log-ipai-dev-data-sea` | Data-plane specific — keep if Databricks uses it |
| `log-ipai-dev-agent-sea` | Agent-plane specific — defer until agent plane active |
| `appi-ipai-dev` | May overlap with runtime App Insights |
| `appi-ipai-dev-agent-sea` | Agent-plane specific — defer |
| `id-ipai-dev` | Generic — may overlap with role-specific identities |
| `id-ipai-dev-agent` | Agent-plane — defer |
| `dbmanagedidentity` | Databricks managed — do not touch |
| `workers-vnet` | Databricks managed — verify before any action |
| `workers-sg` | Databricks managed — verify before any action |
| `stdevipai` | Unclear purpose |
| `stipaidevagent` | Agent artifacts — defer |
| `stlkipaidev` | May duplicate `stipaidevlake` |
| `scansoutheastasiadckrnut` | Purview managed scan storage |
| `dbstorageqba5raeuajc6u` | Databricks managed storage |

### Rule

1. Adopt current names under IaC
2. Classify duplicates/residue
3. Retire only after dependency validation
4. Rename only later, if the rename is worth the migration cost
