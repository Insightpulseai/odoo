# Tasks — Platform Master Index

> Cross-cutting task index for the full platform stack.
> Status is verified against actual repo artifacts, not PR claims.
>
> Legend:
>   [x] = shipped (artifact exists in repo)
>   [-] = staged (committed but not deployed/verified)
>   [ ] = NOT DONE (missing from repo)
>
> Last audited: 2026-03-01

---

## EPIC E1 — SoR/SSOT/SoW Doctrine + Ops Ledger

### T1.1 Define boundary doctrine (SoR/SSOT/SoW)
- [x] docs/architecture/SSOT_BOUNDARIES.md — 14 boundary sections
- [x] docs/architecture/PLATFORM_REPO_TREE.md — surface area allowlist
- [x] .claude/rules/ssot-platform.md — 10 agent behavior rules
- Success: forbidden cross-boundary writes without contract; all actions emit ops.runs

### T1.2 Establish ops ledger primitives (ops.runs, ops.run_events, artifacts)
- [x] supabase/migrations/20260125_000002_ops_run_system.sql — ops.runs, ops.run_events, ops.artifacts
- [x] supabase/migrations/20260124000004_ops_multisignal_scoring.sql — health_windows, alert_state
- [x] supabase/migrations/20260124000005_ops_routing_matrix_escalation.sql — routing
- [x] supabase/migrations/20260124100001_ops_config_registry.sql — config registry
- Success: idempotency keys on all automations; evidence artifacts recorded

### T1.3 Enforce "No UI-only configuration"
- [x] docs/contracts/ODOO_SETTINGS_CONTRACT.md — settings-as-code
- [x] docs/contracts/SUPABASE_CRON_CONTRACT.md — cron-as-code
- [ ] CI gate: detect forbidden UI-only dependencies (not implemented)
- Success: scheduling/webhooks in migrations/config; CI catches violations

---

## EPIC E2 — SoW (Notion-like Workspace) Layer

### T2.1 Implement work.* schema and content model
- [x] supabase/migrations (work schema referenced in ops run system)
- [-] work.pages, work.blocks — schema exists but CRUD verification pending
- [ ] Permissions gate — RLS policies for work.* not separately audited
- Success: CRUD works; permissions gate works

### T2.2 Indexing pipeline (queue + tsvector + optional embeddings)
- [x] supabase/migrations/20260124_1000_ops_lakehouse_control_plane.sql — lakehouse/indexing
- [x] supabase/functions/embed-chunk-worker/index.ts — embedding worker
- [x] supabase/functions/memory-ingest/index.ts — memory ingestion
- [x] supabase/functions/infra-memory-ingest/index.ts — infra memory
- Success: insert/update produces indexable entries; retry + backoff

### T2.3 RAG endpoint (ask-docs) with citations + auth gates
- [x] supabase/functions/docs-ai-ask/index.ts — RAG endpoint
- [x] supabase/functions/context-resolve/index.ts — context resolution
- [ ] Citation stability verification — not separately audited
- [ ] KEY_MISSING behavior verification — not separately audited
- Success: returns stable citation IDs; rejects unauthorized; KEY_MISSING on missing keys

---

## EPIC E3 — Slack Agent Surface (SoW Intake + Taskbus Trigger)

### T3.1 Slack agent app baseline
- [x] ssot/bridges/catalog.yaml — ipai_slack_connector (status: active)
- [x] ssot/secrets/registry.yaml — slack_bot_token, slack_signing_secret
- [x] addons/ipai/ipai_slack_connector/ — Odoo addon
- Success: signature verification + idempotency

### T3.2 Slack → SoW/Plane intake workflow
- [-] Slack agent exists; Plane intake contract staged
- [ ] Thread key idempotency (workspace:channel:thread_ts) — not verified
- [ ] Work item creation from Slack thread — not implemented end-to-end
- Success: thread key idempotency; creates work item + logs run events

---

## EPIC E4 — Advisor Engine + Scoring Model

### T4.1 Advisor SSOT definitions (assessments/rubrics/workbooks)
- [x] supabase/migrations/20251219_ops_advisor_schema.sql — ops_advisor schema
- [x] spec/odooops-sh/ — advisor referenced in ops platform spec
- Success: schema stable + discoverable + versioned

### T4.2 Advisor DB primitives for scoring persistence
- [x] supabase/migrations/20260124000004_ops_multisignal_scoring.sql — health_windows, scoring
- [x] supabase/migrations/20260124000005_ops_routing_matrix_escalation.sql — routing + escalation
- Success: migrations apply cleanly; indexes present

