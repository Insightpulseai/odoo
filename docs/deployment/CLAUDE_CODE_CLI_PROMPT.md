# Claude Code CLI Deployment Prompt

**Copy-paste this prompt into Claude Code CLI to execute production deployment**

---

```
You are a production deployment automation agent for Odoo CE 18.0.

DEPLOYMENT CONTEXT:
- Project: WorkOS (Notion Clone for Odoo)
- Repository: https://github.com/jgtolentino/odoo-ce
- Branch: claude/notion-clone-odoo-module-LSFan (PR #89)
- Target Environment: erp.insightpulseai.com (Production)
- Deployment Path: /opt/odoo-ce
- SSH User: deploy@erp.insightpulseai.com

DEPLOYMENT OBJECTIVES:
1. Pull latest code from remote branch (git fetch + pull)
2. Create database backup BEFORE any changes
3. Deploy WorkOS module to production Odoo instance
4. Verify installation and functionality
5. Generate runtime artifacts (repo tree, DB sitemap, HTTP map)
6. Commit artifacts to git and push to remote
7. Generate deployment manifest

CONSTRAINTS & REQUIREMENTS:
- ✅ MUST pull from remote before deployment (git sync required)
- ✅ MUST create database backup before module install
- ✅ MUST verify all HTTP endpoints after deployment
- ✅ MUST generate and commit runtime artifacts
- ✅ MUST use existing deployment scripts in scripts/prod/
- ⚠️ NO rollback unless explicitly requested
- ⚠️ NO destructive operations without confirmation
- ⚠️ ALL commands must be logged and documented

DEPLOYMENT WORKFLOW:
Execute the following phases in sequence:

Phase 1: Pre-Flight Checks
- Verify SSH connectivity to production server
- Check Odoo health endpoints (/web/login)
- Verify disk space availability
- Confirm backup directory exists
- Check docker containers running

Phase 2: Database Backup
- Create timestamped backup: /var/backups/odoo/odoo_accounting_YYYYMMDD_HHMMSS.sql.gz
- Verify backup file size > 1MB
- Test backup integrity with gunzip -t

Phase 3: Git Sync (CRITICAL)
- git fetch origin
- git checkout claude/notion-clone-odoo-module-LSFan
- git pull --ff-only origin claude/notion-clone-odoo-module-LSFan
- Verify commit hash matches remote
- Show what will be deployed (git log -1)

Phase 4: Module Deployment
- Execute: bash scripts/prod/deploy_workos.sh
- Monitor Odoo container logs during deployment
- Verify module installation completes successfully

Phase 5: Deployment Verification
- Execute: bash scripts/prod/verify_workos.sh
- Verify module state = "installed" in database
- Check HTTP endpoints return 200
- Review Odoo server logs for errors

Phase 6: Generate Runtime Artifacts
- Execute: bash tools/audit/gen_prod_snapshot.sh
- Generate repository tree snapshot
- Generate database menu sitemap
- Generate HTTP route map
- Create deployment manifest

Phase 7: Commit & Push Artifacts
- git add docs/repo docs/runtime docs/PROD_SNAPSHOT.prod.json
- Commit with deployment metadata (timestamp, commit hash, backup path)
- git push origin claude/notion-clone-odoo-module-LSFan

DELIVERABLES:
Generate the following outputs:

1. Complete bash deployment script (ready to execute via SSH)
   - File: scripts/prod/deploy_workos_full.sh
   - Executable: chmod +x
   - Logged: All output to /var/log/odoo-deployment/

2. Pre-flight checklist (for manual review)
   - File: docs/deployment/PRE_FLIGHT_CHECKLIST.md
   - Format: Markdown with checkboxes

3. Deployment verification matrix (post-deployment validation)
   - File: docs/deployment/DEPLOYMENT_VERIFICATION_MATRIX.md
   - Levels: L1 (basic), L2 (functional), L3 (performance), L4 (UAT)

4. Rollback procedure (emergency recovery)
   - File: scripts/prod/rollback_workos.sh
   - Automatic backup restoration
   - Git revert capability

5. Deployment execution guide (step-by-step manual)
   - File: docs/deployment/DEPLOYMENT_EXECUTION_GUIDE.md
   - Quick start + detailed steps
   - Troubleshooting section

ERROR HANDLING:
- If ANY phase fails → STOP immediately
- Log error details to deployment log
- Provide rollback instructions
- DO NOT continue if backup fails
- DO NOT deploy if git sync fails
- DO NOT commit if verification fails

SUCCESS CRITERIA:
Deployment is successful ONLY when:
✅ All 7 phases complete without errors
✅ Module state = "installed" in database
✅ HTTP /web/login returns 200
✅ No ERROR or CRITICAL in Odoo logs
✅ Runtime artifacts generated and committed
✅ Deployment manifest created

EXECUTION MODE:
Use the existing deployment automation scripts:
- scripts/prod/deploy_workos_full.sh (primary)
- scripts/prod/verify_workos.sh (verification)
- tools/audit/gen_prod_snapshot.sh (artifacts)

PROCEED WITH DEPLOYMENT:
Execute the full deployment workflow using the scripts.
Log all operations.
Report completion status.
Provide deployment manifest location.

Ready to deploy? Confirm and execute.
```

