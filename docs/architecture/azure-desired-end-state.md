# Azure Desired End State — Pulser/Odoo

> **Authoritative narrative document** for the Azure estate target. Implementation truth lives in `ssot/azure/{bom,naming-convention,tag-policy}.yaml`.
>
> **Last updated:** 2026-04-14
> **Scope:** Pulser-for-Odoo on Azure, with `dev`, `stg`, `prod` environments. Benchmark scope locked to **D365 Finance + Finance agents + D365 Project Operations** (Core + Integrated with ERP). No Supply Chain / Manufacturing / Commerce / hard-core HR.

## 1. Canonical statement

> A normalized Azure estate with one shared platform group and per-environment resource groups split by **transaction**, **data**, **observability**, and **security** planes; consistent resource prefixes; compact service-constrained names where required; mandatory **policy-enforced tags**; and provider-generated Azure resources explicitly treated as exceptions rather than naming violations.

## 2. Plane assignment rules

| Plane | What lives here | Examples |
|---|---|---|
| **Transaction** | Odoo runtime, OLTP database, integration bus, workload identities, init jobs | `cae-`, `ca-`, `caj-`, `pgfs-`, `sb-`, `id-` (workload-scoped) |
| **Data intelligence** | Databricks, lakehouse storage, access connectors, network for data | `dbw-`, `st-`, `acn-`, `vnet-`, `nsg-` (data-side) |
| **Observability** | App Insights, Log Analytics, action groups | `appi-`, `law-`, `ag-` |
| **Security** | Key Vault, security identities, RBAC artifacts | `kv-`, `id-` (security-scoped) |
| **Shared** | ACR, cross-environment platform assets | `acr` (compact name) |

Planes **mirror** the four-plane PRD architecture (`spec/pulser-odoo/prd.md` §0.1):
- Transaction plane = Odoo+OCA (Plane A)
- Data plane = Databricks+Fabric (data intelligence)
- Observability + Security = governance / WAF pillars
- (Agent plane lives partly in Foundry resource — separate sub `eba824fb` lifecycle)
- (Delivery plane = GitHub + Azure Pipelines — not an Azure-resource plane)

## 3. Naming grammar (locked)

**Global pattern:** `<type>-<org>-<env>-<workload>-<region>`

**RG pattern:** `rg-<org>-<env>-<plane>-<region>`

Vocabularies + type prefixes locked in `ssot/azure/naming-convention.yaml`. Vocabulary additions require PR review.

**Service-constrained exceptions** (Azure forbids hyphens or imposes length): use compact lowercase `<type><org>[<purpose>]<env><region>` (e.g., `acripaisharedsea`, `stipaidevsea`).

## 4. Tagging contract

**14 mandatory tags** enforced via Azure Policy: `org`, `platform`, `env`, `plane`, `workload`, `service`, `owner`, `managed_by`, `criticality`, `cost_center`, `data_classification`, `dr_tier`, `backup_policy`, `ops_state`, `billing_scope`.

Recommended optional: `repo`, `spec_slug`, `iteration`, `parent_service`, `cm-resource-parent`.

**Hard rules:**
- Tags do NOT inherit from RG/subscription — apply per-resource.
- Tag values are **case-sensitive**; tag names are not.
- 50 tag-pair limit per resource/RG/sub.
- **NEVER** put secrets or tokens in tags.
- Use `cm-resource-parent` (Microsoft canonical) for cost rollup.

Full schema in `ssot/azure/tag-policy.yaml`.

## 5. Target resource-group taxonomy

```
rg-ipai-shared-sea
  └─ acripaisharedsea (ACR)

rg-ipai-{env}-transaction-sea     [env: dev|stg|prod]
  ├─ cae-ipai-{env}-odoo-sea
  ├─ ca-ipai-{env}-odoo-web-sea
  ├─ caj-ipai-{env}-odoo-initdb-sea
  ├─ pgfs-ipai-{env}-odoo-sea
  ├─ sb-ipai-{env}-odoo-sea
  └─ id-ipai-{env}-odoo-sea

rg-ipai-{env}-data-sea
  ├─ dbw-ipai-{env}-data-sea
  ├─ stipai{env}sea
  ├─ stipailake{env}sea
  ├─ acn-ipai-{env}-dbw-sea
  ├─ vnet-ipai-{env}-dbw-sea
  └─ nsg-ipai-{env}-dbw-sea

rg-ipai-{env}-observability-sea
  ├─ appi-ipai-{env}-odoo-sea
  ├─ law-ipai-{env}-odoo-sea
  └─ ag-ipai-{env}-observability-sea

rg-ipai-{env}-security-sea
  └─ kv-ipai-{env}-security-sea
```

For `stg` data + security: optional until needed.
For `prod`: full taxonomy required.

## 6. Migration phasing

Five phases per `ssot/azure/bom.yaml §sequencing`:
1. Freeze SSOT (this PR), apply tags audit-only
2. Tag all current resources to baseline
3. Normalize observability + Key Vault (low blast radius)
4. Move PG + identities (medium risk; coordinate with app)
5. Rename ACA env + split Prismalab (highest risk; full re-registration); stand up stg/prod via Bicep; switch policy from Audit → Deny

## 7. Provider-managed exceptions

Do NOT rename:
- `NetworkWatcher_southeastasia` (Azure default in `NetworkWatcherRG`)
- `dbmanagedidentity` (Databricks managed)
- `dbstorageqba5raeuajc6u` (Databricks managed)
- `Application Insights Smart Detection` (auto-created — create user-managed AG alongside)

## 8. Decisions locked

| Decision | Status | Anchor |
|---|---|---|
| Single canonical region: `sea` (Southeast Asia) | LOCKED | `naming-convention.yaml` |
| Three envs only: `dev`, `stg`, `prod` (+ `shared`) | LOCKED | `naming-convention.yaml` + CLAUDE.md |
| Plane-based RG split (transaction/data/observability/security/shared) | LOCKED | `bom.yaml` |
| 14 mandatory tags, policy-enforced | LOCKED | `tag-policy.yaml` |
| Vocabulary additions require PR | LOCKED | `naming-convention.yaml §locks` |
| `cm-resource-parent` adopted as Cost Management canonical | LOCKED | `tag-policy.yaml` |
| Provider-managed resources are explicit exceptions | LOCKED | `bom.yaml §exceptions` + `naming-convention.yaml §exceptions` |

## 9. Anchors

- **SSOT BOM:** [`ssot/azure/bom.yaml`](../../ssot/azure/bom.yaml)
- **SSOT naming:** [`ssot/azure/naming-convention.yaml`](../../ssot/azure/naming-convention.yaml)
- **SSOT tags:** [`ssot/azure/tag-policy.yaml`](../../ssot/azure/tag-policy.yaml)
- **PRD architecture doctrine:** [`spec/pulser-odoo/prd.md`](../../spec/pulser-odoo/prd.md) §0
- **Tenancy model:** [`docs/tenants/TENANCY_MODEL.md`](../tenants/TENANCY_MODEL.md)
- **Predecessor (deprecated):** `ssot/azure/tagging-standard.yaml` — superseded by `tag-policy.yaml`

## 10. Changelog

- **2026-04-14** Initial canonical desired-end-state. Naming, BOM, and tag policy locked. Phase-1 freeze.