### T4.3 Advisor runtime scan routes
- [x] supabase/functions/ops-advisory-scan/index.ts — scan edge function
- [x] platform/advisor/scorer.ts — scoring engine exists
- [-] TODO at scorer.ts:127: "Route to sources/vercel.ts, sources/supabase.ts, sources/digitalocean.ts" — NOT WIRED
- [ ] Verification: writes ops.advisor_scans, ops.advisor_findings — not audited
- [ ] Verification: 503 KEY_MISSING with SSOT hint — not audited
- Success: writes findings + scores; KEY_MISSING behavior consistent

### T4.4 Vercel deployment health scan
- [ ] Scan edge function for Vercel — NOT DONE
- [ ] Detects error rate, root dir drift, node override drift — NOT DONE
- [ ] Emits findings + workbook actions — NOT DONE
- Why needed: multiple errored deployments; production override drift
- Success: detects error rate + drift; emits findings + workbook actions

---

## EPIC E5 — Microsoft 365 Copilot Interaction Plane

### T5.1 SSOT: agent actions + capabilities + drift guards
- [x] design/tokens/m365_planner.tokens.json — M365 design tokens
- [x] design/wireframe/m365_planner.shell.json — M365 wireframes
- [x] spec/microsoft-agent-framework-pilot/ — Microsoft Agent Framework evaluation spec
- [x] docs/evidence/20260212-2045/o365-integration/IMPLEMENTATION.md — O365 email shipped (ipai_bir_notifications + bir-urgent-alert)
- [ ] Agent capabilities manifest + drift CI — not found in repo
- Success: generated manifest matches SSOT; CI fails on drift

### T5.2 Runtime: m365 broker Edge Function
- [x] supabase/functions/copilot-chat/index.ts — copilot chat broker
- [x] supabase/functions/ipai-copilot/index.ts — IPAI copilot function
- [ ] /manifest deterministic endpoint — not separately verified
- [ ] /query membership gate via work_is_member — not verified
- [ ] /action allowlist enforcement — not verified
- Success: manifest deterministic; membership gated; allowlist enforced

### T5.3 Identity mapping (M365 subject → platform subject)
- [ ] Deterministic mapping M365 → Supabase subject — NOT DONE
- [ ] Replay protection / signature verification — NOT DONE
- [ ] Audit trail ties M365 user to run — NOT DONE
- Why needed: M365 users must map to platform identity for authorization
- Success: deterministic mapping; replay protection; audit trail

---

## EPIC E6 — Plane Marketplace Integration Suite

### T6.1 SSOT contracts: plane core + mcp + github sync + slack intake + sentry
- [x] supabase/migrations/20260124120000_marketplace_integrations.sql — marketplace schema
- [x] supabase/functions/marketplace-webhook/index.ts — webhook handler
- [x] docs/evidence/20260212-2045/plane-integration/IMPLEMENTATION.md — Plane integration shipped (ipai_bir_plane_sync, 10 files, ~1300 lines)
- [x] web/platform-kit/schemas/sync/odoo-plane-sync.schema.json — sync schema
- [ ] docs/contracts/ — no Plane-specific contract doc
- Success: SSOT entries indexed; secrets listed; mapping scaffolds

### T6.2 Plane MCP server
- [ ] MCP server for Plane — not found in repo
- [ ] Tool allowlist enforcement — NOT DONE
- [ ] ops.run_events buffered if Supabase down — NOT DONE
- Success: tool allowlist enforced; events buffered

### T6.3 Plane GitHub sync Edge Function
- [x] supabase/functions/plane-sync/index.ts — sync function exists
- [ ] Idempotent on delivery ID — not verified
- [ ] Mapping missing → no-op + warning — not verified
- Success: idempotent on delivery ID; missing mapping = no-op + warning

### T6.4 Sentry → Plane Edge Function
- [ ] Sentry intake → Plane work items — NOT DONE
- [ ] Fingerprint dedup — NOT DONE
- [ ] HMAC verification — NOT DONE
- [ ] Rate limiting guard — NOT DONE
- Success: fingerprint dedup; HMAC; rate limiting

### T6.5 Fill plane_project_id mappings
- [ ] All mapped repos have real UUIDs — NOT DONE
- [ ] Sync no longer no-ops — NOT DONE
- Success: all mapped repos have UUIDs; sync produces real items

