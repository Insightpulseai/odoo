# OdooOps Platform - Product Requirements Document

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-02-12
**Owner**: InsightPulse AI Platform Team

---

## Executive Summary

**OdooOps Platform** is a self-hostable, API-first Platform-as-a-Service for Odoo 19 CE that automates the entire development-to-production lifecycle through GitOps workflows, policy-driven deployments, and deterministic build systems.

### Problem Statement

**Current Pain Points**:

1. **Manual Deployment Complexity**: Deploying Odoo requires manual server configuration, database migrations, addon management, and rollback procedures
2. **Environment Inconsistency**: Dev/staging/prod environments drift due to manual changes and undocumented configuration
3. **No Staging Parity**: Testing in staging doesn't guarantee production success due to data/config differences
4. **Expensive Enterprise Dependency**: Odoo.sh requires Enterprise license and lacks API automation
5. **Operational Toil**: DevOps teams spend 40% of time on deployment operations instead of platform improvements

### Solution Overview

**OdooOps Platform** provides:

- **GitOps Workflows**: Push to git triggers automated build → test → deploy pipelines
- **Branch-Based Environments**: Each git branch gets isolated environment with dedicated database
- **Policy Engine**: Declarative rules govern environment promotion (dev → staging → prod)
- **API-First Control Plane**: Every operation accessible via REST API + CLI wrapper
- **Deterministic Builds**: Same commit SHA produces identical container images across all environments

### Success Criteria

**Quantitative**:
- 80% reduction in deployment time (60 min → 12 min)
- 95% reduction in deployment failures (20% → 1%)
- 100% environment parity between staging and production
- Zero manual configuration changes in production

**Qualitative**:
- Developers can create feature environments in <5 minutes without DevOps involvement
- Operations team focuses on platform improvements, not deployment firefighting
- Audit trail for all infrastructure changes through git history
- Reproducible disaster recovery through infrastructure-as-code

---

## Goals and Non-Goals

### Goals (G1-G3)

#### G1: Developer Velocity

**Objective**: Enable developers to ship features 3x faster through automated infrastructure.

**Key Results**:
- Time to first deployment: < 15 minutes (from repo clone)
- Environment creation: < 3 minutes (new branch)
- Build time (cached): < 2 minutes (incremental changes)
- Rollback time: < 5 minutes (automated revert)

**User Stories**:
- **US-1.1**: As a developer, I want to create a feature environment with one CLI command so I can test changes in isolation
- **US-1.2**: As a developer, I want automatic deployments on git push so I don't manually trigger builds
- **US-1.3**: As a developer, I want database clones from production so I can test with realistic data
- **US-1.4**: As a developer, I want instant rollback capability so I can quickly recover from bad deployments

#### G2: Operational Excellence

**Objective**: Reduce manual operational work by 80% through policy-driven automation.

**Key Results**:
- Manual intervention rate: < 2% of deployments
- Deployment success rate: > 98%
- Infrastructure cost per environment: < $50/month (dev/staging)
- Platform uptime: > 99.5% (production environments)

**User Stories**:
- **US-2.1**: As an ops engineer, I want declarative deployment policies so I don't manually approve promotions
- **US-2.2**: As an ops engineer, I want automated health gates so broken builds never reach production
- **US-2.3**: As an ops engineer, I want resource quotas per environment so costs don't spiral
- **US-2.4**: As an ops engineer, I want audit logs for all changes so I can troubleshoot incidents

#### G3: Production Parity

**Objective**: Achieve 100% staging-production parity to eliminate "works in staging" failures.

**Key Results**:
- Build reproducibility: 100% (same SHA = identical image)
- Configuration drift: 0 (all config in git)
- Database schema parity: 100% (migration validation)
- Dependency pinning: 100% (lockfile-based resolution)

**User Stories**:
- **US-3.1**: As a QA engineer, I want staging to mirror production exactly so tests accurately predict production behavior
- **US-3.2**: As a developer, I want deterministic builds so I can trust that staging success means production success
- **US-3.3**: As a developer, I want locked dependencies so addon version changes don't break production
- **US-3.4**: As an ops engineer, I want configuration as code so no manual changes create drift

### Non-Goals

**Out of Scope**:

- ❌ **Multi-cloud support**: DigitalOcean only (no AWS/GCP/Azure)
- ❌ **Odoo Enterprise**: CE + OCA addons only (no paid Enterprise modules)
- ❌ **General-purpose PaaS**: Odoo-specific optimization (not for Django/Rails/etc)
- ❌ **Managed hosting service**: Self-hosted only (no SaaS offering)
- ❌ **UI-first experience**: CLI/API primary, web UI optional read-only dashboard
- ❌ **Custom database engines**: PostgreSQL 16 only (no MySQL/SQLite)
- ❌ **Real-time collaboration**: No live coding or shared terminals

