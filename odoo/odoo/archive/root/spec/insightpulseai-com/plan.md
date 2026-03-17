# Plan — insightpulseai.com

## Phase 0 — Inventory + SSOT wiring (DONE)

- [x] Identify current canonical URLs and ensure `.com` only
- [x] Confirm SSOT locations:
  - `infra/dns/subdomain-registry.yaml` (DNS SSOT)
  - `infra/cloudflare/envs/prod/subdomains.auto.tfvars` (generated Terraform)
  - `docs/arch/runtime_identifiers.json` (generated runtime config)
  - `docs/architecture/CANONICAL_URLS.md` (human-readable reference)
- [x] Ensure docs reference SSOT, not the other way around
- [x] Fix stale `.net` + `ipa.insightpulseai.com` references (21 files)
- [x] Create `reports/url_inventory.json` (machine-readable with drift)

## Phase 1 — DNS IaC + redirect policy

- [x] Apex + www records defined in `subdomain-registry.yaml`
- [x] Redirect policy documented: `www` → 301 → apex
- [x] DNS sync check CI gate: `.github/workflows/dns-sync-check.yml`
- [ ] Verify Cloudflare page rule / redirect rule enforces www → apex

## Phase 2 — Health checks + reporting

- [x] `scripts/verify-service-health.sh` covers all prod + staging services
- [ ] Extend healthcheck to add marketing surface entries:
  - `insightpulseai.com` (apex) — HTTP 200, content signature
  - `www.insightpulseai.com` — HTTP 301 to apex
- [ ] Emit JSON + Markdown reports as CI artifacts
- [ ] Content signature check detects misrouting

## Phase 3 — `.net` regression gate

- [ ] Add `.github/workflows/domain-lint.yml`
  - Runs on all PRs
  - Greps for `.net` references in non-archive paths
  - Fails with helpful message listing offending files
- [ ] Test with intentional `.net` reference to verify gate

## Phase 4 — Observability + ops integration

- [ ] Token-gated Netdata/Sentry checks (skip when missing)
- [ ] Canonical URLs list published in docs and referenced by README
- [x] `docs/architecture/CANONICAL_URLS.md` created and linked from README

## Phase 5 — Hardening

- [ ] Regression tests for:
  - `.net` leakage (grep gate in CI)
  - Redirect regressions (www → apex)
  - Misrouting signature failures
- [ ] Scheduled healthcheck run (cron workflow, optional)
- [ ] Alert routing to Slack (optional)

## AI Marketing Canvas Roadmap (12 months)

Source: AI Marketing Canvas (PDF)

### Phase 0 (Weeks 0–2): Baseline + Operating System

**Outcomes:** Measurable before/after impact and safe deployment.
**Deliverables:**

- AI Program Charter (scope, north-star metrics, risk policy, ownership)
- KPI Baseline (conversion rates, CAC, LTV, churn, time-to-launch campaign, content throughput)
- Data inventory + "source of truth" map (Odoo vs Supabase)
- Governance rails (data access model, audit logging, model release policy)
  **Exit Criteria:** 5–10 KPIs have baseline values + owners; system boundaries are explicit.
  **KPI Improvements:** Establish baseline.

### Phase 1 (Weeks 3–8): Foundation (Data + Identity + Consent)

**Outcomes:** Reliable "marketing-grade" customer and event data.
**Deliverables:**

- Customer identity resolution (dedupe + stable customer key)
- Consent & preferences (opt-in/out, suppression lists, policy enforcement)
- Event + campaign canonical schema (web/app/pos events, Touchpoints, outcomes)
- Data quality gates (completeness checks, drift checks)
  **Exit Criteria:** Single customer key works across CRM + transactions; consent enforced by default.
  **KPI Improvements:** 100% consent compliance; unified identity across systems.

### Phase 2 (Weeks 9–16): Experimentation (Segments + Playbooks + Measurement)

**Outcomes:** Faster experiments with measurable uplift.
**Deliverables:**

- Segment engine v1 (RFM/cohorts/behavioral segments)
- Experiment harness (treatment/control assignment, holdouts, hypothesis template)
- Marketing playbooks (winback, onboarding/nurture, high-intent lead follow-up)
- Reporting v1 (segment/channel/experiment performance)
  **Exit Criteria:** End-to-end A/B test with clean attribution; 1–2 playbooks produce measurable uplift.
  **KPI Improvements:** Increased campaign conversion rate; reduced time-to-launch.

### Phase 3 (Weeks 17–28): Expansion (Scoring + Next Best Action + Automation)

**Outcomes:** Scalable personalization with guardrails.
**Deliverables:**

- Scoring models v1 (propensity-to-buy, churn risk, lead priority)
- Next Best Action ruleset
- Activation connectors (Odoo Activities, tags, sequences)
- Ops dashboards (audience sizes, score distributions, action outcomes)
  **Exit Criteria:** Scores refresh reliably and produce actions; guardrails prevent fatigue.
  **KPI Improvements:** Lift in high-intent conversion; reduced churn risk.

### Phase 4 (Weeks 29–40): Transformation (Closed Loop + Autopilot + Content Ops)

**Outcomes:** System learns from outcomes and improves automatically.
**Deliverables:**

- Closed-loop learning (capture outcomes, feed back to scoring)
- Autopilot workflows (budget caps, frequency capping, human approval gates for risks)
- Content ops (creative brief generator, RAG over assets, performance recommendations)
  **Exit Criteria:** Actions traced end-to-end; system runs semi-autonomously with gates.
  **KPI Improvements:** Increased content throughput; higher campaign ROI via closed-loop tuning.

### Phase 5 (Weeks 41–52): Monetization (Productize + SLAs + Billing/Audit)

**Outcomes:** Repeatable product offering (internal or client-facing).
**Deliverables:**

- Packaging ("AI Marketing Canvas in a Box" templates)
- SLA + reliability (pipeline SLAs, incident playbook, freshness guarantees)
- Governed exports (client reporting packs, partner feeds)
- Usage-based accounting (audit of predictions/actions)
  **Exit Criteria:** Onboarding new brand/client is configurable; enterprise-grade reliability.
  **KPI Improvements:** New revenue streams; scalable client onboarding.
