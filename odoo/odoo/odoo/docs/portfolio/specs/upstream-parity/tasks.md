# Upstream Parity – Task Checklist

## Documentation Tasks

- [x] Create constitution.md with self-hosted stance
- [x] Create prd.md with capability goals
- [x] Create plan.md with implementation phases
- [x] Create tasks.md (this file)
- [x] Create docs/lakehouse/DATABRICKS_PARITY_MATRIX.md

## Odoo EE Parity Tasks

- [ ] Audit OCA 18.0 addons in use
- [ ] Map Odoo EE features to CE + OCA equivalents
- [ ] Document ipai_enterprise_bridge requirements
- [ ] Create ODOO_EE_PARITY_MATRIX.md

## Lakehouse Parity Tasks

- [ ] Set up Delta Lake storage layer
- [ ] Configure object storage (DO Spaces / S3)
- [ ] Implement medallion architecture
- [ ] Connect Supabase as warehouse endpoint
- [ ] Configure n8n orchestration jobs

## Ingestion Parity Tasks

- [ ] Inventory required connectors
- [ ] Build n8n connector templates
- [ ] Create Edge Function connector patterns
- [ ] Set up dbt-style transformations

## CI/Governance Tasks

- [ ] Add upstream-parity CI workflow
- [ ] Validate spec kit presence across repos
- [ ] Enforce LICENSE + SECURITY.md + CONTRIBUTING.md

## Status Legend

- [x] Complete
- [ ] Pending
- [~] In Progress
- [-] Blocked
