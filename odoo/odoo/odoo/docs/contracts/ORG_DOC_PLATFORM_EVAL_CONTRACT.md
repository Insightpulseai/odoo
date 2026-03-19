# Org Doc Platform Capability Eval Contract

> Defines the maturity rubric, scoring domains, evidence requirements,
> and blocking-gap rules for the org-wide documentation platform.
>
> SSOT: `agents/evals/org_doc_platform_target_capabilities.yaml`
> Scorer: `agents/evals/score_org_doc_platform.py`
> Artifacts: `artifacts/evals/org_doc_platform_eval.{json,md}`

---

## Maturity Scale (0-4)

| Level | Label | Definition |
|-------|-------|------------|
| 0 | Missing | No implementation exists. No code, no config, no evidence. |
| 1 | Scaffolded | Schema/stub/placeholder exists but is not functional. Field defined but unused. |
| 2 | Partial | Code exists and runs in isolation. Not integrated end-to-end. Not validated with real data. |
| 3 | Operational | Works end-to-end in dev/staging. Evidence of successful execution exists. |
| 4 | Target | Production-grade. Monitored, tested, documented, repeatable. |

---

## Scoring Domains (9 domains, weights sum to 1.00)

### 1. Source Coverage (weight: 0.15)

Are all important documentation sources discovered, inventoried, and indexed?

| Level | Criteria |
|-------|----------|
| 0 | No source inventory exists |
| 1 | Source inventory file exists but is incomplete or has no loader |
| 2 | Loaders exist for major source types; inventory tracks >50% of known sources |
| 3 | All major sources indexed; source_inventory.yaml is maintained and accurate |
| 4 | Automated discovery detects new sources; coverage report generated on each refresh |

### 2. Freshness and Lifecycle (weight: 0.10)

Are docs current? Is staleness tracked and acted upon?

| Level | Criteria |
|-------|----------|
| 0 | No freshness tracking |
| 1 | Freshness field exists in schema but is not populated or checked |
| 2 | Git-based timestamps populate freshness; no automation flags stale docs |
| 3 | Stale docs auto-flagged (>90 days); refresh workflow runs on schedule |
| 4 | Freshness dashboard; stale docs trigger owner notifications; lifecycle policy enforced |

### 3. Retrieval Quality (weight: 0.20)

Do searches return relevant, high-quality results?

| Level | Criteria |
|-------|----------|
| 0 | No search capability |
| 1 | Search endpoint exists but index is empty or not populated with org docs |
| 2 | Index populated; basic semantic search works; no eval queries validated |
| 3 | Eval queries return relevant results; filtered search works; recall >70% on eval set |
| 4 | Eval suite runs in CI; precision/recall tracked; query rewriting improves results |

### 4. Grounding/Citation Quality (weight: 0.15)

Are answers cited? Are citations accurate and verifiable?

| Level | Criteria |
|-------|----------|
| 0 | No citation mechanism |
| 1 | Citation schema defined but not enforced at query time |
| 2 | Citations returned with search results; accuracy not validated |
| 3 | Citation accuracy validated against eval queries; confidence bands working |
| 4 | Citation accuracy >90% on eval set; ambiguity detection proven; grounding contract enforced |

### 5. Access Control Readiness (weight: 0.05)

Is document sensitivity respected in search results?

| Level | Criteria |
|-------|----------|
| 0 | No access control mechanism |
| 1 | Sensitivity field exists in schema |
| 2 | Sensitivity classification populated for indexed docs |
| 3 | Search filters by sensitivity at query time; role mapping defined |
| 4 | Role-based filtering enforced; audit trail for sensitive doc access |

### 6. Search UX Quality (weight: 0.10)

Are filters, facets, and confidence bands working for end users?

| Level | Criteria |
|-------|----------|
| 0 | No search UX |
| 1 | Basic search endpoint returns raw results |
| 2 | Doc-type filtering works; results include metadata |
| 3 | Faceted search (source, type, freshness); confidence bands displayed |
| 4 | Source browsing; freshness reporting; user feedback loop |

### 7. Deployment Repeatability (weight: 0.10)

Can we rebuild and redeploy the platform deterministically?

| Level | Criteria |
|-------|----------|
| 0 | No container image or deployment config |
| 1 | Dockerfile exists but is untested |
| 2 | Image builds; deployment config exists; not tested end-to-end |
| 3 | CI publishes image; ACA deployment works; health check passes |
| 4 | Rollback mechanism; blue-green or canary; deployment takes <10 min |

### 8. Observability and Operations (weight: 0.10)

Are there health checks, logs, metrics, and alerting?

| Level | Criteria |
|-------|----------|
| 0 | No observability |
| 1 | Basic Python logging; no structured output |
| 2 | Health endpoint exists; request logging present |
| 3 | Structured logs; health endpoint monitored; error alerting |
| 4 | Metrics dashboard; tracing; SLO defined and tracked |

### 9. Governance and Ownership (weight: 0.05)

Is there a clear operating model for the documentation platform?

| Level | Criteria |
|-------|----------|
| 0 | No governance docs |
| 1 | Owner field in schema; no operating model |
| 2 | Operating model and admission policy drafted |
| 3 | Operating model enforced; eval cadence followed; runbook exists |
| 4 | Doc ownership enforced via CI; deprecation automation; quarterly reviews |

---

## Blocking-Gap Rules

A capability marked `release_blocker: true` blocks production release if `current < 3`.

The following capabilities are release blockers:
- `semantic_search` (retrieval domain) -- platform is useless without working search
- `citation_schema` (grounding domain) -- answers without citations are untrustworthy
- `container_image` (deployment domain) -- cannot deploy without a working image
- `health_endpoint` (observability domain) -- cannot operate without health checks
- `operating_model` (governance domain) -- cannot hand off without governance

---

## Evidence Requirements

Each capability score must cite at least one evidence item:

| Level | Evidence Required |
|-------|-------------------|
| 0 | None (absence is the evidence) |
| 1 | File path showing schema/stub/placeholder |
| 2 | File path + description of what works in isolation |
| 3 | File path + execution log or test output showing end-to-end success |
| 4 | File path + CI/monitoring proof + production health check |

Evidence is stored in `docs/evidence/<YYYYMMDD-HHMM>/org-docs-kb/`.

---

## Scoring Formula

```
domain_score = mean(capability_scores_in_domain) / 4.0
overall_score = sum(domain_score * domain_weight for all domains)
maturity_band:
  0.00-0.25 = missing
  0.25-0.50 = scaffolded
  0.50-0.75 = partial
  0.75-0.90 = operational
  0.90-1.00 = target
```

---

## Eval Cadence

- **Weekly**: Automated score calculation via `score_org_doc_platform.py`
- **Monthly**: Manual review of blockers and next-highest-value actions
- **Quarterly**: Full re-assessment with updated evidence

---

*Contract created: 2026-03-15*
*Owner: Platform Engineering*
