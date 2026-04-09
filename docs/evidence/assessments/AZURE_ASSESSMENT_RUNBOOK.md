# Azure Assessment Harness — Runbook

> Internal preparation and calibration workflow for Microsoft Assessments.
> This harness does NOT replace the official Microsoft Assessments portal.

---

## Prerequisites

- Access to `docs/architecture/IPAI_PLATFORM_ANALYSIS.md` (current: R3)
- Access to `ssot/azure/`, `ssot/assessment/`, `ssot/governance/`
- Access to `infra/azure/modules/` (Bicep state)
- Azure CLI authenticated (`az account show`)
- Azure Boards backlog loaded (`docs/planning/IPAI_AZURE_BOARDS_BACKLOG.md`)

---

## Stage 1 — Evidence Gathering

### 1.1 Run Evidence Harvester

For each assessment family (waf, devops, finops, platform_engineering, go_live, genaiops, saas_journey):

1. Load domain list from `ssot/assessment/microsoft_assessments_map.yaml`
2. Gather evidence from repo artifacts, SSOT, IaC, and runtime state
3. Classify each evidence item as: present / governed / proven
4. Flag gaps where evidence is missing or stale (>30 days)
5. Output: evidence pack per family

### 1.2 Validate evidence freshness

- Platform analysis last updated: check `IPAI_PLATFORM_ANALYSIS.md` header
- Resource reconciliation: check `ssot/azure/RESOURCE_RECONCILIATION_REPORT.md` date
- Live inventory: run `az resource list -o table` if stale

---

## Stage 2 — Answer Drafting

### 2.1 Assign personas

Route each assessment family to the assigned persona per `ssot/assessment/persona_role_map.yaml`:

| Family | Primary Persona | Backup |
|---|---|---|
| waf | waf_solutions_architect | platform_operator |
| devops | devops_delivery_reviewer | — |
| finops | cost_judge (direct) | — |
| platform_engineering | devops_delivery_reviewer | waf_solutions_architect |
| go_live | platform_operator | workload_ops_specialist |
| genaiops | ai_platform_reviewer | — |
| saas_journey | workload_ops_specialist | — |

### 2.2 Draft answers

For each question area in the family:
1. Cite evidence from the harvested pack
2. Score 0-5 per `ssot/assessment/scoring_rubric.yaml`
3. Flag answer_safe / answer_risky per evidence class
4. List missing proof that would strengthen the answer

---

## Stage 3 — Judge Review

### 3.1 Run domain judges

Each judge reviews answers in its assigned domains:
- Reliability Judge → reliability, recovery, resilience
- Security Judge → security, identity, governance
- Cost Judge → cost, finops
- Operations Judge → operational_excellence, automation, runbooks
- Performance Judge → performance, scale, topology
- Drift Judge → iac_alignment, inventory_governance, exception_management

### 3.2 Run workload overlay judges

- AI Workload Judge → ai_workload_fit, grounding_quality, ai_eval_and_safety
- SaaS Workload Judge → saas_operating_model, service_boundaries, scale_model
- SAP Workload Ops Judge → workload_center_maturity, operational_visibility, dr_rigor
- Architecture Pattern Judge → reference_pattern_alignment, topology_completeness

### 3.3 Run Calibration Judge

- Compare internal scores against expected Microsoft scoring style
- Flag over-claiming (internal > expected official)
- Produce recommended portal answer posture (conservative / moderate / confident)

---

## Stage 4 — Synthesis

Produce:
1. **Internal scorecard** — weighted score per family and pillar
2. **Official portal answer guide** — recommended answers for the Microsoft portal
3. **Delta vs R3** — what changed since the last internal assessment
4. **Blocker / recommendation split** — which gaps are hard blockers vs improvements

Save outputs to `docs/evidence/assessments/`.

---

## Stage 5 — Run Official Assessment

1. Go to `https://learn.microsoft.com/assessments/azure-architecture-review/`
2. Register with Microsoft account
3. Answer using the portal answer guide from Stage 4
4. Export results to CSV
5. Save CSV to `docs/evidence/assessments/AZURE_ASSESSMENT_COMPARISON.csv`

---

## Stage 6 — Calibrate

1. Load official CSV and internal scorecard
2. Compute delta per pillar
3. Classify: over-claim / under-claim / aligned
4. Update confidence thresholds in `ssot/assessment/scoring_rubric.yaml`
5. Document lessons in `docs/evidence/assessments/CALIBRATION_NOTES.md`

---

## Official WAF Alignment Model

The internal assessment harness uses a three-layer scoring model:

