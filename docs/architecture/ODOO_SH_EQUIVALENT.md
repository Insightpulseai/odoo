# Odoo.sh-Equivalent Architecture — InsightPulse AI

> **What Odoo.sh gives you**: a 3-environment Git-driven deployment platform with automated
> neutralization of staging/dev databases so restored backups can never send live emails or
> run disruptive scheduled actions. This document mirrors those guarantees in our self-hosted
> stack (DigitalOcean + GitHub Actions + Supabase control-plane).
>
> Odoo.sh references: [Environments](https://www.odoo.com/documentation/19.0/administration/odoo_sh/getting_started/branches.html),
> [Neutralized DB](https://www.odoo.com/documentation/17.0/administration/neutralized_database.html),
> [Create project](https://www.odoo.com/documentation/19.0/administration/odoo_sh/getting_started/create.html)

Last updated: 2026-02-27

---

## 1. Environment Model

Map Git branches to runtimes **exactly like Odoo.sh**:

| Git branch | Runtime   | DB name      | Container       | Safety posture |
|------------|-----------|--------------|-----------------|----------------|
| `main`     | **prod**  | `odoo_prod`  | `odoo_prod`     | Live emails + schedulers allowed |
| `staging`  | **stage** | `odoo_stage` | `odoo_stage`    | **Neutralized**: schedulers disabled, outgoing mail off |
| `dev/*`    | **dev**   | `odoo_dev_*` | `odoo_dev_*`    | Neutralized + disposable |

This is enforced via `IPAI_ENV` environment variable (`prod` | `stage` | `dev`).

### IPAI_ENV wire-up

Every compose file injects `IPAI_ENV`:

```yaml
# docker/compose/prod.yml
environment:
  - IPAI_ENV=prod
  - ...

# docker/compose/stage.yml
environment:
  - IPAI_ENV=stage
  - ...
```

On container start, `scripts/odoo_neutralize.py` reads `IPAI_ENV`:
- `prod` → no-op (live system, all services enabled)
- `stage` or `dev` → disables outgoing mail servers + disables/allowlists scheduled actions

---

## 2. Neutralization Invariants

Odoo.sh documentation is explicit about what "neutralized" means:

| System | Neutralized state | Why |
|--------|-------------------|-----|
| Outgoing mail servers | **Disabled** (all `ir.mail_server` records `active = false`) | Prevent sending real customer emails from restored backups |
| Scheduled actions | **Disabled** (except allowlist) | Prevent disruptive automation, 3rd-party sync, mass mail |
| Payment providers | Out of scope for this stack (no live payment processing in CE) | — |
| IAP tokens | Not applicable (no Odoo.com IAP in CE) | — |

### Cron allowlist (stage/dev)

Only these cron jobs remain active in neutralized environments:

```
mail.mail_gc_notifications         # Clean stale mail notifications (safe)
base_automation.autovacuum         # DB maintenance (safe)
base.ir_cron_auto_vacuum           # Base vacuum (safe)
```

All other scheduled actions are disabled.

---

## 3. Database Lifecycle

Mirrors Odoo.sh semantics:

```
prod (odoo_prod)  ─── snapshot ──→  stage (odoo_stage)  ─── neutralize ──→  ✅ safe
stage (odoo_stage) ── snapshot ──→  dev (odoo_dev_*) ─── neutralize ──→  ✅ safe
```

**Rules:**
1. Restoring a backup into stage **overwrites the stage DB** — data loss is expected and intentional
2. Always run `scripts/odoo_neutralize.py` **immediately after restore** before any user access
3. Code promotion to prod = `git merge main` CI pipeline (not DB promotion)
4. DB promotion to prod = **one-time cutover only** (see `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md`)

### Restore procedure

```bash
# 1. Stop stage container
docker stop odoo_stage

# 2. Drop + recreate stage DB
docker exec odoo-postgres dropdb -U odoo odoo_stage
docker exec odoo-postgres createdb -U odoo odoo_stage

# 3. Restore from prod backup
docker exec -i odoo-postgres pg_restore -U odoo -d odoo_stage < backups/odoo_prod_YYYYMMDD.dump

# 4. Neutralize immediately (critical)
IPAI_ENV=stage \
  DB_HOST=localhost DB_PORT=5432 DB_USER=odoo DB_PASSWORD=... DB_NAME=odoo_stage \
  python3 scripts/odoo_neutralize.py

# 5. Verify neutralization
docker exec odoo-postgres psql -U odoo -d odoo_stage \
  -c "SELECT name, active FROM ir_mail_server;"
# Expected: all active = false

# 6. Start stage container
docker start odoo_stage
```

---

## 4. Mail Constraints

Odoo.sh documentation: **port 25 is closed**; external SMTP must use 465/587.

Our stack:

| Environment | Mail routing | Port |
|-------------|-------------|------|
| `prod` | Zoho Mail API (`ipai_zoho_mail_api`) | N/A (API call, no SMTP socket) |
| `stage` | **Disabled** (neutralized) | — |
| `dev` | **Disabled** (neutralized) | — |

**No port 25 anywhere.** `ipai_zoho_mail_api` uses the Zoho REST API — no outbound SMTP socket.

If SMTP is ever configured as a fallback:
- ✅ Allowed: ports 465 (SMTPS), 587 (STARTTLS)
- ❌ Forbidden: port 25 (blocked by DigitalOcean, also insecure)

CI gate `email-policy-check.yml` verifies no port 25 configs exist.

---

## 5. The Neutralization Hook

`scripts/odoo_neutralize.py` is the single idempotent script that enforces safety in non-prod.

**Trigger mechanisms:**
1. **Manual**: `python3 scripts/odoo_neutralize.py` (post-restore, post-clone)
2. **Container boot**: add to `docker/odoo/entrypoint-hook.sh` (sourced by Dockerfile ENTRYPOINT)
3. **CI gate**: `odoo-env-neutralization-gate.yml` verifies IPAI_ENV is set correctly

**Idempotency guarantee**: running the script N times on an already-neutralized DB produces zero changes on runs 2..N.

---

## 6. Supabase Control-Plane Integration

The declared desired state lives in Supabase (the OdooOps Console backbone):

| Table | Purpose |
|-------|---------|
| `ops.environments` | env name → IPAI_ENV → container identifiers |
| `ops.policies` | neutralization flags, cron allowlist |
| `ops.deployments` | git sha, image tag, status |

OdooOps Console surfaces neutralization status per environment. When `IPAI_ENV` is not `prod`,
the console shows a **NEUTRALIZED** badge and blocks mail-send operations.

---

## 7. CI Policy Gates

| Gate | Workflow | What it checks |
|------|----------|---------------|
| Email policy | `email-policy-check.yml` | No port 25 configs, no personal emails |
| Neutralization | `odoo-env-neutralization-gate.yml` | stage/dev compose files have `IPAI_ENV` set; script exists |
| DB naming | `odoo-dbname-gate.yml` | Only `odoo_prod`, `odoo_stage`, `odoo_dev_*` DB names allowed |

---

## 8. Related Files

| File | Purpose |
|------|---------|
| `scripts/odoo_neutralize.py` | Idempotent neutralization script |
| `docker/compose/stage.yml` | Stage compose (IPAI_ENV=stage) |
| `docker/compose/prod.yml` | Prod compose (IPAI_ENV=prod) |
| `.github/workflows/odoo-env-neutralization-gate.yml` | CI enforcement |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | Go-live runbook |
| `ssot/secrets/registry.yaml` | Secret identifier registry |
