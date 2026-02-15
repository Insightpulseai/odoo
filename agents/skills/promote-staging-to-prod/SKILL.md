# promote-staging-to-prod — Gated Blue-Green Promotion

**Type**: Procedural (Composite)
**Domain**: OdooOps.sh operational parity
**Cloudpepper Equivalent**: `odoo.sh promote` operation
**Evidence Directory**: `docs/evidence/<YYYYMMDD-HHMM>/promote/<run_id>/`

---

## Purpose

Promote staging environment to production using blue-green deployment strategy with automated rollback capability. Composes `backup-odoo-environment` and `restore-odoo-environment` skills to ensure zero-downtime cutover with safety guarantees.

---

## Preconditions (7 Checks)

**MUST validate before execution. Fail fast if any check fails.**

1. **ops.projects row exists** for `project_id`
2. **Staging environment successful** — latest deploy/restore on staging environment must have `status='success'`
3. **Same commit SHA** — staging and production must target the same git commit
4. **Caller has promote permission** via `ops.user_has_permission(p_user_id, p_project_id, 'promote')`
5. **No concurrent operations** on production environment
6. **Production environment accessible** — can connect to PostgreSQL and filesystem
7. **Sufficient disk space** — at least 3x current production size (blue + green + backups)

**Validation Script**: `scripts/odoo_preflight_promote.sh <project_id>`

---

## Inputs

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_id` | string | ✅ | - | ops.projects.project_id |
| `staging_env_id` | string | ✅ | - | ops.environments.environment_id (source) |
| `prod_env_id` | string | ✅ | - | ops.environments.environment_id (target) |
| `rollback_window_hours` | integer | ❌ | `24` | Hours to keep blue snapshot for rollback |
| `skip_smoke_tests` | boolean | ❌ | `false` | Skip smoke tests on green (NEVER true for production) |
| `auto_rollback_on_failure` | boolean | ❌ | `true` | Auto-rollback to blue if cutover fails |

**Input Validation**:
- `staging_env_id` and `prod_env_id` must belong to same `project_id`
- `skip_smoke_tests` MUST be `false` for production promotions
- `rollback_window_hours` must be >= 1 and <= 168 (7 days)

---

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | ops.runs.run_id for this promotion operation |
| `status` | enum | `success` \| `failed` \| `rolled_back` |
| `evidence_dir` | string | `docs/evidence/<YYYYMMDD-HHMM>/promote/<run_id>/` |
| `blue_backup_id` | string | Production snapshot (rollback target) |
| `green_artifact_id` | string | Staging snapshot promoted to production |
| `cutover_timestamp` | RFC3339 | When traffic switched to green |

---

## Execution Steps (ORDER IS MANDATORY)

**Critical**: These steps MUST execute in exact order. Never reorder, never skip.

### Step 1: Create ops run
```sql
INSERT INTO ops.runs (run_id, project_id, environment_id, operation_type, status, created_by, metadata)
VALUES (gen_run_id(), :project_id, :prod_env_id, 'promote', 'running', :user_id, jsonb_build_object(
  'staging_env_id', :staging_env_id,
  'rollback_window_hours', :rollback_window_hours,
  'skip_smoke_tests', :skip_smoke_tests,
  'auto_rollback_on_failure', :auto_rollback_on_failure
));
```

**Evidence**: `docs/evidence/<date>/promote/<run_id>/inputs.json`, `run_id.txt`

### Step 2: Create staging snapshot (artifact to promote)
- Call `backup-odoo-environment` skill on `staging_env_id`
- Wait for backup completion and integrity verification
- Store artifact_id as `green_artifact_id` in ops.runs.metadata
- **This artifact becomes the production candidate**

**Evidence**: `staging_snapshot.json` with artifact_id and checksums

### Step 3: Backup production (blue snapshot for rollback)
- Call `backup-odoo-environment` skill on `prod_env_id`
- Wait for backup completion and integrity verification
- Store artifact_id as `blue_backup_id` in ops.runs.metadata
- **This is the rollback target if promotion fails**

**Evidence**: `blue_backup.json` with artifact_id and checksums

### Step 4: Restore staging snapshot to production (green deployment)
- Call `restore-odoo-environment` skill on `prod_env_id` with `green_artifact_id`
- Use `verify_post_restore=true` for full validation
- Use `rollback_on_failure=false` (we handle rollback at promotion level)
- **This creates the new production environment (green)**

**Evidence**: `green_restore.json` with restore run_id and status

### Step 5: Run smoke tests on green
**Only if `skip_smoke_tests=false`**

Run 5 critical smoke tests:
1. **Health Check**: HTTP 200 on `/web/health`
2. **Database Connectivity**: Query `SELECT 1` succeeds
3. **Module Integrity**: All expected modules installed and loaded
4. **Filestore Accessibility**: Sample attachment retrieval succeeds
5. **User Authentication**: Test login succeeds

**Trigger rollback if any smoke test fails**

**Evidence**: `smoke_tests.json` with pass/fail status for each test

### Step 6: Switch traffic to green (cutover)
- Update environment routing/ingress to point to green deployment
- Record cutover timestamp in ops.runs.metadata
- **Production now serves from green (promoted staging snapshot)**

**Implementation**: Update load balancer, DNS, or reverse proxy configuration

**Evidence**: `cutover.json` with timestamp and routing config

### Step 7: Monitor green for stability (5-minute window)
- Monitor HTTP error rate (must be <1%)
- Monitor database connection errors (must be 0)
- Monitor Odoo process crashes (must be 0)
- **Trigger rollback if stability metrics fail**

**Evidence**: `stability_metrics.json` with error rates and metrics

### Step 8: Finalize promotion (success|failed|rolled_back)
**Success Path**:
```sql
UPDATE ops.runs SET status = 'success', completed_at = NOW(), evidence_dir = :evidence_dir
WHERE run_id = :run_id;

