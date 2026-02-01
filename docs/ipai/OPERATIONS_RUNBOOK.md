# IPAI Module Suite - Operations Runbook

## Overview

Operational procedures for deploying, monitoring, maintaining, and troubleshooting the IPAI module suite on Odoo 18 CE.

**Production Environment**:
- **Host**: 159.223.75.148 (odoo-erp-prod droplet - DigitalOcean SGP1)
- **Database**: PostgreSQL 15 (`odoo` database)
- **Containers**: `odoo-accounting`, `odoo-core`, `odoo-marketing`, `odoo-db-1`
- **Deployment**: Docker Compose (enterprise-parity stack)
- **Monitoring**: Enhanced health check scripts + n8n workflows

**Stack Components**:
- **Odoo**: 18.0 CE + OCA modules + 30 IPAI modules
- **PostgreSQL**: 16-alpine (primary database)
- **Redis**: 7-alpine (session cache + queue)
- **Nginx**: Reverse proxy with SSL termination
- **n8n**: Workflow automation (Mattermost notifications, BIR alerts)

---

## Table of Contents

1. [Deployment Procedures](#deployment-procedures)
2. [Monitoring & Health Checks](#monitoring--health-checks)
3. [Backup & Restore](#backup--restore)
4. [Module Upgrade Procedures](#module-upgrade-procedures)
5. [Database Maintenance](#database-maintenance)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)
8. [Incident Response](#incident-response)
9. [Disaster Recovery](#disaster-recovery)
10. [Operational Checklists](#operational-checklists)

---

## Deployment Procedures

### Pre-Deployment Checklist

**24 Hours Before Deployment**:
- [ ] Review [CHANGELOG.md](./CHANGELOG.md) for breaking changes
- [ ] Notify all users via Mattermost (scheduled downtime if required)
- [ ] Backup production database (see [Backup Procedures](#full-database-backup))
- [ ] Test deployment in staging environment
- [ ] Verify all module dependencies installed (see [INSTALLATION.md](./INSTALLATION.md))
- [ ] Review security changes (see [SECURITY_MODEL.md](./SECURITY_MODEL.md))

**1 Hour Before Deployment**:
- [ ] Take final database backup
- [ ] Enable maintenance mode in Odoo
- [ ] Stop all cron jobs temporarily
- [ ] Verify no users actively in system (check active sessions)

### Standard Deployment Procedure (Docker Compose)

**Location**: DigitalOcean droplet 159.223.75.148

**Step 1: SSH to Production Server**
```bash
ssh root@159.223.75.148
cd /opt/odoo-ce
```

**Step 2: Pull Latest Code**
```bash
# Pull from main branch
git fetch origin
git status  # Verify clean working tree
git pull origin main

# Verify correct commit
git log -1 --oneline
# Expected: Latest commit from GitHub
```

**Step 3: Stop Odoo Containers**
```bash
# Stop all Odoo services (keep database running)
docker stop odoo-accounting odoo-core odoo-marketing

# Verify services stopped
docker ps | grep odoo
# Should only show odoo-db-1 running
```

**Step 4: Rebuild Docker Images (if Dockerfile changes)**
```bash
# Rebuild Odoo image with new addons
docker-compose -f docker/docker-compose.enterprise-parity.yml build odoo

# Verify image built
docker images | grep odoo-ce
# Expected: New image with today's timestamp
```

**Step 5: Start Odoo Containers**
```bash
# Start all services
docker-compose -f docker/docker-compose.enterprise-parity.yml up -d

# Verify services started
docker ps | grep odoo
# Expected: odoo-accounting, odoo-core, odoo-marketing, odoo-db-1 all running
```

**Step 6: Monitor Startup Logs**
```bash
# Follow logs for errors
docker logs -f odoo-accounting

# Watch for:
# ✓ "INFO odoo odoo.service.server: HTTP service (werkzeug) running on 0.0.0.0:8069"
# ✓ "INFO odoo odoo.modules.loading: Modules loaded."
# ✗ "ERROR odoo odoo.modules.loading: Module xxx not found"
```

**Step 7: Module Installation/Upgrade**
```bash
# Install new modules (if applicable)
docker exec -it odoo-accounting odoo-bin \
  -d odoo \
  -i <module_name> \
  --stop-after-init \
  --logfile=/var/log/odoo/install.log

# Upgrade existing modules
docker exec -it odoo-accounting odoo-bin \
  -d odoo \
  -u <module_name> \
  --stop-after-init \
  --logfile=/var/log/odoo/upgrade.log
```

**Step 8: Database Verification**
```bash
# Verify module installation
docker exec -it odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE 'ipai_%' ORDER BY name;"

# Expected: All modules state='installed', latest_version matches manifest
```

**Step 9: Restart Services**
```bash
# Restart Odoo to pickup new modules
docker restart odoo-accounting odoo-core odoo-marketing

# Wait 60 seconds for full startup
sleep 60
```

**Step 10: Health Check Verification**
```bash
# Run health check script
./scripts/enhanced_health_check.sh

# Expected output:
# ✓ Odoo process is running
# ✓ Database connection is healthy
# ✓ Disk usage: XX% (below 90% threshold)
# ✓ Memory usage: XX% (below 90% threshold)
# ✓ HTTP endpoint /web/health returns 200
```

**Step 11: Functional Smoke Tests**
```bash
# Test critical workflows
curl -sf https://odoo.insightpulseai.com/web/login | grep -q "Database Manager" && echo "✓ Login page accessible"

# Test Finance PPM dashboard
curl -sf https://odoo.insightpulseai.com/ipai/finance/ppm | grep -q "TBWA Finance PPM Dashboard" && echo "✓ PPM Dashboard accessible"

# Test n8n webhook (BIR deadline alert)
curl -X POST https://ipa.insightpulseai.com/webhook/bir-deadline-alert \
  -H "Content-Type: application/json" \
  -d '{"test": true}' && echo "✓ n8n webhook responsive"
```

**Step 12: Re-Enable Cron Jobs**
```bash
# Verify cron jobs active
docker exec -it odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT id, name, active, nextcall FROM ir_cron WHERE model LIKE 'ipai%';"

# All should show active=true
```

**Step 13: Disable Maintenance Mode**
```bash
# Via Odoo UI: Settings → General Settings → Maintenance Mode → OFF
# Or via CLI:
docker exec -it odoo-accounting odoo-bin shell -d odoo -c /etc/odoo/odoo.conf
>>> env['ir.config_parameter'].set_param('base.maintenance_mode', False)
```

**Step 14: Notify Users**
```bash
# Post to Mattermost
curl -X POST "$MATTERMOST_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"text": "✅ Odoo deployment complete. System is now live. Please report any issues to #finance-ssc channel."}'
```

---

### Hot-Fix Deployment (Urgent Production Fix)

**Use Case**: Critical bug fix requiring immediate deployment without full deployment cycle.

**Prerequisites**:
- Bug fix already committed to GitHub
- No database schema changes
- No new module dependencies

**Procedure**:
```bash
# 1. SSH to production
ssh root@159.223.75.148
cd /opt/odoo-ce

# 2. Pull latest code
git fetch origin
git pull origin main

# 3. Restart Odoo containers (no rebuild needed)
docker restart odoo-accounting odoo-core odoo-marketing

# 4. Monitor logs for errors
docker logs -f odoo-accounting | grep -E "(ERROR|CRITICAL)"

# 5. Verify fix applied
# (Test specific bug scenario)

# 6. Notify users via Mattermost
curl -X POST "$MATTERMOST_WEBHOOK_URL" \
  -d '{"text": "🔧 Hot-fix deployed: [description]. No downtime required."}'
```

**Rollback If Needed**:
```bash
# Revert to previous commit
git log --oneline -5  # Find previous good commit
git revert <bad_commit_sha>

# Restart containers
docker restart odoo-accounting odoo-core odoo-marketing
```

---

## Monitoring & Health Checks

### Automated Health Check (Enhanced Script)

**Location**: `/opt/odoo-ce/scripts/enhanced_health_check.sh`

**Checks Performed**:
1. **Odoo Process**: Verify `odoo-bin` process running
2. **Database Connection**: Test PostgreSQL connectivity
3. **Disk Space**: Alert if >90% usage
4. **Memory Usage**: Alert if >90% usage
5. **HTTP Endpoint**: Test `/web/health` endpoint
6. **Redis Cache**: Verify Redis connectivity
7. **Cron Jobs**: Ensure active cron jobs running

**Run Manually**:
```bash
ssh root@159.223.75.148
cd /opt/odoo-ce
./scripts/enhanced_health_check.sh
```

**Expected Output**:
```
2025-12-26 10:00:00 [INFO] ✓ Odoo process is running
2025-12-26 10:00:01 [INFO] ✓ Database connection is healthy
2025-12-26 10:00:02 [INFO] ✓ Disk usage: 45% (below 90% threshold)
2025-12-26 10:00:03 [INFO] ✓ Memory usage: 62% (below 90% threshold)
2025-12-26 10:00:04 [INFO] ✓ HTTP endpoint /web/health returns 200
2025-12-26 10:00:05 [INFO] ✓ Redis cache responsive
2025-12-26 10:00:06 [INFO] ✓ Cron jobs active: 8/8
```

**Configure Cron for Continuous Monitoring**:
```bash
# Add to /etc/crontab
*/5 * * * * root /opt/odoo-ce/scripts/enhanced_health_check.sh >> /var/log/odoo_health_check.log 2>&1
```

---

### n8n Workflow Monitoring

**Workflow**: `workflows/finance_ppm/performance_monitor.json`

**Monitoring Points**:
- **BIR Deadline Alert**: Runs daily at 8 AM, sends Mattermost notification for upcoming deadlines (7 days before filing)
- **Task Escalation**: Runs every 2 hours, alerts managers for overdue Finance PPM tasks
- **Monthly Report**: Runs on 1st of month, generates compliance summary and emails stakeholders

**Verify n8n Workflows Active**:
```bash
# Query n8n API
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  https://ipa.insightpulseai.com/api/v1/workflows | jq '.[] | {name, active}'

# Expected: 3 workflows with active=true
```

**Manual Trigger Test**:
```bash
# Trigger BIR deadline alert workflow
curl -X POST https://ipa.insightpulseai.com/webhook/bir-deadline-alert \
  -H "Content-Type: application/json" \
  -d '{"test": true, "form": "1601-C", "days_until_deadline": 7}'

# Check Mattermost for test notification
```

---

### Performance Metrics Collection

**Supabase Table**: `finance_ppm.performance_logs`

**Metrics Tracked**:
- HTTP response times (P50, P95, P99)
- Database query duration
- Task queue processing time
- OCR confidence scores
- Visual parity SSIM scores

**Query Performance Metrics**:
```sql
-- Last 24 hours average response time
SELECT
  AVG(response_time_ms) AS avg_response_time,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) AS p95_response_time,
  MAX(response_time_ms) AS max_response_time
FROM finance_ppm.performance_logs
WHERE timestamp > NOW() - INTERVAL '24 hours';

-- Expected: avg < 500ms, p95 < 2000ms, max < 5000ms
```

---

## Backup & Restore

### Full Database Backup

**Frequency**: Daily (automated via cron)
**Retention**: 30 days (rolling)

**Manual Backup Procedure**:
```bash
# SSH to production
ssh root@159.223.75.148

# Create backup directory
mkdir -p /opt/backups/odoo

# Backup database
docker exec odoo-db-1 pg_dump -U odoo odoo > /opt/backups/odoo/odoo_backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip /opt/backups/odoo/odoo_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup file
ls -lh /opt/backups/odoo/
# Expected: odoo_backup_YYYYMMDD_HHMMSS.sql.gz (size ~500MB for production data)
```

**Automated Backup (Cron)**:
```bash
# Add to /etc/crontab
0 2 * * * root /opt/odoo-ce/scripts/backup_database.sh >> /var/log/odoo_backup.log 2>&1
```

**Backup Script** (`scripts/backup_database.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/odoo"
RETENTION_DAYS=30

# Create backup
docker exec odoo-db-1 pg_dump -U odoo odoo | gzip > "$BACKUP_DIR/odoo_backup_$(date +%Y%m%d_%H%M%S).sql.gz"

# Remove backups older than retention period
find "$BACKUP_DIR" -name "odoo_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Log backup completion
echo "$(date) - Backup completed: $(ls -lh $BACKUP_DIR/odoo_backup_*.sql.gz | tail -1)"
```

---

### Incremental Backup (WAL Archiving)

**Use Case**: Point-in-time recovery (PITR) for critical production environments.

**Configuration** (`/etc/postgresql/postgresql.conf`):
```ini
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /opt/backups/wal_archive/%f && cp %p /opt/backups/wal_archive/%f'
```

**Restore to Point-in-Time**:
```bash
# Stop PostgreSQL
docker stop odoo-db-1

# Restore base backup
docker exec odoo-db-1 pg_restore -U odoo -d postgres /opt/backups/odoo/odoo_backup_YYYYMMDD.sql

# Restore WAL files (point-in-time)
# Edit recovery.conf:
restore_command = 'cp /opt/backups/wal_archive/%f %p'
recovery_target_time = '2025-12-26 10:00:00'

# Start PostgreSQL
docker start odoo-db-1
```

---

### Backup Verification

**Monthly Test**: Restore backup to staging environment and verify data integrity.

**Verification Procedure**:
```bash
# 1. Create staging database
docker exec odoo-db-1 createdb -U odoo odoo_staging

# 2. Restore latest backup
gunzip < /opt/backups/odoo/odoo_backup_latest.sql.gz | \
  docker exec -i odoo-db-1 psql -U odoo -d odoo_staging

# 3. Verify record counts match production
docker exec odoo-db-1 psql -U odoo -d odoo_staging -c \
  "SELECT COUNT(*) FROM account_move;"
# Compare with production count

# 4. Verify IPAI module data intact
docker exec odoo-db-1 psql -U odoo -d odoo_staging -c \
  "SELECT COUNT(*) FROM ipai_finance_bir_schedule;"
# Expected: 8+ BIR forms

# 5. Drop staging database
docker exec odoo-db-1 dropdb -U odoo odoo_staging
```

---

## Module Upgrade Procedures

### Minor Version Upgrade (18.0.1.0.0 → 18.0.1.1.0)

**Step 1: Backup Database**
```bash
docker exec odoo-db-1 pg_dump -U odoo odoo > /opt/backups/odoo/pre_upgrade_$(date +%Y%m%d).sql
```

**Step 2: Pull Latest Code**
```bash
cd /opt/odoo-ce
git pull origin main
```

**Step 3: Upgrade Module**
```bash
docker exec -it odoo-accounting odoo-bin \
  -d odoo \
  -u <module_name> \
  --stop-after-init \
  --logfile=/var/log/odoo/upgrade.log
```

**Step 4: Verify Upgrade**
```bash
# Check module version
docker exec -it odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, latest_version FROM ir_module_module WHERE name = '<module_name>';"

# Expected: latest_version = '18.0.1.1.0'
```

**Step 5: Restart Odoo**
```bash
docker restart odoo-accounting odoo-core odoo-marketing
```

---

### Major Version Upgrade (Odoo 17 → odoo 18)

**⚠️ CRITICAL**: Major version upgrades require comprehensive testing and migration scripts.

**Pre-Upgrade Preparation**:
1. ✅ Backup production database (`pg_dump`)
2. ✅ Create Odoo 18 staging environment
3. ✅ Test upgrade on staging first
4. ✅ Review [CHANGELOG.md](./CHANGELOG.md) for breaking changes
5. ✅ Update all OCA modules to Odoo 18 versions

**Migration Script** (JSONB name fields):
```sql
-- Migrate ir_ui_menu.name from char to jsonb
BEGIN;

ALTER TABLE ir_ui_menu RENAME COLUMN name TO name_old;
ALTER TABLE ir_ui_menu ADD COLUMN name jsonb;
UPDATE ir_ui_menu SET name = jsonb_build_object('en_US', name_old);
ALTER TABLE ir_ui_menu DROP COLUMN name_old;

COMMIT;
```

**Upgrade Procedure**:
```bash
# 1. Stop Odoo 17 containers
docker stop odoo-accounting odoo-core

# 2. Update docker-compose.yml to use Odoo 18 image
# Edit docker/docker-compose.enterprise-parity.yml:
#   image: odoo:18.0

# 3. Run database migration scripts
psql -U odoo -d odoo -f /opt/odoo-ce/migrations/17_to_18/01_jsonb_migration.sql

# 4. Start Odoo 18 containers
docker-compose -f docker/docker-compose.enterprise-parity.yml up -d

# 5. Upgrade all modules
docker exec -it odoo-accounting odoo-bin \
  -d odoo \
  --update=all \
  --stop-after-init

# 6. Verify all IPAI modules upgraded
docker exec -it odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE 'ipai_%';"
```

---

## Database Maintenance

### Vacuum & Analyze (Weekly)

**Purpose**: Reclaim disk space, update statistics for query optimizer.

**Procedure**:
```bash
# Manual vacuum analyze
docker exec -it odoo-db-1 psql -U odoo -d odoo -c "VACUUM ANALYZE;"

# Vacuum specific table
docker exec -it odoo-db-1 psql -U odoo -d odoo -c "VACUUM ANALYZE account_move;"

# Full vacuum (requires exclusive lock - run during maintenance window)
docker exec -it odoo-db-1 psql -U odoo -d odoo -c "VACUUM FULL;"
```

**Automated Vacuum** (Cron):
```bash
# Add to /etc/crontab
0 3 * * 0 root docker exec odoo-db-1 psql -U odoo -d odoo -c "VACUUM ANALYZE;" >> /var/log/pg_vacuum.log 2>&1
```

---

### Index Maintenance

**Check Missing Indexes**:
```sql
-- Identify slow queries needing indexes
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan AS index_scans,
  idx_tup_read AS tuples_read,
  idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY idx_tup_read DESC;
```

**Create Index for Finance PPM**:
```sql
-- Index on ipai_finance_bir_schedule for deadline queries
CREATE INDEX IF NOT EXISTS idx_bir_schedule_filing_deadline
ON ipai_finance_bir_schedule(filing_deadline)
WHERE state IN ('not_started', 'in_progress');

-- Index on project_task for Finance PPM queries
CREATE INDEX IF NOT EXISTS idx_project_task_finance_ppm
ON project_task(finance_logframe_id, bir_schedule_id)
WHERE is_finance_ppm = true;
```

---

### Connection Pool Management

**Check Active Connections**:
```sql
-- Current active connections
SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active';

-- Connections by application
SELECT application_name, COUNT(*)
FROM pg_stat_activity
GROUP BY application_name
ORDER BY count DESC;
```

**Kill Idle Connections** (if needed):
```sql
-- Kill connections idle > 1 hour
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < NOW() - INTERVAL '1 hour';
```

---

## Performance Optimization

### Odoo Configuration Tuning

**File**: `/etc/odoo/odoo.conf`

**Production Settings**:
```ini
[options]
# Database
db_host = localhost
db_port = 5432
db_user = odoo
db_password = <password>
db_name = odoo

# Workers (2 × CPU cores × 6 for SGP1 droplet with 4 vCPUs)
workers = 12
max_cron_threads = 2

# Memory limits
limit_memory_hard = 2684354560  # 2.5 GB
limit_memory_soft = 2147483648  # 2.0 GB

# Request limits
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

# Session store
session_store = redis
redis_host = redis
redis_port = 6379
redis_dbindex = 0

# Proxy mode (behind Nginx)
proxy_mode = True

# Logging
logfile = /var/log/odoo/odoo.log
log_level = info
```

---

### Database Query Optimization

**Slow Query Log**:
```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
SELECT pg_reload_conf();

-- View slow queries
SELECT
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

**Optimize Common Queries**:
```sql
-- Finance PPM dashboard query optimization
EXPLAIN ANALYZE
SELECT
  bir.filing_deadline,
  bir.status,
  COUNT(pt.id) AS task_count
FROM ipai_finance_bir_schedule bir
LEFT JOIN project_task pt ON pt.bir_schedule_id = bir.id
WHERE bir.filing_deadline >= CURRENT_DATE
GROUP BY bir.filing_deadline, bir.status
ORDER BY bir.filing_deadline;

-- Add covering index if needed
CREATE INDEX idx_bir_schedule_dashboard
ON ipai_finance_bir_schedule(filing_deadline, status)
INCLUDE (id);
```

---

### Redis Cache Tuning

**Redis Configuration**:
```bash
# docker-compose.yml redis command
redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

**Monitor Cache Hit Rate**:
```bash
# Redis CLI
docker exec -it odoo-redis redis-cli INFO stats | grep -E "(hits|misses)"

# Expected: > 90% hit rate
# keyspace_hits:150000
# keyspace_misses:5000
# Hit rate = 150000 / (150000 + 5000) = 96.8%
```

**Clear Cache** (if needed):
```bash
# Flush all Redis keys
docker exec -it odoo-redis redis-cli FLUSHALL

# Restart Odoo to rebuild cache
docker restart odoo-accounting odoo-core odoo-marketing
```

---

## Troubleshooting

### Issue 1: Odoo Container Won't Start

**Symptoms**: `docker ps` shows container exited immediately.

**Diagnosis**:
```bash
# Check container logs
docker logs odoo-accounting

# Common errors:
# - "Database 'odoo' does not exist" → Create database
# - "Connection refused (PostgreSQL)" → Check db container running
# - "Module 'xxx' not found" → Missing module in addons path
```

**Fix**:
```bash
# Create database if missing
docker exec -it odoo-db-1 createdb -U odoo odoo

# Verify PostgreSQL running
docker ps | grep odoo-db
docker logs odoo-db-1

# Check addons path
docker exec -it odoo-accounting ls /mnt/extra-addons/ipai
# Should list all IPAI modules
```

---

### Issue 2: Finance PPM Dashboard Returns 404

**Symptoms**: `/ipai/finance/ppm` returns 404 Not Found.

**Diagnosis**:
```bash
# Check if ipai_finance_ppm module installed
docker exec -it odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state FROM ir_module_module WHERE name = 'ipai_finance_ppm';"

# Expected: state='installed'
```

**Fix**:
```bash
# Install module if not installed
docker exec -it odoo-accounting odoo-bin \
  -d odoo \
  -i ipai_finance_ppm \
  --stop-after-init

# Restart Odoo
docker restart odoo-accounting
```

---

### Issue 3: BIR Cron Job Not Running

**Symptoms**: BIR deadline alerts not sent daily at 8 AM.

**Diagnosis**:
```sql
-- Check cron job exists and is active
SELECT id, name, active, nextcall, numbercall
FROM ir_cron
WHERE model = 'ipai.finance.bir_schedule';

-- Expected: active=true, nextcall within next 24 hours
```

**Fix**:
```sql
-- Activate cron job
UPDATE ir_cron SET active = true
WHERE model = 'ipai.finance.bir_schedule';

-- Manually trigger cron (for testing)
-- Via Odoo shell:
docker exec -it odoo-accounting odoo-bin shell -d odoo -c /etc/odoo/odoo.conf
>>> env['ir.cron'].search([('model', '=', 'ipai.finance.bir_schedule')]).method_direct_trigger()
```

---

## Incident Response

### Severity Levels

| Level | Definition | Response Time | Escalation |
|-------|------------|---------------|------------|
| **Critical** | System down, data loss risk, BIR deadline miss | <15 minutes | Finance Director |
| **High** | Degraded performance, multi-user impact | <1 hour | Finance Manager |
| **Medium** | Single-user impact, workaround available | <4 hours | Finance Supervisor |
| **Low** | Cosmetic issues, feature requests | Next sprint | Backlog |

---

### Incident Response Procedure

**Step 1: Triage (< 5 minutes)**
- Assess severity level
- Identify impacted users/workflows
- Determine if rollback needed

**Step 2: Containment (< 15 minutes)**
- Enable maintenance mode if needed
- Stop affected services
- Preserve logs and error messages

**Step 3: Diagnosis (< 30 minutes)**
- Review logs (`docker logs odoo-accounting`)
- Check database integrity
- Identify root cause

**Step 4: Resolution**
- Apply fix (code change, configuration, rollback)
- Test fix in staging first if possible
- Deploy to production

**Step 5: Verification (< 15 minutes)**
- Run health checks
- Test affected workflows
- Confirm users can access system

**Step 6: Communication**
- Notify users via Mattermost
- Update incident ticket
- Document root cause and fix

**Step 7: Post-Mortem (within 48 hours)**
- Root cause analysis
- Prevention measures
- Update runbook

---

## Disaster Recovery

### Scenario 1: Database Corruption

**Recovery Procedure**:
```bash
# 1. Stop Odoo containers
docker stop odoo-accounting odoo-core odoo-marketing

# 2. Assess corruption
docker exec -it odoo-db-1 psql -U odoo -d odoo -c "SELECT * FROM pg_database WHERE datname = 'odoo';"

# 3. Restore from backup
docker exec -it odoo-db-1 dropdb -U odoo odoo
docker exec -it odoo-db-1 createdb -U odoo odoo
gunzip < /opt/backups/odoo/odoo_backup_latest.sql.gz | \
  docker exec -i odoo-db-1 psql -U odoo -d odoo

# 4. Verify data integrity
docker exec -it odoo-db-1 psql -U odoo -d odoo -c "SELECT COUNT(*) FROM account_move;"

# 5. Start Odoo containers
docker start odoo-accounting odoo-core odoo-marketing

# 6. Notify users
curl -X POST "$MATTERMOST_WEBHOOK_URL" \
  -d '{"text": "🚨 Database restored from backup. Data loss: [X hours]. Please verify your recent work."}'
```

---

### Scenario 2: Complete Server Failure

**Recovery Procedure**:
1. ✅ Provision new DigitalOcean droplet (SGP1, 4GB RAM, 80GB disk)
2. ✅ Install Docker + Docker Compose
3. ✅ Clone `odoo-ce` repository
4. ✅ Restore database from latest backup
5. ✅ Deploy Docker Compose stack
6. ✅ Update DNS (`erp.insightpulseai.com` → new IP)
7. ✅ Run health checks
8. ✅ Notify users

**Recovery Time Objective (RTO)**: < 4 hours
**Recovery Point Objective (RPO)**: < 24 hours (daily backups)

---

## Operational Checklists

### Daily Operations

- [ ] Review health check logs (`/var/log/odoo_health_check.log`)
- [ ] Check for cron job failures (Settings → Scheduled Actions)
- [ ] Monitor disk space usage (`df -h`)
- [ ] Review Odoo logs for errors (`docker logs odoo-accounting | grep ERROR`)
- [ ] Verify n8n workflows executed successfully

### Weekly Operations

- [ ] Database vacuum analyze (`VACUUM ANALYZE`)
- [ ] Review slow queries (`pg_stat_statements`)
- [ ] Check backup integrity (restore to staging)
- [ ] Update module documentation if changes deployed
- [ ] Review security audit logs

### Monthly Operations

- [ ] Full database backup rotation (delete backups > 30 days)
- [ ] Performance optimization review (query plans, indexes)
- [ ] Security patch review (Odoo, PostgreSQL, dependencies)
- [ ] Disaster recovery test (restore from backup)
- [ ] User access review (add/remove users as needed)

---

## Next Steps

1. **Review [CHANGELOG.md](./CHANGELOG.md)** for version history and migration notes
2. **Implement Automated Backups**: Setup cron for daily database backups
3. **Configure Monitoring Alerts**: Setup Mattermost notifications for critical errors
4. **Test Disaster Recovery**: Quarterly DR drills to validate procedures
5. **Document Custom Procedures**: Add organization-specific runbook sections

---

## Support

For operational issues:
1. Check [GitHub Issues](https://github.com/jgtolentino/odoo-ce/issues?q=label%3Aoperations)
2. Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) (per-module)
3. Contact: Jake Tolentino (Finance SSC Manager / Odoo Developer)
