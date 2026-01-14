# Production Droplet Setup - Complete Runbook

**Canonical production deployment** to DigitalOcean droplet `178.128.112.214` with DO Managed PostgreSQL, Caddy reverse proxy, and automatic SSL.

**Target:** `erp.insightpulseai.net` → Odoo 18 CE

---

## Prerequisites

- [x] DigitalOcean droplet `178.128.112.214` (Ubuntu/Debian)
- [x] DO Managed PostgreSQL `odoo-db-sgp1` (SGP1)
- [x] DNS: `erp.insightpulseai.net` → `178.128.112.214`
- [x] Network Access: `178.128.112.214` allowlisted in DO database firewall
- [x] Database user `odoo_app` with permissions on database `odoo`

---

## Step 0: System Updates (Recommended)

```bash
# Apply updates and reboot
apt-get update -y
apt-get upgrade -y
reboot
```

**Wait for droplet to restart**, then reconnect via SSH.

---

## Step 1: Install Docker + Dependencies

```bash
# Install baseline tooling
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release ufw

# Add Docker GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" \
> /etc/apt/sources.list.d/docker.list

# Install Docker + Compose plugin
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Enable and start Docker
systemctl enable --now docker

# Verify installation
docker version
docker compose version
```

**Expected output:**
```
Docker version 25.x.x
Docker Compose version v2.x.x
```

---

## Step 2: Configure Firewall

```bash
# Allow SSH (CRITICAL: do this first)
ufw allow OpenSSH

# Allow HTTP and HTTPS (for Caddy)
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw --force enable

# Verify rules
ufw status
```

**Expected output:**
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

**Note:** Port 8069 is NOT exposed externally. Caddy handles all external traffic.

---

## Step 3: Create Directory Structure

```bash
# Create canonical directories
mkdir -p /opt/odoo-ce/{deploy,data,logs}

# Secure deploy directory (secrets live here)
chmod 700 /opt/odoo-ce/deploy

# Create environment file
touch /opt/odoo-ce/deploy/.env
chmod 600 /opt/odoo-ce/deploy/.env
```

---

## Step 4: Configure Environment Variables

```bash
cat >/opt/odoo-ce/deploy/.env <<'ENV'
# --- DigitalOcean Managed Postgres (canonical) ---
DB_HOST=odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
DB_PORT=25060
DB_NAME=odoo
DB_USER=odoo_app
DB_PASSWORD=REPLACE_WITH_PASSWORD

# --- Odoo runtime ---
ODOO_ADMIN_PASSWORD=REPLACE_WITH_MASTER_PASSWORD

# --- public hostnames ---
ODOO_DOMAIN=erp.insightpulseai.net
ENV

# Edit with real credentials
nano /opt/odoo-ce/deploy/.env
```

**Required replacements:**
- `DB_PASSWORD` → Actual password for `odoo_app` user
- `ODOO_ADMIN_PASSWORD` → Secure master password for Odoo database manager

---

## Step 5: Create Docker Compose Configuration

```bash
cat >/opt/odoo-ce/deploy/docker-compose.yml <<'YAML'
services:
  dbssl:
    image: alpine:3.20
    env_file: .env
    command: >
      sh -lc "
      apk add --no-cache stunnel &&
      cat >/etc/stunnel/stunnel.conf <<'CONF'
      client = yes
      foreground = yes
      [postgres]
      accept = 0.0.0.0:5432
      connect = ${DB_HOST}:${DB_PORT}
      CONF
      stunnel /etc/stunnel/stunnel.conf
      "
    restart: unless-stopped
    ports:
      - "127.0.0.1:5432:5432"

  odoo:
    image: odoo:18
    env_file: .env
    depends_on:
      - dbssl
    restart: unless-stopped
    ports:
      - "127.0.0.1:8069:8069"
    volumes:
      - /opt/odoo-ce/data/odoo-web-data:/var/lib/odoo
      - /opt/odoo-ce/deploy/odoo.conf:/etc/odoo/odoo.conf:ro
      - /opt/odoo-ce/logs:/var/log/odoo
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:8069/web/login >/dev/null 2>&1 || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 10

  caddy:
    image: caddy:2
    restart: unless-stopped
    env_file: .env
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /opt/odoo-ce/deploy/Caddyfile:/etc/caddy/Caddyfile:ro
      - /opt/odoo-ce/data/caddy:/data
      - /opt/odoo-ce/data/caddy_config:/config
YAML
```

