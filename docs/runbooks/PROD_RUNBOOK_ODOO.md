# Production Runbook: Odoo on TBWA\SMP Infrastructure

**Droplet**: `178.128.112.214` (odoo-erp-prod, 8GB RAM, SGP1)
**Managed DB**: `odoo-db-sgp1` (DigitalOcean PostgreSQL 16, 1GB RAM)
**Canonical Database**: `odoo` (enforced via `dbfilter = ^odoo$`)
**Domains**: `erp.insightpulseai.com`, `superset.insightpulseai.com`, `mcp.insightpulseai.com`

---

## Start / Stop / Restart

### Start Odoo Stack

```bash
# SSH to production droplet
ssh root@178.128.112.214

# Navigate to infra directory
cd /opt/odoo-ce/infra

# Start Odoo container (uses docker-compose.prod.yaml)
docker compose -f docker-compose.prod.yaml up -d

# Verify container started
docker ps | grep odoo-prod

# Expected output:
# abc123...  odoo:18  Up 5 seconds  0.0.0.0:8069->8069/tcp  odoo-prod
```

### Stop Odoo Stack

```bash
ssh root@178.128.112.214
cd /opt/odoo-ce/infra
docker compose -f docker-compose.prod.yaml stop

# Verify container stopped
docker ps -a | grep odoo-prod

# Expected output:
# abc123...  odoo:18  Exited (0) 2 seconds ago  odoo-prod
```

### Restart Odoo (after config changes)

```bash
ssh root@178.128.112.214
cd /opt/odoo-ce/infra

# Graceful restart (preserves connections)
docker compose -f docker-compose.prod.yaml restart odoo

# Hard restart (faster, drops connections)
docker restart odoo-prod

# Verify restart succeeded
docker logs odoo-prod --tail 50
# Look for: "HTTP service (werkzeug) running on 0.0.0.0:8069"
```

---

## Health Checks

### Container Health

```bash
# Check container status
ssh root@178.128.112.214 "docker ps -a | grep odoo"

# Check container resource usage
ssh root@178.128.112.214 "docker stats odoo-prod --no-stream"

# Expected output (healthy):
# CONTAINER    CPU %   MEM USAGE / LIMIT     MEM %   NET I/O
# odoo-prod    15.2%   1.2GiB / 3.8GiB      31.5%   12MB / 8MB
```

### Web Interface Health

```bash
# Check Odoo web login (via nginx proxy)
curl -sf https://erp.insightpulseai.com/web/login | grep -q "Odoo"
echo $?  # Should return 0

# Check direct container port (bypassing nginx)
curl -sf http://178.128.112.214:8069/web/login | grep -q "Odoo"
echo $?  # Should return 0

# Get HTTP response headers
curl -I https://erp.insightpulseai.com/web/login
# Expected: HTTP/2 200 OK
```

### Application Logs

```bash
# View recent logs
ssh root@178.128.112.214 "docker logs odoo-prod --tail 100"

# Follow logs in real-time
ssh root@178.128.112.214 "docker logs odoo-prod -f"

# Search for errors
ssh root@178.128.112.214 "docker logs odoo-prod --since 1h | grep -E 'ERROR|CRITICAL|FATAL'"

# Expected (healthy): No ERROR/CRITICAL/FATAL messages
```

---

## Database Checks

### Verify Database Connection

```bash
# Test psql connection from droplet
ssh root@178.128.112.214 "docker exec odoo-prod psql \
  -h odoo-db-sgp1-do-user-XXXXX-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d odoo \
  -c 'SELECT version();'"

# Expected output: PostgreSQL 16.x version string
```

### List All Databases

```bash
ssh root@178.128.112.214 "docker exec odoo-prod psql \
  -h <MANAGED_HOST> \
  -p 25060 \
  -U doadmin \
  -d postgres \
  -c '\l'"

# Expected output: Should show "odoo" database with doadmin as owner
```

### Check Database Size

```bash
ssh root@178.128.112.214 "docker exec odoo-prod psql \
  -h <MANAGED_HOST> \
  -p 25060 \
  -U doadmin \
  -d odoo \
  -c 'SELECT pg_size_pretty(pg_database_size(current_database()));'"

# Example output: "245 MB"
```

### Verify Odoo Can Access Database

```bash
# Run Odoo shell (Python REPL with Odoo environment)
ssh root@178.128.112.214 "docker exec -it odoo-prod odoo shell -d odoo" <<'PYTHON'
# Test database connectivity
env['res.users'].search_count([])  # Should return user count (e.g., 5)
env.cr.execute("SELECT version()")
print(env.cr.fetchone())  # Should print PostgreSQL version
exit()
PYTHON
```

---

## Upgrade Modules

### Upgrade Single Module

```bash
# Syntax: odoo -d <database> -u <module> --stop-after-init
ssh root@178.128.112.214 "docker exec odoo-prod odoo -d odoo -u ipai_finance_ppm --stop-after-init"

# Verify upgrade succeeded (check logs)
ssh root@178.128.112.214 "docker logs odoo-prod --tail 50 | grep -E 'ipai_finance_ppm|Module.*loaded'"

# Restart Odoo to apply changes
ssh root@178.128.112.214 "docker restart odoo-prod"
```

### Upgrade Multiple Modules

```bash
# Comma-separated list
ssh root@178.128.112.214 "docker exec odoo-prod odoo -d odoo -u ipai_finance_ppm,ipai_workspace_core,ipai_ce_branding --stop-after-init"

# Restart after upgrade
ssh root@178.128.112.214 "docker restart odoo-prod"
```

