# Tasks — Control Room Platform

> Work breakdown for the Control Room Platform implementation.

---

## Phase 0: Infrastructure

- [ ] **P0.1.1** Research Plane self-hosted requirements (CPU, RAM, storage, PG, Redis)
- [ ] **P0.1.2** Create Plane deployment manifests (Docker Compose or Container Apps Bicep)
- [ ] **P0.1.3** Deploy Plane stack (Web, Admin, API, Worker, Beat, Live, Silo)
- [ ] **P0.1.4** Configure DNS: `plane.insightpulseai.com`
- [ ] **P0.1.5** Configure Entra ID SSO for Plane
- [ ] **P0.2.1** Create workspace "InsightPulseAI Control Room"
- [ ] **P0.2.2** Configure work item types and workflow states
- [ ] **P0.2.3** Apply label taxonomy
- [ ] **P0.2.4** Enable GitHub Silo integration
- [ ] **P0.2.5** Enable Slack integration
- [ ] **P0.3.1** Deploy Plane MCP server
- [ ] **P0.3.2** Register MCP server in agents repo

## Phase 1: Execution Layer

- [ ] **P1.1.1** Create initiative: AI Agent Platform (4 epics)
- [ ] **P1.1.2** Create initiative: ERP Intelligence (4 epics)
- [ ] **P1.1.3** Create initiative: Data Intelligence (4 epics)
- [ ] **P1.1.4** Create initiative: Workspace & Knowledge (3 epics)
- [ ] **P1.2.1** Audit existing planning artifacts (73 identified)
- [ ] **P1.2.2** Map artifacts to Plane initiatives/epics
- [ ] **P1.2.3** Create work items for open items
- [ ] **P1.2.4** Archive legacy planning artifacts
- [ ] **P1.3.1** Define spec bundle → Plane epic linking convention
- [ ] **P1.3.2** Link existing spec bundles to Plane epics

## Phase 2: Intelligence Layer

- [ ] **P2.1.1** Create Plane API → Bronze ingestion pipeline
- [ ] **P2.1.2** Create GitHub API → Bronze ingestion pipeline
- [ ] **P2.1.3** Create Odoo API → Bronze ingestion pipeline
- [ ] **P2.1.4** Create Foundry telemetry → Bronze ingestion pipeline
- [ ] **P2.1.5** Build Silver/Gold transformations for delivery metrics
- [ ] **P2.1.6** Build Silver/Gold transformations for engineering metrics
- [ ] **P2.1.7** Build Silver/Gold transformations for finance metrics
- [ ] **P2.2.1** Scaffold Databricks App (Streamlit)
- [ ] **P2.2.2** Build Executive Summary page
- [ ] **P2.2.3** Build Delivery Health page
- [ ] **P2.2.4** Build Finance Ops Health page
- [ ] **P2.2.5** Build Anomaly/Risk Feed page
- [ ] **P2.2.6** Build Agent Runtime Metrics page
- [ ] **P2.2.7** Build Source System Freshness page
- [ ] **P2.2.8** Build Evidence/Audit Readiness page
- [ ] **P2.2.9** Configure OAuth + Unity Catalog access
- [ ] **P2.3.1** Define data contracts (schema + freshness SLA)
- [ ] **P2.3.2** Implement freshness monitoring pipeline
- [ ] **P2.3.3** Implement anomaly detection pipeline

## Phase 3: Agent Layer

- [ ] **P3.1.1** Build Status Synthesis agent (Foundry)
- [ ] **P3.1.2** Build Blocker Triage agent (Foundry)
- [ ] **P3.1.3** Build Risk Summarizer agent (Foundry)
- [ ] **P3.1.4** Build Finance Close Assistant agent (Foundry)
- [ ] **P3.1.5** Build Control Room Q&A agent (Foundry)
- [ ] **P3.2.1** Connect agents to Plane MCP server
- [ ] **P3.2.2** Implement automated weekly status reports
- [ ] **P3.2.3** Implement work item creation from agent actions
- [ ] **P3.3.1** Connect agents to Databricks Gold/Platinum layers
- [ ] **P3.3.2** Implement RAG for Q&A agent over dashboard data
- [ ] **P3.3.3** Connect Risk agent to anomaly feed

## Phase 4: Strategy Layer

- [ ] **P4.1.1** Create Figma roadmap template
- [ ] **P4.1.2** Populate Q1-Q3 2026 roadmap
- [ ] **P4.1.3** Establish monthly update cadence
- [ ] **P4.2.1** End-to-end flow validation (Figma → Plane → Spec → GitHub)
- [ ] **P4.2.2** Dashboard validation (live data flowing through all pages)
- [ ] **P4.2.3** Agent validation (summaries are accurate and actionable)
