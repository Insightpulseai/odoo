---
name: administration
description: Server deployment, hosting management, database operations, upgrades, and platform administration for Odoo instances
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Administration -- Odoo 19.0 Skill Reference

## Overview

Odoo Administration covers the full lifecycle of hosting, deploying, managing, and upgrading Odoo databases across three hosting platforms: Odoo Online (SaaS), Odoo.sh (PaaS), and On-Premise. It includes database management, version upgrades, hosting transfers, mobile access, email gateway configuration, and security hardening. This reference targets system administrators, DevOps engineers, and IT managers responsible for Odoo infrastructure.

## Key Concepts

- **Odoo Online**: Fully managed SaaS hosting by Odoo. Databases accessed via `<name>.odoo.com`. No custom modules or Odoo Apps Store modules allowed.
- **Odoo.sh**: PaaS platform with GitHub integration, CI/CD, three branch stages (Production, Staging, Development), shell access, and monitoring.
- **On-Premise**: Self-hosted Odoo on your own infrastructure. Full control over server, database, and modules.
- **Database Manager**: Web UI at `/web/database/manager` (on-premise) or `odoo.com/my/databases` (Odoo Online) for creating, duplicating, backing up, and deleting databases.
- **Neutralized Database**: A non-production copy with scheduled actions, outgoing emails, payment providers, bank sync, and IAP tokens disabled. Used for testing and staging.
- **Upgrade**: Moving a database from an older Odoo version to a newer one. Free for Enterprise subscribers. Handled via `upgrade.odoo.com`.
- **Standard Support**: Bug fixes, security patches, and helpdesk support for 3 years per major version.
- **Extended Support**: Additional helpdesk support and bug fixes beyond 3 years (extra fee).
- **Major Version**: Released annually (e.g., 17.0, 18.0, 19.0). Supported on all platforms.
- **Minor/SaaS Version**: Intermediary releases (e.g., 18.2, 18.3) available only on Odoo Online.
- **PWA (Progressive Web App)**: Recommended mobile access method. Supports push notifications and SSO.
- **Build (Odoo.sh)**: A database loaded by an Odoo server running a specific Git revision in a container. Statuses: successful (green), almost successful (yellow), failed (red).
- **Branch Stage (Odoo.sh)**: Production (one per project, runs live database), Staging (neutralized copy of production), Development (fresh database with demo data and unit tests).
- **Email Gateway**: The `odoo-mailgate.py` script that injects incoming emails into Odoo via XML-RPC.
- **dbfilter**: Server config option that selects which database to serve based on hostname pattern matching.
- **admin_passwd**: Master password protecting database management screens. Must be strong and randomly generated.
- **Multi-processing server**: Production-recommended server mode using `--workers` flag. Enables proper hardware utilization (bypasses Python GIL).

## Core Workflows

### 1. Deploy Odoo On-Premise (Source Install)

1. Install Python 3.10+ and PostgreSQL 13+.
2. Clone the Community (and optionally Enterprise) Git repositories:
   ```bash
   git clone https://github.com/odoo/odoo.git
   git clone https://github.com/odoo/enterprise.git  # Enterprise only
   ```
3. Create a PostgreSQL user (non-superuser with `createdb`):
   ```bash
   sudo -u postgres createuser -d -R -S $USER
   createdb $USER
   ```
4. Install Python dependencies:
   ```bash
   cd /path/to/odoo
   pip install -r requirements.txt
   ```
5. Install `wkhtmltopdf` 0.12.6 manually (required for PDF reports with headers/footers).
6. Run Odoo:
   ```bash
   python3 odoo-bin --addons-path=addons,/path/to/enterprise -d mydb
   ```
7. Access at `http://localhost:8069`. Default login: `admin` / `admin`.

### 2. Configure Production Deployment

1. Set `dbfilter` in config file to match hostname:
   ```ini
   [options]
   dbfilter = ^%d$
   ```
2. Set a strong `admin_passwd`:
   ```ini
   admin_passwd = <randomly-generated-string>
   ```
3. Enable multi-processing:
   ```ini
   workers = 8
   max_cron_threads = 1
   limit_memory_hard = 1677721600
   limit_memory_soft = 629145600
   limit_time_cpu = 600
   limit_time_real = 1200
   ```
   Worker formula: `(#CPU * 2) + 1`. Each worker handles ~6 concurrent users.
4. Configure Nginx as reverse proxy with HTTPS:
   - Redirect HTTP to HTTPS.
   - Proxy `/websocket/` to the gevent port (default 8072).
   - Proxy all other requests to port 8069.
   - Enable `proxy_mode = True` in Odoo config.
   - Add `Strict-Transport-Security` header.
   - Set `proxy_cookie_flags session_id samesite=lax secure`.
5. Set `list_db = False` to disable database listing in production.
6. Optionally enable X-Sendfile (Apache) or X-Accel (Nginx) for static file serving.

