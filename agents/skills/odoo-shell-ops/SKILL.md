# Odoo Shell Ops Skill

## Purpose

Use the Odoo interactive shell for debugging and data operations. Covers odoo-bin shell, env access, recordset operations, and debugging workflows.

## Owner

odoo-cli-operator

## Preconditions

- Odoo CE 19.0 installed
- Target database exists and is initialized
- PostgreSQL accessible
- Note: Shell is interactive by nature but can be scripted via stdin piping

## Covered Operations

### Shell Launch

- `odoo-bin shell --database <db> --addons-path <paths>` — interactive shell
- `echo "commands" | odoo-bin shell --database <db>` — scripted shell execution
- `odoo-bin shell -d <db> < script.py` — execute Python script in Odoo env

### Environment Access (inside shell)

- `self` — current user recordset (res.users)
- `self.env` — Odoo environment
- `self.env['model.name']` — access any model
- `self.env.cr` — database cursor (read-only recommended)
- `self.env.uid` — current user ID
- `self.env.company` — current company
- `self.env.context` — current context dict

### Recordset Operations

- `self.env['res.partner'].search([('name', 'ilike', 'test')])` — search records
- `self.env['res.partner'].browse(1)` — browse by ID
- `record.read(['name', 'email'])` — read specific fields
- `record.mapped('field_name')` — extract field values
- `record.filtered(lambda r: r.active)` — filter recordset
- `record.sorted('name')` — sort recordset

### Debugging Workflows

- Inspect module state: `self.env['ir.module.module'].search([('name', '=', 'module')])`
- Check installed modules: `self.env['ir.module.module'].search([('state', '=', 'installed')])`
- Inspect model fields: `self.env['model.name'].fields_get()`
- Check access rights: `self.env['ir.model.access'].search([('model_id.model', '=', 'model.name')])`

## Disallowed Operations

- `self.env.cr.commit()` — BANNED, ORM handles transactions
- Direct SQL writes via cursor — use ORM methods
- Shell operations on production database from dev machine
- Long-running operations that block the database

## Verification

- Shell connected: prompt shows `env: <odoo.api.Environment>`
- Query results: recordset is not empty when expected
- After data inspection: close shell cleanly (exit() or Ctrl+D)
