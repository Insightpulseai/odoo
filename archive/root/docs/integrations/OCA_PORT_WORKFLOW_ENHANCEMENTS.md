# OCA Module Porting Workflow Enhancements

> Production-ready OCA module porting automation with comprehensive error handling, rollback procedures, and Plane integration

**Status**: ✅ Production Ready
**Last Updated**: 2026-03-05
**Version**: 2.0.0

---

## Overview

This document describes the enhanced OCA module porting workflow that provides:

1. **Comprehensive OCA Compliance Validation**
2. **Production-Ready Error Handling**
3. **Automated Rollback Procedures**
4. **Bidirectional Plane Integration**
5. **Complete Integration Test Suite**

---

## Architecture Changes

### Before (v1.0)
```
User triggers workflow
    ↓
Clone OCA repos
    ↓
Run oca-port
    ↓
Basic manifest validation
    ↓
Create PR
    ↓
Create Plane issue (create-only)
    ↓
❌ If anything fails → manual cleanup required
```

### After (v2.0)
```
User triggers workflow
    ↓
Input validation & duplicate check
    ↓
Clone OCA repos (with 3-attempt retry)
    ↓
Create backup BEFORE porting
    ↓
Run oca-port (comprehensive logging)
    ↓
Enhanced OCA compliance validation (15+ checks)
    ↓
Pre-commit hooks validation
    ↓
Odoo tests (with skip option)
    ↓
    ├─ Success → Create PR + Update Plane issue + Update port queue
    └─ Failure → Automated rollback + Evidence collection + Notify team
```

---

## Components

### 1. Enhanced OCA Compliance Validator

**File**: `scripts/oca/validate_oca_compliance.py`

**Validation Categories** (15+):

| Category | Checks |
|----------|--------|
| Module Structure | Required files (__manifest__.py, __init__.py, README) |
| Manifest | 8 required keys + 7 optional keys, version format, license |
| Python Syntax | Syntax errors, deprecated API patterns (6 patterns) |
| Dependencies | Circular deps, common misspellings |
| Security | security/ directory, ir.model.access.csv integrity |
| Pre-commit | Hook availability and compliance |
| License | LICENSE/COPYING file presence |
| Data Files | XML/CSV syntax and manifest references |

**Deprecated API Patterns Detected**:
- `@api.one` decorator
- `@api.v7` / `@api.v8` decorators
- `_columns` attribute
- `.sudo(user)` with parameter
- Obsolete translation patterns

**Exit Codes**:
- `0`: All validation passed
- `1`: Validation errors found (blocking)
- `2`: Script error (invalid arguments, missing dependencies)

**Usage**:
```bash
# Validate single module
./scripts/oca/validate_oca_compliance.py addons/oca/connector/component

# Validate multiple modules
for module in addons/oca/queue/*; do
    if [ -d "$module" ]; then
        ./scripts/oca/validate_oca_compliance.py "$module"
    fi
done
```

**Output Example**:
```
Validating OCA compliance for: queue_job
Module path: /Users/.../addons/oca/queue/queue_job

======================================================================
OCA COMPLIANCE VALIDATION SUMMARY
======================================================================
Module: queue_job
Path: /Users/.../addons/oca/queue/queue_job

⚠️  WARNINGS: 1
  [WARNING] SECURITY_ACCESS: ir.model.access.csv exists but has no access rules (security/ir.model.access.csv)

✅ No errors found (warnings present but non-blocking)
======================================================================
```

---

### 2. Enhanced GitHub Actions Workflow

**File**: `.github/workflows/oca-port-enhanced.yml`

**New Features**:

#### Input Validation & Duplicate Detection
```yaml
validate-input:
  - Module name format validation (lowercase + underscores only)
  - Check for duplicates in port queue
  - Verify module exists in target OCA repository
```

#### Retry Logic for Git Operations
```yaml
clone-repositories:
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_on: error
```

#### Transaction-Safe Porting
```yaml
1. Create backup BEFORE porting
2. Run oca-port with comprehensive logging
3. On success → proceed
4. On failure → trigger rollback job automatically
```

#### Comprehensive Evidence Collection
```yaml
Evidence artifacts (90-day retention):
- Port logs: oca-port-{module}.log
- Validation reports: validation-report.txt
- Pre-commit logs: pre-commit.log
- Test logs: odoo-test-{module}.log
- Rollback summaries: rollback-summary.txt
```

#### Automated Rollback Job
```yaml
rollback-on-failure:
  triggers: port failure OR test failure
  actions:
    - Restore module from backup
    - Create rollback evidence
    - Notify team with failure details
    - Preserve logs for debugging
```

