# Contributing

Contributions to InsightPulse AI follow **OCA-style conventions** with spec-kit governance. Every change is small, focused, and verified before merge.

## Pages in this section

| Page | Description |
|------|-------------|
| [Content guidelines](content-guidelines.md) | Writing style for documentation and UI text |
| [Commit conventions](commits.md) | Commit message format and PR discipline |
| [Spec bundles](spec-bundles.md) | Specification structure for significant changes |

## Contribution workflow

1. Read the relevant spec bundle (if one exists for the feature area).
2. Create a focused branch from `main`.
3. Make changes following the module philosophy: Config > OCA > Delta (`ipai_*`).
4. Write or update tests alongside code changes.
5. Update documentation if behavior changes.
6. Run the verification sequence before pushing.
7. Open a PR with a clear description referencing the spec bundle.

## Verification before push

```bash
./scripts/repo_health.sh && ./scripts/spec_validate.sh && ./scripts/ci_local.sh
```

All three must pass before pushing. The `all-green-gates` CI check blocks merge on failure.
