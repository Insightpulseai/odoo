# C-ODOOS-01 — Odoo.sh Operational Parity Contract

> **Contract ID**: C-ODOOS-01
> **Status**: Active
> **Owner**: Platform Engineering
> **Last Updated**: 2026-03-01

---

## 1. Purpose

This contract documents which Odoo.sh features are implemented in OdooOps Console,
which restrictions are modeled as platform policies, and what is explicitly *not* replicated.

---

## 2. Parity Feature Matrix

| Odoo.sh Feature | OdooOps Module | Backing System | Evidence Artifact | Status |
|-----------------|----------------|----------------|-------------------|--------|
| GitHub integration | Builds + Deployments | GitHub Actions + Vercel | `ops.builds`, GH run links | ✅ beta |
| Clear Logs | Logs page | `ops.platform_events` | log queries + saved filters | ✅ beta |
| Web Shell | Runbooks / Env actions | Remote exec adapter | `ops.exec_sessions` | 🔲 planned |
| Module Dependencies | Modules + Policy Gates | SSOT allowlist + CI | `module_status_*.txt` | 🔲 planned |
| Continuous Integration (Runbot) | Builds | CI pipeline | junit + summary artifacts | ✅ beta |
| SSH Access | Runbooks | SSH key mgmt docs | `ops.exec_sessions` | 🔲 planned |
| Mail Catcher | Observability / Mail Events | Mailgun relay + `ops.mail_events` | mail event records | 🔲 planned |
| Staging Branches | Environments | DO Droplets + Vercel preview | env health rows | ✅ beta |
| Backups & Recovery | Backups | `ops.backups` + job executor | snapshot manifests | ✅ beta |
| Monitoring & KPIs | Overview / Observability | DO + Supabase metrics | healthcheck + metric snapshots | ✅ beta |

---

## 3. Restrictions Modeled as Policies

The following Odoo.sh runtime restrictions are enforced as OdooOps platform policies:

| Restriction | Policy | CI Gate |
|-------------|--------|---------|
| No long-lived daemons | Jobs must be bounded; auto-disable after N repeated timeouts | Job timeout policy check |
| Cron time limits | Enforce `max_duration` on all `pg_cron` / Edge Function jobs | `ops.job_runs` duration audit |
| Staging/dev concurrency | Single-worker semantics documented; concurrency limits set | Manual review + runbook |
| No port 25 SMTP | Non-prod `SMTP_PORT=25` → CI FAIL | CI gate (task 33) |
| Mail catcher in non-prod | Non-prod SMTP host must be Mailgun relay | CI gate (task 33) |
| Immutable base images | No `apt install` in runtime; deps via `requirements.txt` | Dockerfile linting |
| DB object count ceiling | `tables + sequences > 10,000` → gate WARN/FAIL | Parity policy gate (task 24) |
| Multiple addons paths | `addons/odoo`, `addons/oca`, `addons/ipai` — no drift | `check_repo_structure.py` |

---

## 4. Explicit Non-Parity

The following Odoo.sh capabilities are **intentionally not replicated**:

| Odoo.sh Feature | Decision | Rationale |
|-----------------|----------|-----------|
| Odoo.sh platform API (create/delete projects) | Replaced by Vercel/DO/Supabase APIs | We own our control plane |
| Per-customer Odoo.sh branch provisioning | Out of scope for internal ops console | Not a SaaS provisioner |
| Odoo.sh staging database anonymization | Documented in runbook | Manual step, not automated |
| Odoo.sh long-polling server | Handled by Odoo's own gevent server | No change needed |

---

## 5. Change Process

Changes to this contract require:

1. PR updating this file and `spec/odooops-console/prd.md`.
2. Corresponding `tasks.md` task for any new parity gate.
3. One reviewer from Platform Engineering.
