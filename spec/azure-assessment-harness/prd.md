# PRD — Azure Assessment Harness

## Objective

Build a repo-first, local-agent-compatible creator/judge assessment system that gathers evidence, drafts conservative answers, scores with role-based judges, flags confidence and missing proof, and supports later comparison against official Microsoft assessment results.

## Why this matters

The IPAI platform has a 2.7/5.0 internal assessment (R3, 2026-04-05) with 5 open hard blockers. The internal review is evidence-grounded but self-calibrated — there is no external benchmark validation. Running the official Microsoft assessment requires accurate, conservative answers informed by actual platform state. This harness ensures those answers are prepared systematically rather than ad hoc.

## Architecture: Creator Swarm + Judge Swarm

### Creator swarm (produces the answer set)

| Agent | Role |
|---|---|
| Assessment Mapper | Maps internal artifacts to Microsoft assessment families and question types |
| Evidence Harvester | Pulls from IPAI_PLATFORM_ANALYSIS.md, SSOT, IaC, live inventory, docs |
| Answer Drafter | Produces conservative draft answers per assessment family |
| Gap Extractor | Flags present vs governed vs proven gaps |

### Judge swarm (scores and challenges)

| Judge | Scores |
|---|---|
| Reliability Judge | reliability, recovery, resilience |
| Security Judge | security, identity, governance |
| Cost / FinOps Judge | cost, finops |
| Operations Judge | operational_excellence, automation, runbooks |
| Performance Judge | performance, scale, topology |
| Drift Judge | iac_alignment, inventory_governance, exception_management |
| Calibration Judge | microsoft_alignment, answer_safety, confidence |

### Synthesis judge

One final judge produces: weighted score, confidence band, evidence quality rating, answer-safe/answer-risky flags, and recommended next actions.

## Assessment families covered

| Family | Internal module | Microsoft equivalent |
|---|---|---|
| WAF | `waf` | Azure Well-Architected Review |
| DevOps | `devops` | DevOps Capability Assessment |
| FinOps | `finops` | FinOps Review |
| Platform Engineering | `platform_engineering` | Platform Engineering Technical Assessment |
| Go-Live | `go_live` | Go-Live Well-Architected Review |
| GenAIOps | `genaiops` | GenAIOps Maturity Model Assessment |
| SaaS Journey | `saas_journey` | SaaS Journey Review |

## Persona pack

| Persona | Benchmark Role | Domains |
|---|---|---|
| WAF Solutions Architect | AZ-305 | reliability, performance, architecture, topology |
| Platform Operator | AZ-104 | operations, runtime, inventory, recovery |
| Security / Identity Reviewer | AZ-500 | security, identity, secrets, exposure |
| DevOps / Delivery Reviewer | AZ-400 | pipeline, release, traceability, governance |
| AI Platform Reviewer | AI-102 | ai_runtime, model_access, grounding, safety |
| Data Intelligence Reviewer | DP-600 | lakehouse, governance, ingestion, semantic_bi |
| Workload Ops Specialist | AZ-120 | workload_operating_model, workload_monitoring, ha_dr |

## Scoring rubric

| Score | Meaning | Evidence class |
|---|---|---|
| 0 | Absent | — |
| 1 | Ad hoc | Informal or undocumented |
| 2 | Present | Control/resource exists |
| 3 | Present + partly governed | Source-controlled or policy-backed |
| 4 | Governed and mostly proven | Tested or operationally validated |
| 5 | Governed, proven, and repeatable | Automated validation, drift detection |

## Success metrics

- All 7 assessment families have draft answer packs
- Every answer cites at least one evidence artifact
- Judge scores distinguish present/governed/proven
- Calibration judge flags answer-risky postures
- After official assessment, delta between internal and official is measurable

## Affected repos

- agents (personas, judges, skills)
- ssot/assessment (mapping, rubric)
- docs/evidence/assessments (runbook, results)

## Acceptance conditions

- Creator agents can produce a full answer pack from existing artifacts
- Judge agents can score and challenge the answer pack
- Calibration judge can flag confidence and answer safety
- Comparison template exists for post-official-assessment reconciliation
