# OdooOps Platform - Implementation Plan

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-02-12
**Owner**: InsightPulse AI Platform Team

---

## Overview

This document outlines the phased implementation strategy for the OdooOps Platform, from foundational components through production-ready deployment.

### Timeline Summary

| Milestone | Duration | Dependencies | Key Deliverables |
|-----------|----------|--------------|------------------|
| **M0: Foundation** | 2 weeks | None | Control plane DB, API skeleton, CLI prototype |
| **M1: Core Workflows** | 3 weeks | M0 | Env create/destroy, deploy, rollback |
| **M2: Database Operations** | 2 weeks | M1 | Backup/restore/clone, migrations |
| **M3: Git Integration** | 2 weeks | M1 | GitHub webhooks, preview envs, commit status |
| **M4: Policy Engine** | 2 weeks | M3 | Branch mapping, health gates, TTL policies |
| **M5: Production Hardening** | 3 weeks | M4 | Observability, disaster recovery, security audit |

**Total Duration**: 14 weeks (3.5 months)

---

## Milestone 0: Foundation (Weeks 1-2)

### Objective

Establish core infrastructure and API foundation for platform development.

### Deliverables

#### D0.1: Control Plane Database Schema

**Description**: PostgreSQL schema for platform metadata storage.

**Tables**:
```sql
CREATE TABLE environments (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  branch VARCHAR(255) NOT NULL,
  tier VARCHAR(50) NOT NULL,  -- dev, staging, production
  status VARCHAR(50) NOT NULL,  -- provisioning, active, destroying, destroyed
  database_url TEXT NOT NULL,
  filestore_path TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_by VARCHAR(255),
  resource_limits JSONB,
  UNIQUE(branch)
);

CREATE TABLE deployments (
  id UUID PRIMARY KEY,
  environment_id UUID REFERENCES environments(id),
  commit_sha VARCHAR(40) NOT NULL,
  status VARCHAR(50) NOT NULL,  -- queued, building, deploying, success, failed
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  logs_url TEXT,
  triggered_by VARCHAR(255),
  metadata JSONB
);

CREATE TABLE policies (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL,  -- branch_mapping, health_gate, quota, ttl
  config JSONB NOT NULL,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  user_id VARCHAR(255),
  action VARCHAR(100),
  resource_type VARCHAR(50),
  resource_id VARCHAR(255),
  ip_address INET,
  user_agent TEXT,
  request_details JSONB
);

CREATE INDEX idx_deployments_env ON deployments(environment_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
```

**Verification**:
```bash
psql $CONTROL_PLANE_DB -c "\dt"  # List tables
psql $CONTROL_PLANE_DB -c "\d environments"  # Describe schema
```

#### D0.2: API Server Skeleton (FastAPI)

**Description**: HTTP REST API with authentication and basic endpoints.

**Structure**:
```
odooops-api/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── auth.py                 # JWT authentication
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routers/
│   │   ├── environments.py     # /api/v1/environments
│   │   ├── deployments.py      # /api/v1/deployments
│   │   └── health.py           # /api/v1/health
│   └── database.py             # DB connection
├── requirements.txt
└── Dockerfile
```

**Endpoints (MVP)**:
- `GET /api/v1/health` - Health check
- `POST /api/v1/auth/login` - JWT token generation
- `GET /api/v1/environments` - List environments
- `POST /api/v1/environments` - Create environment (stub)

**Authentication**:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
```

**Verification**:
```bash
# Start API server
uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}'
```

#### D0.3: CLI Prototype (Python Click)

**Description**: Command-line interface wrapping API calls.

**Structure**:
```
odooops-cli/
├── odooops/
│   ├── __init__.py
│   ├── cli.py                  # Click CLI entry point
│   ├── api_client.py           # HTTP client for API
│   ├── commands/
│   │   ├── env.py              # Environment commands
│   │   └── auth.py             # Authentication commands
│   └── config.py               # Config file management (~/.odooops.yaml)
├── setup.py
└── requirements.txt
```

**Commands (MVP)**:
```bash
odooops auth login                    # Store JWT token
odooops env list                      # List environments
odooops env create <name> --tier=dev  # Create environment (stub)
```

**Implementation**:
```python
import click
import requests