---

## Personas

### P1: Feature Developer (Primary)

**Profile**:
- **Role**: Full-stack developer working on Odoo modules
- **Experience**: 2-5 years Python/JavaScript, 1 year Odoo
- **Tools**: VS Code, git, Docker Desktop
- **Workflow**: Feature branches → PR → merge → deploy

**Goals**:
- Quickly spin up isolated test environments
- Iterate rapidly without breaking shared dev environment
- Test with production-like data
- Deploy to staging without ops team involvement

**Pain Points**:
- Waiting for ops to provision test environments (2-3 days)
- Staging environment conflicts with other developers
- Can't reproduce production issues locally
- Manual deployment steps are error-prone

**User Journey (Feature Development)**:
1. Create feature branch: `git checkout -b feature/crm-automation`
2. Auto-create environment: `odooops env create feature/crm-automation`
3. Develop locally, push to trigger CI/CD
4. Review in isolated environment: `https://feature-crm-automation.dev.odooops.io`
5. Merge PR → auto-promote to staging
6. Verify in staging → promote to production

### P2: DevOps Engineer (Secondary)

**Profile**:
- **Role**: Platform engineer maintaining infrastructure
- **Experience**: 5+ years DevOps, strong in Docker/Kubernetes/CI-CD
- **Tools**: Terraform, Ansible, GitHub Actions, Prometheus
- **Workflow**: Infrastructure-as-code, GitOps, policy-driven automation

**Goals**:
- Minimize manual deployment toil
- Enforce security and compliance policies
- Monitor platform health and costs
- Enable developer self-service

**Pain Points**:
- Spending 40% of time on deployment requests
- Manual configuration changes create drift
- No visibility into environment resource usage
- Rollback procedures are manual and risky

**User Journey (Platform Operations)**:
1. Define policies: Edit `.odooops/policies.yaml` in git
2. Commit and push policy changes
3. Platform auto-applies policies to all environments
4. Monitor via CLI: `odooops status --all`
5. Review alerts: `odooops alerts list --severity=critical`
6. Audit trail: `odooops audit logs --since=24h`

### P3: QA Engineer (Tertiary)

**Profile**:
- **Role**: Quality assurance testing Odoo modules
- **Experience**: 3-5 years testing, familiar with Selenium/Playwright
- **Tools**: Pytest, Playwright, Postman
- **Workflow**: Test plans → manual + automated testing → bug reports

**Goals**:
- Test in production-like environments
- Validate migrations before production
- Reproduce customer-reported issues
- Automate regression tests

**Pain Points**:
- Staging environment doesn't match production
- Can't reproduce production data scenarios
- Manual test environment setup is time-consuming
- Database state cleanup between test runs

**User Journey (QA Testing)**:
1. Request staging clone: `odooops db clone production --to=qa-staging --anonymize`
2. Run test suite: `odooops test run integration --env=qa-staging`
3. Review test results: `odooops test results --env=qa-staging`
4. Report bugs with environment snapshot: `odooops env snapshot qa-staging --share`

---

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Control Plane                         │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │  API Server│  │ Policy Engine│  │ Build Scheduler  │    │
│  │  (FastAPI) │◄─┤  (YAML Rules)│◄─┤ (Celery Workers) │    │
│  └─────┬──────┘  └──────────────┘  └──────────────────┘    │
│        │                                                      │
│        ▼                                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Database (PostgreSQL)                   │    │
│  │  - Environment metadata                              │    │
│  │  - Deployment history                                │    │
│  │  - Audit logs                                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Orchestrates
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                         Data Plane                           │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Environment: Dev │  │ Environment: Prod│                │
│  │ ┌──────────────┐ │  │ ┌──────────────┐ │                │
│  │ │ Odoo Workers │ │  │ │ Odoo Workers │ │                │
│  │ │ (Gunicorn x2)│ │  │ │ (Gunicorn x8)│ │                │
│  │ └───────┬──────┘ │  │ └───────┬──────┘ │                │
│  │         │        │  │         │        │                │
│  │    ┌────▼─────┐  │  │    ┌────▼─────┐  │                │
│  │    │PostgreSQL│  │  │    │PostgreSQL│  │                │
│  │    │ (Managed)│  │  │    │ (Managed)│  │                │
│  │    └──────────┘  │  │    └──────────┘  │                │
│  │    ┌──────────┐  │  │    ┌──────────┐  │                │
│  │    │Filestore │  │  │    │Filestore │  │                │
│  │    │(S3/Spaces)│  │  │    │(S3/Spaces)│  │                │
│  │    └──────────┘  │  │    └──────────┘  │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Monitored by
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Monitoring Plane                         │
│                (See observability spec)                      │
│  ┌───────────┐  ┌──────────┐  ┌────────────┐               │
│  │Prometheus │  │   Loki   │  │ AlertManager│              │
│  └───────────┘  └──────────┘  └────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### Control Plane Components

