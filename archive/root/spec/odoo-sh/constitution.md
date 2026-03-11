# Constitution: Odoo.sh-Equivalent Platform

## Article 1: Purpose

This specification defines an **Odoo.sh-equivalent platform** for the InsightPulse AI monorepo, providing branch-driven development, staging, and production environments with deterministic builds, hot reload, and evidence-first operations.

**Goals:**
- Branch-driven lifecycle (dev → staging → production)
- Developer hot reload (`--dev=all` with debug assets)
- Staging neutralization (email/crons/integrations disabled by default)
- PR/branch ephemeral environments (Runbot-lite)
- Promotion workflow with CI gates
- Observability and evidence emission

**Non-Goals:**
- Rebuilding Odoo Enterprise SaaS platform features
- Manual UI-based operations (CLI/CI only)
- Multi-tenant infrastructure (single tenant per environment)

---

## Article 2: System Boundaries (SSOT/SOR)

### §2.1 System of Record (SOR)
**Odoo** is the canonical System of Record for:
- ERP ledger (accounting, invoices, payments)
- Operational data (CRM, projects, tasks, inventory)
- User authentication and permissions (Odoo's `res.users`)

**Immutability:** No external system may write to Odoo's SOR tables without Odoo's ORM mediation.

### §2.2 System of Truth (SSOT)
**Supabase** is the canonical System of Truth for:
- Control-plane metadata (deployment logs, build manifests, promotion history)
- Observability data (metrics, traces, evidence artifacts)
- Platform configuration (environment settings, feature flags)
- Task bus and workflow orchestration state

**Boundary Rule:** Supabase stores *how the platform operates*, not *what Odoo records*.

### §2.3 No Shadow Ledger
No external system (Supabase, n8n, or other) may maintain a duplicate/shadow copy of Odoo's transactional data. All reads from Odoo must be via:
- Odoo XML-RPC/JSON-RPC API
- PostgreSQL read replicas (read-only, no writes)
- Approved OCA connector modules

---

## Article 3: Environment Semantics

### §3.1 Three Canonical Environments
| Environment | Purpose | Data Source | Integrations | Odoo Stage |
|-------------|---------|-------------|--------------|------------|
| **dev** | Local development, hot reload | Fresh/anonymized DB | Neutralized (localhost) | `development` |
| **staging** | Pre-production testing, PR previews | Production snapshot (sanitized) | Neutralized (disabled) | `staging` |
| **production** | Live operations | Production DB | Enabled | `production` |

### §3.2 Environment Variable: `ODOO_STAGE`
All environments MUST set `ODOO_STAGE` to one of: `development`, `staging`, `production`.

**Usage:**
- Feature flags: `if os.getenv('ODOO_STAGE') == 'production':`
- Logging verbosity: verbose in dev, structured JSON in production
- External integrations: disabled unless `ODOO_STAGE=production`

### §3.3 Staging Neutralization (Hard Rule)
Staging environment MUST disable:
- **Email sending** (outgoing SMTP, use `mail.catchall` or mailhog)
- **Scheduled actions (crons)** (disable by default, manual trigger only)
- **External integrations** (Slack, n8n webhooks, payment gateways)
- **Production secrets** (use test API keys, dummy credentials)

**Enforcement:** CI validation MUST verify staging configuration has neutralization active.

---

## Article 4: Branch-Driven Lifecycle

### §4.1 Git Branch Mapping
| Branch Pattern | Environment | Build Trigger | Promotion Path |
|----------------|-------------|---------------|----------------|
| `feature/*`, `fix/*` | Ephemeral PR build | On PR creation/push | → staging (via PR merge to `main`) |
| `main` | Staging | On commit to main | → production (via manual promotion) |
| `production` | Production | On promotion merge | Terminal (no further promotion) |

### §4.2 Linear Promotion Rule
**Code MUST flow in this order:**
```
feature/branch → main (staging) → production
```

**Prohibited:**
- Direct commits to `production` branch
- Hotfixes bypassing staging (except documented emergency protocol)
- Cherry-picking from production back to main

### §4.3 PR Environment Lifecycle (Runbot-lite)
**Creation:** On PR open, create ephemeral environment:
- Unique subdomain: `pr-<number>-<slug>.dev.insightpulseai.com`
- Isolated database (copy of staging DB or fresh)
- Deploy branch code with staging neutralization

**Teardown:** On PR close/merge, destroy environment within 1 hour.

---

## Article 5: Deterministic Builds

### §5.1 Code + Config in Repo
All build inputs MUST be version-controlled:
- Python dependencies: `requirements.txt`, `pyproject.toml`
- Odoo addons: `addons/` directory structure
- Configuration: `.env.template`, `odoo.conf.template`
- Infrastructure: `Dockerfile`, `docker-compose.yml`, CI workflows

**Prohibited:** Manual configuration changes on servers, undocumented environment variables.

### §5.2 Addons Path Invariants
**Canonical addons path order:**
```
--addons-path=/workspaces/odoo/addons/odoo,/workspaces/odoo/addons/oca,/workspaces/odoo/addons/ipai,/workspaces/odoo/addons/ipai_meta
```

**Enforcement:** CI MUST validate this order matches across:
- `docker-compose.yml`
- `.devcontainer/devcontainer.json`
- Deployment manifests
- Documentation

See: `docs/architecture/ADDONS_STRUCTURE_BOUNDARY.md`

### §5.3 Build Reproducibility
Given the same git SHA, builds MUST produce byte-identical artifacts (allowing for timestamps in logs).

**Verification:** CI stores build manifests in Supabase `ops.builds` table with content hashes.

---

## Article 6: Evidence-First Operations

### §6.1 Build Metadata
Every build MUST emit:
- Git SHA, branch, commit message, author
- Build timestamp (ISO8601 with timezone)
- Docker image SHA256 digest
- Dependency lock file hashes (`requirements.txt.lock`)

**Storage:** Supabase table `ops.builds`

### §6.2 Deployment Logs
Every deployment MUST emit:
- Deployment timestamp, environment, deployed SHA
- Migration scripts executed (Odoo module upgrades)
- Health check results (HTTP 200, database connectivity)
- Rollback metadata (previous SHA for quick revert)

**Storage:** Supabase table `ops.deployments`

### §6.3 Evidence Artifacts
**Canonical location:** `web/docs/evidence/<YYYYMMDD-HHMM+0800>/<topic>/logs/`

All operational actions (builds, deploys, migrations) MUST save:
- Full stdout/stderr logs
- Error traces
- Verification results

**Timezone:** Asia/Manila (UTC+08:00)

---

## Article 7: Security and Secrets

### §7.1 No Secrets in Git
**Prohibited:** Hardcoded passwords, API keys, tokens in any committed file.

**Allowed:**
- `.env.template` with placeholder values (`CHANGE_ME`, `REPLACE_WITH_REAL_KEY`)
- CI secrets via GitHub Actions encrypted secrets
- Runtime secrets via environment variables or secret managers

### §7.2 Client Data Isolation (RLS)
For any multi-client deployment, Supabase tables storing client-specific data MUST use Row-Level Security (RLS):
```sql
CREATE POLICY client_isolation ON ops.deployments
  USING (client_id = auth.jwt() ->> 'client_id');
```

---

## Article 8: Constraints and Compatibility

### §8.1 Worker Recycling Tolerance
Platform MUST assume Odoo workers are recycled after:
- 8192 requests processed
- 1 hour of uptime
- Memory usage > 512MB per worker

**Implication:** No in-memory state persistence across requests (use PostgreSQL or Redis).

### §8.2 Cron Timeout Limits
Scheduled actions (crons) MUST complete within:
- **Dev:** No timeout (for debugging)
- **Staging:** 10 minutes
- **Production:** 5 minutes

**Enforcement:** Odoo `ir.cron` records MUST set `interval_number` and `interval_type` accordingly.

### §8.3 Resource Constraints (Production)
| Resource | Limit | Rationale |
|----------|-------|-----------|
| Worker count | 4-8 workers | Balance concurrency vs. memory |
| Max request size | 50MB | File upload limit |
| Database connection pool | 20 connections | Avoid PostgreSQL max_connections |
| Log retention | 30 days | Supabase storage limits |

**Verification:** CI MUST validate production configuration matches these constraints.

---

## Non-Negotiables Summary

1. **SSOT/SOR Boundary:** Odoo = SOR (ledger), Supabase = SSOT (control-plane). No shadow ledger.
2. **Staging Neutralization:** Email/crons/integrations MUST be disabled in staging.
3. **Linear Promotion:** Code flows `feature → main → production` only.
4. **Deterministic Builds:** Same SHA = same build artifacts.
5. **Evidence Emission:** All builds/deploys MUST log to Supabase `ops.*` tables.
6. **No Secrets in Git:** Use environment variables or secret managers only.
7. **Addons Path Invariants:** Order MUST match across all deployment surfaces.
8. **Worker Recycling:** No in-memory state persistence assumptions.
