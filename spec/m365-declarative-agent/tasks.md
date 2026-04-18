# M365 Declarative Agent -- Tasks

Legend: `[ ]` = not done · `[~]` = in progress · `[x]` = done + verified

---

## Phase A -- Entra Agent ID (due 2026-05-01, hard deadline)

- [ ] A.1 Create MI `id-ipai-agent-pulser-p2p` in `rg-ipai-dev-security-sea`
- [ ] A.2 Create MI `id-ipai-agent-pulser-r2r` in `rg-ipai-dev-security-sea`
- [ ] A.3 Register both in Entra Agent ID console
- [ ] A.4 Define scoped permission manifest per agent (read-only on Pulser API)
- [ ] A.5 Dual-register in TBWA tenant as custom catalog entry
- [ ] A.6 Wire Agent IDs into `agents/pulser-surface/appPackage/manifest.json`
- [ ] A.7 Smoke test: each agent token validates against Pulser API

## Phase B -- API Plugin Hardening

- [ ] B.1 Finalize OpenAPI spec for Pulser API endpoints (source for `ai-plugin.json`)
- [ ] B.2 OAuth 2.0 delegated-permission auth flow
- [ ] B.3 Rate limiter per tenant (50 req/min default; configurable via Pulser admin)
- [ ] B.4 App Insights correlation ID logging on every invocation
- [ ] B.5 Content Safety filter on all agent-bound responses
- [ ] B.6 Smoke-test suite: top 20 user journeys pass

## Phase C -- Agent Content + UX

### C.1 `pulser-project-to-profit`
- [ ] C.1.1 Tune instructions for Odoo project + finance scope
- [ ] C.1.2 Adaptive Card: project P&L summary
- [ ] C.1.3 Adaptive Card: outstanding AR/AP by project
- [ ] C.1.4 Deep-link schema: invoice approval -> Pulser SaaS action URL
- [ ] C.1.5 20 sample prompts with ground-truth answers for eval

### C.2 `pulser-record-to-report`
- [ ] C.2.1 Tune instructions for month-end close + R2R scope
- [ ] C.2.2 Adaptive Card: close checklist status
- [ ] C.2.3 Adaptive Card: aging summary
- [ ] C.2.4 Deep-link schema: approval queue -> Pulser SaaS action URL
- [ ] C.2.5 20 sample prompts with ground-truth answers for eval

### C.3 Cross-cutting
- [ ] C.3.1 Accessibility: WCAG AA pass on all Adaptive Cards
- [ ] C.3.2 Localization framework (EN primary; hooks for PH-Filipino Wave 3)
- [ ] C.3.3 Error handling: graceful degrade when Pulser API unreachable
- [ ] C.3.4 Non-subscriber UX: prompt to sign up via marketplace listing

## Phase D -- Sideloaded Pilot (Jul-Aug 2026)

- [ ] D.1 Sideload into IPAI tenant (internal dogfood)
- [ ] D.2 Sideload into TBWA\\SMP tenant (design partner 1)
- [ ] D.3 Sideload into W9 Studio tenant (design partner 2, contingent on GWS-M365 bridging)
- [ ] D.4 4-6 weeks of usage telemetry collection
- [ ] D.5 Iterate on top 3 failure modes
- [ ] D.6 Validation report with metrics committed to `docs/evidence/`

## Phase E -- M365 Agent Store Submission (Sep-Oct 2026)

- [ ] E.1 Package app per M365 cert requirements (icons, privacy URL, terms URL — verify valid)
- [ ] E.2 Submit to M365 Agent Store via Partner Center
- [ ] E.3 Respond to cert feedback loop (1-3 rounds typical)
- [ ] E.4 Companion listing on Microsoft Commercial Marketplace (optional but recommended)
- [ ] E.5 Cross-link: SaaS listing -> Agent; Agent listing -> SaaS

## Phase F -- Launch + Attach (Q4 2026)

- [ ] F.1 Announce agent availability to all Wave 1 SaaS customers
- [ ] F.2 Pulser SaaS dashboard: "Install in Teams" button
- [ ] F.3 Launch webinar demonstrating cross-surface flow
- [ ] F.4 Marketplace Rewards co-marketing proposal with Microsoft APAC
- [ ] F.5 Attach rate dashboard (Partner Center Insights + Power BI workspace)
- [ ] F.6 Quarterly target: 50% attach rate by 2027-Q1

---

## Cross-cutting

- [ ] X.1 `agents/pulser-surface/appPackage/manifest.json` icons (`color.png`, `outline.png`) - verify exist
- [ ] X.2 Privacy and terms URLs in manifest resolve to live pages (`insightpulseai.com/privacy`, `/terms`)
- [ ] X.3 All manifest domains reachable from public internet
- [ ] X.4 Agent descriptions approved by a human (not LLM-generated without review)
- [ ] X.5 Each agent has a corresponding eval bundle under `agents/evals/`

---

## Dependencies

- Wave 1 spec: `spec/microsoft-marketplace-gtm/`
- Agent package files: `agents/pulser-surface/appPackage/`
- Identity: `id-ipai-agent-pulser-*` MIs (to be created)
- Foundry: `ipai-copilot-resource` with Content Safety
- API: Pulser API endpoints with OpenAPI spec stable

---

*Bootstrap 2026-04-18.*