**API Server** (FastAPI, Python):
- **Responsibilities**: HTTP REST API, authentication, authorization, request validation
- **Endpoints**: 20+ endpoints (env CRUD, deploy, logs, backup/restore, policy management)
- **Authentication**: JWT tokens with 12-hour expiry
- **Rate Limiting**: 100 req/min per user, 1000 req/min per API key
- **Technology**: FastAPI 0.109+, Pydantic for validation, SQLAlchemy for ORM

**Policy Engine**:
- **Responsibilities**: Branch mapping rules, health gate validation, promotion logic
- **Configuration**: YAML-based policies in `.odooops/policies.yaml`
- **Evaluation**: Pre-deployment policy checks, blocking vs warning rules
- **Examples**: "staging requires 100% test pass", "prod requires manual approval"

**Build Scheduler** (Celery):
- **Responsibilities**: Queue management, build orchestration, artifact caching
- **Workers**: 4 workers for concurrent builds
- **Queue**: Redis-backed task queue
- **Tasks**: Build image, run tests, deploy container, run migrations, backup database

**Database** (PostgreSQL control_plane schema):
- **Tables**: environments, deployments, builds, policies, audit_logs
- **Retention**: 90 days for audit logs, 30 days for build artifacts
- **Encryption**: At-rest encryption via pgcrypto

#### Data Plane Components

**Odoo Workers** (Gunicorn + Odoo):
- **Configuration**: Gunicorn with configurable worker count (1-8 per environment)
- **Worker Types**: Web (HTTP), cron (scheduled tasks), queue (job processing)
- **Resource Limits**: CPU/memory quotas per environment tier
- **Isolation**: Dedicated database + filestore per environment

**PostgreSQL Databases**:
- **Deployment**: DigitalOcean Managed PostgreSQL 16
- **Isolation**: Separate database per environment (no schema sharing)
- **Connection Pooling**: PgBouncer with 100 max connections per environment
- **Backup**: Automated daily backups with 7-30 day retention

**Filestore**:
- **Storage**: DigitalOcean Spaces (S3-compatible)
- **Structure**: `bucket/environment-id/attachments/`
- **Quota**: 10GB (dev), 50GB (staging), 100GB (prod)
- **Access**: Signed URLs with 1-hour expiry

**nginx Reverse Proxy**:
- **Purpose**: SSL termination, request routing, rate limiting
- **Configuration**: Per-environment config with custom domain support
- **SSL**: Let's Encrypt automated certificate renewal
- **Caching**: Static asset caching (7-day TTL)

---

## Functional Requirements

### 7.1 Environment Management

**FR-1.1: Create Environment**
- **Input**: Branch name, environment tier (dev/staging/prod), optional resource overrides
- **Output**: Environment ID, database credentials, HTTPS URL, deployment status
- **Behavior**:
  - Provision database (managed PostgreSQL)
  - Create filestore bucket
  - Generate nginx config
  - Deploy Odoo container
  - Run initial migrations
  - Return ready status (< 3 minutes)
- **API**: `POST /api/v1/environments`
- **CLI**: `odooops env create feature/new-reports --tier=dev`

**FR-1.2: List Environments**
- **Input**: Optional filters (branch, tier, status, user)
- **Output**: Paginated list of environments with metadata
- **Behavior**: Query control plane database, return active environments only (exclude destroyed)
- **API**: `GET /api/v1/environments?tier=dev&status=active`
- **CLI**: `odooops env list --tier=dev`

**FR-1.3: Get Environment Details**
- **Input**: Environment ID or branch name
- **Output**: Full environment spec (database URL, filestore path, deployed SHA, resource usage, logs URL)
- **Behavior**: Retrieve from control plane database, include real-time metrics
- **API**: `GET /api/v1/environments/{env-id}`
- **CLI**: `odooops env get feature/new-reports`

**FR-1.4: Update Environment**
- **Input**: Environment ID, optional updates (worker count, resource limits, custom domain)
- **Output**: Updated environment spec, deployment status
- **Behavior**: Trigger redeploy with new configuration, health check validation
- **API**: `PATCH /api/v1/environments/{env-id}`
- **CLI**: `odooops env update feature/new-reports --workers=4`

