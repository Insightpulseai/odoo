# PRD — Control Room Platform

> Product requirements for the three-layer planning + execution + intelligence system.

---

## Problem Statement

73 scattered planning artifacts exist across the org with no canonical roadmap, no centralized execution tracking, and no operational intelligence dashboard. Decision-making is fragmented across Slack threads, GitHub issues, and ad-hoc docs.

## Solution

A three-layer Control Room Platform:

1. **Figma** — Strategic roadmap visualization (quarterly, executive-facing)
2. **Plane** — Execution workspace (weekly, team-facing)
3. **Databricks Apps** — Operational analytics (real-time, data-driven)

With **Azure Foundry** agents providing AI-powered coordination across layers.

---

## Requirements

### R1: Plane Workspace

#### R1.1: Workspace Structure

```
Workspace: InsightPulseAI Control Room

Initiatives:
├── AI Agent Platform
│   ├── Azure Foundry runtime
│   ├── Agent framework integration
│   ├── Copilot publication
│   └── MCP tool platform
│
├── ERP Intelligence
│   ├── Odoo Copilot
│   ├── Finance automation
│   ├── Compliance assistant
│   └── Document AI
│
├── Data Intelligence
│   ├── Databricks Apps
│   ├── Delta lakehouse
│   ├── AI forecasting
│   └── CES analytics
│
└── Workspace & Knowledge
    ├── Plane workspace rollout
    ├── Knowledge grounding
    └── Docs integration
```

#### R1.2: Work Item Types

| Type | Purpose |
|------|---------|
| Feature | New functionality |
| Task | Implementation work |
| Bug | Defect fix |
| Research | Investigation / spike |
| Infrastructure | Platform / infra work |
| Spec | Spec bundle creation |

#### R1.3: Workflow States

```
Backlog → Ready → In Progress → Review → Done
                                    ↓
                                 Blocked
```

#### R1.4: Labels

| Category | Labels |
|----------|--------|
| Domain | AI, ERP, Analytics, Infra, Security, Compliance |
| Agent | claude, copilot, gemini, foundry |
| Priority | critical, high, medium, low |

#### R1.5: Integrations

- GitHub Silo: bidirectional PR/issue sync
- Slack: notifications for state transitions
- MCP Server: agent-driven work item creation

---

### R2: Databricks Control Room App

#### R2.1: App Pages

| Page | Content |
|------|---------|
| Executive Summary | Initiative health, velocity, risk score |
| Delivery Health | Epic progress, burndown, cycle time |
| Finance Ops Health | Close readiness, compliance score, PPM metrics |
| Anomaly/Risk Feed | AI-detected anomalies across all data sources |
| Agent Runtime Metrics | Foundry agent performance, tool usage, latency |
| Source System Freshness | Data pipeline SLA, last-updated timestamps |
| Evidence / Audit Readiness | Compliance evidence inventory, gap analysis |

#### R2.2: Data Sources

- Plane API → delivery metrics (via lakehouse ingestion)
- Odoo API → finance/ERP metrics (via lakehouse ingestion)
- Databricks system tables → pipeline/compute metrics
- Foundry telemetry → agent metrics
- GitHub API → engineering metrics

#### R2.3: Technology

- Framework: Streamlit or Dash (Python)
- Hosting: Databricks Apps (serverless)
- Auth: Databricks OAuth + Unity Catalog governance
- Data: Gold/Platinum layers only

---

### R3: Foundry Agent Roles

| Agent | Purpose |
|-------|---------|
| Status Synthesis | Weekly delivery summary from Plane + GitHub |
| Blocker Triage | Identify and escalate blocked work items |
| Risk Summarizer | Cross-system anomaly aggregation |
| Finance Close Assistant | Close readiness checks, compliance gaps |
| Control Room Q&A | Natural language queries against dashboards |

---

### R4: Figma Roadmap

#### R4.1: Board Layout

Quarterly timeline with swim lanes per initiative:

```
Q1 2026                    Q2 2026                    Q3 2026
─────────────────────────  ─────────────────────────  ─────────────
AI: Odoo Copilot           AI: Intelligence Layer     AI: Enterprise Copilot
AI: Azure Foundry          AI: Plane integration      AI: Marketplace plugins
Data: Databricks Apps      Data: CES Analytics        Data: Forecasting
ERP: Finance PPM           ERP: Compliance            ERP: Document AI
```

#### R4.2: Not a Task Manager

The Figma roadmap shows:
- Strategic direction (what, when, why)
- Initiative ownership
- Quarterly milestones

It does NOT show:
- Individual tasks
- Sprint items
- Bug fixes

---

## Success Criteria

1. Single Plane workspace replaces all scattered planning artifacts
2. Databricks Control Room App serves as the operational intelligence dashboard
3. Foundry agents automate status synthesis and risk detection
4. Figma roadmap is the single executive-facing strategic view
5. All layers are connected: Figma → Plane → Spec Kit → GitHub