@click.group()
def cli():
    pass

@cli.group()
def env():
    pass

@env.command()
def list():
    """List all environments"""
    token = load_token()
    response = requests.get(
        "http://localhost:8000/api/v1/environments",
        headers={"Authorization": f"Bearer {token}"}
    )
    for env in response.json()["data"]:
        click.echo(f"{env['name']} ({env['tier']}) - {env['status']}")
```

**Verification**:
```bash
# Install CLI
pip install -e .

# Test commands
odooops --help
odooops auth login --username=admin --password=secret
odooops env list
```

#### D0.4: Build Scheduler Setup (Celery + Redis)

**Description**: Task queue for asynchronous build jobs.

**Configuration**:
```python
# celeryconfig.py
broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/0"
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"

# tasks.py
from celery import Celery

app = Celery("odooops", broker="redis://localhost:6379/0")

@app.task
def build_image(deployment_id, commit_sha):
    # Placeholder: will implement in M1
    print(f"Building image for {commit_sha}")
    return {"status": "success", "image_tag": commit_sha}
```

**Verification**:
```bash
# Start Redis
docker run -d -p 6379:6379 redis:7

# Start Celery worker
celery -A tasks worker --loglevel=info

# Test task (Python shell)
from tasks import build_image
result = build_image.delay("deploy-123", "abc123")
print(result.get())
```

### Dependencies

- **External**: None (foundation milestone)
- **Internal**: Control plane database provisioned (Supabase or self-hosted PostgreSQL)

### Success Criteria

- [ ] Control plane database schema deployed and verified
- [ ] API server responds to health check and authentication endpoints
- [ ] CLI can authenticate and list environments (even if empty)
- [ ] Celery worker processes tasks from Redis queue

---

## Milestone 1: Core Workflows (Weeks 3-5)

### Objective

Implement essential environment and deployment workflows.

### Deliverables

#### D1.1: Environment Provisioning

**Description**: Create isolated Odoo environments with dedicated resources.

**Implementation**:
```python
@environments_router.post("/")
async def create_environment(request: EnvironmentCreateRequest):
    # 1. Provision database
    db_url = provision_database(request.name, request.tier)

    # 2. Create filestore bucket
    filestore_path = create_filestore_bucket(request.name)

    # 3. Generate nginx config
    generate_nginx_config(request.name, request.tier)

    # 4. Deploy Odoo container
    deploy_odoo_container(
        name=request.name,
        database_url=db_url,
        filestore=filestore_path,
        workers=get_worker_count(request.tier)
    )

    # 5. Run initial migrations
    run_migrations(db_url)

    # 6. Save to control plane
    env = Environment(
        name=request.name,
        branch=request.branch,
        tier=request.tier,
        database_url=db_url,
        filestore_path=filestore_path,
        status="active"
    )
    db.add(env)
    db.commit()

    return {"environment_id": env.id, "url": f"https://{request.name}.odooops.io"}
