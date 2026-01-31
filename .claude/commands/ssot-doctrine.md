# SSOT Doctrine Command

Apply the Supabase SSOT / Odoo SoR doctrine to evaluate and enforce architectural boundaries.

## Usage

Invoke with `/project:ssot-doctrine` to:
1. Verify data ownership boundaries
2. Check secret management compliance
3. Validate orchestration patterns
4. Ensure AI agent access rules

## Core Doctrine

**Supabase** = Single Source of Truth (SSOT)
- Platform state, analytics, AI, secrets, orchestration

**Odoo** = System of Record (SoR)
- Business transactions, compliance, auditable records

## Quick Rules

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

## Enforcement Actions

When this command is invoked:

### 1. Data Ownership Check
- Verify no business transactions written to Supabase
- Verify no analytics/AI data written to Odoo
- Check for data duplication without justification

### 2. Secret Audit
- Scan for hardcoded secrets in codebase
- Check Odoo models for secret storage
- Verify Supabase Vault usage

### 3. Orchestration Review
- Verify no Odoo cron jobs (should be pg_cron/n8n)
- Check scheduled job locations
- Validate webhook configurations

### 4. AI Access Review
- Verify agent default reads from Supabase
- Check for unauthorized Odoo access
- Validate output storage schemas

## Reference

Full specification: `spec/supabase-ssot-doctrine/`
Architecture doc: `docs/architecture/SOURCE_OF_TRUTH.md`
Agent prompt: `spec/supabase-ssot-doctrine/agent-prompt.md`

## Violation Protocol

If doctrine violation detected:
1. **STOP** - Do not proceed with violating action
2. **EXPLAIN** - Document the specific violation
3. **PROPOSE** - Suggest compliant alternative
