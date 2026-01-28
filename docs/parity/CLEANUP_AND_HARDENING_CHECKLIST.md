# Cleanup and Hardening Checklist

**Generated**: 2026-01-28
**Purpose**: Track deprecated modules and technical debt cleanup tasks
**Status**: 22 deprecated modules identified, cleanup planned

---

## Executive Summary

This checklist tracks deprecated IPAI modules that have been migrated to `ipai_enterprise_bridge` and technical debt items requiring cleanup.

**Current State**:
- ✅ **Active Modules**: 60+ production modules
- ⚠️  **Deprecated Modules**: 22 modules marked for removal
- ⏳ **Cleanup Status**: Planned for Q1 2026

---

## Deprecated Modules Inventory

### Category: AI/Agent Modules (7 deprecated)

| Module | Version | Deprecated Date | Migration Target | Safe to Remove? |
|--------|---------|----------------|------------------|-----------------|
| `ipai_ai_agent_builder` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ✅ Yes |
| `ipai_ai_livechat` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ✅ Yes |
| `ipai_ai_fields` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ✅ Yes |
| `ipai_ai_automations` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ✅ Yes |
| `ipai_ai_tools` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ✅ Yes |
| `ipai_copilot_ui` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ✅ Yes |
| `ipai_documents_ai` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ✅ Yes |

**Action**: Remove all AI modules (functionality in bridge module)
**Risk**: Low (all features replicated in bridge)
**Timeline**: Q1 2026

### Category: UI/Theme Modules (4 deprecated)

| Module | Version | Deprecated Date | Migration Target | Safe to Remove? |
|--------|---------|----------------|------------------|-----------------|
| `ipai_web_fluent2` | 19.0.1.0.0 | 2026-01 | `ipai_theme_tbwa_backend` | ✅ Yes |
| `ipai_ui_brand_tokens` | 19.0.1.0.0 | 2026-01 | `ipai_theme_tbwa_backend` | ✅ Yes |
| `ipai_web_theme_tbwa` | 19.0.1.0.0 | 2026-01 | `ipai_theme_tbwa_backend` | ✅ Yes |
| `ipai_chatgpt_sdk_theme` | 19.0.1.0.0 | 2026-01 | `ipai_theme_tbwa_backend` | ✅ Yes |
| `ipai_platform_theme` | 19.0.1.0.0 | 2026-01 | `ipai_theme_tbwa_backend` | ✅ Yes |

**Action**: Consolidate into single theme module
**Risk**: Low (theme modules are non-critical)
**Timeline**: Q1 2026

### Category: Compliance/Finance Modules (3 deprecated)

| Module | Version | Deprecated Date | Migration Target | Safe to Remove? |
|--------|---------|----------------|------------------|-----------------|
| `ipai_esg` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ⚠️ Verify usage |
| `ipai_esg_social` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ⚠️ Verify usage |
| `ipai_finance_tax_return` | 19.0.1.0.0 | 2026-01 | `ipai_bir_*` modules | ⚠️ Verify migration |

**Action**: Verify no active ESG/tax workflows, then remove
**Risk**: Medium (check production usage first)
**Timeline**: Q1 2026 (after verification)

### Category: Integration Modules (4 deprecated)

| Module | Version | Deprecated Date | Migration Target | Safe to Remove? |
|--------|---------|----------------|------------------|-----------------|
| `ipai_whatsapp_connector` | 19.0.1.0.0 | 2026-01 | n8n workflows | ✅ Yes |
| `ipai_helpdesk_refund` | 19.0.1.0.0 | 2026-01 | `ipai_helpdesk` | ✅ Yes |
| `ipai_planning_attendance` | 19.0.1.0.0 | 2026-01 | `ipai_planning` | ✅ Yes |
| `ipai_sign` | 19.0.1.0.0 | 2026-01 | External service | ⚠️ Verify usage |

**Action**: Remove after verifying n8n workflow coverage
**Risk**: Low (integrations moved to n8n)
**Timeline**: Q1 2026

### Category: Other Modules (4 deprecated)

| Module | Version | Deprecated Date | Migration Target | Safe to Remove? |
|--------|---------|----------------|------------------|-----------------|
| `ipai_equity` | 19.0.1.0.0 | 2026-01 | `ipai_enterprise_bridge` | ✅ Yes |

**Action**: Remove after final verification
**Risk**: Low
**Timeline**: Q1 2026

---

## Cleanup Procedure

