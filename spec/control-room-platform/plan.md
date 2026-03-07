# Plan — Control Room Platform

> Implementation plan for the three-layer Control Room Platform.

---

## Phase 0: Infrastructure (Week 1)

### P0.1: Deploy Plane Self-Hosted

- Deploy Plane on Azure Container Apps (or DigitalOcean if cost-constrained)
- Services: Web, Admin, API, Worker, Beat, Live, Silo
- Dependencies: PostgreSQL, Redis/Valkey
- DNS: `plane.insightpulseai.com`
- Auth: SSO via Microsoft Entra ID

### P0.2: Configure Plane Workspace

- Create workspace: "InsightPulseAI Control Room"
- Configure work item types (Feature, Task, Bug, Research, Infrastructure, Spec)
- Configure workflow states (Backlog → Ready → In Progress → Review → Blocked → Done)
- Apply label taxonomy
- Enable GitHub Silo integration
- Enable Slack integration

### P0.3: Plane MCP Server

- Deploy Plane MCP server for agent integration
- Configure tool permissions (create, read, update work items)
- Register in agents repo MCP registry

---

## Phase 1: Execution Layer (Week 2-3)

### P1.1: Create Initiative Structure

Create 4 initiatives with epics per the PRD workspace structure.

### P1.2: Migrate Existing Planning Artifacts

- Audit 73 existing planning artifacts across repos
- Map each to the correct Plane initiative/epic
- Create work items for open items
- Archive or link legacy artifacts

### P1.3: Spec Kit → Plane Mapping

- Each spec bundle maps to a Plane epic
- Create linking convention: Plane epic description links to `spec/<bundle>/`
- Spec bundle `tasks.md` maps to Plane work items

---

## Phase 2: Intelligence Layer (Week 3-4)

### P2.1: Lakehouse Ingestion Pipelines

Create Bronze → Silver → Gold pipelines for:
- Plane API → delivery metrics
- Odoo API → finance/ERP metrics
- GitHub API → engineering metrics
- Foundry telemetry → agent metrics

### P2.2: Databricks Control Room App

- Build Streamlit/Dash app on Databricks Apps
- Implement 7 pages per PRD (executive summary through audit readiness)
- Configure OAuth + Unity Catalog access
- Deploy on Databricks serverless

### P2.3: Data Contracts

- Define schema contracts between source systems and Gold layer
- Implement freshness SLA monitoring
- Create anomaly detection pipeline

---

## Phase 3: Agent Layer (Week 4-5)

### P3.1: Foundry Agent Deployment

Deploy 5 agents per PRD:
1. Status Synthesis agent
2. Blocker Triage agent
3. Risk Summarizer agent
4. Finance Close Assistant
5. Control Room Q&A agent

### P3.2: Agent ↔ Plane Integration

- Connect agents to Plane via MCP server
- Agents can create work items, update status, add comments
- Weekly automated status reports

### P3.3: Agent ↔ Databricks Integration

- Agents query Gold/Platinum layers for intelligence
- Q&A agent uses RAG over dashboard data
- Risk agent monitors anomaly feed

---

## Phase 4: Strategy Layer (Week 5-6)

### P4.1: Figma Roadmap Board

- Create quarterly roadmap in Figma
- Populate with current initiatives
- Establish update cadence (monthly)

### P4.2: End-to-End Flow Validation

- Verify: Figma item → Plane initiative → Spec bundle → GitHub implementation
- Verify: Databricks App reflects live delivery/finance metrics
- Verify: Foundry agents produce actionable summaries

---

## Dependencies

```
P0 (Infra)
  ├── P1 (Execution) — needs Plane running
  │     └── P2.1 (Ingestion) — needs Plane API data
  └── P3.1 (Agents) — needs Plane MCP

P2.1 (Ingestion)
  └── P2.2 (Dashboard) — needs Gold layer data

P1 + P2 + P3
  └── P4 (Strategy) — needs all layers working
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Plane self-hosted complexity | Start with Docker Compose, migrate to k8s later |
| Data pipeline delays | Start with GitHub + Plane APIs (simplest), add Odoo later |
| Agent quality | Implement eval framework before production deployment |
| Figma adoption | Keep roadmap simple, update monthly not weekly |
