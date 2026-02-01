# WorkOS Production Deployment Package

**Complete deployment automation for WorkOS (Notion Clone) to erp.insightpulseai.com**

---

## 📦 Package Contents

### Deployment Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| **deploy_workos_full.sh** | Full automated deployment | `scripts/prod/` |
| **rollback_workos.sh** | Automatic rollback | `scripts/prod/` |
| **verify_workos.sh** | Post-deployment verification | `scripts/prod/` |
| **gen_prod_snapshot.sh** | Runtime artifact generation | `tools/audit/` |

### Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| **DEPLOYMENT_EXECUTION_GUIDE.md** | Complete deployment manual | `docs/deployment/` |
| **PRE_FLIGHT_CHECKLIST.md** | Pre-deployment validation | `docs/deployment/` |
| **DEPLOYMENT_VERIFICATION_MATRIX.md** | Post-deployment testing | `docs/deployment/` |
| **CLAUDE_CODE_CLI_PROMPT.md** | Claude Code automation prompt | `docs/deployment/` |
| **WORKOS_DEPLOYMENT_PACKAGE.md** | This file (package overview) | `docs/deployment/` |

---

## 🚀 Quick Start

### Option 1: Claude Code CLI (Recommended)

```bash
# Copy-paste the deployment prompt
cat docs/deployment/CLAUDE_CODE_CLI_PROMPT.md

# Then paste into Claude Code CLI interface
```

### Option 2: Direct Script Execution

```bash
# Navigate to repository
cd ~/Documents/GitHub/odoo-ce

# Execute full deployment
chmod +x scripts/prod/deploy_workos_full.sh
bash scripts/prod/deploy_workos_full.sh
```

### Option 3: Claude Code Web Session

⚠️ **Note**: Web session can generate scripts but CANNOT execute on production

1. Copy prompt from `CLAUDE_CODE_CLI_PROMPT.md`
2. Paste into Claude Code web interface
3. Download generated scripts
4. Execute manually via SSH

---

## ✅ What's Included

### ✅ Full Deployment Automation (`deploy_workos_full.sh`)

- Pre-flight checks (SSH, disk space, Odoo health)
- Database backup with integrity verification
- Git sync from remote branch
- WorkOS module deployment
- Post-deployment verification
- Runtime artifact generation
- Git commit and push

### ✅ Rollback Capability (`rollback_workos.sh`)

- Automatic backup identification
- Database restoration
- Git commit revert
- Container restart
- Rollback verification
- Incident reporting

### ✅ Verification Matrix (`DEPLOYMENT_VERIFICATION_MATRIX.md`)

- **L1**: Basic deployment success
- **L2**: Functional verification
- **L3**: Performance & security
- **L4**: User acceptance testing

### ✅ Comprehensive Documentation

- Step-by-step execution guide
- Pre-flight checklist with sign-off
- Troubleshooting procedures
- Claude Code CLI prompt

---

## 📋 Deployment Workflow

```
Phase 1: Pre-Flight Checks
    ↓
Phase 2: Database Backup
    ↓
Phase 3: Git Sync (⚠️ CRITICAL)
    ↓
Phase 4: Module Deployment
    ↓
Phase 5: Deployment Verification
    ↓
Phase 6: Artifact Generation
    ↓
Phase 7: Commit & Push
    ↓
✅ Deployment Complete
```

**Duration**: ~15-20 minutes total

---

## 🛡️ Safety Features

| Feature | Description |
|---------|-------------|
| **Automatic Backup** | Database backup BEFORE any changes |
| **Validation Gates** | Pre-flight, installation, and post-deployment checks |
| **Rollback Ready** | One-command rollback with database restoration |
| **Error Handling** | Fail-fast on errors with detailed logging |
| **Audit Trail** | Complete deployment log for forensics |

---

## 📊 Success Criteria

**Deployment is SUCCESSFUL when:**

1. ✅ All 7 deployment phases complete without errors
2. ✅ Module state = "installed" in database
3. ✅ HTTP /web/login returns 200
4. ✅ No ERROR or CRITICAL in Odoo logs
5. ✅ User acceptance tests pass
6. ✅ Runtime artifacts committed to git
7. ✅ Deployment manifest generated

**Deployment is FAILED when:**

1. ❌ Module installation fails
2. ❌ Database errors occur
3. ❌ HTTP 500 errors persist
4. ❌ Critical features broken
5. ❌ Rollback required

---

## 🔥 Emergency Rollback

```bash
# SSH to production
ssh deploy@erp.insightpulseai.com

# Execute rollback
cd /opt/odoo-ce
bash scripts/prod/rollback_workos.sh
```

**What happens**:
- Confirms rollback intent (type "YES")
- Restores database from latest backup
- Reverts git to previous commit
- Restarts Odoo container
- Generates rollback report

**Duration**: ~5-10 minutes

---

## 📞 Support

### Deployment Team

- **Primary**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
- **Repository**: https://github.com/jgtolentino/odoo-ce
- **Branch**: claude/notion-clone-odoo-module-LSFan (PR #89)

### Documentation

1. **Quick Start**: `DEPLOYMENT_EXECUTION_GUIDE.md` → "Quick Start"
2. **Full Manual**: `DEPLOYMENT_EXECUTION_GUIDE.md` → "Step-by-Step"
3. **Verification**: `DEPLOYMENT_VERIFICATION_MATRIX.md`
4. **Rollback**: `DEPLOYMENT_EXECUTION_GUIDE.md` → "Rollback Procedure"

---

## 🎯 Next Steps

### Before Deployment

1. Review `PRE_FLIGHT_CHECKLIST.md`
2. Ensure PR #89 is approved
3. Verify SSH access to production
4. Confirm backup directory exists

### Execute Deployment

Choose one of three options:
- **Claude Code CLI** (recommended - automated)
- **Direct Script** (manual but reliable)
- **Claude Code Web** (requires manual execution)

### After Deployment

1. Complete verification matrix
2. Test admin user access
3. Create test workspace/page
4. Review deployment manifest
5. Monitor for 24 hours

---

**Package Version**: 1.0.0
**Created**: 2025-01-24
**Maintainer**: Jake Tolentino