```

**CLI Integration**:
```bash
odooops env create feature/crm-reports --tier=dev --wait
# Output:
# ✓ Provisioning database... (30s)
# ✓ Creating filestore... (5s)
# ✓ Deploying Odoo... (120s)
# ✓ Running migrations... (20s)
# Environment created: https://feature-crm-reports.dev.odooops.io
```

**Verification**:
```bash
odooops env get feature/crm-reports
# Output:
# Name: feature/crm-reports
# Tier: dev
# Status: active
# URL: https://feature-crm-reports.dev.odooops.io
# Database: postgres://...
# Workers: 2
```

#### D1.2: Deployment Pipeline

**Description**: Build Docker image, run tests, deploy to environment.

**Celery Task**:
```python
@app.task
def deploy(deployment_id, environment_id, commit_sha):
    # 1. Clone repository
    repo_path = clone_repo(commit_sha)

    # 2. Build Docker image
    image_tag = build_docker_image(repo_path, commit_sha)

    # 3. Run tests in build container
    test_results = run_tests(image_tag)
    if not test_results["passed"]:
        raise Exception("Tests failed")

    # 4. Push image to registry
    push_image(image_tag)

    # 5. Update environment
    update_environment_image(environment_id, image_tag)

    # 6. Run database migrations
    run_migrations(environment_id)

    # 7. Restart Odoo workers
    restart_workers(environment_id)

    # 8. Health check
    if not health_check(environment_id):
        rollback_deployment(environment_id)
        raise Exception("Health check failed")

    # 9. Update deployment status
    update_deployment_status(deployment_id, "success")
```

**CLI Integration**:
```bash
odooops deploy feature/crm-reports --sha=abc123 --wait
# Output:
# ✓ Building image... (180s)
# ✓ Running tests... (60s)
# ✓ Pushing image... (30s)
# ✓ Deploying... (45s)
# ✓ Running migrations... (15s)
# ✓ Health check passed
# Deployment successful: https://feature-crm-reports.dev.odooops.io
```

#### D1.3: Rollback Mechanism

**Description**: Revert to previous successful deployment.

**Implementation**:
```python
@deployments_router.post("/{environment_id}/rollback")
async def rollback_deployment(environment_id: str):
    # 1. Find previous successful deployment
    prev_deployment = db.query(Deployment) \
        .filter(Deployment.environment_id == environment_id) \
        .filter(Deployment.status == "success") \
        .order_by(Deployment.completed_at.desc()) \
        .offset(1) \
        .first()

    if not prev_deployment:
        raise HTTPException(404, "No previous deployment found")

    # 2. Redeploy previous image
    rollback_image(environment_id, prev_deployment.commit_sha)

    # 3. Rollback migrations (if safe)
    rollback_migrations(environment_id, prev_deployment.commit_sha)

    # 4. Restart workers
    restart_workers(environment_id)

    return {"status": "rolled_back", "commit_sha": prev_deployment.commit_sha}
```

**CLI Integration**:
```bash
odooops rollback feature/crm-reports
# Output:
# ✓ Rolling back to abc123 (previous deployment)
# ✓ Redeploying image... (30s)
# ✓ Rolling back migrations... (10s)
# ✓ Restarting workers... (15s)
# ✓ Health check passed
# Rollback successful: https://feature-crm-reports.dev.odooops.io
```

#### D1.4: Environment Destruction

**Description**: Clean up all resources associated with environment.

**Implementation**:
```python
@environments_router.delete("/{environment_id}")
async def destroy_environment(environment_id: str, keep_database: bool = False):
    env = get_environment(environment_id)

    # 1. Stop Odoo workers
    stop_workers(environment_id)

    # 2. Delete nginx config
    delete_nginx_config(environment_id)

    # 3. Drop database (unless flagged)
    if not keep_database:
        drop_database(env.database_url)

    # 4. Delete filestore bucket
    delete_filestore(env.filestore_path)

    # 5. Update status in control plane
    env.status = "destroyed"
    db.commit()

    return {"status": "destroyed"}
