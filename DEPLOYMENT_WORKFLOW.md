# Odoo CE v0.9.1 - Production Deployment Workflow

**Date**: 2025-11-25
**Target**: erp.insightpulseai.com (159.223.75.148)
**Status**: ✅ Ready for Deployment

---

## Pre-Deployment Checklist

### ☐ Phase 0: Review & Planning (1 hour)

**Documents to Review:**
- [x] Read: `EXECUTIVE_SUMMARY.md` (key findings)
- [x] Review: `ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md` (full audit)
- [x] Understand: `v0.9.1_DEPLOYMENT_GUIDE.md` (step-by-step)
- [x] Check: `CHANGELOG.md` (what changed)

**Team Alignment:**
- [ ] Notify Finance Director CKVC (Khalil Veracruz) of deployment window
- [ ] Schedule maintenance window (recommend: off-hours, 2-4 AM SGT)
- [ ] Prepare rollback plan with team

**Access Verification:**
- [ ] SSH access to VPS: `ssh root@159.223.75.148`
- [ ] GitHub Container Registry access (GHCR_PAT set)
- [ ] DigitalOcean admin access (for VPS resize)
- [ ] Domain access (verify DNS propagation)

---

## Phase 1: Infrastructure Preparation (1-2 hours)

### ☐ Step 1.1: VPS Upgrade

**Current State:**
- Droplet: odoo-erp-prod (4GB RAM, 80GB Disk)
- Services: Odoo + Auth + n8n (resource contention)

**Upgrade Required:**
```bash
# Option A: Via DigitalOcean Console
# 1. Go to: https://cloud.digitalocean.com/droplets
# 2. Select: odoo-erp-prod
# 3. Resize: 8GB RAM / 4vCPU ($48/month)
# 4. Wait: 5-10 minutes

# Option B: Via CLI
doctl auth init
doctl compute droplet resize odoo-erp-prod --size s-4vcpu-8gb --wait
doctl compute droplet get odoo-erp-prod --format Name,Memory
```

**Verification:**
```bash
ssh root@159.223.75.148
free -h
# Expected: Total memory ~8GB
```

**Cost Impact:** $24/month → $48/month (+$24)

**Checkpoint:** VPS upgraded and all services restarted ✅

---

### ☐ Step 1.2: Backup Current State

**Critical: Always backup before major changes!**

```bash
ssh root@159.223.75.148
cd ~/odoo-prod  # Or wherever your deployment is

# Create backup directory
mkdir -p backups/pre-v0.9.1-$(date +%Y%m%d_%H%M%S)

# Backup docker-compose
cp docker-compose.yml backups/pre-v0.9.1-$(date +%Y%m%d_%H%M%S)/

# Backup database
docker exec odoo-db pg_dump -U odoo odoo > backups/pre-v0.9.1-$(date +%Y%m%d_%H%M%S)/odoo_backup.sql
gzip backups/pre-v0.9.1-$(date +%Y%m%d_%H%M%S)/odoo_backup.sql

# Verify backup size
ls -lh backups/pre-v0.9.1-$(date +%Y%m%d_%H%M%S)/
```

**Checkpoint:** Backup created and verified ✅

---

## Phase 2: Build & Push Image (1-2 hours)

### ☐ Step 2.1: Apply Dockerfile Fixes

**On your local machine or CI runner:**

```bash
cd ~/odoo-ce  # Your repo directory

# Copy fixed Dockerfile
# Option A: If you have the audit outputs
cp /path/to/audit/outputs/Dockerfile.v0.9.1 ./Dockerfile

# Option B: Apply fixes manually (see CHANGELOG.md)
# 1. Add curl to system dependencies
# 2. Add Python requirements installation
# 3. Add ENV variable defaults
# 4. Add HEALTHCHECK directive

# Verify changes
cat Dockerfile
# Should show all 3 critical fixes applied
```

**Checkpoint:** Dockerfile updated with all fixes ✅

---

### ☐ Step 2.2: Build Image

```bash
cd ~/odoo-ce

# Set image tag
export IMAGE=ghcr.io/jgtolentino/odoo-ce:v0.9.1

# Build with automated script
./scripts/build_v0.9.1.sh

# OR manual build:
# export GHCR_PAT=your_github_token
# echo "$GHCR_PAT" | docker login ghcr.io -u jgtolentino --password-stdin
# DOCKER_BUILDKIT=1 docker build -t "$IMAGE" .
# docker push "$IMAGE"
```

**Expected Output:**
```
✅ Build successful!
✅ Health check: Present
✅ Environment variables: Set
✅ Custom modules: 5 ipai_* modules present
✅ Image verification complete
```