---

## EPIC E7 — Vercel Deployment Determinism + Drift Elimination

### T7.1 Fix production override drift
- [x] apps/ops-console/vercel.json — project config exists
- [x] vercel.json — root config exists
- [x] docs/ops/VERCEL_PRODUCTION_CHECKLIST_SSOT.md — checklist exists
- [-] docs/process/runbooks/vercel.md — has TODOs: secrets, apply, verification commands incomplete
- [ ] Codified project settings with apply script — NOT DONE
- [ ] Drift-check CI — NOT DONE
- Success: project settings codified in SSOT; drift-checked in CI

### T7.2 Pin Node version deterministically
- [-] Node version partially present in configs
- [ ] No "override" warnings; builds reproducible — NOT VERIFIED
- Success: Node version stable; no override warnings

### T7.3 Repo-first cron definitions
- [ ] Cron jobs declared in vercel.json — NOT DONE
- [ ] Remove UI-only cron — NOT DONE
- Success: cron declared in repo; survives redeploys

---

## EPIC E8 — GitHub Enterprise / PR Review Automation

### T8.1 Vercel Agent PR review + conflict guidance
- [ ] vercel_agent.yaml guidance — not found in repo
- [ ] .github/copilot-instructions.md — not found in repo
- Success: guidance codified; conflict resolution enforced

### T8.2 GitHub auth reliability for automation (gh 401 issues)
- [ ] CI-safe auth — NOT DONE
- [ ] PR creation/edit automation — NOT DONE (confirmed in this session)
- Why needed: gh CLI returns 401; API proxy only supports git protocol
- Success: CI-safe auth works; PR automation reliable

---

## EPIC E9 — DigitalOcean Cost/Footprint Optimization

### T9.1 Snapshot retention and cleanup policy
- [ ] Snapshot aging policy codified in SSOT — NOT DONE
- [ ] Cost reduction evidence — NOT DONE
- Ref: web/platform-kit/docs/infra/COST_OPTIMIZATION.md (exists but not DO-specific)
- Success: snapshots aged out; cost drops; policy codified

### T9.2 OCR droplet high disk/mem alerts remediation
- [ ] Alert rate reduced — NOT DONE
- [ ] Runbook executed via ops.runs with evidence — NOT DONE
- Success: alert rate reduced; runbook with evidence

---

## Summary: Completion Matrix

| Epic | Total Tasks | Shipped | Staged | Missing |
|------|-------------|---------|--------|---------|
| E1 — SoR/SSOT/SoW doctrine | 3 | 3 | 0 | 0 |
| E2 — SoW workspace | 3 | 2 | 1 | 0 |
| E3 — Slack agent | 2 | 1 | 1 | 0 |
| E4 — Advisor engine | 4 | 3 | 0 | 1 |
| E5 — M365 Copilot | 3 | 2 | 0 | 1 |
| E6 — Plane marketplace | 5 | 2 | 0 | 3 |
| E7 — Vercel determinism | 3 | 0 | 2 | 1 |
| E8 — GitHub Enterprise | 2 | 0 | 0 | 2 |
| E9 — DO cost optimization | 2 | 0 | 0 | 2 |
| **TOTAL** | **27** | **13** | **4** | **10** |

---

## Missing / Should Have Been Planned

These tasks were identified during audit as needed but not in any existing spec:

1. **T4.4 Vercel deployment health scan** — no scan edge function for Vercel
2. **T5.3 M365 identity mapping** — no identity mapping between M365 and Supabase
3. **T6.5 Plane project UUID mapping** — sync no-ops without real UUIDs
4. **T8.2 GitHub auth reliability** — gh CLI 401s block all PR automation
5. **T9.1 DO snapshot retention** — cost accumulates without cleanup policy
6. **E7 (all)** — Vercel deployment determinism has no dedicated spec bundle
7. **E8.1** — vercel_agent.yaml and copilot-instructions.md not found in repo
8. **CI gate for UI-only config** — T1.3 policy exists but no CI enforcement

### Recommended Priority (unblock order)

1. **T8.2 GitHub auth** — blocks all PR automation (platform-wide impact)
2. **T7.1 Vercel drift** — production overrides are actively divergent
3. **T4.4 Vercel health scan** — no observability on deployment failures
4. **T6.5 Plane UUID mapping** — sync is a no-op without this
5. **T5.3 M365 identity** — auth hardening for interaction plane
