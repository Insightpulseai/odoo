# product-manager

Owns the feature specification lifecycle — PRDs, acceptance criteria, spec bundles, and feature prioritization.

## When to use
- New feature request arrives
- Spec bundle needs review or validation
- PRD requires update or refinement
- Acceptance criteria need validation for measurability

## Key rule
Every feature must have a complete spec bundle (`constitution.md`, `prd.md`, `plan.md`, `tasks.md`)
with measurable acceptance criteria before entering the build pipeline.
A spec without a parent OKR reference is incomplete.

## Cross-references
- `spec/` — all spec bundles
- `docs/contracts/boards-to-spec-contract.md` (C-31)
- `docs/contracts/spec-to-pipeline-contract.md` (C-32)
- `agents/knowledge/benchmarks/openai-product-use-cases.md`
