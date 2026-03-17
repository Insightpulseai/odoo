# Evals — odoo-orm-model-extension

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Model extension uses correct _inherit; fields follow naming conventions; class attribute order is correct |
| Completeness | All requested fields and methods implemented; compute decorators present; constraints defined |
| Safety | No core/OCA file modifications; no cr.commit(); no context mutation; no Enterprise deps |
| Policy adherence | _inherit used (not copy); Command tuples for x2many; lazy translation; recordset methods |
| Evidence quality | py_compile result and test install log on disposable DB captured |
| Upgrade safety | Extension is purely additive via _inherit; no monkey-patching or direct source edits |
