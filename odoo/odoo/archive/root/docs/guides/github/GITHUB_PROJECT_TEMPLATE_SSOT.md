# GitHub Project Template SSOT

## Purpose

This repository manages GitHub Projects v2 as code:

- Template specs: `odoo/ssot/github/projects/templates/*.project.yaml`
- Template schema: `odoo/ssot/github/projects/templates/schema.project-template.v1.json`
- Projection metadata: `odoo/ssot/github/projects/*.yaml`
- Validator: `odoo/scripts/github/validate_project_template_ssot.py`
- Sync tool: `odoo/scripts/github/sync_project_template.py`

## Workflow split

- PRs run validation and dry-run drift checks only.
- `main` and scheduled runs perform apply sync.

Workflows:

- `odoo/.github/workflows/github-project-template-ssot-gate.yml`
- `odoo/.github/workflows/sync-github-project-templates.yml`

## Add a new template

1. Create a new `*.project.yaml` under `odoo/ssot/github/projects/templates/`.
2. Create or update its projection file under `odoo/ssot/github/projects/`.
3. Run local validation.
4. Run local dry-run sync.

## Commands

```bash
python odoo/scripts/github/validate_project_template_ssot.py \
  --spec "odoo/ssot/github/projects/templates/*.project.yaml" \
  --schema "odoo/ssot/github/projects/templates/schema.project-template.v1.json" \
  --json-output "odoo/artifacts/github/projects/validation_report.json"

python odoo/scripts/github/sync_project_template.py \
  --dry-run \
  --spec odoo/ssot/github/projects/templates/finops_month_end.project.yaml \
  --output odoo/artifacts/github/projects/drift_report.json
```

## Drift report format

`drift_report.json` contains:

- `spec_id`
- `org`
- `project_title`
- `project_number`
- `mode` (`dry-run` or `apply`)
- `missing_fields`
- `extra_fields`
- `changed_fields`
- `option_diffs`
- `has_drift`

## Secrets

Set `GITHUB_PROJECTS_TOKEN` in GitHub Actions.

Required scopes:

- `read:project` for dry-run
- `project` for apply

If scope is missing, sync exits with:

`CI.GH_PROJECTS_TOKEN_MISSING_SCOPE read:project|project`
