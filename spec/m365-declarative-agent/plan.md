# M365 Declarative Agent -- Implementation Plan

> Wave 2 -- starts in parallel with Wave 1 hardening, publishes Q4 2026.

---

## Phase A: Entra Agent ID Registration (BLOCKING, due 2026-05-01)

**Goal:** Register both declarative agents in Entra Agent ID before hard
Microsoft deadline.

- Create per-agent managed identities in `rg-ipai-dev-security-sea`
- Register in Entra admin center as agent identities
- Apply scoped permissions (read-only on Pulser API; no direct Odoo scope)
- Dual-register in TBWA tenant as custom catalog entry for design-partner
  access
- Update `agents/pulser-surface/appPackage/manifest.json` with Agent IDs

**Exit:** Both agents visible in Entra Agent ID console; identity tokens
validated against Pulser API.

## Phase B: API Plugin Hardening (parallel with Wave 1 build, Apr-Jun 2026)

**Goal:** `ai-plugin.json` operations cover Wave 1 user journeys.

- Finalize OpenAPI spec for Pulser API endpoints consumed by the agent
- OAuth 2.0 auth flow with delegated permissions
- Rate limiting per tenant (avoid runaway agent loops)
- Telemetry: every invocation logs correlation ID to App Insights
- Content Safety filter on all agent-bound responses
- Smoke-test suite for top 20 user journeys

**Exit:** `curl` test harness passes for all operations in
`ai-plugin.json`; Foundry eval pass rate >= 90%.

## Phase C: Agent Content + UX (May-Jul 2026)

**Goal:** Both declarative agents produce high-quality grounded responses.

- Instructions file tuning per agent (P2P + R2R)
- Adaptive Card schemas for top responses (invoice summary, project P&L, AP
  aging, R2R dashboard)
- Link-back pattern: every mutating intent returns a deep-link to Pulser
  SaaS pre-filled action
- Accessibility pass (WCAG AA on cards)
- Localization framework (EN primary; PH-Filipino deferred to Wave 3)

**Exit:** Design-partner tenant uses both agents in Copilot Chat with
positive feedback on 20 real user journeys.

## Phase D: Sideloaded Pilot in Design-Partner Tenants (Jul-Aug 2026)

**Goal:** Battle-test agent in real tenants before M365 Agent Store cert.

- Sideload app package into IPAI tenant
- Sideload into 2 design-partner tenants (e.g., TBWA\\SMP, W9 Studio)
- Collect usage telemetry for 4-6 weeks
- Iterate on failure modes discovered

**Exit:** 60 days of clean usage data across 3+ tenants; no critical
failures.

## Phase E: M365 Agent Store Submission (Sep-Oct 2026)

**Goal:** Publish to the public M365 Agent Store so any tenant can discover.

- Prepare app package per Microsoft M365 cert requirements
- Submit to M365 Agent Store through Partner Center
- Cert takes 2-4 weeks; iterate on feedback
- Parallel path: publish listing on Microsoft Commercial Marketplace as a
  companion app to the Pulser SaaS offer

**Exit:** Both agents live in M365 Agent Store; linked from Pulser SaaS
listing; Pulser SaaS listing references the agent.

## Phase F: Launch + Attach (Q4 2026 / Q1 2027)

**Goal:** Drive adoption across Wave 1 SaaS customer base.

- Announce M365 agent availability to all Pulser SaaS customers
- "Install in Teams" button added to Pulser SaaS dashboard
- Webinar demonstrating cross-surface flow (Teams -> SaaS)
- Co-marketing push with Microsoft APAC via Marketplace Rewards
- Track attach rate metric for App Accelerate nomination

**Exit:** 50% of Wave 1 customers have installed at least one declarative
agent; attach rate visible in Partner Center insights.

---

## Timeline (calendar)

```
2026-04  Phase A Entra Agent ID (deadline 2026-05-01)
2026-05  Phase B API plugin hardening + Phase C content (parallel)
2026-06  Phase B + C continuation
2026-07  Phase C + Phase D sideloaded pilot
2026-08  Phase D pilot + Wave 1 SaaS publish
2026-09  Phase D pilot + Wave 1 GA
2026-10  Phase E Agent Store submission + cert
2026-11  Phase E cert + Phase F launch prep
2026-12  Phase F launch and attach push
2027-Q1  Phase F measurement and iterate
```

---

## Dependencies

- Wave 1 Pulser SaaS published (hard)
- Pulser API stable (hard)
- Foundry `ipai-copilot-resource` with Content Safety enabled (hard)
- ISV Success profile in Partner Center for Agent Store submission (soft)
- Design-partner tenants willing to sideload (soft)
