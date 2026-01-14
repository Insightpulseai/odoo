# Droplet Deployment Guide

Production deployment to DigitalOcean Droplet `178.128.112.214` with DO Managed PostgreSQL.

## Prerequisites

- [x] Droplet `178.128.112.214` running Ubuntu/Debian
- [x] Docker + Docker Compose installed on droplet
- [x] DO Managed PostgreSQL cluster `odoo-db-sgp1` accessible
- [x] Network Access: `178.128.112.214` allowlisted in DO database firewall
- [x] User `odoo_app` created in DO database (see CANONICAL_NAMING.md)

---

## Deployment Steps

### 1. Prepare Droplet

```bash
# SSH into droplet
ssh root@178.128.112.214

# Create deployment directory
sudo mkdir -p /opt/odoo-ce
cd /opt/odoo-ce

# Clone repository (or rsync from local)
git clone https://github.com/jgtolentino/odoo-ce.git .
# OR
# rsync -avz --exclude='.git' ./ root@178.128.112.214:/opt/odoo-ce/
```

---

### 2. Configure Environment

```bash
cd /opt/odoo-ce/deploy

# Copy environment template
cp .env.droplet.example .env

# Edit with real credentials
nano .env
```

**Required variables in `.env`:**
```bash
DB_HOST=odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
DB_PORT=25060
DB_USER=odoo_app
DB_PASSWORD=<actual_password>
DB_NAME=odoo
ADMIN_PASSWD=<secure_admin_password>
```

---

### 3. Verify Database User

Before starting Odoo, create the `odoo_app` user in DO Managed Database:

```bash
# Connect to DO database as doadmin
PGPASSWORD='<doadmin_password>' psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d defaultdb \
  --set=sslmode=require

# Create odoo_app user
CREATE USER odoo_app WITH PASSWORD '<secure_password>';

# Create odoo database
CREATE DATABASE odoo WITH OWNER odoo_app;

# Grant permissions
GRANT ALL PRIVILEGES ON DATABASE odoo TO odoo_app;

# Exit
\q
```

---

### 4. Test Database Connection

```bash
# Source environment
source /opt/odoo-ce/deploy/.env

# Test connection (before starting containers)
PGPASSWORD="$DB_PASSWORD" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --set=sslmode=require \
  -c "SELECT version();"
```

Expected output:
```
                                                 version
---------------------------------------------------------------------------------------------------------
 PostgreSQL 16.x on x86_64-pc-linux-gnu, compiled by gcc (GCC) 11.x, 64-bit
(1 row)
```

---

### 5. Start Services

```bash
cd /opt/odoo-ce/deploy

# Pull latest images
docker compose -f docker-compose.droplet.yml pull

# Start services
docker compose -f docker-compose.droplet.yml up -d

# Check status
docker compose -f docker-compose.droplet.yml ps
```

Expected output:
```
NAME                 IMAGE        STATUS         PORTS
odoo-dbssl           alpine:3.20  Up (healthy)
odoo-prod            odoo:18.0    Up (healthy)   0.0.0.0:8069->8069/tcp
```

---

### 6. Verify Deployment

#### Check logs

```bash
# All logs
docker compose -f docker-compose.droplet.yml logs -f

# Odoo only
docker compose -f docker-compose.droplet.yml logs -f odoo

# Database tunnel
docker compose -f docker-compose.droplet.yml logs -f dbssl
```

#### Test database connection from container

```bash
docker compose -f docker-compose.droplet.yml exec odoo bash -c '
  python3 -c "
import psycopg2, os
conn = psycopg2.connect(
    host=os.environ[\"DB_HOST\"],
    port=os.environ[\"DB_PORT\"],
    dbname=os.environ[\"DB_NAME\"],
    user=os.environ[\"DB_USER\"],
    password=os.environ[\"DB_PASSWORD\"]
)
print(\"✓ Database connection successful\")
conn.close()
  "
'
```

#### Test HTTP endpoint

```bash
# From droplet
curl -sf http://localhost:8069/web/health

# From external
curl -sf http://178.128.112.214:8069/web/health
```

---

### 7. Initialize Odoo Database

Access Odoo at `http://178.128.112.214:8069`

**First-time setup:**
1. Database Manager → Create Database
2. Master Password: (from `.env` → `ADMIN_PASSWD`)
3. Database Name: `odoo` (should match `DB_NAME`)
4. Email: admin email
5. Password: admin password
6. Language: English
7. Country: Philippines (or appropriate)

**Note:** Database should already exist if you created it via psql in step 3. If not, Odoo will create it automatically.

---

### 8. Install Modules

```bash
# Update apps list
docker compose -f docker-compose.droplet.yml exec odoo \
  odoo -d odoo -u base --stop-after-init

# Install custom module
docker compose -f docker-compose.droplet.yml exec odoo \
  odoo -d odoo -i ipai_finance_ppm --stop-after-init

# Restart to apply changes
docker compose -f docker-compose.droplet.yml restart odoo
```

---

## Configuration Files

### `/opt/odoo-ce/deploy/`

```
deploy/
├── docker-compose.droplet.yml    # Droplet-specific compose
├── odoo.conf.droplet             # Production Odoo config
├── .env                          # Environment variables (NEVER commit)
└── .env.droplet.example          # Template
```

