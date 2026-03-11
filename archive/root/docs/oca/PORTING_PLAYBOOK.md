# OCA Module Porting Playbook (18.0 → 19.0)

> **Canonical reference for porting OCA modules to Odoo 19.0**
> Uses official OCA tooling: `oca-port` CLI, OpenUpgrade libraries, maintainer-tools

---

## Overview

**Goal**: Port 40 OCA modules from 18.0 to 19.0 to achieve 85%+ Odoo EE parity.

**Tooling**:
- `oca-port` (PyPI): Automated migration assistant
- OpenUpgrade: Migration data and scripts
- OCA maintainer-tools: Quality validation

**Workflow**: select → port → test → commit → PR (upstream)

---

## Prerequisites

```bash
# Install oca-port globally (one-time)
pip3 install oca-port

# Verify installation
oca-port --version
# Expected: oca-port 0.x.x or higher
```

---

## Deterministic Workflow

### Step 1: Select Module

**From port queue**:

```bash
# View pending P0 modules
yq '.priorities.P0.modules[] | select(.status == "pending")' config/oca/port_queue.yml

# Check dependencies
yq '.priorities.P0.modules[] | select(.name == "server_environment") | .depends' config/oca/port_queue.yml
# Expected: [] (no dependencies) → safe to port
```

**Manual selection** (if queue unavailable):

1. Identify missing module in `addons/oca/<repo>/`
2. Confirm OCA repo has 18.0 branch on GitHub
3. Check no blocking dependencies

### Step 2: Fork & Port (Automated via `oca-port`)

```bash
# Set module and repo
MODULE="server_environment"
REPO="server-tools"

# Run oca-port (handles git operations + migration)
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
oca-port ${MODULE} --from 18.0 --to 19.0 --repo OCA/${REPO}

# oca-port automatically:
# 1. Clones OCA repo if not exists
# 2. Creates port branch: port/<module>/18.0-to-19.0
# 3. Applies OpenUpgrade migration scripts
# 4. Updates __manifest__.py version
# 5. Commits changes with conventional message
```

**Expected output**:

```
INFO: Cloning OCA/server-tools...
INFO: Creating port branch port/server_environment/18.0-to-19.0
INFO: Applying migration from 18.0 to 19.0...
INFO: Updated __manifest__.py version to 19.0.1.0.0
INFO: Port completed successfully
```

### Step 3: Smoke Test (Minimal Acceptance Criteria)

**Checklist**:

- ✅ Module exists in `addons/oca/<repo>/<module>/`
- ✅ `__manifest__.py` version is `19.0.x.y.z`
- ✅ No Python syntax errors
- ✅ Module loads in Odoo shell
- ✅ Module installs without errors

**Commands**:

```bash
# 1. Verify module directory
ls -la addons/oca/${REPO}/${MODULE}/__manifest__.py
# Expected: file exists

# 2. Check version
grep "^    'version':" addons/oca/${REPO}/${MODULE}/__manifest__.py
# Expected: 'version': '19.0.1.0.0' or similar

# 3. Python syntax check
python3 -m py_compile addons/oca/${REPO}/${MODULE}/**/*.py
# Expected: no output (success)

# 4. Odoo shell load test
./scripts/odoo_shell.sh -c "env['ir.module.module'].search([('name', '=', '${MODULE}')])"
# Expected: module record returned (not empty)

# 5. Install test
./scripts/odoo_module_install.sh ${MODULE}
# Expected: "Module ${MODULE} installed successfully"
```

### Step 4: Evidence Capture

**Required artifacts**:

```bash
# Create evidence directory
TIMESTAMP=$(date +"%Y%m%d-%H%M%z")
EVIDENCE_DIR="web/docs/evidence/${TIMESTAMP}/oca-port-${MODULE}"
mkdir -p "${EVIDENCE_DIR}/logs"

# Capture port log
oca-port ${MODULE} --from 18.0 --to 19.0 --repo OCA/${REPO} 2>&1 | tee "${EVIDENCE_DIR}/logs/port.log"

# Capture install log
./scripts/odoo_module_install.sh ${MODULE} 2>&1 | tee "${EVIDENCE_DIR}/logs/install.log"

# Save patch (if manual changes)
git diff > "${EVIDENCE_DIR}/patch/${MODULE}.patch"

# Document status
cat > "${EVIDENCE_DIR}/STATUS.md" << EOFSTATUS
# Port Status: ${MODULE}

- **From**: 18.0
- **To**: 19.0
- **OCA Repo**: ${REPO}
- **Status**: ✅ COMPLETED
- **Timestamp**: ${TIMESTAMP}

## Verification

- [x] Module directory exists
- [x] Version is 19.0.x.y.z
- [x] No syntax errors
- [x] Loads in Odoo shell
- [x] Installs successfully

## Evidence

- Port log: logs/port.log
- Install log: logs/install.log
- Patch (if any): patch/${MODULE}.patch
EOFSTATUS
```

### Step 5: Update Port Queue

**Manual update** (automated by `port_addon.sh`):

```bash
# Update status in config/oca/port_queue.yml
yq -i ".priorities.P0.modules[] |= (select(.name == \"${MODULE}\") | .status = \"completed\")" config/oca/port_queue.yml

# Add to port_log
cat >> config/oca/port_queue.yml << EOFLOG
  - module: ${MODULE}
    status: completed
    timestamp: ${TIMESTAMP}
    evidence: ${EVIDENCE_DIR}
    notes: "Automated port via oca-port, smoke tests passed"
EOFLOG
```

### Step 6: Commit & Push

