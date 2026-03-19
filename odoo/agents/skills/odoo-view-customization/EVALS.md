# Evals — odoo-view-customization

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Xpath expressions target correct elements; inherit_id references are valid; XML IDs follow convention |
| Completeness | All requested UI changes implemented; actions and menus wired correctly |
| Safety | No core/OCA XML files modified; no view replacements (only inheritance) |
| Policy adherence | XML ID conventions followed; Odoo 19 terminology used; xpath positions explicit |
| Evidence quality | XML validation result and view rendering screenshot/log captured |
| Upgrade safety | All changes are purely additive via view inheritance; no direct patching |
