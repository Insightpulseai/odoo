# Data Source of Truth (SSOT) Policy

> **Status:** Canonical | **Last updated:** 2026-02-23 | **Owner:** Architecture Team
> This policy governs which datastores are authoritative (SSOT/SOR), conditional, or prohibited.

---

## 1. PostgreSQL — System of Record and SSOT

PostgreSQL is the **only SSOT** for all production data in the InsightPulse AI platform:

| Data Domain | System | Location |
|-------------|--------|----------|
| ERP transactions (invoices, payments, stock) | Odoo CE 19 | DO Managed Postgres |
| Ops / control plane state | Supabase `ops.*` | Supabase Managed Postgres |
| Auth and identity (non-Odoo surfaces) | Supabase Auth | Supabase Managed Postgres |
| Analytics-ready datasets | Supabase gold/platinum schemas | Supabase Managed Postgres |
| Tool metadata (Superset, n8n) | PostgreSQL | DO Managed Postgres or Supabase |

**Corollary:** All other datastores are either staging zones, integration transports, or explicitly prohibited.

---

## 2. MySQL / MariaDB — Conditional Use Only

MySQL is permitted **only** for:
- Source-system compatibility (ingesting from legacy MySQL systems)
- Staging / Bronze landing zones (non-authoritative)
- Short-lived reproduction environments (documented constraint)
- Legacy tool constraints where no MySQL-free alternative exists (must be documented)

MySQL **MUST NOT:**
- Be treated as SSOT for any business domain
- Host authoritative business logic or final-state data
- Become a long-term dependency without an approved migration plan

---

## 3. SQLite — Prohibited in Production

SQLite is **explicitly prohibited** for any production workload:

| Context | SQLite | Notes |
|---------|--------|-------|
| Superset metadata DB | ❌ Prohibited | Use PostgreSQL |
| n8n production storage | ❌ Prohibited | Use external PostgreSQL |
| Any persistent service | ❌ Prohibited | Data lost on container restart |
| Local dev sandbox (throwaway) | 🟡 Permitted | Never commit or promote |
| Unit/integration test fixtures | 🟡 Permitted | In-memory only |

**Why:** SQLite is not safe for production persistence — it loses data on container restart, is not multi-replica safe, and cannot be backed up consistently in containerized environments.

---

## 4. Superset-Specific Rules

| Component | Required | Rationale |
|-----------|----------|-----------|
| Metadata DB engine | PostgreSQL | Multi-replica safe, survives restarts |
| `SQLALCHEMY_DATABASE_URI` | `postgresql://...` prefix | Never `sqlite:///...` |
| Datasource connections (BI) | Transaction Pooler preferred | IPv4-safe; works from all CI/serverless |
| Datasource connections (direct) | IPv6-capable infra only | Supabase Direct is IPv6-first |

---

## 5. Poolers and IPv4/IPv6 Compatibility

Supabase Direct connections are **IPv6-first**. IPv4-only clients **must** use the Transaction Pooler.

**IPv4-only clients (must use pooler):**
- Vercel serverless functions
- GitHub Actions runners (unless explicitly IPv6-enabled)
- Most SaaS BI tools
- Superset on standard DO droplets (confirm IPv6 availability before using Direct)

Failing to follow this rule causes silent connection failures that are difficult to debug. See `docs/architecture/CONNECTION_MATRIX.md` for the full connection decision guide.

---

## 6. Enforcement

| Rule | Enforced By |
|------|-------------|
| No SQLite metadata DB (Superset) | `docker-compose` config review + admin panel check |
| Stray SQL files outside migrations | `scripts/ci/check_supabase_contract.sh` |
| Pooler vs Direct guidance | `docs/architecture/CONNECTION_MATRIX.md` (documentation) |
| DO PG Network Access allowlisting | Terraform (`infra/digitalocean/terraform/`) |

---

## 7. Summary Table

| Datastore | Role | Production | Dev/Test |
|-----------|------|-----------|---------|
| **PostgreSQL** | SSOT / SOR | ✅ Required | ✅ |
| **MySQL/MariaDB** | Non-SSOT source/staging | 🟡 Conditional only | 🟡 |
| **SQLite** | — | ❌ Prohibited | 🟡 Local/test only |

---

## References

- Connection decision guide: `docs/architecture/CONNECTION_MATRIX.md`
- SSOT boundary rules: `docs/architecture/SSOT_BOUNDARIES.md`
- Platform contracts: `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`
