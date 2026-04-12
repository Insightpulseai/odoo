# Platform Readiness Scorecard

## Current baseline (2026-04-13)

| Framework | Current Score | Current Level | Primary blocker |
|---|---:|---|---|
| GenAIOps Maturity | 15/28 | L2 Defined | AI eval coverage / index operationalization |
| Azure Well-Architected Review | 57/100 | C | Cost optimization (42%) |
| Azure WAF SaaS Workload | 49/100 | D+ | Cost (38%) + commercialization readiness |

## FinOps judge flags
- Cost Optimization: 42% — **FAIL** (threshold 65%)
- Commercialization: 38% — **FAIL** (threshold 65%)

## This week's blocking actions
1. Resolve Fabric vs Databricks decision (ADR-001)
2. Add break-glass Entra identity path
3. Burn down 10 critical Dependabot findings

## This month's evidence actions
1. Define SLOs (docs/sre/slo.md)
2. Prove canary rollout with ACA revision labels
3. Populate AI Search index (`srch-ipai-dev`)
4. Run evals across all 12 active agents

## Exit criteria for next review
- WAF Review >= 65
- WAF SaaS >= 56
- GenAIOps >= 16
- All P0 blockers have evidence links
- FinOps judge passes (>= 65%)

## Evidence links
- [GenAIOps Maturity](../evidence/20260413-0100/assessments/01-genaiops-maturity-assessment.md)
- [Azure WAF Review](../evidence/20260413-0100/assessments/02-azure-waf-review.md)
- [WAF SaaS Workload](../evidence/20260413-0100/assessments/03-waf-saas-workload.md)
- [Judge evaluations](../evidence/20260412-2000/judge-evaluations/session-evaluation.md)
