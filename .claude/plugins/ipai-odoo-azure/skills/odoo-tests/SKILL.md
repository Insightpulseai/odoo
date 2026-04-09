---
name: odoo-tests
description: Write and run Odoo 18 module tests using disposable databases
triggers:
  - file_pattern: "addons/ipai/**/tests/*.py"
  - keywords: ["test_", "TransactionCase", "HttpCase", "--test-enable"]
layer: A-domain
---

# Odoo 18 Test Skill

1. Every test uses a disposable database: `test_<module_name>`
2. Never use `odoo` (prod), `odoo_dev` (dev), or `odoo_staging` for tests
3. Classify every failure: passes_locally | init_only | env_issue | migration_gap | real_defect
4. Save raw output to `docs/evidence/<YYYYMMDD-HHMM>/<module>/test.log`
5. Never claim "all tests pass" without citing the evidence log
6. Pipeline runner: `scripts/ci/run_odoo_tests.sh`
7. Safety guard in runner refuses non-disposable DB names
