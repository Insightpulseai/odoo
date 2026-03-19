# Databases and Roles — InsightPulse AI Platform

**Last updated:** 2026-02-28
**Status:** Active
**SSOT cross-reference:** [`ipai-ops-platform/ssot/databases/topology.yaml`](../../../../../../ipai-ops-platform/ssot/databases/topology.yaml)
**Cluster detail:** [`ipai-ops-platform/ssot/databases/postgres_clusters/odoo-db-sgp1.yaml`](../../../../../../ipai-ops-platform/ssot/databases/postgres_clusters/odoo-db-sgp1.yaml)

---

## 1. System Overview

InsightPulse AI runs exactly **two** Postgres systems:

| System | Provider | Purpose | Doctrine role |
|--------|----------|---------|---------------|
| **odoo-db-sgp1** | DigitalOcean Managed Postgres 16 | Odoo business data (sales, accounting, inventory, HR, projects) | System of Record (SoR) |
| **Supabase** (`spdtwktxdalcfigzeqrz`) | Supabase (PG 15, Singapore) | Control plane, auth, integrations, Edge Functions, task bus, pgvector | SSOT / control plane |

These two systems cover every operational need. A third physical database is added only when explicit expansion criteria are met (see Section 6).

---

## 2. Database and Role Reference Table

### 2.1 Odoo SoR — odoo-db-sgp1

| Database | Environment | Lifecycle | Role | Type | Access | Consumer(s) | Rotation |
|----------|-------------|-----------|------|------|--------|-------------|----------|
| `odoo` | production | active | `doadmin` | admin / break-glass | full superuser | none (emergency only) | Annually; immediately on exposure |
| `odoo` | production | active | `odoo_app` | application | readwrite on public schema | Odoo CE container | Quarterly |
| `odoo` | production | active | `superset_ro` | readonly | SELECT on public schema | Apache Superset | Quarterly |
| `odoo` | production | active | `n8n_rpc` | no DB role | XML-RPC only (port 8069) | n8n workflows | N/A |
| `odoo_dev` | development | active | `doadmin` | admin / break-glass | full superuser | none (emergency only) | Annually; immediately on exposure |
| `odoo_dev` | development | active | `odoo_app` | application | readwrite on public schema | Odoo CE container (dev) | Quarterly |
| `odoo_stage` | staging | **planned** | `odoo_app` | application | readwrite on public schema | Odoo CE container (stage) | Quarterly |

**Notes on provisioning status:**
- `odoo_app` role does not yet exist as a distinct Postgres role. Odoo currently connects as `doadmin`. This is the primary hardening gap and must be remediated before first external audit.
- `superset_ro` is not yet provisioned. Provision alongside Superset datasource configuration.
- `odoo_stage` database is not yet created; will be provisioned when a staging droplet is stood up.

### 2.2 Supabase SSOT — `spdtwktxdalcfigzeqrz`

All Supabase roles are built-in; no custom roles are required.

| Database | Role | Type | Access | Consumer(s) | Rotation |
|----------|------|------|--------|-------------|----------|
| `postgres` | `anon` | built-in | RLS-governed, unauthenticated read | Public API clients | Annually |
| `postgres` | `authenticated` | built-in | RLS-governed readwrite | JWT-authenticated session users | Annually |
| `postgres` | `service_role` | built-in | RLS-bypass readwrite | Edge Functions, n8n Supabase bridge | Quarterly |
| `postgres` | `supabase_admin` | built-in / break-glass | Superuser (platform maintenance) | Supabase platform only | Managed by Supabase |

**RLS requirement:** Every table accessible to `anon` or `authenticated` MUST have an explicit Row-Level Security policy. Tables without RLS enabled are inaccessible to non-service-role callers by default (and must stay that way).

### 2.3 Other Databases on odoo-db-sgp1 (Non-Odoo)

| Database | Application | Role | Notes |
|----------|-------------|------|-------|
| `shelf_db` | Shelf.nu asset management | `shelf_app` | Independent application; not an Odoo database |
| `plane_db` | Plane project management | `plane_app` | Independent application; not an Odoo database |
| `defaultdb` | DO admin only | `doadmin` | DO-managed default; no app reads this |

---

## 3. Minimal Sane Set — Why Two Systems, Not Five

