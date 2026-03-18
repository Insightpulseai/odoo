# Evals — odoo-data-migration-script

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Migration scripts handle correct schema/data changes; version numbers match manifest |
| Completeness | Both pre and post migration covered; fresh install guard present; logging included |
| Safety | No cr.commit(); tested on disposable DB only; idempotent operations |
| Policy adherence | Pre-migration uses raw SQL; post-migration uses ORM; version directory matches manifest |
| Evidence quality | Migration log output captured; forward migration and fresh install both tested |
| Upgrade safety | Migrations are idempotent; handle both upgrade and fresh install; no data loss |