#### Enhanced Plane Integration
```yaml
notify-plane:
  features:
    - Check for existing issue (avoid duplicates)
    - Update existing issue instead of creating new
    - Include PR links and evidence references
    - Proper state transitions (pending → in_progress → done)
    - Label management (oca, module-port, automation)
```

#### Port Queue Auto-Update
```yaml
update-port-queue:
  on_success:
    - Update module status to 'completed'
    - Add port_log entry with timestamp
    - Include PR number and URL
    - Reference evidence artifacts
    - Commit changes to main branch
```

---

### 3. Integration Test Suite

**File**: `scripts/oca/test_oca_port_workflow.sh`

**Test Scenarios**:

| Test # | Name | Purpose | Validations |
|--------|------|---------|-------------|
| 1 | Input Validation | Module name format | Regex matching, error detection |
| 2 | Repository Cloning | Retry logic | 3-attempt retry, module existence |
| 3 | OCA Compliance | Validation logic | Valid/invalid manifest handling |
| 4 | Backup & Rollback | Restore procedures | Backup integrity, restoration |
| 5 | Evidence Collection | Log generation | File creation, content validation |
| 6 | Port Queue Update | YAML manipulation | Status updates, log entries |
| 7 | Dependency Resolution | Circular deps | Detection accuracy |

**Running Tests**:
```bash
# Run all tests
./scripts/oca/test_oca_port_workflow.sh

# Test specific module
./scripts/oca/test_oca_port_workflow.sh queue_job queue

# View results
cat test-results/oca-port-workflow/test-summary.txt
```

**Expected Output**:
```
=========================================
Test 1: Input Validation
=========================================
[INFO] Testing input validation...
[INFO] ✓ Invalid module name detected correctly
[INFO] ✓ Valid module name accepted
[INFO] ✅ PASSED: Input Validation

...

=========================================
TEST SUMMARY
=========================================
Total Tests: 7
Passed:      7
Failed:      0

[INFO] ✅ All tests passed!
```

---

## Deployment Guide

### Step 1: Configure GitHub Secrets

Go to repository `Settings → Secrets → Actions` and add:

```bash
# Deployment Server (if using self-hosted runner)
SSH_PRIVATE_KEY=[SSH key for deployment server]

# Odoo Credentials
ODOO_URL=https://erp.insightpulseai.com
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=[from Supabase Vault]

# Plane API (Required for Plane integration)
PLANE_API_URL=https://plane.insightpulseai.com/api/v1
PLANE_API_KEY=[from Plane profile → API Tokens]
PLANE_WORKSPACE_SLUG=fin-ops
PLANE_BIR_PROJECT_ID=dd0b3bd5-43e8-47ab-b3ad-279bb15d4778

# Slack (Optional - for notifications)
SLACK_BOT_TOKEN=xoxb-[your-bot-token]

# n8n (Optional - for workflow orchestration)
N8N_WEBHOOK_URL=https://n8n.insightpulseai.com/webhook
N8N_WEBHOOK_SECRET=[from n8n settings]
```

### Step 2: Verify Local Tools

```bash
# Check Python version (3.12+ required)
python3 --version

# Install oca-port CLI
pip install oca-port

# Install pre-commit
pip install pre-commit

# Install validation dependencies
pip install pylint-odoo

# Verify installation
oca-port --version
pre-commit --version
```

### Step 3: Run Integration Tests

```bash
# Navigate to repository root
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Run test suite
./scripts/oca/test_oca_port_workflow.sh

# Verify all tests pass
# Expected: Total Tests: 7, Passed: 7, Failed: 0
```

### Step 4: Test Enhanced Workflow

**Recommended Test Module**: `queue_job` (P0, already ported, safe to re-port)

```bash
# Trigger workflow via GitHub UI:
# Actions → OCA Module Port to 19.0 (Enhanced)

# Inputs:
module_name: queue_job
source_version: 18.0
target_version: 19.0
oca_repository: queue
skip_tests: false
create_plane_issue: true
```

**Expected Behavior**:
1. ✅ Input validation passes
2. ✅ Duplicate check detects existing module (warning, proceeds)
3. ✅ OCA repos cloned successfully
4. ✅ Backup created before porting
5. ✅ oca-port completes successfully
6. ✅ OCA compliance validation passes
7. ✅ Pre-commit hooks applied
8. ✅ Odoo tests pass
9. ✅ PR created with evidence links
10. ✅ Plane issue created/updated
11. ✅ Port queue updated with completion

**Artifacts to Review**:
- `evidence-logs-{PORT_ID}` - Port and validation logs
- `test-logs-{PORT_ID}` - Odoo test outputs
- `ported-module-{PORT_ID}` - Successfully ported module

---

## Workflow Usage

