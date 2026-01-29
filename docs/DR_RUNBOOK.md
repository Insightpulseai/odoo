# Disaster Recovery Runbook

**Version:** 1.0.0
**Last Updated:** 2026-01-29
**Odoo.sh Parity:** GAP 3 - Multi-DC Backups

---

## 1. Overview

This runbook provides step-by-step procedures for disaster recovery of the Odoo CE self-hosted environment. It implements multi-datacenter backup strategies equivalent to Odoo.sh.

### 1.1 Recovery Objectives

| Metric | Target | Odoo.sh Equivalent |
|--------|--------|-------------------|
| **RTO** (Recovery Time Objective) | < 4 hours | ~4 hours |
| **RPO** (Recovery Point Objective) | < 24 hours | Daily backups |
| **Backup Regions** | 3 datacenters | 3 continents |

### 1.2 Backup Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Multi-DC Backup Architecture                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│   │   SGP1      │    │   NYC3      │    │   AMS3      │             │
│   │  (Primary)  │    │ (Secondary) │    │ (Tertiary)  │             │
│   │  Singapore  │    │  New York   │    │  Amsterdam  │             │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘             │
│          │                  │                  │                     │
│          ▼                  ▼                  ▼                     │
│   ┌─────────────────────────────────────────────────────┐           │
│   │              S3/Spaces Cross-Region Replication      │           │
│   │                                                      │           │
│   │  • Daily database backups (pg_dump)                 │           │
│   │  • Daily filestore snapshots                         │           │
│   │  • Weekly full backups                               │           │
│   │  • Monthly archive backups                           │           │
│   └─────────────────────────────────────────────────────┘           │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backup Schedule

### 2.1 Automated Backups

| Type | Frequency | Retention | Regions |
|------|-----------|-----------|---------|
| Daily | Every 24h at 02:00 UTC | 30 days | All 3 |
| Weekly | Sunday 03:00 UTC | 12 weeks | All 3 |
| Monthly | 1st of month | 6 months | All 3 |
| Pre-deploy | Before each production deploy | 7 days | Primary |

### 2.2 Cron Configuration

```bash
# /etc/cron.d/odoo-backup

# Daily backup at 02:00 UTC
0 2 * * * root /opt/odoo-ce/scripts/backup/full_backup.sh >> /var/log/odoo-backup.log 2>&1

# Weekly backup on Sunday at 03:00 UTC
0 3 * * 0 root /opt/odoo-ce/scripts/backup/full_backup.sh --retain 84 >> /var/log/odoo-backup.log 2>&1

# Monthly backup on 1st at 04:00 UTC
0 4 1 * * root /opt/odoo-ce/scripts/backup/full_backup.sh --retain 180 >> /var/log/odoo-backup.log 2>&1

# Restore test every Sunday at 05:00 UTC
0 5 * * 0 root /opt/odoo-ce/scripts/backup/restore_test.sh --latest >> /var/log/odoo-restore-test.log 2>&1
```

---

## 3. Disaster Scenarios

### 3.1 Scenario Classification

| Severity | Description | RTO | Runbook Section |
|----------|-------------|-----|-----------------|
| **P1** | Complete data loss | < 4h | 4.1 |
| **P2** | Database corruption | < 2h | 4.2 |
| **P3** | Partial data loss | < 1h | 4.3 |
| **P4** | Configuration loss | < 30m | 4.4 |

---

## 4. Recovery Procedures

### 4.1 Complete Data Loss (P1)

**Trigger:** Primary datacenter failure, ransomware, catastrophic hardware failure

**Prerequisites:**
- Access to secondary region S3/Spaces
- Clean server or container environment
- Database credentials

**Procedure:**

