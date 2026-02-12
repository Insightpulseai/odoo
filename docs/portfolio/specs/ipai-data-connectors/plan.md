# IPAI Data Connectors — Implementation Plan

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-01-25
> **Related Docs**: [constitution.md](constitution.md) | [prd.md](prd.md) | [tasks.md](tasks.md)

---

## 1. Overview

This plan outlines the phased implementation of IPAI Data Connectors, a self-hosted ELT platform delivering Fivetran-style connectors with Databricks-style lakehouse architecture.

---

## 2. Implementation Phases

### Phase 0: Foundation & Sandbox

**Objective**: Establish project structure, control plane, and development environment.

**Deliverables**:
- [x] Finalize spec kit (constitution, prd, plan, tasks)
- [ ] Create repository structure (`connectors/`, `configs/`, `sql/`)
- [ ] Implement Supabase schema for control plane
- [ ] Docker Compose for scheduler and single worker
- [ ] CI pipeline skeleton with quality gates
- [ ] Sandbox environment for testing

**Key Work**:
```
connectors/
├── core/                    # Core framework
│   ├── base_connector.py    # Abstract base class
│   ├── scheduler.py         # Job scheduler
│   ├── worker.py            # Job executor
│   └── state_manager.py     # Cursor/bookmark management
├── destinations/
│   ├── postgres.py          # Postgres/Supabase writer
│   └── object_storage.py    # S3/DO Spaces writer
└── utils/
    ├── auth.py              # OAuth, API key handlers
    ├── retry.py             # Exponential backoff
    └── logging.py           # Structured logging
```

**Success Criteria**:
- [ ] Control plane tables created in Supabase
- [ ] Worker can claim and execute a no-op test job
- [ ] CI validates YAML specs and runs linting
- [ ] Docker Compose starts scheduler + worker

---

### Phase 1: Google + DevOps Core

**Objective**: Deliver high-value Google and DevOps connectors with Bronze/Silver/Gold layers.

**Deliverables**:
- [ ] GA4 connector (incremental, events/sessions)
- [ ] Google Ads connector (campaigns, ad groups, metrics)
- [ ] Google Search Console connector (queries, pages)
- [ ] GitHub connector (repos, commits, PRs, issues)
- [ ] Bronze layer tables for all connectors
- [ ] Silver models (dbt or SQL scripts)
- [ ] Basic Gold views for marketing domain
- [ ] Superset dashboards (marketing overview)

**Key Work**:
```
connectors/
├── google/
│   ├── ga4/
│   │   ├── connector.py
│   │   ├── spec.yaml
│   │   └── streams/
│   │       ├── events.py
│   │       └── sessions.py
│   ├── google_ads/
│   │   ├── connector.py
│   │   └── spec.yaml
│   └── search_console/
│       ├── connector.py
│       └── spec.yaml
├── devops/
│   └── github/
│       ├── connector.py
│       └── spec.yaml

configs/connectors/
├── prod_ga4.yaml
├── prod_google_ads.yaml
├── prod_gsc.yaml
└── prod_github.yaml

sql/models/
├── bronze/
│   └── (auto-generated from connectors)
├── silver/
│   ├── ga4_sessions.sql
│   ├── ga4_events.sql
│   └── github_commits.sql
└── gold/
    └── gold_marketing_campaigns.sql
```

**Success Criteria**:
- [ ] All 4 connectors pass CI validation
- [ ] Incremental syncs working with cursor persistence
- [ ] Bronze → Silver → Gold pipeline functional
- [ ] Superset dashboard shows live marketing data
- [ ] 95% success rate on scheduled syncs

---

### Phase 2: Odoo + Finance Integration

**Objective**: Integrate Odoo CE/OCA data and build finance/retail analytics.

**Deliverables**:
- [ ] Odoo CE connector (Postgres direct + optional API)
- [ ] YouTube Analytics connector
- [ ] BigQuery export connector
- [ ] Finance Silver models (journal entries, invoices)
- [ ] Retail Silver models (sales, inventory)
- [ ] Gold views for finance domain
- [ ] Odoo CE dashboards via FDW/views

**Key Work**:
```
connectors/
├── odoo/
│   ├── connector.py           # Postgres-based extraction
│   ├── spec.yaml
│   └── streams/
│       ├── account_move.py
│       ├── account_invoice.py
│       ├── sale_order.py
│       └── stock_move.py
├── google/
│   ├── youtube_analytics/
│   └── bigquery_export/

sql/models/
├── silver/
│   ├── odoo_journal_entries.sql
│   ├── odoo_invoices.sql
│   └── odoo_sales.sql
└── gold/
    ├── gold_finance_general_ledger.sql
    ├── gold_finance_ar_aging.sql
    └── gold_retail_sales_summary.sql
```

