# Odoo.sh Parity Map — Insightpulseai/odoo

> Maps Odoo.sh features/constraints to our DigitalOcean on-prem equivalent.
> Gaps column identifies what we must close manually via GitHub Actions + scripts.
> Generated: 2026-03-02 | Source: `ssot/docs/odoo_docs.yaml`

---

## Parity Map

| Odoo.sh Feature | Odoo.sh Behavior | Our Equivalent | Gap | Action to close |
|----------------|-----------------|---------------|-----|-----------------|
| **Staging branch (fresh build from prod on each push)** | On each push to a staging branch, Odoo.sh restores a fresh copy of the prod DB, runs all custom module updates, and presents a live staging URL within minutes. | GitHub Actions SSH → `pg_dump` prod → `neutralize` → restore to `odoo_dev` → `odoo-bin -u all` → recycle staging container. | No automated fresh-from-prod restore on every push (manual trigger only). No ephemeral per-branch URLs — single shared `odoo_dev` database. | `.github/workflows/odoo-staging.yml`: add `workflow_dispatch` + `push` trigger; `scripts/odoo_stage_refresh.sh`: `pg_dump prod → neutralize → restore odoo_dev → -u all` |
| **Automatic daily/weekly/monthly backups (production)** | Keeps 7 daily, 4 weekly, 3 monthly encrypted backups of production DB including filestore, logs, and sessions — zero operator intervention. | `scripts/odoo_backup.sh` triggered by cron or GitHub Actions schedule; backups to DigitalOcean Spaces or local volume. | Rotation schedule (7d/4w/3m) may not be implemented; filestore and session snapshots may be missing; no automated offsite upload verification. | `scripts/odoo_backup.sh`: implement `pg_dump` + filestore tar + rotation logic; `.github/workflows/odoo-backup.yml`: `schedule: '0 2 * * *'`; upload to DO Spaces with lifecycle rules matching 7d/4w/3m retention |
| **Build log + test suite on every push** | Every push triggers a build; if tests enabled, Odoo.sh runs `--test-tags` and reports pass/fail in branch UI before promotion. | `.github/workflows/odoo-tests.yml` running `odoo-bin --test-enable --test-tags` on a test DB inside the CI runner. | CI tests run in GitHub-hosted runner, not against the actual DO droplet image; Docker image version drift can mask environment-specific failures. | `.github/workflows/odoo-tests.yml`: use same `Dockerfile` as `deploy/Dockerfile.odoo`; add `--test-tags +ipai` to scope to custom modules only |
| **Submodule auto-detection and addons_path injection** | Scans `.gitmodules`, clones each submodule, automatically appends submodule roots to `addons_path` — no manual config needed. | `.gitmodules` + `git submodule update --init` in CI/deploy + manual `addons_path` list in `odoo.conf`. | `addons_path` must be manually updated in `config/odoo/odoo.conf` each time a new OCA submodule is added; no automatic detection. | `scripts/generate_addons_path.sh`: scan `.gitmodules` → emit `addons_path` line; hook into deploy workflow to regenerate before container start |
| **Online editor (in-browser code editing on staging)** | VS Code-style in-browser editor connected to staging containers — edit module files and see live changes without SSH. | DevContainer via VS Code Remote SSH or GitHub Codespaces (`.devcontainer/` config). | Requires local VS Code + SSH key setup; no web-only fallback; Codespaces path exists but Colima profile split adds complexity. | `docs/runbooks/devcontainers/ONBOARDING.md`: document VS Code Remote SSH as primary path; `.devcontainer/devcontainer.json`: already configured per MEMORY DevContainer Root |
| **Cron throttling on idle databases** | Reduces cron job frequency when no users are active on a branch to conserve shared platform resources. | `max_cron_threads = 1` in `odoo.conf`; no dynamic throttling — cron runs at full frequency 24/7. | Always-on cron wastes CPU on the shared DO droplet during off-hours; no adaptive throttling. | `config/odoo/odoo.conf`: evaluate `max_cron_threads = 1` (already minimal); optional: systemd timer to pause cron worker at night via `odoo-bin --max-cron-threads 0` during off-hours |
| **Worker count tuning per branch type** | Automatically allocates workers by branch type: production = full allocation; staging = reduced; development = 1-2. | Single `workers = N` in `odoo.conf` shared across all deployments on the DO droplet. | No per-environment worker differentiation; staging and production share the same worker pool if run on the same droplet. | `config/odoo/odoo.conf.prod`: `workers=8`; `config/odoo/odoo.conf.staging`: `workers=2`; `deploy/odoo-prod.compose.yml`: mount correct conf per service profile |
| **Module installation scoping on dev builds** | Development branches can install only the branch's own modules, excluding submodule/OCA modules, to speed up build time. | `odoo-bin -i <module_list>` or `-u <module_list>` in CI scripts; no automatic scope limiting. | CI test runs may unnecessarily install/update all OCA modules, slowing test execution. | `.github/workflows/odoo-tests.yml`: use `-i $(cat addons/ipai/module_list.txt)` to scope install to `ipai_*` only during PR checks |
| **HTTPS / custom domain per branch** | Every branch gets an auto-provisioned HTTPS URL (e.g., `staging-<hash>.odoo.sh`); production branches support custom domain + auto Let's Encrypt SSL. | Single nginx vhost on DO droplet with Cloudflare-proxied DNS for `erp.insightpulseai.com`; staging uses a subdomain. | No per-branch ephemeral HTTPS URL; staging must share the main domain or use a manually configured subdomain. | `infra/dns/subdomain-registry.yaml`: add `staging.erp` A record; `deploy/nginx/odoo-staging.conf`: separate vhost on port 8070; Cloudflare: add staging subdomain via Terraform |

---

## Key constraints we model as explicit rules

| Odoo.sh constraint | Our equivalent |
|--------------------|----------------|
| `list_db = False` in production | `config/odoo/odoo.conf`: `list_db = False` |
| No direct DB access from modules | Odoo ORM only — no raw `psycopg2` connections in `ipai_*` |
| Outgoing email disabled in staging | `scripts/odoo_neutralize.sh` disables `ir.mail_server` after restore |
| No hardcoded admin passwords | Secrets in `.env` only; `scripts/odoo_neutralize.sh` resets passwords |
| `proxy_mode = True` behind nginx | `config/odoo/odoo.conf`: `proxy_mode = True` |
| Workers ≥ 2 for production | `config/odoo/odoo.conf`: `workers = N` (N ≥ 2, ≤ 2×CPU cores) |

---

## External API deprecation warning

**XML-RPC (`/xmlrpc/2/*`) and JSON-RPC 1 are deprecated in Odoo 19.0 and will be removed in Odoo 20 (estimated late 2026).**

All integrations using these endpoints must migrate to the JSON-2 API (`Authorization: Bearer <api_key>`) before the Odoo 20 release window.

Affected files to audit:
- `automations/n8n/workflows/*.json` — n8n Odoo credential nodes
- `scripts/odoo_api_client.py` — Python API client
- `supabase/functions/` — any Edge Function calling Odoo directly

---

## See also

- [`docs/dev/odoo/DOCS_INDEX.md`](DOCS_INDEX.md) — Full Odoo docs reference table
- [`ssot/docs/odoo_docs.yaml`](../../ssot/docs/odoo_docs.yaml) — Machine-readable catalog
- `config/odoo/odoo.conf` — Production configuration
- `scripts/odoo_neutralize.sh` — Staging DB neutralization script