```

**CLI Integration**:
```bash
odooops env destroy feature/crm-reports --confirm
# Output:
# ⚠ This will destroy environment 'feature/crm-reports'
# ✓ Stopping workers... (5s)
# ✓ Deleting database... (10s)
# ✓ Deleting filestore... (5s)
# Environment destroyed
```

### Dependencies

- **M0**: Control plane DB, API server, CLI, Celery worker

### Success Criteria

- [ ] Create environment completes in < 3 minutes
- [ ] Deploy builds image, runs tests, deploys in < 8 minutes (clean build)
- [ ] Rollback reverts to previous version in < 5 minutes
- [ ] Destroy environment cleans up all resources

---

## Milestone 2: Database Operations (Weeks 6-7)

### Objective

Implement backup, restore, clone, and migration workflows.

### Deliverables

#### D2.1: Automated Backups

**Description**: Scheduled database backups with retention policies.

**Implementation**:
```python
@app.task
def backup_database(environment_id):
    env = get_environment(environment_id)

    # 1. Generate backup ID
    backup_id = f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # 2. Run pg_dump
    dump_file = f"/tmp/{backup_id}.sql.gz"
    subprocess.run([
        "pg_dump",
        env.database_url,
        "--format=custom",
        "--compress=9",
        f"--file={dump_file}"
    ], check=True)

    # 3. Upload to S3
    s3_url = upload_to_s3(dump_file, f"backups/{environment_id}/{backup_id}.sql.gz")

    # 4. Record in control plane
    backup = Backup(
        id=backup_id,
        environment_id=environment_id,
        s3_url=s3_url,
        size=os.path.getsize(dump_file),
        created_at=datetime.now()
    )
    db.add(backup)
    db.commit()

    # 5. Apply retention policy
    apply_retention_policy(environment_id)

    return {"backup_id": backup_id, "size": backup.size}

# Schedule backups
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Production: every 6 hours
    sender.add_periodic_task(
        crontab(minute=0, hour="*/6"),
        backup_database.s(environment_id="production")
    )
```

**CLI Integration**:
```bash
odooops db backup production --description="Pre-migration backup"
# Output:
# ✓ Creating backup... (180s)
# ✓ Uploading to S3... (60s)
# Backup created: backup-20260212-103000 (2.3 GB)

odooops db backups production --limit=10
# Output:
# backup-20260212-103000  2.3 GB  2026-02-12 10:30 (expires 2026-03-14)
# backup-20260212-040000  2.2 GB  2026-02-12 04:00 (expires 2026-03-14)
# backup-20260211-220000  2.1 GB  2026-02-11 22:00 (expires 2026-03-13)
```

#### D2.2: Database Restore

**Description**: Restore database from backup.

**Implementation**:
```python
@app.task
def restore_database(backup_id, target_environment_id, force=False):
    backup = get_backup(backup_id)
    target_env = get_environment(target_environment_id)

    # 1. Download backup from S3
    dump_file = download_from_s3(backup.s3_url)

    # 2. Drop target database (if force)
    if force:
        drop_database(target_env.database_url)

    # 3. Create target database
    create_database(target_env.database_url)

    # 4. Restore dump
    subprocess.run([
        "pg_restore",
        "--dbname", target_env.database_url,
        "--format=custom",
        "--no-owner",
        "--no-acl",
        dump_file
    ], check=True)

    # 5. Validate schema
    validate_schema(target_env.database_url)

    # 6. Restart workers
    restart_workers(target_environment_id)

    return {"status": "restored"}
```

**CLI Integration**:
```bash
odooops db restore production --backup=backup-20260212-103000 --to=staging
# Output:
# ⚠ This will overwrite database in 'staging'
# ✓ Downloading backup... (90s)
# ✓ Dropping database... (5s)
# ✓ Creating database... (2s)
# ✓ Restoring dump... (240s)
# ✓ Validating schema... (10s)
# ✓ Restarting workers... (15s)
# Database restored to staging
```

#### D2.3: Database Cloning with Anonymization

**Description**: Clone production database to staging with PII masking.

**Implementation**:
```python
@app.task
def clone_database(source_env_id, target_env_id, anonymize=False):
    # 1. Create backup of source
    backup_id = backup_database(source_env_id).get()

    # 2. Restore to target
    restore_database(backup_id, target_env_id, force=True)

    # 3. Anonymize PII (if enabled)
    if anonymize:
        anonymize_pii(target_env_id)

    # 4. Post-clone cleanup
    run_post_clone_sql(target_env_id)

    return {"status": "cloned"}

