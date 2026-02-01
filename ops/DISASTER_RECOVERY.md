# Disaster Recovery Procedures

> **InsightPulse ERP - Production Recovery Guide**
> Last updated: 2024

## Overview

This document provides step-by-step procedures for recovering InsightPulse ERP from various failure scenarios.

## Quick Reference

| Scenario | RTO | RPO | Procedure |
|----------|-----|-----|-----------|
| Database corruption | 1 hour | 24 hours | [Restore from backup](#database-restore) |
| Service outage | 15 min | 0 | [Service restart](#service-restart) |
| Complete server failure | 4 hours | 24 hours | [Full restoration](#full-server-restoration) |
| Security breach | 2 hours | varies | [Security incident](#security-incident) |

## Prerequisites

- SSH access to production server
- Access to backup storage (local or S3)
- Docker and Docker Compose installed
- PostgreSQL client tools

## Recovery Procedures

### Service Restart

**Symptoms:** Odoo not responding, containers stopped

```bash
# SSH into server
ssh root@erp.insightpulseai.com

# Check container status
cd /opt/odoo-ce
docker compose ps

# View recent logs
docker compose logs --tail=100 odoo

# Restart all services
docker compose restart

# If restart fails, recreate containers
docker compose down
docker compose up -d

# Verify health
curl http://localhost:8069/web/health
```

### Database Restore

**Symptoms:** Data corruption, accidental deletion, failed migration

#### Step 1: Download Backup

```bash
# From S3 (if configured)
aws s3 cp s3://odoo-backups-prod/2024/01/odoo_db_20240101_020000.sql.gz /tmp/

# Or from local backup
cp /backups/odoo/odoo_db_20240101_020000.sql.gz /tmp/
```

#### Step 2: Stop Odoo

```bash
cd /opt/odoo-ce
docker compose stop odoo
```

#### Step 3: Restore Database

```bash
# Drop existing database (WARNING: This deletes all current data!)
docker compose exec db psql -U odoo -c "DROP DATABASE IF EXISTS odoo_restore;"
docker compose exec db psql -U odoo -c "CREATE DATABASE odoo_restore;"

# Restore from backup
gunzip < /tmp/odoo_db_20240101_020000.sql.gz | \
    docker compose exec -T db psql -U odoo -d odoo_restore

# Verify restore
docker compose exec db psql -U odoo -d odoo_restore -c "SELECT count(*) FROM res_users;"
```

#### Step 4: Switch Databases

```bash
# Rename databases
docker compose exec db psql -U odoo -c "ALTER DATABASE odoo RENAME TO odoo_corrupted;"
docker compose exec db psql -U odoo -c "ALTER DATABASE odoo_restore RENAME TO odoo;"
```

#### Step 5: Restart Odoo

```bash
docker compose up -d odoo

# Wait for startup
sleep 30

# Verify
curl http://localhost:8069/web/health
```

#### Step 6: Verify Data

```bash
# Check logs for errors
docker compose logs --tail=50 odoo | grep -i error

# Test login
curl -s https://erp.insightpulseai.com/web/login | grep -q "Login"
```

### Filestore Restore

**Symptoms:** Missing attachments, broken document links

```bash
# Stop Odoo
docker compose stop odoo

# Backup current filestore
mv /opt/odoo-ce/.local/share/Odoo/filestore /opt/odoo-ce/.local/share/Odoo/filestore.bak

# Restore from backup
tar -xzf /tmp/odoo_filestore_20240101_020000.tar.gz \
    -C /opt/odoo-ce/.local/share/Odoo/

# Start Odoo
docker compose up -d odoo
```

### Full Server Restoration

**Symptoms:** Server completely unresponsive, hardware failure

#### Step 1: Provision New Server

```bash
# Create new droplet/VM with:
# - Ubuntu 22.04 LTS
# - 4 GB RAM minimum
# - 50 GB SSD
# - Docker installed
```

#### Step 2: Install Docker

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
apt-get install -y docker-compose-plugin
```

#### Step 3: Clone Repository

```bash
cd /opt
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce
git checkout main
```

#### Step 4: Configure Environment

```bash
# Copy environment template
cp deploy/.env.production.template deploy/.env

# Edit with production values
nano deploy/.env
# Set:
# - DB_PASSWORD
# - ADMIN_PASSWORD
# - Other secrets
```

#### Step 5: Restore Data

```bash
# Download backups from S3
aws s3 cp s3://odoo-backups-prod/latest/ /tmp/backups/ --recursive

# Start database only
docker compose up -d db
sleep 10

# Restore database
gunzip < /tmp/backups/odoo_db_*.sql.gz | \
    docker compose exec -T db psql -U odoo -d odoo

# Restore filestore
tar -xzf /tmp/backups/odoo_filestore_*.tar.gz \
    -C /opt/odoo-ce/.local/share/Odoo/
```

#### Step 6: Start Services

```bash
docker compose up -d

# Verify
docker compose ps
curl http://localhost:8069/web/health
```

#### Step 7: Update DNS

```bash
# Point erp.insightpulseai.com to new server IP
# Wait for DNS propagation (up to 48 hours, usually faster)
```

#### Step 8: Setup SSL

```bash
# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d erp.insightpulseai.com
```

### Security Incident

**Symptoms:** Unauthorized access, compromised credentials, suspicious activity

#### Immediate Actions (First 15 minutes)

```bash
# 1. Stop all containers immediately
docker compose down

# 2. Take snapshot of current state
tar -czf /tmp/incident_snapshot_$(date +%Y%m%d_%H%M%S).tar.gz \
    /opt/odoo-ce \
    /var/log/nginx \
    /var/log/auth.log

# 3. Block incoming traffic (except your IP)
ufw default deny incoming
ufw allow from YOUR_IP

# 4. Rotate all credentials
# Generate new passwords for:
# - Database
# - Admin user
# - API keys
# - SSH keys
```

#### Investigation

```bash
# Check access logs
grep -i "login\|auth" /var/log/nginx/access.log | tail -100

# Check audit logs in database
docker compose up -d db
docker compose exec db psql -U odoo -d odoo -c \
    "SELECT * FROM ir_logging ORDER BY create_date DESC LIMIT 100;"

# Check for unauthorized users
docker compose exec db psql -U odoo -d odoo -c \
    "SELECT id, login, create_date FROM res_users WHERE active = true;"
```

#### Recovery

```bash
# 1. Restore from known-good backup
# Follow database restore procedure above

# 2. Update all secrets
# Generate new passwords for all services

# 3. Revoke suspicious sessions
docker compose exec db psql -U odoo -d odoo -c \
    "DELETE FROM ir_sessions;"

# 4. Re-enable services with new configuration
docker compose up -d

# 5. Enable additional security measures
# - 2FA for all admin users
# - IP whitelist for admin access
# - Enhanced logging
```

## Verification Checklist

After any recovery:

- [ ] Odoo web interface loads
- [ ] Login works for test user
- [ ] Database shows expected record counts
- [ ] File attachments display correctly
- [ ] Email/notifications functioning
- [ ] Scheduled actions running
- [ ] No errors in logs

## Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| DevOps Lead | [Contact Info] | 24/7 |
| Database Admin | [Contact Info] | Business hours |
| Security Team | [Contact Info] | 24/7 |

## Backup Verification Schedule

| Day | Action |
|-----|--------|
| Daily | Automated backup runs at 2 AM |
| Weekly | Manual backup verification |
| Monthly | Test restore procedure |
| Quarterly | Full DR drill |

---

*This document should be reviewed and updated quarterly.*
