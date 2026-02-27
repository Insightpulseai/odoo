# Tasks: ERP SaaS Parity Plus

## Current Objective

Formalize the SSOT documentation artifacts that govern the 7 Layers of Parity.

- [ ] `docs/parity/ERP_SAAS_PARITY_MATRIX.md`
- [ ] `docs/architecture/TENANCY_MODEL.md`
- [ ] `docs/ops/OBSERVABILITY.md`
- [ ] `docs/ops/RELEASE_TRAIN.md`
- [ ] `docs/ops/RUNBOOKS/finance-close.md`
- [ ] `docs/ops/RUNBOOKS/incident-dead-jobs.md`
- [ ] `docs/ops/RUNBOOKS/incident-auth.md`
- [ ] `docs/product/BILLING_ENTITLEMENTS.md`
- [ ] `docs/plus/AGENTIC_OPS.md`

## Integration Enforcement

- [x] Create Supabase integration schema `ops.*`.
- [x] Create Atomic Claim RPC.
- [x] Configure pg_cron & tick Edge Function.

## IDC FutureScape & MIT Readiness Epics

- [ ] Epic: KPI Baseline & AI KPI Schema (pre/post, in-loop vs autonomous).
- [ ] Epic: Composable ERP Strangler Milestones (domain extraction plan).
- [ ] Epic: Compliance Exchange Adapter Layer (regional plugins, evidence logs).
- [ ] Epic: Data Liquidity Layer (canonical IDs, curated access surfaces, cross-domain joins).
- [ ] Epic: Lineage + Metadata for AI (track dataset provenance and doc metadata extraction).
- [ ] Epic: ROI/KPI Instrumentation (baseline, A/B workflow runs, KPI deltas).

## UI / Analytics

- [ ] Build Next.js Ops Console dashboard charting `/health` metrics.
- [ ] Wire Slack app to ping `#alerts` when `dead_jobs > 0`.
