# Odoo Workspace OS — Constitution

> Non-negotiable architectural boundaries for the Odoo Workspace OS platform.

## Three Systems Rule

### System of Truth: Odoo CE 19
**Owns**: Master objects, projects, tasks, timesheets, expenses, approvals, accounting, budgets, invoices, audit trail.

- Odoo is the **sole authoritative source** for all transactional and financial data
- All business rules, workflows, and approvals execute inside Odoo
- No external system may write master data directly — all mutations route through Odoo APIs or UI

### System of Context: Workspace / AI Layer
**Owns**: Notes, summaries, document grounding, copilots, search, recommendations.

- Reads from Odoo (never writes master data)
- Provides intelligence overlay: summarization, search, recommendations, copilot interactions
- Stores AI-generated artifacts (summaries, embeddings, suggestions) in its own store
- May create draft records in Odoo (e.g., suggested expense entries) but human approval required

### System of Analytics: Data Plane (Databricks)
**Owns**: Portfolio analytics, close analytics, expense analytics, AI-ready marts.

- Read-only from Odoo's perspective — analytics derive from Odoo, never override
- Medallion architecture: Bronze (raw) → Silver (cleaned) → Gold (business) → Platinum (AI-ready)
- Unity Catalog governed, schema-on-read for bronze, schema-on-write for silver+

## Conflict Resolution
1. **Odoo always wins** — if Odoo says a PO is approved, it's approved regardless of what the AI layer thinks
2. **AI suggests, humans approve** — no autonomous writes to Odoo master data
3. **Analytics are derived** — never used as source of truth for operational decisions without Odoo confirmation

## Module Naming
All custom modules follow: `ipai_<domain>_<feature>`
- Config first → OCA second → ipai_* delta only when needed

## Technology Boundaries
- Odoo CE 19 + OCA (no Enterprise modules)
- PostgreSQL 16 (local, NOT Supabase)
- Supabase for external integrations only (n8n bridge, task bus)
- Databricks for all analytics workloads
