# Diva Goals -- Target State Architecture

> What Diva Goals is, why it exists, how it relates to the existing platform, and why it requires the capability axis and Microsoft Agent Framework.

---

## What is Diva Goals?

Diva Goals is an **AI-native strategy, capability, and execution control plane** for the agentic DevOps SDLC. It is the orchestration, review, and readiness layer that connects strategic objectives to delivery evidence, runtime outcomes, and organizational capability.

It provides:

1. A **strategy-to-execution graph** that traces from goals through KRs, initiatives, specs, work items, agent runs, PRs, pipelines, eval gates, releases, and runtime metrics.
2. An **evidence engine** that ingests delivery and runtime data from source systems and computes derived status.
3. A **review engine** that provides structured review ceremonies (execution, portfolio, capability, agent readiness, exception) with evidence-backed inputs and decision tracking.
4. An **agent participation model** that treats maker agents, judge agents, and ops agents as first-class graph entities with identity, confidence scoring, and approval workflows.
5. A **human capability model** that maps role families, proficiency ladders, and capability gaps to strategic priorities, with learning-path linkage and readiness tracking.
6. An **agent capability model** that governs agent roles, skill packs, eval-based readiness tiers, autonomy management, and degradation rules.

---

## Why Diva Goals Is More Than Goals Software

Traditional OKR tools answer one question: "Are we hitting our targets?" Diva Goals answers five:

1. **Are we hitting our targets?** (Strategy graph + derived status from execution evidence)
2. **Do we have the delivery chain to hit them?** (Execution graph + spec/work-item/PR/pipeline traceability)
3. **Do our people have the capabilities to execute?** (Human capability graph + gap scoring + learning linkage)
4. **Do our agents have the skills and readiness to operate?** (Agent capability graph + eval scores + autonomy tiers)
5. **Are we getting better?** (Review engine + trend analysis + readiness trajectory)

A goals tool without the capability axis is blind to the most common reason goals fail: the organization lacks the skills (human or agent) to execute. A goals tool without agent governance is blind to the fastest-growing workforce in the organization.

### The Five Product Modules

| Module | Owns | Key Question |
|--------|------|-------------|
| **Goals** | Objectives, KRs, Initiatives, strategic alignment | Are we on track? |
| **Execution** | Spec bundles, work items, agent runs, PRs, pipelines, eval gates, releases | Are we delivering? |
| **People Capability** | Role families, proficiency ladders, capability gaps, learning paths, assessments | Can our people execute? |
| **Agent Capability** | Agent roles, skill packs, eval scores, autonomy tiers, degradation rules | Can our agents operate? |
| **Reviews** | Execution review, portfolio review, capability review, agent readiness review, exception review | Are we governing? |
| **Governance** | Policy gates, audit trails, export/snapshot, stale evidence management | Are we compliant? |

---

## Why It Exists

Traditional OKR and goal-tracking tools were designed for human-only organizations. They model goals as text fields, status as dropdowns, and progress as self-reported percentages. This breaks in an AI-first organization where:

- **Agents produce delivery artifacts** (code, specs, configs) and need to be modeled as participants, not invisible background processes.
- **Eval gates** determine release readiness based on automated scoring, not human checkbox completion.
- **Spec-driven delivery** means work is structured as spec bundles (constitution, PRD, plan, tasks), not flat task lists.
- **Runtime evidence** should close the loop on whether goals were actually achieved, not just whether tasks were marked done.
- **Confidence scoring** for agent outputs requires routing logic (auto-approve, human-review, reject) that traditional tools cannot express.
- **Capability gaps** block strategic outcomes but live in siloed L&D systems disconnected from strategy.
- **Agent workforce governance** requires eval-based promotion, degradation rules, and maker/judge separation that no existing tool provides.

---

## Why Agent Framework + Foundry Is the Canonical Stack

Diva Goals is not just a dashboard that reads from APIs. It is an **active orchestration system** with agents that collect evidence, synthesize reviews, validate readiness, and enforce policy. These agents need:

1. **Orchestration** -- multi-agent workflow graphs with sequential steps, parallel execution, and human-approval checkpoints. **Microsoft Agent Framework SDK** provides this.

2. **Managed runtime** -- hosted agent execution with versioning, scaling, and rollback. **Azure AI Foundry Agent Service** provides this.

3. **Knowledge access** -- domain knowledge (specs, architecture docs, policies) accessible to agents at inference time. **Foundry IQ via MCP** (`knowledge_base_retrieve`) provides this.

4. **Skills packaging** -- reusable agent capabilities with defined input/output contracts. **Agent Skills** provides this.

5. **Evaluation** -- automated scoring of agent output quality across multiple dimensions. **Foundry evaluators** (task_completion, task_adherence, intent_resolution, tool_call_accuracy, groundedness) provide this.

6. **Observability** -- traceable telemetry for every agent invocation with latency, errors, and audit trails. **Foundry tracing + Azure Monitor** provides this.

No single tool provides all six. The Agent Framework + Foundry combination is the only stack that does, while remaining native to the Azure platform that hosts the rest of the InsightPulse AI infrastructure.

---

## Diva Goals Review Stack

Diva Goals provides five structured review ceremonies, each with defined cadence, inputs, outputs, and governance rules.

### Business Reviews

| Review | Cadence | Focus |
|--------|---------|-------|
| **Execution Review** | Weekly | Initiative progress, blocked items, agent output pending review, drift flags |
| **Portfolio Review** | Monthly | Goal/KR progress, strategic alignment, resource allocation, exception log |

