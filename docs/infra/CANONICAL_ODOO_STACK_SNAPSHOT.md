# CANONICAL_ODOO_STACK_SNAPSHOT.md

**Purpose**: Single Source of Truth for InsightPulse AI Odoo Stack
**Status**: PRODUCTION
**Last Updated**: 2026-01-28
**Maintenance**: Update this file when infrastructure changes; agents must read this before emitting any DevOps commands

---

## 1. Hosts / DNS

**Primary Droplet**: 178.128.112.214 (DigitalOcean SGP1)

### Core A Records
All app subdomains terminate on the same droplet, demultiplexed by nginx virtual hosts:

| Subdomain | Type | Target | Service |
|-----------|------|--------|---------|
| @ | A | 178.128.112.214 | Root site |
| www | CNAME | insightpulseai.net | Canonical WWW alias |
| erp | A | 178.128.112.214 | Odoo production |
| erp.staging | A | 178.128.112.214 | Odoo staging |
| n8n | A | 178.128.112.214 | n8n automation |
| mcp | A | 178.128.112.214 | MCP tools hub |
| auth | A | 178.128.112.214 | Auth/IdP/SSO |
| superset | A | 178.128.112.214 | Apache Superset BI |

### Mailgun DNS (mg.insightpulseai.net)

**MX Records**:
| Host | Priority | Value |
|------|----------|-------|
| mg | 10 | mxa.mailgun.org |
| mg | 10 | mxb.mailgun.org |

**Authentication**:
| Record Type | Host | Value |
|-------------|------|-------|
| SPF | mg | `v=spf1 include:mailgun.org ~all` |
| DKIM | pic._domainkey.mg | `k=rsa; p=...` (from Mailgun) |
| DMARC | _dmarc.mg | `v=DMARC1; p=none; rua=...` |

**Root Domain Email**:
| Record Type | Host | Value |
|-------------|------|-------|
| SPF | @ | `v=spf1 include:mailgun.org ~all` |
| DMARC | _dmarc | `v=DMARC1; p=none; rua=mailto:3651085@dmarc.mailgun.org` |

**Security**:
| Record Type | Value |
|-------------|-------|
| CAA | `0 issue "letsencrypt.org"` |

---

## 2. Nginx Layout (178.128.112.214)

### Container Architecture
- **nginx-prod-v2**: Nginx reverse proxy running in Docker
- **Ports**: 80 (HTTP redirect), 443 (HTTPS)
- **Config Location**: `/etc/nginx/conf.d/` (inside container)

### TLS Certificates (Let's Encrypt)
**Storage**: `/etc/letsencrypt/live/` (host filesystem, mounted read-only to nginx container)

