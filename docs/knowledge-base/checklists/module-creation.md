# Checklist: Module Creation

## Before Creating

- [ ] Verified CE configuration cannot solve this
- [ ] Searched OCA repos for existing 18.0 module
- [ ] Checked existing ipai_* modules for extensibility
- [ ] Confirmed this is truly custom to our business
- [ ] Named following `ipai_<domain>_<feature>` convention

## Module Structure

- [ ] `__init__.py` in root and every Python package
- [ ] `__manifest__.py` with all required fields
- [ ] `version` starts with `18.0.`
- [ ] `depends` lists only CE + OCA modules (no EE)
- [ ] `license` is `LGPL-3` or `AGPL-3`
- [ ] `data` key lists files in correct load order (security first, then views)
- [ ] `static/description/icon.png` exists (128x128)

## Models

- [ ] Every model has `_name` and `_description`
- [ ] Naming: `ipai.<domain>.<entity>` (dots, lowercase)
- [ ] `company_id` field on transactional models
- [ ] `mail.thread` mixin on auditable models
- [ ] `tracking=True` on critical fields
- [ ] All compute methods iterate `self`
- [ ] `@api.depends` declared for all stored computes
- [ ] `@api.constrains` for business rules

## Security

- [ ] `security/ir.model.access.csv` has entries for EVERY model
- [ ] User and manager groups defined
- [ ] Record rules for multi-company isolation
- [ ] No `sudo()` without documented justification

## Views

- [ ] Form view for each primary model
- [ ] List view for each primary model
- [ ] Search view with relevant filters and groups
- [ ] Proper `xml_id` naming: `<module>.<type>_<model>_<qualifier>`
- [ ] View inheritance uses xpath with specific selectors

## Tests

- [ ] `tests/__init__.py` imports all test modules
- [ ] Root `__init__.py` does NOT import tests
- [ ] At least one `TransactionCase` per model
- [ ] `@tagged("post_install", "-at_install")`
- [ ] Tests cover: defaults, transitions, constraints, computes
- [ ] Tests use disposable `test_<module>` database

## Pre-Commit

- [ ] Passes `pylint` (OCA plugin)
- [ ] Passes `flake8`
- [ ] Passes `isort`
- [ ] Passes `black`
- [ ] No hardcoded secrets

## Final

- [ ] Installs on fresh database: `odoo-bin -d test_<module> -i <module> --stop-after-init`
- [ ] All tests pass: `--test-enable`
- [ ] No Python warnings in install log
- [ ] No JavaScript console errors
