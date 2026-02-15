# restore-odoo-environment — Deterministic Odoo Environment Restoration

**Type**: Procedural
**Domain**: OdooOps.sh operational parity
**Cloudpepper Equivalent**: `odoo.sh restore` operation
**Evidence Directory**: `docs/evidence/<YYYYMMDD-HHMM>/restore/<run_id>/`

---

## Purpose

Restore Odoo environment from backup artifact with automatic pre-restore safety backup, integrity validation, and auto-rollback on failure. Implements Cloudpepper/Odoo.sh restore workflow with mandatory evidence trail and safety guarantees.

---

## Preconditions (9 Checks)

**MUST validate before execution. Fail fast if any check fails.**

1. **ops.projects row exists** for `project_id`
2. **ops.environments row exists** for `environment_id` and matches `project_id`
3. **Caller has restore permission** via `ops.user_has_permission(p_user_id, p_project_id, 'restore')`
4. **No concurrent runs** (deploy/restore/backup all blocked) — query `ops.runs` for active runs on same environment
5. **ops.artifacts row exists** for `artifact_id` and matches `environment_id`
6. **Artifact integrity verified** — checksums match metadata
7. **Sufficient disk space** — at least 2x artifact size available on target environment
8. **Target environment accessible** — can connect to PostgreSQL and filesystem
9. **Backup artifact metadata readable** — JSON metadata file exists and is valid

**Validation Script**: `scripts/odoo_preflight_restore.sh <environment_id> <artifact_id>`

---

## Inputs

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_id` | string | ✅ | - | ops.projects.project_id |
| `environment_id` | string | ✅ | - | ops.environments.environment_id |
| `artifact_id` | string | ✅ | - | ops.artifacts.artifact_id (backup to restore) |
| `restore_type` | enum | ❌ | `full` | `full` \| `db_only` \| `filestore_only` |
| `verify_post_restore` | boolean | ❌ | `true` | Run post-restore validation (7 checks) |
| `skip_confirmation` | boolean | ❌ | `false` | Skip human confirmation for production (NEVER true for prod) |
| `rollback_on_failure` | boolean | ❌ | `true` | Auto-rollback to pre_restore_backup on failure |

**Input Validation**:
- `restore_type` must be one of: `full`, `db_only`, `filestore_only`
- `skip_confirmation` MUST be `false` if environment type is `production`
- `artifact_id` must point to valid backup artifact (not a deployment artifact)

---

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | ops.runs.run_id for this restore operation |
| `status` | enum | `success` \| `failed` \| `rolled_back` |
| `evidence_dir` | string | `docs/evidence/<YYYYMMDD-HHMM>/restore/<run_id>/` |
| `pre_restore_backup_id` | string | ops.artifacts.artifact_id for emergency backup created before restore |

---

## Artifact Contract (MUST MATCH backup-odoo-environment)

Restore requires an input `backup_artifact` with the following minimum fields:

```json
{
  "artifact_id": "string",
  "created_at": "RFC3339",
  "source_env": {
    "name": "dev|staging|prod",
    "db": "odoo_*"
  },
  "db_dump": {
    "path": "string",
    "sha256": "string"
  },
  "filestore": {
    "path": "string",
    "sha256": "string"
  },
  "manifest": {
    "odoo_version": "19.0",
    "addons_hash": "sha256",
    "modules_installed": ["..."],
    "db_major_version": 16
  }
}
```

**Validation**: If any required field is missing → fail preconditions (Precondition #5: ops.artifacts row exists and matches environment_id).

**Compatibility**: This contract matches `backup-odoo-environment` output artifact structure. Any backup artifact created by that skill is guaranteed to be restorable by this skill.

---

## Idempotency Rules

**Restore Marker (Prevent Duplicate Restores)**:
- If `target_env` already contains a restore marker for the same `artifact_id`, the skill MUST short-circuit to validation-only mode.
- Restore marker location: `ops.runs` WHERE `operation_type='restore'` AND `status='success'` AND `metadata->>'artifact_id' = :artifact_id`
- Validation-only mode: Skip Steps 2-8, only run Step 9 (post-restore validation) and Step 10 (finalize)

**Rollback Marker (Prevent Rollback Loops)**:
- Rollback MUST NOT re-run if a rollback marker already exists for the same `failure_id`.
- Rollback marker location: `ops.runs` WHERE `operation_type='restore'` AND `status='rolled_back'` AND `metadata->>'original_run_id' = :failure_id`
- If rollback marker exists → log warning, update status to 'failed', skip rollback execution

**Implementation**:
```sql
-- Check for existing restore marker
SELECT run_id FROM ops.runs
WHERE environment_id = :environment_id
  AND operation_type = 'restore'
  AND status = 'success'
  AND metadata->>'artifact_id' = :artifact_id