def anonymize_pii(environment_id):
    env = get_environment(environment_id)

    # SQL to anonymize PII
    sql_commands = [
        "UPDATE res_partner SET email = 'user' || id || '@example.com' WHERE email IS NOT NULL",
        "UPDATE res_partner SET phone = NULL",
        "UPDATE res_partner SET mobile = NULL",
        "UPDATE res_users SET password = crypt('password', gen_salt('bf'))",
    ]

    for sql in sql_commands:
        execute_sql(env.database_url, sql)

def run_post_clone_sql(environment_id):
    env = get_environment(environment_id)

    # Disable scheduled actions in non-prod
    execute_sql(env.database_url, "UPDATE ir_cron SET active = false")

    # Update system parameters
    execute_sql(env.database_url, """
        UPDATE ir_config_parameter
        SET value = 'https://staging.odooops.io'
        WHERE key = 'web.base.url'
    """)
```

**CLI Integration**:
```bash
odooops db clone production --to=qa-staging --anonymize
# Output:
# ✓ Creating backup... (180s)
# ✓ Restoring to qa-staging... (240s)
# ✓ Anonymizing PII... (30s)
# ✓ Running post-clone scripts... (10s)
# Database cloned to qa-staging (PII anonymized)
```

#### D2.4: Migration Runner

**Description**: Detect and run pending Odoo database migrations.

**Implementation**:
```python
@app.task
def run_migrations(environment_id, dry_run=False):
    env = get_environment(environment_id)

    # 1. Detect pending migrations
    pending_migrations = detect_pending_migrations(env.database_url)

    if not pending_migrations:
        return {"status": "no_migrations"}

    # 2. Run migrations (in transaction)
    if not dry_run:
        for migration in pending_migrations:
            execute_migration(env.database_url, migration)

    return {"status": "success", "migrations": pending_migrations}

def detect_pending_migrations(database_url):
    # Query ir_module_module for modules needing updates
    result = execute_sql(database_url, """
        SELECT name
        FROM ir_module_module
        WHERE state = 'to upgrade' OR state = 'to install'
    """)
    return [row[0] for row in result]

def execute_migration(database_url, module_name):
    # Run odoo-bin with --update flag
    subprocess.run([
        "odoo-bin",
        "--database", database_url,
        "--update", module_name,
        "--stop-after-init"
    ], check=True)
```

**CLI Integration**:
```bash
odooops db migrate staging --dry-run
# Output:
# Pending migrations:
# - account (v19.0.1.2.0 → v19.0.1.3.0)
# - sale (v19.0.2.1.0 → v19.0.2.2.0)
# - crm_reports (v1.0.0 → v1.1.0)

odooops db migrate staging
# Output:
# ✓ Running migration: account... (15s)
# ✓ Running migration: sale... (10s)
# ✓ Running migration: crm_reports... (5s)
# Migrations complete
```

### Dependencies

- **M1**: Environment provisioning, deployment pipeline

### Success Criteria

- [ ] Backups complete in < 5 minutes for 50GB database
- [ ] Restore completes in < 10 minutes for 50GB database
- [ ] Clone with anonymization completes in < 15 minutes
- [ ] Migrations run successfully with dry-run support

---

## Milestone 3: Git Integration (Weeks 8-9)

### Objective

Automate deployments through GitHub webhooks and enable ephemeral preview environments.

### Deliverables

#### D3.1: GitHub Webhook Receiver

**Description**: Handle GitHub push/PR events and trigger deployments.

**Implementation**:
```python
@app.post("/api/v1/webhooks/github")
async def github_webhook(request: Request):
    # 1. Validate webhook signature
    signature = request.headers.get("X-Hub-Signature-256")
    if not validate_signature(await request.body(), signature):
        raise HTTPException(403, "Invalid signature")

    # 2. Parse payload
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    # 3. Handle events
    if event == "push":
        branch = payload["ref"].replace("refs/heads/", "")
        commit_sha = payload["after"]

        # Match branch against policies
        policy = match_branch_policy(branch)
        if policy and policy.auto_deploy:
            deploy.delay(environment_id=policy.environment_id, commit_sha=commit_sha)

    elif event == "pull_request":
        action = payload["action"]
        pr_number = payload["pull_request"]["number"]

        if action == "opened":
            create_preview_environment(pr_number, payload["pull_request"]["head"]["sha"])
        elif action == "closed":
            destroy_preview_environment(pr_number)

    return {"status": "ok"}
