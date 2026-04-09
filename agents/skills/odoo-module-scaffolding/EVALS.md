# Evals — odoo-module-scaffolding

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Module structure matches Odoo 18 conventions; manifest is valid Python with correct version/license |
| Completeness | All required files created: manifest, init, models, security CSV, views, tests, README |
| Safety | No Enterprise dependencies; no IAP dependencies; no core file modifications |
| Policy adherence | ipai_<domain>_<feature> naming enforced; LGPL-3 license; all 4 CRUD columns in ACL CSV |
| Evidence quality | File tree output and py_compile result captured in evidence directory |
| Upgrade safety | Module uses _inherit for extensions; no vendor/odoo/ modifications |
