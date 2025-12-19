# Delivery Plan — IPAI Control Center (v1.0.0)

## 0) Current State (from repo + PR context)
- Modules implemented: `ipai_ppm`, `ipai_advisor` (+ Supabase ops_advisor schema).
- PR #61 has known P1 issues from Codex review:
  1) Docker compose restart loop risk: `--stop-after-init` + `restart: unless-stopped`.
  2) QWeb inheritance xmlid reuse in branding views.
- CI failing checks: guardrails, repo-structure, parity tests; merge blocked by conflicts in PPM parity + finance PPM files.

## 1) Target Architecture
### Odoo Modules (5-module architecture)
1. `ipai_workspace_core`
   - shared mixins, tags, ownership, base menus, mail threading patterns
2. `ipai_ppm`
   - portfolio/program/risk/resource allocation/kpi snapshots
3. `ipai_advisor`
   - categories, recommendations, playbooks, scoring, lifecycle, evidence
4. `ipai_workbooks`
   - workbook registry, links to Superset dashboards/datasets, ownership/tags
5. `ipai_connectors`
   - ingestion endpoints, webhook auth, mapping, scheduled sync jobs, outbound notifs

### Supabase (ops_advisor schema)
- `ops_advisor.recommendations`
- `ops_advisor.scores`
- `ops_advisor.activity_log`
- functions: deterministic key gen, upsert, recompute scores
- RLS policies per role

### Automation Bus
- n8n workflows produce signals → `ipai_connectors` endpoint → Odoo record + Supabase upsert
- Mattermost notifications on severity thresholds / status changes

### Pulser SDK
- Pulser SDK installed in repo with a minimal agent spec for:
  - nightly scoring refresh
  - report generation (workbooks export)
  - ingest verification run

## 2) Milestones
### M0 — Unblock Mergeability (Day 0–1)
- Fix compose restart loop by splitting init into one-shot job OR removing `--stop-after-init` from long-running service.
- Fix branding xmlid reuse: new unique ids for inherited QWeb templates.
- Resolve PR conflicts and re-run CI until green.

### M1 — Advisor MVP End-to-End (Day 1–3)
- Ingest endpoint contract + idempotent upsert
- Recommendation lifecycle UI + evidence panel + playbook links
- Score recompute (manual + scheduled)
- Supabase RLS + audit log consistency

### M2 — PPM MVP + Rollups (Day 3–5)
- Portfolio health rollup (budget/risk/resource load)
- Program aggregation across projects
- Resource allocation overload detection + capacity view
- KPI snapshots wiring (time-series)

### M3 — Workbooks Registry (Day 5–6)
- Workbook model + tagging + ownership
- Links to Superset dashboards/datasets
- "Open in Superset" + "Embed/Share" metadata fields

### M4 — Connectors + Notifs + Ops (Day 6–7)
- n8n templates for:
  - GitHub signal ingestion (CI failures → advisor rec)
  - nightly recompute scores
  - Mattermost notify rules
- Observability dashboards (basic)

## 3) Technical Decisions (Locked)
- Use Odoo mail.thread + activity for lifecycle and accountability.
- Use deterministic `rec_key` for dedupe (category + resource + rule + fingerprint).
- Use Supabase as analytics store + time-series snapshots; Odoo remains operational UI.
- Use only OCA modules from `18.0` branches and vendored with lockfile.

## 4) Risks + Mitigations
- **Apple "minimum functionality"** (if iOS wrapper is pursued): mitigate by adding push/biometric/deep-links.
- **OCA module drift**: mitigate with vendoring + lock file + CI pinning.
- **Data divergence** Odoo vs Supabase: mitigate with single ingestion path + idempotent upsert + audit log.

## 5) Verification (Automated)
- CI:
  - repo-structure, guardrails, parity tests
- Runtime:
  - `/web` health
  - seed install on fresh DB
  - ingest replay test (same payload twice → no dupes)
  - score recompute test (stable outputs)