```bash
# Step 1: Identify latest backup from secondary region
export AWS_DEFAULT_REGION=nyc3
aws s3 ls s3://odoo-backups-secondary/ --recursive | sort -k1,2 | tail -5

# Step 2: Download latest backup
LATEST_BACKUP=$(aws s3 ls s3://odoo-backups-secondary/ --recursive | \
    grep "\.sql\.gz$" | sort -k1,2 | tail -1 | awk '{print $4}')
aws s3 cp "s3://odoo-backups-secondary/$LATEST_BACKUP" /tmp/restore/

# Step 3: Create fresh database
sudo -u postgres createdb odoo_core

# Step 4: Restore database
gunzip -c "/tmp/restore/$(basename $LATEST_BACKUP)" | \
    sudo -u postgres psql odoo_core

# Step 5: Download and restore filestore
LATEST_FILES=$(aws s3 ls s3://odoo-backups-secondary/ --recursive | \
    grep "filestore.*\.tar\.gz$" | sort -k1,2 | tail -1 | awk '{print $4}')
aws s3 cp "s3://odoo-backups-secondary/$LATEST_FILES" /tmp/restore/
tar -xzf "/tmp/restore/$(basename $LATEST_FILES)" -C /var/lib/odoo/

# Step 6: Fix permissions
chown -R odoo:odoo /var/lib/odoo/filestore

# Step 7: Start Odoo
systemctl start odoo
# or
docker compose up -d odoo

# Step 8: Verify recovery
curl -s http://localhost:8069/web/health
```

**Verification Checklist:**
- [ ] Database accessible via psql
- [ ] Odoo health endpoint returns 200
- [ ] Users can log in
- [ ] Critical data (invoices, partners) present
- [ ] Filestore attachments accessible

**Estimated Time:** 2-4 hours

---

### 4.2 Database Corruption (P2)

**Trigger:** Failed migration, disk corruption, incomplete transaction

**Procedure:**

```bash
# Step 1: Stop Odoo immediately
systemctl stop odoo
# or
docker compose stop odoo

# Step 2: Identify corruption
sudo -u postgres psql odoo_core -c "SELECT * FROM pg_stat_activity;"

# Step 3: Attempt repair (if possible)
sudo -u postgres psql odoo_core -c "VACUUM FULL;"
sudo -u postgres psql odoo_core -c "REINDEX DATABASE odoo_core;"

# Step 4: If repair fails, restore from backup
./scripts/backup/restore_test.sh --latest --db-name odoo_core_new

# Step 5: Swap databases
sudo -u postgres psql -c "ALTER DATABASE odoo_core RENAME TO odoo_core_corrupted;"
sudo -u postgres psql -c "ALTER DATABASE odoo_core_new RENAME TO odoo_core;"

# Step 6: Restart Odoo
systemctl start odoo
```

**Estimated Time:** 1-2 hours

---

### 4.3 Partial Data Loss (P3)

**Trigger:** Accidental deletion, user error, bad data import

**Procedure:**

```bash
# Step 1: Identify affected tables/records
# Check audit logs or user reports

# Step 2: Create point-in-time backup of current state
./scripts/backup/full_backup.sh --db-only

# Step 3: Restore specific tables from backup to temp database
gunzip -c /var/backups/odoo/db/odoo_*.sql.gz | \
    sudo -u postgres psql odoo_core_restore

# Step 4: Extract and reimport specific data
sudo -u postgres psql odoo_core_restore -c \
    "COPY res_partner TO '/tmp/partners_backup.csv' CSV HEADER;"

sudo -u postgres psql odoo_core -c \
    "COPY res_partner FROM '/tmp/partners_backup.csv' CSV HEADER;"

# Step 5: Update sequences
sudo -u postgres psql odoo_core -c \
    "SELECT setval('res_partner_id_seq', (SELECT MAX(id) FROM res_partner));"
```

**Estimated Time:** 30-60 minutes

---

### 4.4 Configuration Loss (P4)

**Trigger:** Lost secrets, configuration files, environment variables

**Procedure:**

```bash
# Step 1: Restore configuration from git
cd /opt/odoo-ce
git checkout -- .

# Step 2: Restore secrets from backup
# Secrets should be in a separate secure location
cp /backup/secrets/.env.prod /opt/odoo-ce/.env.prod

# Step 3: Restore from Supabase Vault (if available)
supabase secrets list --project-ref $SUPABASE_PROJECT_REF

# Step 4: Regenerate if necessary
# DB_PASSWORD - generate new, update database and config
# API_KEYS - regenerate from provider dashboards
# SSL_CERTS - regenerate via Caddy/Let's Encrypt

# Step 5: Restart services
docker compose restart
```

