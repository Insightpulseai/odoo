# Examples — odoo-branch-series-governance

## Example 1: Series ready

**Input**: Check 19.0 series readiness across OCA repos in addons manifest

**Output**:
- Target version: 19.0
- OCB branch: exists — PASS
- repo-maintainer-conf: 19.0 rules defined — PASS
- CI tooling: pre-commit updated for 19.0 — PASS
- oca-github-bot: 19.0 series configured — PASS
- Migration issues: 34/34 repos have migration issues — PASS
- OCA repos with 19.0 branch: 30/34
- OCA repos missing 19.0 branch: server-auth, connector-telephony, l10n-thailand, reporting-engine
- Series readiness: partial (88% branch coverage)
- Blockers: 4 repos without 19.0 branch — check if modules from those repos are critical path

## Example 2: Series not ready

**Input**: Check 20.0 series readiness (pre-release)

**Output**:
- Target version: 20.0
- OCB branch: does not exist — FAIL
- repo-maintainer-conf: no 20.0 rules yet — FAIL
- CI tooling: not updated — FAIL
- oca-github-bot: not configured — FAIL
- Migration issues: not created — FAIL
- Series readiness: not ready
- Blockers: Odoo 20.0 not yet released. No OCA infrastructure available.

## Example 3: Custom repo alignment check

**Input**: Check if ipai_* custom modules follow OCA branch conventions

**Output**:
- Custom modules in addons/ipai/: 69
- Following OCA version convention (19.0.x.y.z): 52
- Non-conformant versioning: 17
  - ipai_finance_ppm: version `1.0.0` (should be `19.0.1.0.0`)
  - ... (16 more)
- Recommendation: align all ipai_* manifests to OCA version convention
