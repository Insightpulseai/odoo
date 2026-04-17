---
name: odoo-staging
category: tester
scope: odoo-on-azure
authority: docs/architecture/ODOO_SH_EQUIVALENCE_MATRIX.md
odoo_sh_equivalent: "Staging branches — built with production data, alive for weeks"
---

# odoo-staging — Copy Prod DB + Neutralize + Deploy Staging

## When to use

Use this skill when:
- A feature branch needs production-data testing before go-live
- QA needs a production-like environment
- You need to validate module upgrades against real data

## Decision workflow

```
1. Copy production database to staging:
   DROP DATABASE IF EXISTS odoo_staging;
   CREATE DATABASE odoo_staging WITH TEMPLATE odoo;

2. Neutralize staging (13 Odoo.sh safety items):
   Run scripts/ci/neutralize_staging.sql against odoo_staging
   
   Items neutralized:
   ✓ ir.cron deactivated (except auto-vacuum)
   ✓ Outbound mail servers disabled
   ✓ Payment providers → test mode
   ✓ IAP accounts deleted
   ✓ Fetchmail (inbound) disabled
   ✓ Social integrations disabled
   ✓ Bank sync disabled
   ✓ Marketplace accounts disabled
   ✓ Calendar sync tokens removed
   ✓ Drive sync tokens removed
   ✓ Government EDI cancelled
   ✓ web.base.url → staging URL
   ✓ robots.txt → noindex,nofollow

3. Deploy staging containers:
   odoo-web-staging, odoo-worker-staging, odoo-cron-staging
   With ODOO_STAGE=staging, ODOO_VERSION=18.0

4. Validate:
   → judge-staging-safety confirms all 13 items neutralized
   → Health check passes
   → URL accessible for testers
```

## Guardrails

- NEVER deploy staging without running the 13-item neutralization
- NEVER use staging for persistent data — it is rebuilt from prod on each deploy
- NEVER expose staging to customers without explicit test-sharing decision
- NEVER leave production mail servers active in staging
- NEVER leave payment providers in live mode in staging
- ALWAYS set ODOO_STAGE=staging so code can branch on environment

## Tools

- Azure Pipelines staging deployment stage
- `psql` for DB copy + neutralization script
- `az containerapp update` for ACA revision
- `judge-staging-safety` for validation

## Related

- `odoo-promote` — dev → staging promotion
- `odoo-ship` — staging → production
- `judge-staging-safety` — validates neutralization
- `odoo-mail-safety` — mail suppression details