### Scenario 1: Port New Module (Happy Path)

```yaml
# Inputs
module_name: purchase_tier_validation
source_version: 18.0
target_version: 19.0
oca_repository: purchase-workflow
skip_tests: false
create_plane_issue: true

# Expected Flow
✅ Input validation → ✅ Clone repos → ✅ Backup → ✅ Port → ✅ Validate
→ ✅ Tests → ✅ PR created → ✅ Plane updated → ✅ Queue updated
```

### Scenario 2: Port Fails (Automatic Rollback)

```yaml
# Inputs
module_name: problematic_module
source_version: 18.0
target_version: 19.0
oca_repository: some-repo
skip_tests: false

# Flow
✅ Input validation → ✅ Clone repos → ✅ Backup → ❌ Port fails
→ 🔄 Rollback triggered → ✅ Backup restored → ✅ Evidence collected
→ 📧 Team notified → 🛑 Workflow stops (no PR created)

# Artifacts Available
- rollback-evidence-{PORT_ID}/rollback-summary.txt
- evidence-logs-{PORT_ID}/oca-port-{module}.log
- evidence-logs-{PORT_ID}/port-failure-summary.txt
```

### Scenario 3: Tests Fail (Rollback + Debug Evidence)

```yaml
# Inputs
module_name: test_failing_module
source_version: 18.0
target_version: 19.0
oca_repository: some-repo
skip_tests: false  # Tests will run and fail

# Flow
✅ Input validation → ✅ Clone → ✅ Backup → ✅ Port → ✅ Validate
→ ❌ Tests fail → 🔄 Rollback → ✅ Evidence preserved
→ 📧 Team notified with test logs

# Available for Debugging
- test-logs-{PORT_ID}/odoo-test-{module}.log (full test output)
- evidence-logs-{PORT_ID}/validation-report.txt
- rollback-evidence-{PORT_ID}/rollback-summary.txt
```

### Scenario 4: Skip Tests (Fast Iteration)

```yaml
# Inputs (for debugging/development)
module_name: experimental_module
source_version: 18.0
target_version: 19.0
oca_repository: some-repo
skip_tests: true  # Skip Odoo tests for faster iteration

# Flow
✅ Input validation → ✅ Clone → ✅ Backup → ✅ Port → ✅ Validate
→ ⏭️  Tests skipped → ✅ PR created → ✅ Plane updated

# Use Case
- Initial porting exploration
- Debugging port issues
- Iterating on oca-port command parameters
```

---

## Plane Integration Details

### Issue Lifecycle

```
New Port Request
    ↓
[Plane Issue Created]
    State: backlog
    Labels: [oca, module-port, automation]
    Priority: medium
    ↓
Workflow Triggered
    ↓
[Plane Issue Updated]
    State: in_progress
    Description: Added port evidence
    ↓
    ├─ Success → State: in_progress (awaiting PR review)
    └─ Failure → State: backlog (with error details)
    ↓
PR Merged
    ↓
[Manual Update Required]
    State: done
```

### Issue Detection Logic

```python
# Check for existing issue
EXISTING_ISSUE = curl "https://plane.insightpulseai.com/api/v1/.../issues/"
    | jq '.results[] | select(.name | contains("module_name")) | .id'

if EXISTING_ISSUE exists:
    # Update existing issue (PATCH)
    - Add PR link to description
    - Update state to in_progress
    - Add evidence references
else:
    # Create new issue (POST)
    - Set initial state: backlog
    - Add all metadata
    - Include workflow run link
```

### Plane API Calls

**Create Issue**:
```bash
curl -X POST \
  "https://plane.insightpulseai.com/api/v1/workspaces/fin-ops/projects/{project_id}/issues/" \
  -H "X-API-Key: {api_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "[OCA Port] queue_job (18.0 → 19.0)",
    "description_html": "<p>Automated OCA module port</p>",
    "state": "backlog",
    "priority": "medium",
    "labels": ["oca", "module-port", "automation"]
  }'
```

**Update Issue**:
```bash
curl -X PATCH \
  "https://plane.insightpulseai.com/api/v1/workspaces/fin-ops/projects/{project_id}/issues/{issue_id}/" \
  -H "X-API-Key: {api_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "in_progress",
    "description_html": "<p><strong>Port Status</strong>: Completed ✅</p><p><strong>PR</strong>: <a href=\"{pr_url}\">#{pr_number}</a></p>"
  }'
```

---

## Error Handling Matrix

