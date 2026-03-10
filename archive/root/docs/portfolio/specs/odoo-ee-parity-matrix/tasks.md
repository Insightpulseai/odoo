# Tasks — Odoo EE → CE/OCA Parity Matrix

## M0 — Spec kit + CI

- [x] Add spec kit files under spec/odoo-ee-parity-matrix/
- [x] Add scripts/validate_spec_kit.sh
- [x] Add catalog schema + validator script
- [x] Add GitHub Actions workflow gates

## M1 — Catalog

- [x] Create catalog/odoo_parity_plans.schema.json
- [x] Create catalog/odoo_parity_plans.yaml seed
- [ ] Validate in CI

## M2 — Seed 25–40 mappings

- [ ] Finance (accounting, invoicing, payment)
- [ ] HR (recruitment, appraisals, fleet)
- [ ] Documents/DMS
- [ ] Helpdesk/Support
- [ ] Field Service/Maintenance
- [ ] Governance/Security
- [ ] BI/Reporting

## M3 — Verification Automation

- [ ] Dockerized Odoo CE + OCA smoke runner
- [ ] last_verified timestamps
- [ ] CI integration for smoke tests
