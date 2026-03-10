# IPAI Data Connectors — Product Requirements Document

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-01-25
> **Related Docs**: [constitution.md](constitution.md) | [plan.md](plan.md) | [tasks.md](tasks.md)

---

## 1. Executive Summary

Build a self-hosted, open connector platform ("IPAI Data Connectors") that delivers Fivetran-style ELT into a Databricks-style lakehouse and Odoo CE/OCA stack, without relying on proprietary Fivetran or Databricks licenses.

The platform will:

- Provide **first-class connectors** for Google and other key SaaS sources
- Land data into a **Delta-compatible lakehouse** (Parquet + Delta-style metadata) plus **Postgres/Supabase** for operational use
- Be **agent-driven and API-first**, designed to integrate with Supabase MCP, n8n, and the Pulser agent framework

---

## 2. Problem Statement

### 2.1 Current State

- Ad-hoc scripts for data extraction across teams
- Heterogeneous ETL with no single "connector" abstraction
- Dependency on expensive SaaS tools (Fivetran, Databricks)
- No agent-accessible interface for automated data operations

### 2.2 Desired State

- Unified connector framework with declarative configuration
- Self-hosted on DigitalOcean/Supabase/on-prem infrastructure
- Lakehouse architecture with Bronze/Silver/Gold layers
- Full agent/MCP integration for automated orchestration

---

## 3. User Personas

| Persona | Role | Responsibilities | Pain Points |
|---------|------|------------------|-------------|
| **DataEng Dana** | Data Engineer | Define connectors, schemas, SLAs | Too many custom scripts, no reusability |
| **Analyst Alex** | Finance/Ops Analyst | Consume curated views for reporting | Data freshness issues, manual exports |
| **Agent Otto** | AI Orchestrator (Pulser/n8n) | Programmatically manage syncs | No API to trigger or monitor jobs |
| **Admin Ada** | Platform Admin | Monitor health, manage credentials | Scattered configs, no single dashboard |

---

## 4. Functional Requirements

### 4.1 Connector Framework

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Each connector defined as YAML spec (source_type, auth, sync_mode, schedule) | P0 |
| FR-002 | Support OAuth 2.0, API key, and service account authentication | P0 |
| FR-003 | Support full, incremental, and CDC sync modes | P0 |
| FR-004 | Centralized scheduler with cron expression support | P0 |
| FR-005 | State management for cursors and bookmarks | P0 |
| FR-006 | Retry with exponential backoff and API quota awareness | P0 |
| FR-007 | Per-run logs persisted to Supabase | P0 |
| FR-008 | Python/TypeScript "tap" implementation pattern | P1 |
| FR-009 | Generic HTTP connector for custom APIs | P1 |
| FR-010 | Generic JDBC connector for database sources | P1 |

### 4.2 Destination & Schema

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-011 | Object storage destination (DO Spaces, S3, Supabase Storage) | P0 |
| FR-012 | Postgres/Supabase destination via COPY/INSERT | P0 |
| FR-013 | Bronze layer: `raw_<source>_<stream>` tables with minimal typing | P0 |
| FR-014 | Silver layer: deduplicated, typed tables with partitioning | P0 |
| FR-015 | Gold layer: business views (`gold_<domain>_<entity>`) | P0 |
| FR-016 | Support Parquet output format | P1 |
| FR-017 | Support Delta Lake metadata format | P2 |

### 4.3 Control Plane (Supabase)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-018 | `connector_definitions` table (id, type, yaml_spec, version, enabled) | P0 |
| FR-019 | `connector_instances` table (id, definition_id, env, schedule, status) | P0 |
| FR-020 | `connector_runs` table (id, instance_id, started_at, ended_at, status, rows_processed) | P0 |
| FR-021 | `connector_state` table (instance_id, state_json) | P0 |
| FR-022 | Supabase Vault integration for secrets | P0 |
| FR-023 | RPC functions for agent/CI connector operations | P0 |

### 4.4 Phase 1 Connectors

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-024 | Google Analytics 4 (GA4) connector | P0 |
| FR-025 | Google Ads connector | P0 |
| FR-026 | Google Search Console connector | P0 |
| FR-027 | YouTube Analytics connector | P1 |
| FR-028 | BigQuery export tables connector | P1 |
| FR-029 | GitHub connector (repos, commits, PRs, issues) | P0 |
| FR-030 | Odoo CE/OCA connector (Postgres direct or API) | P0 |
| FR-031 | Vercel connector (projects, deployments, logs) | P1 |
| FR-032 | Supabase connector (tables, functions, logs) | P1 |
| FR-033 | DigitalOcean connector (droplets, apps, metrics) | P1 |

