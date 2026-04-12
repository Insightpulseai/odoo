# ADR-001: Fabric vs Databricks mirror for analytics/runtime continuity

## Status
Proposed

## Context
Current assessment evidence identifies an unresolved decision between:
1. Upgrading Fabric capacity (F2, ~$730/mo)
2. Migrating the Odoo ERP Mirror + Power BI analytics path to Databricks Gold layer

This decision materially affects:
- Cost optimization score (WAF 42%)
- Reliability score (WAF 63%)
- Commercial readiness evidence (SaaS 38%)

Current state: `fcipaidev` Fabric workspace on trial. Trial expires ~2026-05-20.

## Decision deadline
2026-05-20

## Options

### Option A — Keep Fabric and upgrade to F2
- Pros: Power BI native integration, existing Odoo Mirror pipeline, OneLake for lakehouse
- Cons: ~$730/mo recurring, Fabric GA maturity still evolving, single-region
- Monthly cost impact: +$730
- Operational dependencies: Fabric mirroring pipeline, Power BI workspace
- Exit criteria: Mirror lag < 1h, Power BI OKR dashboard renders from live data

### Option B — Migrate mirror to Databricks Gold layer
- Pros: Already have `dbw-ipai-dev` with SQL Warehouse, Unity Catalog governance, no Fabric dependency
- Cons: Requires rebuilding mirror pipeline in DLT, Power BI connects via Databricks SQL endpoint instead of Fabric
- Monthly cost impact: Included in existing Databricks commitment (DBU-based)
- Operational dependencies: DLT pipeline, Databricks SQL endpoint, Power BI gateway
- Exit criteria: Gold layer tables match Odoo schema, Power BI connects via SQL endpoint

## Decision
TBD

## Consequences
- Required infra changes: depends on option
- Data migration changes: Odoo Mirror pipeline rebuild (Option B) or capacity upgrade (Option A)
- Reporting / BI impact: Power BI data source changes if Option B
- Rollback path: Option A is reversible (downgrade capacity). Option B requires keeping Fabric as hot standby during migration.

## Owner
Jake Tolentino

## Evidence
- Assessment evidence pack: docs/evidence/20260413-0100/assessments/
- Fabric workspace: `fcipaidev` in `rg-ipai-dev-odoo-data`
- Databricks workspace: `dbw-ipai-dev`, SQL Warehouse `e7d89eabce4c330c`