**FR-1.5: Destroy Environment**
- **Input**: Environment ID, optional --keep-database flag
- **Output**: Destruction status, cleanup report
- **Behavior**:
  - Stop Odoo workers
  - Delete nginx config
  - Drop database (unless flagged)
  - Delete filestore bucket
  - Remove from control plane
- **API**: `DELETE /api/v1/environments/{env-id}`
- **CLI**: `odooops env destroy feature/new-reports --confirm`

### 7.2 Deployment Workflows

**FR-2.1: Trigger Deployment**
- **Input**: Environment ID, git commit SHA, optional --wait flag
- **Output**: Deployment ID, build logs URL, estimated completion time
- **Behavior**:
  - Queue build job (Celery task)
  - Build Docker image with commit SHA tag
  - Run tests in build container
  - Push image to registry
  - Deploy to environment
  - Run database migrations
  - Health check validation
  - Mark deployment complete/failed
- **API**: `POST /api/v1/deployments`
- **CLI**: `odooops deploy feature/new-reports --sha=abc123 --wait`

**FR-2.2: Rollback Deployment**
- **Input**: Environment ID, optional target deployment ID (default: previous)
- **Output**: Rollback deployment ID, status
- **Behavior**:
  - Identify previous successful deployment
  - Redeploy previous Docker image
  - Rollback database migrations (if safe)
  - Health check validation
  - Notify via configured channels
- **API**: `POST /api/v1/environments/{env-id}/rollback`
- **CLI**: `odooops rollback production`

**FR-2.3: Promote Between Stages**
- **Input**: Source environment ID, target environment ID, optional --auto-migrate
- **Output**: Promotion deployment ID, status
- **Behavior**:
  - Validate policy rules (e.g., staging → prod requires approval)
  - Deploy same Docker image as source environment
  - Optionally run migrations
  - Health check validation
  - Update deployment history
- **API**: `POST /api/v1/promotions`
- **CLI**: `odooops promote staging production --confirm`

**FR-2.4: Get Deployment Status**
- **Input**: Deployment ID
- **Output**: Deployment details (status, logs, duration, commit SHA, tests passed/failed)
- **Behavior**: Query control plane database, include build logs and test results
- **API**: `GET /api/v1/deployments/{deployment-id}`
- **CLI**: `odooops deployment get abc123`

**FR-2.5: List Deployments**
- **Input**: Environment ID, optional filters (status, date range)
- **Output**: Paginated deployment history
- **Behavior**: Query control plane database, ordered by timestamp DESC
- **API**: `GET /api/v1/environments/{env-id}/deployments`
- **CLI**: `odooops deployment list production --limit=10`

### 7.3 Database Operations

**FR-3.1: Clone Database**
- **Input**: Source environment ID, target environment ID, optional --anonymize flag
- **Output**: Clone job ID, estimated time, target database credentials
- **Behavior**:
  - Create database dump (pg_dump)
  - Optionally anonymize PII (emails, names, addresses)
  - Restore dump to target database (pg_restore)
  - Run post-clone SQL scripts (update ir_config_parameter, disable crons)
  - Validate schema integrity
- **API**: `POST /api/v1/databases/clone`
- **CLI**: `odooops db clone production --to=qa-staging --anonymize`

**FR-3.2: Backup Database**
- **Input**: Environment ID, optional --description
- **Output**: Backup ID, S3 URL, size, timestamp
- **Behavior**:
  - Trigger pg_dump with compression
  - Upload to S3 (DigitalOcean Spaces)
  - Record metadata in control plane
  - Apply retention policy (auto-delete old backups)
- **API**: `POST /api/v1/databases/{env-id}/backup`
- **CLI**: `odooops db backup production --description="Pre-migration backup"`

**FR-3.3: Restore Database**
- **Input**: Backup ID, target environment ID, optional --force
- **Output**: Restore job ID, status
- **Behavior**:
  - Download backup from S3
  - Drop target database (if --force)
  - Create target database
  - Restore dump (pg_restore)
  - Validate schema integrity
  - Restart Odoo workers
- **API**: `POST /api/v1/databases/restore`
- **CLI**: `odooops db restore production --backup=backup-123 --to=staging`

**FR-3.4: Run Migrations**
- **Input**: Environment ID, optional --dry-run
- **Output**: Migration results (SQL executed, errors, duration)
- **Behavior**:
  - Connect to database
  - Detect pending Odoo migrations
  - Run migrations in transaction
  - Rollback on failure
  - Log migration SQL for audit
- **API**: `POST /api/v1/databases/{env-id}/migrate`
- **CLI**: `odooops db migrate staging --dry-run`

