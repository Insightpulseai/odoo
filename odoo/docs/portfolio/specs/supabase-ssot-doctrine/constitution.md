# Supabase SSOT Doctrine – Constitution

## Non-Negotiable Rules

### 1. Single Source of Truth (SSOT) vs System of Record (SoR)

**Supabase** is the **Single Source of Truth (SSOT)** for:
- Platform state and operational metadata
- Analytics-ready data and derived datasets
- AI-accessible data (embeddings, vectors, summaries)
- Cross-system orchestration state
- Secrets used by automation, schedulers, and agents
- Agent memory and audit findings
- Deployment and infrastructure metadata

**Odoo** is the **System of Record (SoR)** for:
- Business transactions (invoices, bills, payments)
- Accounting, HR, CRM, Inventory records
- Legal, compliance, and auditable records
- Canonical operational workflows
- Customer, vendor, and contract entities

### 2. Data Ownership Boundaries

These roles are **NON-OVERLAPPING** and **MUST NOT** be confused.

| Domain | Owner | Never In |
|--------|-------|----------|
| Financial records | Odoo | Supabase |
| Invoices, bills, payments | Odoo | Supabase |
| HR records | Odoo | Supabase |
| Inventory transactions | Odoo | Supabase |
| CRM entities | Odoo | Supabase |
| Analytical projections | Supabase | Odoo |
| Aggregations, metrics, KPIs | Supabase | Odoo |
| Derived datasets | Supabase | Odoo |
| AI embeddings/vectors | Supabase | Odoo |
| Agent memory | Supabase | Odoo |
| Platform metadata | Supabase | Odoo |

### 3. Write Rules

- **NEVER** write business truth directly into Odoo unless explicitly instructed
- **NEVER** treat Supabase as a transactional ERP
- Supabase MAY write: sync status, shadow tables, AI annotations, derived fields
- Odoo writes are STRICTLY controlled, explicit, and auditable

### 4. Secret Management

- Supabase Vault is the DEFAULT secret store for:
  - GitHub App credentials
  - API keys
  - Webhook secrets
  - Scheduler credentials
  - Agent credentials
- Edge Function secrets are allowed ONLY for runtime-only values
- Secrets MUST NOT be:
  - Hardcoded
  - Committed to Git
  - Stored in Odoo models
  - Duplicated across systems without justification

### 5. Orchestration & Automation

- Supabase is the orchestration plane (pg_cron, Edge Functions, webhooks)
- Odoo is NEVER used as a scheduler, job runner, or secret vault
- All scheduled jobs run from Supabase or n8n, not Odoo

### 6. AI & Agent Access

- AI agents READ from Supabase by default
- AI agents DO NOT read raw Odoo tables unless explicitly allowed
- AI outputs are stored in Supabase schemas: `ops.*`, `ai.*`, `audit.*`, `analytics.*`

### 7. Conflict Resolution

When conflicts arise:
1. Odoo wins for transactional truth
2. Supabase wins for analytical truth
3. Secrets always live in Supabase Vault
4. Agents defer to Supabase unless explicitly instructed otherwise

## Violation Protocol

If instructions violate this model:
1. STOP
2. EXPLAIN the violation
3. PROPOSE a compliant alternative
