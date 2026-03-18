# Evals — odoo-test-authoring

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Tests verify the intended behavior; assertions are correct and specific |
| Completeness | All requested scenarios covered; setUp creates all needed test data; failures classified |
| Safety | Tests run on disposable DB only; no prod/dev/staging DB usage; no cr.commit() |
| Policy adherence | Failure classification applied to every result; evidence log cited for pass claims |
| Evidence quality | Raw test output saved with module name, DB name, test count, pass/fail, tracebacks |
| Upgrade safety | Tests use _inherit-based test data; no direct core modifications in test fixtures |