**Certificates**:
| Domain | Certificate Path | Expiry | SANs |
|--------|------------------|--------|------|
| erp.insightpulseai.net | `/etc/letsencrypt/live/erp.insightpulseai.net/fullchain.pem` | 2026-04-08 | erp, n8n, superset |
| erp.staging.insightpulseai.net | `/etc/letsencrypt/live/erp.staging.insightpulseai.net/` | (Let's Encrypt managed) | staging |

**Renewal**: Automated via certbot (systemd timer or cron)

### Virtual Hosts

**Production** (`erp.insightpulseai.net`):
```nginx
upstream odoo {
    server odoo:8069;
}

upstream odoo_im {
    server odoo:8072;
}

server {
    listen 443 ssl http2;
    server_name erp.insightpulseai.net;

    ssl_certificate /etc/letsencrypt/live/erp.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.net/privkey.pem;

    client_max_body_size 100M;
    proxy_read_timeout 720s;

    location / {
        proxy_pass http://odoo;
    }

    location /longpolling {
        proxy_pass http://odoo_im;
    }

    location ~* /web/static/ {
        proxy_pass http://odoo;
        expires 864000;
    }
}
```

**Staging** (`erp.staging.insightpulseai.net`):
- Same structure as production
- Upstream: `odoo-staging:8069`
- Visual indicator: `X-Environment: STAGING` header

---

## 3. Odoo Stack (Docker Compose)

### Services

**odoo-prod** (Production):
- Image: `odoo:18.0` or custom build
- Port: 8069 (HTTP), 8072 (longpolling)
- Database: DigitalOcean Managed PostgreSQL
- Config: `/etc/odoo/odoo.conf`
- Addons: `/mnt/extra-addons/ipai`, `/mnt/extra-addons/external/oca`

**odoo-staging** (Staging):
- Same image as production
- Port: 8069, 8072
- Database: Separate staging database (sanitized copy)
- Purpose: Pre-production validation

**postgres** (Development only):
- Image: `postgres:16-alpine`
- Port: 5432
- Storage: Docker volume `pgdata`
- Note: Production uses DigitalOcean Managed PostgreSQL

**nginx-prod-v2** (Reverse Proxy):
- Image: `nginx:alpine` or custom build
- Ports: 80, 443
- Config: `/etc/nginx/conf.d/odoo.conf`
- Certificates: `/etc/letsencrypt` (read-only mount)

**redis** (Session Store):
- Image: `redis:alpine`
- Port: 6379
- Purpose: Odoo session storage

### Odoo Configuration

**File**: `/etc/odoo/odoo.conf` (inside container)

**Database**:
```ini
db_host = odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
db_port = 25060
db_user = doadmin
db_password = ${POSTGRES_PASSWORD}
db_sslmode = require
db_maxconn = 64
```

### EE Parity Core Modules

**Installation Method**: Environment-driven via `.env` + scripts

**OCA Modules**: Defined in `ODOO_EE_PARITY_OCA_MODULES` (.env)
- Accounting: `account_usability`, `account_asset_management`, `mis_builder`, etc.
- Base/UX: `web_responsive`, `web_environment_ribbon`, `base_technical_features`, etc.
- Sales: `portal_sale_order_search`, `sale_delivery_state`, etc.

**IPAI Modules**: Defined in `ODOO_EE_PARITY_IPAI_MODULES` (.env)
- `ipai_mailgun_bridge` - Email observability integration
- (Extend with: `ipai_finance_ppm`, `ipai_bir_compliance`, etc.)

**Install/Upgrade Command**:
```bash
./scripts/dev/install-ee-parity-modules.sh
```

**Verify Installation Status**:
```bash
./scripts/dev/list-ee-parity-modules.sh
```

**Documentation**: `sandbox/dev/docs/EE_PARITY_INSTALL_PACK.md`

**Expected State**: All modules in ✅ `installed` state (verify before deploying to staging/production)

**Addons**:
```ini
addons_path = /mnt/extra-addons/ipai,/mnt/extra-addons/external/oca,/usr/lib/python3/dist-packages/odoo/addons
```

**Performance**:
```ini
workers = 12              # 2 × CPU cores
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
```

**HTTP**:
```ini
http_port = 8069
longpolling_port = 8072
proxy_mode = True
```

**Session**:
```ini
session_store = redis
session_redis_host = redis
session_redis_port = 6379
```

### Directory Structure

**Production** (`/opt/odoo-ce/`):
```
repo/                          # Git-tracked
├── addons/
│   ├── ipai/                  # 80+ custom modules
│   └── external/oca/          # OCA submodules
├── config/odoo.conf
├── deploy/docker-compose.yml
└── scripts/

data/                          # Runtime (not tracked)
├── filestore/                 # Odoo attachments
├── sessions/                  # Session storage
└── addons/                    # Symlinks

backups/                       # Database backups
├── daily/
├── weekly/
└── monthly/
```

---

## 4. Email Observability (Supabase Email Events Pack)

### Schema: email_parity

**Database**: Supabase PostgreSQL (project_ref: `spdtwktxdalcfigzeqrz`)

**Tables**:

**messages** (one row per logical outbound message):
```sql
id              bigserial primary key
message_id      text not null unique
odoo_mail_id    integer
from_address    text not null
to_addresses    text[] not null default '{}'
subject         text
template_key    text
meta            jsonb not null default '{}'::jsonb
created_at      timestamptz not null default now()
```

**events** (one row per email event):
```sql
id                  bigserial primary key
message_id          text not null references messages(message_id)
event_type          text not null
provider            text not null default 'mailgun'
provider_event_id   text
event_payload       jsonb not null default '{}'::jsonb
recipient           text
endpoint            text
ip                  inet
user_agent          text
occurred_at         timestamptz
```

**webhook_logs** (one row per webhook hit):
```sql
id              bigserial primary key
endpoint        text not null
status_code     integer not null
request_headers jsonb not null default '{}'::jsonb
request_body    jsonb not null default '{}'::jsonb
error_message   text
received_at     timestamptz not null default now()
```

**Views**:
- `v_message_summary`: Aggregated metrics (opens, clicks, open_rate_pct)
- `v_recipient_health`: Per-recipient health score (0-100)
- `v_template_performance`: Template-level analytics

### Edge Function

**Endpoint**: `https://{project_ref}.supabase.co/functions/v1/email-events`
**Runtime**: Deno TypeScript
**Purpose**: Mailgun webhook handler

**Workflow**:
1. Verify HMAC signature (MAILGUN_SIGNING_KEY)
2. Parse event payload
3. Upsert message to `email_parity.messages`
4. Insert event to `email_parity.events`
5. Log webhook to `email_parity.webhook_logs`
6. Return 200 OK

**Security**: HMAC signature verification (currently basic check, can be enhanced)

### Mailgun Webhook Configuration

**Webhook URL**: `https://{project_ref}.supabase.co/functions/v1/email-events`

**Events to Track**:
- delivered
- opened
- clicked
- bounced
- complained
- unsubscribed

---

## 5. Email Flow (End-to-End)

### Outbound Email Path

```
Odoo CE (ipai_mailgun_bridge)
    ↓ HTTP POST
Mailgun API (mg.insightpulseai.net)
    ↓ SMTP
Recipient MX
    ↓ Events (delivered, opened, clicked)
Mailgun Webhooks
    ↓ HTTPS POST
Supabase Edge Function (email-events)
    ↓ SQL INSERT
email_parity.messages + events
```

### Integration with Odoo

**Module**: `ipai_mailgun_bridge` (custom Odoo module)

**Metadata Passing**:
- Odoo mail_id → `email_parity.messages.odoo_mail_id`
- Template key → `email_parity.messages.template_key`
- Environment → `email_parity.messages.meta.environment`
- User → `email_parity.messages.meta.user_id`

### EE Parity Features

This setup replicates Odoo Enterprise Edition email tracking:
- ✅ Delivery tracking (delivered, bounced)
- ✅ Engagement analytics (opened, clicked)
- ✅ Per-recipient health scores
- ✅ Template performance metrics
- ✅ Compliance audit trail (webhook_logs)

---

## 6. Deployment Scripts

**Canonical Scripts** (in repo at `/opt/odoo-ce/repo/scripts/`):

### Deploy Odoo Modules
```bash
#!/bin/bash
# scripts/deploy/deploy_odoo_modules.sh

ssh root@178.128.112.214 << 'EOF'
cd /opt/odoo-ce/repo
git pull origin main
docker compose exec odoo-prod odoo -d odoo -u all --stop-after-init
docker compose restart odoo-prod
curl -f https://erp.insightpulseai.net/web/health || echo "Health check failed"
EOF
```

### Deploy Supabase Email Events Pack
```bash
#!/bin/bash
# scripts/supabase/apply-email-events-pack.sh

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

supabase db push --env-file .env.supabase
cd supabase/functions/email-events
supabase functions deploy email-events --project-ref "${SUPABASE_PROJECT_REF}" --env-file ../../.env.supabase
```

### Backup Database
```bash
#!/bin/bash
# scripts/deploy/backup_db.sh

ssh root@178.128.112.214 << 'EOF'
BACKUP_DIR="/opt/odoo-ce/backups/daily"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker compose exec postgres pg_dump -U odoo odoo > "$BACKUP_DIR/odoo_$TIMESTAMP.sql"
find "$BACKUP_DIR" -name "odoo_*.sql" -mtime +7 -delete
EOF
```

---

## 7. Monitoring & Health Checks

### Health Endpoints

| Service | Endpoint | Expected Response |
|---------|----------|-------------------|
| Odoo Production | `https://erp.insightpulseai.net/web/health` | HTTP 200 |
| Odoo Staging | `https://erp.staging.insightpulseai.net/web/health` | HTTP 200 |
| n8n | `https://n8n.insightpulseai.net/healthz` | HTTP 200 |
| Supabase | `https://{project_ref}.supabase.co/rest/v1/` | HTTP 200 (with auth) |

### Monitoring Checks (n8n workflows)

**Frequency**: Every 5 minutes

**Alerts**: Mattermost webhook on failure

**Metrics Collected**:
- HTTP status code
- Response time
- Error logs

### Log Locations

**Odoo**:
- Container logs: `docker logs odoo-prod`
- Application logs: `/var/log/odoo/odoo.log` (inside container)

**Nginx**:
- Access logs: `/var/log/nginx/erp.insightpulseai.net.access.log`
- Error logs: `/var/log/nginx/erp.insightpulseai.net.error.log`

**PostgreSQL** (Managed):
- DigitalOcean control panel metrics
- Slow query logs (if enabled)

---

## 8. Security

### Firewall (ufw)

```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (redirects to HTTPS)
ufw allow 443/tcp   # HTTPS
ufw enable
```

### Secrets Management

**Storage**:
- Database password: `.env` file (not tracked)
- Admin password: `.env` file (not tracked)
- API keys: Supabase Vault or environment variables

**Environment Variables** (required):
```bash
POSTGRES_PASSWORD=<database_password>
ADMIN_PASSWORD=<odoo_admin_password>
SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
MAILGUN_SIGNING_KEY=<mailgun_signing_key>
```

### SSL/TLS

**Certificate Authority**: Let's Encrypt
**Renewal**: Automated via certbot

**Verification Command**:
```bash
openssl s_client -connect erp.insightpulseai.net:443 -servername erp.insightpulseai.net < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

---

## 9. Verification Commands

**Run these commands to verify stack state** (copy-paste ready):

### DNS Verification
```bash
dig +short insightpulseai.net A
dig +short erp.insightpulseai.net A
dig +short mg.insightpulseai.net MX
dig +short mg.insightpulseai.net TXT
```

### Service Health
```bash
curl -f https://erp.insightpulseai.net/web/health
curl -f https://erp.staging.insightpulseai.net/web/health
```

### Docker Status (on 178.128.112.214)
```bash
ssh root@178.128.112.214 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

### Certificate Validity
```bash
echo | openssl s_client -servername erp.insightpulseai.net -connect erp.insightpulseai.net:443 2>/dev/null | openssl x509 -noout -dates
```

### Supabase Schema
```bash
psql "$POSTGRES_URL" -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'email_parity';"
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM email_parity.messages;"
```

---

## 10. Agent Consumption Guidelines

**For AI coding agents and automation scripts:**

1. **Read this file first** before generating any infrastructure commands
2. **Do not claim to have executed** commands; provide copy-paste scripts instead
3. **Treat this as source of truth** for topology, paths, and configurations
4. **Generate scripts** that operators can run, rather than narrating as if you ran them
5. **Reference canonical paths** from this document (e.g., `/etc/letsencrypt/live/`)

**Example Agent Response** (correct approach):
```
Based on CANONICAL_ODOO_STACK_SNAPSHOT.md, the nginx config is at:
/etc/nginx/conf.d/odoo.conf (inside nginx-prod-v2 container)

To view it, run:
docker exec nginx-prod-v2 cat /etc/nginx/conf.d/odoo.conf
```

**Anti-Pattern** (incorrect approach):
```
I checked the nginx config and I see it's configured for...
```

---

## 11. Update History

| Date | Author | Change |
|------|--------|--------|
| 2026-01-28 | Claude (via Jake) | Initial creation - consolidated from 4 canonical docs |

**Maintenance Rule**: Update this file when infrastructure changes. Do not let it drift from reality.

---

## 12. References

- **DNS Details**: `docs/infra/CANONICAL_DNS_INSIGHTPULSEAI.md`
- **Odoo Details**: `docs/infra/CANONICAL_ODOO_PACK.md`
- **Nginx Config**: `deploy/nginx/erp.insightpulseai.net.conf`
- **Email Events Runbook**: `docs/runbooks/SUPABASE_EMAIL_EVENTS_PACK.md`
- **Agent Skills**: `docs/agents/ODOO_CLOUD_DEVOPS_AGENT_SKILLS.md`
- **Odoo.sh Parity**: `docs/parity/odoo_sh/ODOO_SH_FEATURES_MAP.md`
