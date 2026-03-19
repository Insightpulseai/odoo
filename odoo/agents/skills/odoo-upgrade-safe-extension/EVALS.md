# Evals — odoo-upgrade-safe-extension

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly identifies _inherit usage, core modifications, and deprecated patterns |
| Completeness | All files in module audited; migration script presence checked; all Odoo 19 breaking changes verified |
| Safety | No false negatives on core/OCA modifications; all deprecated patterns flagged |
| Policy adherence | _inherit enforced; OCA governance rules followed; migration scripts required for schema changes |
| Evidence quality | File-level audit results with line references for deprecated patterns |
| Upgrade safety | Assessment correctly reflects whether module will survive a minor/major Odoo version bump |