---

## How to Use This Prompt

### Option 1: Claude Code Web Session

1. Copy the entire prompt above
2. Paste into Claude Code web interface
3. Claude will generate scripts but CANNOT execute on production
4. Download generated scripts and execute manually via SSH

### Option 2: Claude Code CLI

1. Save this file locally
2. Run: `claude code chat "$(cat docs/deployment/CLAUDE_CODE_CLI_PROMPT.md)"`
3. Claude Code CLI will execute deployment automation
4. Monitor output and verify completion

### Option 3: Direct Script Execution

```bash
# Navigate to repository
cd ~/Documents/GitHub/odoo-ce

# Make script executable
chmod +x scripts/prod/deploy_workos_full.sh

# Execute deployment
bash scripts/prod/deploy_workos_full.sh
```

---

## What Claude Code Will Do

### Automated Actions

1. ✅ SSH to production server
2. ✅ Pull latest code from remote branch
3. ✅ Create database backup
4. ✅ Deploy WorkOS module
5. ✅ Verify installation
6. ✅ Generate runtime artifacts
7. ✅ Commit and push to remote

### Manual Review Points

- Database backup path confirmation
- Module installation log review
- Verification test results
- Deployment manifest review

### Duration

- **Full Deployment**: ~10-15 minutes
- **Verification**: ~5 minutes
- **Artifact Generation**: ~2-3 minutes
- **Total**: ~20-25 minutes

---

## Expected Output

```
=========================================
WorkOS Production Deployment
Target: erp.insightpulseai.com
Branch: claude/notion-clone-odoo-module-LSFan
Time: 2025-01-24 14:30:00
=========================================

=== Phase 1: Pre-Deployment Verification ===
✓ SSH connection successful
✓ Repository path verified
✓ Odoo /web/login is accessible
✓ Disk usage: 45%
✓ Pre-flight checks completed

=== Phase 2: Database Backup ===
✓ Database backup created: /var/backups/odoo/odoo_accounting_20250124_143000.sql.gz (125 MB)

=== Phase 3: Git Sync ===
Current branch: claude/notion-clone-odoo-module-LSFan
Deploying commit: abc1234 feat: WorkOS module implementation
✓ Git sync completed

=== Phase 4: Module Deployment ===
Running deployment script...
Module installation successful
✓ Module deployment completed

=== Phase 5: Deployment Verification ===
Running verification script...
Module state: installed
HTTP status: 200
✓ Deployment verification completed

=== Phase 6: Commit Runtime Artifacts ===
✓ Artifacts committed and pushed

=== Phase 7: Generate Deployment Manifest ===
✓ Deployment manifest generated

=========================================
✅ DEPLOYMENT COMPLETED SUCCESSFULLY
=========================================
Deployment log: /var/log/odoo-deployment/workos_deploy_20250124_143000.log
Backup: /var/backups/odoo/odoo_accounting_20250124_143000.sql.gz
Manifest: docs/runtime/PROD_SNAPSHOT_MANIFEST.md
```

---

## Troubleshooting

If deployment fails, Claude Code will:

1. **Stop immediately** at failed phase
2. **Log error details** to deployment log
3. **Provide rollback command**: `bash scripts/prod/rollback_workos.sh`
4. **Show error context** for debugging

Common issues:

- **SSH authentication fails** → Check SSH keys
- **Git sync fails** → Resolve merge conflicts manually
- **Module install fails** → Check Odoo logs, execute rollback
- **Verification fails** → Review verification matrix, decide if critical

---

**Created**: 2025-01-24
**Version**: 1.0.0
**Maintainer**: Jake Tolentino
