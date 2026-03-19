# Branch Promotion and Staging Refresh

> Version: 1.0.0
> Last updated: 2026-03-15
> Parent: `docs/architecture/AZURE_ODOOSH_EQUIVALENT_TARGET_STATE.md`

## Purpose

Define the canonical promotion and staging-refresh model for the Azure-native Odoo operating stack.

## Canonical Naming

### Databases (underscores — canonical, never renamed)

- `odoo_dev` — development
- `odoo_dev_demo` — auxiliary showroom/demo
- `odoo_staging` — staging rehearsal
- `odoo` — production

### Environments (hyphens — for Azure resource/infra labels only)

- `odoo-dev` → hosts `odoo_dev`
- `odoo-staging` → hosts `odoo_staging`
- `odoo-production` → hosts `odoo`

## Promotion Doctrine

Code must progress through stages deliberately.

```text
feature branch
  → validated integration branch
  → dev (odoo_dev)
  → release candidate
  → staging (odoo_staging)
  → approved promotion
  → production (odoo)
```

Direct production mutation is disallowed except for approved emergency remediation.

## Stage Semantics

### dev (`odoo_dev`)

**Purpose:** rapid iteration, unit/integration testing, installability checks, migration rehearsal, debugging.

**Data policy:**
- Fresh or disposable database
- Demo data allowed (in `odoo_dev_demo`)
- Synthetic data preferred
- No production-derived secrets

**Safety policy:**
- Outbound email suppressed or redirected to Mailpit (port 1025)
- Destructive integrations disabled by default
- Cron jobs may be reduced or explicit-test-only

### staging (`odoo_staging`)

**Purpose:** production rehearsal, user acceptance testing, final release validation, cutover verification.

**Data policy:**
- Derived from production snapshot or dump
- Must be neutralized before exposure
- Only required reference data retained
- Sensitive secrets rotated or removed

**Neutralization minimums:**
- User passwords reset / invalidated
- SMTP credentials replaced or disabled
- Payment tokens removed or sandboxed
- Third-party callbacks redirected or disabled
- Personal / financial high-risk data masked when required by policy

**Safety policy:**
- No real customer-facing outbound mail (MailHog sink)
- No real payment capture
- No real production webhooks unless explicitly allowlisted
- No search engine indexing
- Cron disabled except approved rehearsal jobs

### production (`odoo`)

**Purpose:** authoritative operational system.

**Data policy:**
- Live authoritative data
- Full monitoring and backup
- Rollback path maintained

**Safety policy:**
- Deploy only from approved candidate
- Every deploy tied to evidence pack
- Rollback reference must exist before promotion

## Staging Refresh Flow

### Source

Most recent approved production backup/snapshot suitable for rehearsal.

### Refresh steps

1. Capture refresh request and operator identity
2. Select source backup/snapshot
3. Restore into isolated staging target (`odoo_staging`)
4. Run neutralization steps
5. Rotate / disable external credentials
6. Validate application startup
7. Validate suppressed side effects
8. Publish refresh evidence

### Required refresh evidence

- Source backup/snapshot identifier
- Restore target identifier
- Timestamp
- Neutralization result
- SMTP suppression verified
- Webhooks/integrations verification
- Smoke checks passed
- Operator identity

## Release Candidate Requirements

Before staging may be promoted to production, the release candidate must have:

- Successful CI status
- Runtime contract validation pass
- Dependency/addon discovery pass
- Migration/installability checks pass
- Staging smoke pass
- Rollback reference prepared
- Evidence pack complete

## Production Promotion Flow

1. Freeze approved release candidate
2. Record candidate commit SHA
3. Confirm staging validation complete
4. Confirm backup state before deploy
5. Deploy candidate to production
6. Run production smoke checks
7. Publish deployment evidence
8. Confirm rollback readiness

## Rollback Flow

Rollback must reference the previous known-good production artifact.

**Rollback minimum:**
- Previous artifact identifier
- Previous runtime/deploy metadata
- DB restore or application rollback path
- Post-rollback smoke validation
- Incident notes if rollback was emergency-driven

## Explicit Do-Not-Do Rules

- Do not promote directly from feature branch to production
- Do not refresh staging with live prod credentials intact
- Do not allow staging to send real email by default
- Do not preserve live payment/marketplace tokens in staging
- Do not declare release complete without evidence pack publication