**FR-3.5: List Backups**
- **Input**: Environment ID, optional filters (date range)
- **Output**: Paginated backup list (ID, timestamp, size, retention expiry)
- **Behavior**: Query control plane database, include S3 metadata
- **API**: `GET /api/v1/databases/{env-id}/backups`
- **CLI**: `odooops db backups production --limit=20`

### 7.4 Policy Management

**FR-4.1: Define Branch Mapping**
- **Input**: Git branch pattern, environment tier, auto-deploy flag
- **Output**: Policy ID, validation status
- **Behavior**:
  - Parse policy YAML
  - Validate branch regex patterns
  - Store in control plane database
  - Apply to all future git push events
- **Configuration**: `.odooops/policies.yaml`
  ```yaml
  branch_mappings:
    - pattern: "develop"
      tier: "dev"
      auto_deploy: true
    - pattern: "release/*"
      tier: "staging"
      auto_deploy: true
    - pattern: "main"
      tier: "production"
      auto_deploy: false
  ```
- **CLI**: `odooops policy validate` (validates `.odooops/policies.yaml`)

**FR-4.2: Define Health Gates**
- **Input**: Stage name, validation rules (tests, migrations, smoke checks)
- **Output**: Policy ID, validation status
- **Behavior**:
  - Store health gate rules
  - Evaluate before deployment
  - Block deployment on failure
  - Log validation results
- **Configuration**: `.odooops/policies.yaml`
  ```yaml
  health_gates:
    staging:
      - type: "tests"
        command: "pytest tests/"
        required: true
      - type: "migrations"
        required: true
    production:
      - type: "manual_approval"
        required: true
      - type: "smoke_tests"
        command: "pytest tests/smoke/"
        required: true
  ```
- **CLI**: `odooops policy check staging` (dry-run validation)

**FR-4.3: Define Resource Quotas**
- **Input**: Environment tier, resource limits (CPU, memory, storage, workers)
- **Output**: Policy ID, validation status
- **Behavior**:
  - Enforce resource limits at deployment time
  - Throttle CPU if exceeded
  - Block deployment if storage quota exceeded
- **Configuration**: `.odooops/policies.yaml`
  ```yaml
  resource_quotas:
    dev:
      workers: 2
      cpu: "1000m"
      memory: "2Gi"
      storage: "10Gi"
    production:
      workers: 8
      cpu: "4000m"
      memory: "8Gi"
      storage: "100Gi"
  ```

**FR-4.4: Define TTL Policies**
- **Input**: Environment tier, TTL duration
- **Output**: Policy ID, validation status
- **Behavior**:
  - Auto-destroy environments after TTL expiry
  - Send warning notification 24h before destruction
  - Extend TTL via CLI command
- **Configuration**: `.odooops/policies.yaml`
  ```yaml
  ttl_policies:
    dev_ephemeral: 7d
    dev_named: 14d
    staging: never
    production: never
  ```
- **CLI**: `odooops env extend feature/new-reports --days=7`

### 7.5 Git Integration

**FR-5.1: Webhook Receiver**
- **Input**: GitHub webhook payload (push, PR, branch events)
- **Output**: HTTP 200 OK, deployment job ID
- **Behavior**:
  - Validate webhook signature (HMAC)
  - Extract commit SHA, branch name, author
  - Match branch against policies
  - Queue deployment job if auto-deploy enabled
  - Respond immediately (async processing)
- **API**: `POST /api/v1/webhooks/github`
- **Configuration**: GitHub repo settings → Webhooks → `https://odooops.io/api/v1/webhooks/github`

**FR-5.2: Ephemeral Preview Environments**
- **Input**: PR opened event from GitHub webhook
- **Output**: Preview environment URL (e.g., `https://pr-123.preview.odooops.io`)
- **Behavior**:
  - Create temporary environment on PR open
  - Deploy PR head commit
  - Comment on PR with preview URL
  - Auto-destroy on PR close/merge
- **API**: Triggered by webhook (no direct CLI)
- **CLI**: `odooops preview create --pr=123` (manual override)

**FR-5.3: Build Status Integration**
- **Input**: Deployment status change
- **Output**: GitHub commit status update
- **Behavior**:
  - Update commit status (pending/success/failure)
  - Link to deployment logs
  - Block PR merge if deployment fails (optional)
- **API**: GitHub Status API (outbound from OdooOps)
- **Configuration**: `.odooops/policies.yaml`
  ```yaml
  github_integration:
    update_commit_status: true
    block_merge_on_failure: true
    comment_on_pr: true
  ```

### 7.6 Observability & Logging