### Upgrade All Modules (use with caution)

```bash
# Update module list first
ssh root@178.128.112.214 "docker exec odoo-prod odoo -d odoo --update=all --stop-after-init"

# WARNING: This can take 10-30 minutes depending on module count
# Monitor progress via logs:
ssh root@178.128.112.214 "docker logs odoo-prod -f"
```

### Install New Module

```bash
# Syntax: odoo -d <database> -i <module> --stop-after-init
ssh root@178.128.112.214 "docker exec odoo-prod odoo -d odoo -i ipai_new_module --stop-after-init"

# Verify installation
ssh root@178.128.112.214 "docker logs odoo-prod --tail 50 | grep 'ipai_new_module'"

# Restart to load module
ssh root@178.128.112.214 "docker restart odoo-prod"
```

---

## Backup / Restore Notes

### Filestore Backup (Attachments)

```bash
# Backup named volume to tarball
ssh root@178.128.112.214 "docker run --rm -v odoo-data:/data -v /root/backups:/backup alpine tar -czf /backup/odoo-filestore-$(date +%Y%m%d-%H%M%S).tar.gz -C /data ."

# Verify backup created
ssh root@178.128.112.214 "ls -lh /root/backups/odoo-filestore-*.tar.gz"
```

### Filestore Restore

```bash
# Stop Odoo first
ssh root@178.128.112.214 "docker stop odoo-prod"

# Restore from tarball
ssh root@178.128.112.214 "docker run --rm -v odoo-data:/data -v /root/backups:/backup alpine sh -c 'cd /data && tar -xzf /backup/odoo-filestore-YYYYMMDD-HHMMSS.tar.gz'"

# Start Odoo
ssh root@178.128.112.214 "docker start odoo-prod"
```

### Database Backup (Managed PostgreSQL)

**Recommended**: Use DigitalOcean's automated backups (enabled on managed cluster)

**Manual backup via pg_dump:**
```bash
ssh root@178.128.112.214 "docker exec odoo-prod pg_dump \
  -h <MANAGED_HOST> \
  -p 25060 \
  -U doadmin \
  -d odoo \
  --format=custom \
  --file=/tmp/odoo-backup-$(date +%Y%m%d-%H%M%S).dump"

# Copy backup out of container
ssh root@178.128.112.214 "docker cp odoo-prod:/tmp/odoo-backup-*.dump /root/backups/"
```

### Database Restore

```bash
# WARNING: This will drop and recreate the database
ssh root@178.128.112.214 "docker exec odoo-prod dropdb \
  -h <MANAGED_HOST> \
  -p 25060 \
  -U doadmin \
  --if-exists odoo"

ssh root@178.128.112.214 "docker exec odoo-prod createdb \
  -h <MANAGED_HOST> \
  -p 25060 \
  -U doadmin \
  odoo"

ssh root@178.128.112.214 "docker exec odoo-prod pg_restore \
  -h <MANAGED_HOST> \
  -p 25060 \
  -U doadmin \
  -d odoo \
  --no-owner \
  /tmp/odoo-backup-YYYYMMDD-HHMMSS.dump"
```

---

## Common Maintenance Tasks

### View Active Sessions

```bash
ssh root@178.128.112.214 "docker exec odoo-prod psql \
  -h <MANAGED_HOST> \
  -p 25060 \
  -U doadmin \
  -d odoo \
  -c 'SELECT pid, usename, application_name, client_addr, state FROM pg_stat_activity WHERE datname = '\''odoo'\'';'"
```

### Kill Specific Database Session

```bash
# Get session PID from above query, then:
ssh root@178.128.112.214 "docker exec odoo-prod psql \
  -h <MANAGED_HOST> \
  -p 25060 \
  -U doadmin \
  -d odoo \
  -c 'SELECT pg_terminate_backend(<PID>);'"
```

### Clear Odoo Cache

```bash
# Restart Odoo to clear in-memory cache
ssh root@178.128.112.214 "docker restart odoo-prod"

# Or use Odoo shell to clear specific caches
ssh root@178.128.112.214 "docker exec -it odoo-prod odoo shell -d odoo" <<'PYTHON'
env.registry.clear_caches()
exit()
PYTHON
```

### Update Module List (after adding new addons)

```bash
ssh root@178.128.112.214 "docker exec odoo-prod odoo -d odoo --update=base --stop-after-init"
ssh root@178.128.112.214 "docker restart odoo-prod"
```

---

## Troubleshooting Quick Reference

| Symptom | Command | Expected Output |
|---------|---------|-----------------|
| Container not starting | `docker logs odoo-prod` | Look for FATAL errors |
| Database connection fails | `docker exec odoo-prod psql -h <HOST> -p 25060 -U doadmin -d odoo -c 'SELECT 1;'` | Returns `1` |
| High memory usage | `docker stats odoo-prod --no-stream` | <80% of 3.8GiB limit |
| Web interface slow | `curl -w '%{time_total}\n' -o /dev/null -s https://erp.insightpulseai.com/web/login` | <2 seconds |
| Module upgrade failed | `docker logs odoo-prod | grep ERROR` | Identify error message |

---

**Last Updated**: 2026-01-14
**Applies To**: Production droplet `178.128.112.214` (odoo-erp-prod)
**Managed Database**: `odoo-db-sgp1` (DigitalOcean PostgreSQL 16)
**Canonical Odoo Database**: `odoo`
