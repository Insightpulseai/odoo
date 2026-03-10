# Odoo Semantic Lint

Static analyzer that catches Python↔XML↔manifest mismatches at CI time, before
`odoo -i <module>` reveals them at install.

## Rules

| ID   | Severity | What it checks |
|------|----------|----------------|
| R001 | MEDIUM   | Duplicate `<record id="...">` within a module |
| R002 | LOW      | XML file present but not listed in `__manifest__.py` `data` |
| R003 | HIGH     | `ipai_*` dependency in `depends` not found in addons_path |
| R004 | LOW      | `res.config.settings` field possibly missing `config_parameter` |

## Usage

```bash
# Lint default addons/ipai directory
python3 scripts/odoo/odoo_semantic_lint.py

# Lint a specific addons directory
python3 scripts/odoo/odoo_semantic_lint.py addons/ipai_finance_ppm_umbrella

# Run built-in self-tests
python3 scripts/odoo/odoo_semantic_lint.py --self-test

# Write current findings to baseline (suppress pre-existing issues)
python3 scripts/odoo/odoo_semantic_lint.py --baseline
```

## Baseline

`scripts/odoo/baselines/odoo_semantic_lint_baseline.json` suppresses known
pre-existing findings so CI only fails on **new** issues introduced by a PR.

To update baseline after a known-good cleanup:
```bash
python3 scripts/odoo/odoo_semantic_lint.py --baseline
git add scripts/odoo/baselines/odoo_semantic_lint_baseline.json
git commit -m "chore(ci): update odoo semantic lint baseline"
```

## CI

`.github/workflows/odoo-semantic-lint.yml` runs on:
- PRs touching `addons/ipai/**` or `addons/ipai_*/**`
- Pushes to `main` touching those paths

HIGH severity findings fail CI. MEDIUM/LOW are reported but don't block merge
(promote to baseline-suppress or fix before they accumulate).

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | Clean (or only LOW/MEDIUM after baseline suppression) |
| 1    | HIGH severity findings present |
| 2    | Configuration error (addons dir not found) |