**Architecture:**
```
Internet → Caddy (80/443) → Odoo (127.0.0.1:8069) → stunnel (127.0.0.1:5432) → DO Managed DB (25060)
```

---

## Step 6: Create Odoo Configuration

```bash
cat >/opt/odoo-ce/deploy/odoo.conf <<'CONF'
[options]
; master password for db manager:
admin_passwd = ${ODOO_ADMIN_PASSWORD}

; DO managed Postgres via local stunnel:
db_host = 127.0.0.1
db_port = 5432
db_user = ${DB_USER}
db_password = ${DB_PASSWORD}

; keep canonical db naming (you can remove dbfilter if you want multiple DBs):
; dbfilter = ^odoo$

proxy_mode = True
logfile = /var/log/odoo/odoo.log
log_level = info
workers = 2
max_cron_threads = 1
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560
limit_time_cpu = 120
limit_time_real = 240
CONF
```

**Key settings:**
- `db_host = 127.0.0.1` → Connects via stunnel (not directly to DO)
- `db_name` → Not specified, allows multiple databases (or uncomment `dbfilter`)
- `proxy_mode = True` → Required for Caddy reverse proxy
- `workers = 2` → Multi-threaded for production

---

## Step 7: Create Caddy Reverse Proxy Configuration

```bash
cat >/opt/odoo-ce/deploy/Caddyfile <<'CADDY'
{$ODOO_DOMAIN} {
  encode zstd gzip
  reverse_proxy 127.0.0.1:8069
}
CADDY
```

**Caddy features:**
- Automatic HTTPS via Let's Encrypt
- Automatic certificate renewal
- HTTP/2 and HTTP/3 support
- Compression (zstd, gzip)

---

## Step 8: Start Services

```bash
cd /opt/odoo-ce/deploy

# Pull images
docker compose pull

# Start services
docker compose up -d

# Check status
docker compose ps
```

**Expected output:**
```
NAME                 IMAGE        STATUS         PORTS
deploy-caddy-1       caddy:2      Up             0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
deploy-odoo-1        odoo:18      Up (healthy)   127.0.0.1:8069->8069/tcp
deploy-dbssl-1       alpine:3.20  Up             127.0.0.1:5432->5432/tcp
```

### View logs

```bash
# All services
docker compose logs -f

# Odoo only
docker compose logs -n 200 --no-log-prefix odoo

# Caddy only
docker compose logs -f caddy

# Database tunnel
docker compose logs -f dbssl
```

---

## Step 9: Verify Local Connection

```bash
# Test Odoo HTTP endpoint
curl -I http://127.0.0.1:8069/web/login
```

**Expected output:**
```
HTTP/1.0 200 OK
Server: Werkzeug/x.x
```

---

## Step 10: Verify Public HTTPS Connection

```bash
# Test public domain
curl -I https://erp.insightpulseai.net/web/login
```

**Expected output:**
```
HTTP/2 200
server: Caddy
```

**Browser test:**
```
https://erp.insightpulseai.net
```

Should show Odoo login page with valid SSL certificate.

---

## Step 11 (Optional): Enforce Single Database

To restrict Odoo to only use database `odoo`:

```bash
# Uncomment dbfilter line
sed -i 's/^; dbfilter/dbfilter/' /opt/odoo-ce/deploy/odoo.conf

# Restart Odoo
docker compose restart odoo

# Verify logs
docker compose logs -n 200 --no-log-prefix odoo
```

