# Odoo Official Docker Image → TBWA\SMP Production Canonical Mapping

**Source**: https://github.com/docker-library/docs/blob/master/odoo/README.md
**Purpose**: Map official Odoo Docker conventions to TBWA\SMP production architecture

---

## Official vs TBWA\SMP Canonical

| Official Convention | TBWA\SMP Production | Notes |
|---------------------|---------------------|-------|
| **PostgreSQL Container** | DigitalOcean Managed Postgres | No container; external managed service |
| Service alias: `db` | Managed cluster: `odoo-db-sgp1` | Official "db" alias applies to container networking only |
| Container: `postgres:15` | PostgreSQL 16 (managed) | Managed version may differ from official examples |
| `HOST=db` (default) | `HOST=odoo-db-sgp1-do-user-XXXXX-0.g.db.ondigitalocean.com` | Override default with managed hostname |
| `PORT=5432` (default) | `PORT=25060` | Managed Postgres uses non-standard port |
| `POSTGRES_DB=postgres` | N/A (managed cluster) | Initial DB not applicable; Odoo DB enforced separately |
| **Odoo Container** | `odoo-prod` (single container) | Runs on droplet `178.128.112.214` |
| Service name: `web` | Container name: `odoo-prod` | Single-container deployment |
| Image: `odoo:17.0` | Image: `odoo:18` | Latest stable version |
| Volume: `/var/lib/odoo` | Named volume: `odoo-data` | Filestore persistence |
| Mount: `/mnt/extra-addons` | Bind mount: `/opt/odoo-ce/repo/addons:/mnt/extra-addons` | Custom IPAI modules |
| Mount: `/etc/odoo/odoo.conf` | Bind mount: `/opt/odoo-ce/infra/odoo.conf:/etc/odoo/odoo.conf:ro` | Production config |
| Exposed port: `8069:8069` | Behind nginx reverse proxy | `erp.insightpulseai.net`, `superset.insightpulseai.net`, `mcp.insightpulseai.net` |

---

## Canonical Invariants (TBWA\SMP Production)

### Database Configuration

```bash
# Enforced Odoo database name (inside managed PostgreSQL)
ODOO_DB_NAME=odoo

# Database filter (only allow "odoo" database)
dbfilter = ^odoo$

# Managed Postgres connection
db_host = odoo-db-sgp1-do-user-XXXXX-0.g.db.ondigitalocean.com
db_port = 25060
db_user = doadmin
db_password = ${ODOO_DB_PASSWORD}  # From ~/.zshrc or secrets manager
```

### Proxy Configuration

```ini
# Behind nginx reverse proxy (required)
proxy_mode = True

# Workers (production tuning for 8GB RAM droplet)
workers = 5
max_cron_threads = 2

# Memory limits (production)
limit_memory_hard = 2684354560  # 2.5 GB
limit_memory_soft = 2147483648  # 2 GB
```

### Volume Persistence

```yaml
volumes:
  odoo-data:  # Named volume for /var/lib/odoo (filestore + sessions)
```

---

## Verification Checklist

### 1. Container Health

```bash
# Check Odoo container status
ssh root@178.128.112.214 "docker ps -a | grep odoo"

# Expected output:
# CONTAINER ID   IMAGE       STATUS          PORTS                    NAMES
# abc123...      odoo:18     Up 2 hours      0.0.0.0:8069->8069/tcp   odoo-prod

# Check Odoo logs
ssh root@178.128.112.214 "docker logs odoo-prod --tail 50"

# Expected: No "FATAL" or "ERROR" messages, should see "HTTP service (werkzeug) running"
```

### 2. Web Accessibility

```bash
# Check Odoo web interface (via nginx proxy)
curl -sf https://erp.insightpulseai.net/web/login | grep -q "Odoo"
echo $?  # Should return 0 (success)

# Check direct container port (bypassing nginx)
curl -sf http://178.128.112.214:8069/web/login | grep -q "Odoo"
echo $?  # Should return 0 (success)
```

### 3. Database Connectivity

```bash
# Test managed Postgres connection from droplet
ssh root@178.128.112.214 "docker exec odoo-prod psql -h odoo-db-sgp1-do-user-XXXXX-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d odoo -c 'SELECT version();'"

# Expected output: PostgreSQL 16.x version string

# Verify Odoo database exists
ssh root@178.128.112.214 "docker exec odoo-prod psql -h <MANAGED_HOST> -p 25060 -U doadmin -d postgres -c '\\l' | grep odoo"

# Expected output: Line showing "odoo" database with doadmin as owner
```

### 4. Filestore Persistence

```bash
# Check filestore volume mount
ssh root@178.128.112.214 "docker inspect odoo-prod --format '{{json .Mounts}}' | jq '.[] | select(.Destination==\"/var/lib/odoo\")'"

# Expected output: Named volume "odoo-data" mounted at /var/lib/odoo

# Verify filestore directory exists and is writable
ssh root@178.128.112.214 "docker exec odoo-prod ls -la /var/lib/odoo/filestore/"
```

---

## Failure Modes + Fixes

### Cannot Connect to Database

**Symptoms:**
- Odoo logs show: `FATAL: could not connect to database`
- Web UI shows: "Database connection error"

**Root Causes:**
1. **Wrong HOST/PORT**: Official default is `HOST=db`, but production uses managed hostname
2. **Firewall rules**: Managed Postgres requires droplet IP in trusted sources
3. **Invalid credentials**: `db_user` or `db_password` incorrect

