# Design → Code Contract (Figma SSOT)

This directory holds machine-readable exports from Figma used to:
- Generate scaffolds (routes, components, RLS policies)
- Compute token diffs
- Gate PRs on design parity
- Drive AI-first code generation

## Required Files

| File | Source | Purpose |
|------|--------|---------|
| `figma_contract.json` | Figma API export | Feature contract with phase, owners, routes, tokens |
| `token_diff.json` | Generated | Diff between Figma tokens and `tokens.json` |
| `component_inventory.json` | Figma API export | Components used vs available |

## Figma Taxonomy

### Pages (Phases)
- `0-Portfolio` - Intake, qualification
- `1-Discovery` - IA, domain objects, roles
- `2-System-Design` - Architecture, integrations
- `3-Design` - UI specs, tokens, components
- `4-Build` - Implementation tracking
- `5-Test` - QA checklists
- `6-Launch` - Readiness, deployment

### Frame Naming Convention
```
[PHASE]-[SLUG]-[TYPE]
Example: 3-control-room-dashboard-Components
```

### Contract Table Block
Every feature frame MUST include a "Contract Table" section with:
- `feature_slug`
- `phase` (0-6)
- `owners` (Design/Eng/Data/Ops handles)
- `routes` (URL paths)
- `roles` (RLS roles affected)
- `tables_touched`
- `functions_touched`
- `tokens_touched`
- `success_metrics`

## Export Workflow

```bash
# Export from Figma (requires FIGMA_TOKEN)
./scripts/design/export_figma_contract.ts --file-key <KEY>

# Compute token diff
./scripts/design/compute_token_diff.ts

# Validate contract
./scripts/design/validate_contract.sh
```

## CI Gate Requirements

PRs that touch UI code must:
1. Include `ops/design/figma_contract.json` with matching `feature_slug`
2. Have `phase >= 3` (Design phase or later)
3. Include all `owners` as PR reviewers
4. Pass token diff validation (no unexpected changes)

## Schema

See `schemas/figma_contract.schema.json` for the strict JSON Schema.
