# OdooOps Platform - Task Breakdown

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-02-12
**Owner**: InsightPulse AI Platform Team

---

## Task Organization

Tasks are organized by milestone (M0-M5) and categorized by component. Each task includes:
- **Task ID**: Unique identifier (e.g., T0.1.1)
- **Description**: What needs to be done
- **Owner**: Primary responsible party
- **Estimate**: Time estimate in hours or days
- **Dependencies**: Prerequisites
- **Acceptance Criteria**: Definition of done

**Conventions**:
- ☐ Not started
- 🔄 In progress
- ✅ Complete
- ❌ Blocked

---

## M0: Foundation (Weeks 1-2)

### T0.1: Control Plane Database

#### T0.1.1: Schema Design
- ☐ Design PostgreSQL schema for control plane
- ☐ Create ER diagram for tables (environments, deployments, policies, audit_logs)
- ☐ Define indexes for query optimization
- ☐ Document foreign key relationships
- **Owner**: Database team
- **Estimate**: 4 hours
- **Acceptance**: Schema diagram approved, all tables defined

#### T0.1.2: Database Provisioning
- ☐ Choose deployment method (Supabase vs self-hosted PostgreSQL)
- ☐ Provision database instance (DigitalOcean Managed DB or Supabase project)
- ☐ Configure connection pooling (PgBouncer if self-hosted)
- ☐ Set up automated backups (daily at minimum)
- **Owner**: DevOps team
- **Estimate**: 2 hours
- **Acceptance**: Database accessible, backups configured

#### T0.1.3: Schema Migration
- ☐ Create Alembic migration for initial schema
- ☐ Run migration against control plane database
- ☐ Verify all tables created correctly
- ☐ Seed initial data (admin user, default policies)
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Dependencies**: T0.1.2
- **Acceptance**: `\dt` shows all tables, seed data inserted

#### T0.1.4: Database Access Layer
- ☐ Implement SQLAlchemy ORM models (Environment, Deployment, Policy, AuditLog)
- ☐ Write database connection manager with retry logic
- ☐ Create CRUD operations for each model
- ☐ Add transaction management utilities
- **Owner**: Backend team
- **Estimate**: 8 hours
- **Dependencies**: T0.1.3
- **Acceptance**: Models work, CRUD operations tested

### T0.2: API Server Skeleton

#### T0.2.1: FastAPI Project Setup
- ☐ Initialize FastAPI project structure
- ☐ Configure development dependencies (pytest, black, mypy)
- ☐ Set up Docker development environment
- ☐ Create `.env.example` with required environment variables
- **Owner**: Backend team
- **Estimate**: 2 hours
- **Acceptance**: `uvicorn app.main:app --reload` starts successfully

#### T0.2.2: Authentication System
- ☐ Implement JWT token generation with HS256
- ☐ Create `/api/v1/auth/login` endpoint
- ☐ Implement token verification middleware
- ☐ Add scope-based authorization (admin, developer, viewer)
- **Owner**: Backend team
- **Estimate**: 6 hours
- **Acceptance**: Login returns valid JWT, protected endpoints require auth

#### T0.2.3: Core API Endpoints (Stubs)
- ☐ `GET /api/v1/health` - Health check endpoint
- ☐ `GET /api/v1/environments` - List environments (stub)
- ☐ `POST /api/v1/environments` - Create environment (stub)
- ☐ `GET /api/v1/environments/{id}` - Get environment details (stub)
- ☐ `DELETE /api/v1/environments/{id}` - Delete environment (stub)
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T0.2.2
- **Acceptance**: All endpoints return 200 with placeholder data

#### T0.2.4: Error Handling
- ☐ Implement global exception handler
- ☐ Create structured error response format (error code, message, remediation)
- ☐ Add validation error handling (Pydantic)
- ☐ Implement request ID tracking for debugging
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Acceptance**: Errors return consistent format with error codes

#### T0.2.5: API Documentation
- ☐ Generate OpenAPI 3.1 spec from FastAPI
- ☐ Configure Swagger UI at `/docs`
- ☐ Add endpoint descriptions and examples
- ☐ Document authentication flow
- **Owner**: Backend team
- **Estimate**: 2 hours
- **Dependencies**: T0.2.3
- **Acceptance**: Swagger UI accessible, all endpoints documented

