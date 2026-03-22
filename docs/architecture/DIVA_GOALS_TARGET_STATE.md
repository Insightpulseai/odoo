# Diva Goals -- Target State Architecture

> What Diva Goals is, why it exists, and how it relates to the existing platform.

---

## What is Diva Goals?

Diva Goals is an **AI-native goals and execution control plane** for the agentic DevOps SDLC. It is the orchestration and review layer that connects strategic objectives to delivery evidence and runtime outcomes.

It provides:

1. A **strategy-to-execution graph** that traces from goals through KRs, initiatives, specs, work items, agent runs, PRs, pipelines, eval gates, releases, and runtime metrics.
2. An **evidence engine** that ingests delivery and runtime data from source systems and computes derived status.
3. A **review engine** that provides structured review ceremonies (execution, portfolio, exception) with evidence-backed inputs and decision tracking.
4. An **agent participation model** that treats maker agents, judge agents, and ops agents as first-class graph entities with identity, confidence scoring, and approval workflows.

---

## Why It Exists

Traditional OKR and goal-tracking tools were designed for human-only organizations. They model goals as text fields, status as dropdowns, and progress as self-reported percentages. This breaks in an AI-first organization where:

- **Agents produce delivery artifacts** (code, specs, configs) and need to be modeled as participants, not invisible background processes.
- **Eval gates** determine release readiness based on automated scoring, not human checkbox completion.
- **Spec-driven delivery** means work is structured as spec bundles (constitution, PRD, plan, tasks), not flat task lists.
- **Runtime evidence** should close the loop on whether goals were actually achieved, not just whether tasks were marked done.
- **Confidence scoring** for agent outputs requires routing logic (auto-approve, human-review, reject) that traditional tools cannot express.

Diva Goals exists because no existing tool models the full agentic SDLC chain with evidence-backed status, agent participation, and structured review.

---

## Why It Is Not Just an OKR Tool

An OKR tool models: Objective -> Key Result -> (maybe) Initiative -> Task.
Status is self-reported. Evidence is optional. Agents do not exist as entities.

Diva Goals models:

```
Objective -> KR -> Initiative -> Spec -> Work Item -> Agent Run -> PR -> Pipeline -> Eval Gate -> Release -> Runtime Metric
```

Every entity has:
- A source system reference (Azure Boards ID, GitHub PR URL, pipeline run ID)
- Derived status computed from source system evidence
- Freshness tracking (how old is the evidence?)
- Participant attribution (which human or agent produced this?)

Status is derived, not self-reported. Evidence is mandatory, not optional. Agents are first-class participants with identity, confidence scores, and audit trails.

---

## Relationship to Existing Systems

### Azure Boards

Azure Boards is the **source of truth for goals, KRs, initiatives, and work items**. Diva Goals reads from Azure Boards via API (batch sync + webhooks). It does not replace Azure Boards for backlog management, sprint planning, or task assignment.

Diva Goals adds: derived status computation, evidence linkage, drift detection, and structured review on top of Azure Boards data.

### Spec Kit (spec/ directory)

The spec kit is the **source of truth for product specifications**. Each spec bundle (constitution.md, prd.md, plan.md, tasks.md) defines a delivery unit. Diva Goals scans the spec directory, computes completeness scores, and links spec bundles to initiatives.

Diva Goals adds: spec-to-goal traceability, completeness tracking, and task extraction for work item mapping.

### GitHub

GitHub is the **source of truth for code, PRs, and repositories**. Diva Goals ingests PR events, Actions run results, and release publications via webhooks.

Diva Goals adds: PR-to-work-item traceability, agent authorship detection, and evidence linkage from PRs through the delivery chain.

### Azure DevOps Pipelines

Azure DevOps Pipelines is the **source of truth for CI/CD execution**. Diva Goals ingests pipeline completion events via webhooks.

Diva Goals adds: pipeline-to-work-item traceability, eval gate detection within pipeline stages, and evidence for delivery status.

### Runtime Observability (Application Insights, Databricks, Power BI)

These systems are the **source of truth for runtime metrics and health**. Diva Goals reads metrics in batch (hourly/daily) to compute KR current values.

Diva Goals adds: metric-to-KR binding, freshness tracking, and the final link in the evidence chain (did the goal actually produce a runtime outcome?).

---

## Why Agentic SDLC is First-Class

In the InsightPulse AI platform, agents are not peripheral tools -- they are core delivery participants:

- **Claude Code** produces code changes, spec drafts, and configuration updates.
- **AI Foundry agents** execute specialized tasks (tax compliance, document processing, data ingestion).
- **Eval runners** score agent output quality and gate releases.
- **Ops agents** monitor runtime health and report metrics.

A control plane that ignores agent participation is blind to how most of the delivery work actually happens. Diva Goals models:

- **Agent identity**: Who is this agent? What can it do? When was it registered?
- **Agent runs**: When did it run? What was the input? What did it produce? How confident is it?
- **Confidence scoring**: 0.0-1.0 scale with routing thresholds (auto-approve >= 0.9, human-review 0.7-0.89, low-confidence 0.5-0.69, auto-reject < 0.5).
- **Approval workflow**: Human approval required for agent outputs above the work-item level. Every approval is logged with justification.

---

## Why Humans Remain Approval Authority

Diva Goals follows the principle: **humans approve, agents propose**. Agents can:

- Propose status changes
- Create draft review summaries
- Flag drift and orphans
- Recommend actions

Agents cannot:

- Close goals or KRs
- Mark initiatives as complete
- Override failing eval gates
- Approve releases
- Modify governance policy

This is not a temporary constraint. It is a permanent architectural decision. The value of Diva Goals is that it makes agent participation visible and auditable while keeping humans in control of material decisions.

---

## Persistence and Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Graph storage | Databricks Unity Catalog (Delta tables) | Governed, queryable, auditable, integrates with existing lakehouse |
| Evidence ingestion | Azure Functions + Event Grid | Event-driven for CI/CD, batch for metrics |
| Read surface | Power BI | Primary business-facing reporting surface (platform standard) |
| Review UI | Custom web app (Azure Container Apps) | Interactive review ceremonies not suited for BI dashboards |
| Secrets | Azure Key Vault | Platform standard for all credentials |
| Identity | Microsoft Entra ID | Platform standard for user authentication |

---

## Delivery Phases

1. **Core Strategy Graph** (Weeks 1-3): Import from Azure Boards, establish graph, derive status.
2. **SDLC Evidence Chain** (Weeks 4-6): Ingest PRs, pipelines, evals. Drill-through from goal to evidence.
3. **Agent Participation** (Weeks 7-9): Agent identity, runs, confidence, approval workflow.
4. **Review Engine** (Weeks 10-12): Execution/portfolio/exception reviews. Drift and orphan detection.
5. **Governance Automation** (Weeks 13-16): Policy gates, override audit, export/snapshot.

---

## Reference

- Spec bundle: `spec/diva-goals/` (constitution, PRD, plan, tasks)
- SSOT metadata: `ssot/platform/diva_goals.yaml`
- Constitution (invariants): `spec/diva-goals/constitution.md`

---

*Product: Diva Goals*
*Version: 1.0*
*Last updated: 2026-03-23*