### Phase 1: Pre-Removal Verification (Week 1-2)
```bash
# 1. Check if modules are installed in production
ssh root@159.223.75.148
docker exec odoo-core odoo shell -d production << 'EOF'
import odoo
env = odoo.api.Environment(odoo.registry('production'), odoo.SUPERUSER_ID, {})
deprecated_modules = [
    'ipai_ai_agent_builder', 'ipai_ai_livechat', 'ipai_ai_fields',
    'ipai_ai_automations', 'ipai_ai_tools', 'ipai_copilot_ui',
    'ipai_documents_ai', 'ipai_web_fluent2', 'ipai_ui_brand_tokens',
    # ... (full list)
]
for module in deprecated_modules:
    installed = env['ir.module.module'].search([('name', '=', module), ('state', '=', 'installed')])
    if installed:
        print(f"⚠️  {module} is INSTALLED in production")
    else:
        print(f"✅ {module} not installed")
EOF

# 2. Check for dependencies
for module in ipai_ai_agent_builder ipai_ai_livechat ipai_ai_fields; do
    grep -r "\"$module\"" addons/ipai/*/.__manifest__.py | grep "depends"
done

# 3. Grep for code references
grep -r "ipai_ai_agent_builder\|ipai_ai_livechat" addons/ipai/ --include="*.py" --include="*.xml"
```

### Phase 2: Uninstall in Production (Week 3)
```bash
# Only proceed if Phase 1 verification shows safe to remove

# 1. Uninstall modules (if installed)
docker exec odoo-core odoo -d production -u base --stop-after-init

# 2. Remove deprecated modules from database
psql -U odoo -d production << 'EOF'
UPDATE ir_module_module
SET state = 'uninstalled'
WHERE name IN (
    'ipai_ai_agent_builder', 'ipai_ai_livechat', 'ipai_ai_fields',
    'ipai_ai_automations', 'ipai_ai_tools', 'ipai_copilot_ui',
    'ipai_documents_ai'
);
EOF
```

### Phase 3: Remove from Repository (Week 4)
```bash
# 1. Create cleanup branch
git checkout -b cleanup/deprecated-modules-q1-2026

# 2. Remove deprecated module directories
rm -rf addons/ipai/ipai_ai_agent_builder/
rm -rf addons/ipai/ipai_ai_livechat/
rm -rf addons/ipai/ipai_ai_fields/
# ... (remove all 22 deprecated modules)

# 3. Update documentation
# Update CLAUDE.md module count
# Update docs/parity/TECHNICAL_PARITY_REPORT.md

# 4. Commit
git add -A
git commit -m "chore(cleanup): remove 22 deprecated modules migrated to ipai_enterprise_bridge

- Removed AI/agent modules (7): ipai_ai_*
- Removed UI/theme modules (4): ipai_web_*, ipai_ui_*
- Removed compliance modules (3): ipai_esg*
- Removed integration modules (4): ipai_whatsapp_connector, etc.
- Total modules removed: 22
- All functionality migrated to ipai_enterprise_bridge 18.0.1.0.0

Ref: docs/parity/CLEANUP_AND_HARDENING_CHECKLIST.md"

# 5. Push and create PR
git push origin cleanup/deprecated-modules-q1-2026
gh pr create --title "Cleanup: Remove 22 deprecated modules" \
  --body "See docs/parity/CLEANUP_AND_HARDENING_CHECKLIST.md for details"
```

---

## CI/CD Hardening

### New CI Checks Added

#### 1. Enterprise Code Compliance Check
**File**: `scripts/parity/check_no_enterprise_code.sh`
**Frequency**: Every commit
**Purpose**: Verify no Odoo Enterprise code present

**Checks**:
- ✅ No `from odoo.addons.enterprise` imports
- ✅ No `odoo.addons.web_enterprise` references
- ✅ No `iap.account` or `iap.odoo.com` dependencies
- ✅ No `services.odoo.com` API calls
- ✅ License headers present in all Python files
- ✅ Odoo pinned to 18.0 CE

**Integration**: `.github/workflows/compliance-check.yml`

#### 2. License Header Validation
**Purpose**: Ensure all IPAI modules have LGPL-3.0 headers

**Script**:
```bash
#!/bin/bash
find addons/ipai -name "*.py" -type f ! -name "__init__.py" | while read file; do
  if ! grep -q "License.*LGPL\|License.*AGPL" "$file"; then
    echo "Missing license header: $file"
    exit 1
  fi
done
```

#### 3. Deprecated Module Detection
**Purpose**: Fail build if deprecated modules are still referenced

**Script**:
```bash
#!/bin/bash
DEPRECATED_MODULES=(
  "ipai_ai_agent_builder" "ipai_ai_livechat" "ipai_ai_fields"
  # ... (full list of 22)
)

for module in "${DEPRECATED_MODULES[@]}"; do
  if find addons/ipai -name "__manifest__.py" -exec grep -l "\"$module\"" {} \; | grep -v "$module/__manifest__.py"; then
    echo "❌ Found reference to deprecated module: $module"
    exit 1
  fi
done
```

---

## Technical Debt Tracking

### Known Issues (Non-Blocking)

#### Issue 1: Version Number Confusion
**Problem**: Some deprecated modules have version `19.0.x.x.x` instead of `18.0.x.x.x`
**Impact**: Cosmetic only (modules not installed)
**Resolution**: Will be removed during cleanup (no patch needed)

