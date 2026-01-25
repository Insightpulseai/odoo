# Upstream Parity – Constitution

Non-negotiables:

- There is **no commercial SaaS license ceiling** for Databricks or Odoo EE, because all capabilities are implemented via self-hosted, open-source components on our own infrastructure.
- Odoo EE parity is achieved via Odoo CE + OCA + a single IPAI bridge layer (ipai_enterprise_bridge), never by copying EE code.
- Lakehouse parity is achieved via open components:
  - Delta Lake (Apache-2.0) as the storage/transaction layer.
  - Postgres/Supabase as the warehouse and control plane.
  - Object storage (e.g., DigitalOcean Spaces, S3-compatible) as the data lake.
  - Superset/BI tools for analytics.
  - n8n + MCP for orchestration and automation.
- Ingestion/ELT parity (Fivetran-style) is implemented via:
  - Connectors (n8n, Edge Functions, MCP tools).
  - dbt-style transformations, inspired by public Fivetran dbt packages.

License principles (still mandatory):

- We only reuse code where upstream licenses permit:
  - Odoo CE: LGPL-3.0
  - OCA addons: typically AGPL-3.0 – implies network copyleft for derivatives.
  - Supabase: Apache-2.0
  - Vercel examples: commonly MIT
  - Delta Lake: Apache-2.0
  - n8n: Fair-Code License
  - Fivetran dbt packages: Apache-2.0
  - MCP spec: Apache-2.0
- Org-wide patterns (structure, automation, docs, CI) are always safe to reuse; code reuse must be explicitly checked against upstream licenses.
- All InsightPulseAI repos must carry:
  - Spec Kit bundle (constitution/prd/plan/tasks)
  - LICENSE + SECURITY.md + CONTRIBUTING.md
  - At least one CI workflow enforcing tests + spec kit presence + changelog rules.