---

## Service Management

### Start/Stop/Restart

```bash
cd /opt/odoo-ce/deploy

# Start
docker compose -f docker-compose.droplet.yml up -d

# Stop
docker compose -f docker-compose.droplet.yml stop

# Restart Odoo only
docker compose -f docker-compose.droplet.yml restart odoo

# Full restart
docker compose -f docker-compose.droplet.yml restart
```

### View Logs

```bash
# Follow logs
docker compose -f docker-compose.droplet.yml logs -f

# Last 100 lines
docker compose -f docker-compose.droplet.yml logs --tail 100

# Odoo only
docker compose -f docker-compose.droplet.yml logs -f odoo
```

### Access Container

```bash
# Bash shell in Odoo container
docker compose -f docker-compose.droplet.yml exec odoo bash

# Python shell (Odoo shell)
docker compose -f docker-compose.droplet.yml exec odoo \
  odoo shell -d odoo
```

---

## Troubleshooting

### Database Connection Errors

**Symptom:** `FATAL: connection to server failed`

**Check:**
1. Network Access allowlist in DO dashboard
2. `.env` credentials are correct
3. `odoo_app` user exists and has permissions
4. stunnel is healthy: `docker logs odoo-dbssl`

**Fix:**
```bash
# Verify allowlist
# DigitalOcean Dashboard → Databases → odoo-db-sgp1 → Network Access
# Ensure 178.128.112.214 is listed

# Test from droplet
PGPASSWORD="$DB_PASSWORD" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --set=sslmode=require
```

---

### Odoo Not Starting

**Symptom:** Container restarts repeatedly

**Check:**
```bash
# View logs
docker compose -f docker-compose.droplet.yml logs odoo

# Check healthcheck
docker inspect odoo-prod | grep -A 10 Health
```

**Common issues:**
- Database connection failed → Check stunnel logs
- Port 8069 in use → Check `netstat -tulpn | grep 8069`
- Configuration error → Check `odoo.conf.droplet` syntax

---

### stunnel SSL Errors

**Symptom:** `connect_blocking: s_connect: Connection refused`

**Check:**
```bash
# View stunnel logs
docker logs odoo-dbssl

# Verify DO database host is correct
echo $DB_HOST
```

**Fix:**
- Verify `DB_HOST` in `.env` matches DO cluster hostname
- Ensure port `25060` is correct
- Check DO database is running (DO Dashboard)

---

## Monitoring

### Health Checks

```bash
# Container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Odoo health endpoint
curl -sf http://localhost:8069/web/health

# Database connection
docker compose -f docker-compose.droplet.yml exec dbssl \
  nc -z localhost 5432 && echo "✓ stunnel OK" || echo "✗ stunnel FAIL"
```

---

### Log Rotation

Logs are automatically rotated via Docker logging driver:
- Max size: 10MB per file
- Max files: 3
- Total max: ~30MB per container

**Manual log cleanup:**
```bash
docker compose -f docker-compose.droplet.yml logs --tail 0
```

---

## Backup & Recovery

### Database Backup

```bash
# Backup from DO Managed Database
PGPASSWORD="$DB_PASSWORD" pg_dump \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --no-owner --no-acl \
  | gzip > /opt/backups/odoo_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Restore Database

```bash
# Restore to DO Managed Database
gunzip -c /opt/backups/odoo_YYYYMMDD_HHMMSS.sql.gz | \
  PGPASSWORD="$DB_PASSWORD" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME"
```

### Filestore Backup

```bash
# Backup filestore volume
docker run --rm \
  -v odoo_odoo-web-data:/data \
  -v /opt/backups:/backup \
  alpine tar czf /backup/odoo_filestore_$(date +%Y%m%d).tar.gz /data
```

---

## Upgrade Procedure

### 1. Backup Everything

```bash
# Database
pg_dump ... > backup.sql.gz

# Filestore
docker run --rm -v odoo_odoo-web-data:/data -v /opt/backups:/backup \
  alpine tar czf /backup/filestore.tar.gz /data
```

### 2. Pull New Image

```bash
docker compose -f docker-compose.droplet.yml pull
```

### 3. Upgrade Modules

```bash
docker compose -f docker-compose.droplet.yml up -d
docker compose -f docker-compose.droplet.yml exec odoo \
  odoo -d odoo -u all --stop-after-init
```

### 4. Verify

```bash
# Check version
docker compose -f docker-compose.droplet.yml exec odoo odoo --version

# Test HTTP
curl -sf http://localhost:8069/web/health
```

---

## Security Checklist

- [ ] `.env` file is secured (`chmod 600 /opt/odoo-ce/deploy/.env`)
- [ ] DO database allowlist only includes `178.128.112.214`
- [ ] `admin_passwd` is strong and unique
- [ ] `odoo_app` user has minimal permissions
- [ ] Firewall allows only necessary ports (22, 80, 443, 8069)
- [ ] SSL/TLS enforced via stunnel
- [ ] Regular backups scheduled
- [ ] Log monitoring enabled

---

**Deployment Date:** 2026-01-14
**Droplet IP:** 178.128.112.214
**Database:** odoo-db-sgp1 (PostgreSQL 16, SGP1)
**Odoo Version:** 18.0