### T0.3: CLI Prototype

#### T0.3.1: CLI Project Setup
- ☐ Initialize Python Click CLI project
- ☐ Create `setup.py` for pip installation
- ☐ Configure entry point (`odooops` command)
- ☐ Set up CLI project structure (commands/, api_client.py, config.py)
- **Owner**: Frontend/CLI team
- **Estimate**: 2 hours
- **Acceptance**: `odooops --help` works after `pip install -e .`

#### T0.3.2: Configuration Management
- ☐ Implement `~/.odooops.yaml` config file handling
- ☐ Create `odooops config set <key> <value>` command
- ☐ Store API token securely (keyring or file with 600 permissions)
- ☐ Add environment variable fallback
- **Owner**: Frontend/CLI team
- **Estimate**: 3 hours
- **Acceptance**: Config persists across commands, token stored securely

#### T0.3.3: HTTP Client
- ☐ Implement API client wrapper (requests library)
- ☐ Add automatic JWT token injection from config
- ☐ Implement retry logic with exponential backoff
- ☐ Add error response parsing
- **Owner**: Frontend/CLI team
- **Estimate**: 4 hours
- **Acceptance**: Client handles auth, retries, and errors correctly

#### T0.3.4: Core Commands (Stubs)
- ☐ `odooops auth login` - Authenticate and store token
- ☐ `odooops env list` - List environments
- ☐ `odooops env create <name>` - Create environment (stub)
- ☐ `odooops env get <name>` - Get environment details (stub)
- ☐ `odooops env destroy <name>` - Delete environment (stub)
- **Owner**: Frontend/CLI team
- **Estimate**: 6 hours
- **Dependencies**: T0.3.3, T0.2.3
- **Acceptance**: Commands work, output is human-readable

#### T0.3.5: Output Formatting
- ☐ Implement table formatting for list commands
- ☐ Add `--json` flag for machine-readable output
- ☐ Add color support (click.style)
- ☐ Implement progress indicators (spinners for long operations)
- **Owner**: Frontend/CLI team
- **Estimate**: 3 hours
- **Acceptance**: Commands have pretty output, JSON mode works

### T0.4: Build Scheduler

#### T0.4.1: Redis Setup
- ☐ Deploy Redis instance (Docker or managed service)
- ☐ Configure Redis connection in Celery
- ☐ Set up Redis monitoring (basic health checks)
- **Owner**: DevOps team
- **Estimate**: 1 hour
- **Acceptance**: Redis accessible, Celery can connect

#### T0.4.2: Celery Worker Setup
- ☐ Create Celery app configuration
- ☐ Define base task class with logging
- ☐ Set up Celery worker Dockerfile
- ☐ Configure worker count and concurrency
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Dependencies**: T0.4.1
- **Acceptance**: `celery -A tasks worker` starts successfully

#### T0.4.3: Task Stubs
- ☐ `build_image(deployment_id, commit_sha)` - Build Docker image (stub)
- ☐ `deploy(deployment_id, environment_id, commit_sha)` - Deploy environment (stub)
- ☐ `backup_database(environment_id)` - Backup database (stub)
- ☐ `restore_database(backup_id, target_environment_id)` - Restore database (stub)
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: Tasks can be queued and return placeholder results

#### T0.4.4: Task Monitoring
- ☐ Implement Celery task result storage (Redis backend)
- ☐ Add task status endpoint in API (`GET /api/v1/tasks/{task_id}`)
- ☐ Implement task cancellation (`DELETE /api/v1/tasks/{task_id}`)
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Dependencies**: T0.4.3
- **Acceptance**: Task status queryable via API

---

## M1: Core Workflows (Weeks 3-5)

### T1.1: Environment Provisioning

