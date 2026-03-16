# IPAI Data Connectors — Task Checklist

> **Related Docs**: [constitution.md](constitution.md) | [prd.md](prd.md) | [plan.md](plan.md)

---

## Phase 0: Foundation & Sandbox

### Spec Kit
- [x] Create constitution.md
- [x] Create prd.md
- [x] Create plan.md
- [x] Create tasks.md

### Repository Structure
- [ ] Create `connectors/` directory structure
- [ ] Create `connectors/core/base_connector.py`
- [ ] Create `connectors/core/scheduler.py`
- [ ] Create `connectors/core/worker.py`
- [ ] Create `connectors/core/state_manager.py`
- [ ] Create `connectors/destinations/postgres.py`
- [ ] Create `connectors/destinations/object_storage.py`
- [ ] Create `connectors/utils/auth.py`
- [ ] Create `connectors/utils/retry.py`
- [ ] Create `connectors/utils/logging.py`
- [ ] Create `configs/connectors/` directory
- [ ] Create `sql/models/bronze/` directory
- [ ] Create `sql/models/silver/` directory
- [ ] Create `sql/models/gold/` directory

### Supabase Control Plane
- [ ] Create `connectors` schema in Supabase
- [ ] Create `connector_definitions` table
- [ ] Create `connector_instances` table
- [ ] Create `connector_runs` table
- [ ] Create `connector_state` table
- [ ] Configure Supabase Vault for secrets
- [ ] Create RPC function `enqueue_connector_job`
- [ ] Create RPC function `claim_connector_job`
- [ ] Create RPC function `complete_connector_job`
- [ ] Create RPC function `fail_connector_job`
- [ ] Configure RLS policies on control plane tables

### Docker Environment
- [ ] Create `docker/Dockerfile.connector-worker`
- [ ] Add connector services to `docker-compose.yml`
- [ ] Configure scheduler container
- [ ] Configure worker container
- [ ] Test local Docker environment

### CI Pipeline
- [ ] Create YAML spec JSON schema
- [ ] Create CI workflow for connector validation
- [ ] Add linting checks (black, isort, flake8)
- [ ] Add type checking (mypy)
- [ ] Add unit test runner
- [ ] Add dry-run sync validation

---

## Phase 1: Google + DevOps Core

### GA4 Connector
- [ ] Create `connectors/google/ga4/spec.yaml`
- [ ] Create `connectors/google/ga4/connector.py`
- [ ] Implement events stream
- [ ] Implement sessions stream
- [ ] Implement incremental sync with cursors
- [ ] Add unit tests
- [ ] Add integration tests with sandbox

### Google Ads Connector
- [ ] Create `connectors/google/google_ads/spec.yaml`
- [ ] Create `connectors/google/google_ads/connector.py`
- [ ] Implement campaigns stream
- [ ] Implement ad_groups stream
- [ ] Implement metrics stream
- [ ] Add unit tests

### Google Search Console Connector
- [ ] Create `connectors/google/search_console/spec.yaml`
- [ ] Create `connectors/google/search_console/connector.py`
- [ ] Implement queries stream
- [ ] Implement pages stream
- [ ] Add unit tests

### GitHub Connector
- [ ] Create `connectors/devops/github/spec.yaml`
- [ ] Create `connectors/devops/github/connector.py`
- [ ] Implement repos stream
- [ ] Implement commits stream
- [ ] Implement pull_requests stream
- [ ] Implement issues stream
- [ ] Add unit tests

### Bronze Layer
- [ ] Create `raw_ga4_events` table
- [ ] Create `raw_ga4_sessions` table
- [ ] Create `raw_google_ads_campaigns` table
- [ ] Create `raw_gsc_queries` table
- [ ] Create `raw_github_commits` table
- [ ] Create `raw_github_pull_requests` table

### Silver Layer
- [ ] Create `sql/models/silver/ga4_sessions.sql`
- [ ] Create `sql/models/silver/ga4_events.sql`
- [ ] Create `sql/models/silver/google_ads_campaigns.sql`
- [ ] Create `sql/models/silver/github_commits.sql`

### Gold Layer
- [ ] Create `sql/models/gold/gold_marketing_campaigns.sql`
- [ ] Create `sql/models/gold/gold_marketing_traffic.sql`

### Dashboards
- [ ] Create Superset dataset for marketing data
- [ ] Create marketing overview dashboard
- [ ] Create traffic analytics dashboard

---

## Phase 2: Odoo + Finance Integration

### Odoo Connector
- [ ] Create `connectors/odoo/spec.yaml`
- [ ] Create `connectors/odoo/connector.py`
- [ ] Implement account_move stream
- [ ] Implement account_invoice stream
- [ ] Implement sale_order stream
- [ ] Implement stock_move stream
- [ ] Implement res_partner stream
- [ ] Add unit tests

### YouTube Analytics Connector
- [ ] Create `connectors/google/youtube_analytics/spec.yaml`
- [ ] Create `connectors/google/youtube_analytics/connector.py`
- [ ] Implement channel_stats stream
- [ ] Implement video_stats stream

### BigQuery Export Connector
- [ ] Create `connectors/google/bigquery_export/spec.yaml`
- [ ] Create `connectors/google/bigquery_export/connector.py`

### Finance Models
- [ ] Create `sql/models/silver/odoo_journal_entries.sql`
- [ ] Create `sql/models/silver/odoo_invoices.sql`
- [ ] Create `sql/models/silver/odoo_sales.sql`
- [ ] Create `sql/models/gold/gold_finance_general_ledger.sql`
- [ ] Create `sql/models/gold/gold_finance_ar_aging.sql`
- [ ] Create `sql/models/gold/gold_retail_sales_summary.sql`

### Odoo Integration
- [ ] Configure FDW from Odoo to Gold schema
- [ ] Create finance dashboard in Odoo
- [ ] Test end-to-end data flow

---

## Phase 3: Agent/MCP Integration

### MCP Server
- [ ] Create `mcp/servers/connector-mcp-server/` structure
- [ ] Implement `connector:list` tool
- [ ] Implement `connector:create` tool
- [ ] Implement `connector:run` tool
- [ ] Implement `connector:status` tool
- [ ] Implement `connector:logs` tool
- [ ] Add to `.claude/mcp-servers.json`
- [ ] Document MCP tools in README

### n8n Integration
- [ ] Create webhook endpoint for sync events
- [ ] Create `n8n/workflows/connector-sync-complete.json`
- [ ] Create `n8n/workflows/connector-failure-alert.json`
- [ ] Test webhook triggers

### Pulser Integration
- [ ] Define connector agent capabilities
- [ ] Create example pipeline workflow
- [ ] Document agent usage patterns

---

## Phase 4: Connector Catalog Expansion

### Additional Connectors
- [ ] Vercel connector
- [ ] Supabase connector
- [ ] DigitalOcean connector
- [ ] Generic HTTP connector
- [ ] Generic JDBC connector

### Documentation
- [ ] Create `connectors/CONTRIBUTING.md`
- [ ] Create `docs/recipes/google-to-superset.md`
- [ ] Create `docs/recipes/odoo-to-bi.md`
- [ ] Create `docs/recipes/devops-dashboard.md`
- [ ] Create connector development guide

---

## Ongoing

### Quality
- [ ] Maintain 80%+ test coverage
- [ ] Keep sync success rate ≥ 95%
- [ ] Review and rotate OAuth tokens quarterly

### Monitoring
- [ ] Set up alerting for failed syncs
- [ ] Create observability dashboard
- [ ] Monitor API quota usage

---

*Last Updated: 2026-01-25*
