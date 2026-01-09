# Odoo 18 CE Production Defaults - Canonical Configuration

**Last Updated**: 2026-01-08
**Status**: ✅ Working
**Instance**: https://erp.insightpulseai.net/

---

## Canonical Naming Standards

### Containers
- **Odoo**: `odoo-erp-prod` (currently: `odoo-ce`)
- **Postgres**: `db` (currently: `odoo-postgres`)
- **Reverse Proxy**: Host nginx (port 80/443)

### Database
- **DB Name**: `odoo` (currently: `odoo_core`)
- **DB User**: `odoo`
- **DB Host**: `db` (currently: `postgres`)
- **DB Port**: `5432`

### Volumes
- **Filestore**: `odoo-web-data` → `/var/lib/odoo` (currently: `odoo-filestore`)
- **Postgres Data**: `odoo-db-data` → `/var/lib/postgresql/data`
- **IPAI Addons**: `./addons/ipai` → `/mnt/addons/ipai`
- **OCA Addons**: `./oca` → `/mnt/addons/oca`

### Ports
- **Odoo Web**: `8069` (bind: `127.0.0.1:8069`)
- **Longpolling**: `8072` (optional, currently not exposed)

---

## Current Working Configuration

### DNS
```
erp.insightpulseai.net → 159.223.75.148 (TTL: 60)
```

### Container Stack
```
nginx (host) :443 → odoo-ce :8069 → odoo-postgres :5432
```

### Key Files
- **Config**: `/root/odoo-ce/deploy/odoo.conf`
- **Compose**: `/root/odoo-ce/deploy/docker-compose.prod.v0.10.0.yml`
- **Nginx**: `/etc/nginx/sites-available/erp.insightpulseai.net.conf`

### Working odoo.conf
```ini
[options]
; ----- Database -----
db_host = postgres
db_port = 5432
db_user = odoo
db_password = odoo
db_name = odoo_core
; dbfilter and list_db commented out to avoid selector conflicts
db_sslmode = disable

; ----- Addons -----
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/addons/ipai,/mnt/addons/oca

; ----- HTTP -----
http_port = 8069
proxy_mode = True
limit_time_cpu = 600
limit_time_real = 1200

; ----- Logging -----
logfile = /var/log/odoo/odoo.log
log_level = debug

; ----- Security -----
admin_passwd = CHANGE_ME_SUPERMASTER_PASSWORD

; ----- Resource Limits -----
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192

; ----- Worker Configuration -----
workers = 4
max_cron_threads = 2
db_maxconn = 64
```

### Working Nginx Config
```nginx
server {
    listen 80;
    server_name erp.insightpulseai.net;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name erp.insightpulseai.net;

    ssl_certificate /etc/letsencrypt/live/erp.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.insightpulseai.net/privkey.pem;

    # Odoo proxy
    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port 443;
        proxy_redirect off;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Buffers
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        proxy_read_timeout 600s;
    }

    # Longpolling
    location /longpolling {
        proxy_pass http://127.0.0.1:8072;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port 443;
        proxy_redirect off;
    }

    client_max_body_size 64m;
}
```

---

## Migration Path to Canonical Names

### Phase 1: Rename Resources (Non-Breaking)
```bash
# 1. Stop containers
cd /root/odoo-ce/deploy
docker compose -f docker-compose.prod.v0.10.0.yml stop odoo

# 2. Create new database (copy from odoo_core)
docker exec odoo-postgres pg_dump -U odoo odoo_core | \
  docker exec -i odoo-postgres psql -U odoo -c "CREATE DATABASE odoo;"

# 3. Rename volume
docker volume create odoo-web-data
docker run --rm -v odoo-filestore:/source -v odoo-web-data:/target alpine \
  sh -c "cp -a /source/. /target/"

# 4. Update docker-compose.yml with canonical names

# 5. Update odoo.conf with canonical settings

# 6. Restart with new configuration
```

### Phase 2: Update odoo.conf
```ini
[options]
proxy_mode = True
data_dir = /var/lib/odoo

db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
db_name = odoo

addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/addons/oca,/mnt/addons/ipai

workers = 4
max_cron_threads = 2
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560
limit_time_cpu = 600
limit_time_real = 1200

log_level = info
```

