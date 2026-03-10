# Tasks — IPAI Control Center (v1.0.0)

## T0 — Mergeability / CI Green (BLOCKER)
- [ ] Fix Docker compose restart loop:
  - split DB init to a one-shot service OR remove `--stop-after-init` from long-running service
  - add CI check to prevent recurrence
- [ ] Fix branding QWeb xmlid reuse:
  - ensure inherited templates have unique ids (e.g., `ipai_ce_branding_web_login_inherit`)
- [ ] Resolve PR conflicts in:
  - `addons/ipai_clarity_ppm_parity/*`
  - `addons/ipai_finance_ppm/*`
  - `addons/ipai_ppm_monthly_close/*`
  - `spec.md`
- [ ] Make CI green:
  - guardrails
  - repo-structure
  - parity tests

## T1 — Advisor Core (M1)
- [ ] Define ingestion payload schema (minimal + extensible)
- [ ] Implement `/api/advisor/ingest`:
  - auth
  - mapping
  - deterministic rec_key generation
  - idempotent upsert to Odoo + Supabase
- [ ] Implement lifecycle:
  - Open → Acknowledged → In Progress → Resolved
  - evidence + playbook link fields
  - status change audit log
- [ ] Implement scoring:
  - category scores
  - trend snapshots
  - `/api/advisor/recompute` + scheduled job

## T2 — PPM Core (M2)
- [ ] Portfolio model:
  - budget rollup
  - health scoring
  - KPIs
- [ ] Program model:
  - project aggregation
  - risk rollup
- [ ] Risk register:
  - impact × probability → severity
  - mitigation owner + due date
- [ ] Resource allocation:
  - capacity planning
  - overload detection
  - calendar integration

## T3 — Workbooks Registry (M3)
- [ ] Workbook model + views:
  - title, owner, tags, URL, system (Superset/Other), last_refresh
- [ ] Link to Superset assets:
  - dashboard URL
  - dataset identifiers (optional)
- [ ] Export / inventory:
  - CSV/JSON export for governance

## T4 — Connectors + Automation (M4)
- [ ] Add n8n workflows:
  - GitHub CI failure → create recommendation
  - Nightly recompute → write score snapshot
  - Mattermost notify on high severity
- [ ] Mattermost integration:
  - channels + templates
  - dedupe notifications by rec_key + state
- [ ] Observability:
  - ingest logs
  - recompute duration
  - queue depth (if async)

## T5 — Pulser SDK (Mandatory)
- [ ] Add Pulser SDK install instructions to repo docs
- [ ] Add minimal Pulser agent spec for:
  - nightly recompute
  - ingestion verification run
  - workbook export

## Optional Track — iOS Packaging (if pursued)
- [ ] Fork Next.js + Capacitor starter
- [ ] Wrapper mode against Control Center URL
- [ ] Add 2–3 native features (push/biometric/deep-links) to avoid App Store "minimum functionality"
