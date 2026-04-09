# Documentation Authority Model

## Purpose

Define which repo (or monorepo directory) owns each documentation family, so that docs live next to their executable truth and `docs/odoo-on-azure/` serves as the cross-repo architecture index and navigation surface.

## Scope

This rule applies to all Odoo-on-Azure documentation families. It governs where the **source of truth** for each doc family lives, and where an **index/mirror** page is published for cross-repo discoverability.

## Authority Rules

| Authority | Owns |
|---|---|
| `docs/` | Cross-repo narrative, benchmark mapping, overview, planning, reference index |
| `platform/` | Control-plane truth: workload center, monitoring, AI platform bridge/control-plane |
| `infra/` | Deployment/IaC truth: automation, networking, environment bootstrap |
| `odoo/` (repo root) | ERP runtime/app truth: Odoo topology, app-level how-tos, thin integration surfaces |
| `agents/` | Agent/runtime/skill truth: agent patterns, AI-led SDLC, orchestration |
| `data-intelligence/` | Analytics/lakehouse truth: medallion, governance, BI, AI-ready data |
| `.github/` | Engineering governance: CI/CD policy, repo policy, spec-driven dev workflow |
| `web/` | Presentation layer: docs site frontend, resource hub navigation |

## Doc Family to Authority Mapping

| Doc Family | Canonical Location | `docs/odoo-on-azure/` Role |
|---|---|---|
| `overview/` | `docs/odoo-on-azure/overview/` | **Source** — cross-repo architecture reference |
| `planning/` | `docs/odoo-on-azure/planning/` | **Source** — operating model, design decisions |
| `reference/` | `docs/odoo-on-azure/reference/` | **Source** — benchmark map, terminology, this file |
| `workload-center/` | `platform/docs/workload-center/` | **Index** — links to platform canonical |
| `monitoring/` | `platform/docs/monitoring/` | **Index** — links to platform canonical |
| `deployment-automation/` | `infra/docs/deployment-automation/` | **Index** — links to infra canonical |
| `runtime/` | `docs/odoo-on-azure/runtime/` | **Source** — Odoo runtime topology (repo-root scope) |
| `quickstarts/` | Split: `infra/`, `odoo/`, `platform/` | **Index** — aggregates from subsystems |
| `how-to/` | Split by subsystem | **Index** — aggregates from subsystems |
| `integrations/` | Split: `platform/`, `odoo/`, `agents/`, `data-intelligence/` | **Index** — aggregates from subsystems |
| `ai-platform/` | `platform/docs/ai-platform/` + `agents/docs/ai-platform/` | **Index** — links to platform and agents canonical |
| `engineering/` | `.github/` + `agents/docs/engineering/` | **Index** — links to governance and agents canonical |
| `data-intelligence/` | `data-intelligence/docs/` | **Index** — links to data-intelligence canonical |

## Rules

1. **`docs/odoo-on-azure/` is not the storage location for all truth.** It is the architecture index, benchmark map, and cross-repo navigation surface.
2. **Subsystem directories own executable-truth-adjacent documentation.** If a doc describes how something works and lives next to the code that implements it, the subsystem directory is the canonical location.
3. **Index pages link, they do not duplicate.** An index page in `docs/odoo-on-azure/` should summarize scope and link to the canonical location. It must not contain a full copy of the content.
4. **Canonical full pages live where the code lives.** Platform control-plane docs in `platform/docs/`, agent runtime docs in `agents/docs/`, IaC docs in `infra/docs/`.
5. **Future multi-repo split is transparent.** When subsystem directories become separate repos, the index pages in `docs/odoo-on-azure/` update their links — no content migration needed because source was already in the right place.

## Related Documents

- `docs/odoo-on-azure/README.md` — top-level navigation
- `docs/odoo-on-azure/reference/benchmark-map.md` — parity matrix
- `docs/architecture/ODOO_ON_AZURE_REFERENCE_ARCHITECTURE.md` — single-page reference architecture

---

*Created: 2026-04-05 | Version: 1.0*
