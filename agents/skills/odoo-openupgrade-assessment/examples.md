# Examples — odoo-openupgrade-assessment

## Example 1: Clean upgrade with full coverage

**Input**: Upgrade from Odoo 18.0 to 19.0, 45 modules installed

**Output**:
- Current version: 18.0
- Target version: 19.0
- Total modules: 45
- Covered by OpenUpgrade: 38 (base, sale, account, purchase, stock, ...)
- Partial coverage: 4 (account_asset — script exists but no data migration for custom fields)
- No coverage: 3 (ipai_finance_ppm, ipai_ai_copilot, ipai_slack_connector)
- Custom modules requiring manual migration: 3
- Risk classification: medium
- Recommended next step: write migration scripts for 3 custom modules, then rehearse
- Evidence: OpenUpgrade 19.0 branch commit hash, per-module script listing

## Example 2: Upgrade with critical gaps

**Input**: Upgrade from Odoo 17.0 to 19.0, 120 modules installed (skip version)

**Output**:
- Current version: 17.0
- Target version: 19.0
- Total modules: 120
- Covered by OpenUpgrade: 62 (direct 17->19 scripts)
- Partial coverage: 18
- No coverage: 40 (including 25 OCA modules without 19.0 branches)
- Custom modules requiring manual migration: 12
- Risk classification: critical
- Recommended next step: do NOT attempt direct 17->19. Stage via 17->18->19 or address 40 gaps first.
- Evidence: OpenUpgrade branch inspection, OCA repo branch availability check

## Example 3: Minor version with near-complete coverage

**Input**: Upgrade from Odoo 18.0 to 18.0 (point release with schema changes)

**Output**:
- Current version: 18.0.20260101
- Target version: 18.0.20260315
- Total modules: 60
- Schema changes detected: 2 modules (account, stock)
- OpenUpgrade coverage: not applicable (point release)
- Recommended next step: standard update procedure, no OpenUpgrade needed
- Risk classification: low