-- Schedule blue snapshot deletion after rollback window
INSERT INTO ops.scheduled_tasks (task_type, execute_at, metadata)
VALUES ('delete_backup', NOW() + INTERVAL ':rollback_window_hours hours',
        jsonb_build_object('artifact_id', :blue_backup_id));
```

**Failure Path** (if `auto_rollback_on_failure=true`):
1. Log failure reason to ops.run_events
2. Switch traffic back to blue (original production)
3. Delete green deployment
4. Update ops.runs status to 'rolled_back'
5. **Preserve both failure evidence and rollback evidence**

**Evidence**: `final_status.json` with status, completion time, rollback details (if applicable)

---

## Composition Model

This skill composes three core skills:

| Skill | Purpose | Invoked When |
|-------|---------|--------------|
| `backup-odoo-environment` | Create staging snapshot (green artifact) | Step 2 |
| `backup-odoo-environment` | Create production snapshot (blue rollback target) | Step 3 |
| `restore-odoo-environment` | Deploy staging snapshot to production (green) | Step 4 |

**Dependency Contract**: All composed skills MUST use the same artifact contract (backup-odoo-environment output → restore-odoo-environment input).

---

## Evidence Outputs (11 Required Files)

**MANDATORY**: All files MUST be created in `docs/evidence/<YYYYMMDD-HHMM>/promote/<run_id>/`

1. **inputs.json** — All input parameters (staging_env_id, prod_env_id, etc.)
2. **run_id.txt** — ops.runs.run_id for this operation
3. **staging_snapshot.json** — Green artifact_id and checksums
4. **blue_backup.json** — Blue backup artifact_id and checksums
5. **green_restore.json** — Restore run_id and status
6. **smoke_tests.json** — Smoke test results (if enabled)
7. **cutover.json** — Cutover timestamp and routing config
8. **stability_metrics.json** — 5-minute stability metrics
9. **rollback.json** — Rollback details (if triggered)
10. **final_status.json** — Operation outcome, timestamps
11. **promotion_summary.md** — Human-readable summary of promotion

**Secret Redaction**: All evidence files MUST redact passwords, tokens, API keys. Use `[REDACTED]` placeholder.

---

## Non-Negotiables (8 Rules)

1. **Staging must be successful first** (`prod_requires_staging_success` guardrail)
2. **Same commit SHA** (staging and prod must target identical git commit)
3. **Blue backup MUST be created and verified** (Step 3 is mandatory)
4. **Smoke tests required for production** (`skip_smoke_tests=false` for prod)
5. **Evidence mandatory** (missing evidence = FAIL)
6. **Step order mandatory** (no reorder/skip)
7. **No Enterprise modules** (`forbid_enterprise_modules` guardrail)
8. **Auto-rollback on failure** (unless explicitly disabled)

---

## Guardrails (4 Required)

**Enforced via `agents/registry/odoo_skills.yaml` and validated by `tests/test_skill_registry.py`**

1. **`prod_requires_staging_success: true`** — Block promotion if staging has failures
2. **`forbid_enterprise_modules: true`** — No proprietary modules in promoted artifact
3. **`rollback_default: true`** — Default to auto-rollback unless explicitly disabled
4. **`evidence_required: true`** — All 11 evidence files must be created

---

## Rollback Strategy

**Auto-Rollback Trigger Conditions**:
- Green restore failure (Step 4)
- Smoke test failure (Step 5)
- Cutover failure (Step 6)
- Stability metrics failure (Step 7)

**Rollback Workflow**:
1. Log failure event to ops.run_events with full context
2. Switch traffic back to blue (original production)
3. Delete green deployment (cleanup failed promotion)
4. Update ops.runs status to 'rolled_back'
5. Preserve both failure evidence and rollback evidence

**Rollback Prevention**:
- Blue backup verified before green deployment
- Rollback is a simple traffic switch (no restore needed)
- Original production (blue) remains untouched during promotion

---

## Blue-Green Deployment Model

```
┌─────────────────────────────────────────────────────────────┐
│ Production Environment (Before Promotion)                    │
│                                                              │
│  Traffic → Blue (Current Production)                         │
│           └─ Odoo 19.0 + Current Modules                    │
└─────────────────────────────────────────────────────────────┘

                           ▼ Promotion