**Verification:**
```bash
# Check image size
docker images | grep odoo-ce
# Expected: ~1.3-1.5GB

# Verify health check
docker inspect ghcr.io/jgtolentino/odoo-ce:v0.9.1 --format='{{.Config.Healthcheck}}'
# Expected: HEALTHCHECK configuration

# Verify ENV vars
docker inspect ghcr.io/jgtolentino/odoo-ce:v0.9.1 --format='{{range .Config.Env}}{{println .}}{{end}}' | grep "HOST\|PORT\|USER"
# Expected: HOST=db, PORT=5432, USER=odoo, etc.
```

**Checkpoint:** Image built, verified, and pushed to GHCR ✅

---

## Phase 3: Production Deployment (1 hour)

### ☐ Step 3.1: Prepare Production Configuration

**On VPS:**

```bash
ssh root@159.223.75.148
cd ~/odoo-prod

# Copy new production compose file
# Option A: If you have deploy scripts
cp /path/to/deploy/docker-compose.prod.yml ./

# Option B: Update existing file
sed -i 's|image: ghcr.io/jgtolentino/odoo-ce:.*|image: ghcr.io/jgtolentino/odoo-ce:v0.9.1|g' docker-compose.yml

# Create .env.production from template
cp /path/to/deploy/.env.production.template .env.production

# CRITICAL: Edit .env.production with real passwords
nano .env.production
# Replace ALL CHANGE_ME_* placeholders

# Verify no placeholders remain
grep "CHANGE_ME" .env.production
# Expected: No output (empty result)
```

**Checkpoint:** Configuration updated with real credentials ✅

---

### ☐ Step 3.2: Deploy v0.9.1

```bash
cd ~/odoo-prod

# Option A: Automated deployment
./scripts/deploy_prod.sh

# Option B: Manual deployment
docker compose pull odoo
docker compose stop odoo
docker compose rm -f odoo
docker compose up -d odoo

# Wait for startup (60 seconds)
sleep 60

# Check status
docker compose ps
```

**Expected Output:**
```
NAME      IMAGE                                  STATUS
odoo-ce   ghcr.io/jgtolentino/odoo-ce:v0.9.1    Up (healthy)
odoo-db   postgres:16                            Up (healthy)
```

**Checkpoint:** Deployment complete, containers running ✅

---

## Phase 4: Verification & Testing (30 minutes)

### ☐ Step 4.1: Smoke Tests

```bash
cd ~/odoo-prod

# Run automated smoke tests
./scripts/smoketest.sh

# Expected output:
# ✅ All critical tests passed!
```

**Manual Checks:**

```bash
# 1. Health endpoint
curl -f http://127.0.0.1:8069/web/health
# Expected: HTTP 200

# 2. Web interface
curl -I http://127.0.0.1:8069/web
# Expected: HTTP 200 or 302

# 3. Container health
docker inspect odoo-ce --format='{{.State.Health.Status}}'
# Expected: healthy

# 4. Logs clean
docker logs odoo-ce --tail 50 | grep -i "error\|critical"
# Expected: No critical errors

# 5. Resource usage
docker stats odoo-ce --no-stream
# Expected: MEM < 2GB, CPU < 50%
```

**Checkpoint:** All smoke tests passing ✅

---

### ☐ Step 4.2: Browser Testing

**Open in browser:**

1. Navigate to: https://erp.insightpulseai.com
   - Expected: ✅ Odoo login page (no errors)

2. Login with admin credentials
   - Expected: ✅ Dashboard loads

3. Go to: Apps → Search "ipai"
   - Expected: ✅ All 5 custom modules visible:
     - IPAI CE Cleaner
     - IPAI Equipment Management
     - IPAI Expense & Travel (PH)
     - IPAI Finance Monthly Closing
     - IPAI Expense OCR

4. Test basic functionality:
   - Create a test project
   - Create a test expense
   - Verify database writes work

**Checkpoint:** Browser testing complete ✅

---

### ☐ Step 4.3: Module Verification

```bash
# Install/Update custom modules
docker exec odoo-ce odoo-bin -c /etc/odoo/odoo.conf \
  -d odoo \
  -u ipai_expense,ipai_ocr_expense,ipai_finance_monthly_closing \
  --stop-after-init

# Expected: Exit code 0, no errors
echo $?
# Expected: 0
```

**Checkpoint:** Modules install/update successfully ✅

---

## Phase 5: Monitoring Setup (30 minutes)

### ☐ Step 5.1: Enable DigitalOcean Alerts

```bash
# High memory alert
doctl monitoring alert-policy create \
  --name "odoo-high-memory" \
  --type v1/insights/droplet/memory_utilization_percent \
  --compare GreaterThan \
  --value 85 \
  --window 5m \
  --emails "your-email@example.com"

# High CPU alert
doctl monitoring alert-policy create \
  --name "odoo-high-cpu" \
  --type v1/insights/droplet/cpu \
  --compare GreaterThan \
  --value 90 \
  --window 5m \
  --emails "your-email@example.com"

# Disk space alert
doctl monitoring alert-policy create \
  --name "odoo-low-disk" \
  --type v1/insights/droplet/disk_utilization_percent \
  --compare GreaterThan \
  --value 80 \
  --window 5m \
  --emails "your-email@example.com"
```

