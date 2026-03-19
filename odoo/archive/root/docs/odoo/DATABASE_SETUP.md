# Odoo Database Setup - DigitalOcean PostgreSQL Cluster

## Infrastructure Overview

**Cluster Details:**
- **Name**: odoo-db-sgp1
- **Location**: Singapore (SGP1)
- **Version**: PostgreSQL 16.11
- **Host**: odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
- **Port**: 25060 (managed cluster custom port)

**Databases:**
- `odoo_dev` - Development database (use for local IDE)
- `odoo_stage` - Staging database
- `odoo_prod` - Production database (mapped to odoo19)

**Authentication:**
- **Admin Role**: `doadmin` (full privileges, DO managed)
- **App Role**: `odoo_app` (least-privilege role for Odoo)

## Network Architecture

The DigitalOcean managed PostgreSQL cluster is in a **private network** and **not directly accessible** from external IP addresses. Access requires:

1. **From DigitalOcean Droplet** (178.128.112.214): Direct connection via private network
2. **From Local Development Machine**: SSH tunnel through the droplet

## Configuration Files

### 1. Direct Connection (odoo.conf)
**Location**: `/Users/tbwa/Library/Mobile Documents/com~apple~CloudDocs/Documents/TBWA/odoo/odoo/config/odoo.conf`

**Use Case**: Production deployments, server-side operations

```ini
[options]
db_host = odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
db_port = 25060
db_user = odoo_app
db_password = OdooAppDev2026
db_name = odoo_dev
db_sslmode = require
list_db = False
```

**Note**: This configuration will **NOT work** from local development machine due to network restrictions.

### 2. SSH Tunnel Configuration (odoo-tunnel.conf)
**Location**: `/Users/tbwa/Library/Mobile Documents/com~apple~CloudDocs/Documents/TBWA/odoo/odoo/config/odoo-tunnel.conf`

**Use Case**: Local development via VS Code, debugging

```ini
[options]
db_host = localhost
db_port = 5433
db_user = odoo_app
db_password = OdooAppDev2026
db_name = odoo_dev
db_sslmode = disable
list_db = False
```

**Prerequisites**: SSH tunnel must be running (see below)

## Local Development Setup

### Step 1: Start SSH Tunnel

```bash
# Terminal 1: Start tunnel (keep running)
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
./scripts/ssh-tunnel-db.sh

# Output:
# === Setting up SSH tunnel to DigitalOcean PostgreSQL ===
# Remote: odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060
# Local: localhost:5433
#
# Press Ctrl+C to stop the tunnel
```

**Verify tunnel is working:**
```bash
# Terminal 2: Test connection
PGPASSWORD="OdooAppDev2026" psql -h localhost -p 5433 -U odoo_app -d odoo_dev -c "SELECT version();"

# Expected output:
# PostgreSQL 16.11 on x86_64-pc-linux-gnu...
```

### Step 2: Update VS Code Launch Configuration

**File**: `.vscode/launch.json`

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Odoo: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/vendor/odoo/odoo-bin",
            "args": [
                "-c",
                "/Users/tbwa/Library/Mobile Documents/com~apple~CloudDocs/Documents/TBWA/odoo/odoo/config/odoo-tunnel.conf"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/vendor/odoo",
            "justMyCode": false,
            "env": {
                "PYTHONPATH": "${workspaceFolder}/vendor/odoo"
            }
        }
    ]
}
```

### Step 3: Initialize Odoo Database (First Time Only)

```bash
# With tunnel running in Terminal 1
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/vendor/odoo

# Initialize base modules
python3 odoo-bin \
  -c "/Users/tbwa/Library/Mobile Documents/com~apple~CloudDocs/Documents/TBWA/odoo/odoo/config/odoo-tunnel.conf" \
  -d odoo_dev \
  -i base \
  --stop-after-init \
  --log-level=info

# Expected output:
# INFO odoo_dev odoo.modules.loading: 42 modules loaded in 2.3s, 0 queries
# INFO odoo_dev odoo.modules.registry: Registry loaded in 0.5s
```

### Step 4: Start Odoo via VS Code

1. Ensure SSH tunnel is running in Terminal 1
2. Press **F5** in VS Code
3. Odoo should start and connect to odoo_dev database
4. Access at http://localhost:8069

## Database Management

### Create Staging/Production Databases

Staging and production databases already exist but are empty:

```bash
# Connect via tunnel
PGPASSWORD="OdooAppDev2026" psql -h localhost -p 5433 -U odoo_app -d odoo_stage

# Or via DigitalOcean droplet
ssh root@178.128.112.214
PGPASSWORD="OdooAppDev2026" psql -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U odoo_app -d odoo_stage
```

### Database Roles and Permissions

```sql
-- View role details
\du odoo_app

-- View database ownership
\l odoo_dev

-- Check schema privileges
\dn+ public