```

**Verification**:
```bash
# Test webhook locally with ngrok
ngrok http 8000

# Configure GitHub webhook
# URL: https://abc123.ngrok.io/api/v1/webhooks/github
# Secret: <WEBHOOK_SECRET>
# Events: push, pull_request

# Trigger deployment by pushing to branch
git push origin feature/crm-reports
```

#### D3.2: Ephemeral Preview Environments

**Description**: Auto-create environments for PRs.

**Implementation**:
```python
def create_preview_environment(pr_number, commit_sha):
    # 1. Create environment
    env_name = f"pr-{pr_number}"
    env_id = create_environment(
        name=env_name,
        branch=f"pull/{pr_number}",
        tier="dev_ephemeral"
    )

    # 2. Deploy commit
    deploy.delay(environment_id=env_id, commit_sha=commit_sha)

    # 3. Comment on PR with preview URL
    comment_on_pr(pr_number, f"""
    🚀 Preview environment ready!

    URL: https://pr-{pr_number}.preview.odooops.io
    Commit: {commit_sha[:7]}

    This environment will auto-destroy when PR is closed.
    """)

    return env_id
```

**GitHub PR Comment Example**:
```
🚀 Preview environment ready!

URL: https://pr-123.preview.odooops.io
Commit: abc1234

This environment will auto-destroy when PR is closed.
```

#### D3.3: Commit Status Integration

**Description**: Update GitHub commit status with deployment results.

**Implementation**:
```python
def update_commit_status(commit_sha, state, description, logs_url=None):
    github_api_url = f"https://api.github.com/repos/{REPO}/statuses/{commit_sha}"

    payload = {
        "state": state,  # pending, success, error, failure
        "description": description,
        "context": "odooops/deployment",
        "target_url": logs_url
    }

    requests.post(
        github_api_url,
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        json=payload
    )

# In deployment task
@app.task
def deploy(deployment_id, environment_id, commit_sha):
    update_commit_status(commit_sha, "pending", "Building...")

    try:
        # Build and deploy
        build_image(commit_sha)
        update_commit_status(commit_sha, "pending", "Deploying...")

        deploy_to_environment(environment_id)
        update_commit_status(commit_sha, "success", "Deployment successful", logs_url)
    except Exception as e:
        update_commit_status(commit_sha, "failure", f"Deployment failed: {e}", logs_url)
        raise
```

### Dependencies

- **M1**: Deployment pipeline, environment provisioning

### Success Criteria

- [ ] GitHub push triggers auto-deployment within 30 seconds
- [ ] PR opening creates preview environment in < 5 minutes
- [ ] Commit status updates appear on GitHub within 10 seconds
- [ ] Preview environments auto-destroy on PR close

---

## Milestone 4: Policy Engine (Weeks 10-11)

### Objective

Implement declarative policy system for deployment automation.

### Deliverables

#### D4.1: Branch Mapping Policies

**Description**: Map git branches to environment tiers.

**Policy Configuration** (`.odooops/policies.yaml`):
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

**Implementation**:
```python
def match_branch_policy(branch_name):
    policies = load_policies("branch_mappings")

    for policy in policies:
        if re.match(policy["pattern"], branch_name):
            return policy

    return None

# In webhook handler
policy = match_branch_policy("release/v2.1")
if policy and policy["auto_deploy"]:
    deploy.delay(environment_id=policy["tier"], commit_sha=commit_sha)
