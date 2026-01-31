# Source of Truth – Architectural Doctrine

## Canonical Repository

Primary repository: https://github.com/jgtolentino/odoo-ce

Do not reference deprecated repositories in scripts/docs/workflows.

---

## SSOT/SoR Doctrine

### Core Principle

The InsightPulseAI platform operates with a strict separation of concerns:

| System | Role | Owns |
|--------|------|------|
| **Supabase** | Single Source of Truth (SSOT) | Platform state, analytics, AI, secrets, orchestration |
| **Odoo** | System of Record (SoR) | Business transactions, compliance, auditable records |

These roles are **non-overlapping** and must not be confused.

### Data Ownership Matrix

| Data Domain | Owner | Never Store In |
|-------------|-------|----------------|
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
| Secrets/credentials | Supabase Vault | Odoo, Git, env files |

### Write Rules

```
Supabase MAY write:     Sync status, shadow tables, AI annotations, derived fields
Supabase MUST NOT:      Business transactions, ERP data

Odoo MAY write:         Business transactions, compliance records
Odoo MUST NOT:          Analytics, platform state, secrets
```

### Secret Management

**Supabase Vault** is the canonical secret store:
- GitHub App credentials
- API keys (OpenAI, Anthropic, etc.)
- Webhook secrets
- Scheduler credentials
- Agent credentials

**Forbidden locations for secrets:**
- Odoo models/database
- Git repository (including .env committed files)
- Hardcoded in source code

### Orchestration

| Component | Platform |
|-----------|----------|
| Scheduled jobs (pg_cron) | Supabase |
| Edge Functions | Supabase |
| Webhooks | Supabase / n8n |
| Workflow automation | n8n |
| Business logic | Odoo |

**Odoo is never used as a scheduler, job runner, or secret vault.**

### AI & Agent Access

| Access Type | Default Source |
|-------------|----------------|
| Agent reads | Supabase |
| Agent writes | Supabase (ops.*, ai.*, audit.*, analytics.*) |
| Odoo access | Requires explicit permission |
| Agent memory | Supabase |

### Conflict Resolution

When data exists in both systems:
1. **Transactional truth** → Odoo wins
2. **Analytical truth** → Supabase wins
3. **Secrets** → Always Supabase Vault
4. **Default** → Agents defer to Supabase

---

## Full Specification

See: `spec/supabase-ssot-doctrine/`

| Document | Purpose |
|----------|---------|
| `constitution.md` | Non-negotiable rules |
| `prd.md` | Product requirements |
| `plan.md` | Implementation plan |
| `tasks.md` | Task checklist |
| `agent-prompt.md` | Copy-paste agent prompts |

---

## Quick Reference for Agents

```
[10-RULE SSOT DOCTRINE]
1. Supabase = platform truth, Odoo = business truth
2. Financial/HR/CRM records → Odoo only
3. Analytics/AI/agents → Supabase only
4. Secrets → Supabase Vault only
5. Scheduled jobs → pg_cron or n8n, never Odoo
6. AI reads Supabase by default, Odoo with permission
7. AI outputs → Supabase schemas (ops, ai, audit, analytics)
8. Odoo canonical when data exists in both
9. Never hardcode secrets or store in Odoo
10. Violation → STOP, EXPLAIN, PROPOSE alternative
```

---

*Last updated: 2026-01-31*
