# Constitution — Odoo Cloud Platform (IPAI)

> Governance principles for IPAI's Odoo.sh-equivalent Azure-native ERP platform.

## Repo placement (locked)

- **Spec + control plane**: `platform/` (this spec + `platform/ssot/*`)
- **Infrastructure**: `infra/` (Azure IaC; ACA + ACR + PostgreSQL + networking + KV + monitoring)
- **Application / runtime payload**: `addons/` (Odoo CE 18 + OCA + `ipai_*`) — this is the "odoo" repo concern inside the monorepo
- **Agent runtime harness**: `agent-platform/`
- **Definitions**: `agents/`

## Invariants

1. **Odoo CE 18 + OCA remains the application baseline** (per CLAUDE.md and `ssot/odoo/odoo-18-vs-19-adoption-decision.yaml`)
2. **No EE source** in the CE repo (per `platform/ssot/odoo/ee-capability-target-map.yaml`)
3. **Azure Pipelines is the sole deploy authority** (per CLAUDE.md)
4. **Azure Boards is the sole portfolio planning SoR**
5. **GitHub is the sole code/PR truth**
6. **Config → OCA → thin `ipai_*` delta** — extension order never inverted
7. **Branch/environment contract is machine-readable** (per `platform/ssot/runtime/branch-environment-contract.yaml`)
8. **Backup/restore and DR are first-class platform features**, not afterthoughts
9. **Every promotion between envs requires an evidence pack**

## Related

- [prd.md](prd.md)
- [plan.md](plan.md)
- [tasks.md](tasks.md)
- Branch/env contract: [../../platform/ssot/runtime/branch-environment-contract.yaml](../../platform/ssot/runtime/branch-environment-contract.yaml)
- Platform BOM: [../../platform/ssot/architecture/odoo-cloud-platform-bom.yaml](../../platform/ssot/architecture/odoo-cloud-platform-bom.yaml)
- Release gates: [../../platform/ssot/release/odoo-cloud-release-gates.yaml](../../platform/ssot/release/odoo-cloud-release-gates.yaml)
- Resource inventory: [../../platform/ssot/azure/resource-inventory.dev.yaml](../../platform/ssot/azure/resource-inventory.dev.yaml)
- EE capability target: [../../platform/ssot/odoo/ee-capability-target-map.yaml](../../platform/ssot/odoo/ee-capability-target-map.yaml)
