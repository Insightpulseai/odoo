# Canonical Odoo Pack - Architecture & Layout

**Status**: REFERENCE
**Target**: Odoo 18 CE + OCA + ipai_* (InsightPulse AI)
**Last Updated**: 2026-01-28

---

## 1. Directory Layout (Logical)

```
/opt/odoo-ce/
├── repo/                          # Git-tracked repository
│   ├── addons/
│   │   ├── ipai/                  # Custom modules (80+ modules)
│   │   └── external/oca/          # OCA modules (git submodules)
│   ├── config/
│   │   └── odoo.conf              # Base configuration
│   ├── deploy/
│   │   ├── docker-compose.yml     # Production stack
│   │   └── nginx/
│   │       └── erp.insightpulseai.net.conf
│   └── scripts/
│       └── deploy/
├── data/                          # Runtime data (not tracked)
│   ├── filestore/                 # Odoo attachments
│   ├── sessions/                  # Session storage
│   └── addons/                    # Symlinks to repo/addons
└── backups/                       # Database backups
    ├── daily/
    ├── weekly/
    └── monthly/
```

---

## 2. Docker Compose Stack

**Production**: `deploy/docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    restart: always

  odoo:
    image: odoo:18.0
    depends_on:
      - postgres
    volumes:
      - ./repo/addons:/mnt/extra-addons
      - ./data/filestore:/var/lib/odoo
      - ./config/odoo.conf:/etc/odoo/odoo.conf
    environment:
      - HOST=postgres
      - USER=odoo
      - PASSWORD=${POSTGRES_PASSWORD}
    restart: always
    command: odoo -c /etc/odoo/odoo.conf

  nginx:
    image: nginx:alpine
    depends_on:
      - odoo
    volumes:
      - ./deploy/nginx/erp.insightpulseai.net.conf:/etc/nginx/conf.d/default.conf
      - /etc/letsencrypt:/etc/letsencrypt:ro
    ports:
      - "80:80"
      - "443:443"
    restart: always

volumes:
  pgdata:
```

---

## 3. Nginx Virtual Host

**File**: `deploy/nginx/erp.insightpulseai.net.conf`

```nginx
upstream odoo {
    server odoo:8069;
}

upstream odoo_im {
    server odoo:8072;
}

server {
    listen 80;
    server_name erp.insightpulseai.net;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name erp.insightpulseai.net;

    ssl_certificate /etc/letsencrypt/live/erp.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.net/privkey.pem;

    client_max_body_size 100M;
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    location / {
        proxy_pass http://odoo;
        proxy_redirect off;
    }

    location /longpolling {
        proxy_pass http://odoo_im;
    }

    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }
}
```

---

## 4. Odoo Configuration

**File**: `config/odoo.conf`

```ini
[options]
# Database
db_host = postgres
db_port = 5432
db_user = odoo
db_password = ${POSTGRES_PASSWORD}
db_maxconn = 64
db_template = template0

# Addons
addons_path = /mnt/extra-addons/ipai,/mnt/extra-addons/external/oca,/usr/lib/python3/dist-packages/odoo/addons

# Performance
workers = 12              # 2 × CPU cores
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 60
limit_time_real = 120

# HTTP
http_port = 8069
longpolling_port = 8072
proxy_mode = True

# Session
session_store = redis
session_redis_host = redis
session_redis_port = 6379

# Logging
log_level = info
log_handler = :INFO
logfile = /var/log/odoo/odoo.log

# Security
admin_passwd = ${ADMIN_PASSWORD}
list_db = False
```

---

## 5. Environment Topologies

### 5.1. Development (sandbox/dev)

**Host**: localhost (Docker Desktop)
**Ports**: 8069 (HTTP), 5432 (PostgreSQL direct)
**Hot-reload**: Yes (watchdog on addons/)
**Data**: Seeded with demo data

### 5.2. Staging (erp.staging.insightpulseai.net)

**Host**: 178.128.112.214
**Stack**: Same as production (separate containers)
**Data**: Sanitized copy from production (weekly refresh)
**Purpose**: Pre-production validation, BIR testing

