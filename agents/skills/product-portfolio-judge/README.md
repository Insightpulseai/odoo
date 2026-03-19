# product-portfolio-judge

Validates alignment between product specs and portfolio goals — detects drift, orphan specs, unfunded goals, and scope mismatch.

## When to use
- Pre-release gate (mandatory)
- Quarterly alignment review
- New spec bundle merged to main
- OKR update or amendment

## Key rule
The judge requires both product-manager and portfolio-manager outputs as inputs.
It never auto-closes or auto-resolves items — it flags misalignment for human decision.
Items older than 30 days without activity are flagged as stale.

## Cross-references
- `agents/skills/product-manager/skill-contract.yaml`
- `agents/skills/portfolio-manager/skill-contract.yaml`
- `docs/contracts/boards-to-spec-contract.md` (C-31)
- `docs/contracts/spec-to-pipeline-contract.md` (C-32)
- `docs/contracts/eval-gate-contract.md`
- `agents/knowledge/benchmarks/openai-product-use-cases.md`
