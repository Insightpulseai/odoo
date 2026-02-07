# Domain Health Audit — 2026-02-07

> Create these as GitHub issues. Each section = one issue.
> Labels suggested per issue. Priority: P0 = create immediately, P1 = this sprint, P2 = next sprint.

---

## Issue 1: CSS/SCSS broken on both insightpulseai.com and erp.insightpulseai.com

**Labels**: `bug`, `P0`

### Problem

Both `insightpulseai.com` and `erp.insightpulseai.com` render completely unstyled (zero CSS). Content loads but no stylesheets are applied. Confirmed via mobile screenshots (2026-02-07).

### Likely Root Causes

**1. Filestore lost during Odoo 18→19 migration (most likely)**

Odoo stores compiled SCSS→CSS bundles in `/var/lib/odoo/filestore/<db>/`. If the filestore volume was recreated or the database name changed during the v18→v19 upgrade, all compiled asset bundles are gone.

- Dev compose volume: `odoo_data:/var/lib/odoo`
- Prod compose volume: `odoo-filestore:/var/lib/odoo`
- If volume name changed or was wiped → all assets lost

**2. Odoo 19 asset pipeline incompatibility**

Odoo 19 changed the asset bundling system. Old v18 compiled bundles in the filestore are invalid and need regeneration.

**3. Missing SCSS source files in theme modules**

- `ipai_theme_tbwa/views/assets.xml` references `static/src/scss/tbwa_backend.scss` — **file does not exist**
- `ipai_theme_copilot/views/assets.xml` references `static/src/scss/backend.scss` + `frontend.scss` — **files do not exist**
- No `static/` directory exists in either module

**4. File permissions**

SCSS compilation requires write access to filestore. If Odoo process (UID 100) can't write to `/var/lib/odoo`, compilation fails silently.

### Fix (in priority order)

```bash
# 1. Force asset recompilation (regenerates all CSS from SCSS)
docker compose exec -T web odoo -d odoo -u web --stop-after-init

# 2. Verify filestore exists and has content
docker compose exec web ls -la /var/lib/odoo/filestore/

# 3. If filestore is empty/missing, check volume
docker volume inspect odoo-filestore

# 4. Fix permissions if needed
docker compose exec web chown -R odoo:odoo /var/lib/odoo

# 5. Check Odoo logs for SCSS compilation errors
docker compose logs web 2>&1 | grep -i "scss\|asset\|style\|compile"
```

---

## Issue 2: insightpulseai.com should serve Next.js app, not Odoo

**Labels**: `bug`, `infra`, `P0`

### Problem

`insightpulseai.com` (main domain) is serving Odoo website content instead of the Next.js marketing site (`apps/web/`). Both `insightpulseai.com` and `erp.insightpulseai.com` show identical Odoo content.

### Expected Architecture

| Domain | Should Serve | Technology |
|--------|-------------|-----------|
| `insightpulseai.com` | Marketing site | Next.js on Vercel (`apps/web/`) |
| `erp.insightpulseai.com` | Odoo ERP backend | Odoo CE 19 (self-hosted DO) |

### Fix

In Cloudflare DNS:
- `insightpulseai.com` → CNAME to Vercel (`cname.vercel-dns.com`)
- `erp.insightpulseai.com` → A record to DO droplet IP

---

## Issue 3: ipai_theme_tbwa and ipai_theme_copilot have missing SCSS files

**Labels**: `bug`, `odoo`, `P1`

### Problem

Both theme modules declare SCSS assets in `views/assets.xml` that reference files that don't exist:

| Module | Missing File | Reference |
|--------|-------------|-----------|
| `ipai_theme_tbwa` | `static/src/scss/tbwa_backend.scss` | `views/assets.xml` line 5 |
| `ipai_theme_copilot` | `static/src/scss/backend.scss` | `views/assets.xml` line 6 |
| `ipai_theme_copilot` | `static/src/scss/frontend.scss` | `views/assets.xml` line 7 |

Neither module has a `static/` directory at all.

### Fix

Either:
1. Create the SCSS files with proper theme styles
2. Or remove the asset references from `views/assets.xml` if themes are not ready
3. Or set `installable: False` in `__manifest__.py` to prevent installation

---

## Issue 4: Stale database name `odoo_core` in active configs

**Labels**: `chore`, `config-drift`, `P1`

### Problem

Multiple active config files reference `odoo_core` as the database name. The canonical databases are: `odoo` (prod) and `odoo_dev` (local). No other DB names should exist.

### Files to fix

| File | Current | Should Be |
|------|---------|-----------|
| `config/odoo-core.conf` | `db_name = odoo_core` | `db_name = odoo` |
| `CLAUDE_CODE_WEB.md` | `DB_NAME=odoo_core` | `DB_NAME=odoo` |
| `ship_v1_1_0.sh` | `${ODOO_DB:=odoo_core}` | `${ODOO_DB:=odoo}` |
| `stack/odoo19_stack.yaml` | `name: "odoo_core"` | `name: "odoo"` |
| `VERIFY.md` | Multiple `-d odoo_core` | `-d odoo` |
| `infra/deploy/docker-compose.ce19.yml` | `${POSTGRES_DB:-odoo_ce19}` | `${POSTGRES_DB:-odoo}` |