```

#### D4.2: Health Gate Validation

**Description**: Block deployments that fail health checks.

**Policy Configuration**:
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

**Implementation**:
```python
@app.task
def validate_health_gates(deployment_id, environment_id):
    gates = load_policies("health_gates")[environment_id]

    results = []
    for gate in gates:
        if gate["type"] == "tests":
            result = run_command(gate["command"])
            results.append({"gate": gate["type"], "passed": result.returncode == 0})

        elif gate["type"] == "manual_approval":
            result = wait_for_approval(deployment_id)
            results.append({"gate": gate["type"], "passed": result})

    if all(r["passed"] for r in results):
        return {"status": "passed"}
    else:
        raise Exception(f"Health gates failed: {results}")
```

#### D4.3: Resource Quotas

**Description**: Enforce resource limits per environment tier.

**Policy Configuration**:
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

**Enforcement**:
```python
def enforce_resource_quotas(environment_id):
    env = get_environment(environment_id)
    quota = load_policies("resource_quotas")[env.tier]

    # Apply limits to container
    update_container_limits(
        environment_id,
        cpu=quota["cpu"],
        memory=quota["memory"]
    )

    # Check storage usage
    storage_used = get_storage_usage(environment_id)
    if storage_used > quota["storage"]:
        raise Exception(f"Storage quota exceeded: {storage_used} > {quota['storage']}")
```

#### D4.4: TTL Policies

**Description**: Auto-destroy ephemeral environments after TTL.

**Policy Configuration**:
```yaml
ttl_policies:
  dev_ephemeral: 7d
  dev_named: 14d
  staging: never
  production: never
```

**Implementation**:
```python
@app.task
def cleanup_expired_environments():
    policies = load_policies("ttl_policies")

    for tier, ttl in policies.items():
        if ttl == "never":
            continue

        expiry_date = datetime.now() - parse_duration(ttl)

        expired_envs = db.query(Environment) \
            .filter(Environment.tier == tier) \
            .filter(Environment.created_at < expiry_date) \
            .all()

        for env in expired_envs:
            # Send warning 24h before destruction
            if env.created_at < expiry_date - timedelta(hours=24):
                destroy_environment(env.id)
            else:
                send_ttl_warning(env.id)

# Schedule cleanup
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=3, minute=0),  # 3 AM daily
        cleanup_expired_environments.s()
    )
```

### Dependencies

- **M3**: Git integration, webhook handling

### Success Criteria

- [ ] Branch mapping policies correctly route deployments
- [ ] Health gates block failed deployments
- [ ] Resource quotas prevent overallocation
- [ ] TTL policies auto-destroy expired environments

---

## Milestone 5: Production Hardening (Weeks 12-14)

### Objective

Prepare platform for production workloads through observability, security, and disaster recovery.

### Deliverables

#### D5.1: Observability Integration

**Note**: See separate spec (`odooops-observability-enterprise-pack/`) for detailed requirements.

**Summary**:
- OpenTelemetry instrumentation (API, Celery, Odoo workers)
- Prometheus metrics collection
- Loki log aggregation
- AlertManager notification routing

**Verification**:
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Query metrics
curl 'http://localhost:9090/api/v1/query?query=odooops_deployments_total'

# View Grafana dashboard
open http://localhost:3000/d/odooops-overview
```

#### D5.2: Disaster Recovery Procedures

**Description**: Documented and tested recovery procedures.

**Runbook: Full Platform Restore**:
```bash
# 1. Restore control plane database
pg_restore --dbname=control_plane backup-control-plane.sql

# 2. Restore environment databases
for env in $(odooops env list --json | jq -r '.[] | .id'); do
  odooops db restore $env --backup=latest
done

# 3. Redeploy all environments
for env in $(odooops env list --json | jq -r '.[] | .id'); do
  odooops deploy $env --sha=$(git rev-parse HEAD)
done

# 4. Verify health
odooops health check --all
```

**Automated Testing**:
```python
@app.task
def test_disaster_recovery():
    # 1. Create test environment
    env_id = create_test_environment()

    # 2. Backup database
    backup_id = backup_database(env_id)

    # 3. Destroy environment
    destroy_environment(env_id, keep_database=False)

    # 4. Restore from backup
    restore_database(backup_id, env_id)

    # 5. Verify restoration
    assert health_check(env_id)

    # 6. Cleanup
    destroy_environment(env_id)
```

