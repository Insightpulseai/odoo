# Database Selector Issue - Troubleshooting Guide

**Problem**: `https://erp.insightpulseai.com/web/login` redirects to `/web/database/selector`

**Root Cause**: Database connection failures cause Odoo to show database selector

---

## Diagnosis

```bash
# Check if login redirects to selector
curl -I https://erp.insightpulseai.com/web/login
# If you see: location: /web/database/selector → PROBLEM

# Check Odoo logs for database connection failures
ssh root@178.128.112.214 "docker logs odoo-prod 2>&1 | grep 'Connection to the database failed' | tail -5"
# If you see repeated failures → Database password or connection issue
```

---

## Fix 1: Update Database Password

**Symptom**: `psycopg2.OperationalError: password authentication failed for user "doadmin"`

**Solution**: Update odoo.conf with correct password

```bash
# On server
ssh root@178.128.112.214

# Edit odoo.conf
vi /etc/odoo/odoo.conf

# Find this line:
# db_password = <WRONG_PASSWORD_HERE>

# Replace with correct password from DigitalOcean dashboard:
# 1. Go to: https://cloud.digitalocean.com/databases
# 2. Select: odoo-db-sgp1
# 3. Click: "Connection Details" → Show password
# 4. Copy password and update odoo.conf

# Restart Odoo
docker restart odoo-prod

# Verify (should see no more connection failures)
docker logs odoo-prod 2>&1 | grep -E 'database|HTTP service' | tail -10
```

---

## Fix 2: Verify dbfilter Configuration

**Config location**: `/etc/odoo/odoo.conf` (inside container)

**Required settings**:
```ini
[options]
# Database filter (MUST match your database name exactly)
dbfilter = ^odoo$

# Disable database listing
list_db = False

# Database name
db_name = odoo
```

**Verification**:
```bash
# Check dbfilter in running container
ssh root@178.128.112.214 "docker exec odoo-prod grep dbfilter /etc/odoo/odoo.conf"
# Expected: dbfilter = ^odoo$

# Test that login goes directly to login page (not selector)
curl -I https://erp.insightpulseai.com/web/login
# Expected: HTTP/2 200 (not 303 redirect to /web/database/selector)
```

---

## Fix 3: Ensure Database Exists

```bash
# Connect to managed PostgreSQL (requires password)
ssh root@178.128.112.214
psql "postgresql://doadmin:CORRECT_PASSWORD_HERE@private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/postgres?sslmode=require"

# List databases
\l

# Expected output should include:
# odoo | doadmin | UTF8 | ...

# If "odoo" database doesn't exist, create it:
CREATE DATABASE odoo OWNER doadmin;
\q
```

---

## Fix 4: Restart Odoo Container

```bash
ssh root@178.128.112.214 "docker restart odoo-prod"

# Wait 10 seconds
sleep 10

# Check logs for successful startup
ssh root@178.128.112.214 "docker logs odoo-prod 2>&1 | tail -20"

# Expected (healthy):
# INFO ? odoo: Odoo version 18.0
# INFO ? odoo: database: doadmin@private-odoo-db-sgp1...
# INFO ? werkzeug: HTTP service (werkzeug) running on 0.0.0.0:8069
```

---

## Verification Checklist

After applying fixes:

1. ✅ No database connection errors in logs
2. ✅ `https://erp.insightpulseai.com/web/login` returns HTTP 200 (not 303 redirect)
3. ✅ Login page shows Odoo login form (not database selector)
4. ✅ Can log in with admin credentials
5. ✅ No database dropdown in UI (only one database available)

---

## Common Mistakes

### Mistake 1: Wrong dbfilter regex

```ini
# WRONG (will not match)
dbfilter = odoo          # Missing regex anchors
dbfilter = ^.*$          # Matches all databases (shows selector)
dbfilter = ^Odoo$        # Case-sensitive mismatch

# CORRECT
dbfilter = ^odoo$        # Exact match for "odoo" database
```

### Mistake 2: list_db = True

```ini
# WRONG
list_db = True           # Allows database listing

# CORRECT
list_db = False          # Disables database listing
```

### Mistake 3: No db_name parameter

```ini
# Add this if missing:
db_name = odoo           # Explicit database name
```

---

## Emergency Recovery

If Odoo is completely broken:

```bash
# 1. Stop Odoo
ssh root@178.128.112.214 "docker stop odoo-prod"

# 2. Backup current config
ssh root@178.128.112.214 "docker exec odoo-prod cat /etc/odoo/odoo.conf > /root/odoo.conf.backup"

# 3. Create minimal working config
ssh root@178.128.112.214 "cat > /tmp/odoo.conf.minimal <<'EOF'
[options]
admin_passwd = admin
db_host = private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
db_port = 25060
db_user = doadmin
db_password = CORRECT_PASSWORD_FROM_DO_DASHBOARD
db_name = odoo
db_sslmode = require
addons_path = /usr/lib/python3/dist-packages/odoo/addons
http_port = 8069
dbfilter = ^odoo$
list_db = False
proxy_mode = True
EOF"

# 4. Copy to container
ssh root@178.128.112.214 "docker cp /tmp/odoo.conf.minimal odoo-prod:/etc/odoo/odoo.conf"

# 5. Start Odoo
ssh root@178.128.112.214 "docker start odoo-prod"

# 6. Verify
ssh root@178.128.112.214 "docker logs odoo-prod -f"
```

---

**Last Updated**: 2026-01-14
**Applies To**: Production Odoo CE 18.0 (`erp.insightpulseai.com`)
**Container**: `odoo-prod`
**Database**: `odoo` on managed PostgreSQL