### Capability Reviews

| Review | Cadence | Focus |
|--------|---------|-------|
| **Capability/Readiness Review** | Quarterly | Human capability gaps, learning effectiveness, readiness heat map |
| **Agent Readiness Review** | Quarterly | Agent eval scores, autonomy tier appropriateness, skill-pack coverage |
| **Learning Effectiveness Review** | Quarterly | L&D program outcomes, capability gap closure rate, learning ROI |

### Exception Reviews

| Review | Cadence | Focus |
|--------|---------|-------|
| **Exception Review** | On-demand | Specific drift, eval failure, stale evidence, manual escalation |

### Organizational Health

The review stack as a whole provides a **layered health signal**:

- **Weekly**: Are we delivering? (execution)
- **Monthly**: Are we aligned? (portfolio)
- **Quarterly**: Can we execute? (capability + agent readiness)
- **On-demand**: Is something broken? (exception)

No layer operates in isolation. Exception reviews escalate to portfolio reviews. Capability gaps surface in execution reviews as blockers. Agent readiness affects delivery velocity.

---

## Relationship to Existing Systems

### Azure Boards

Azure Boards is the **source of truth for goals, KRs, initiatives, and work items**. Diva Goals reads from Azure Boards via API (batch sync + webhooks). It does not replace Azure Boards for backlog management, sprint planning, or task assignment.

Diva Goals adds: derived status computation, evidence linkage, drift detection, capability-requirement mapping, and structured review on top of Azure Boards data.

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

### HR/L&D Systems

HR and L&D systems are the **source of truth for people capability evidence** -- role assignments, assessment scores, learning completions, certifications. Diva Goals reads this data to populate the human capability graph.

Diva Goals adds: strategic-priority-to-capability mapping, gap scoring as strategic blockers, and readiness review ceremonies.

### Agent Registries and Eval Frameworks

Agent registries and Foundry eval pipelines are the **source of truth for agent capability evidence** -- registered roles, skill packs, eval scores, autonomy tiers. Diva Goals reads this data to populate the agent capability graph.

Diva Goals adds: agent-role-to-strategic-priority mapping, eval-based autonomy governance, and agent readiness review ceremonies.

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
- **Autonomy tiers**: Supervised, semi-autonomous, autonomous -- with eval-gated promotion and automatic degradation.
- **Skill packs**: Versioned capability packages with tool declarations, knowledge-base bindings, and eval suites.

---

## Why Humans Remain Approval Authority

Diva Goals follows the principle: **humans approve, agents propose**. Agents can:

- Propose status changes
- Create draft review summaries
- Flag drift and orphans
- Recommend actions
- Score readiness

Agents cannot:

- Close goals or KRs
- Mark initiatives as complete
- Override failing eval gates
- Approve releases
- Modify governance policy
- Promote agent autonomy tiers
- Certify human capability readiness

This is not a temporary constraint. It is a permanent architectural decision. The value of Diva Goals is that it makes agent participation visible and auditable while keeping humans in control of material decisions.

---

## Persistence and Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Graph storage | Databricks Unity Catalog (Delta tables) | Governed, queryable, auditable, integrates with existing lakehouse |
| Evidence ingestion | Azure Functions + Event Grid | Event-driven for CI/CD, batch for metrics |
| Read surface | Power BI | Primary business-facing reporting surface (platform standard) |
| Review UI | Custom web app (Azure Container Apps) | Interactive review ceremonies not suited for BI dashboards |
| Agent orchestration | Microsoft Agent Framework SDK | Multi-agent workflow graphs with approval checkpoints |
| Agent runtime | Azure AI Foundry Agent Service | Hosted agent execution with versioning |
| Agent knowledge | Foundry IQ / Azure AI Search via MCP | Domain knowledge for agents |
| Agent skills | Agent Skills packages | Reusable agent capabilities |
| Agent evaluation | Foundry evaluators | task_completion, task_adherence, intent_resolution, tool_call_accuracy |
| Agent observability | Foundry tracing + Azure Monitor | Telemetry for all agent operations |
| Secrets | Azure Key Vault | Platform standard for all credentials |
| Identity | Microsoft Entra ID | Platform standard for user authentication |

---

## Delivery Phases

1. **Core Strategy Graph** (Weeks 1-3): Import from Azure Boards, establish graph, derive status.
2. **SDLC Evidence Chain** (Weeks 4-6): Ingest PRs, pipelines, evals. Drill-through from goal to evidence.
3. **Agent Participation** (Weeks 7-9): Agent identity, runs, confidence, approval workflow.
4. **Review Engine** (Weeks 10-12): Execution/portfolio/exception reviews. Drift and orphan detection.
5. **Governance Automation** (Weeks 13-16): Policy gates, override audit, export/snapshot.
6. **Capability Model** (Weeks 17-20): Human capability taxonomy, role families, proficiency ladders, gap scoring.
7. **Agent Development Governance** (Weeks 21-24): Agent role catalog, skill packs, eval tiers, autonomy management, degradation rules.

---

## Reference

- Spec bundle: `spec/diva-goals/` (constitution, PRD, plan, tasks)
- SSOT metadata: `ssot/platform/diva_goals.yaml`
- Constitution (invariants): `spec/diva-goals/constitution.md`

---

*Product: Diva Goals*
*Version: 2.0*
*Last updated: 2026-03-23*