#### D5.3: Security Audit and Hardening

**Security Checklist**:
- [ ] All API endpoints require authentication
- [ ] Database credentials rotated per environment
- [ ] Secrets stored in encrypted vault
- [ ] Network policies isolate environments
- [ ] Audit logs immutable and encrypted
- [ ] TLS 1.3 for all HTTPS traffic
- [ ] Weekly vulnerability scans (Trivy)
- [ ] Penetration testing completed

**Hardening Script**:
```bash
#!/bin/bash
# security-hardening.sh

# Rotate database credentials
for env in $(odooops env list --json | jq -r '.[] | .id'); do
  odooops db rotate-credentials $env
done

# Scan container images
for image in $(docker images --format "{{.Repository}}:{{.Tag}}"); do
  trivy image --severity HIGH,CRITICAL $image
done

# Review audit logs for suspicious activity
odooops audit logs --since=7d --filter=failed_auth > audit-report.txt

# Update SSL certificates
certbot renew --nginx
```

#### D5.4: Documentation and Runbooks

**Required Documentation**:
- **Architecture Diagram**: Control plane, data plane, monitoring plane
- **API Reference**: OpenAPI 3.1 specification
- **CLI Usage Guide**: All commands with examples
- **Deployment Playbook**: Step-by-step deployment procedures
- **Troubleshooting Guide**: Common issues and solutions
- **Disaster Recovery Runbook**: Full restoration procedures
- **Security Policy**: Authentication, encryption, compliance

**Documentation Structure**:
```
docs/
├── architecture.md           # System architecture
├── api-reference.md          # API endpoints (generated from OpenAPI)
├── cli-guide.md              # CLI usage examples
├── deployment-playbook.md    # Deployment procedures
├── troubleshooting.md        # Common issues
├── disaster-recovery.md      # Recovery procedures
└── security-policy.md        # Security standards
```

### Dependencies

- **M1-M4**: All previous milestones complete

### Success Criteria

- [ ] Observability stack deployed (Prometheus, Loki, Grafana)
- [ ] Disaster recovery tested and verified
- [ ] Security audit passed (no critical vulnerabilities)
- [ ] Documentation complete and reviewed
- [ ] Platform achieves 99.5% uptime over 30-day trial period

---

## Risk Mitigation

### Technical Risks

**R1: Database Clone Performance**
- **Mitigation**: Implement incremental clones (schema + selective data)
- **Timeline**: Address during M2 if performance < target

**R2: Build System Bottlenecks**
- **Mitigation**: Horizontal scaling of Celery workers
- **Timeline**: Address during M1 performance testing

**R3: Storage Costs**
- **Mitigation**: Enforce TTL policies and storage quotas
- **Timeline**: Implement during M4 (policy engine)

### Operational Risks

**R4: Production Deployment Failures**
- **Mitigation**: Comprehensive health gates and rollback automation
- **Timeline**: Implement during M1, strengthen during M4

**R5: Credential Leakage**
- **Mitigation**: Encrypted secrets vault, audit logging
- **Timeline**: Implement during M5 (security hardening)

---

## Success Criteria Summary

**MVP Ready** (End of M3):
- [ ] Create/destroy environments via CLI
- [ ] Deploy from git commit SHA
- [ ] Backup/restore databases
- [ ] GitHub webhooks trigger deployments

**Production Ready** (End of M5):
- [ ] 99.5% uptime over 30 days
- [ ] < 200ms API latency (p95)
- [ ] Deployment success rate > 98%
- [ ] Full observability stack
- [ ] Security audit passed
- [ ] Documentation complete

---

**Document Status**: ✅ Implementation plan complete
**Next Steps**: Create task breakdown (tasks.md)
**Review Date**: 2026-03-01 or on major scope changes