┌─────────────────────────────────────────────────────────────┐
│ Production Environment (During Promotion)                    │
│                                                              │
│  Blue (Inactive, Rollback Target)   Green (New Production)  │
│  └─ Backup created ✓                └─ Staging snapshot     │
│                                        restored ✓            │
│                                      └─ Smoke tests ✓        │
│                                                              │
│  Traffic → Switch to Green                                  │
└─────────────────────────────────────────────────────────────┘

                           ▼ Success

┌─────────────────────────────────────────────────────────────┐
│ Production Environment (After Promotion)                     │
│                                                              │
│  Traffic → Green (New Production)                            │
│           └─ Promoted Staging Snapshot                      │
│                                                              │
│  Blue (Rollback Window: 24h default)                        │
│  └─ Deleted after rollback_window_hours                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Example Usage

**Standard Promotion (with smoke tests)**:
```yaml
project_id: "proj_abc123"
staging_env_id: "env_staging_xyz"
prod_env_id: "env_prod_main"
rollback_window_hours: 24
skip_smoke_tests: false
auto_rollback_on_failure: true
```

**Emergency Promotion (skip smoke tests, shorter rollback window)**:
```yaml
project_id: "proj_abc123"
staging_env_id: "env_staging_xyz"
prod_env_id: "env_prod_main"
rollback_window_hours: 4
skip_smoke_tests: true  # NOT RECOMMENDED for production
auto_rollback_on_failure: true
```

---

## Validation Commands

**Pre-flight Check**:
```bash
./scripts/odoo_preflight_promote.sh proj_abc123
```

**Staging Success Verification**:
```bash
./scripts/verify_staging_success.sh env_staging_xyz
```

**Post-Promotion Validation**:
```bash
./scripts/odoo_validate_environment.sh env_prod_main
```

---

## Related Skills

- **backup-odoo-environment** — Creates blue and green artifacts
- **restore-odoo-environment** — Deploys green to production
- **deploy-odoo-modules-git** — Code deployment (different from data promotion)

---

## Success Criteria

✅ **Promotion Successful When**:
1. All 8 execution steps completed without errors
2. All 11 evidence files created with valid content
3. Smoke tests passed (if enabled)
4. Stability metrics within thresholds
5. ops.runs status updated to 'success'
6. Production serving from green deployment
7. Blue snapshot scheduled for deletion after rollback window

❌ **Promotion Failed When**:
1. Staging environment not successful
2. Green restore failed
3. Smoke tests failed
4. Stability metrics failed
5. Rollback triggered and completed (status: 'rolled_back')

---

**Determinism**: Every promotion with same inputs produces identical blue-green deployment and evidence structure.
**Audit Trail**: Complete evidence chain from staging snapshot through cutover and stability monitoring.
**Safety**: Mandatory blue backup + instant rollback capability ensures zero-downtime deployments.