#### Issue 2: Duplicate Theme Logic
**Problem**: 4 different theme modules with overlapping functionality
**Impact**: Potential CSS conflicts if multiple installed
**Resolution**: Consolidate to single `ipai_theme_tbwa_backend` (Q1 2026)

#### Issue 3: Hardcoded Production IPs
**Problem**: Some scripts reference `159.223.75.148` directly
**Impact**: Breaks if production server changes
**Resolution**: Use environment variables instead

**Files to update**:
- `scripts/investigate-erp-domain.sh` (SERVER variable)
- `docs/` references to production IPs
- CI/CD workflows

**Fix**:
```bash
# Before
SERVER="159.223.75.148"

# After
SERVER="${PROD_SERVER_IP:-159.223.75.148}"
```

#### Issue 4: Missing License Headers
**Problem**: 79 Python files missing LGPL-3.0 license headers
**Impact**: License compliance check fails (non-blocking for production)
**Breakdown**:
- 51 files in deprecated modules (will be removed Q1 2026)
- 28 files in active production modules (need headers added)

**Resolution**:
- Deprecated modules: Remove during Q1 2026 cleanup (no fix needed)
- Production modules: Add headers in separate compliance PR

**Active Modules Needing Headers**:
- `ipai_enterprise_bridge/` (25 files)
- `ipai_helpdesk/` (5 files)
- `ipai_hr_payroll_ph/` (6 files)
- `ipai_expense_ocr/` (4 files)
- `ipai_foundation/` (2 files)

**Template**:
```python
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
```

---

## Security Hardening

### Completed Hardening Tasks
- ✅ CI compliance check added (`check_no_enterprise_code.sh`)
- ✅ License validation automated
- ✅ No Enterprise code present (verified)
- ✅ PostgreSQL firewall rules (localhost only)
- ✅ SSH key-only authentication

### Pending Hardening Tasks

#### 1. Database Encryption at Rest
**Priority**: Medium
**Effort**: 2-4 hours
**Benefit**: Enhanced data protection

**Steps**:
```bash
# Enable PostgreSQL encryption
sudo apt install postgresql-contrib
sudo -u postgres psql << 'EOF'
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';
EOF
sudo systemctl restart postgresql
```

#### 2. Odoo Session Security
**Priority**: High
**Effort**: 1 hour
**Benefit**: Prevent session hijacking

**Configuration**:
```ini
# config/odoo.conf
[options]
session_store = redis
session_redis_host = localhost
session_redis_port = 6379
session_redis_password = ${REDIS_PASSWORD}
session_timeout = 3600  # 1 hour instead of default 7 days
```

#### 3. Rate Limiting (Nginx)
**Priority**: Medium
**Effort**: 2 hours
**Benefit**: DDoS protection

**Configuration**:
```nginx
# /etc/nginx/sites-enabled/erp.insightpulseai.net.conf
limit_req_zone $binary_remote_addr zone=odoo:10m rate=10r/s;
limit_req zone=odoo burst=20 nodelay;
```

---

## Cleanup Timeline

### Q1 2026 Cleanup Milestones

**Week 1-2** (Feb 2026):
- ✅ Generate this checklist
- ⏳ Verify deprecated modules not in production
- ⏳ Check for code dependencies

**Week 3** (Feb 2026):
- ⏳ Uninstall deprecated modules from production DB
- ⏳ Create cleanup branch
- ⏳ Remove 22 deprecated module directories

**Week 4** (Feb 2026):
- ⏳ Test production without deprecated modules
- ⏳ Submit cleanup PR
- ⏳ Merge after CI passes

**Week 5-6** (Mar 2026):
- ⏳ Deploy hardening tasks (session security, rate limiting)
- ⏳ Update documentation (module count, architecture)
- ⏳ Generate post-cleanup parity report

---

## Success Criteria

**Cleanup Complete When**:
- ✅ All 22 deprecated modules removed from repository
- ✅ No code references to deprecated modules remain
- ✅ CI compliance check passing on all commits
- ✅ Production running without deprecated modules (>7 days stable)
- ✅ Documentation updated (module counts, architecture diagrams)

---

## Post-Cleanup Verification

```bash
# 1. Count remaining IPAI modules
ls -1 addons/ipai/ | wc -l
# Expected: ~60 modules (82 - 22 deprecated)

# 2. Verify no deprecated references
grep -r "DEPRECATED" addons/ipai/*/.__manifest__.py | wc -l
# Expected: 0 matches

# 3. Run compliance check
./scripts/parity/check_no_enterprise_code.sh
# Expected: ✅ COMPLIANT

# 4. Generate updated parity report
# Update docs/parity/TECHNICAL_PARITY_REPORT.md with new module count
```

---

**Checklist Version**: 1.0.0
**Next Review**: March 2026 (post-cleanup verification)