**Effect:** Only database named `odoo` will be accessible/creatable.

---

## Step 12: Initialize Odoo Database

Access `https://erp.insightpulseai.net` in browser.

**First-time setup:**
1. Click "Create Database"
2. Master Password: (from `.env` → `ODOO_ADMIN_PASSWORD`)
3. Database Name: `odoo`
4. Email: admin email
5. Password: admin user password
6. Language: English
7. Country: Philippines
8. Demo data: No

**Note:** If database `odoo` already exists in DO Managed DB, Odoo will connect to it automatically.

---

## Step 13 (Optional): Auto-Start on Boot

Create systemd service for automatic startup:

```bash
cat >/etc/systemd/system/odoo-stack.service <<'UNIT'
[Unit]
Description=Odoo 18 CE Stack (Caddy + Odoo + dbssl)
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/odoo-ce/deploy
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
UNIT

# Reload systemd
systemctl daemon-reload

# Enable and start service
systemctl enable --now odoo-stack.service

# Check status
systemctl status odoo-stack.service --no-pager
```

**Verification:**
```bash
# Reboot droplet
reboot

# After reboot, check services
docker compose -f /opt/odoo-ce/deploy/docker-compose.yml ps
curl -I https://erp.insightpulseai.net/web/login
```

---

## Quick Operations Reference

### Service Management

```bash
cd /opt/odoo-ce/deploy

# View logs (follow mode)
docker compose logs -f odoo

# Restart Odoo only
docker compose restart odoo

# Restart all services
docker compose restart

# Stop all services
docker compose down

# Start all services
docker compose up -d

# View service status
docker compose ps
```

---

### Database Operations

```bash
# Connect to DO Managed Database via stunnel
docker compose exec odoo bash -c '
  PGPASSWORD="$DB_PASSWORD" psql \
    -h 127.0.0.1 \
    -p 5432 \
    -U "$DB_USER" \
    -d "$DB_NAME"
'

# Backup database
PGPASSWORD="$DB_PASSWORD" pg_dump \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo \
  --no-owner --no-acl \
  | gzip > /opt/backups/odoo_$(date +%Y%m%d).sql.gz
```

---

### Module Operations

```bash
# Update apps list
docker compose exec odoo odoo -d odoo -u base --stop-after-init

# Install module
docker compose exec odoo odoo -d odoo -i ipai_finance_ppm --stop-after-init

# Upgrade module
docker compose exec odoo odoo -d odoo -u ipai_finance_ppm --stop-after-init

# Restart after module changes
docker compose restart odoo
```

---

## Troubleshooting

### Caddy SSL Certificate Issues

**Symptom:** "acme: error presenting token"

**Check:**
```bash
# Verify DNS resolves to droplet
dig +short erp.insightpulseai.net

# Should return: 178.128.112.214
```

**Fix:**
```bash
# Check Caddy logs
docker compose logs caddy

# Restart Caddy
docker compose restart caddy
```

---

### Odoo Not Accessible

**Symptom:** 502 Bad Gateway or connection timeout

**Check:**
```bash
# Verify Odoo is running
docker compose ps odoo

# Check Odoo logs
docker compose logs odoo

# Test local connection
curl -I http://127.0.0.1:8069/web/login
```

**Fix:**
```bash
# Restart Odoo
docker compose restart odoo

# If still failing, check database connection
docker compose exec odoo bash -c '
  python3 -c "
import psycopg2, os
conn = psycopg2.connect(
    host=\"127.0.0.1\",
    port=5432,
    dbname=os.environ[\"DB_NAME\"],
    user=os.environ[\"DB_USER\"],
    password=os.environ[\"DB_PASSWORD\"]
)
print(\"✓ Database connection successful\")
conn.close()
  "
'
```

---

### Database Connection Failed

**Symptom:** `FATAL: connection to server failed`

**Check:**
1. Network Access allowlist in DO dashboard
2. stunnel is running: `docker compose ps dbssl`
3. stunnel logs: `docker compose logs dbssl`

