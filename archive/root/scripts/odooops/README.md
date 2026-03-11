# OdooOps Shell Scripts - Integration Guide

Shell scripts for OdooOps Sh workflow lifecycle management integrated with Supabase ops.* schema.

## Overview

These scripts manage the complete lifecycle of OdooOps build/deploy runs:

1. **env_create.sh** - Queue a new run
2. **env_wait_ready.sh** - Poll run status until complete
3. **env_destroy.sh** - Cancel a running/queued run
4. **test_e2e.sh** - End-to-end test suite

## Architecture

**Database Integration**: All scripts interact with Supabase PostgreSQL via REST API:
- `ops.projects` - Project registry
- `ops.environments` - Environment configurations (dev, staging, prod)
- `ops.runs` - Main run queue and status tracking
- `ops.run_events` - Structured event logs for each run
- `ops.artifacts` - Build artifacts (Docker images, SBOMs, logs)

**State Machine**:
```
queued → claimed → running → success/failed/cancelled
```

## Prerequisites

Environment variables required (typically in `.env`):

```bash
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
```

## Scripts

### env_create.sh

**Purpose**: Insert a queued run into `ops.runs` table.

**Usage**:
```bash
./scripts/odooops/env_create.sh <project_id> <workflow_type> <git_ref> <commit_sha> [env_id]
```

**Arguments**:
- `project_id` - Project identifier (must exist in ops.projects)
- `workflow_type` - Workflow type: `build`, `deploy`, `test`
- `git_ref` - Git branch/tag: `main`, `feature/auth`, `release/1.0`
- `commit_sha` - Full 40-char commit SHA
- `env_id` - Environment: `dev`, `staging`, `prod` (default: `dev`)

**Example**:
```bash
# Queue a build for main branch
run_id=$(./scripts/odooops/env_create.sh \
  my-project \
  build \
  main \
  abc123def456789012345678901234567890abcd \
  dev)

echo "Created run: $run_id"
# Output: run-20260214-120000-abc123d
```

**Database Operations**:
1. Generates unique `run_id` with format: `run-YYYYMMDD-HHMMSS-<short-sha>`
2. Inserts row into `ops.runs` with status `queued`
3. Sets metadata: workflow_type, created_by, git_ref
4. Returns `run_id` for tracking

**Expected Output**:
```
run-20260214-120000-abc123d
```

**Error Handling**:
- Exits 1 if run creation fails
- Prints response body to stderr on error
- Validates run_id in response

---

### env_wait_ready.sh

**Purpose**: Poll `ops.runs` status until run reaches terminal state (success/failed/cancelled).

**Usage**:
```bash
./scripts/odooops/env_wait_ready.sh <run_id> [max_wait_seconds] [sleep_seconds]
```

**Arguments**:
- `run_id` - Run identifier from env_create.sh
- `max_wait_seconds` - Timeout in seconds (default: 1200 = 20 min)
- `sleep_seconds` - Polling interval (default: 5 seconds)

**Example**:
```bash
# Wait for run to complete (20 min timeout)
./scripts/odooops/env_wait_ready.sh run-20260214-120000-abc123d

# Custom timeout and poll interval
./scripts/odooops/env_wait_ready.sh run-20260214-120000-abc123d 600 2
```

**Database Operations**:
1. Queries `ops.runs` for current status
2. Queries `ops.run_events` for latest 5 log entries (displays progress)
3. On success: queries `ops.artifacts` for build output URL
4. Polls every `sleep_seconds` until terminal state or timeout

**Terminal States**:
- `success` - Exits 0, prints artifact URL or "success"
- `failed` - Exits 1, suggests checking ops.run_events
- `cancelled` - Exits 1, run was cancelled

**Non-Terminal States** (continues polling):
- `queued` - Waiting for worker
- `claimed` - Worker claimed, not started
- `running` - Actively executing

**Expected Output** (stderr):
```
Waiting for run run-20260214-120000-abc123d to complete (timeout: 1200s)...
Status: queued - waiting...
Recent logs:
[info] Run queued successfully
Status: claimed - waiting...
Recent logs:
[info] Worker worker-001 claimed run
[info] Starting build process
Status: running - waiting...
Recent logs:
[info] Building Docker image
[debug] Layer 1/5 complete
[info] Build complete, pushing to registry
Run completed successfully: run-20260214-120000-abc123d
```

**Expected Output** (stdout):
```
ghcr.io/org/repo:abc123d
```
or
```
success
```

**Error Cases**:
- Run not found: Exits 1
- Timeout: Exits 1 after max_wait_seconds
- Failed run: Exits 1, prints error guidance

---

### env_destroy.sh

**Purpose**: Cancel a queued or running run by updating status to `cancelled`.