The platform was designed with a strict constraint: **operate at minimum viable infrastructure cost** without sacrificing correctness or auditability.

**Why not a separate analytics database?**
Superset reads directly from `odoo-db-sgp1` via `superset_ro`. The read volume from Superset is low enough that a dedicated analytics replica is not warranted. If sustained query load from Superset drives odoo-db-sgp1 CPU above 80%, the upgrade path is a DO read replica on the same cluster — not a new database system.

**Why not a separate auth database?**
Supabase provides managed auth (GoTrue) backed by its own `auth` schema. There is no operational or compliance reason to run a separate auth database; Supabase Auth is production-grade and covers PKCE, MFA, and SSO.

**Why not a separate integration database?**
n8n workflow state and integration event logs live in Supabase `public` schema tables. This is intentional: Supabase provides realtime subscriptions, Row-Level Security, and Edge Functions that make it ideal for integration choreography. Running a separate integration database would add cost and operational complexity with no benefit.

**The two-system rule:**

> **Business data belongs in Odoo Postgres. Control-plane, auth, and integration data belongs in Supabase. Everything else is a view, schema, or derived artifact — not a new physical database.**

---

## 4. Write Boundary Rules

These rules are non-negotiable and are enforced at the application layer and (where possible) at the network layer.

### 4.1 Odoo is the System of Record for Business Data

All writes to Odoo business objects — `res.partner`, `account.move`, `sale.order`, `stock.*`, `hr.*`, `project.*`, and any installed OCA or `ipai_*` module models — MUST go through the Odoo ORM:

- Odoo XML-RPC (port 8069, used by n8n and external integrations)
- Odoo JSON-RPC
- Python model calls within the Odoo process

Direct SQL writes to the `odoo` database are **forbidden** except for:
1. Break-glass emergency operations performed by `doadmin` under incident protocol
2. Migration scripts executed by the Odoo migration framework (not raw SQL to ORM-managed tables)

### 4.2 Supabase Does Not Write to Odoo Postgres

Supabase Edge Functions and n8n Supabase nodes must NOT open a direct Postgres connection to `odoo-db-sgp1`. Data flowing from Supabase into Odoo must use the Odoo API (XML-RPC or REST).

This boundary is enforced by the absence of any firewall rule permitting Supabase egress IPs to connect to odoo-db-sgp1 port 25060.

### 4.3 Superset is Read-Only on Odoo Postgres

Superset connects to `odoo-db-sgp1` exclusively via the `superset_ro` role, which holds only `SELECT` grants. Superset MUST NOT be configured with `doadmin`, `odoo_app`, or any other role that has write capability. If Superset requires data transformation, that transformation is done in Superset itself (calculated columns, custom SQL) — never written back to the Odoo database.

### 4.4 Summary Matrix

| From \ To | Odoo Postgres (write) | Odoo Postgres (read) | Supabase (write) | Supabase (read) |
|-----------|----------------------|---------------------|-----------------|----------------|
| Odoo ORM | Allowed | Allowed | Via Edge Function / n8n | Via Edge Function / n8n |
| n8n | XML-RPC only | XML-RPC only | Allowed (service_role) | Allowed |
| Superset | **Forbidden** | Allowed (superset_ro only) | — | — |
| Edge Functions | **Forbidden** | **Forbidden** | Allowed (service_role) | Allowed |

---

## 5. Superset Reading Rules

Apache Superset is the BI layer. Its data access is governed by these rules:

1. **Primary source:** `odoo-db-sgp1` via `superset_ro` role (SELECT on `public` schema of `odoo` database only)
2. **Secondary source:** Supabase `postgres` database — Superset may connect via a read-only service account to query control-plane analytics schemas (e.g., task bus metrics, Edge Function execution logs)
3. **Never write:** Superset MUST NOT have a writable connection to any database in this topology
4. **No cross-database joins in Superset:** Joins between Odoo data and Supabase data must be materialised into Supabase tables via n8n or Edge Functions, then read from Supabase by Superset — not attempted as live cross-database joins
5. **Credential isolation:** `superset_ro` password is stored only in the Superset datasource connection string (GitHub secret `SUPERSET_RO_PASSWORD`); it is not shared with any other service

---

## 6. When to Add Another Physical Database

