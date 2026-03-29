# Judge: dependency-integrity-judge

## Scope

Validates that the OCA addon dependency chain is fully resolvable before installation or promotion.

## Verdict: PASS when

- All OCA repos are on the target Odoo version branch
- Every OCA repo with modules is in addons_path
- All `depends` in target module manifests resolve to available modules
- All `external_dependencies.python` packages are pip-installed
- No empty repos in addons_path
- Manifest version prefixes match target Odoo version

## Verdict: FAIL when

- Any OCA repo is on wrong branch (e.g. 18.0 on Odoo 19 runtime)
- Any repo with modules is missing from addons_path
- Any declared dependency is unresolvable
- Any Python external dependency is missing
- Manifest version mismatch detected

## Inputs

- `addons_path` (from odoo.conf or CLI)
- OCA repo root directory
- Target Odoo version
- Module list to validate

## Checks (ordered)

1. `oca.branch-version-audit` — all repos on correct branch
2. `oca.addon-discovery` check 2 — addons_path completeness
3. `oca.module-dependency-resolution` — full tree resolvable
4. `oca.manifest-review` — per-module manifest correctness

## Never

- Mutate any file or config
- Install modules
- Switch branches
- Only score and report
