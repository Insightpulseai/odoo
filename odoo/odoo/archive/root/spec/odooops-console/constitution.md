# OdooOps Console — Constitution
# Spec: spec/odooops-console/
# Slug: odooops-console
# Last updated: 2026-03-01

---

## Purpose

Provide an Odoo.sh-equivalent operational control plane for Odoo CE on
DigitalOcean + Supabase, deployed via Vercel.

**Vercel project**: `odooops-console`
**Project ID**: `prj_0pVE25oMd1EHDD1Ks3Xr7RTgqfsX`
**Team slug**: `tbwa`
**Domain**: `https://odooops-console.vercel.app`

---

## Non-negotiable constraints

1. **SSOT-first**: All configuration is expressed in SSOT (`spec/odooops-console/` + `ssot/*`)
   and reflected in runtime state (`ops.*` tables). UI does not hardcode infra inventory.

2. **Baseline-plan bias**: Prefer Vercel-native + Supabase-native primitives before
   introducing paid marketplace integrations.

3. **No dead nav routes**: Any left-nav route must return HTTP 200 with a stable empty
   state. 404 is forbidden.

4. **JSON-only internal APIs**: All `/api/**` routes must return `application/json` for
   success and failure. No `204` responses without a JSON body. All responses must parse
   safely (no "Unexpected end of JSON input").

5. **Evidence-driven**: Every automated operation produces evidence artifacts (run IDs,
   logs, and/or files in Storage) and is linkable from the UI.

6. **Idempotent operations**: All jobs and inbound event handlers must be replay-safe
   (dedupe key + persisted ledger before side-effects).

7. **Secrets discipline**: Secrets are referenced only via SSOT secret keys (registry);
   no plaintext in repo. UI may display *presence* but not values.

8. **Provider adapters**: Vercel/Supabase/DigitalOcean/Slack/Plane integrations must be
   implemented as provider adapters with shared retry/backoff + error envelopes.

9. **Policy gates are product**: CI policy gates surfaced in UI must be deterministic,
   queryable, and backed by evidence artifacts.

10. **Maturity states**: Every feature declares `scaffold | beta | prod` maturity and
    required backing data sources.

11. **Odoo.sh parity constraints**: Enforce bounded execution (no daemonized processes),
    worker recycling assumptions, staging/dev resource constraints, and "no port 25"
    outbound SMTP parity restrictions.

12. **Parity gates**: CI must include parity checks for DB object count, cron/job timeout
    policy, and module dependency allowlist.

---

## Definition of Done (DoD)

A feature is complete when:

- [ ] UI routes stable (no 404 sub-routes)
- [ ] `ops.*` tables populated for each surfaced feature
- [ ] Evidence links present for builds/gates/backups/modules
- [ ] Secret flows audited (sync run records) and API responses parse-safe
- [ ] Parity constraints enforced or documented as deliberate non-parity
