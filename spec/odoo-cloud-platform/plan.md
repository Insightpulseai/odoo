# Plan — Odoo Cloud Platform (IPAI)

## Repo split

| Concern | Repo path | Authority |
|---|---|---|
| Spec + control plane | `platform/` (this spec + `platform/ssot/*`) | platform-architecture |
| Azure IaC | `infra/azure/` | infra |
| Application runtime | `addons/` (Odoo CE 18 + OCA + `ipai_*`) | odoo-runtime |
| Agent harness | `agent-platform/` | platform-architecture |
| Agent definitions | `agents/` | platform-architecture |

## What goes where

### `platform/`
- [platform/ssot/runtime/branch-environment-contract.yaml](../../platform/ssot/runtime/branch-environment-contract.yaml)
- [platform/ssot/architecture/odoo-cloud-platform-bom.yaml](../../platform/ssot/architecture/odoo-cloud-platform-bom.yaml)
- [platform/ssot/release/odoo-cloud-release-gates.yaml](../../platform/ssot/release/odoo-cloud-release-gates.yaml)
- `platform/ssot/ui/odoo-cloud-platform-ui.yaml` (future — operator UI contract)

### `infra/azure/`
- `infra/azure/aca-odoo-platform/` — ACA env + app definitions
- `infra/azure/postgres/` — pg-ipai-odoo + backup/restore policy
- `infra/azure/network/` — VNet, private endpoints, Front Door wiring
- `infra/azure/monitoring/` — App Insights + Log Analytics + action groups

### `addons/` (odoo runtime)
- `docker/` — Odoo Docker build inputs
- `config/` — Odoo config per environment (via env vars, not hardcoded)
- `scripts/` — operator scripts consumed by platform pipelines
- `ssot/odoo/` — runtime state + ORM registry + domains + interop template
- `addons/ipai/**` — IPAI custom modules
- `tests/` — Odoo module tests

## Phases

| Phase | Scope | Exit criteria |
|---|---|---|
| 1 | Branch/env contract SSOT + platform BOM stub | SSOTs committed + linted |
| 2 | Azure Pipelines lane: `azure-pipelines-odoo-promote.yml` | Smoke deploy to dev passes |
| 3 | Backup/restore automation for pg-ipai-odoo | Tested restore drill |
| 4 | Release gate integration (ties to go-live-readiness) | End-to-end promotion with evidence |
| 5 | Operator UI (optional; reads from SSOTs; deployed as part of `platform/`) | Read-only dashboard works |
| 6 | Pulser-assisted operator actions (read/suggest only) | Via `pulser_erp` pack + guarded_write tools |

## Anti-patterns (do NOT)
- Put Odoo Cloud Platform logic primarily in `addons/` (mixes app + control plane)
- Put it in `web/` (that's user-facing surfaces)
- Put it in `agent-platform/` (that's runtime harness)
- Bidirectional sync with Odoo.sh (we're not using Odoo.sh; this is our equivalent on Azure)

## Related
- [constitution.md](constitution.md)
- [prd.md](prd.md)
- [tasks.md](tasks.md)
