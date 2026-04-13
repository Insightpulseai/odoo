# Technical Guide

> **Purpose of this file.** Answer HOW this module is built, for maintainers and reviewers.
> Required by `CLAUDE.md` §"Odoo extension and customization doctrine".

## Architecture

One-paragraph description + diagram if helpful (ASCII or link to `docs/architecture.svg`).

## Models extended

| Model | Technique | Fields added | Purpose |
|---|---|---|---|
| `res.partner` | `_inherit` | `x_ipai_foo`, `x_ipai_bar` | ... |

## Fields added

For each new field:

- **Field name:** `x_ipai_<name>`
- **Type:** `Char | Many2one | Selection | ...`
- **Required:** yes/no
- **Indexed:** yes/no
- **Stored:** yes/no (note if computed + stored)
- **Why this field is needed:** ...
- **Default:** ...

## Methods overridden

| Method | Reason | `super()` call preserved? |
|---|---|---|
| `action_confirm` | Add pre-check for X | Yes — line N |

## View inheritance points

| View | Technique | XPath target | Purpose |
|---|---|---|---|
| `res.partner.view_form` | `<xpath expr="..."/>` | Add tab | ... |

## Security model

- **Groups introduced:** `ipai_<module>_user`, `ipai_<module>_admin`
- **Record rules:** (multi-company rules per `docs/tenants/TENANCY_MODEL.md`)
- **Access CSV:** `security/ir.model.access.csv`
- **Inherits from:** `base.group_user`, `base.group_portal`

## Data files loaded

| File | Purpose | Load order |
|---|---|---|
| `data/parameter.xml` | ir.config_parameter defaults | Before demo |
| `security/ir.model.access.csv` | ACL | Pre-init |

## External integrations

| Integration | Protocol | Auth | Secret source |
|---|---|---|---|
| Foundry Document Intelligence | REST | Managed Identity | Azure Key Vault |
| Zoho SMTP | SMTP/587 | User+pass | Azure Key Vault (`zoho-smtp-user`, `zoho-smtp-password`) |

## Jobs / cron / queues / webhooks

| Job | Schedule | Purpose | Timeout |
|---|---|---|---|
| `_cron_<name>` | every 1h | ... | 5min |

## Test strategy

- **Unit tests:** `tests/test_<model>.py` — covers <scenarios>
- **Integration tests:** `tests/test_integration.py` — covers <scenarios>
- **Test DB:** `test_ipai_<module>` (disposable per CLAUDE.md)
- **CI job:** `.github/workflows/<workflow>.yml` or Azure DevOps pipeline
- **Coverage target:** ≥80%

## Upgrade / rollback notes

- **Install:** `./scripts/odoo_install.sh -d odoo_dev -m ipai_<module>`
- **Upgrade:** migrations in `migrations/<version>/pre-migration.py` and `post-migration.py`
- **Rollback:** data migrations are reversible via `post-migration.py` down-scripts
- **Downtime:** <none | seconds | minutes>

## Known limitations and failure modes

- **Limit:** ... (workaround: ...)
- **Failure mode:** ... (detection: ..., recovery: ...)
