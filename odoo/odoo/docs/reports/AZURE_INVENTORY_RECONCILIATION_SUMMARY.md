# Azure Inventory Reconciliation Summary

> **Date**: 2026-03-11
> **Branch**: `feat/azure-front-door-migration`
> **Source**: Azure portal export (57 resources) + CSV confirmation
> **Scope**: Inventory and doctrine reconciliation only. No Bicep/Terraform renames.

---

## What Changed

### Files Updated

| File | Change |
|---|---|
| `infra/ssot/azure/resources.yaml` | Rewritten from ~17 to 57 confirmed resources. Schema v2.0 with `lifecycle`, `owner_domain`, `managed_by` fields. |
| `infra/ssot/azure/PLATFORM_TARGET_STATE.md` | v1.4.1 → v1.5.0. §2 split into current-state summary (referencing resources.yaml) + target-state aspirational. §10/§13/§14 updated for actual resource names. |

### Files Created

| File | Purpose |
|---|---|
| `infra/ssot/azure/RESOURCE_RECONCILIATION_REPORT.md` | Full gap analysis: newly discovered resources, aspirational resources, naming mismatches, RG mismatches, managed resources, high-risk ambiguities. |
| `infra/ssot/azure/exceptions/dual-odoo-deployment.yaml` | Formal exception record for dual Odoo deployments across rg-ipai-agents-dev and rg-ipai-dev. |
| `docs/reports/AZURE_INVENTORY_RECONCILIATION_SUMMARY.md` | This file. |

---

## Counts

| Metric | Count |
|---|---|
| Portal confirmed resources | 57 |
| Previously documented (resources.yaml v1.0) | ~17 |
| Newly documented | 40 |
| Resource groups (owned) | 8 |
| Resource groups (managed/auto-created) | 2 |
| Managed/auto-created resources | 8 |
| Target-state aspirational (not yet deployed) | ~31 |
| Naming convention deviations (non-managed) | 4 |

---

## Unresolved Exceptions

| ID | Title | Risk | Status |
|---|---|---|---|
| EXC-001 | Dual Odoo Container App Deployments | HIGH | Unresolved |

**EXC-001 details**:
- Two Odoo deployment surfaces: `rg-ipai-agents-dev` (Deployment A) and `rg-ipai-dev` (Deployment B)
- Two PG Flexible Servers: `pg-ipai-dev` (shared) and `ipai-odoo-dev-pg` (dedicated)
- Two Container Registries: `cripaidev` (shared) and `ipaiodoodevacr` (dedicated)
- Canonical deployment: UNKNOWN
- Resolution required before: hostname cutover / topology lock
- Full details: `infra/ssot/azure/exceptions/dual-odoo-deployment.yaml`

---

## Decision Log

| ID | Decision | Status |
|---|---|---|
| D-001 | Dual Odoo deployment | Unresolved exception — document both, do not guess canonical |
| D-002 | Naming convention mismatch | Accepted temporary divergence — document actual names as-is |
| D-003 | Scope of reconciliation | Fixed — inventory/doctrine only, no Bicep/Terraform renames |

---

## Deferred Work

| Item | Reason |
|---|---|
| Bicep/Terraform module naming alignment | Out of scope for this pass |
| Resource renames to match `{type}-ipai-{env}` convention | Deferred until topology is locked |
| EXC-001 resolution (canonical Odoo deployment) | Requires architecture decision |
| Hub-spoke networking provisioning | Planned, pending requirements |
| Monitoring stack (Grafana, Prometheus) provisioning | Planned, pending requirements |
| Backup vault provisioning | Planned, pending requirements |

---

## Verification

- [x] Every portal resource (57) appears in `resources.yaml` with `source: confirmed`
- [x] No planned/aspirational resource is marked as `source: confirmed`
- [x] `PLATFORM_TARGET_STATE.md` clearly separates target state from current deviations
- [x] Dual Odoo deployment is recorded as a formal exception
- [x] Reconciliation report covers all gap categories
- [x] Summary report produced with counts and exception list
