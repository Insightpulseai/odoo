# Platform Governance: SSOT & SoR Architecture

This document defines the authoritative roles and boundaries for Supabase and Odoo in this platform.

## Core Principle

| System | Role | Description |
|--------|------|-------------|
| **Supabase** | Single Source of Truth (SSOT) | Platform state, analytics, AI data, orchestration, secrets |
| **Odoo** | System of Record (SoR) | Business transactions, accounting, HR, legal records |

These roles are **non-overlapping** and must not be confused.

---

## 1. Data Ownership

### Odoo Owns (System of Record)

- Financial records (invoices, bills, payments)
- HR records (employees, contracts, payroll)
- Inventory transactions
- CRM entities (customers, vendors, leads)
- Sales and purchase orders
- Accounting journal entries

### Supabase Owns (Single Source of Truth)

- Analytical projections and aggregations
- Metrics, KPIs, dashboards
- AI embeddings, vectors, summaries
- Cross-system state
- Agent memory and context
- Audit findings and recommendations
- Deployment and platform metadata
- Operational telemetry (`ops.*` schema)

### Conflict Resolution

If data exists in both systems:
1. **Odoo is canonical** for business truth
2. **Supabase holds replicated, transformed, or summarized versions** (via `mirror.*` schema)

---

## 2. Write Rules

| Action | Allowed | Not Allowed |
|--------|---------|-------------|
| Write business data to Odoo | Via `odoo-proxy` Edge Function only | Direct SQL, dblink, FDW |
| Write analytics to Supabase | Directly via service role | N/A |
| Write secrets | Supabase Vault only | .env files, compose, git |
| Store AI outputs | Supabase `ops.*`, `ai.*`, `analytics.*` | Odoo models |

### Key Constraints

- **NEVER** write business truth directly into Odoo unless explicitly instructed
- **NEVER** treat Supabase as a transactional ERP
- Odoo writes are **strictly controlled, explicit, and auditable**

---

## 3. Secret Management

### Supabase Vault (Default)

Store in Vault:
- GitHub App credentials (ID, private key)
- API keys for external services
- Webhook secrets
- Scheduler credentials
- Database connection strings

### Edge Function Secrets (Exception)

Use only for:
- Runtime-only values that cannot be fetched from Vault
- Short-lived execution secrets

### Prohibited

- Hardcoded secrets in code
- Secrets committed to git
- Secrets stored in Odoo models
- Secrets duplicated across systems without justification

---

## 4. Orchestration & Automation

### Supabase is the Orchestration Plane

- `pg_cron` scheduled jobs
- Edge Functions for business logic
- Webhooks and event handlers
- Repository audits
- Deployment checks
- AI agent coordination

### Odoo is NOT

- A scheduler or job runner
- A secret vault
- An orchestration engine

---

## 5. AI & Agent Access

| Access Type | Default Behavior |
|-------------|------------------|
| Read | Agents read from Supabase |
| Write | Agents write to Supabase (`ops.*`, `ai.*`, `audit.*`) |
| Odoo Access | Agents do NOT read raw Odoo tables unless explicitly allowed |

---

## 6. Deployment & CI/CD

- Supabase schema, functions, and policies are managed as code
- Supabase is the reference point for:
  - Environment state
  - Drift detection
  - Repository hardening
  - Platform audits
- Odoo deployments are treated as application releases, not platform state

---

## 7. Decision Matrix

| Scenario | Decision |
|----------|----------|
| Transactional data conflict | Odoo wins |
| Analytical data conflict | Supabase wins |
| Where to store secrets | Supabase Vault |
| Where to schedule jobs | Supabase pg_cron |
| Where to store AI outputs | Supabase |
| How to write to Odoo | Edge Function proxy only |

---

## Agent Prompt (for AI/Automation)

```
[DEFAULT BEHAVIOR]
- Assume Supabase is authoritative for platform decisions
- Assume Odoo is authoritative for business records
- Enforce strict boundaries
- Prefer automation, idempotency, and auditability
- Never merge responsibilities unless explicitly instructed

[FAILURE MODE]
If instructions violate this model:
1. STOP
2. EXPLAIN the violation
3. PROPOSE a compliant alternative
```

---

## 8. Production Hardening Checklist

### Platform (Supabase)

| Item | Priority | Status |
|------|----------|--------|
| RLS enabled on all `ops.*` tables | Critical | |
| RLS enabled on all `advisor.*` tables | Critical | |
| RLS enabled on all `mirror.*` tables | Critical | |
| JWT role claims enforced in Edge Functions | Critical | |
| Audit logs (`ops.events`) are append-only | High | |
| Secrets stored in Supabase Vault only | Critical | |
| Service role key never exposed to frontend | Critical | |
| Database connection pooling configured | Medium | |
| Query timeouts set (statement_timeout) | Medium | |

### Odoo (DigitalOcean)

| Item | Priority | Status |
|------|----------|--------|
| Database accessible only via private network | Critical | |
| Reverse proxy (nginx) with TLS termination | Critical | |
| Nightly backups verified (test restore) | High | |
| Worker limits configured (`--workers`, `--max-cron-threads`) | High | |
| Fail2ban or equivalent for SSH | Medium | |
| API endpoints rate-limited | Medium | |
| HMAC verification enabled on all `/ipai/` routes | Critical | |

### CI/CD (GitHub Actions)

| Item | Priority | Status |
|------|----------|--------|
| Preview environments on every PR (Vercel) | High | |
| Staging environment validated before production | Critical | |
| Promote via git tags only | Medium | |
| Evidence pack per deploy (logs, health checks) | High | |
| Secrets in GitHub Secrets, not in code | Critical | |
| Dependabot enabled for security updates | Medium | |

### Vercel

| Item | Priority | Status |
|------|----------|--------|
| Security headers enabled (nosniff, DENY framing) | High | |
| Health gate after deployment (`/api/health`) | Critical | |
| Environment variables isolated per environment | High | |
| No direct database access from frontend | Critical | |
| Edge Functions verified with test cases | Medium | |

### Secrets Management

| Item | Priority | Status |
|------|----------|--------|
| No secrets in git history | Critical | |
| `.env*` files in `.gitignore` | Critical | |
| All Edge Functions fetch from Vault | High | |
| Rotation schedule documented | Medium | |
| Break-glass procedure documented | High | |

---

## Related Documentation

- [supabase/ARCHITECTURE.md](../supabase/ARCHITECTURE.md) - Technical architecture details
- [docs/CANONICAL_ARCHITECTURE.md](./CANONICAL_ARCHITECTURE.md) - Combined platform architecture
- [docs/PHASE1_CHECKLIST.md](./PHASE1_CHECKLIST.md) - Implementation checklist
- [docs/CI_SUPABASE_SECRETS.md](./CI_SUPABASE_SECRETS.md) - CI/CD secrets setup
- [docs/COPILOT_RULES.md](./COPILOT_RULES.md) - Quick reference for AI agents
- [Supabase Vault Docs](https://supabase.com/docs/guides/database/vault)
- [Supabase Scheduling Docs](https://supabase.com/docs/guides/functions/schedule-functions)
