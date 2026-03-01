# OdooOps Console — Tasks
# Spec: spec/odooops-console/
# Slug: odooops-console
# Last updated: 2026-03-01

---

## Phase 1 — Route Stability (DONE ✅)

1. ~~Fix `/logs` 404~~ → **DONE**: `app/logs/page.tsx` committed, `.gitignore` exception added. (commit `df209ea2c`)
2. Add nav-route smoke test ensuring all left-nav routes resolve in prod build.

---

## Phase 2 — Secret Sync Robustness

3. Add `safeJson(res)` helper and update UI to never throw "Unexpected end of JSON input".
4. Update API route for secret sync to always return JSON (no `204` without body).
5. Add `ops.secret_sync_runs` migration; write an audit record per sync attempt.

---

## Phase 3 — Integrations Catalog (DONE ✅)

6. ~~Create `ops.integrations_catalog` + `ops.integrations_installations`~~ → **DONE** (`20260301000040_ops_integrations_catalog.sql`).
7. ~~Seed catalog with current installed + extended entries~~ → **DONE** (12 rows seeded).
8. ~~Update `/integrations` to render from catalog + installations (baseline filter)~~ → **DONE** (`integrations-client.tsx`).

---

## Phase 4 — DigitalOcean Provider (DONE ✅)

9. ~~Create `docs/contracts/C-DO-01-digitalocean-api.md`~~ → **DONE** (C-18 in contracts index).
10. ~~Create `ssot/providers/digitalocean/provider.yaml`~~ → **DONE**.
11. ~~Create `ops.do_droplets` + `ops.do_databases` + `ops.do_firewalls` + `ops.do_actions` + `ops.do_ingest_runs`~~ → **DONE** (`20260301000050_ops_digitalocean.sql`).
12. Implement `ops-do-ingest` Edge Function:
    - List droplets/databases/firewalls via DO API v2
    - Upsert into `ops.do_*` tables
    - Write `ops.do_ingest_runs` + `ops.run_events` for audit
    - Bounded retries (max 5) for 429/5xx
13. Update Overview "Active Nodes" to query `ops.do_droplets` + `ops.do_databases`.
14. Create `/platform/digitalocean` page with Droplets/Databases/Networking cards.

---

## Phase 5 — Control Plane Maturation

15. Create `ops.capabilities` migration seeding Supabase primitives:
    - database, auth, rls, edge_functions, realtime, storage, vault, branches, logs, metrics
    - Each with `maturity`, `data_source`, `baseline_allowed` fields
16. Update `/control-plane` page to read capability maturity from `ops.capabilities`.
17. Add "Coming online" state for `scaffold`-tier capabilities (no spinner, no broken states).

---

## Phase 6 — Modules + SSOT Waves

18. Add `ssot/modules/waves.yaml` (Wave 1–4 OCA module lists).
19. Define CI artifact contract: `module_status_<env>.txt` + diff JSON.
20. Update `/modules` UI: Wave tabs + installed vs allowlisted diff + evidence links.

---

## Phase 7 — Advisor + Observability + Metrics

21. Create `ops.advisor_runs` + `ops.advisor_findings` migrations.
22. Wire "Run Scan" button to job executor; persist findings.
23. Ensure `/metrics` page is SSOT-backed; store `GRAFANA_DASHBOARD_URL` presence in settings.

---

## Phase 8 — Odoo.sh Parity Gates (MUST)

24. Add parity policy gates (CI-enforced):
    - DB object count guard: `tables + sequences > 10000` → gate FAIL
    - Job timeout policy: enforce max duration + auto-disable on repeated timeout
    - Staging/dev concurrency constraints: single-worker semantics documented
    - SMTP port policy: `SMTP_PORT = 25` in non-prod → gate FAIL
    - Mail catcher enforced in non-prod (task 27 below)
25. Add `docs/contracts/C-ODOOS-01-parity.md`:
    - Parity matrix (feature → module → evidence)
    - "Restrictions modeled" section
    - Explicit non-parity list
26. Add runbooks:
    - `docs/ops/runbooks/mail-catcher.md`
    - `docs/ops/runbooks/web-shell.md` (exec adapter)
    - `docs/ops/runbooks/staging-branches.md` (lifecycle + data policy)

---

## Phase 9 — Mail Catcher (Mailgun Parity)

27. Create `ops.mail_events` migration:
    - `id` (uuid pk), `env` (prod|stage|dev), `provider` (mailgun),
      `message_id`, `subject`, `sender`, `recipient`,
      `transport` (e.g. `smtp.mailgun.org:2525`), `stamp`,
      `raw` (jsonb), `received_at`
28. Implement `ops-mailgun-ingest` Edge Function:
    - Verify Mailgun webhook HMAC signature
    - Normalize + upsert into `ops.mail_events`
    - Return `{ ok: true }` JSON always
29. Create `ssot/integrations/mailgun.yaml`:
    - domain `mg.insightpulseai.com`, SMTP host/ports, webhook config, evidence fields
30. Update `ssot/secrets/registry.yaml`: add `mailgun_api_key`, `mailgun_signing_key`, `mailgun_smtp_password`.
31. Add "Mail Catcher" panel under Observability:
    - Last 50 events, filter by env
    - Columns: stamp / subject / from / to / transport / env
32. Add `docs/contracts/C-MAIL-01-mail-catcher.md`.
33. Add CI gate: STAGE/DEV `SMTP_HOST` must be `smtp.mailgun.org`; `SMTP_PORT=25` → FAIL.

---

## Phase 10 — Starters Catalog

34. Create `ssot/sources/github/vercel_examples.yaml` (vercel/examples repo metadata).
35. Create `ops.starters` migration (source, slug, title, framework, tags, deploy_url).
36. Implement ingestion job pulling GitHub API for vercel/examples.
37. Create `/resources/starters` page with Deploy Button URL generation.

---

## Phase 11 — Spec Kit Spec Validate Guard

38. Add CI check: all nav routes from layout have a corresponding `app/*/page.tsx` or `app/**/page.tsx`.
39. Add `scripts/check-spec-kit.sh` for `spec/odooops-console/` bundle completeness validation.