Add a new database only when one of these criteria is met:

| Criterion | Action |
|-----------|--------|
| New application with an independent data model (not an Odoo module) | Add a new database on `odoo-db-sgp1` (same cluster) or a new DO managed cluster |
| Compliance requirement mandating data isolation (PCI-DSS, HIPAA, data residency) | Provision a dedicated cluster in the required region |
| `odoo-db-sgp1` sustained CPU > 80% or total connections > 20 | Upgrade cluster tier OR add a read replica — do not add a new database |
| Staging environment provisioned | Create `odoo_stage` on same cluster; add `odoo_app` role for staging |

**Do NOT add a new database for:**
- New Odoo modules — use `addons/` within the existing `odoo` database
- New Supabase features — add a schema or table to the existing `postgres` database
- BI/analytics views — use `superset_ro` on the existing `odoo` database or Supabase schemas
- Caching — use Redis (already available) or Supabase Realtime

---

## 7. Credential Rotation Policy

| Role | System | Cadence | Method | On Suspected Exposure |
|------|--------|---------|--------|-----------------------|
| `odoo_app` | odoo-sor | Quarterly | Generate new password → update GitHub secret `ODOO_DB_PASSWORD` → restart Odoo container → verify health check | Immediate |
| `superset_ro` | odoo-sor | Quarterly | Generate new password → update Superset datasource → verify dashboards | Immediate |
| `doadmin` | odoo-sor | Annually | Rotate via DigitalOcean console → update `DO_DB_ADMIN_PASSWORD` GitHub secret → confirm no app container references it | Immediate |
| `service_role` | supabase-ssot | Quarterly | Rotate via Supabase dashboard (Settings → API) → update all consumers → redeploy Edge Functions | Immediate |
| `anon` | supabase-ssot | Annually | Rotate via Supabase dashboard → update `NEXT_PUBLIC_SUPABASE_ANON_KEY` in all client apps | Immediate |

**Rotation checklist (generic):**
1. Generate new credential (Postgres: `ALTER ROLE ... PASSWORD '...'`; Supabase: rotate via dashboard)
2. Update the GitHub secret or environment variable
3. Restart the consuming service
4. Verify health checks pass
5. Record rotation in `docs/evidence/<YYYYMMDD-HHMM>/db-rotation/`
6. Revoke the old credential (for Supabase keys) or confirm the old password is no longer usable

---

## 8. Cross-References

| Document | Location | Purpose |
|----------|----------|---------|
| Database topology SSOT (machine-readable) | `ipai-ops-platform/ssot/databases/topology.yaml` | Authoritative system/role/consumer bindings |
| Cluster detail SSOT | `ipai-ops-platform/ssot/databases/postgres_clusters/odoo-db-sgp1.yaml` | Cluster host, port, tier, SSL, connection notes |
| Secrets registry | `ipai-ops-platform/ssot/secrets/registry.yaml` | Secret IDs and storage locations |
| Supabase integration architecture | `docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md` | Edge Functions, pgvector, Auth, Realtime usage |
| Superset integration guide | `docs/superset/SUPERSET_INTEGRATION.md` | Datasource configuration, dashboard setup |
| DB init runbook | `docs/DB_INIT_RUNBOOK.md` | Step-by-step database initialisation |
| Secrets policy | `docs/architecture/SECRETS_POLICY.md` | Storage, rotation, and disclosure rules |

---

## 9. Open Hardening Items

These gaps are known and tracked. The `odoo_app` role creation is the highest priority.

| Gap | Risk | Remediation | Priority |
|-----|------|-------------|----------|
| Odoo connects as `doadmin` instead of `odoo_app` | High — any bug in Odoo code runs with superuser privileges | Create `odoo_app` role, grant minimum privileges, update `ODOO_DB_PASSWORD` | P0 — before next external audit |
| `superset_ro` role not yet provisioned | Medium — Superset datasource not configured; BI unavailable | Provision role, configure Superset datasource | P1 — when Superset goes live |
| `odoo_stage` database not provisioned | Low — staging environment not yet stood up | Create when staging droplet is provisioned | P2 — next infrastructure sprint |
| No automated credential rotation | Medium — manual rotation is error-prone | Implement rotation automation via GitHub Actions or DO API | P2 — security hardening sprint |