**Success Criteria**:
- [ ] Odoo connector extracts all core finance tables
- [ ] Finance PPM data available in Gold layer
- [ ] Odoo CE can query Gold views via FDW
- [ ] Finance dashboards operational

---

### Phase 3: Agent/MCP Integration

**Objective**: Enable AI agents to manage connectors programmatically.

**Deliverables**:
- [ ] MCP server for connector operations
- [ ] MCP tools: list, create, run, status, logs
- [ ] n8n workflow templates for sync triggers
- [ ] Pulser agent integration
- [ ] Agent-triggered pipeline examples

**Key Work**:
```
mcp/servers/connector-mcp-server/
├── src/
│   ├── index.ts
│   ├── tools/
│   │   ├── list.ts
│   │   ├── create.ts
│   │   ├── run.ts
│   │   ├── status.ts
│   │   └── logs.ts
│   └── supabase-client.ts
├── package.json
└── README.md

n8n/workflows/
├── connector-sync-complete.json
└── connector-failure-alert.json
```

**Success Criteria**:
- [ ] MCP tools functional and documented
- [ ] Agent can trigger sync and retrieve results
- [ ] n8n webhooks fire on sync events
- [ ] 50% of syncs triggered via API/MCP

---

### Phase 4: Connector Catalog Expansion

**Objective**: Expand connector catalog and establish community patterns.

**Deliverables**:
- [ ] Vercel connector
- [ ] Supabase connector
- [ ] DigitalOcean connector
- [ ] Generic HTTP connector
- [ ] Generic JDBC connector
- [ ] Connector contribution guide
- [ ] Recipe documentation for common stacks

**Key Work**:
```
connectors/
├── infra/
│   ├── vercel/
│   ├── digitalocean/
│   └── supabase/
├── generic/
│   ├── http/
│   └── jdbc/

docs/
├── CONTRIBUTING.md
├── recipes/
│   ├── google-to-superset.md
│   ├── odoo-to-bi.md
│   └── devops-dashboard.md
```

**Success Criteria**:
- [ ] 10+ production-ready connectors
- [ ] External contributors can add connectors
- [ ] 3+ documented recipes

---

## 3. Dependency Tree

```
Phase 0: Foundation
├── Supabase Control Plane
│   ├── connector_definitions
│   ├── connector_instances
│   ├── connector_runs
│   └── connector_state
├── Core Framework
│   ├── base_connector.py
│   ├── scheduler.py
│   └── worker.py
└── CI Pipeline
    ├── YAML validation
    └── Linting/tests

Phase 1: Google + DevOps
├── [Depends on Phase 0]
├── GA4 Connector
├── Google Ads Connector
├── GSC Connector
├── GitHub Connector
├── Bronze Layer
├── Silver Models
└── Gold Views

Phase 2: Odoo + Finance
├── [Depends on Phase 1]
├── Odoo Connector
├── YouTube Connector
├── Finance Silver
└── Finance Gold

Phase 3: MCP Integration
├── [Depends on Phase 1]
├── MCP Server
├── MCP Tools
└── n8n Workflows

Phase 4: Catalog Expansion
├── [Depends on Phase 1, 3]
├── Additional Connectors
└── Documentation
```

---

## 4. Risk Mitigation

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| Google API quota limits | High | Implement quota tracking, request increases | Data Eng |
| OAuth complexity | Medium | Use existing OAuth libraries, test flows | Data Eng |
| Schema drift in sources | Medium | Schema version tracking, automated alerts | Data Eng |
| Worker scaling issues | Medium | Queue-based architecture from start | Platform |
| Agent integration delays | Low | MCP server can be parallel workstream | AI Team |

---

## 5. Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Connector Runtime | Python 3.10+ | Ecosystem, Google SDK support |
| Scheduler | APScheduler / Celery | Proven, Postgres-backed |
| Queue | Redis / Postgres | Simple, reliable |
| Control Plane | Supabase (Postgres) | Existing infrastructure |
| Object Storage | DO Spaces / S3 | Cost-effective, S3-compatible |
| Transforms | dbt Core / SQL | Open source, GitOps friendly |
| BI | Superset | Existing infrastructure |
| MCP Server | TypeScript | MCP ecosystem standard |

---

## 6. Success Criteria Summary

| Phase | Key Metric | Target |
|-------|------------|--------|
| Phase 0 | Environment ready | Scheduler + worker running |
| Phase 1 | Core connectors | 4 connectors, 95% success rate |
| Phase 2 | Odoo integration | Finance data in Gold layer |
| Phase 3 | Agent adoption | 50% API-triggered syncs |
| Phase 4 | Catalog growth | 10+ connectors |

---

## 7. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-01-25 | IPAI Team | Initial plan |
