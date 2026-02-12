# IPAI Databricks – Tasks

## M1: Foundations

### Schemas
- [ ] Create migration: `ipai_bronze_core` schema
- [ ] Create migration: `ipai_silver_core` schema
- [ ] Create migration: `ipai_gold_core` schema
- [ ] Create migration: `ipai_platinum_core` schema
- [ ] Create migration: `ipai_bronze_erp` schema
- [ ] Create migration: `ipai_silver_erp` schema
- [ ] Create migration: `ipai_gold_erp` schema
- [ ] Create migration: `ipai_bronze_devops` schema
- [ ] Create migration: `ipai_gold_devops` schema

### Infrastructure
- [ ] Configure Supabase project extensions (pgvector, pg_cron)
- [ ] Set up Supabase Vault secrets structure
- [ ] Create DO Spaces bucket for blob storage
- [ ] Configure Vercel project for apps

### CI/CD
- [ ] Add Spec Kit validation to CI workflow
- [ ] Implement migration dry-run on scratch DB
- [ ] Add lint gates for connector code

---

## M2: Core Connectors

### Framework
- [ ] Create `ipai_connector_config` table migration
- [ ] Create `ipai_connector_run` table migration
- [ ] Implement `run_connector()` RPC
- [ ] Wire scheduler (n8n or Supabase cron)

### Odoo CE Connector
- [ ] Implement Edge Function: `ipai-connector-odoo`
- [ ] Support full sync mode
- [ ] Support incremental sync (timestamp-based)
- [ ] Map Odoo models → bronze tables:
  - [ ] `account.move` → `ipai_bronze_erp.invoices`
  - [ ] `account.move.line` → `ipai_bronze_erp.journal_entries`
  - [ ] `res.partner` → `ipai_bronze_erp.partners`
  - [ ] `project.project` → `ipai_bronze_erp.projects`

### GitHub Connector
- [ ] Implement Edge Function: `ipai-connector-github`
- [ ] Sync repositories metadata
- [ ] Sync issues and PRs
- [ ] Sync workflow runs
- [ ] Implement webhook receiver for real-time events

### File Connector
- [ ] Implement Edge Function: `ipai-connector-files`
- [ ] Support CSV parsing
- [ ] Support JSON parsing
- [ ] Support Parquet parsing (via duckdb-wasm or similar)
- [ ] Schema inference logic

---

## M3: Apps v1

### App Registry
- [ ] Create `ipai_app_registry` table migration
- [ ] Implement app deployment pipeline (Vercel)
- [ ] Configure Supabase Auth for apps

### Finance Command Center
- [ ] Create gold views: P&L, balance sheet, cashflow
- [ ] Build Next.js app: `ipai-finance-command-center`
- [ ] Implement AR/AP aging dashboard
- [ ] Add AI reconciliation suggestions feature

### DevOps Health App
- [ ] Create gold views: spec compliance, CI metrics
- [ ] Build Next.js app: `ipai-devops-health`
- [ ] Implement deployment timeline view
- [ ] Add CI status overview

---

## M4: Agent Governance

### Agent Registry
- [ ] Create `ipai_agent` table migration
- [ ] Create `ipai_agent_run` table migration
- [ ] Implement agent registration RPC
- [ ] Implement run logging RPC

### MCP Integration
- [ ] Configure Supabase MCP server tools
- [ ] Define tool → schema mappings
- [ ] Implement data scope enforcement

### Policies
- [ ] Add RLS policies for agent access patterns
- [ ] Implement cost tracking logic
- [ ] Wire cost alerts to n8n/Mattermost

---

## M5: Observability & Hardening

### Observability
- [ ] Set up connector metrics dashboard
- [ ] Set up agent metrics dashboard
- [ ] Set up app availability dashboard

### Alerting
- [ ] Define SLO targets in config
- [ ] Implement error budget tracking
- [ ] Wire alerts to Mattermost/Slack

### Security
- [ ] Audit all RLS policies
- [ ] Implement Vault secrets rotation schedule
- [ ] Conduct security review / pen test

### Documentation
- [ ] Write connector runbooks
- [ ] Write agent governance runbooks
- [ ] Write incident response playbooks
- [ ] Document architecture decisions (ADRs)

---

## Future / Backlog

- [ ] Additional connectors: Figma, Slack, HubSpot, Mail
- [ ] dbt-style transformation layer
- [ ] Advanced vector embeddings for AI features
- [ ] Multi-tenant isolation patterns
- [ ] Cost optimization dashboards

---

*Last updated: 2026-01-25*