-- Expected privileges for odoo_app:
-- - ALL on DATABASE odoo_dev, odoo_stage
-- - ALL on SCHEMA public
-- - ALL on ALL TABLES IN SCHEMA public
-- - ALL on ALL SEQUENCES IN SCHEMA public
```

### Backup and Restore

```bash
# Backup (via tunnel)
PGPASSWORD="OdooAppDev2026" pg_dump -h localhost -p 5433 -U odoo_app -d odoo_dev -Fc -f odoo_dev_backup.dump

# Backup (via droplet)
ssh root@178.128.112.214 "PGPASSWORD='OdooAppDev2026' pg_dump -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U odoo_app -d odoo_dev -Fc" > odoo_dev_backup.dump

# Restore (via tunnel)
PGPASSWORD="OdooAppDev2026" pg_restore -h localhost -p 5433 -U odoo_app -d odoo_dev -c odoo_dev_backup.dump

# Restore (via droplet)
cat odoo_dev_backup.dump | ssh root@178.128.112.214 "PGPASSWORD='OdooAppDev2026' pg_restore -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U odoo_app -d odoo_dev -c"
```

## Troubleshooting

### Connection Timeout

**Symptom**: Connection to odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com times out

**Cause**: Database cluster is in private network, not accessible from external IPs

**Solution**: Use SSH tunnel (see Step 1 above)

### Password Authentication Failed

**Symptom**: `FATAL: password authentication failed for user "odoo_app"`

**Causes**:
1. Wrong password in config file
2. Special characters in password not properly escaped
3. Role doesn't have LOGIN privilege

**Solutions**:
```bash
# Reset password (via doadmin)
ssh root@178.128.112.214 'PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d odoo_dev -c "ALTER ROLE odoo_app WITH PASSWORD '\''OdooAppDev2026'\'';"'

# Verify role can login
ssh root@178.128.112.214 'PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d odoo_dev -c "\du odoo_app"'
```

### SSH Tunnel Already Running

**Symptom**: "Address already in use" when starting tunnel

**Solution**:
```bash
# Find existing tunnel process
ps aux | grep "ssh.*25060"

# Kill existing tunnel
pkill -f "ssh.*odoo-db-sgp1.*25060"

# Or kill by PID
kill <PID>

# Restart tunnel
./scripts/ssh-tunnel-db.sh
```

### Odoo Cannot Connect via Tunnel

**Symptom**: Odoo shows "database connection error"

**Checklist**:
1. ✅ SSH tunnel is running (check Terminal 1)
2. ✅ Test direct psql connection: `PGPASSWORD="OdooAppDev2026" psql -h localhost -p 5433 -U odoo_app -d odoo_dev -c "SELECT 1;"`
3. ✅ Verify config file path in VS Code launch.json
4. ✅ Check db_sslmode is "disable" in odoo-tunnel.conf (not "require" for tunnel)
5. ✅ Restart Odoo after config changes

## Security Notes

### Credentials Storage

**Current Location**: Config files in iCloud directory (not committed to git)

**Best Practice** (for production):
```bash
# Store password in environment variable
export ODOO_DB_PASSWORD="OdooAppDev2026"

# Reference in odoo.conf
db_password = ${ODOO_DB_PASSWORD}

# Add to ~/.zshrc for persistence
echo 'export ODOO_DB_PASSWORD="OdooAppDev2026"' >> ~/.zshrc
```

### Password Rotation

To change odoo_app password:

```bash
# 1. Connect as doadmin
ssh root@178.128.112.214
PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d odoo_dev

# 2. Reset password
ALTER ROLE odoo_app WITH PASSWORD 'NewSecurePassword';

# 3. Update all config files
# - odoo.conf
# - odoo-tunnel.conf
# - VS Code launch.json (if hardcoded)
# - ~/.zshrc (if using env vars)
```

## Production Database Mapping

**Current State** (from production config):
- Production uses database `odoo19` (not `odoo_prod`)
- User: `doadmin`
- Host: `private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com` (private endpoint)

**Recommended Migration**:
1. Rename `odoo19` → `odoo_prod` for consistency
2. Create `odoo_app` role for production (least-privilege)
3. Update production odoo.conf to use `odoo_app` role

```bash
# Rename database (requires downtime)
ssh root@178.128.112.214
PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d defaultdb

-- Stop Odoo first
ALTER DATABASE odoo19 RENAME TO odoo_prod;

-- Verify
\l odoo_prod
```

## Next Steps

1. ✅ Database infrastructure configured (odoo_dev, odoo_stage created)
2. ✅ odoo_app role created with proper permissions
3. ✅ SSH tunnel script created
4. ✅ Config files created (direct + tunnel modes)
5. ⏳ Test Odoo initialization via tunnel
6. ⏳ Update VS Code launch configuration
7. ⏳ Document workflow in team wiki

**Test Command**:
```bash
# Start tunnel
./scripts/ssh-tunnel-db.sh

# In another terminal, test Odoo
cd vendor/odoo
python3 odoo-bin -c "/Users/tbwa/Library/Mobile Documents/com~apple~CloudDocs/Documents/TBWA/odoo/odoo/config/odoo-tunnel.conf" --version

# Expected: Odoo Server 19.0
```

---

**Last Updated**: 2026-02-09
**Maintained By**: Development Team
