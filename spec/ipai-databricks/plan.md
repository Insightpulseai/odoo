# IPAI Databricks – Implementation Plan

## Overview

This plan outlines the phased implementation of IPAI Databricks, a self-hosted lakehouse platform built on Supabase, DigitalOcean, Vercel, Odoo CE, and the Pulser/MCP agent framework.

---

## Phase 1: Foundations (M1)

### Objectives
- Establish lakehouse schema structure
- Configure infrastructure baseline
- Implement Spec Kit CI enforcement

### Deliverables

**1.1 Lakehouse Schemas**
- Create Supabase migrations for:
  - `ipai_bronze_core` schema (raw data landing)
  - `ipai_silver_core` schema (cleaned/normalized)
  - `ipai_gold_core` schema (analytics-ready)
  - `ipai_platinum_core` schema (ML/AI features)
- Implement specialized schemas:
  - `ipai_bronze_erp`, `ipai_silver_erp`, `ipai_gold_erp`
  - `ipai_bronze_devops`, `ipai_gold_devops`

**1.2 Infrastructure Setup**
- Supabase project configuration
  - Enable required extensions (pgvector, pg_cron)
  - Configure Vault for secrets
  - Set up RLS policies
- DigitalOcean resources
  - Object storage (Spaces) for large files
  - Compute droplet for heavy workloads
- Vercel project setup
  - App deployment pipeline
  - AI Gateway configuration

**1.3 CI/CD Pipeline**
- Spec Kit validation workflow
- Migration testing on scratch DB
- Lint and test gates

### Dependencies
- Supabase access token
- DO API token
- Vercel team access

---

## Phase 2: Core Connectors (M2)

### Objectives
- Implement IPAI Connector Framework
- Build priority connectors (Odoo, GitHub, Files)

### Deliverables

**2.1 Connector Framework**
- `ipai_connector_config` table and RPCs
- `ipai_connector_run` logging
- Scheduler integration (n8n / Supabase cron)

**2.2 Odoo CE Connector**
- Full sync: invoices, journal entries, partners, products, projects
- Incremental sync: timestamp-based
- Schema mapping: Odoo → bronze tables

**2.3 GitHub Connector**
- Sync: repositories, issues, PRs, workflows
- Event ingestion: webhooks for real-time
- Schema mapping: GitHub → bronze tables

**2.4 File Connector**
- Support: CSV, JSON, Parquet
- Sources: Supabase Storage, DO Spaces, URL
- Schema inference and mapping

### Dependencies
- Odoo CE XML-RPC access
- GitHub App credentials
- Storage bucket configuration

---

## Phase 3: Apps v1 (M3)

### Objectives
- Launch reference apps with governed data access
- Integrate basic AI copilot features

### Deliverables

**3.1 App Registry**
- `ipai_app_registry` table
- Deployment pipeline (Vercel)
- Auth integration (Supabase Auth)

**3.2 Finance Command Center**
- Views: P&L, balance sheet, cashflow
- Features: open items, AR/AP aging
- AI: reconciliation suggestions

**3.3 DevOps Health App**
- Views: Spec Kit compliance, CI status
- Features: deployment timeline, MTTR
- AI: anomaly detection alerts

**3.4 App Runtime Contract**
- Standard auth flow
- Data access via Supabase client
- Logging and error handling

### Dependencies
- Gold-layer views populated
- Agent framework ready (M4 overlap)

---

## Phase 4: Agent Governance (M4)

### Objectives
- Register and govern AI agents
- Integrate MCP tools with data scopes

### Deliverables

**4.1 Agent Registry**
- `ipai_agent` table with:
  - allowed_tools
  - allowed_schemas
  - cost/latency budgets
- `ipai_agent_run` logging

**4.2 MCP Integration**
- Supabase MCP server tools
- Data scope enforcement
- Tool registration for agents

**4.3 Agent Policies**
- RLS policies for agent access
- Audit logging for all invocations
- Cost tracking and alerts

### Dependencies
- Pulser MCP framework
- Vercel AI Gateway (optional)

---

## Phase 5: Observability & Hardening (M5)

### Objectives
- Production-grade monitoring
- Security audit and compliance
- Operational runbooks

### Deliverables

**5.1 Observability Stack**
- Connector metrics (success rate, latency)
- Agent metrics (tokens, cost, latency)
- App metrics (availability, errors)

**5.2 Alerting**
- SLO-based alerts (n8n / Mattermost)
- Error budget tracking
- On-call integration

**5.3 Security Hardening**
- RLS audit across all schemas
- Vault secrets rotation
- Penetration testing

**5.4 Documentation**
- Runbooks for common operations
- Incident response playbooks
- Architecture decision records

### Dependencies
- All previous phases complete
- Observability backend (Axiom / Sentry)

---

## Timeline (Indicative Phases)

| Phase | Focus | Prerequisites |
|-------|-------|---------------|
| M1 | Foundations | None |
| M2 | Core Connectors | M1 complete |
| M3 | Apps v1 | M1, partial M2 |
| M4 | Agent Governance | M1, M2 |
| M5 | Observability | M1-M4 complete |

---

## Sub-Specs to Spawn

As IPAI Databricks matures, spawn dedicated Spec Kits for:

1. `spec/ipai-connector-odoo/` - Odoo CE connector details
2. `spec/ipai-connector-github/` - GitHub connector details
3. `spec/ipai-app-finance/` - Finance Command Center
4. `spec/ipai-app-devops/` - DevOps Health app
5. `spec/ipai-agent-governance/` - Agent framework deep-dive

---

*Last updated: 2026-01-25*
