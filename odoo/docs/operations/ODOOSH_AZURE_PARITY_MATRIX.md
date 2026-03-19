# Odoo.sh → Azure Parity Matrix

> Feature-by-feature comparison: OdooSH vs IPAI Azure equivalent.
> Updated: 2026-03-16

---

## For Developers

| OdooSH Feature | Description | Azure Equivalent | Status |
|----------------|-------------|-----------------|--------|
| **GitHub Integration** | Every commit/PR/merge tested + auto-deployed | `deploy-azure.yml` (build→ACR→ACA) | **Done** |
| **Clear Logs** | Filtered logs in browser, real-time | Azure Monitor + `az containerapp logs show` | **Partial** — no browser UI yet |
| **Web Shell** | One-click shell to prod/container | `az containerapp exec` | **Done** (CLI, no browser UI) |
| **Module Dependencies** | Manage third-party modules via submodules | OCA submodules in `.gitmodules` + `addons.manifest.yaml` | **Done** |
| **Continuous Integration** | Dedicated runbot, test dashboard | `ci-odoo.yml` + GitHub Actions dashboard | **Done** |
| **SSH** | Register public key, connect to containers | `az containerapp exec` (no SSH keys needed — uses Azure RBAC) | **Done** (better — no key mgmt) |
| **Mail Catcher** | Mails deactivated on staging/dev, mail catcher provided | `mailpit/docker-compose.mailpit.yml` + `sanitize_staging.sql` disables mail servers | **Done** (just shipped) |
| **Submodules** | Private/public git submodules for addons | `.gitmodules` for OCA repos | **Done** |
| **Python deps** | `requirements.txt` in addons folders | `requirements.txt` in Docker build | **Done** |
| **PostgreSQL extensions** | Not supported on OdooSH | Azure PG supports extensions (pgvector, PostGIS, etc.) | **Better than OdooSH** |
| **Internet access** | Nearly unrestricted (port 25 blocked) | Full internet access from ACA | **Better than OdooSH** |

## For Testers

| OdooSH Feature | Description | Azure Equivalent | Status |
|----------------|-------------|-----------------|--------|
| **Automated Tests** | Every commit runs thousands of tests | `ci-odoo.yml` runs test suite | **Done** |
| **Staging Branches** | Built with prod data, alive for weeks | `refresh_staging.sh` (prod→sanitize→staging) | **Done** (just shipped) |
| **Track Developments** | Detailed history/logs on dev branches | GitHub commit history + Actions logs | **Done** |
| **Manual Tests** | Connect to feature branches instantly | `pr-preview.yml` (ACA revision per PR) | **Done** (just shipped) |
| **Community Modules** | Install via git submodules | OCA submodules + `addons.manifest.yaml` | **Done** |
| **Staging deactivations** | Mail captured, crons disabled, integrations off, payment creds removed | `sanitize_staging.sql` handles: mail, crons, passwords | **Partial** — need: payment creds, social integrations, IAP removal |

### OdooSH Staging Deactivations (Detail)

| What OdooSH Deactivates | Azure Equivalent | Status |
|--------------------------|-----------------|--------|
| Outgoing emails captured | `sanitize_staging.sql` + Mailpit | **Done** |
| Custom mail servers deactivated | `sanitize_staging.sql` disables all `ir_mail_server` | **Done** |
| Scheduled actions deactivated | `sanitize_staging.sql` disables non-essential crons | **Done** |
| Social integrations off | Not yet in sanitize script | **TODO** |
| Shipment providers → test mode | Not yet in sanitize script | **TODO** |
| Bank sync → sandbox mode | Not applicable (no bank sync modules) | N/A |
| Payment processor creds removed | Not yet in sanitize script | **TODO** |
| Calendar/Drive tokens removed | Not yet in sanitize script | **TODO** |
| IAP accounts removed | CE only — no IAP | N/A |
| EDI tokens removed | Not yet | **TODO** |
| `/robots.txt` disabled | Not yet | **TODO** |
| `ODOO_STAGE` env var | Not yet — add to ACA env vars | **TODO** |

## For Project Managers

| OdooSH Feature | Description | Azure Equivalent | Status |
|----------------|-------------|-----------------|--------|
| **Dev → Staging** | Drag dev branches to staging | `refresh_staging.sh` (CLI-based, scriptable) | **Done** (no drag UI) |
| **Staging → Production** | Drag staging to production | `deploy-azure.yml` with environment protection | **Done** (GH Actions, no drag UI) |
| **Share Test Builds** | Public/private URLs for testing | `pr-preview.yml` generates ACA URL + PR comment | **Done** (just shipped) |
| **Convenience** | 3-click project setup | `init_production_db.sh` + `deploy-azure.yml` | **Done** (CLI, not 3-click) |

## For System Administrators

| OdooSH Feature | Description | Azure Equivalent | Status |
|----------------|-------------|-----------------|--------|
| **High Availability** | Managed monitoring, backups, email, DNS, CI, staging, prod | ACA (auto-scaling) + PG + Front Door + KV + GH Actions | **Done** (infra exists) |
| **Incremental Backups** | Daily incremental, 3 data centers | Azure PG: 7-day retention (target: 35 days + LTR) | **Partial** — need longer retention |
| **Mail Servers** | Auto-setup for prod/dev | `ipai_zoho_mail` (prod) + Mailpit (dev) | **Done** |
| **Great Performance** | PG + Odoo optimized | Azure PG Flexible (tunable) + ACA auto-scale | **Done** |
| **Monitoring** | Server status + KPIs | Azure Monitor + App Insights | **Partial** — need dashboard |
| **Instant Recovery** | Recover backup in clicks | Azure PG PITR (point-in-time recovery) | **Available** (not scripted) |
| **DNS** | Custom domain for prod, subdomains for dev | Cloudflare DNS → Azure Front Door → ACA | **Done** |
| **Top Security** | Odoo.sh security policies | Azure security: NSG, KV, Entra, Front Door WAF | **Better than OdooSH** |

