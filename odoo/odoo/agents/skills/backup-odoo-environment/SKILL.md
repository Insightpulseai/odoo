# SKILL: Backup Odoo Environment

## Skill ID

backup-odoo-environment

## Skill Type

Procedural (Deterministic)

## Purpose

Create an audit-grade backup of an Odoo environment (database + filestore + config snapshot), store as an artifact, and record evidence + run events.

## Preconditions (MUST all hold)

1. ops.projects row exists for project_id
2. ops.environments row exists for environment_id and belongs to project_id
3. Caller has backup permission for project_id via ops.user_has_permission()
4. No concurrent running ops.runs for environment_id of type deploy/restore/backup
5. Target runtime executor can access DB + filestore + configs for the environment
6. Sufficient storage quota available for estimated backup size

## Inputs (required)

project_id: string
environment_id: string
backup_type: full|db_only|filestore_only
retention_policy:
daily: int # default 7
weekly: int # default 4
monthly: int # default 3
label: string|null # optional human label

## Outputs (required)

run_id: string
artifact_id: string
status: success|failed
evidence_dir: string # docs/evidence/<YYYY-MM-DD>/backup/<run_id>/

## Non-negotiables

- No backups during deploy/restore runs (hard fail)
- Evidence artifacts are mandatory; missing evidence => FAIL
- Backups must be integrity-checked (checksums + restore viability checks for DB dumps)
- Never store secrets in evidence outputs (redact)
- Step order is mandatory; do not reorder or skip

## Execution Steps (ORDER IS MANDATORY)

### 1) Create ops run

- Insert ops.runs(status=queued, type=backup_environment, payload=<inputs>)
- Emit run_id

### 2) Discover environment runtime bindings

- Resolve: DB connection (host/port/db/user/sslmode) and filestore path/volume binding
- Capture _redacted_ binding summary in evidence (no passwords/tokens)

### 3) Quiesce writes (best-effort, bounded)

- Put Odoo into “backup-safe mode” if supported (maintenance/drain queue)
- Wait up to N seconds; record whether quiesce succeeded
- If cannot quiesce: continue but mark run_events as degraded_mode=true

### 4) Export database (if backup_type includes DB)

- Prefer pg_dump in custom format (-Fc) for speed/size
- Produce: db.dump
- Produce: db.dump.sha256
- Produce: db.dump.meta.json (size, pg_dump version, db name, started_at, finished_at)

### 5) Archive filestore (if backup_type includes filestore)

- Tar+compress filestore directory / volume mount
- Produce: filestore.tar.zst (or equivalent)
- Produce: filestore.tar.zst.sha256
- Produce: filestore.meta.json (size, path fingerprint, started_at, finished_at)

### 6) Config snapshot (always)

- Capture odoo.conf (redacted), addons list, installed modules list, git commit of repo if applicable
- Produce: config_snapshot.json (must redact secrets)

### 7) Upload artifact + register ops.artifacts

- Upload backup bundle to artifact storage
- Insert ops.artifacts(row) with pointers (uri, checksums, sizes, backup_type)
- Emit artifact_id

### 8) Retention pruning (7/4/3)

- Evaluate prior backups for this environment_id
- Delete/prune older artifacts beyond retention buckets
- Record pruned artifact ids in run_events + evidence

### 9) Finalize run

- ops.runs.status=success|failed
- ops.run_events(event_type=backup_completed, payload={artifact_id,status,degraded_mode,...})

## Evidence Outputs (REQUIRED)

Write to:
docs/evidence/<YYYY-MM-DD>/backup/<run_id>/
Must include:

- inputs.json
- runtime_bindings_redacted.json
- quiesce_status.json
- db.dump.meta.json (if db)
- db.dump.sha256 (if db)
- filestore.meta.json (if filestore)
- filestore.tar.zst.sha256 (if filestore)
- config_snapshot.json
- artifact_registration.json (artifact_id + uri + checksums)
- retention_prune.json
- final_status.json

Missing evidence => FAIL