**Usage**:
```bash
./scripts/odooops/env_destroy.sh <run_id>
```

**Arguments**:
- `run_id` - Run identifier to cancel

**Example**:
```bash
# Cancel a run
./scripts/odooops/env_destroy.sh run-20260214-120000-abc123d
# Output: cancelled:run-20260214-120000-abc123d
```

**Database Operations**:
1. Updates `ops.runs` row: `status = 'cancelled'`
2. Inserts event into `ops.run_events`:
   - level: `info`
   - message: "Run cancelled by env_destroy.sh"
   - payload: action, timestamp

**Expected Output**:
```
cancelled:run-20260214-120000-abc123d
```

**Use Cases**:
- Cancel stuck runs
- Stop long-running builds
- Clean up test runs
- Emergency stop during incidents

---

### test_e2e.sh

**Purpose**: End-to-end integration test suite for entire workflow lifecycle.

**Usage**:
```bash
./scripts/odooops/test_e2e.sh
```

**Test Coverage**:

1. **Project Setup** - Create test project in ops.projects
2. **Environment Setup** - Create test environment in ops.environments
3. **Run Creation** - Call env_create.sh, verify run_id format
4. **Status Verification** - Verify initial status is 'queued'
5. **Worker Claim** - Simulate worker claiming run
6. **Log Events** - Insert log events at different levels (info, debug, warn)
7. **Running State** - Mark run as running with started_at timestamp
8. **Artifact Storage** - Add Docker image artifact to ops.artifacts
9. **Success State** - Mark run as success with finished_at timestamp
10. **Wait Ready** - Test env_wait_ready.sh with completed run
11. **Cancellation** - Create run, cancel with env_destroy.sh
12. **Failure Detection** - Mark run as failed, verify env_wait_ready.sh detects it

**Example Output**:
```bash
$ ./scripts/odooops/test_e2e.sh

[TEST] Test 1: Create test project in ops.projects
[PASS] Project created successfully
[TEST] Test 2: Create test environment in ops.environments
[PASS] Environment created successfully
[TEST] Test 3: Create queued run using env_create.sh
[PASS] Run created with ID: run-20260214-120530-abc123d
[TEST] Test 4: Verify run status is 'queued'
[PASS] Run status is 'queued'
[TEST] Test 5: Simulate worker claiming run
[PASS] Run claimed by worker
[TEST] Test 6: Add log events to ops.run_events
[PASS] Log events created (3 total)
[TEST] Test 7: Mark run as running
[PASS] Run marked as running
[TEST] Test 8: Add artifact to ops.artifacts
[PASS] Artifact created: art-f47ac10b-58cc-4372-a567-0e02b2c3d479
[TEST] Test 9: Mark run as success
[PASS] Run marked as success
[TEST] Test 10: Test env_wait_ready.sh with completed run
[PASS] env_wait_ready.sh returned successfully
[TEST] Test 11: Create another run and cancel it
[PASS] Run cancelled successfully: run-20260214-120531-def456a
[PASS] Run status confirmed as cancelled
[TEST] Test 12: Create run, mark as failed, verify wait_ready detects it
[PASS] env_wait_ready.sh correctly detected failed run

==========================================
E2E Test Suite Summary
==========================================
PASSED: 14
FAILED: 0
==========================================
All tests passed!
```

**Cleanup**: Test suite automatically cleans up all test data on exit.

---

## Integration Points

### With GitHub Actions

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Queue deployment run
        id: deploy
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        run: |
          run_id=$(./scripts/odooops/env_create.sh \
            my-project \
            deploy \
            ${{ github.ref_name }} \
            ${{ github.sha }} \
            prod)
          echo "run_id=$run_id" >> $GITHUB_OUTPUT

      - name: Wait for deployment
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        run: |
          ./scripts/odooops/env_wait_ready.sh \
            ${{ steps.deploy.outputs.run_id }} \
            1800 \
            10
```

### With Worker Agent

Worker agents can claim and execute runs:

```bash
#!/bin/bash
# worker.sh - Simple worker loop

WORKER_ID="worker-$(hostname)-$$"

while true; do
  # Claim next queued run
  run=$(psql "$DATABASE_URL" -t -c \
    "SELECT run_id FROM ops.claim_next_run('$WORKER_ID') LIMIT 1;")

  if [[ -n "$run" ]]; then
    echo "Claimed run: $run"

    # Mark as running
    psql "$DATABASE_URL" -c \
      "UPDATE ops.runs SET status='running', started_at=NOW() WHERE run_id='$run';"

    # Execute build/deploy
    if ./scripts/odooops/execute_run.sh "$run"; then
      # Success
      psql "$DATABASE_URL" -c \
        "UPDATE ops.runs SET status='success', finished_at=NOW() WHERE run_id='$run';"
    else
      # Failed
      psql "$DATABASE_URL" -c \
        "UPDATE ops.runs SET status='failed', finished_at=NOW() WHERE run_id='$run';"
    fi
  fi

  sleep 5