### 5.3. Production (erp.insightpulseai.net)

**Host**: 178.128.112.214
**Stack**: docker-compose with nginx reverse proxy
**Data**: Live data (daily backups to DigitalOcean Spaces)
**Uptime**: 99.9% target

---

## 6. Deployment Workflow

```bash
# 1. SSH to production droplet
ssh root@178.128.112.214

# 2. Navigate to repo
cd /opt/odoo-ce/repo

# 3. Pull latest changes
git pull origin main

# 4. Backup database
./scripts/deploy/backup_db.sh

# 5. Update modules
docker compose exec odoo odoo -d odoo -u all --stop-after-init

# 6. Restart services
docker compose restart odoo

# 7. Verify
curl -f https://erp.insightpulseai.net/web/health || echo "Health check failed"
```

---

## 7. Backup Strategy

**Database**:
- **Daily**: Full pg_dump to `/opt/odoo-ce/backups/daily/` (7-day retention)
- **Weekly**: Full pg_dump to DigitalOcean Spaces (30-day retention)
- **Monthly**: Full pg_dump to DigitalOcean Spaces (12-month retention)

**Filestore**:
- **Daily**: rsync to `/opt/odoo-ce/backups/daily/filestore/` (7-day retention)
- **Weekly**: tar.gz to DigitalOcean Spaces (30-day retention)

**Configuration**:
- Git-tracked in repo (no separate backup needed)

---

## 8. Monitoring

**Health Checks**:
- **Endpoint**: `https://erp.insightpulseai.net/web/health`
- **Frequency**: Every 5 minutes (n8n workflow)
- **Alert**: Mattermost webhook on failure

**Metrics**:
- **PostgreSQL**: Connection count, query time, table sizes
- **Odoo**: Request latency, error rate, active sessions
- **System**: CPU, memory, disk usage (DigitalOcean metrics)

**Logs**:
- **Odoo**: `/var/log/odoo/odoo.log` (rotated daily)
- **Nginx**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **PostgreSQL**: Docker logs (`docker compose logs postgres`)

---

## 9. Security

**Firewall** (ufw):
```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (redirect to HTTPS)
ufw allow 443/tcp   # HTTPS
ufw enable
```

**TLS Certificates** (Let's Encrypt):
```bash
certbot certonly --nginx -d erp.insightpulseai.net
```

**Secrets Management**:
- **Database password**: `.env` file (not tracked)
- **Admin password**: `.env` file (not tracked)
- **API keys**: Supabase Vault or environment variables

---

## 10. OCA Module Management

**Strategy**: Git submodules for OCA repositories

```bash
# Add OCA repo as submodule
git submodule add https://github.com/OCA/project.git addons/external/oca/project
git submodule add https://github.com/OCA/helpdesk.git addons/external/oca/helpdesk

# Update all submodules
git submodule update --init --recursive

# Pull latest OCA changes
git submodule foreach git pull origin 18.0
```

**Lock File**: `oca.lock.json` tracks exact commit SHAs for reproducibility

---

## 11. Multi-Edition Support

**Experimental**: Support for multiple Odoo editions on same host

| Edition | Port | Database | Module Focus |
|---------|------|----------|--------------|
| Core | 8069 | odoo_core | Base CE + IPAI workspace |
| Marketing | 8070 | odoo_marketing | Marketing agency extensions |
| Accounting | 8071 | odoo_accounting | Accounting firm extensions |

**Status**: Conceptual (not yet implemented in production)

---

## 12. References

- **DNS**: `docs/infra/CANONICAL_DNS_INSIGHTPULSEAI.md`
- **Parity**: `docs/parity/odoo_sh/ODOO_SH_FEATURES_MAP.md`
- **Docker SSOT**: `infra/docker/DOCKER_DESKTOP_SSOT.yaml`
- **Odoo 18 Docs**: https://www.odoo.com/documentation/18.0/
- **OCA Guidelines**: https://github.com/OCA/odoo-community.org
