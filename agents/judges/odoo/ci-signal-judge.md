# Judge: ci-signal-judge

## Scope

Validates that CI signals are green and authoritative before merge or deploy.

## Verdict: PASS when

- All required GitHub Actions checks pass
- No ignored red pipelines
- CI authority matches repo (GitHub Actions for CI + web deploy, Azure DevOps for Odoo/Databricks/Infra deploy)
- No duplicate CI lane ambiguity

## Verdict: FAIL when

- Any required check is red or skipped
- CI ran on wrong authority surface
- Duplicate pipelines exist for same concern

## Checks

1. Required status checks all green
2. Authority routing correct per `ssot/governance/platform-authority-split.yaml`
3. No stale/orphaned workflow runs
