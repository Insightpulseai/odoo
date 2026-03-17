# Examples — odoo-bot-automation-patterns

## Example 1: Pattern alignment audit

**Input**: Compare custom CI patterns against OCA bot for 19.0 series

**Output**:
- Series: 19.0
- OCA bot patterns:
  - Branch creation: auto-generated from repo-maintainer-conf rules
  - Migration issues: 1 issue per module per repo when branch created
  - CI: shared `oca-ci/github-action-*` reusable workflows
  - Merge: 2 reviews required, CI must pass, maintainer approval
  - Labels: auto-applied (migration, ready to merge, needs review)
- Custom CI patterns:
  - Branch creation: manual
  - Migration tracking: no auto-issue creation
  - CI: custom workflows in `.github/workflows/`
  - Merge: 1 review required, CI must pass
  - Labels: manual
- Alignment opportunities:
  - Adopt auto-migration issue creation for ipai_* modules on version bumps
  - Align review requirement to 2 reviewers for addons manifest changes
  - Consider shared workflow templates for module CI
- Recommendations:
  1. Create workflow to auto-generate migration issues when new Odoo version is targeted
  2. Update branch protection to require 2 reviews on addons/ path changes
  3. Adopt OCA-style reusable workflows for module testing

## Example 2: Bot health check

**Input**: Verify oca-github-bot is operational for 19.0 series

**Output**:
- Bot status: operational
- Last activity: 2 hours ago (branch creation on OCA/account-financial-tools)
- 19.0 series: fully supported
- Migration issues: 847 created across 34 repos
- Open migration issues: 312
- Closed (completed): 535
- Evidence: GitHub API query results for OCA org bot activity

## Example 3: Divergence analysis

**Input**: Identify intentional vs unintentional divergences from OCA patterns

**Output**:
- Intentional divergences:
  - Single reviewer (solo developer context) — accepted deviation
  - Custom deployment workflows (Azure-specific) — not applicable to OCA
  - ipai_* module CI (project-specific testing) — extends OCA pattern
- Unintentional divergences:
  - No auto-migration issue creation — should align
  - Inconsistent label usage — should adopt OCA label conventions
  - Stale submodule pins not automatically flagged — should add CI check
- Recommendations: address 3 unintentional divergences in next CI improvement cycle