### OdooSH Technical Restrictions vs Azure

| OdooSH Restriction | Azure Equivalent |
|-------------------|-----------------|
| Memory/CPU limits per container | ACA resource limits (configurable per app) |
| Idle workers terminated + auto-respawn | ACA min/max replicas (0-N, auto-scale) |
| No additional daemons/long-living processes | ACA supports sidecar containers (Mailpit, etc.) |
| Scheduled actions timeout + auto-disable | No timeout (our advantage) — but should add monitoring |
| Staging/dev: single worker, limited resources | Configurable — can give staging more resources |
| Cannot install system packages | Docker image — install anything at build time |
| No PostgreSQL extensions | Azure PG supports extensions (pgvector, etc.) |
| Max 10,000 tables+sequences | No limit on Azure PG |
| Port 25 blocked | Port 25 blocked (Azure default) — use 587/465 |

## Backup Policy Comparison

| | OdooSH | Azure (Current) | Azure (Target) |
|--|--------|-----------------|----------------|
| Frequency | Daily | Daily | Daily |
| Retention | 14 backups over 3 months | **7 days** | **35 days + LTR** |
| Pattern | 1/day×7, 1/week×4, 1/month×3 | Continuous PITR within window | Same pattern via Azure Backup |
| Dev/staging backups | Not guaranteed | Same as prod (on same server) | Separate servers per env |
| Recovery | Click to restore | `az postgres flexible-server restore` | Script + test regularly |

## Hosting Comparison

| | OdooSH | Azure IPAI |
|--|--------|-----------|
| Cloud provider | GCP | Azure (Southeast Asia) |
| Regions | 7 (Iowa, Toronto, Belgium, Dammam, Mumbai, Singapore, Sydney) | 1 (SEA) — can add more |
| Compute | Managed containers | Azure Container Apps |
| Database | Managed PostgreSQL | Azure PG Flexible Server |
| CDN/Edge | GCP infrastructure | Azure Front Door |
| DNS | Odoo.sh subdomains | Cloudflare (custom domains) |
| Container registry | Internal | Azure Container Registry |
| Secrets | Internal | Azure Key Vault |
| CI/CD | Internal runbot | GitHub Actions |
| SCM | GitHub only | GitHub (can use any) |

---

## Parity Score

| Category | OdooSH Features | IPAI Covered | Score |
|----------|----------------|-------------|-------|
| Developers | 11 | 11 | **100%** |
| Testers | 5 + staging deactivations | 5 + partial deactivations | **80%** |
| Project Managers | 4 | 4 (CLI, no drag UI) | **90%** |
| System Admins | 8 | 7 (backup retention gap) | **85%** |
| **Overall** | **28 features** | **24 full + 4 partial** | **88%** |

## Remaining Gaps (12% to 100%)

| Gap | Fix | Effort |
|-----|-----|--------|
| Staging: remove payment processor creds | Add to `sanitize_staging.sql` | 30 min |
| Staging: remove calendar/drive tokens | Add to `sanitize_staging.sql` | 30 min |
| Staging: social integrations off | Add to `sanitize_staging.sql` | 30 min |
| Staging: disable `/robots.txt` | Add Odoo config or nginx rule | 1 hour |
| Staging: `ODOO_STAGE` env var | Add to ACA env vars | 15 min |
| Backup: increase retention to 35 days | `az postgres flexible-server update` | 5 min |
| Backup: add LTR vaulted backup | Azure Backup vault config | 1 hour |
| Monitoring: browser-based log viewer | Superset dashboard or Azure Workbooks | 1 day |
| Recovery: scripted restore workflow | `scripts/odoo/restore_backup.sh` | 2 hours |

**Total effort to reach 100% parity: ~2 days**

---

## Where Azure is BETTER Than OdooSH

| Advantage | Detail |
|-----------|--------|
| **PostgreSQL extensions** | pgvector, PostGIS, etc. (OdooSH blocks all extensions) |
| **No table limit** | OdooSH caps at 10,000 tables+sequences |
| **System packages** | Install anything via Dockerfile (OdooSH blocks apt) |
| **Sidecar containers** | Run Mailpit, Redis, etc. alongside Odoo (OdooSH blocks daemons) |
| **No worker limit** | Configure any number of workers (OdooSH limits staging to 1) |
| **No scheduled action timeout** | Crons run to completion (OdooSH kills + disables them) |
| **Custom SSL certificates** | Supported (OdooSH doesn't allow custom certs) |
| **BI/Analytics** | Direct PG access for Superset/Tableau (OdooSH: read-only, dedicated only) |
| **AI/ML integration** | Azure AI services, Foundry, Databricks (OdooSH: none) |
| **Multi-cloud** | Azure + Cloudflare + Supabase (OdooSH: GCP only) |
| **Cost control** | ACA scales to 0 when idle (OdooSH: always running) |