**Fix:**
```bash
# Verify DO database allowlist
# DigitalOcean Dashboard → Databases → odoo-db-sgp1 → Network Access
# Ensure 178.128.112.214 is listed

# Test direct connection (bypass stunnel)
PGPASSWORD="$DB_PASSWORD" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo \
  --set=sslmode=require

# Restart stunnel
docker compose restart dbssl
```

---

## Security Checklist

- [x] `.env` file permissions: `chmod 600`
- [x] Deploy directory permissions: `chmod 700`
- [x] Firewall allows only SSH, HTTP, HTTPS
- [x] Port 8069 NOT exposed externally (only 127.0.0.1)
- [x] Database port 5432 NOT exposed externally (only 127.0.0.1)
- [x] DO database allowlist includes only `178.128.112.214`
- [x] SSL/TLS enforced via Caddy (automatic HTTPS)
- [x] SSL/TLS enforced to database via stunnel
- [x] Strong admin password set
- [x] Separate database user `odoo_app` (not `doadmin`)
- [x] Regular backups scheduled

---

## Monitoring

### Health Checks

```bash
# Service health
docker compose ps

# Odoo health endpoint
curl -sf https://erp.insightpulseai.net/web/health

# Database connection
docker compose exec odoo bash -c '
  PGPASSWORD="$DB_PASSWORD" psql \
    -h 127.0.0.1 \
    -p 5432 \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -c "SELECT version();"
'

# Disk usage
df -h /opt/odoo-ce

# Memory usage
docker stats --no-stream
```

---

### Log Management

```bash
# Odoo logs
tail -f /opt/odoo-ce/logs/odoo.log

# Docker logs
docker compose logs --tail 100

# Clear old logs (keep last 7 days)
find /opt/odoo-ce/logs -name "*.log" -mtime +7 -delete
```

---

## Backup Strategy

### Database Backup (Daily)

```bash
#!/bin/bash
# /opt/odoo-ce/scripts/backup-db.sh

source /opt/odoo-ce/deploy/.env
BACKUP_DIR="/opt/backups/odoo"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

PGPASSWORD="$DB_PASSWORD" pg_dump \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --no-owner --no-acl \
  | gzip > "$BACKUP_DIR/odoo_${DATE}.sql.gz"

# Keep last 7 days
find "$BACKUP_DIR" -name "odoo_*.sql.gz" -mtime +7 -delete
```

**Cron job:**
```bash
# Daily at 2 AM
0 2 * * * /opt/odoo-ce/scripts/backup-db.sh >> /opt/odoo-ce/logs/backup.log 2>&1
```

---

### Filestore Backup

```bash
#!/bin/bash
# /opt/odoo-ce/scripts/backup-filestore.sh

BACKUP_DIR="/opt/backups/odoo"
DATE=$(date +%Y%m%d)

tar czf "$BACKUP_DIR/filestore_${DATE}.tar.gz" \
  /opt/odoo-ce/data/odoo-web-data

# Keep last 7 days
find "$BACKUP_DIR" -name "filestore_*.tar.gz" -mtime +7 -delete
```

---

## Deployment Summary

| Component | Value |
|-----------|-------|
| **Droplet IP** | 178.128.112.214 |
| **Public URL** | https://erp.insightpulseai.net |
| **Odoo Version** | 18 (official image) |
| **Database** | odoo-db-sgp1 (DO Managed PostgreSQL 16) |
| **Database Name** | `odoo` (canonical) |
| **Database User** | `odoo_app` |
| **SSL/TLS** | Automatic (Caddy + Let's Encrypt) |
| **Reverse Proxy** | Caddy 2 |
| **Database Tunnel** | stunnel (SSL to DO Managed DB) |
| **Firewall** | UFW (SSH, HTTP, HTTPS only) |
| **Auto-Start** | systemd (`odoo-stack.service`) |

---

**Deployment Date:** 2026-01-14
**Last Updated:** 2026-01-14