**Checkpoint:** Monitoring alerts configured ✅

---

### ☐ Step 5.2: Log Monitoring

```bash
# Enable log monitoring
docker compose logs -f odoo &

# Or use dedicated log viewer
# tail -f /var/log/odoo/odoo.log  # If log volume mounted
```

**Checkpoint:** Log monitoring active ✅

---

## Phase 6: Post-Deployment (1-2 hours)

### ☐ Step 6.1: Team Notification

- [ ] Notify Finance Director CKVC: Deployment complete
- [ ] Notify Finance SSC team: System available
- [ ] Share deployment summary with stakeholders
- [ ] Schedule follow-up review (24 hours)

---

### ☐ Step 6.2: Documentation Updates

- [ ] Update deployment log with completion time
- [ ] Document any issues encountered
- [ ] Update runbook with lessons learned
- [ ] Archive backup confirmation

---

### ☐ Step 6.3: 24-Hour Monitoring

**Monitor these metrics for 24 hours:**

```bash
# Every 6 hours, check:
ssh root@159.223.75.148

# 1. Container health
docker compose ps

# 2. Resource usage
docker stats odoo-ce --no-stream

# 3. Error count
docker logs odoo-ce --since 6h 2>&1 | grep -c "ERROR\|CRITICAL"

# 4. Response time
time curl -sf http://127.0.0.1:8069/web/health

# 5. Disk space
df -h /
```

**Action if issues found:**
- Review logs: `docker logs odoo-ce --tail 200`
- Check resources: `htop` or `docker stats`
- Escalate if needed to Jake Tolentino

**Checkpoint:** 24-hour monitoring scheduled ✅

---

## Rollback Procedure (Emergency Only)

**If critical issues arise:**

```bash
ssh root@159.223.75.148
cd ~/odoo-prod

# Stop current deployment
docker compose down

# Restore backup config
cp backups/pre-v0.9.1-YYYYMMDD_HHMMSS/docker-compose.yml ./

# Restore database (if needed)
gunzip -c backups/pre-v0.9.1-YYYYMMDD_HHMMSS/odoo_backup.sql.gz | \
  docker exec -i odoo-db psql -U odoo odoo

# Restart with previous version
docker compose up -d

# Verify rollback
docker compose ps
curl http://127.0.0.1:8069/web
```

**Document rollback reason and open GitHub issue!**

---

## Success Criteria

**Deployment considered successful when ALL criteria met:**

- [x] VPS upgraded to 8GB RAM
- [x] Image v0.9.1 built and pushed to GHCR
- [x] Production deployment completed without errors
- [x] All smoke tests passing
- [x] Web interface accessible at https://erp.insightpulseai.com
- [x] All 5 custom modules visible and functional
- [x] No critical errors in logs
- [x] Resource usage within acceptable limits (MEM < 80%, CPU < 90%)
- [x] Health checks responding correctly
- [x] Database connectivity verified
- [x] Monitoring alerts configured
- [x] Team notified of successful deployment

---

## Key Contacts

**Deployment Lead:**
- Jake Tolentino (Finance SSC Technical Lead)
- Email: jgtolentino@tbwa-smp.ph
- GitHub: @jgtolentino

**Escalation Path:**
1. Jake Tolentino (Technical Lead)
2. Khalil Veracruz (Finance Director CKVC)
3. DigitalOcean Support (Infrastructure issues)

**Emergency Contacts:**
- Production Issues: GitHub Issues (security label)
- Infrastructure Down: DigitalOcean Support
- Critical Data Loss: Immediate escalation to Finance Director

---

## Deployment Log Template

```
Date: YYYY-MM-DD
Time Started: HH:MM SGT
Time Completed: HH:MM SGT
Deployed By: [Name]
Version: v0.9.1

Pre-Deployment:
- VPS State: [4GB/8GB]
- Backup Created: [Yes/No]
- Team Notified: [Yes/No]

Deployment:
- Build Time: [X minutes]
- Push Time: [X minutes]
- Deploy Time: [X minutes]
- Downtime: [X minutes]

Post-Deployment:
- Smoke Tests: [Pass/Fail]
- Browser Tests: [Pass/Fail]
- Performance: [Good/Acceptable/Poor]

Issues Encountered:
- [List any issues]

Lessons Learned:
- [Document improvements for next time]

Next Review: [Date + 24 hours]
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-25
**Status**: Ready for Production Deployment

---

**Good luck with the deployment! 🚀**
