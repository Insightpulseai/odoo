# Odoo 18 CE Image Build Specification

> Canonical build spec for the IPAI Odoo runtime image family.
> Target: ACR (`acripaiodoo`) → ACA (`ipai-odoo-{dev,ha}-{web,worker,cron}`).

## Runtime Evidence

| Resource | Value |
|----------|-------|
| ACR | `acripaiodoo.azurecr.io` |
| ACA Dev | `ipai-odoo-dev-web`, `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron` |
| ACA HA | `ipai-odoo-ha-web`, `ipai-odoo-ha-worker`, `ipai-odoo-ha-cron` |
| Database | Azure Database for PostgreSQL Flexible Server (`pg-ipai-odoo`) |
| Front Door | `fd-ipai-odoo` → `erp.insightpulseai.com` |
| Key Vault | `kv-ipai-dev` (SMTP creds, DB creds, HMAC secrets) |

## Image Families

### Production (`docker/Dockerfile.prod`)

Purpose: ACR push, ACA deployment, release candidates.

- Base: `odoo:18.0` (Debian, official image)
- Bakes addons into `/opt/odoo/src/{oca,ipai,local}/`
- Generates `addons_path` at build time from repos on disk
- Config: `config/azure/odoo.conf` (ACA) or `config/prod/odoo.conf` (standalone)
- Entrypoint: `docker/entrypoint.sh` (role-based: web/worker/cron)
- No secrets, no test artifacts, no dev tooling

### Dev (`docker/Dockerfile.dev`)

Purpose: Local iteration, test, debug, Playwright/browser work.

- Base: `odoo:18.0` (same lineage as prod)
- Does NOT bake addons — expects volume mounts
- Adds: `debugpy`, `ipython`, `watchdog`, `freezegun`, `lxml[html_clean]`
- Mounts: `./addons/oca`, `./addons/ipai`, `./config/dev/odoo.conf`
- Entrypoint: same `docker/entrypoint.sh`

## Addon Inclusion Rules

### Include in runtime image

| Layer | Source | Image Path |
|-------|--------|-----------|
| CE core | `odoo:18.0` base image | `/usr/lib/python3/dist-packages/odoo/addons` |
| OCA | `addons/oca/` | `/opt/odoo/src/oca/<repo>/` |
| IPAI | `addons/ipai/` | `/opt/odoo/src/ipai/` |
| Local | `addons/local/` | `/opt/odoo/src/local/` |

### IPAI module inclusion

The image contains the **available addon surface**. The database decides which modules are installed.

**Always include** (installable, has code or critical data):

- `ipai_enterprise_bridge` — EE-parity stubs, shared config
- `ipai_odoo_copilot` — Foundry-backed skill router
- `ipai_copilot_actions` — AI job state, approval gates
- `ipai_document_intelligence` — Azure Document Intelligence OCR
- `ipai_finance_ppm` — Project portfolio management
- `ipai_hr_expense_liquidation` — Cash advance workflow
- `ipai_mail_plugin_bridge` — Gmail add-on endpoints
- `ipai_marketing_automation` — Campaign automation
- `ipai_service_calculator` — SO line generator
- `ipai_timesheet_leaderboard` — Billable hours views
- `ipai_bir_tax_compliance` — PH BIR compliance
- `ipai_auth_oidc` — OIDC SSO + TOTP MFA
- `ipai_aca_proxy` — ACA header injection
- `ipai_security_frontdoor` — Front Door FDID validation
- `ipai_project_timeline_fix` — CE view_mode fix (auto_install)
- `ipai_web_branding` — Login page styling

**Exclude from prod image** (deprecated, `installable: False`):

- `ipai_ai_channel_actions` — superseded by Foundry livechat
- `ipai_ai_copilot` — superseded by `ipai_odoo_copilot`
- `ipai_ai_platform` — superseded by Foundry API
- `ipai_ai_widget` — superseded by Foundry ask mode
- `ipai_ask_ai_azure` — superseded by Foundry ask mode
- `ipai_llm_supabase_bridge` — Supabase deprecated

**Exclude from prod image** (seed/demo only):

- `ipai_finance_close_seed` — TBWA\SMP demo data
- `ipai_project_seed` — Demo projects/tasks

**Incomplete stubs** (no manifest, not runnable):

- `ipai_bir_notifications`, `ipai_hr_payroll_ph`, `ipai_ops_connector`
- `ipai_system_config`, `ipai_theme_copilot`

## Role-Based Startup

The same image serves all three ACA roles via `ODOO_ROLE` env var.

### Role contract

| Role | Responsibility | Serves HTTP? | Cron? | Public ingress? | Flags |
|------|---------------|:------------:|:-----:|:---------------:|-------|
| `web` | User-facing Odoo app (UI + API + longpolling) | Yes (8069 + 8072) | No | Yes (Front Door) | `--max-cron-threads=0` |
| `cron` | ir.cron scheduled actions + mail queue | No | Yes (2 threads) | No | `--no-http --workers=0 --max-cron-threads=2` |
| `worker` | OCA queue_job background job processing | No | No | No | `--no-http --workers=0 --max-cron-threads=0` |

### Role semantics (precise)

**web**: Starts Odoo with HTTP enabled. `workers` count comes from `odoo.conf` (4 in prod, 0 in dev). Cron is explicitly disabled (`--max-cron-threads=0`) because the dedicated cron container handles scheduled actions. This is the only role that receives traffic from Front Door / ACA ingress. Health check: `GET /web/health` must return 200.