#### T1.1.1: Database Provisioning
- ☐ Implement PostgreSQL database creation via DigitalOcean API
- ☐ Generate random database credentials
- ☐ Store credentials in encrypted vault (Supabase Vault or HashiCorp Vault)
- ☐ Configure PgBouncer connection pooling
- **Owner**: Backend team
- **Estimate**: 1 day
- **Acceptance**: Databases created successfully, credentials stored securely

#### T1.1.2: Filestore Provisioning
- ☐ Implement S3 bucket creation (DigitalOcean Spaces)
- ☐ Set bucket permissions (private with signed URL access)
- ☐ Configure lifecycle policies (optional cleanup for dev environments)
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: Buckets created, Odoo can read/write attachments

#### T1.1.3: Nginx Configuration
- ☐ Generate nginx config template for environments
- ☐ Implement SSL certificate automation (Let's Encrypt)
- ☐ Add rate limiting and request size limits
- ☐ Configure static asset caching
- **Owner**: DevOps team
- **Estimate**: 6 hours
- **Acceptance**: Nginx routes requests correctly, SSL works

#### T1.1.4: Odoo Container Deployment
- ☐ Create Odoo Dockerfile with configurable workers
- ☐ Implement container deployment via Docker API or Docker Compose
- ☐ Configure environment variables (DB_HOST, WORKERS, etc.)
- ☐ Set resource limits (CPU, memory)
- **Owner**: DevOps team
- **Estimate**: 1 day
- **Acceptance**: Odoo container runs, connects to database

#### T1.1.5: Initial Migrations
- ☐ Implement odoo-bin --init command execution
- ☐ Run base module installation
- ☐ Verify database schema initialized correctly
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Dependencies**: T1.1.4
- **Acceptance**: Odoo boots successfully, base modules installed

#### T1.1.6: Environment Lifecycle API
- ☐ Implement `POST /api/v1/environments` (full implementation)
- ☐ Implement `GET /api/v1/environments` (list with filters)
- ☐ Implement `GET /api/v1/environments/{id}` (full details)
- ☐ Implement `PATCH /api/v1/environments/{id}` (update config)
- ☐ Implement `DELETE /api/v1/environments/{id}` (destroy)
- **Owner**: Backend team
- **Estimate**: 1 day
- **Dependencies**: T1.1.1-T1.1.5
- **Acceptance**: All CRUD operations work end-to-end

### T1.2: Deployment Pipeline

#### T1.2.1: Repository Cloning
- ☐ Implement git clone with sparse checkout
- ☐ Configure Git LFS support (if needed)
- ☐ Add shallow clone optimization (depth=1)
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Acceptance**: Repository cloned correctly for any commit SHA

#### T1.2.2: Docker Image Building
- ☐ Implement Dockerfile build with commit SHA tag
- ☐ Add layer caching configuration
- ☐ Implement multi-stage builds (build → runtime)
- ☐ Tag images with commit SHA and environment
- **Owner**: DevOps team
- **Estimate**: 1 day
- **Acceptance**: Images build successfully, cached builds < 2 min

#### T1.2.3: Test Execution
- ☐ Run tests inside build container (pytest for Odoo modules)
- ☐ Capture test results and logs
- ☐ Fail build if tests fail
- ☐ Upload test results to control plane
- **Owner**: QA team
- **Estimate**: 6 hours
- **Acceptance**: Tests run, results captured, builds fail on test failure

#### T1.2.4: Image Registry Push
- ☐ Configure Docker registry (Docker Hub or GitHub Container Registry)
- ☐ Implement image push with authentication
- ☐ Tag images as latest for environment
- **Owner**: DevOps team
- **Estimate**: 2 hours
- **Acceptance**: Images pushed successfully, tagged correctly

#### T1.2.5: Container Update
- ☐ Implement container image update (pull new image)
- ☐ Restart Odoo workers with new image
- ☐ Wait for workers to be ready (health check)
- **Owner**: DevOps team
- **Estimate**: 4 hours
- **Dependencies**: T1.2.4
- **Acceptance**: Containers updated, no downtime

#### T1.2.6: Migration Execution
- ☐ Detect pending migrations (query ir_module_module)
- ☐ Run odoo-bin --update for changed modules
- ☐ Capture migration logs
- ☐ Rollback on migration failure
- **Owner**: Backend team
- **Estimate**: 1 day
- **Acceptance**: Migrations run automatically, rollback works

#### T1.2.7: Health Check Validation
- ☐ Implement HTTP health check endpoint in Odoo
- ☐ Check database connectivity
- ☐ Verify all workers are responsive
- ☐ Fail deployment if health check fails
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: Health checks detect issues, deployments rollback on failure

#### T1.2.8: Deployment API
- ☐ Implement `POST /api/v1/deployments` (trigger deployment)
- ☐ Implement `GET /api/v1/deployments/{id}` (get status)
- ☐ Implement `GET /api/v1/environments/{id}/deployments` (list history)
- ☐ Add real-time deployment logs streaming (WebSocket or SSE)
- **Owner**: Backend team
- **Estimate**: 1 day
- **Dependencies**: T1.2.1-T1.2.7
- **Acceptance**: Deployments work end-to-end, logs accessible

### T1.3: Rollback Mechanism

#### T1.3.1: Previous Deployment Detection
- ☐ Query control plane for previous successful deployment
- ☐ Verify previous image still exists in registry
- ☐ Check if migration rollback is safe
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Acceptance**: Previous deployment identified correctly

#### T1.3.2: Image Rollback
- ☐ Redeploy previous Docker image
- ☐ Restart workers with previous image
- ☐ Verify workers are healthy
- **Owner**: DevOps team
- **Estimate**: 3 hours
- **Dependencies**: T1.3.1
- **Acceptance**: Previous image deployed successfully

#### T1.3.3: Migration Rollback
- ☐ Implement safe migration rollback detection
- ☐ Run migration rollback if safe
- ☐ Warn if rollback unsafe (manual intervention required)
- **Owner**: Backend team
- **Estimate**: 6 hours
- **Acceptance**: Safe rollbacks work, unsafe rollbacks warn user

#### T1.3.4: Rollback API
- ☐ Implement `POST /api/v1/environments/{id}/rollback`
- ☐ Add optional target deployment ID parameter
- ☐ Return rollback status and details
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Dependencies**: T1.3.1-T1.3.3
- **Acceptance**: Rollback command works via API and CLI

### T1.4: Environment Destruction

#### T1.4.1: Worker Shutdown
- ☐ Stop Odoo workers gracefully (SIGTERM)
- ☐ Wait for workers to finish requests (30s timeout)
- ☐ Force kill if timeout exceeded (SIGKILL)
- **Owner**: DevOps team
- **Estimate**: 2 hours
- **Acceptance**: Workers shut down cleanly

#### T1.4.2: Database Cleanup
- ☐ Drop database (unless --keep-database flag)
- ☐ Revoke database credentials
- ☐ Remove database user
- **Owner**: Backend team
- **Estimate**: 2 hours
- **Acceptance**: Database dropped, credentials revoked

#### T1.4.3: Filestore Cleanup
- ☐ Delete S3 bucket contents
- ☐ Delete S3 bucket
- ☐ Verify deletion completed
- **Owner**: Backend team
- **Estimate**: 2 hours
- **Acceptance**: Filestore completely removed

#### T1.4.4: Nginx Cleanup
- ☐ Remove nginx config file
- ☐ Reload nginx configuration
- ☐ Verify routes removed
- **Owner**: DevOps team
- **Estimate**: 1 hour
- **Acceptance**: Nginx no longer routes to destroyed environment

#### T1.4.5: Control Plane Cleanup
- ☐ Update environment status to "destroyed"
- ☐ Archive deployment history (don't delete)
- ☐ Archive audit logs
- **Owner**: Backend team
- **Estimate**: 2 hours
- **Acceptance**: Environment marked destroyed, history preserved

---

## M2: Database Operations (Weeks 6-7)

### T2.1: Automated Backups

#### T2.1.1: Backup Job Implementation
- ☐ Implement pg_dump wrapper with compression
- ☐ Generate unique backup IDs
- ☐ Upload compressed dump to S3
- ☐ Record backup metadata in control plane
- **Owner**: Backend team
- **Estimate**: 1 day
- **Acceptance**: Backups complete successfully, stored in S3

#### T2.1.2: Backup Scheduling
- ☐ Configure Celery periodic tasks for backups
- ☐ Set schedules per environment tier (6h prod, 24h staging, never dev)
- ☐ Add manual backup trigger API
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T2.1.1
- **Acceptance**: Backups run automatically, manual trigger works

#### T2.1.3: Retention Policies
- ☐ Implement retention policy enforcement
- ☐ Auto-delete backups older than retention period
- ☐ Keep minimum number of backups (e.g., last 5)
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: Old backups deleted automatically

#### T2.1.4: Backup API
- ☐ `POST /api/v1/databases/{env_id}/backup` - Trigger backup
- ☐ `GET /api/v1/databases/{env_id}/backups` - List backups
- ☐ `GET /api/v1/backups/{backup_id}` - Get backup details
- ☐ `DELETE /api/v1/backups/{backup_id}` - Delete backup
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T2.1.1-T2.1.3
- **Acceptance**: Backup operations work via API

### T2.2: Database Restore

#### T2.2.1: Restore Job Implementation
- ☐ Download backup from S3
- ☐ Drop target database (if --force)
- ☐ Create target database
- ☐ Run pg_restore with proper flags
- ☐ Validate schema integrity
- **Owner**: Backend team
- **Estimate**: 1 day
- **Acceptance**: Restore completes successfully, database accessible

#### T2.2.2: Worker Restart After Restore
- ☐ Restart Odoo workers after restore
- ☐ Clear Redis caches
- ☐ Verify workers can connect to restored database
- **Owner**: DevOps team
- **Estimate**: 2 hours
- **Dependencies**: T2.2.1
- **Acceptance**: Workers work with restored database

#### T2.2.3: Restore API
- ☐ `POST /api/v1/databases/restore` - Restore from backup
- ☐ Add safety confirmation for production restores
- ☐ Return restore job status
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T2.2.1-T2.2.2
- **Acceptance**: Restore works via API with safety checks

### T2.3: Database Cloning with Anonymization

#### T2.3.1: Clone Implementation
- ☐ Create backup of source database
- ☐ Restore backup to target database
- ☐ Run post-clone SQL scripts
- **Owner**: Backend team
- **Estimate**: 6 hours
- **Dependencies**: T2.1.1, T2.2.1
- **Acceptance**: Clone completes successfully

#### T2.3.2: PII Anonymization
- ☐ Identify PII fields (emails, phones, names, addresses)
- ☐ Implement anonymization SQL scripts
- ☐ Add --anonymize flag to clone command
- ☐ Verify anonymization with sample queries
- **Owner**: Backend + Security team
- **Estimate**: 1 day
- **Acceptance**: PII fields anonymized, data still usable for testing

#### T2.3.3: Post-Clone Configuration
- ☐ Disable scheduled actions (ir_cron)
- ☐ Update system parameters (web.base.url)
- ☐ Clear user sessions
- ☐ Reset OAuth tokens (if applicable)
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: Cloned environment safe for testing

#### T2.3.4: Clone API
- ☐ `POST /api/v1/databases/clone` - Clone database
- ☐ Add --anonymize and --keep-database flags
- ☐ Return clone job status
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T2.3.1-T2.3.3
- **Acceptance**: Clone works with all options

### T2.4: Migration Runner

#### T2.4.1: Migration Detection
- ☐ Query ir_module_module for pending updates
- ☐ Detect new modules to install
- ☐ Detect modules to upgrade
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: Pending migrations detected correctly

#### T2.4.2: Migration Execution
- ☐ Run odoo-bin --update for each module
- ☐ Capture migration logs
- ☐ Fail if migration errors occur
- **Owner**: Backend team
- **Estimate**: 6 hours
- **Dependencies**: T2.4.1
- **Acceptance**: Migrations run successfully

#### T2.4.3: Dry-Run Mode
- ☐ Implement --dry-run flag
- ☐ Show pending migrations without executing
- ☐ Estimate migration time
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Acceptance**: Dry-run shows migrations without changing database

#### T2.4.4: Migration API
- ☐ `POST /api/v1/databases/{env_id}/migrate` - Run migrations
- ☐ `GET /api/v1/databases/{env_id}/migrations` - List pending migrations
- ☐ Add --dry-run flag
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T2.4.1-T2.4.3
- **Acceptance**: Migrations work via API with dry-run support

---

## M3: Git Integration (Weeks 8-9)

### T3.1: GitHub Webhook Receiver

#### T3.1.1: Webhook Endpoint
- ☐ Create `POST /api/v1/webhooks/github` endpoint
- ☐ Implement HMAC signature verification
- ☐ Parse GitHub webhook payloads
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: Webhook receives and verifies GitHub events

#### T3.1.2: Event Handling
- ☐ Handle push events (trigger deployment)
- ☐ Handle pull_request events (create/destroy preview envs)
- ☐ Handle branch deletion events (cleanup)
- **Owner**: Backend team
- **Estimate**: 1 day
- **Dependencies**: T3.1.1
- **Acceptance**: Events trigger correct actions

#### T3.1.3: Policy Matching
- ☐ Match branch name against policies
- ☐ Determine if auto-deploy is enabled
- ☐ Queue deployment if policy matches
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T3.1.2
- **Acceptance**: Webhooks respect branch mapping policies

### T3.2: Ephemeral Preview Environments

#### T3.2.1: Preview Environment Creation
- ☐ Create environment on PR open
- ☐ Name environment as pr-{number}
- ☐ Deploy PR head commit
- ☐ Set TTL to 7 days
- **Owner**: Backend team
- **Estimate**: 6 hours
- **Dependencies**: T3.1.2
- **Acceptance**: PR opening creates preview environment

#### T3.2.2: PR Comment Integration
- ☐ Implement GitHub API comment posting
- ☐ Comment on PR with preview URL
- ☐ Update comment when deployment completes
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: PR comments posted with correct preview URL

#### T3.2.3: Preview Cleanup
- ☐ Destroy preview environment on PR close
- ☐ Destroy preview environment on PR merge
- ☐ Handle manual cleanup (TTL expiry)
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Acceptance**: Preview environments cleaned up automatically

### T3.3: Commit Status Integration

#### T3.3.1: Status Update Implementation
- ☐ Implement GitHub Status API client
- ☐ Update commit status on deployment start (pending)
- ☐ Update commit status on deployment success/failure
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: Commit statuses appear on GitHub

#### T3.3.2: Status Details
- ☐ Add links to deployment logs in status
- ☐ Add detailed descriptions (e.g., "Building...", "Tests passed")
- ☐ Configure status context ("odooops/deployment")
- **Owner**: Backend team
- **Estimate**: 2 hours
- **Dependencies**: T3.3.1
- **Acceptance**: Status details are informative

---

## M4: Policy Engine (Weeks 10-11)

### T4.1: Branch Mapping Policies

#### T4.1.1: Policy Schema Definition
- ☐ Define YAML schema for branch_mappings
- ☐ Implement policy validation (regex patterns, valid tiers)
- ☐ Document policy format in constitution.md
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Acceptance**: Policy schema documented, validation works

#### T4.1.2: Policy Loading
- ☐ Load policies from `.odooops/policies.yaml` in repository
- ☐ Cache policies in control plane database
- ☐ Reload policies on file change (webhook trigger)
- **Owner**: Backend team
- **Estimate**: 6 hours
- **Acceptance**: Policies loaded correctly

#### T4.1.3: Branch Matching Logic
- ☐ Implement regex pattern matching for branches
- ☐ Select first matching policy (priority order)
- ☐ Return policy details (tier, auto_deploy)
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T4.1.2
- **Acceptance**: Branch matching works correctly

### T4.2: Health Gate Validation

#### T4.2.1: Health Gate Schema
- ☐ Define YAML schema for health_gates
- ☐ Support gate types (tests, migrations, manual_approval, smoke_tests)
- ☐ Implement gate validation
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Acceptance**: Health gate schema defined

#### T4.2.2: Gate Execution
- ☐ Execute test gates (run pytest)
- ☐ Execute migration gates (check pending migrations)
- ☐ Execute manual approval gates (pause deployment)
- ☐ Execute smoke test gates (run smoke tests)
- **Owner**: Backend + QA team
- **Estimate**: 1 day
- **Dependencies**: T4.2.1
- **Acceptance**: All gate types work

#### T4.2.3: Gate Enforcement
- ☐ Block deployment if required gate fails
- ☐ Allow warning gates to proceed
- ☐ Log gate results in deployment history
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T4.2.2
- **Acceptance**: Deployments blocked on gate failure

### T4.3: Resource Quotas

#### T4.3.1: Quota Schema Definition
- ☐ Define YAML schema for resource_quotas
- ☐ Support quota types (workers, cpu, memory, storage)
- ☐ Implement quota validation
- **Owner**: Backend team
- **Estimate**: 3 hours
- **Acceptance**: Quota schema defined

#### T4.3.2: Quota Enforcement
- ☐ Apply CPU limits to containers
- ☐ Apply memory limits to containers
- ☐ Enforce worker count limits
- ☐ Check storage usage against quota
- **Owner**: DevOps team
- **Estimate**: 1 day
- **Dependencies**: T4.3.1
- **Acceptance**: Quotas enforced correctly

### T4.4: TTL Policies

#### T4.4.1: TTL Schema Definition
- ☐ Define YAML schema for ttl_policies
- ☐ Support TTL formats (7d, 14d, never)
- ☐ Implement TTL parsing
- **Owner**: Backend team
- **Estimate**: 2 hours
- **Acceptance**: TTL schema defined

#### T4.4.2: TTL Enforcement
- ☐ Identify environments exceeding TTL
- ☐ Send warning notification 24h before destruction
- ☐ Auto-destroy environments after TTL expiry
- **Owner**: Backend team
- **Estimate**: 1 day
- **Dependencies**: T4.4.1
- **Acceptance**: TTL policies enforced, warnings sent

#### T4.4.3: TTL Extension
- ☐ Implement `PATCH /api/v1/environments/{id}/ttl` endpoint
- ☐ Allow extending TTL by specified duration
- ☐ Add CLI command `odooops env extend <name> --days=7`
- **Owner**: Backend team
- **Estimate**: 4 hours
- **Dependencies**: T4.4.2
- **Acceptance**: TTL extension works via API and CLI

---

## M5: Production Hardening (Weeks 12-14)

### T5.1: Observability Integration

**Note**: See `odooops-observability-enterprise-pack/` spec for detailed task breakdown.

#### T5.1.1: OpenTelemetry Setup
- ☐ Install OpenTelemetry collector
- ☐ Configure OTLP exporters (metrics, traces, logs)
- ☐ Instrument FastAPI with OTEL SDK
- **Owner**: DevOps team
- **Estimate**: 1 day
- **Acceptance**: OTEL collector running, metrics exported

#### T5.1.2: Prometheus Integration
- ☐ Configure Prometheus to scrape OTEL collector
- ☐ Define alerting rules (deployment failures, high latency)
- ☐ Set up Grafana dashboards
- **Owner**: DevOps team
- **Estimate**: 1 day
- **Acceptance**: Metrics visible in Grafana

#### T5.1.3: Loki Integration
- ☐ Deploy Loki for log aggregation
- ☐ Configure log forwarding from containers
- ☐ Set up log retention (30 days)
- **Owner**: DevOps team
- **Estimate**: 1 day
- **Acceptance**: Logs queryable in Grafana

### T5.2: Disaster Recovery

#### T5.2.1: Recovery Runbooks
- ☐ Document full platform restore procedure
- ☐ Document database restore procedure
- ☐ Document control plane restore procedure
- **Owner**: DevOps + Technical Writer
- **Estimate**: 1 day
- **Acceptance**: Runbooks complete, tested

#### T5.2.2: Automated DR Testing
- ☐ Implement automated DR test (create → backup → destroy → restore)
- ☐ Schedule weekly DR tests
- ☐ Alert on DR test failures
- **Owner**: DevOps team
- **Estimate**: 1 day
- **Acceptance**: DR tests run successfully

### T5.3: Security Audit and Hardening

#### T5.3.1: Security Checklist Review
- ☐ Review all API endpoints for authentication
- ☐ Verify database credentials are encrypted
- ☐ Audit secrets management (no hardcoded secrets)
- ☐ Review network isolation policies
- **Owner**: Security team
- **Estimate**: 2 days
- **Acceptance**: Security checklist completed, no critical issues

#### T5.3.2: Vulnerability Scanning
- ☐ Set up Trivy for container scanning
- ☐ Schedule weekly scans
- ☐ Alert on high/critical vulnerabilities
- **Owner**: DevOps team
- **Estimate**: 4 hours
- **Acceptance**: Scans running, no critical vulnerabilities

#### T5.3.3: Penetration Testing
- ☐ Engage external penetration testing firm
- ☐ Provide test credentials and scope
- ☐ Review findings and remediate issues
- **Owner**: Security team
- **Estimate**: External (1 week turnaround)
- **Acceptance**: Pentest completed, critical issues resolved

### T5.4: Documentation

#### T5.4.1: Architecture Documentation
- ☐ Create architecture diagram (control/supabase/data/monitoring planes)
- ☐ Document component interactions
- ☐ Write architecture overview
- **Owner**: Technical Writer + Architect
- **Estimate**: 1 day
- **Acceptance**: Architecture documented, diagram published

#### T5.4.2: API Reference
- ☐ Generate API documentation from OpenAPI spec
- ☐ Add usage examples for each endpoint
- ☐ Document authentication flow
- **Owner**: Technical Writer
- **Estimate**: 2 days
- **Acceptance**: API reference complete

#### T5.4.3: CLI Usage Guide
- ☐ Document all CLI commands with examples
- ☐ Create workflow tutorials (feature dev, deployment, rollback)
- ☐ Add troubleshooting section
- **Owner**: Technical Writer
- **Estimate**: 2 days
- **Acceptance**: CLI guide complete

#### T5.4.4: Deployment Playbook
- ☐ Document deployment procedures
- ☐ Document rollback procedures
- ☐ Document emergency procedures
- **Owner**: Technical Writer + DevOps
- **Estimate**: 1 day
- **Acceptance**: Playbook complete, tested

---

## Testing and Validation Tasks

### TV.1: Unit Tests
- ☐ Write unit tests for API endpoints (pytest)
- ☐ Write unit tests for CLI commands
- ☐ Write unit tests for Celery tasks
- ☐ Achieve >80% code coverage
- **Owner**: QA team
- **Estimate**: Ongoing (30% of dev time)
- **Acceptance**: 80%+ coverage, CI passing

### TV.2: Integration Tests
- ☐ Write integration tests for environment lifecycle
- ☐ Write integration tests for deployment pipeline
- ☐ Write integration tests for database operations
- **Owner**: QA team
- **Estimate**: Ongoing (20% of dev time)
- **Acceptance**: Critical paths covered

### TV.3: End-to-End Tests
- ☐ Create E2E test: Create env → Deploy → Rollback → Destroy
- ☐ Create E2E test: Backup → Restore
- ☐ Create E2E test: GitHub webhook → Auto-deploy
- **Owner**: QA team
- **Estimate**: 1 week
- **Acceptance**: E2E tests pass on staging

---

## Task Summary

| Milestone | Total Tasks | Estimated Duration |
|-----------|-------------|--------------------|
| M0: Foundation | 23 tasks | 2 weeks |
| M1: Core Workflows | 32 tasks | 3 weeks |
| M2: Database Operations | 21 tasks | 2 weeks |
| M3: Git Integration | 12 tasks | 2 weeks |
| M4: Policy Engine | 15 tasks | 2 weeks |
| M5: Production Hardening | 13 tasks | 3 weeks |
| Testing/Validation | 10 tasks | Ongoing |
| **Total** | **126 tasks** | **14 weeks** |

---

**Document Status**: ✅ Task breakdown complete
**Next Steps**: Begin M0 implementation
**Review Date**: Weekly during development
