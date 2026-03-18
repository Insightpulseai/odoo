# Environments Contract

> Defines dev/staging/prod identifiers, acceptance criteria, and secret-of-record rules.

## Environment Matrix

| Env | Supabase Project | Vercel Project | Odoo DB | Domain Pattern | Slack Channel |
|---|---|---|---|---|---|
| dev | (set in `config/dev/`) | preview deploys | `odoo_dev` | `*.dev.insightpulseai.com` | `#dev-alerts` |
| staging | (set in `config/staging/`) | preview (staging) | `odoo_staging` | `*.staging.insightpulseai.com` | `#staging-alerts` |
| prod | (set in `config/prod/`) | production | `odoo` | `*.insightpulseai.com` | `#prod-alerts` |

## Identifier Locations (Non-Secret)

Each environment has a `config/<env>/runtime_identifiers.yaml` with non-secret identifiers only:
- Supabase project ref
- Vercel project name
- Odoo DB name
- Domain patterns
- Slack channel

Secrets are **never** stored in these files. See `docs/architecture/SECRETS_POLICY.md`.

---

## Staging Deployed: Acceptance Criteria

A staging deployment is "done" when all of these are true:

### 1. Supabase Staging

- [ ] Schema/migrations applied
- [ ] Edge Functions deployed
- [ ] Staging secrets set (Vault/Edge secrets)

### 2. Vercel Staging

- [ ] App deployed and points to staging Supabase
- [ ] `SUPABASE_URL` + `SUPABASE_ANON_KEY` are staging values
- [ ] Preview/production env mapping is explicit

### 3. Odoo Staging

- [ ] `odoo_staging` database exists with separate config
- [ ] Addons pinned to the same commit/tag being tested
- [ ] Base URL distinct (`staging.erp.insightpulseai.com` or similar)

### 4. Observability

- [ ] Deploy events visible in ops schema
- [ ] Slack alerts on success/failure
- [ ] Health checks pass for all three planes

---

## Platform-Specific Environment Mapping

### Supabase

| Env | Project | Secrets Store |
|---|---|---|
| dev | `spdtwktxdalcfigzeqrz` (or dev-specific) | Supabase Vault / Edge secrets |
| staging | separate project ref | Supabase Vault / Edge secrets |
| prod | `spdtwktxdalcfigzeqrz` | Supabase Vault / Edge secrets |

### Vercel

| Vercel Environment | Maps To | Notes |
|---|---|---|
| Development | dev (local) | local `.env.development` |
| Preview | staging / per-PR ephemeral | auto-deploy on push |
| Production | prod | main branch only |

Shared env vars allowed only for non-privileged values (or explicitly approved list).

### Odoo

| Env | DB Name | Config Path | Deploy Method |
|---|---|---|---|
| dev | `odoo_dev` | `config/dev/odoo.conf` | docker compose (local) |
| staging | `odoo_staging` | `config/staging/odoo.conf` | CI-triggered remote deploy |
| prod | `odoo` | `config/prod/odoo.conf` | CI-triggered with approval gate |

### Superset

| Env | URL | Primary DB | Notes |
|---|---|---|---|
| dev | (set in `config/dev/`) | `odoo_dev` | safe seed data |
| staging | (set in `config/staging/`) | `odoo_staging` | prod-like masking |
| prod | (set in `config/prod/`) | `odoo` | strict access, read-only role |

---

## CI/CD Contracts

### Deploy Workflow

- `.github/workflows/deploy-staging.yml` — uses GitHub Environment `staging` (approval gate)
- Steps: deploy Supabase (migrations + functions) → deploy Vercel → trigger Odoo staging → notify Slack

### Verify Workflow

- `.github/workflows/verify-staging.yml` — health checks for all planes
- Checks: Supabase health RPC, Vercel URL build string, Odoo `/web/health`

---

## Rules

1. **Never share API keys across envs** unless the provider forces it
2. **Staging must be a separate Supabase project** (or branch) to prevent data/secret bleed
3. **Vercel staging** is either a dedicated project or Preview environment (not mixed)
4. **Odoo staging** runs on a separate DB with separate config
5. **All deploys are CI-triggered** — no manual CLI deploys to staging/prod
