# Upstream Parity PRD

## Problem

We want Odoo EE-like business capability and Databricks-like lakehouse capability **without purchasing Odoo EE or Databricks SaaS**, by running a fully self-hosted stack built from open-source components and our own infrastructure. At the same time, we must respect all applicable open-source licenses (LGPL/AGPL/Apache/MIT/etc.) and keep the architecture maintainable and auditable.

## Goals

1. **Odoo EE Parity (Self-hosted, OSS-based)**
   - Replace all EE-only features with:
     - Odoo CE core.
     - OCA addons (18.0) aligned with OCA guidelines.
     - Minimal ipai_* bridge modules (e.g., ipai_enterprise_bridge) instead of scattered custom addons.
   - Follow OCA governance, coding, and tooling patterns.

2. **Lakehouse / Databricks Parity (Self-hosted)**
   - Use Delta Lake + object storage + Postgres/Supabase + BI (Superset/Power BI) to reproduce core Lakehouse benefits:
     - ACID over the data lake.
     - Medallion architecture (bronze/silver/gold).
     - Jobs/orchestration via n8n + MCP tools.
   - No Databricks runtime or licensing is required; everything runs on your own infra.

3. **Ingestion / ELT Parity (Fivetran-style, Self-hosted)**
   - Model ingestion as:
     - Connectors (n8n + Edge Functions + MCP tools).
     - Transformations (dbt-style packages, inspired by Fivetran's public dbt packages where Apache-2.0 allows).
   - No managed Fivetran service is required; patterns and schemas are mirrored, not the closed-source product.

4. **Org-Level Best Practices**
   - Adopt architectural and repo patterns from:
     - Supabase: monorepo, declarative DB, docs + AI prompts, strong SECURITY/CONTRIBUTING.
     - Vercel: templates, AI gateway patterns, examples-first DX.
     - Odoo + OCA: CONTRIBUTING, addon standards, pre-commit and towncrier-based changelogs.
     - n8n: env-driven self-hosting with clear license boundaries.
   - Ensure InsightPulseAI behaves like a first-class OSS org: predictable layouts, clear governance, automation-by-default.