### 4.5 Agent/MCP Integration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-034 | MCP tool: `connector:list` - list all connectors | P0 |
| FR-035 | MCP tool: `connector:create` - create sync config | P0 |
| FR-036 | MCP tool: `connector:run` - trigger sync | P0 |
| FR-037 | MCP tool: `connector:status` - get run status | P0 |
| FR-038 | MCP tool: `connector:logs` - retrieve run logs | P0 |
| FR-039 | n8n webhook triggers on run completion | P1 |
| FR-040 | Pulser agent can orchestrate multi-connector pipelines | P1 |

---

## 5. Non-Functional Requirements

| ID | Requirement | Category | Priority |
|----|-------------|----------|----------|
| NFR-001 | Handle millions of rows per run for key connectors | Performance | P0 |
| NFR-002 | Incremental sync to limit API and warehouse cost | Performance | P0 |
| NFR-003 | At-least-once delivery with idempotent upserts | Reliability | P0 |
| NFR-004 | Job retries with exponential backoff | Reliability | P0 |
| NFR-005 | All secrets in Supabase Vault | Security | P0 |
| NFR-006 | Encrypted traffic (HTTPS/TLS) | Security | P0 |
| NFR-007 | Supabase RLS on control plane tables | Security | P0 |
| NFR-008 | Structured JSON logs for every run | Observability | P0 |
| NFR-009 | Metrics: rows per table, runtime, error counts | Observability | P0 |
| NFR-010 | Dashboards in Superset/Grafana | Observability | P1 |
| NFR-011 | 95% sync success rate target | SLA | P0 |
| NFR-012 | Horizontal scaling via queue-based workers | Scalability | P1 |

---

## 6. User Stories

### 6.1 Data Engineer Stories

**US-001**: As a Data Engineer, I want to define a connector via YAML so that I can version control and review sync configurations.

**Acceptance Criteria**:
- [ ] YAML spec includes source_type, auth method, sync mode, schedule
- [ ] Spec validates against JSON schema
- [ ] Changes require PR review

**US-002**: As a Data Engineer, I want incremental syncs to use cursors so that I minimize API calls and processing time.

**Acceptance Criteria**:
- [ ] Cursor persisted after each run
- [ ] Next run resumes from last cursor
- [ ] Full resync available on demand

### 6.2 Analyst Stories

**US-003**: As an Analyst, I want curated Gold views so that I can build dashboards without understanding raw data.

**Acceptance Criteria**:
- [ ] Gold views have consistent naming (`gold_<domain>_<entity>`)
- [ ] Views documented with column descriptions
- [ ] Views accessible from Superset

### 6.3 Agent Stories

**US-004**: As an AI Agent, I want to trigger syncs via MCP so that I can automate data refresh workflows.

**Acceptance Criteria**:
- [ ] MCP tool `connector:run` accepts instance_id
- [ ] Returns run_id for status tracking
- [ ] Errors returned as structured response

---

## 7. Integration Points

### 7.1 Internal Systems

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| Odoo CE/OCA | Postgres FDW / API | Expose Gold views for finance/ops |
| Superset | Direct SQL | BI dashboards on Gold layer |
| n8n | Webhooks | Workflow triggers on sync completion |
| Pulser | MCP | Agent-driven pipeline orchestration |

### 7.2 External Systems

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| Google APIs | REST API | GA4, Ads, GSC, YouTube data |
| GitHub API | REST/GraphQL | Repository and workflow data |
| Vercel API | REST | Deployment and log data |
| DigitalOcean API | REST | Infrastructure metrics |

---

## 8. Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Sync success rate | ≥ 95% | successful_runs / total_runs |
| Time-to-add-connector | ≤ 3 days | Spec approval to staging deploy |
| Time-to-dashboard | ≤ 1 week | New source to production dashboard |
| Ad-hoc ETL reduction | ≥ 70% | Custom scripts deprecated count |
| Odoo EE data parity | ≥ 80% | Data needs met by platform |
| Agent adoption | ≥ 50% syncs | Syncs triggered via MCP/API |

---

## 9. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API quota exceeded | Sync delays | Medium | Per-connector rate configs, backoff |
| Schema drift | Data quality issues | Medium | Schema introspection, auto-alerts |
| OAuth token expiry | Sync failures | Low | Proactive refresh, monitoring |
| Worker crash | Data loss | Low | Checkpoint resume, idempotent writes |
| Vendor TOS changes | Connector breaks | Low | Small modular code, TOS monitoring |

---

## 10. Future Work

- Multi-tenant management layer
- Automatic dbt model generation from schemas
- Per-table cost and carbon reporting
- Managed service offering on OSS core
- Real-time CDC for high-frequency sources
- Vector store exports for RAG pipelines

---

## 11. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-25 | IPAI Team | Initial PRD |
