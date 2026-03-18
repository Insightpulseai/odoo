# Examples — product-portfolio-judge

## Example 1: Clean alignment — quarterly review

**Input**:
- Product-manager output: 8 validated spec bundles for Q1-2026
- Portfolio-manager output: 3 platform OKRs with 8 linked work items
- Milestone timeline: P1 MVP ERP (March 2026)

**Output**:
- Review period: Q1-2026
- Alignment summary: 8 matched, 0 orphan specs, 0 unfunded goals, 0 conflicts
- Orphan specs: none
- Unfunded goals: none
- Priority conflicts: none
- Timeline feasibility: FEASIBLE (all spec delivery dates before milestone)
- Stale items: none
- Recommended actions: none — alignment is clean
- Evidence: `docs/evidence/20260331-1600/alignment/Q1-2026/`

## Example 2: Drift detected — pre-release gate

**Input**:
- Product-manager output: 12 validated spec bundles
- Portfolio-manager output: 3 platform OKRs, 2 orphan work items flagged
- Milestone timeline: P1 MVP ERP gate check

**Output**:
- Review period: P1-2026 pre-release
- Alignment summary: 9 matched, 2 orphan specs, 1 unfunded goal, 1 conflict
- Orphan specs:
  - `spec/slack-bot-v2/` — parent OKR "Mattermost integration" was retired (Mattermost deprecated)
  - `spec/vercel-edge-caching/` — Vercel is deprecated, no current goal references it
- Unfunded goals:
  - "Azure Front Door WAF hardening" — no spec bundle exists, goal was added in mid-quarter amendment
- Priority conflicts:
  - `spec/ee-parity-helpdesk/` marked P1 (critical) but parent goal "EE parity 80%" is P2 (high) — inconsistent
- Timeline feasibility: AT_RISK
  - `spec/bir-tax-compliance-v2/` delivery date March 28 but milestone gate is March 25
- Stale items:
  - `spec/marketplace-integrations/` — last activity 2026-02-10 (35 days)
- Recommended actions:
  1. Archive `spec/slack-bot-v2/` or reparent to current Slack OKR
  2. Archive `spec/vercel-edge-caching/` (deprecated platform)
  3. Create spec bundle for "Azure Front Door WAF hardening" or defer goal to Q2
  4. Resolve priority conflict: either elevate parent goal to P1 or downgrade helpdesk spec to P2
  5. Accelerate BIR tax compliance or negotiate 3-day milestone extension
  6. Review stale marketplace-integrations spec — continue, defer, or archive
- Evidence: `docs/evidence/20260325-0900/alignment/P1-gate/`

## Example 3: Missing upstream input — error case

**Input**:
- Product-manager output: 5 validated spec bundles
- Portfolio-manager output: NOT PROVIDED

**Output**:
- ERROR: Cannot produce alignment report without portfolio-manager output
- Required input missing: validated goal hierarchy and capacity plan
- Action: Run portfolio-manager skill first, then re-invoke product-portfolio-judge
- No partial report generated (per guardrail: never run in isolation without upstream outputs)
