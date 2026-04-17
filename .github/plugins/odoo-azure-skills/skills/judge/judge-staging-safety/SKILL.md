---
name: judge-staging-safety
category: judge
scope: odoo-on-azure
authority: docs/architecture/ODOO_SH_EQUIVALENCE_MATRIX.md
odoo_sh_equivalent: "Staging safety — 13-item neutralization per Odoo.sh FAQ"
---

# judge-staging-safety — Validate Staging Neutralization

## Purpose

Validates that ALL 13 Odoo.sh staging safety items are neutralized before declaring staging ready for testing. Blocks staging access if any item fails.

## Checklist (all must PASS)

```sql
-- Run against odoo_staging database. Every query must return 0 rows.

-- 1. Active cron (except auto-vacuum)
SELECT count(*) FROM ir_cron WHERE active=true AND function != 'autovacuum';
-- EXPECTED: 0

-- 2. Active outbound mail servers
SELECT count(*) FROM ir_mail_server WHERE active=true;
-- EXPECTED: 0

-- 3. Payment providers in live mode
SELECT count(*) FROM payment_provider WHERE state='enabled';
-- EXPECTED: 0

-- 4. IAP accounts present
SELECT count(*) FROM iap_account;
-- EXPECTED: 0

-- 5. Active fetchmail servers
SELECT count(*) FROM fetchmail_server WHERE active=true;
-- EXPECTED: 0

-- 6. Active social integrations
SELECT count(*) FROM social_account WHERE active=true;
-- EXPECTED: 0 (or table doesn't exist)

-- 7. Bank sync active
SELECT count(*) FROM online_bank_statement_provider WHERE state != 'disabled';
-- EXPECTED: 0 (or table doesn't exist)

-- 8. Marketplace accounts active
SELECT count(*) FROM sale_amazon_account WHERE active=true;
-- EXPECTED: 0 (or table doesn't exist)

-- 9. Calendar sync tokens present
SELECT count(*) FROM res_users WHERE google_calendar_token IS NOT NULL OR microsoft_calendar_token IS NOT NULL;
-- EXPECTED: 0

-- 10. Drive sync tokens present
SELECT count(*) FROM res_users WHERE google_drive_access_token IS NOT NULL;
-- EXPECTED: 0 (or column doesn't exist)

-- 11. Government EDI in sent state
SELECT count(*) FROM account_edi_document WHERE state='sent';
-- EXPECTED: 0 (or table doesn't exist)

-- 12. web.base.url points to production
SELECT count(*) FROM ir_config_parameter WHERE key='web.base.url' AND value NOT LIKE '%staging%';
-- EXPECTED: 0

-- 13. robots.txt allows indexing
SELECT count(*) FROM ir_config_parameter WHERE key='website.robots' AND value NOT LIKE '%noindex%';
-- EXPECTED: 0
```

## Verdict

- **PASS**: all 13 checks return 0 → staging is safe for testing
- **FAIL**: any check returns >0 → block staging, report which items failed
- **ERROR**: query fails (missing table) → treat as PASS for that item (module not installed)

## When to run

- After every staging DB copy from production
- Before granting tester access to staging URL
- As a pipeline gate in the staging deploy stage

## Tools

- `psql` against `odoo_staging` database
- Azure Pipeline task in staging deploy stage
- Can be invoked by Pulser supervisor as a judge worker

## Related

- `odoo-staging` — the staging deploy workflow that triggers this judge
- `scripts/ci/neutralize_staging.sql` — the script that performs neutralization