LIMIT 1;

-- Check for existing rollback marker
SELECT run_id FROM ops.runs
WHERE environment_id = :environment_id
  AND operation_type = 'restore'
  AND status = 'rolled_back'
  AND metadata->>'original_run_id' = :failure_id
LIMIT 1;
```

**Safety**: Idempotency prevents accidental re-execution of successful restores and prevents infinite rollback loops.

---

## Execution Steps (ORDER IS MANDATORY)

**Critical**: These steps MUST execute in exact order. Never reorder, never skip.

### Step 1: Create ops run
```sql
INSERT INTO ops.runs (run_id, project_id, environment_id, operation_type, status, created_by, metadata)
VALUES (gen_run_id(), :project_id, :environment_id, 'restore', 'running', :user_id, jsonb_build_object(
  'artifact_id', :artifact_id,
  'restore_type', :restore_type,
  'verify_post_restore', :verify_post_restore,
  'rollback_on_failure', :rollback_on_failure
));
```

**Evidence**: `docs/evidence/<date>/restore/<run_id>/inputs.json`, `run_id.txt`

### Step 2: Verify artifact integrity (checksums, metadata)
- Fetch artifact metadata from ops.artifacts
- Download artifact files (db.dump, filestore.tar.zst, config_snapshot.json)
- Compute SHA256 checksums for all files
- Compare against metadata.checksums
- **Fail if any mismatch detected**

**Evidence**: `artifact_verification.json` with checksums and validation results

### Step 3: Pre-restore environment backup (emergency safety net)
- **MANDATORY**: Create full backup of current environment state before any restore operation
- Use backup-odoo-environment skill internally
- Store backup artifact ID in ops.runs.metadata.pre_restore_backup_id
- **This backup is the rollback target if restore fails**
- Wait for backup completion and integrity verification before proceeding

**Evidence**: `pre_restore_backup.json` with artifact_id and verification status

### Step 4: Quiesce environment (best-effort maintenance mode)
- Set environment to maintenance mode (if Odoo is running)
- Terminate active user sessions (best-effort, 30s timeout)
- Stop Odoo service gracefully
- Wait for all connections to close (timeout: 60s)
- **Do NOT fail restore if quiesce fails** — log warning and continue

**Evidence**: `quiesce_status.json` with maintenance mode status, active sessions terminated, stop duration

### Step 5: Restore database (pg_restore from db.dump)
- Drop existing database (if exists)
- Create new database with same encoding/locale
- Run `pg_restore -Fc -d <database> <artifact>/db.dump`
- Verify restore exit code
- Compute checksum of restored database dump (pg_dump -Fc | sha256sum)
- **Trigger rollback if restore fails**

**Evidence**: `db_restore.log`, `db_restore_duration.json`, `db_restore_checksum_verification.json`

### Step 6: Restore filestore (extract from filestore.tar.zst)
- Remove existing filestore directory
- Extract `tar -I zstd -xf <artifact>/filestore.tar.zst -C <odoo_data_dir>`
- Verify extraction exit code
- Compute directory tree checksum (find + sha256sum)
- **Trigger rollback if extraction fails**

**Evidence**: `filestore_restore.log`, `filestore_restore_duration.json`, `filestore_restore_checksum_verification.json`

### Step 7: Restore configuration snapshot (compare + flag mismatches)
- Load config_snapshot.json from artifact
- Compare with current environment configuration
- **Log mismatches** (e.g., db_host changed, filestore path different)
- **Do NOT apply config changes** — this is informational only
- Flag any critical mismatches (encryption keys, database credentials)

**Evidence**: `config_snapshot.json`, `config_comparison.json`

### Step 8: Restart Odoo (graceful, wait for health check)
- Start Odoo service
- Wait for HTTP health check (timeout: 120s)
- Verify database connection
- Exit maintenance mode
- **Trigger rollback if restart fails or health check times out**

**Evidence**: `odoo_restart.log`, `restart_duration.json`

### Step 9: Post-restore validation (7 checks: registry, migrations, modules, data samples, filestore, syntax)
**Only if `verify_post_restore=true`**

1. **Registry Consistency**: Verify ir.model.data entries match module manifests
2. **Migration Status**: Check ir.module.module for expected installed state
3. **Module Integrity**: Verify all expected modules are installed and up-to-date
4. **Data Samples**: Query 5 random records from key tables (res.partner, res.users, account.move)
5. **Filestore Accessibility**: Verify filestore attachments are readable
6. **Syntax Validation**: Run `odoo-bin --test-enable --stop-after-init` (dry-run)
7. **Log Analysis**: Scan Odoo logs for ERROR/CRITICAL entries post-restore

**Trigger rollback if any validation fails**

**Evidence**: `validation_report.json` with pass/fail status for each check

### Step 10: Finalize run (success|failed|rolled_back with auto-rollback on failure)
**Success Path**:
```sql
UPDATE ops.runs SET status = 'success', completed_at = NOW(), evidence_dir = :evidence_dir
WHERE run_id = :run_id;
```

**Failure Path** (if `rollback_on_failure=true`):
1. Log failure reason to ops.run_events
2. Trigger restore from pre_restore_backup_id (recursive call with rollback_on_failure=false)
3. Update ops.runs status to 'rolled_back'
4. **Preserve both failure evidence and rollback evidence**

**Evidence**: `final_status.json` with status, completion time, rollback details (if applicable)

---

## Evidence Outputs (15 Required Files)

**MANDATORY**: All files MUST be created in `docs/evidence/<YYYYMMDD-HHMM>/restore/<run_id>/`

1. **inputs.json** — All input parameters (restore_type, artifact_id, etc.)
2. **run_id.txt** — ops.runs.run_id for this operation
3. **artifact_verification.json** — Checksum validation results
4. **pre_restore_backup.json** — Emergency backup artifact_id and status
5. **quiesce_status.json** — Maintenance mode, session termination, stop duration
6. **db_restore.log** — pg_restore output (stdout + stderr)
7. **db_restore_duration.json** — Restore start/end time, duration
8. **db_restore_checksum_verification.json** — Post-restore database checksum
9. **filestore_restore.log** — tar extraction output
10. **filestore_restore_duration.json** — Extraction start/end time, duration
11. **filestore_restore_checksum_verification.json** — Directory tree checksum
12. **config_snapshot.json** — Config from artifact
13. **config_comparison.json** — Current vs artifact config diff
14. **odoo_restart.log** — Service restart output
15. **validation_report.json** — Post-restore validation results (if enabled)
16. **final_status.json** — Operation outcome, rollback details

**Secret Redaction**: All evidence files MUST redact passwords, tokens, API keys. Use `[REDACTED]` placeholder.

---

## Non-Negotiables (8 Rules)

1. **Never restore to production without explicit confirmation** (`skip_confirmation=false` for prod)
2. **Pre-restore backup MUST be created and verified first** (Step 3 is mandatory)
3. **Artifact integrity checks mandatory** (bad checksums = FAIL)
4. **Auto-rollback to pre_restore_backup on failure** (if `rollback_on_failure=true`)
5. **Evidence mandatory** (missing evidence = FAIL)
6. **Step order mandatory** (no reorder/skip)
7. **No state-changing local SLMs** (see `docs/agents/LOCAL_LLM_ROUTING.md`)
8. **Secret redaction in all evidence files** (passwords, tokens, keys)

---

## Guardrails (6 Required)

**Enforced via `agents/registry/odoo_skills.yaml` and validated by `tests/test_skill_registry.py`**

1. **`forbid_parallel_deploy_restore: true`** — Block concurrent deploy/restore/backup on same environment
2. **`prod_requires_human_confirmation: true`** — Production restores require `skip_confirmation=false`
3. **`pre_restore_backup_mandatory: true`** — Step 3 cannot be skipped
4. **`redact_secrets_in_evidence: true`** — All evidence files must redact sensitive data
5. **`integrity_checks_required: true`** — Artifact checksums must be verified before restore
6. **`rollback_on_failure_default: true`** — Default to auto-rollback unless explicitly disabled

---

## Rollback Strategy

**Auto-Rollback Trigger Conditions**:
- Database restore failure (Step 5)
- Filestore restore failure (Step 6)
- Odoo restart failure (Step 8)
- Health check timeout (Step 8)
- Validation failure (Step 9, if enabled)

**Rollback Workflow**:
1. Log failure event to ops.run_events with full context
2. Call restore-odoo-environment recursively with:
   - `artifact_id = pre_restore_backup_id`
   - `rollback_on_failure = false` (prevent rollback loops)
   - `verify_post_restore = false` (speed up rollback)
3. Update original ops.runs status to 'rolled_back'
4. Preserve both failure evidence and rollback evidence directories

**Rollback Prevention**:
- Only 1 level of rollback allowed (no recursive rollbacks)
- Pre-restore backup creation is atomic and verified
- Rollback uses same deterministic restore workflow

---

## Example Usage

**Full Restore with Validation**:
```yaml
project_id: "proj_abc123"
environment_id: "env_staging_xyz"
artifact_id: "artifact_backup_20260215_1430"
restore_type: "full"
verify_post_restore: true
rollback_on_failure: true
```

**Database-Only Restore (Skip Filestore)**:
```yaml
project_id: "proj_abc123"
environment_id: "env_dev_local"
artifact_id: "artifact_backup_20260215_1200"
restore_type: "db_only"
verify_post_restore: false
rollback_on_failure: true
```

**Production Restore (Requires Confirmation)**:
```yaml
project_id: "proj_production"
environment_id: "env_prod_main"
artifact_id: "artifact_backup_20260214_2300"
restore_type: "full"
skip_confirmation: false  # MANDATORY for production
verify_post_restore: true
rollback_on_failure: true
```

---

## Validation Commands

**Pre-flight Check**:
```bash
./scripts/odoo_preflight_restore.sh env_staging_xyz artifact_backup_20260215_1430
```

**Integrity Verification**:
```bash
./scripts/verify_artifact_integrity.sh artifact_backup_20260215_1430
```

**Post-Restore Validation**:
```bash
./scripts/odoo_validate_environment.sh env_staging_xyz
```

---

## Related Skills

- **backup-odoo-environment** — Creates artifacts for restore
- **deploy-odoo-modules-git** — Code deployment (different from data restore)
- **promote-staging-to-prod** — Uses restore internally for blue-green deployment

---

## Success Criteria

✅ **Restore Successful When**:
1. All 10 execution steps completed without errors
2. All 15 evidence files created with valid content
3. Post-restore validation passed (if enabled)
4. ops.runs status updated to 'success'
5. Environment health check passing
6. Odoo accessible and functional

❌ **Restore Failed When**:
1. Pre-restore backup creation failed
2. Artifact integrity checks failed
3. Database or filestore restore failed
4. Odoo restart or health check failed
5. Post-restore validation failed
6. Rollback triggered and completed (status: 'rolled_back')

---

**Determinism**: Every restore operation with same inputs produces identical results and evidence structure.
**Audit Trail**: Complete evidence chain from artifact verification through final status.
**Safety**: Mandatory pre-restore backup + auto-rollback ensures recoverability.