```bash
# Create commit
git add addons/oca/${REPO}/${MODULE}/
git add config/oca/port_queue.yml
git add web/docs/evidence/${TIMESTAMP}/

git commit -m "chore(oca): port ${MODULE} from 18.0 to 19.0

- Tool: oca-port CLI
- Status: smoke tests passed
- Evidence: ${EVIDENCE_DIR}
- Upstream: OCA/${REPO}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to feature branch
git push origin feat/oca-porting-pipeline
```

### Step 7: Upstream PR (Optional - for stable ports)

```bash
# After local validation, submit to OCA
cd addons/oca/${REPO}
git remote add upstream https://github.com/OCA/${REPO}.git
git fetch upstream

# Create OCA-compatible branch
git checkout -b 19.0-mig-${MODULE}
git push origin 19.0-mig-${MODULE}

# Create PR via gh CLI
gh pr create \
  --repo OCA/${REPO} \
  --base 19.0 \
  --head Insightpulseai:19.0-mig-${MODULE} \
  --title "[MIG] ${MODULE}: Migration to 19.0" \
  --body "Automated migration from 18.0 to 19.0 using oca-port.

**Status**: Smoke tests passed (load + install)
**Evidence**: [link to evidence directory]

Resolves #[issue number if exists]"
```

---

## Dependency Resolution

**Rule**: Port dependencies BEFORE dependent modules.

**Example dependency chain**:

```
server_environment (no deps) → PORT FIRST
    ↓
web_environment_ribbon (depends on server_environment) → PORT SECOND
```

**From port_queue.yml**:

```bash
# Check dependencies
yq '.priorities.P0.modules[] | select(.name == "web_environment_ribbon") | .depends' config/oca/port_queue.yml
# Output: [server_environment]

# Verify dependency ported
yq '.port_log[] | select(.module == "server_environment") | .status' config/oca/port_queue.yml
# Expected: completed
```

**If dependency not ported**: Port dependency first, then retry.

---

## Troubleshooting

### Issue: `oca-port` fails with "No migration found"

**Cause**: Module not in OpenUpgrade migration database.

**Solution**: Manual migration required.

```bash
# 1. Clone module manually
git clone https://github.com/OCA/${REPO}.git /tmp/${REPO}
cd /tmp/${REPO}
git checkout -b 19.0-mig-${MODULE} origin/18.0

# 2. Manual changes
# - Update __manifest__.py version to 19.0.1.0.0
# - Fix API changes (consult Odoo 19.0 migration guide)
# - Test locally

# 3. Copy to addons/oca/
cp -r ${MODULE} /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/addons/oca/${REPO}/

# 4. Proceed with smoke tests (Step 3)
```

### Issue: Module install fails

**Cause**: Dependency module missing or API incompatibility.

**Diagnosis**:

```bash
# Check install log for errors
grep "ERROR" web/docs/evidence/${TIMESTAMP}/oca-port-${MODULE}/logs/install.log

# Common patterns:
# - "No module named 'odoo.addons.xxx'" → Missing dependency
# - "AttributeError: 'xxx' object has no attribute 'yyy'" → API change
```

**Solutions**:

1. **Missing dependency**: Port dependency first
2. **API incompatibility**: Consult Odoo 19.0 changelog, manual fix required

### Issue: Python syntax errors

**Cause**: Python 3.12 compatibility issue.

**Diagnosis**:

```bash
python3 -m py_compile addons/oca/${REPO}/${MODULE}/**/*.py
# Shows exact file + line number of error
```

**Common fixes**:

- Replace `async` variable names (now reserved keyword)
- Update deprecated imports (e.g., `collections.Iterable` → `collections.abc.Iterable`)
- Fix f-string syntax incompatibilities

---

## Acceptance Checklist

Before marking module as "completed" in port_queue.yml:

- [ ] `oca-port` completed without errors (or manual migration documented)
- [ ] Module directory exists in `addons/oca/<repo>/<module>/`
- [ ] `__manifest__.py` version is `19.0.x.y.z`
- [ ] `python3 -m py_compile` passes for all `.py` files
- [ ] Module loads in Odoo shell: `env['ir.module.module'].search([('name', '=', '${MODULE}')])`
- [ ] Module installs: `./scripts/odoo_module_install.sh ${MODULE}` succeeds
- [ ] Evidence directory created with logs
- [ ] `config/oca/port_queue.yml` updated with status
- [ ] Commit created and pushed

**Optional (for stable ports)**:

- [ ] Functional tests pass (if test suite exists)
- [ ] PR submitted to OCA upstream

---

## Batch Porting (Multiple Modules)

**For modules with no dependencies**:

```bash
# Port all P0 modules with no dependencies in parallel
for module in server_environment component account_statement_import_base queue_job base_tier_validation base_exception mail_tracking fetchmail_notify_error_to_sender mail_debrand; do
  echo "Porting ${module}..."
  ./scripts/oca/port_addon.sh ${module} &
done
wait
```

**Note**: Only parallelize modules with `depends: []` in port_queue.yml.

---

## Performance Metrics

**Target timeline** (40 modules):

- **P0 (15 modules)**: 5-7 days (accounting for dependencies)
- **P1 (19 modules)**: 10-14 days
- **P2 (6 modules)**: 3-4 days

**Total**: 4-6 weeks

**Throughput**: 1-2 modules per day (average, including testing)

---

## References

- OCA porting guide: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-X.0
- `oca-port` documentation: https://pypi.org/project/oca-port/
- OpenUpgrade project: https://github.com/OCA/OpenUpgrade
- Odoo 19.0 migration guide: https://www.odoo.com/documentation/19.0/developer/howtos/upgrade.html
