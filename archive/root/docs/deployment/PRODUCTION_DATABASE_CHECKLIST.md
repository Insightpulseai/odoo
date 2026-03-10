# Production Database Creation Checklist

**Purpose**: Formal procedure for creating `odoo_prod` database when ready to promote from staging.

**Prerequisites**:
- ✅ `odoo_dev` fully initialized and tested
- ✅ `odoo_stage` contains validated data and configuration
- ✅ All staging tests passing
- ✅ Production deployment plan approved

---

## Pre-Creation Checklist

### 1. Staging Validation

- [ ] All Odoo modules installed and configured in `odoo_stage`
- [ ] Data migration scripts tested and verified
- [ ] Security policies (RLS, permissions) validated
- [ ] Performance testing completed (load tests, response times)
- [ ] Backup/restore procedures tested
- [ ] Disaster recovery plan documented

### 2. Production Environment Preparation

- [ ] Production Odoo configuration file ready
- [ ] Production domain and SSL certificates configured
- [ ] Production firewall rules and security groups configured
- [ ] Production monitoring and alerting configured
- [ ] Production backup schedule configured (daily minimum)
- [ ] Incident response procedures documented

### 3. Team Readiness

- [ ] Database admin trained on production procedures
- [ ] DevOps team briefed on deployment workflow
- [ ] Support team trained on troubleshooting procedures
- [ ] Rollback procedures documented and tested
- [ ] Communication plan for production cutover

---

## Database Creation Procedure

### Step 1: Create Production Database

**Executor**: Database Administrator
**Approval Required**: YES (signed-off by DevOps Lead)

```bash
# Connect as doadmin via DigitalOcean droplet
ssh root@178.128.112.214

# Create production database
PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d defaultdb \
  << EOF

-- Create production database
CREATE DATABASE odoo_prod
  ENCODING 'UTF8'
  LC_COLLATE 'en_US.UTF-8'
  LC_CTYPE 'en_US.UTF-8'
  TEMPLATE template0;

-- Grant privileges to odoo_app
GRANT ALL PRIVILEGES ON DATABASE odoo_prod TO odoo_app;

-- Verify creation
\l odoo_prod

EOF
```

**Verification**:
```bash
# Confirm database exists
PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d defaultdb \
  -c "\l odoo_prod"

# Expected output:
#   Name    |  Owner  | Encoding |   Collate   |    Ctype
# ----------+---------+----------+-------------+-------------
#  odoo_prod | doadmin | UTF8     | en_US.UTF-8 | en_US.UTF-8
```

### Step 2: Configure Schema Permissions

```bash
# Connect to odoo_prod
PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d odoo_prod \
  << EOF

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO odoo_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO odoo_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO odoo_app;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO odoo_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO odoo_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO odoo_app;

-- Verify permissions
\du odoo_app
\dn+ public

EOF
```

### Step 3: Initialize or Restore Data

**Option A: Fresh Initialization (New Production)**
```bash
# Initialize with base modules only (no demo data)
python3 odoo-bin \
  -c /path/to/production/odoo.conf \
  -d odoo_prod \
  -i base \
  --without-demo=all \
  --stop-after-init \
  --log-level=info

# Verify initialization
PGPASSWORD="OdooAppDev2026" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo_prod \
  -c "SELECT COUNT(*) FROM ir_module_module WHERE state='installed';"
```

**Option B: Restore from Staging (Promotion)**
```bash
# 1. Backup staging database
PGPASSWORD="OdooAppDev2026" pg_dump \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo_stage \
  -Fc \
  -f odoo_stage_$(date +%Y%m%d_%H%M%S).dump

# 2. Restore to production
PGPASSWORD="OdooAppDev2026" pg_restore \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo_prod \
  -c \
  --if-exists \
  odoo_stage_$(date +%Y%m%d_%H%M%S).dump

# 3. Update production-specific settings
PGPASSWORD="OdooAppDev2026" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo_prod \
  << EOF

-- Remove demo data if any
DELETE FROM ir_demo;

-- Update base URL for production
UPDATE ir_config_parameter SET value = 'https://insightpulseai.com' WHERE key = 'web.base.url';

-- Disable test modes
UPDATE ir_config_parameter SET value = 'False' WHERE key = 'test_mode';

-- Set production email settings
UPDATE ir_mail_server SET smtp_host = 'smtp.zoho.com', smtp_port = 587 WHERE active = true;

EOF
```

### Step 4: Production Configuration File

Create production-specific config:

