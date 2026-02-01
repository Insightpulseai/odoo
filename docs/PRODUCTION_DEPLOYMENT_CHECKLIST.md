# Production Deployment Checklist

**Status**: Ready for execution
**Target**: DigitalOcean Singapore (SGP1)
**Stack**: Odoo 18 CE + PostgreSQL 16 + Nginx + Let's Encrypt
**Est. Time**: 30-45 minutes (mostly automated)

---

## Pre-Flight Checklist

### ✅ DigitalOcean Resources Created

- [ ] **Droplet**: s-4vcpu-8gb Ubuntu 24.04 LTS (Singapore)
  - [ ] SSH key added
  - [ ] Hostname: `odoo-prod-01`
  - [ ] VPC: `fin-vpc` (or default)
  - [ ] Tags: `odoo`, `production`
  - [ ] IP Address: `_______________` (note here after creation)

- [ ] **Managed PostgreSQL** (Optional but Recommended)
  - [ ] Version: PostgreSQL 16
  - [ ] Size: db-s-1vcpu-1gb ($15/mo)
  - [ ] Region: Singapore
  - [ ] Database: `odoo_prod`
  - [ ] User: `odoo`
  - [ ] Password: `_______________` (save securely)
  - [ ] Connection Pool: Enabled
  - [ ] Connection String: `_______________`

- [ ] **Spaces Bucket** (Backups)
  - [ ] Name: `insightpulse-backups`
  - [ ] Region: Singapore
  - [ ] Access Key: `_______________`
  - [ ] Secret Key: `_______________`

### ✅ DNS Configuration

- [ ] **A Record**: `erp.insightpulseai.com` → Droplet IP
  - [ ] TTL: 300 seconds (5 minutes)
  - [ ] Propagation verified: `dig erp.insightpulseai.com +short`

### ✅ Local Machine Prerequisites

- [ ] SSH access to droplet verified:
  ```bash
  ssh root@<DROPLET_IP>
  ```
- [ ] DigitalOcean CLI installed (optional):
  ```bash
  doctl version
  ```

---

## Deployment Execution

### Option 1: One-Line Remote Execution (Recommended)

From your local machine:

```bash
# 1. SSH into fresh droplet
ssh root@<DROPLET_IP>

# 2. Set environment variables (if using Managed DB)
export DOMAIN="erp.insightpulseai.com"
export EMAIL="admin@insightpulseai.com"
export DB_HOST="your-db.db.ondigitalocean.com"
export DB_PORT="25060"
export DB_USER="odoo"
export DB_PASSWORD="your-secure-password"
export DB_NAME="odoo_prod"
export S3_BUCKET="insightpulse-backups"

# 3. Download and execute bootstrap script
curl -fsSL https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/scripts/deploy/do-bootstrap-odoo-prod.sh | bash
```

### Option 2: Local Execution with Custom Config

```bash
# 1. Clone repository on droplet
git clone https://github.com/jgtolentino/odoo-ce.git /tmp/odoo-ce
cd /tmp/odoo-ce

# 2. Configure deployment
export DOMAIN="erp.insightpulseai.com"
export EMAIL="admin@insightpulseai.com"
export DB_HOST="localhost"  # Use local PostgreSQL
export WORKERS="7"          # (4 CPU × 2) + 1 - 2 cron
export GIT_REF="main"       # Or specific tag/branch

# 3. Run bootstrap
bash scripts/deploy/do-bootstrap-odoo-prod.sh
```

**Estimated Duration**: 25-35 minutes (depends on package downloads)

---

## Post-Deployment Verification

### 1. Service Health Checks

```bash
# Check Odoo service status
systemctl status odoo

# Check Nginx status
systemctl status nginx

# Check recent logs
journalctl -u odoo -n 50 --no-pager

# Check Odoo application logs
tail -f /var/log/odoo/odoo.log
```

**Expected Output**:
```
● odoo.service - Odoo 18 CE
   Active: active (running)

● nginx.service - A high performance web server
   Active: active (running)
```

