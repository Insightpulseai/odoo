# WorkOS Production Deployment - Execution Guide

**Target Environment**: erp.insightpulseai.com (Production)
**Module**: WorkOS (Notion Clone for Odoo)
**Branch**: claude/notion-clone-odoo-module-LSFan (PR #89)
**Repository**: https://github.com/jgtolentino/odoo-ce

---

## Quick Start (For CLI Deployment)

### Prerequisites

1. **CLI Tool Ready**: Claude Code CLI or standard terminal
2. **SSH Access**: Key-based authentication to `deploy@erp.insightpulseai.com`
3. **Git Access**: Authenticated to GitHub repository
4. **Permissions**: Sudo access on production server

### One-Command Deployment

```bash
# Clone or navigate to repository
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce

# Make deployment script executable
chmod +x scripts/prod/deploy_workos_full.sh

# Execute deployment (local → production)
bash scripts/prod/deploy_workos_full.sh
```

**What This Does**:
1. ✅ Pre-flight checks (SSH, disk space, Odoo health)
2. ✅ Creates database backup
3. ✅ Pulls latest code from remote
4. ✅ Deploys WorkOS module
5. ✅ Verifies installation
6. ✅ Commits runtime artifacts
7. ✅ Generates deployment manifest

**Duration**: ~10-15 minutes (including backups)

---

## Step-by-Step Manual Deployment

### Step 1: Pre-Flight Preparation

**Local Machine:**

```bash
# Navigate to repository
cd ~/Documents/GitHub/odoo-ce

# Pull latest changes
git fetch origin
git checkout claude/notion-clone-odoo-module-LSFan
git pull origin claude/notion-clone-odoo-module-LSFan

# Verify deployment scripts exist
ls -l scripts/prod/deploy_workos*.sh
ls -l docs/deployment/PRE_FLIGHT_CHECKLIST.md

# Review checklist
cat docs/deployment/PRE_FLIGHT_CHECKLIST.md
```

**Production Server:**

```bash
# SSH to production
ssh deploy@erp.insightpulseai.com

# Verify current state
cd /opt/odoo-ce
git status
git branch --show-current
docker ps | grep odoo

# Check disk space
df -h /opt/odoo-ce

# Check Odoo health
curl -I https://erp.insightpulseai.com/web/login
```

### Step 2: Database Backup

**Critical**: Always backup before deployment

```bash
# SSH to production
ssh deploy@erp.insightpulseai.com

# Create backup directory
sudo mkdir -p /var/backups/odoo
sudo chown deploy:deploy /var/backups/odoo

# Backup database
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec odoo-postgres pg_dump -U odoo -d odoo_accounting | gzip > /var/backups/odoo/odoo_accounting_${TIMESTAMP}.sql.gz

# Verify backup
ls -lh /var/backups/odoo/odoo_accounting_${TIMESTAMP}.sql.gz

# Test backup integrity
gunzip -t /var/backups/odoo/odoo_accounting_${TIMESTAMP}.sql.gz
echo "Backup OK"
```

### Step 3: Git Sync

**Production Server:**

```bash
cd /opt/odoo-ce

# Fetch remote changes
git fetch origin

# Show what will be deployed
git log --oneline HEAD..origin/claude/notion-clone-odoo-module-LSFan

# Checkout and pull
git checkout claude/notion-clone-odoo-module-LSFan
git pull --ff-only origin claude/notion-clone-odoo-module-LSFan

# Verify deployment commit
git log -1 --oneline
git rev-parse HEAD
```

### Step 4: Module Deployment

**Production Server:**

```bash
cd /opt/odoo-ce

# Make deployment script executable
chmod +x scripts/prod/deploy_workos.sh

# Run deployment
bash scripts/prod/deploy_workos.sh

# Monitor Odoo logs during deployment
docker logs -f odoo-accounting &

# Wait for deployment to complete
```

**Expected Output**:
- Module installation logs
- Database migration messages
- "Module installed successfully"

### Step 5: Verification

**Production Server:**

```bash
cd /opt/odoo-ce

# Run verification script
chmod +x scripts/prod/verify_workos.sh
bash scripts/prod/verify_workos.sh

# Manual verification
docker exec odoo-postgres psql -U odoo -d odoo_accounting -c "SELECT name, state FROM ir_module_module WHERE name = 'workos';"

# Expected: workos | installed

# Check HTTP endpoint
curl -I https://erp.insightpulseai.com/web/login

# Expected: HTTP/2 200
```

### Step 6: Generate Runtime Artifacts

**Production Server:**

```bash
cd /opt/odoo-ce

# Generate production snapshot
chmod +x tools/audit/gen_prod_snapshot.sh
bash tools/audit/gen_prod_snapshot.sh

# Verify artifacts created
ls -l docs/repo/REPO_SNAPSHOT.prod.json
ls -l docs/runtime/0000_MENU_SITEMAP.json
ls -l docs/runtime/PROD_SNAPSHOT_MANIFEST.md
```

### Step 7: Commit & Push

**Production Server:**

```bash
cd /opt/odoo-ce

# Stage runtime artifacts
git add docs/repo docs/runtime docs/PROD_SNAPSHOT.prod.json

# Commit
git commit -m "docs(runtime): production snapshot $(date +%Y%m%d_%H%M%S)

Deployed: claude/notion-clone-odoo-module-LSFan
Commit: $(git rev-parse HEAD)
Backup: /var/backups/odoo/odoo_accounting_${TIMESTAMP}.sql.gz"

# Push to remote
git push origin claude/notion-clone-odoo-module-LSFan
```

---

## Rollback Procedure

### Automatic Rollback

```bash
# SSH to production
ssh deploy@erp.insightpulseai.com

# Execute rollback script
cd /opt/odoo-ce
chmod +x scripts/prod/rollback_workos.sh
bash scripts/prod/rollback_workos.sh
```

**Script Will**:
1. Confirm rollback intent
2. Identify latest backup
3. Stop Odoo container
4. Restore database
5. Revert git commit
6. Restart Odoo
7. Verify rollback
8. Generate rollback report

### Manual Rollback

**If automatic rollback fails:**

```bash
# Stop Odoo
docker stop odoo-accounting

# Restore database
BACKUP_FILE="/var/backups/odoo/odoo_accounting_20250124_*.sql.gz"
docker exec odoo-postgres psql -U odoo -c "DROP DATABASE odoo_accounting;"
docker exec odoo-postgres psql -U odoo -c "CREATE DATABASE odoo_accounting OWNER odoo;"
gunzip < $BACKUP_FILE | docker exec -i odoo-postgres psql -U odoo -d odoo_accounting

# Revert git
cd /opt/odoo-ce
git reset --hard HEAD~1

# Restart Odoo
docker start odoo-accounting

# Verify
curl -I https://erp.insightpulseai.com/web/login
```

---

## Troubleshooting

### Issue: Module Install Fails

**Symptoms**: Error during `deploy_workos.sh` execution

**Diagnosis**:
```bash
# Check Odoo logs
docker logs odoo-accounting --tail=100 | grep ERROR

# Check PostgreSQL logs
docker logs odoo-postgres --tail=100

# Check module state
docker exec odoo-postgres psql -U odoo -d odoo_accounting -c "SELECT name, state FROM ir_module_module WHERE name = 'workos';"
```

**Resolution**:
1. Review error messages
2. Check for missing dependencies
3. Verify database schema
4. Execute rollback if unrecoverable

### Issue: HTTP 500 Errors

**Symptoms**: `/web/login` returns HTTP 500

**Diagnosis**:
```bash
# Check Odoo server logs
docker logs odoo-accounting --tail=200

# Check for Python traceback
docker logs odoo-accounting 2>&1 | grep -A 10 "Traceback"

# Test database connectivity
docker exec odoo-accounting python3 -c "import psycopg2; conn = psycopg2.connect('dbname=odoo_accounting user=odoo host=odoo-postgres'); print('DB OK')"
```

**Resolution**:
1. Restart Odoo container: `docker restart odoo-accounting`
2. If persists, execute rollback
3. Investigate root cause before retry

### Issue: Database Backup Fails

**Symptoms**: Backup file is 0 bytes or `pg_dump` errors

**Diagnosis**:
```bash
# Check PostgreSQL container
docker ps | grep odoo-postgres

# Test database access
docker exec odoo-postgres psql -U odoo -c "SELECT 1;"

# Check disk space
df -h /var/backups/odoo
```

**Resolution**:
1. Ensure PostgreSQL container is running
2. Verify database credentials
3. Check disk space availability
4. Retry backup manually

### Issue: Git Sync Fails

**Symptoms**: `git pull` fails with conflicts

**Diagnosis**:
```bash
cd /opt/odoo-ce
git status
git diff
git log --oneline --graph --all
```

**Resolution**:
```bash
# Option 1: Stash local changes
git stash
git pull --ff-only origin claude/notion-clone-odoo-module-LSFan

# Option 2: Hard reset (DESTRUCTIVE)
git reset --hard origin/claude/notion-clone-odoo-module-LSFan

# Option 3: Abort and investigate
git merge --abort
# Manual resolution required
```

---

## Post-Deployment Checklist

### Immediate (Within 1 Hour)

- [ ] Verify `/web/login` accessible
- [ ] Check Odoo server logs for errors
- [ ] Confirm module state = "installed"
- [ ] Test admin user login
- [ ] Create test workspace/page
- [ ] Review deployment manifest

### Short-Term (Within 24 Hours)

- [ ] User acceptance testing
- [ ] Performance monitoring
- [ ] Security scan
- [ ] Review all verification matrix items
- [ ] Update deployment documentation

### Long-Term (Within 1 Week)

- [ ] Collect user feedback
- [ ] Monitor error logs
- [ ] Performance optimization
- [ ] Plan next iteration
- [ ] Document lessons learned

---

## Contact & Escalation

### Deployment Team

- **Primary Contact**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
- **Backup Contact**: [Secondary contact if available]
- **Escalation**: [Manager/Director if critical issue]

### Emergency Contacts

- **Infrastructure**: DigitalOcean Support
- **Database**: PostgreSQL Expert (if available)
- **Application**: Odoo CE Community Forums

### Incident Response

**Severity Levels**:
- **P0 (Critical)**: Production down, immediate rollback
- **P1 (High)**: Major feature broken, deploy hotfix
- **P2 (Medium)**: Minor issues, fix in next cycle
- **P3 (Low)**: Cosmetic issues, backlog

---

## Appendix: File Locations

### Local Repository

```
odoo-ce/
├── scripts/prod/
│   ├── deploy_workos_full.sh       # Full deployment automation
│   ├── deploy_workos.sh            # Module deployment script
│   ├── verify_workos.sh            # Verification script
│   └── rollback_workos.sh          # Rollback automation
├── docs/deployment/
│   ├── PRE_FLIGHT_CHECKLIST.md     # Pre-deployment checklist
│   ├── DEPLOYMENT_VERIFICATION_MATRIX.md  # Verification matrix
│   └── DEPLOYMENT_EXECUTION_GUIDE.md      # This file
└── tools/audit/
    └── gen_prod_snapshot.sh        # Artifact generation
```

### Production Server

```
/opt/odoo-ce/                       # Repository root
/var/backups/odoo/                  # Database backups
/var/log/odoo-deployment/           # Deployment logs
/var/log/nginx/                     # Web server logs
```

---

## Success Criteria

**Deployment is successful when:**

1. ✅ All phases complete without errors
2. ✅ HTTP endpoints return 200
3. ✅ Module state = "installed"
4. ✅ No errors in Odoo logs
5. ✅ User acceptance tests pass
6. ✅ Runtime artifacts committed
7. ✅ Deployment manifest generated

**Deployment is failed when:**

1. ❌ Module install fails
2. ❌ Database errors occur
3. ❌ HTTP 500 errors persist
4. ❌ Critical features broken
5. ❌ Rollback required

---

**Last Updated**: 2025-01-24
**Version**: 1.0.0
**Maintainer**: Jake Tolentino