| Error Type | Detection | Response | Evidence | Recovery |
|------------|-----------|----------|----------|----------|
| Invalid module name | Input validation job | Fail fast (exit 1) | None | Fix input, re-run |
| Module not in source repo | Clone verification | Fail fast (exit 1) | Clone logs | Verify repo + module name |
| oca-port failure | Port exit code ≠ 0 | Trigger rollback job | port-failure-summary.txt, full logs | Review logs, fix issues, re-run |
| OCA compliance failure | Validation script exit 1 | Trigger rollback job | validation-report.txt | Fix validation errors, re-run |
| Odoo test failure | Test exit code ≠ 0 | Trigger rollback job | odoo-test-{module}.log | Debug tests, fix module, re-run |
| Git clone failure | Retry exhausted (3 attempts) | Fail fast (exit 1) | Retry logs | Check network, repo availability |
| Plane API failure | HTTP error | Continue (non-blocking) | API response | Manual Plane issue creation |

---

## Troubleshooting

### Problem: oca-port fails with "module not found"

**Symptoms**:
```
ERROR: Module not found in source repository
Repository: OCA/some-repo
Branch: 18.0
Module: module_name
```

**Diagnosis**:
1. Verify module exists on upstream OCA repository
2. Check correct repository name (common misspellings)
3. Confirm source version has the module

**Fix**:
```bash
# Check upstream manually
git clone -b 18.0 --single-branch https://github.com/OCA/{repo}.git /tmp/check
ls /tmp/check/  # Verify module directory exists
```

---

### Problem: OCA compliance validation fails

**Symptoms**:
```
[ERROR] MANIFEST_VERSION: Version must start with 19.0. (got: 18.0.1.0.0)
```

**Diagnosis**: oca-port didn't update version number

**Fix**:
1. Check oca-port logs in evidence artifacts
2. Manually update `__manifest__.py` version
3. Re-run validation:
```bash
./scripts/oca/validate_oca_compliance.py addons/oca/{repo}/{module}
```

---

### Problem: Rollback job cannot find backup

**Symptoms**:
```
⚠️  Backup not found - manual intervention may be required
```

**Diagnosis**: Backup artifact upload failed or expired

**Fix**:
1. Check workflow artifacts for `oca-repositories-{PORT_ID}`
2. If missing: re-run entire workflow (starts fresh)
3. If artifact expired (>30 days): manual module restoration required

---

### Problem: Plane issue creation fails

**Symptoms**:
```
curl: (7) Failed to connect to plane.insightpulseai.com
```

**Diagnosis**: Plane API unreachable or authentication failure

**Fix**:
1. Verify Plane is accessible: `curl -I https://plane.insightpulseai.com`
2. Check GitHub secrets: `PLANE_API_URL`, `PLANE_API_KEY`
3. Verify API key validity in Plane profile
4. Workflow continues even if Plane fails (non-blocking)

---

## Metrics & Monitoring

### Key Performance Indicators

| Metric | Target | Current | Measurement |
|--------|--------|---------|-------------|
| Port Success Rate | >90% | TBD | Successful ports / total attempts |
| Rollback Accuracy | 100% | TBD | Successful rollbacks / triggered rollbacks |
| OCA Compliance Pass Rate | >95% | TBD | Modules passing validation / total ports |
| Average Port Time | <10 min | TBD | Workflow duration (input → PR creation) |
| Test Pass Rate | >85% | TBD | Modules passing tests / total ports |

### Monitoring Dashboards

**GitHub Actions**:
- Workflow success/failure rate
- Average execution time per job
- Artifact retention usage

**Plane Integration**:
- Issues created vs updated
- Issue state distribution
- Average time to completion

---

## Future Enhancements

### Planned Improvements

1. **Parallel Module Porting**
   - Port multiple modules concurrently
   - Dependency-aware scheduling
   - Batch PR creation

2. **AI-Assisted Debugging**
   - Automatic analysis of port failure logs
   - Suggested fixes for common errors
   - Pattern recognition for deprecation warnings

3. **Progressive Port Queue Processing**
   - Automatic processing of pending modules
   - Priority-based scheduling (P0 → P1 → P2)
   - Dependency chain resolution

4. **Enhanced Plane Sync**
   - Webhook-based bidirectional sync
   - Automatic state updates on PR merge
   - Custom field synchronization

5. **Performance Optimization**
   - Cached OCA repository clones
   - Incremental oca-port (skip unchanged files)
   - Parallel test execution

---

## References

- [OCA oca-port Tool](https://github.com/OCA/oca-port)
- [OCA Development Guidelines](https://odoo-community.org/page/development-guidelines)
- [Odoo 18.0 Developer Documentation](https://www.odoo.com/documentation/19.0/developer)
- [Plane API Documentation](https://plane.so/docs/api)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

**Last Updated**: 2026-03-05
**Version**: 2.0.0
**Status**: Production Ready
**Maintainer**: Backend Architect Team