**Fixes:**
```bash
# 1. Verify environment variables
ssh root@178.128.112.214 "docker exec odoo-prod env | grep -E 'HOST|PORT|USER|PASSWORD'"

# Expected:
# HOST=odoo-db-sgp1-do-user-XXXXX-0.g.db.ondigitalocean.com
# PORT=25060
# USER=doadmin
# PASSWORD=<actual-password>

# 2. Test direct psql connection
ssh root@178.128.112.214 "psql 'postgresql://doadmin:${ODOO_DB_PASSWORD}@<MANAGED_HOST>:25060/odoo?sslmode=require'"

# 3. Check DigitalOcean firewall (trusted sources must include 178.128.112.214)
doctl databases firewalls list <DATABASE_ID>
```

### Wrong dbfilter

**Symptoms:**
- Database selector appears instead of direct login
- Error: "Access to database 'postgres' denied"

**Root Cause:**
- `dbfilter` not set to `^odoo$` (exact match for "odoo" database only)
- Odoo attempting to connect to default `postgres` database instead of `odoo`

**Fixes:**
```bash
# 1. Verify odoo.conf dbfilter setting
ssh root@178.128.112.214 "grep dbfilter /opt/odoo-ce/infra/odoo.conf"

# Expected: dbfilter = ^odoo$

# 2. If incorrect, update and restart
ssh root@178.128.112.214 "sed -i 's/^dbfilter =.*/dbfilter = ^odoo$/' /opt/odoo-ce/infra/odoo.conf && docker restart odoo-prod"
```

### "Access Denied" from RLS/ACL (Odoo-side)

**Symptoms:**
- User can log in but sees "Access Rights" error when accessing modules
- Logs show: `AccessError: You are not allowed to access this document`

**Root Cause:**
- Odoo user lacks proper security groups
- Module security rules (ir.model.access, ir.rule) misconfigured

**Fixes:**
```bash
# 1. Grant admin access (for initial setup)
ssh root@178.128.112.214 "docker exec odoo-prod odoo shell -d odoo" <<'PYTHON'
env['res.users'].browse(2).groups_id += env.ref('base.group_system')
env.cr.commit()
PYTHON

# 2. Reset admin password (if locked out)
ssh root@178.128.112.214 "docker exec odoo-prod odoo -d odoo -i base --stop-after-init --without-demo=all"
```

### Filestore Persistence Issues

**Symptoms:**
- Uploaded files disappear after container restart
- Attachment download errors: "File not found"

**Root Cause:**
- `/var/lib/odoo` not mounted to named volume (using container's ephemeral storage)
- Volume mount path incorrect

**Fixes:**
```bash
# 1. Verify named volume exists and is mounted
ssh root@178.128.112.214 "docker volume ls | grep odoo"
ssh root@178.128.112.214 "docker inspect odoo-prod --format '{{json .Mounts}}' | jq"

# 2. If volume missing, recreate container with proper mount
ssh root@178.128.112.214 "cd /opt/odoo-ce && docker compose -f infra/docker-compose.prod.yaml down"
ssh root@178.128.112.214 "docker volume create odoo-data"
ssh root@178.128.112.214 "cd /opt/odoo-ce && docker compose -f infra/docker-compose.prod.yaml up -d"
```

---

## Differences from Official Examples (Intentional)

### 1. Managed PostgreSQL Instead of Container

**Official**: Two-container setup (`db` + `web` services)
```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
  web:
    image: odoo:17.0
    depends_on: [db]
```

**TBWA\SMP**: Single Odoo container + external managed Postgres
```yaml
services:
  odoo:
    image: odoo:18
    environment:
      HOST: odoo-db-sgp1-do-user-XXXXX-0.g.db.ondigitalocean.com
      PORT: 25060
      USER: doadmin
      PASSWORD: ${ODOO_DB_PASSWORD}
```

**Rationale**: Managed Postgres provides automated backups, scaling, and maintenance without container overhead

### 2. Explicit Database Name Enforcement

**Official**: Uses default `POSTGRES_DB=postgres`, Odoo creates any database via UI
**TBWA\SMP**: Enforces single database `odoo` via `dbfilter = ^odoo$`

**Rationale**: Prevents accidental database proliferation, simplifies backup/restore, ensures consistent naming across environments

### 3. Nginx Reverse Proxy

**Official**: Direct port exposure `8069:8069`
**TBWA\SMP**: Nginx proxy with SSL termination (ports 80/443) → Odoo (8069)

**Rationale**: SSL/TLS for production, domain-based routing (`erp.insightpulseai.net`, `superset.insightpulseai.net`)

### 4. Production Tuning

**Official**: No worker configuration (single-threaded for development)
**TBWA\SMP**: Multi-worker mode with memory limits

**Rationale**: 8GB droplet requires worker tuning to handle concurrent users without OOM kills

---


### Official `db` alias vs TBWA\SMP production

Official examples assume Postgres runs as a Docker service reachable as `db`.
In TBWA\SMP production, Postgres is DO Managed DB, so there is no `db` container.
We preserve `db` as a conceptual dependency name in diagrams, but `db_host` points to the managed hostname.

**Key distinction:**
- **Official**: `HOST=db` (Docker container alias via Compose networking)
- **TBWA\SMP**: `HOST=odoo-db-sgp1-do-user-XXXXX-0.g.db.ondigitalocean.com` (managed cluster hostname)

The "db must be named db" constraint only applies to Docker container networking. With managed databases, you simply override `db_host` to point to the external hostname.

---

**Last Updated**: 2026-01-14
**Applies To**: Production droplet `178.128.112.214` (odoo-erp-prod)
**Managed Database**: `odoo-db-sgp1` (DigitalOcean PostgreSQL 16)
**Canonical Odoo Database**: `odoo` (enforced via `dbfilter = ^odoo$`)
