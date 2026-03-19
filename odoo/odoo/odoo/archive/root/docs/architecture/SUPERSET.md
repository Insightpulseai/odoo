# Superset Integration Contract

## Purpose

Superset is the BI layer for operational dashboards and ad-hoc analysis.
It must be reproducible, environment-scoped (dev/staging/prod), and secrets-free in git.

## Topology

- **Superset runtime**: hosted on DigitalOcean (container or DO App Platform)
- **Data sources**:
  - Primary: Odoo Postgres (DO managed PG cluster)
  - Optional: Supabase Postgres (control plane / analytics DB)
- **Network**:
  - DB connections require SSL (`sslmode=require`) where applicable
  - Prefer VPC/private networking if available; otherwise IP allowlists

## SSOT Locations

| Path | Purpose |
|------|---------|
| `infra/superset/` | Templates + provisioning stubs (no secrets) |
| `infra/superset/manifest.json` | Pinned image reference (tag, digest, metadata) |
| `infra/superset/do-app-spec.yaml` | DO App Platform deployment spec |
| `infra/superset/env/.env.superset.example` | Env var template (placeholders only) |
| `infra/superset/provisioning/` | DB/datasource/dashboard provisioning stubs |
| `config/{dev,staging,prod}/` | Environment identifiers (endpoints, DB names, non-secret flags) |
| `.github/workflows/superset-bump.yml` | CI: update image tag |

## Secret Handling (Non-Negotiable)

- No DB passwords, JWTs, API keys in git.
- Runtime secrets are injected via:
  - DO env vars / container env
  - Supabase Edge Function secrets (if brokering tokens)
  - GitHub Actions secrets (CI only; never written to repo)

## Environment Mapping

| Env | Superset URL | Primary DB | Notes |
|---|---|---|---|
| dev | (set in `config/dev/`) | `odoo_dev` | safe seed data |
| staging | (set in `config/staging/`) | `odoo_staging` | prod-like masking |
| prod | (set in `config/prod/`) | `odoo` | strict access, read-only role |

## Data Access Model

- Use a dedicated **read-only DB role** for Superset (least privilege).
- Prefer **analytics views** (stable schemas) over raw ERP tables.
- If row-level constraints are needed, implement via DB views + role grants.
  - Superset RLS is not a substitute for DB RLS.

## Artifact Contract

```
superset repo          odoo repo
┌──────────────┐       ┌──────────────────┐
│ Build → Push │ image │ manifest.json    │
│ to GHCR      │──────>│ (pinned tag)     │
│              │       │                  │
│ CI: build,   │webhook│ do-app-spec.yaml │
│ scan, push   │──────>│ (deploy spec)    │
└──────────────┘       └──────────────────┘
```

1. Superset repo builds and pushes container image
2. Superset repo (optionally) sends `repository_dispatch` to odoo
3. `superset-bump.yml` workflow updates `manifest.json` + `do-app-spec.yaml`
4. PR opened for review
5. After merge, DO App auto-deploys new image

## Provisioning Strategy

- Baseline provisioning files live under `infra/superset/provisioning/`:
  - `databases/` — DB connections (env-driven)
  - `datasources/` — dataset definitions (optional)
  - `dashboards/` — dashboard exports (optional, if versioning dashboards)
- Keep provisioning minimal at first; expand once contracts stabilize.

## Operational Expectations

- **Backup**: Superset metadata DB backed up with the runtime
- **Upgrade**: pinned version, reproducible compose/service definition
- **Observability**: health endpoint (`/health`) + Slack alerts via n8n or GitHub Actions
- **Health check**: `curl https://superset.insightpulseai.com/health` → `{"status": "OK"}`