**Estimated Time:** 15-30 minutes

---

## 5. Monitoring & Alerts

### 5.1 Backup Monitoring

```yaml
# n8n workflow: backup_monitor.json
triggers:
  - schedule: "0 6 * * *"  # Daily at 06:00 UTC

checks:
  - name: "Daily backup exists"
    query: |
      SELECT COUNT(*) FROM backup_manifests
      WHERE created_at > NOW() - INTERVAL '26 hours'
    threshold: ">= 1"

  - name: "Backup size reasonable"
    query: |
      SELECT size_bytes FROM backup_manifests
      ORDER BY created_at DESC LIMIT 1
    threshold: "> 1000000"  # > 1MB

  - name: "Restore test passed"
    query: |
      SELECT status FROM restore_test_results
      ORDER BY created_at DESC LIMIT 1
    expected: "PASS"

alerts:
  - channel: "#ops-alerts"
  - email: "ops@insightpulseai.com"
```

### 5.2 Health Check Endpoints

```bash
# Backup health check
curl -s http://localhost:8069/backup/health | jq .

# Expected response:
{
  "status": "healthy",
  "last_backup": "2026-01-29T02:00:00Z",
  "backup_age_hours": 4,
  "regions_synced": 3,
  "restore_test_passed": true
}
```

---

## 6. Contact & Escalation

### 6.1 Escalation Matrix

| Level | Contact | Response Time | Authority |
|-------|---------|---------------|-----------|
| L1 | On-call Engineer | < 15 min | Restart services |
| L2 | Senior DevOps | < 30 min | Database restore |
| L3 | CTO | < 1 hour | Full DR execution |

### 6.2 External Contacts

| Service | Contact | Purpose |
|---------|---------|---------|
| DigitalOcean Support | support@digitalocean.com | Infrastructure |
| Supabase Support | support@supabase.io | External DB |

---

## 7. Post-Incident

### 7.1 Recovery Verification Checklist

- [ ] All services running (`docker compose ps`)
- [ ] Database connections working (`psql -c "SELECT 1"`)
- [ ] Odoo health check passing (`curl /web/health`)
- [ ] User logins working
- [ ] Critical modules installed
- [ ] Filestore accessible
- [ ] Email sending working
- [ ] n8n workflows active
- [ ] Backups resuming

### 7.2 Post-Incident Report Template

```markdown
# Incident Report: [DATE] - [TITLE]

## Summary
- **Duration:** X hours
- **Impact:** [Users/Services affected]
- **Severity:** P1/P2/P3/P4

## Timeline
- HH:MM - Incident detected
- HH:MM - Response initiated
- HH:MM - Root cause identified
- HH:MM - Recovery started
- HH:MM - Service restored
- HH:MM - Incident closed

## Root Cause
[Description]

## Resolution
[Steps taken]

## Prevention
[Action items to prevent recurrence]
```

---

## 8. Appendix

### 8.1 Backup Script Reference

```bash
# Full backup to all regions
./scripts/backup/full_backup.sh

# Database only
./scripts/backup/full_backup.sh --db-only

# To specific region
./scripts/backup/full_backup.sh --region nyc3

# Dry run
./scripts/backup/full_backup.sh --dry-run --verbose
```

### 8.2 Restore Script Reference

```bash
# Test latest backup
./scripts/backup/restore_test.sh --latest

# Test specific backup
./scripts/backup/restore_test.sh --backup /path/to/backup.sql.gz

# Restore to specific database
./scripts/backup/restore_test.sh --latest --db-name odoo_restored
```

### 8.3 S3/Spaces Configuration

```bash
# Environment variables required
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export S3_PRIMARY_BUCKET=odoo-backups-primary
export S3_SECONDARY_BUCKET=odoo-backups-secondary
export S3_TERTIARY_BUCKET=odoo-backups-tertiary
export PRIMARY_REGION=sgp1
export SECONDARY_REGION=nyc3
export TERTIARY_REGION=ams3
```

---

**Document Control:**
- Created: 2026-01-29
- Reviewed: [Pending]
- Approved: [Pending]
- Next Review: 2026-04-29
