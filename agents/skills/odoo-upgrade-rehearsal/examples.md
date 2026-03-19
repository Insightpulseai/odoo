# Examples — odoo-upgrade-rehearsal

## Example 1: Clean rehearsal pass

**Input**: Rehearse upgrade from 18.0 to 19.0 on disposable copy

**Output**:
- Source version: 18.0
- Target version: 19.0
- Database: `test_upgrade_18_to_19`
- Migration execution: PASS (12m 34s)
- Module status: 45/45 pass
- Data integrity: record counts match (res.partner: 1,204, account.move: 8,921)
- Test results: 312 tests, 312 pass, 0 fail
- Failure classification: none
- Blockers: none
- Evidence: `docs/evidence/20260317-1400/oca-governance/odoo-upgrade-rehearsal/test.log`

## Example 2: Rehearsal with migration gaps

**Input**: Rehearse upgrade with 3 custom modules lacking migration scripts

**Output**:
- Source version: 18.0
- Target version: 19.0
- Database: `test_upgrade_18_to_19`
- Migration execution: PARTIAL (migration completed but 3 modules failed init)
- Module status: 42/45 pass, 3 fail (ipai_finance_ppm, ipai_ai_copilot, ipai_bir_tax_compliance)
- Failure classification:
  - ipai_finance_ppm: migration gap — field `ppm_line_ids` renamed but no migration script
  - ipai_ai_copilot: migration gap — depends on removed `res.users.groups_id` (now `group_ids`)
  - ipai_bir_tax_compliance: real defect — compute method references deleted field
- Data integrity: cannot fully validate due to 3 failed modules
- Blockers: [3 custom modules require migration scripts before production upgrade]
- Evidence: `docs/evidence/20260317-1400/oca-governance/odoo-upgrade-rehearsal/test.log`

## Example 3: Blocker — wrong database used

**Input**: Rehearse upgrade against `odoo_dev`

**Output**:
- BLOCKER: Rehearsal target `odoo_dev` is a canonical dev database
- Action: Create disposable copy first: `createdb -T odoo_dev test_upgrade_18_to_19`
- Rehearsal NOT executed