```bash
# /etc/odoo/odoo-prod.conf
[options]
# Database: DigitalOcean Managed PostgreSQL (odoo_prod)
db_host = private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
db_port = 25060
db_user = odoo_app
db_password = ${ODOO_DB_PASSWORD}
db_name = odoo_prod
db_sslmode = require

# Security (PRODUCTION LOCKED)
admin_passwd = ${ODOO_ADMIN_PASSWORD}
list_db = False
dbfilter = ^odoo_prod$

# Performance (tuned for production)
workers = 4
max_cron_threads = 2
db_maxconn = 64
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200

# Proxy mode (behind reverse proxy)
proxy_mode = True

# Logging (production level)
logfile = /var/log/odoo/odoo-prod.log
log_level = warn
log_handler = :WARN,werkzeug:CRITICAL

# No demo data
without_demo = all

# Email (Zoho SMTP)
smtp_server = smtp.zoho.com
smtp_port = 587
smtp_user = notifications@insightpulseai.com
smtp_password = ${ZOHO_SMTP_PASSWORD}
smtp_ssl = True
email_from = notifications@insightpulseai.com
```

### Step 5: Verification Tests

```bash
# 1. Connection test
PGPASSWORD="OdooAppDev2026" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo_prod \
  -c "SELECT current_database(), current_user, version();"

# 2. Table count
PGPASSWORD="OdooAppDev2026" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo_prod \
  -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"

# 3. Module installation check
PGPASSWORD="OdooAppDev2026" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo_prod \
  -c "SELECT name, state FROM ir_module_module WHERE state = 'installed' ORDER BY name;"

# 4. No demo data check
PGPASSWORD="OdooAppDev2026" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo_prod \
  -c "SELECT COUNT(*) FROM ir_demo;"
# Expected: 0

# 5. Configuration parameters check
PGPASSWORD="OdooAppDev2026" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U odoo_app \
  -d odoo_prod \
  -c "SELECT key, value FROM ir_config_parameter WHERE key IN ('web.base.url', 'test_mode') ORDER BY key;"
```

### Step 6: Backup Configuration

```bash
# Configure automated backups via DigitalOcean
doctl databases backup list odoo-db-sgp1

# Verify backup retention policy
doctl databases get odoo-db-sgp1 --format BackupRetentionPeriodDays

# Test manual backup
doctl databases backup create odoo-db-sgp1
```

### Step 7: Security Hardening

```bash
# 1. Revoke public schema creation
PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d odoo_prod \
  -c "REVOKE CREATE ON SCHEMA public FROM PUBLIC;"

# 2. Set connection limits
PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d odoo_prod \
  -c "ALTER ROLE odoo_app CONNECTION LIMIT 50;"

# 3. Enable connection logging
PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d odoo_prod \
  -c "ALTER DATABASE odoo_prod SET log_connections = on;"
```

---

## Post-Creation Checklist

### Database Level
- [ ] Database created successfully
- [ ] odoo_app role has correct permissions
- [ ] Schema initialized with Odoo tables
- [ ] No demo data present (production)
- [ ] Configuration parameters set correctly
- [ ] Connection limits configured
- [ ] Backup schedule verified

### Application Level
- [ ] Odoo starts successfully with odoo_prod
- [ ] Web interface accessible
- [ ] Login works with admin credentials
- [ ] All critical modules installed
- [ ] Email notifications working
- [ ] SSL/TLS configured
- [ ] Reverse proxy configured

### Security
- [ ] list_db = False enforced
- [ ] dbfilter restricts to odoo_prod only
- [ ] Admin password changed from default
- [ ] Database passwords rotated
- [ ] Firewall rules verified
- [ ] SSL certificates valid

### Monitoring
- [ ] Database monitoring enabled
- [ ] Application monitoring enabled
- [ ] Log aggregation configured
- [ ] Alert notifications configured
- [ ] Backup alerts configured
- [ ] Performance metrics baseline established

### Documentation
- [ ] Production runbook updated
- [ ] Connection details documented (securely)
- [ ] Rollback procedures documented
- [ ] Support procedures documented
- [ ] Incident response plan updated

---

## Rollback Procedure

If production database creation fails or needs to be reverted:

```bash
# 1. Stop Odoo application
sudo systemctl stop odoo

# 2. Drop production database
PGPASSWORD="REDACTED_DO_DB_PASSWORD" psql \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -U doadmin \
  -d defaultdb \
  -c "DROP DATABASE IF EXISTS odoo_prod;"

# 3. Revert configuration
mv /etc/odoo/odoo-prod.conf.backup /etc/odoo/odoo-prod.conf

# 4. Restart Odoo with previous configuration
sudo systemctl start odoo

# 5. Verify rollback
sudo systemctl status odoo
```

---

## Success Criteria

**Production database is ready when ALL of these pass:**

✅ Database `odoo_prod` exists and is accessible
✅ Role `odoo_app` has correct privileges
✅ Odoo schema initialized (>200 tables)
✅ Zero demo data records
✅ Configuration parameters match production requirements
✅ Backups configured and tested
✅ Monitoring and alerting active
✅ Security hardening complete
✅ Team trained on production procedures
✅ Rollback plan tested and documented

---

**Approval Required Before Execution:**
- [ ] DevOps Lead
- [ ] Database Administrator
- [ ] Project Manager

**Sign-off Date**: _____________
**Executed By**: _____________
**Execution Date**: _____________