### 2. HTTP Endpoint Tests

```bash
# Test local Odoo endpoint
curl -I http://localhost:8069/web/health

# Test Nginx reverse proxy (if SSL configured)
curl -I https://erp.insightpulseai.com

# Test websocket endpoint
curl -I http://localhost:8072/websocket
```

**Expected Output**:
- Status: `200 OK` or `302 Found` (redirect to login)
- Headers: `Server: nginx`, `X-Frame-Options: SAMEORIGIN`

### 3. Database Connectivity

```bash
# For local PostgreSQL
sudo -u postgres psql -d odoo_prod -c "SELECT count(*) FROM ir_module_module;"

# For Managed PostgreSQL
PGPASSWORD="your-password" psql \
  -h your-db.db.ondigitalocean.com \
  -p 25060 \
  -U odoo \
  -d odoo_prod \
  -c "SELECT version();"
```

**Expected Output**: PostgreSQL version 16.x

### 4. SSL Certificate Verification

```bash
# Check certificate details
certbot certificates

# Test SSL configuration
curl -vI https://erp.insightpulseai.com 2>&1 | grep -i "ssl"
```

**Expected Output**:
```
Certificate Name: erp.insightpulseai.com
  Valid: Yes
  Expiry Date: [90 days from now]
```

### 5. Firewall Configuration

```bash
# Check UFW status
ufw status numbered

# Verify open ports
netstat -tuln | grep LISTEN
```

**Expected Output**:
```
22/tcp    ALLOW       Anywhere
80/tcp    ALLOW       Anywhere
443/tcp   ALLOW       Anywhere
```

### 6. Backup Configuration

```bash
# Check cron job
cat /etc/cron.d/odoo-backup

# Test backup script manually
sudo -u odoo /opt/odoo/scripts/backup.sh

# Verify backup files created
ls -lh /var/lib/odoo/backups/
```

**Expected Output**:
```
-rw-r--r-- 1 odoo odoo 15M Jan  8 14:30 odoo_prod_20260108_143000.dump.gz
-rw-r--r-- 1 odoo odoo 5M  Jan  8 14:30 filestore_20260108_143000.tar.gz
```

---

## Web UI Verification

### 1. Access Odoo

Open browser: `https://erp.insightpulseai.com`

**Expected**: Odoo database creation screen or login page

### 2. Create Database (First-Time Only)

If using local PostgreSQL:

1. Click **"Create Database"**
2. Fill in form:
   - **Database Name**: `odoo_prod`
   - **Email**: `admin@insightpulseai.com`
   - **Password**: (use Admin Password from `/root/odoo-credentials.txt`)
   - **Language**: English
   - **Country**: Philippines
   - **Demo Data**: Unchecked
3. Click **"Create Database"**

**Expected**: Database initialization takes 2-5 minutes, then redirects to app selection

### 3. Install IPAI Modules

From Apps menu:

1. Search: `ipai_health`
2. Click **Install**
3. Search: `ipai_workspace_core`
4. Click **Install**

**Expected**: Modules install successfully with dependencies

### 4. Verify Health Endpoint

```bash
curl https://erp.insightpulseai.com/web/health
```

**Expected Output**:
```json
{"status": "pass"}
```

---

## Security Hardening (Post-Deployment)

### 1. Save Credentials Securely

```bash
# View generated credentials
cat /root/odoo-credentials.txt

# Copy to password manager, then delete
rm /root/odoo-credentials.txt
```

### 2. Configure S3/Spaces for Backups

```bash
# Configure s3cmd (interactive)
s3cmd --configure

# Test upload
echo "test" > /tmp/test.txt
s3cmd put /tmp/test.txt s3://insightpulse-backups/test.txt
s3cmd ls s3://insightpulse-backups/
```

### 3. SSH Hardening (Optional)

```bash
# Disable password authentication
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd
```

### 4. Setup Monitoring Alerts (Recommended)