**Note**: Detailed observability requirements in separate spec (`odooops-observability-enterprise-pack/`).

**FR-6.1: Stream Logs**
- **Input**: Environment ID, optional filters (service, log level, time range)
- **Output**: Real-time log stream (WebSocket) or historical logs (HTTP)
- **Behavior**:
  - Tail logs from Loki
  - Support follow mode (--follow)
  - Filter by service (odoo, nginx, postgres)
- **API**: `GET /api/v1/environments/{env-id}/logs?follow=true`
- **CLI**: `odooops logs feature/new-reports --follow`

**FR-6.2: Get Metrics**
- **Input**: Environment ID, metric type (CPU, memory, requests), time range
- **Output**: Time-series data (Prometheus format)
- **Behavior**:
  - Query Prometheus for metrics
  - Return in JSON format
  - Support aggregation (avg, max, p95)
- **API**: `GET /api/v1/environments/{env-id}/metrics?metric=cpu&range=1h`
- **CLI**: `odooops metrics feature/new-reports --metric=cpu --range=1h`

**FR-6.3: Audit Logs**
- **Input**: Optional filters (user, action, date range)
- **Output**: Paginated audit log entries
- **Behavior**:
  - Query control plane audit_logs table
  - Include user, action, timestamp, IP, request details
  - Immutable append-only log
- **API**: `GET /api/v1/audit-logs?user=john@example.com&since=2026-02-01`
- **CLI**: `odooops audit logs --user=john@example.com --since=2026-02-01`

---

## Non-Functional Requirements

### Performance

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| API Latency (p95) | < 200ms | Prometheus histogram |
| Build Time (Clean) | < 8 min | Deployment duration metric |
| Build Time (Cached) | < 2 min | Deployment duration metric |
| Environment Creation | < 3 min | Provisioning duration metric |
| Database Clone Time | < 10 min | pg_dump + pg_restore duration |
| Rollback Time | < 5 min | Deployment duration metric |

### Scalability

| Dimension | Target | Scaling Strategy |
|-----------|--------|------------------|
| Concurrent Builds | 10 | Horizontal scaling (Celery workers) |
| Total Environments | 100 | Database partitioning + resource quotas |
| API Requests/min | 1000 | Rate limiting + caching |
| Database Size | 500GB | Managed PostgreSQL auto-scaling |
| Filestore Size | 1TB | S3 storage (unlimited) |

### Reliability

| Metric | Target | Implementation |
|--------|--------|----------------|
| Platform Uptime | > 99.5% | Health checks, auto-restart, monitoring |
| Deployment Success Rate | > 98% | Pre-flight validation, health gates |
| Data Loss Risk (RPO) | < 1 hour | Automated backups every 1 hour (prod) |
| Recovery Time (RTO) | < 15 min | Automated restore from backup |
| Build Reproducibility | 100% | Lockfile-based dependencies, immutable images |

### Security

| Requirement | Implementation |
|-------------|----------------|
| **Authentication** | JWT tokens (12h expiry), API keys (long-lived) |
| **Authorization** | Role-based access control (RBAC) with scopes |
| **Data Encryption** | At-rest: pgcrypto for sensitive data; In-transit: TLS 1.3 |
| **Network Isolation** | Internal DNS per environment, no direct DB access |
| **Secrets Management** | Encrypted vault (Supabase Vault or HashiCorp Vault) |
| **Audit Logging** | Immutable append-only logs for all control plane operations |
| **Vulnerability Scanning** | Weekly Trivy scans of Docker images |

---

## User Experience Requirements

### CLI Design Principles

**Discoverability**:
- `odooops help` shows all commands with examples
- `odooops <command> --help` shows detailed usage
- Tab completion for bash/zsh

**Consistency**:
- Resource naming: `odooops <resource> <action> <target>`
- Flags follow conventions: `--wait`, `--confirm`, `--json`
- Output format: human-readable by default, `--json` for machine parsing

**Feedback**:
- Progress indicators for long operations (build, restore)
- Color-coded output (success=green, error=red, warning=yellow)
- Actionable error messages with remediation steps

**Example Commands**:
```bash
# Environment management
odooops env create feature/reports --tier=dev
odooops env list --tier=prod
odooops env destroy feature/reports --confirm

# Deployment
odooops deploy staging --sha=abc123 --wait
odooops rollback production
odooops promote staging production --confirm

# Database operations
odooops db clone production --to=staging --anonymize
odooops db backup production --description="Pre-migration"
odooops db restore production --backup=backup-123

# Logs and metrics
odooops logs production --follow
odooops metrics production --metric=cpu --range=1h

# Policy management
odooops policy validate
odooops policy check staging
```

