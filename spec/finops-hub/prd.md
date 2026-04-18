# FinOps Hub -- PRD

> Product requirements for the InsightPulseAI FinOps observability plane.

---

## Problem

- **63 Azure resources** run on Microsoft Azure Sponsorship (sub `eba824fb`).
- No central cost dashboard. Today sponsorship burn-rate is only visible by
  manually paging through Cost Management UI.
- No per-tenant (Pulser / W9 Studio / Prismalab) cost allocation.
- Pulser finance copilot has no grounded answer to "what did we spend on
  \<tenant\> this month?".
- Pre-production overruns on idle resources (e.g. failed ACA `ipai-w9studio-dev`,
  orphan `w9studio-landing-dev` in `rg-ipai-dev-odoo-runtime`) go unnoticed.

## Users

| Persona | Need |
|---|---|
| Platform eng (Jake) | Burn-rate dashboard + alert on sponsorship cap approach |
| Finance operator (accounts@w9studio.net, IPAI finance) | Per-tenant monthly cost report |
| Pulser finance copilot | Grounded FOCUS-schema cost data for NL Q&A |
| CSO / compliance | Audit trail of cost export access + retention |

## Functional Requirements

1. **Cost export** — Azure Cost Management exports daily to `stdevipai/finops/` in FOCUS format.
2. **Hub ingest** — FinOps Toolkit Hub normalizes + stores in lake partitioned by date+scope.
3. **Power BI** — Upstream starter reports deployed to `wks-ipai-finops` Power BI workspace, bound to hub dataset.
4. **Tag allocation** — All 63 resources carry `tenant` and `cost_center` tags (gap-fill in Phase 1).
5. **Alerts** — Budget threshold alert (80%, 95%, 100%) via Action Group `ag-ipai-dev-sea`.
6. **Idle detection** — Flag ACA apps in `Failed` state or zero-traffic for 14 days.
7. **Fabric mirror** — Lake cost tables mirrored to OneLake via existing Unity Catalog mirror.
8. **Pulser knowledge binding** — FOCUS tables registered as MCP Knowledge source for finance copilot grounding.

## Non-Functional Requirements

- **Freshness**: Dashboard ≤ 24h stale
- **Alerts**: ≤ 4h from threshold breach
- **Security**: Managed-identity-only; no secrets in repo
- **Cost**: Hub itself runs ≤ $50/month (small hub SKU)
- **Retention**: 13 months hot, then lifecycle-managed cold

## Out of Scope (Scope Zero)

- Multi-cloud (AWS/GCP) — phase 3
- Non-Azure licensing (M365, GitHub) — phase 2
- Custom optimization recommendations beyond upstream — phase 2
- Replacement of Odoo finance — never

## Dependencies

- `kv-ipai-dev-sea` — hub identity secrets (if any)
- `stdevipai` + `stipaidevlake` — storage targets
- `dbw-ipai-dev` + Unity Catalog — lake engineering
- Azure Pipelines — deploy authority
- Tag governance rollout (prerequisite for allocation)

## Acceptance

- Hub deployed into `rg-ipai-dev-mon-sea` via Azure Pipelines
- FOCUS data visible in `wks-ipai-finops` within 48h of first export
- Power BI report rendering per-RG spend for the last 30 days
- Pulser answers "how much did `ipai-odoo-dev` cost last week?" within tolerance of the Cost Management ground truth