### 3. Manage an Odoo Online Database

1. Sign in to the [database manager](https://www.odoo.com/my/databases).
2. Available operations per database:
   - **Domain Names**: Configure custom domains.
   - **Tags**: Add labels for organization.
   - **Hide**: Permanently remove from manager (still accessible by URL).
   - **Manage**: Switch plans, Upgrade, Rename, Duplicate, Download Backup, View Admin Activity Logs, Transfer Ownership, Delete.
3. Duplicates: Created with testing mode enabled by default (external actions disabled). Expire after 15 days. Max 5 per database.
4. Programmatic database listing via JSON-2 API:
   ```python
   requests.post(
       "https://www.odoo.com/json/2/odoo.database/list",
       headers={
           "Authorization": f"bearer {APIKEY}",
           "X-Odoo-Database": "openerp",
       },
       json={},
   )
   ```

### 4. Work with Odoo.sh Branches and Builds

1. **Production branch**: One per project. Pushes trigger server restart with new revision. Module updates triggered by incrementing version in `__manifest__.py`. Auto-rollback on failure. Backups: 7 daily + 4 weekly + 3 monthly.
2. **Staging branch**: Creates neutralized copy of production database on each push. Scheduled actions disabled, emails intercepted by mail catcher, payment providers in test mode. Databases last up to 3 months.
3. **Development branch**: Creates fresh database with demo data. Unit tests run by default. Databases last ~3 days.
4. **Merging**: Drag-and-drop branches in the UI, or use `git merge` locally. Merging staging to production merges source code only (not database changes).
5. **Tabs**: History, Mails (mail catcher), Shell (container terminal), Editor (online IDE), Monitor (CPU/memory/storage/HTTP metrics), Logs, Backups, Upgrade, Tools (code profiler), Settings.
6. **Shell commands**: `odoo-bin shell`, `odoo-update`, `odoosh-restart`, `odoosh-storage`, `psql`, `lnav ~/logs/odoo.log`, `ncdu`.

### 5. Upgrade a Database

1. **Request a test upgrade**:
   - *Odoo Online*: Database manager > Manage > Upgrade. Select target version, email, purpose=Test.
   - *Odoo.sh*: Use the Upgrade tab on a staging branch. Latest production backup is sent to upgrade platform.
   - *On-premise*: `python <(curl -s https://upgrade.odoo.com/upgrade) test -d <dbname> -t <target_version>`
2. **Test thoroughly**: Verify views, reports, workflows, mail templates, translations, search filters, data exports, integrations, automated actions.
3. **Upgrade production**:
   - *Odoo Online*: Same as test but set purpose=Production. Database unavailable during upgrade. Irreversible.
   - *Odoo.sh*: Use Upgrade tab on Production branch. Triggered on next commit. Auto-rollback on failure.
   - *On-premise*: `python <(curl -s https://upgrade.odoo.com/upgrade) production -d <dbname> -t <target_version>`
4. Report issues via [Odoo Support](https://www.odoo.com/help?stage=migration) (testing) or [post-upgrade support](https://www.odoo.com/help?stage=post_upgrade) (production).

### 6. Transfer Between Hosting Platforms

**On-premise to Odoo Online**:
1. Duplicate database, uninstall non-standard apps.
2. Create dump with filestore.
3. Submit support ticket with subscription number, desired URL, and dump.

**On-premise to Odoo.sh**:
1. Follow Odoo.sh Import Database workflow.

**Odoo Online to On-premise**:
1. Download backup from database manager.
2. Restore via on-premise database manager.

**Odoo Online to Odoo.sh**:
1. Download backup from database manager.
2. Import via Odoo.sh Backups tab.

**Odoo.sh to Odoo Online**:
1. Uninstall non-standard apps in staging first, then production.
2. Submit support ticket with subscription, branch, region, admins, and timeline.

**Odoo.sh to On-premise**:
1. Download production backup from Odoo.sh Backups tab.
2. Restore on local server.

## Technical Reference

### Server Configuration (odoo.conf)

| Parameter | Purpose | Default |
|---|---|---|
| `dbfilter` | Regex to filter databases by hostname | (none) |
| `db_host` | PostgreSQL server address | localhost (UNIX socket) |
| `db_port` | PostgreSQL port | 5432 |
| `db_user` | PostgreSQL user | (system user) |
| `db_password` | PostgreSQL password | (none) |
| `db_sslmode` | SSL mode for PG connection | (none) |
| `admin_passwd` | Master password for DB management | admin |
| `list_db` | Enable/disable database listing | True |
| `workers` | Number of HTTP worker processes | 0 (multi-threaded) |
| `max_cron_threads` | Cron worker count | 2 |
| `limit_memory_hard` | Hard memory limit per worker (bytes) | 2684354560 |
| `limit_memory_soft` | Soft memory limit per worker (bytes) | 2147483648 |
| `limit_time_cpu` | CPU time limit per request (seconds) | 60 |
| `limit_time_real` | Real time limit per request (seconds) | 120 |
| `limit_request` | Max requests before worker recycle | 8196 |
| `proxy_mode` | Trust X-Forwarded-* headers | False |
| `addons-path` | Comma-separated paths to addon directories | addons |
| `http_port` | HTTP listening port | 8069 |
| `gevent-port` | Gevent (websocket/livechat) port | 8072 |
| `x-sendfile` | Enable X-Sendfile/X-Accel for static files | False |
| `no-http` | Disable HTTP server (cron-only mode) | False |

### Nginx Configuration (Key Blocks)

```nginx
upstream odoo { server 127.0.0.1:8069; }
upstream odoochat { server 127.0.0.1:8072; }

server {
    listen 443 ssl;
    location /websocket {
        proxy_pass http://odoochat;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header X-Forwarded-Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location / {
        proxy_pass http://odoo;
        proxy_set_header X-Forwarded-Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Email Gateway (Postfix)

```text
# /etc/aliases
email@address: "|/odoo-directory/addons/mail/static/scripts/odoo-mailgate.py -d <database-name> -u <userid> -p <password>"
```

### Odoo.sh Backup Retention

| Stage | Automatic | Manual |
|---|---|---|
| Production | 7 daily + 4 weekly + 3 monthly | Yes (retained 3 days, max 5/day) |
| Staging | No | Yes (retained 3 days, max 5/day) |
| Development | No | No |

### Version Support Timeline

| Version | Release | End of Standard Support |
|---|---|---|
| **Odoo 19.0** | September 2025 | September 2028 (planned) |
| **Odoo 18.0** | October 2024 | September 2027 (planned) |
| **Odoo 17.0** | November 2023 | September 2026 (planned) |
| **Odoo 16.0** | October 2022 | September 2025 |

Minor/SaaS versions (e.g., 18.2, 18.3, 18.4) are Odoo Online only and not eligible for extended support.

## API / RPC Patterns

### List Databases (Odoo Online JSON-2 API)

```python
import requests

APIKEY = "your_apikey"
response = requests.post(
    "https://www.odoo.com/json/2/odoo.database/list",
    headers={
        "Authorization": f"bearer {APIKEY}",
        "X-Odoo-Database": "openerp",
    },
    json={},
)
```

### Upgrade CLI (On-Premise)

```bash
# Request test upgrade
python <(curl -s https://upgrade.odoo.com/upgrade) test -d mydb -t 19.0

# Request production upgrade
python <(curl -s https://upgrade.odoo.com/upgrade) production -d mydb -t 19.0

# Display help
python <(curl -s https://upgrade.odoo.com/upgrade) --help
```

Requirements: Linux (or WSL), PostgreSQL client access configured for the executing user, outbound TCP 443 + ports 32768-60999 open.

### Email Gateway Script

```bash
/odoo-directory/addons/mail/static/scripts/odoo-mailgate.py \
    -d <database-name> \
    -u <userid> \
    -p <password>
```

Invoked by MTA (Postfix/Exim) for each incoming email. Connects to Odoo via XML-RPC and calls `MailThread.message_process()`.

## Version Notes (19.0)

- **PostgreSQL 13 minimum** required (was 12 in Odoo 17/18).
- **Python 3.10+ minimum** (unchanged from 17.0).
- **Odoo 19.0 standard support** runs through September 2028.
- **Upgrade platform** services endpoint for Odoo 18.0+: `services.odoo.com` on port 80 (was `services.openerp.com` for 17.0 and below).
- **Odoo Online Rolling Release**: mandatory upgrade for minor versions within weeks of next release; automatic upgrade for major versions every 2 years.
- **Odoo.sh**: After 3 years of standard support, 2 additional years to complete upgrade before enforcement.
- **On-Premise**: No forced upgrade, but staying on unsupported versions not recommended.

<!-- TODO: Specific feature-level breaking changes vs 18.0 not enumerated in admin docs -->

## Common Pitfalls

- **dbfilter not set in multi-database production**: Website, portal, and non-logged-in features break. Always set `dbfilter` when `website` is installed or multiple databases exist.
- **admin_passwd left as default 'admin'**: Exposes database management screens to trivial attack. Generate a random 32+ character password immediately.
- **Odoo Online intermediary versions cannot transfer directly**: Databases on minor versions (e.g., 16.3) must be upgraded to the next major version before transferring to Odoo.sh or on-premise.
- **Timing-based automation rules running retroactively on Odoo.sh upgrades**: When upgrading, the `Automation Rules: check and execute` scheduled action must be manually run first to set the initial timestamp; otherwise rules may fire on historical records.
- **Database Manager exposed on production**: Disable with `list_db = False` and block `/web/database` routes in your reverse proxy. The DB manager is a development tool, not production-ready.
