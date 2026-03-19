# Neutralize & Populate Policy

## Neutralization Rules

- ALWAYS backup before neutralizing
- NEVER neutralize production database in-place — copy first, then neutralize the copy
- NEVER share non-neutralized production data with third parties
- Refuse to neutralize `odoo` and `odoo_staging` directly — require explicit copy step
- After neutralization, verify sensitive data is actually stripped (run verification queries)

## Populate Rules

- NEVER populate production databases (odoo, odoo_staging)
- Populate is for development and demo databases only
- Not all models support populate — modules must implement _populate_factories
- Size options (small/medium/large) depend on module implementation

## Data Safety

- Neutralized databases may still contain business logic configuration
- Review ir_config_parameter for any remaining sensitive values
- Check fetchmail_server for webhook URLs
- Verify no OAuth tokens or API keys remain in the database

## Workflow Enforcement

1. Backup (mandatory)
2. Copy to development database name
3. Neutralize the copy
4. Verify neutralization
5. Optionally populate
6. Share or use for development

Skipping any step is a policy violation.
