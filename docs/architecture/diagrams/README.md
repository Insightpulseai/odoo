# Architecture Diagrams

## Source / Render Contract

| File | Role | Editable? |
|------|------|-----------|
| `*.drawio` | Canonical editable source | Yes — edit in [app.diagrams.net](https://app.diagrams.net) or VS Code draw.io extension |
| `*.png` | Derived render artifact | No — regenerate via `scripts/docs/export_drawio.sh` |

## Rules

1. **Source is truth.** The `.drawio` file is the single source. The `.png` is a derived artifact.
2. **No orphan renders.** Every `.png` must have a corresponding `.drawio` in the same directory.
3. **CI-enforced lockstep.** `diagram-drift-check.yml` fails the PR if `.drawio` changes without a matching `.png` refresh.
4. **Naming.** `<scope>-<level>.drawio` where level is `overview`, `high-level`, or `low-level`.
5. **Registry.** Every diagram must be registered in `ssot/architecture/diagram_catalog.yaml`.

## Diagram Levels

Per `docs/architecture/diagram-conventions.md`:

| Level | Shows | Does Not Show |
|-------|-------|---------------|
| **Overview** | Six planes, truth-plane legend, major boundaries | Every resource, networking detail, CI/CD |
| **High-level** | Azure services, resource groups, shared/workload split | Implementation wiring, identity detail |
| **Low-level** | Deployment pipelines, container configs, identity flows | (Everything) |

## Current Diagrams

| Diagram | Level | Source | Render |
|---------|-------|--------|--------|
| Azure Platform Overview | overview | `azure-platform-overview.drawio` | `azure-platform-overview.png` |

## Export

```bash
# Render all diagrams
./scripts/docs/export_drawio.sh

# Render a single diagram
./scripts/docs/export_drawio.sh docs/architecture/diagrams/azure-platform-overview.drawio
```

Requires: `drawio` CLI (`brew install --cask drawio` or `npm install -g @nicedoc/drawio-cli`).