---

## Issue 5: Stale Mailgun references in active configs (should be Zoho Mail)

**Labels**: `chore`, `config-drift`, `P1`

### Problem

Mail was migrated from Mailgun to Zoho Mail, but several active configs still reference Mailgun:

| File | Issue |
|------|-------|
| `.env.example` (lines 101-108) | Mailgun SMTP config section |
| `infra/deploy/odoo.conf` (line 29-38) | `smtp.mailgun.org:2525` |
| `.env.smtp.example` | Lists Mailgun as provider option |
| `config/integrations/integration_manifest.yaml` | `mg.insightpulseai.com` references |
| `README.md` (lines 295, 305-307, 326, 350) | Mailgun deployment docs |

### Fix

Replace all with Zoho Mail:
```
SMTP Host: smtp.zoho.com
SMTP Port: 587
Encryption: STARTTLS
User: noreply@insightpulseai.com
```

---

## Issue 6: Stale Mattermost references in active configs

**Labels**: `chore`, `config-drift`, `P2`

### Problem

Mattermost was deprecated 2026-01-28 (replaced by Slack), but references remain in:

| File | Issue |
|------|-------|
| `.env.example` (lines 96-99) | Mattermost config section |
| `CLAUDE_CODE_WEB.md` | Mattermost URL in docs |
| `addons/ipai/README.md` (line 72) | Lists `ipai_mattermost_connector` |
| `SITEMAP.md` (line 650) | References `ipai_mattermost_connector` |
| `workflows/odoo/W403_AP_AGING_HEATMAP.json` | Mattermost webhook URLs |
| `docs/modules/ipai_mattermost_connector.md` | Full module documentation |

### Fix

Remove Mattermost config sections, replace webhook references with Slack equivalents.

---

## Issue 7: Nginx config file named `.net` but content references `.com`

**Labels**: `chore`, `infra`, `P2`

### Problem

`infra/deploy/nginx/erp.insightpulseai.net.conf` — filename uses old `.net` domain, but all content inside references `.com`. Also:

- Staging proxy block references `odoo-staging:8069` container that doesn't exist
- No nginx config exists for the root `insightpulseai.com` domain

### Fix

1. Rename: `erp.insightpulseai.net.conf` → `erp.insightpulseai.com.conf`
2. Fix staging proxy: `odoo-staging` → proper container name or `127.0.0.1:8169`
3. Create nginx config for root domain (or confirm Cloudflare handles routing to Vercel)

---

## Issue 8: Activate pg_cron scheduled jobs in Supabase

**Labels**: `enhancement`, `supabase`, `P2`

### Problem

4 cron jobs are seeded in Supabase `cron_jobs` table but pg_cron extension is not activated. These jobs handle:

| Job | Schedule | Purpose |
|-----|----------|---------|
| BIR compliance alerts | Daily 8 AM MNL | Regulatory compliance |
| PPM reminders | Weekly Monday 9 AM MNL | Project management |
| Health check | Every 15 min | Infrastructure monitoring |
| Stale data cleanup | Daily 2 AM MNL | Data hygiene |

### Fix

```sql
-- Activate in Supabase SQL Editor
SELECT cron.schedule('bir-alerts', '0 8 * * *', $$SELECT process_bir_alerts()$$);
SELECT cron.schedule('ppm-reminders', '0 9 * * 1', $$SELECT process_ppm_reminders()$$);
SELECT cron.schedule('health-check', '*/15 * * * *', $$SELECT run_health_check()$$);
SELECT cron.schedule('stale-cleanup', '0 2 * * *', $$SELECT cleanup_stale_data()$$);
```

---

## Issue 9: Activate Supabase Storage for document management

**Labels**: `enhancement`, `supabase`, `P2`

### Problem

Supabase Storage is configured (50MiB limit) but has zero usage. BIR compliance documents, report exports, and attachments are not leveraging this included-with-Pro feature.

### Fix

Create buckets and wire upload routes:
- `documents` — BIR forms, compliance exports (authenticated)
- `attachments` — Odoo record attachments (authenticated)
- `exports` — Report exports, CSV/PDF downloads (signed URLs)
- `public` — Landing page assets, logos

---

## Summary

| # | Issue | Priority | Category |
|---|-------|----------|----------|
| 1 | CSS/SCSS broken on both domains | P0 | Bug — filestore/migration |
| 2 | Main domain routing wrong | P0 | Bug — DNS/infra |
| 3 | Missing SCSS in theme modules | P1 | Bug — Odoo modules |
| 4 | Stale `odoo_core` DB name | P1 | Config drift |
| 5 | Stale Mailgun references | P1 | Config drift |
| 6 | Stale Mattermost references | P2 | Config drift |
| 7 | Nginx config naming + staging | P2 | Infra |
| 8 | Activate pg_cron jobs | P2 | Enhancement |
| 9 | Activate Supabase Storage | P2 | Enhancement |
