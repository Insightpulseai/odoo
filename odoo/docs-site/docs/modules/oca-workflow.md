# OCA workflow

OCA (Odoo Community Association) modules are the preferred source for features not available in Odoo CE. This page covers how to evaluate, adopt, and maintain OCA modules in InsightPulse AI.

## Non-negotiable rules

!!! danger "These rules are mandatory"

    1. **No `copier` in the repo root** — OCA scaffolding uses `copier` but it must never run in the repository root directory
    2. **Use `/tmp` for templates** — all `copier`/`mrbob` template operations run in `/tmp`, then copy results in
    3. **Selective port only** — never bulk-import an entire OCA repository; pick individual modules
    4. **Never modify OCA source** — treat OCA modules as read-only; extend via `ipai_*` modules

## Evaluation criteria

Before adopting an OCA module, verify:

| Criterion | Check |
|-----------|-------|
| Odoo 19 compatible | Branch `19.0` exists and CI passes |
| Active maintenance | Commits in the last 6 months |
| Test coverage | Module has unit tests |
| Dependencies | No dependency on EE or unavailable modules |
| License | LGPL-3 or AGPL-3 (compatible with CE) |

## Pre-commit setup

OCA modules require pre-commit hooks for code quality. Configure in the devcontainer:

```bash
pip install pre-commit
pre-commit install
```

The `.pre-commit-config.yaml` includes OCA-standard hooks:

- `pylint` with OCA plugin
- `flake8` with OCA conventions
- `isort` for import ordering
- `black` for code formatting (if enabled)

## Module scaffolding with mrbob

Create new OCA-compatible module structures using `mrbob`:

```bash
# Run in /tmp to avoid polluting the repo
cd /tmp
pip install bobtemplates.odoo
mrbob bobtemplates.odoo:addon

# Answer the prompts, then copy the result
cp -r /tmp/<module_name> /workspaces/odoo/addons/
```

!!! warning "Never run `mrbob` in the repo root"
    Template tools create temporary files and directories. Always run them in `/tmp` and copy the output.

## OCA module isolation

When you need to customize an OCA module's behavior:

### Step 1: Add OCA module as dependency

```python
# addons/ipai_account_ext/__manifest__.py
{
    "name": "IPAI Account Extensions",
    "depends": ["account_financial_report"],  # OCA module
    "auto_install": False,
}
```

### Step 2: Override in your module

```python
# addons/ipai_account_ext/models/report.py
from odoo import models

class FinancialReportExtension(models.Model):
    _inherit = "account.financial.report"

    def _compute_custom_field(self):
        # Your customization here
        ...
```

### Step 3: Extend views

```xml
<!-- addons/ipai_account_ext/views/report_views.xml -->
<odoo>
  <record id="view_financial_report_form_ext" model="ir.ui.view">
    <field name="name">account.financial.report.form.ext</field>
    <field name="model">account.financial.report</field>
    <field name="inherit_id" ref="account_financial_report.view_financial_report_form"/>
    <field name="arch" type="xml">
      <xpath expr="//field[@name='name']" position="after">
        <field name="custom_field"/>
      </xpath>
    </field>
  </record>
</odoo>
```

## Version pinning with `oca.lock.json`

Pin OCA module versions to prevent unexpected upgrades:

```json
{
  "account_financial_report": {
    "repo": "OCA/account-financial-reporting",
    "branch": "19.0",
    "commit": "a1b2c3d4e5f6",
    "adopted": "2026-02-15"
  },
  "account_reconcile_oca": {
    "repo": "OCA/account-reconcile",
    "branch": "19.0",
    "commit": "f6e5d4c3b2a1",
    "adopted": "2026-02-20"
  }
}
```

Update the lock file when upgrading an OCA module:

```bash
# After testing the new version
./scripts/oca_update_lock.sh account_financial_report <new_commit_hash>
```

## Updating an OCA module

1. Check the OCA repository for new commits on the `19.0` branch
2. Review the changelog for breaking changes
3. Update the module in `oca_addons/`
4. Run tests: `./scripts/odoo/odoo_test.sh -m <module_name>`
5. Update `oca.lock.json` with the new commit hash
6. Commit with `chore(oca): update <module_name> to <commit>`

!!! tip "Check OCA CI first"
    Before updating, verify the module's CI status on GitHub. A failing CI on the OCA side means the update is not ready.

## Directory structure

```
/workspaces/odoo/
├── addons/              # Custom ipai_* modules
│   ├── ipai_finance_ppm/
│   └── ipai_account_ext/
├── oca_addons/          # OCA module clones
│   ├── account-financial-reporting/
│   └── account-reconcile/
└── oca.lock.json        # Version pins
```