### API Design Principles

**REST Conventions**:
- Resource-oriented URLs: `/api/v1/environments/{env-id}`
- HTTP verbs: GET (read), POST (create), PATCH (update), DELETE (destroy)
- Status codes: 200 (success), 201 (created), 400 (bad request), 401 (unauthorized), 404 (not found), 500 (server error)

**Versioning**:
- URL-based versioning: `/api/v1/`
- Version in headers: `Accept: application/vnd.odooops.v1+json`
- Deprecation notices in response headers

**Response Format**:
```json
{
  "data": { ... },
  "meta": {
    "request_id": "req-abc123",
    "timestamp": "2026-02-12T10:30:00Z"
  },
  "errors": []
}
```

**Error Format**:
```json
{
  "error": "DEPLOYMENT_FAILED",
  "message": "Health check failed after deployment",
  "details": {
    "check": "smoke_tests",
    "exit_code": 1,
    "logs": "https://odooops.io/logs/deploy-abc123"
  },
  "remediation": "Run 'odooops logs deploy-abc123' to view full logs",
  "docs": "https://docs.odooops.io/errors/DEPLOYMENT_FAILED"
}
```

---

## Dependencies and Integrations

### External Dependencies

| Dependency | Purpose | Version | Critical? |
|------------|---------|---------|-----------|
| **DigitalOcean Managed PostgreSQL** | Database hosting | 16+ | Yes |
| **DigitalOcean Spaces** | Filestore (S3-compatible) | N/A | Yes |
| **Docker Registry** | Container image storage | Docker Hub or GHCR | Yes |
| **GitHub** | Git hosting + webhooks | N/A | Yes |
| **Let's Encrypt** | SSL certificate provider | N/A | Yes |
| **Redis** | Task queue + caching | 7.0+ | Yes |
| **Prometheus** | Metrics storage | 2.45+ | No (observability) |
| **Loki** | Log aggregation | 2.9+ | No (observability) |

### Internal Integrations

**Supabase** (per `docs/ai/SUPABASE.md`):
- **Project**: `spdtwktxdalcfigzeqrz`
- **Usage**: Control plane database (alternative to self-hosted PostgreSQL)
- **Features**: Audit logs via `control_plane` schema, realtime notifications, encrypted secrets vault
- **Integration**: OdooOps API can optionally use Supabase as control plane DB

**n8n** (per `docs/architecture/PROD_RUNTIME_SNAPSHOT.md`):
- **Domain**: `n8n.insightpulseai.com`
- **Usage**: Webhook routing for alerts, notifications, integrations
- **Workflows**: GitHub webhook → n8n → Slack notification
- **Integration**: OdooOps sends deployment events to n8n webhooks

**GitHub Actions** (per `.github/workflows/cd-production.yml`):
- **Usage**: Trigger OdooOps deployments via API on git push
- **Integration**: GitHub Action → OdooOps API → Deployment pipeline
- **Example**:
  ```yaml
  - name: Trigger OdooOps Deployment
    run: |
      curl -X POST https://odooops.io/api/v1/deployments \
        -H "Authorization: Bearer ${{ secrets.ODOOOPS_API_TOKEN }}" \
        -d '{"environment_id": "prod", "commit_sha": "${{ github.sha }}"}'
  ```

---

## Implementation Phases

See `plan.md` for detailed phased implementation.

**Summary**:
- **M0**: Foundation (control plane DB, API skeleton)
- **M1**: Core workflows (env create/destroy, deploy)
- **M2**: Database operations (backup/restore/clone)
- **M3**: Git integration (webhooks, preview envs)
- **M4**: Policy engine (branch mapping, health gates)
- **M5**: Production hardening (observability, disaster recovery)

---

## Success Criteria

### Acceptance Criteria

**MVP (Minimum Viable Platform)**:
- [ ] Create/destroy environments via CLI
- [ ] Deploy Odoo from git commit SHA
- [ ] Backup/restore production database
- [ ] GitHub webhook triggers auto-deployment
- [ ] Branch mapping policies work (dev/staging/prod)

**Production Ready**:
- [ ] 99.5% uptime over 30-day period
- [ ] < 200ms API latency (p95)
- [ ] Deployment success rate > 98%
- [ ] All 20 core API endpoints functional
- [ ] Comprehensive documentation (API spec + user guide)

**Feature Complete**:
- [ ] Ephemeral preview environments on PR open
- [ ] Database anonymization for clones
- [ ] Custom domain support with Let's Encrypt
- [ ] SSH/shell access with audit logging
- [ ] Mail neutralization for dev/staging

### Key Performance Indicators (KPIs)