### Phase 3: Update docker-compose.yml
```yaml
version: "3.9"

services:
  db:
    image: postgres:16
    container_name: db
    restart: unless-stopped
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_MAX_CONNECTIONS: 100
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    networks:
      - odoo_backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  odoo:
    image: ghcr.io/jgtolentino/odoo-ce:v0.10.0
    container_name: odoo-erp-prod
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    command: -- --config /etc/odoo/odoo.conf
    volumes:
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
      - odoo-web-data:/var/lib/odoo
      - ../addons/ipai:/mnt/addons/ipai:ro
      - ./oca:/mnt/addons/oca:ro
    ports:
      - "127.0.0.1:8069:8069"
    networks:
      - odoo_backend
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8069/web/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  odoo-web-data:
    name: odoo-web-data
  odoo-db-data:
    name: odoo-db-data

networks:
  odoo_backend:
    driver: bridge
```

---

## Health Check Commands

### Container Status
```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E "(odoo-erp-prod|db)"
```

### Odoo Responding
```bash
curl -sS -I http://127.0.0.1:8069/web | head -5
```

### Database Connection
```bash
docker exec -it odoo-erp-prod python3 -c "
import psycopg2
conn = psycopg2.connect(host='db', port=5432, user='odoo', password='odoo', dbname='odoo')
print('✅ Database connection successful')
conn.close()
"
```

### Public Endpoint
```bash
curl -sS -I https://erp.insightpulseai.net/ | head -5
```

---

## Known Issues Fixed (2026-01-08)

### Issue 1: 502 Bad Gateway
**Root Cause**: DNS A record pointed to wrong IP (165.227.10.178 instead of 159.223.75.148)
**Fix**: Updated DigitalOcean DNS record to correct IP

### Issue 2: Database Authentication Failed
**Root Cause**: Environment variables in docker-compose overriding odoo.conf password
**Fix**: Removed environment variables from docker-compose, rely on odoo.conf only

### Issue 3: Database Selector 500 Error
**Root Cause**: Conflict between `db_name`, `dbfilter`, and `list_db` settings
**Fix**: Commented out `dbfilter` and `list_db` to allow database selection

### Issue 4: Password Authentication Loop
**Root Cause**: `PASSWORD` environment variable in container had old value
**Fix**: Removed all database-related environment variables from docker-compose

---

## Acceptance Gates

Before considering deployment complete, verify:

1. ✅ DNS resolves to correct IP: `dig +short erp.insightpulseai.net` returns `159.223.75.148`
2. ✅ Container healthy: `docker ps --filter name=odoo-erp-prod` shows `(healthy)`
3. ✅ Database connected: Python connection test succeeds
4. ✅ Nginx proxying: `curl -I https://erp.insightpulseai.net/` returns 200-series status
5. ✅ Odoo UI loads: Browser shows Odoo login or database selector
6. ✅ No authentication errors in logs: `docker logs odoo-erp-prod | grep -i "authentication failed"` returns empty

---

## Rollback Procedure

If issues occur after migration:

```bash
# 1. Stop new containers
docker compose -f docker-compose.prod.v0.10.0.yml down

# 2. Restore old configuration
git checkout HEAD~1 -- deploy/odoo.conf deploy/docker-compose.prod.v0.10.0.yml

# 3. Restart with old config
docker compose -f docker-compose.prod.v0.10.0.yml up -d

# 4. Verify health
curl -I https://erp.insightpulseai.net/
```

---

## Next Steps

1. **Standardize Naming** - Migrate to canonical container/volume names
2. **Simplify Configuration** - Remove deprecated settings, use minimal config
3. **Document Runtime** - Update `docs/architecture/runtime_identifiers.json`
4. **Automate Health Checks** - Add monitoring for DNS/containers/nginx/odoo
5. **SMTP Configuration** - Set up Mailgun SMTP (see `docs/SMTP_FIX_SUMMARY.md`)