**cron**: Starts Odoo with `--no-http` in single-thread mode (`--workers=0`). The `--max-cron-threads=2` flag enables Odoo's built-in cron runner, which polls `ir.cron` records and executes scheduled actions (mail queue, agent dispatch, monitoring). Must NOT have public ingress. Connects to the same database as web.

**worker**: Starts Odoo with `--no-http --workers=0 --max-cron-threads=0`. In this mode, Odoo starts its single-thread server with no HTTP and no cron. OCA `queue_job`'s jobrunner hooks into the Odoo server lifecycle and polls the database for enqueued jobs, processing them in-process. Job channels are configured in the `[queue_job]` section of `odoo.conf`. If `queue_job` is not installed in the database, this role starts but idles harmlessly. Must NOT have public ingress.

**Why three roles instead of one**: Vanilla Odoo can run all three concerns in a single process (`workers=N` with `max_cron_threads=M`). The ACA split provides:
- Independent scaling (web scales with traffic, cron is fixed, worker scales with queue depth)
- Isolation (a slow cron job cannot block HTTP responses)
- Restart independence (deploying a new web image does not interrupt running cron jobs)

### Entrypoint behavior (`docker/entrypoint.sh`)

1. Reads `ODOO_ROLE` env var (default: `web`)
2. Validates config file exists at `$ODOO_RC`
3. Waits for database at `$DB_HOST:$DB_PORT` (max 30s, using `pg_isready`)
4. Logs role + config + DB target
5. Execs `odoo` with role-appropriate flags
6. Passes through any extra args via `$@`

## Local Compose Topology

`docker-compose.odoo.local.yml` mirrors ACA:

```
odoo-web     → ODOO_ROLE=web     (always starts)
odoo-worker  → ODOO_ROLE=worker  (profile: aca-parity)
odoo-cron    → ODOO_ROLE=cron    (profile: aca-parity)
db           → postgres:16-alpine (local convenience)
redis        → redis:7-alpine    (session/bus)
```

Default: `up odoo-web db` (single-process dev).
Full parity: `up --profile aca-parity` (web + worker + cron).

## Secrets and Config

### Never bake into image

- Database credentials (injected via ACA env vars from Key Vault)
- SMTP credentials (resolved at runtime via managed identity)
- HMAC secrets, API keys, OAuth client secrets
- `.env` files

### Config hierarchy

| Environment | Config Source | DB Credentials |
|------------|-------------|----------------|
| Local dev | `config/dev/odoo.conf` (volume mount) | Compose env vars |
| ACA staging | `config/azure/odoo.conf` (image-baked) | Key Vault → ACA env |
| ACA prod | `config/azure/odoo.conf` (image-baked) | Key Vault → ACA env |

## Promotion Path

```
1. Build locally:     docker build -f docker/Dockerfile.prod -t ipai-odoo:18.0-rc .
2. Validate locally:  docker compose -f docker-compose.odoo.local.yml up
3. Tag RC:            docker tag ipai-odoo:18.0-rc acripaiodoo.azurecr.io/ipai-odoo-web:18.0-<sha>
4. Push to ACR:       docker push acripaiodoo.azurecr.io/ipai-odoo-web:18.0-<sha>
5. Deploy to ACA:     az containerapp update --image acripaiodoo.azurecr.io/ipai-odoo-web:18.0-<sha>
```

## Build Context

`.dockerignore` uses exclude-everything-then-allowlist pattern:

- Allowed: `addons/oca/**`, `addons/ipai/**`, `config/**`, `docker/**`
- Excluded: `.git`, tests, `__pycache__`, `.venv`, evidence, screenshots

## Acceptance Gates

A runtime image is NOT promotable to ACR/ACA unless:

| Gate | Verification |
|------|-------------|
| Fresh install | `odoo -c $ODOO_RC -d test_image_smoke -i base --stop-after-init` exits 0 |
| Web health | `curl -sf http://localhost:8069/web/health` returns 200 in web role |
| Role selection | Each role starts with correct flags (no HTTP on cron/worker, no cron on web/worker) |
| Addon surface | Included addons match approved classification (no deprecated, no stubs) |
| No secrets | `docker history --no-trunc <image>` contains no credential values |
| Config valid | `odoo.conf` has `list_db=False`, `proxy_mode=True`, no plaintext passwords |

## Image Manifest

Each built image should produce a machine-readable manifest at `/etc/odoo/image-manifest.json`:

```json
{
  "base_image": "odoo:18.0",
  "build_date": "2026-04-06T00:00:00Z",
  "git_sha": "<commit>",
  "odoo_version": "18.0",
  "oca_repos": ["account-financial-tools", "..."],
  "oca_module_count": 119,
  "ipai_modules": ["ipai_enterprise_bridge", "..."],
  "ipai_module_count": 16,
  "excluded_ipai": ["ipai_ai_widget", "..."],
  "python_packages": "pip freeze output path"
}
```

Generated at build time by a `RUN` step in `Dockerfile.prod`. Not required for dev image.

## Non-Goals

- No secrets in image layers
- No database embedded in image
- No seed/demo data in prod image
- No Compose-for-Agents for core Odoo runtime (reserved for AI sidecars/MCP)
- No single monolith container for all roles

## Files

| File | Purpose |
|------|---------|
| `docker/Dockerfile.prod` | Production image, baked addons |
| `docker/Dockerfile.dev` | Dev image, mount-friendly |
| `docker/entrypoint.sh` | Role-based startup (web/worker/cron) |
| `docker-compose.odoo.local.yml` | Local ACA-parity compose |
| `config/azure/odoo.conf` | ACA runtime config |
| `config/prod/odoo.conf` | Standalone prod config |
| `config/dev/odoo.conf` | Local dev config |
| `.dockerignore` | Build context filter |