**Developer Velocity**:
- Time to first deployment: Target < 15 min (currently ~60 min manual)
- Environment creation time: Target < 3 min (currently ~2-3 days via ops team)
- Build time (cached): Target < 2 min (currently ~10 min)

**Operational Efficiency**:
- Manual intervention rate: Target < 2% (currently ~40% of deployments)
- Deployment success rate: Target > 98% (currently ~80%)
- Infrastructure cost per env: Target < $50/month (currently ~$150/month)

**Platform Reliability**:
- Platform uptime: Target > 99.5% (currently no SLA)
- Data loss risk (RPO): Target < 1 hour (currently ~24 hours)
- Recovery time (RTO): Target < 15 min (currently ~2 hours)

---

## Risks and Mitigations

### Technical Risks

**R1: Database Clone Performance**
- **Risk**: Large production databases (>100GB) take >30 minutes to clone
- **Impact**: Delays QA testing, staging environment refresh
- **Mitigation**: Implement incremental clones (pg_dump with --schema-only + selective data)
- **Contingency**: Provide partial clones (last 30 days of data) as fast option

**R2: Build System Bottlenecks**
- **Risk**: 10+ concurrent builds saturate build workers
- **Impact**: Deployment queue delays exceed 10 minutes
- **Mitigation**: Horizontal scaling of Celery workers, priority queues (prod > staging > dev)
- **Contingency**: Burst to external CI (GitHub Actions) for overflow builds

**R3: Storage Costs**
- **Risk**: Unlimited environment creation causes storage costs to spike
- **Impact**: $1000+/month storage bills
- **Mitigation**: Enforce TTL policies, storage quotas per environment, automated cleanup
- **Contingency**: Implement tiered storage (frequent → infrequent → archive)

### Operational Risks

**R4: Credential Leakage**
- **Risk**: Database credentials exposed via logs or API responses
- **Impact**: Security breach, data exfiltration
- **Mitigation**: Encrypted secrets vault, credential rotation, audit logging
- **Contingency**: Immediate credential rotation, incident response playbook

**R5: Runaway Resource Usage**
- **Risk**: Misconfigured environment consumes all CPU/memory
- **Impact**: Platform-wide outage
- **Mitigation**: Resource quotas, CPU throttling, OOM killer, alerting
- **Contingency**: Manual environment shutdown, rollback to previous config

**R6: Policy Misconfiguration**
- **Risk**: Incorrect branch mapping deploys dev to production
- **Impact**: Production outage, data corruption
- **Mitigation**: Policy validation on commit, dry-run mode, manual approval for prod
- **Contingency**: Instant rollback, database restore from backup

---

## Open Questions

1. **Database Masking**: What PII fields need anonymization for prod → staging clones?
   - **Assignee**: Security team
   - **Target**: Before M2 implementation

2. **Custom Domains**: Should we support custom apex domains or subdomains only?
   - **Assignee**: DevOps team
   - **Target**: Before M4 implementation

3. **Multi-Tenancy**: Do we need tenant isolation (multiple customers on one platform)?
   - **Assignee**: Product team
   - **Target**: Before M0 implementation (affects architecture)

4. **SSH Access**: Should SSH be enabled by default or opt-in per environment?
   - **Assignee**: Security team
   - **Target**: Before M3 implementation

5. **Mail Catcher**: Integrate existing tool (MailHog/MailCatcher) or build custom?
   - **Assignee**: DevOps team
   - **Target**: Before M4 implementation

---

## Appendices

### Glossary

- **Control Plane**: Orchestration layer (API, policy engine, build scheduler)
- **Data Plane**: Runtime Odoo environments (workers, databases, filestore)
- **Ephemeral Environment**: Temporary environment with TTL (e.g., PR previews)
- **Health Gate**: Validation rule that blocks deployment on failure
- **Policy Engine**: Declarative rule system for deployment automation
- **Promotion**: Deploying same artifact from one stage to another (staging → prod)

### References

- **`spec/odoo-sh-next/`**: Original platform spec (foundation for this PRD)
- **`spec/platform-kit/`**: Generic platform patterns
- **`spec/odooops-observability-enterprise-pack/`**: Observability layer extending this platform
- **`docs/architecture/PROD_RUNTIME_SNAPSHOT.md`**: Current deployment architecture
- **`docs/ai/SUPABASE.md`**: Supabase integration capabilities
- **`.github/workflows/cd-production.yml`**: Current CI/CD pipeline

---

**Document Status**: ✅ PRD complete
**Next Steps**: Create implementation plan (plan.md) and task breakdown (tasks.md)
**Review Date**: 2026-03-01 (or on major requirement changes)