- [ ] Configure DigitalOcean monitoring alerts:
  - CPU usage >80% for 5 minutes
  - Memory usage >90% for 5 minutes
  - Disk usage >85%
- [ ] Configure Odoo health check monitoring (external service)

---

## Rollback Procedure (If Needed)

### Quick Rollback

```bash
# Stop services
systemctl stop odoo nginx

# Restore database from backup
PGPASSWORD="password" pg_restore \
  -h localhost -p 5432 -U odoo -d odoo_prod \
  /var/lib/odoo/backups/odoo_prod_YYYYMMDD_HHMMSS.dump

# Restore filestore
cd /var/lib/odoo/filestore/odoo_prod
tar -xzf /var/lib/odoo/backups/filestore_YYYYMMDD_HHMMSS.tar.gz

# Restart services
systemctl start odoo nginx
```

---

## Troubleshooting

### Issue: Odoo service fails to start

**Check logs**:
```bash
journalctl -u odoo -n 100 --no-pager
tail -f /var/log/odoo/odoo.log
```

**Common causes**:
- Database connection failure → Check DB credentials in `/etc/odoo/odoo.conf`
- Port already in use → `netstat -tuln | grep 8069`
- Permission issues → `chown -R odoo:odoo /var/lib/odoo`

### Issue: SSL certificate fails

**Check DNS propagation**:
```bash
dig erp.insightpulseai.com +short
```

**Manual certbot retry**:
```bash
certbot --nginx -d erp.insightpulseai.com
```

### Issue: Database connection refused

**For Managed DB**:
```bash
# Verify VPC connectivity
ping -c 3 your-db.db.ondigitalocean.com

# Check firewall rules
ufw status numbered
```

### Issue: Nginx 502 Bad Gateway

**Check Odoo backend**:
```bash
curl -I http://localhost:8069
systemctl status odoo
```

---

## Success Criteria ✅

All of the following must be true:

- [ ] Odoo service: `active (running)`
- [ ] Nginx service: `active (running)`
- [ ] PostgreSQL: Connection successful
- [ ] SSL certificate: Valid (if DNS configured)
- [ ] Health endpoint: Returns `{"status": "pass"}`
- [ ] Backup script: Executes successfully
- [ ] Web UI: Accessible via HTTPS
- [ ] Database created: `odoo_prod` exists
- [ ] IPAI modules: `ipai_health`, `ipai_workspace_core` installed

---

## Cost Summary (Monthly)

| Component | Service | Size | Cost |
|-----------|---------|------|------|
| Compute | DO Droplet | s-4vcpu-8gb | $48 |
| Database | Managed PostgreSQL | db-s-1vcpu-1gb | $15 |
| Storage | Spaces (Backups) | 100GB | $5 |
| Bandwidth | Included | 4TB | $0 |
| **Total** | | | **$68/mo** |

**vs. Odoo.com**: $240/mo (72% savings)

---

## Next Steps After Deployment

1. **Configure Email SMTP** (for notifications)
   - Update `/etc/odoo/odoo.conf`:
     ```ini
     smtp_server = smtp.sendgrid.net
     smtp_port = 587
     smtp_user = apikey
     smtp_password = YOUR_SENDGRID_API_KEY
     ```

2. **Setup n8n Integration** (workflows)
   - Install n8n on same droplet or separate container
   - Configure Odoo XML-RPC credentials in n8n

3. **Install Additional OCA Modules**
   - See `addons/oca/` directory
   - Example: `account_financial_report`, `project_timeline`

4. **Configure Multi-Database** (optional)
   - Enable `list_db = True` in `/etc/odoo/odoo.conf`
   - Create additional databases for staging/testing

5. **Setup Ops Control Room** (if M0 complete)
   - See `spec/ops-control-room/DEPLOYMENT_INTEGRATION.md`
   - Deploy Ops workers to DigitalOcean App Platform

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-08
**Maintainer**: Jake Tolentino
**Support**: https://github.com/jgtolentino/odoo-ce/issues