done
```

---

## Database Schema Reference

### ops.runs

| Column | Type | Description |
|--------|------|-------------|
| run_id | TEXT (PK) | Unique run identifier: `run-YYYYMMDD-HHMMSS-<sha>` |
| project_id | TEXT (FK) | References ops.projects |
| env_id | TEXT (FK) | References ops.environments |
| git_sha | TEXT | Full 40-char commit SHA |
| git_ref | TEXT | Branch/tag name |
| status | TEXT | `queued`, `claimed`, `running`, `success`, `failed`, `cancelled` |
| claimed_by | TEXT | Worker ID that claimed this run |
| queued_at | TIMESTAMPTZ | When run was queued |
| started_at | TIMESTAMPTZ | When worker started execution |
| finished_at | TIMESTAMPTZ | When run reached terminal state |
| metadata | JSONB | workflow_type, created_by, custom data |

### ops.run_events

| Column | Type | Description |
|--------|------|-------------|
| event_id | TEXT (PK) | Auto-generated: `evt-<uuid>` |
| run_id | TEXT (FK) | References ops.runs |
| level | TEXT | `debug`, `info`, `warn`, `error` |
| message | TEXT | Human-readable log message |
| payload | JSONB | Structured event data |
| created_at | TIMESTAMPTZ | Event timestamp |

### ops.artifacts

| Column | Type | Description |
|--------|------|-------------|
| artifact_id | TEXT (PK) | Auto-generated: `art-<uuid>` |
| run_id | TEXT (FK) | References ops.runs |
| artifact_type | TEXT | `image`, `sbom`, `logs`, `evidence`, `manifest` |
| storage_path | TEXT | GHCR URL, S3 path, etc. |
| digest | TEXT | SHA256 digest for images |
| size_bytes | BIGINT | Artifact size |
| metadata | JSONB | Custom artifact data |

---

## Troubleshooting

### Run stuck in 'queued' state

**Cause**: No workers available to claim run.

**Solution**:
1. Check worker logs: `docker logs worker-001`
2. Verify worker is running: `docker ps | grep worker`
3. Manually claim run:
   ```sql
   UPDATE ops.runs
   SET status='claimed', claimed_by='manual-worker'
   WHERE run_id='run-20260214-120000-abc123d';
   ```

### env_wait_ready.sh times out

**Cause**: Run is stuck or build taking too long.

**Solution**:
1. Check run status:
   ```bash
   psql "$DATABASE_URL" -c \
     "SELECT run_id, status, started_at, finished_at
      FROM ops.runs WHERE run_id='<run_id>';"
   ```
2. Check logs:
   ```bash
   psql "$DATABASE_URL" -c \
     "SELECT level, message, created_at
      FROM ops.run_events
      WHERE run_id='<run_id>'
      ORDER BY created_at DESC LIMIT 20;"
   ```
3. Increase timeout or cancel run:
   ```bash
   ./scripts/odooops/env_destroy.sh <run_id>
   ```

### Supabase connection errors

**Error**: `missing SUPABASE_URL`

**Solution**: Set environment variables:
```bash
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_ANON_KEY="<anon-key>"
export SUPABASE_SERVICE_ROLE_KEY="<service-role-key>"
```

**Error**: `curl: (22) HTTP 404`

**Solution**: Verify table exists:
```sql
SELECT tablename FROM pg_tables WHERE schemaname='ops' ORDER BY tablename;
```

If missing, run migration:
```bash
cd supabase
supabase db push
```

### Test suite failures

**Error**: `Failed to create project`

**Cause**: Project ID conflict or missing schema.

**Solution**:
1. Delete existing test data:
   ```sql
   DELETE FROM ops.projects WHERE project_id LIKE 'test-project-%';
   ```
2. Verify schema:
   ```sql
   \d ops.projects
   ```

---

## Migration History

| Date | Change | Impact |
|------|--------|--------|
| 2026-02-13 | Created ops.* schema | Initial implementation |
| 2026-02-14 | Updated scripts for Supabase | Replaced legacy API calls |
| 2026-02-14 | Added e2e test suite | Comprehensive workflow testing |

---

## See Also

- **Spec Bundle**: `spec/odooops-sh/` - Complete specification
- **Schema**: `supabase/migrations/20260214_000001_ops_schema_core.sql`
- **Documentation**: `docs/odooops-sh/RUN_LIFECYCLE.md`
- **CI Integration**: `.github/workflows/odooops-sh-spec-gates.yml`