1. **Layer A — WAF Core pass** (weight: 0.60)
   Score the five WAF pillars:
   - Reliability
   - Security
   - Cost Optimization
   - Operational Excellence
   - Performance Efficiency

2. **Layer B — Workload overlay pass** (weight: 0.20)
   Challenge the workload through the most relevant Azure workload lenses:
   - SaaS
   - AI
   - SAP
   - Mission-critical (only where justified)

3. **Layer C — Transformation readiness overlay** (weight: 0.20)
   Evaluate whether the organization can execute and sustain the transformation:
   - Discover — current-state visibility, inventory, SSOT discipline
   - Analyze — dependency mapping, bottleneck detection, business/IT alignment
   - Design — target-state clarity, scenario planning, roadmap quality
   - Implement — change management, enablement, execution alignment
   - Operate — continuous improvement, governance, KPI feedback, adaptation

No layer replaces another. Layer A scores cloud quality. Layer B scores workload fit.
Layer C scores organizational transformation capability.

**Final score** = (0.60 x Layer A) + (0.20 x Layer B) + (0.20 x Layer C)

## Transformation Readiness Overlay

In addition to WAF core scoring and workload overlays, the internal harness applies a
transformation-readiness overlay based on five phases: Discover, Analyze, Design,
Implement, Operate.

This overlay does not replace WAF. It evaluates whether the organization can:
- understand its current state (Discover)
- identify bottlenecks and dependencies (Analyze)
- define a realistic target state with sequenced roadmap (Design)
- implement change with alignment and enablement (Implement)
- sustain value through ongoing governance and adaptation (Operate)

Use this overlay especially when the dominant risks are:
- drift between intended and live state
- weak ownership or communication
- unclear roadmap dependencies
- poor post-go-live governance

### Transformation scoring dimensions

Each phase is scored on five dimensions:
1. **Visibility** — can you see what exists?
2. **Alignment** — do business and IT agree on priority and direction?
3. **Governance** — are decisions tracked, enforced, and auditable?
4. **Execution readiness** — can you actually do it with current capacity?
5. **Continuous feedback** — does output from this phase feed back into improvement?

### IPAI current posture (estimated)

| Phase | Posture | Notes |
|---|---|---|
| Discover | Relatively strong | Evidence inventory and architecture analysis habit |
| Analyze | Moderate | Dependency awareness exists but not machine-mapped |
| Design | Moderate | Spec bundles exist but coverage is partial |
| Implement | Mixed | Execution happens but variance tracking is weak |
| Operate | Weakest | Post-go-live governance and drift closure are the dominant gap |

Dominant risk: governance drift between intended state and runtime reality,
not absence of infrastructure.

## Pattern-corpus rule

External architecture centers and reference repositories are used as challenge corpora and pattern libraries, not as primary scoring authorities.

For SAP-oriented workload rigor, `SAP/architecture-center` may be used to challenge:
- operational model completeness
- integration topology
- recovery and enterprise pattern assumptions
- workload decomposition

For transformation lifecycle rigor, the SAP LeanIX/Signavio five-phase model is used
as the methodology reference for the transformation-readiness overlay.

## Azure Architecture Center benchmark usage

Azure Architecture Center research is used as a benchmark corpus for:

- reference architecture alignment
- container platform selection
- AI agent orchestration pattern fit
- landing-zone and workload-boundary discipline
- analytics architecture pattern fit

It is not a scoring authority by itself.

### Agent orchestration rule

Default to a single-agent pattern first.
Escalate to multi-agent patterns only when justified by:

- decomposition needs
- concurrency needs
- handoff requirements
- shared-context collaboration needs

High-impact workflows must define HITL gates explicitly.

### Current AAC-aligned implications for IPAI

- Azure Container Apps remains the preferred runtime over AKS for the current workload profile
- Databricks + Fabric remains the preferred analytics split
- workload-team vs platform-team separation should remain explicit
- WAF MCP guidance can be used as a supplemental evidence input

## SAP on Azure operating-model taxonomy usage

SAP on Azure offering categories are used to structure the Odoo-on-Azure workload documentation families:

- workload center
- deployment automation
- monitoring
- integrations
- backup and disaster recovery
- analytics and AI integration
- DevOps / IaC / governance

This taxonomy is used to improve completeness and comparability of the Odoo-on-Azure documentation set.
It mirrors the operational family structure Microsoft exposes for SAP on Azure, including Azure Center for
SAP solutions, deployment automation, Azure Monitor for SAP solutions, integrations with Microsoft services,
backup and site recovery, analytics services, Azure DevOps, IaC, and Azure Policy.

---

*Created: 2026-04-05 | Version: 2.0*
