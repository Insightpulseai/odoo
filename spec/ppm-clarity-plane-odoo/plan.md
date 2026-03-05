# Plan: PPM Clarity — Plane.so + Odoo Portfolio/Program/Project Management

## Context

**Why this change is needed:**
- Need enterprise-grade portfolio/program/project management with SSOT governance
- Plane.so provides template-driven planning (3 layers: Portfolio → Program → Project)
- Odoo provides operational execution (tasks, time tracking, invoicing, resource allocation)
- Current gap: No formal sync contract between planning truth (Plane) and operational truth (Odoo)
- Analytics requirement: Rollup from Odoo actuals → Plane dashboards for portfolio health visibility

**Intended outcome:**
- **3-Layer Contract Architecture**: Plane (planning truth), Odoo (operational truth), SSOT (reconciliation truth)
- **Plane Template Structure**: Portfolio/Program/Project templates with states, labels, work item types
- **Bidirectional Sync**: Label-driven provisioning (Plane → Odoo), facts-only writeback (Odoo → Plane)
- **Analytics Integration**: Plane dashboards visualize Odoo operational data via SSOT aggregation
- **SSOT Artifacts**: YAML-based configuration with CI validation following DNS pattern

**User provided extensive PPM Clarity specification** with template structure, sync contract, and analytics requirements.

## Exploration Findings

### Plane.so Capabilities (From WebFetch Research)

**Analytics System (6 Types):**
- ✅ **Overview** - Workspace-level metrics (user stats, project counts, work item totals, intake data)
- ✅ **Projects Analysis** - Health status, lifecycle phases, team composition, resource allocation
- ✅ **Work Items Analysis** - Task distribution by state with "created vs resolved" trends
- ✅ **Cycles Analysis** - Sprint progress tracking with completion percentages
- ✅ **Modules Analysis** - Major workstream progression with status distribution
- ✅ **Intake Analysis** - Request volume trends, acceptance/decline rates
- **Interactive Chart Builder**: Custom dimensions (priority, assignee, state, labels, cycles)
- **CSV Export**: Available for comprehensive data analysis across all views

**Dashboard System (Pro Plan):**
- ✅ **6 Widget Types**: Bar Charts, Line Charts, Area Charts, Donut/Pie Charts, Number Widgets
- **Customization**: Grouping properties (work item types, priority, assignee), metrics (count, estimate points)
- **Visual Themes**: Preset palettes (Modern, Horizon, Earthen) with opacity/border/smoothing controls
- **Interaction**: Hover details, legend filtering, edit/view mode toggling

**Template Structure (From Docs):**
- ✅ **Project Templates** - Predefined states, labels, work item types
- ✅ **GitHub Integration** - Bidirectional sync via bracketed references, label-based triggers, PR lifecycle automation
- ❌ NO formal Portfolio/Program template hierarchy (user-defined convention required)

**SSOT Integration Gaps:**
- ❌ NO Odoo integration patterns
- ❌ NO sync contract for operational data writeback
- ❌ NO rollup/aggregation from external systems to Plane analytics

**Proven SSOT Pattern (DNS):**
- Production-ready workflow: Edit YAML → run generator → commit artifacts → CI validates → applies
- Files: `infra/dns/subdomain-registry.yaml` (SSOT) → generates Terraform tfvars + runtime JSON + validation spec
- CI enforcement: `.github/workflows/dns-sync-check.yml` blocks drift on main branch
- **PPM Clarity sync should replicate this pattern**

**Repository Context:**
- Evidence path: `web/docs/evidence/<YYYYMMDD-HHMM+0800>/<topic>/logs/` (Asia/Manila timezone)
- Spec bundles: 62+ in `spec/` directory following spec-kit framework (constitution, PRD, plan, tasks)
- n8n workflows: 14 canonical automations available for orchestration
- Supabase: Task Bus (`ops.task_queue`) available for async sync operations

## Implementation Plan

### Phase 1: Create Spec Kit Bundle for PPM Clarity

**Goal**: Establish governance framework via Spec Kit artifacts

**Location**: `spec/ppm-clarity-plane-odoo/`

**Files to Create**:
1. **`constitution.md`** - Non-negotiable rules
   - Field ownership rules (Plane vs Odoo)
   - Sync triggers (Plane→Odoo commitment, Odoo→Plane completion/blockers)
   - Idempotency policy + audit requirements
   - Failure modes and rollback strategy

2. **`prd.md`** - Product requirements
   - User stories: portfolio manager, delivery lead, finance controller
   - Plane template structure (states, labels, work item types)
   - Odoo project mapping (execution mirror)
   - Analytics rollup requirements (Odoo → Plane dashboards)

3. **`plan.md`** - Technical implementation plan
   - Phases: template → mapping schema → sync MVP → conflict handling → rollout
   - Integration architecture (n8n orchestration + Supabase SSOT)
   - API contracts (Plane X-API-Key, Odoo RPC)

4. **`tasks.md`** - Task breakdown
   - Concrete tasks for: tables, RPC clients, n8n workflows, tests, evidence

**Key Governance Principles**:
- **IDs are immutable**: Persistent mapping between Plane and Odoo
- **Field ownership** (no ping-pong edits):
  - Plane owns: title, description, priority, labels, cycle, state
  - Odoo owns: assigned users, timesheets, costs, billable flags, attachments, chatter
- **Single writeback direction** per field (explicitly declared)
- **Append-only event ledger** for 100% audit coverage

### Phase 2: Implement Supabase SSOT Schema

**Goal**: Create SSOT mapping and event ledger tables

**Location**: `supabase/migrations/`

**Migration File**: `<timestamp>_create_ppm_clarity_schema.sql`

**Tables to Create**:

1. **`ops.work_item_links`** - Bidirectional ID mapping
   ```sql
   CREATE TABLE ops.work_item_links (
     id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
     plane_project_id text NOT NULL,
     plane_issue_id text NOT NULL,
     odoo_project_id integer,
     odoo_task_id integer,
     sync_state text NOT NULL DEFAULT 'ok' CHECK (sync_state IN ('ok', 'needs_review', 'blocked')),
     last_plane_hash text,
     last_odoo_hash text,
     last_synced_at timestamptz,
     created_at timestamptz NOT NULL DEFAULT now(),
     updated_at timestamptz NOT NULL DEFAULT now(),
     UNIQUE (plane_project_id, plane_issue_id),
     UNIQUE (odoo_project_id, odoo_task_id)
   );
   ```

2. **`ops.work_item_events`** - Append-only audit ledger
   ```sql
   CREATE TABLE ops.work_item_events (
     id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
     link_id uuid REFERENCES ops.work_item_links(id),
     event_type text NOT NULL CHECK (event_type IN ('plane_to_odoo', 'odoo_to_plane', 'reconciliation', 'conflict')),
     source_system text NOT NULL CHECK (source_system IN ('plane', 'odoo', 'n8n')),
     event_data jsonb NOT NULL,
     idempotency_key text UNIQUE,
     success boolean NOT NULL,
     error_message text,
     created_at timestamptz NOT NULL DEFAULT now()
   );
   ```

**RPC Functions** (for service_role only):
- `upsert_work_item_link()` - Atomic mapping creation/update
- `append_work_item_event()` - Safe event logging with idempotency
- `get_sync_conflicts()` - Query items with sync_state='needs_review'

### Phase 3: Implement Integration Clients

**Goal**: Create Plane and Odoo API client modules
**Location**: `scripts/ppm/` (Python modules)

**1. Plane Client** (`plane_client.py`):
```python
class PlaneClient:
    """Plane.so API client using X-API-Key authentication"""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}

    def get_project(self, project_id: str) -> dict:
        """Get project details including template metadata"""
        pass

    def list_issues(self, project_id: str, filters: dict = None) -> list:
        """List work items with optional state/label filters"""
        pass

    def create_issue(self, project_id: str, data: dict) -> dict:
        """Create work item from template"""
        pass

    def update_issue(self, project_id: str, issue_id: str, data: dict) -> dict:
        """Update work item (state, labels, description)"""
        pass

    def calculate_hash(self, issue: dict) -> str:
        """Calculate deterministic hash of Plane-owned fields"""
        # Hash: title, description, priority, labels, cycle, state
        pass
```

**2. Odoo Client** (`odoo_client.py`):
```python
class OdooClient:
    """Odoo external RPC client (XML-RPC/JSON-RPC)"""

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.uid = self._authenticate(username, password)

    def create_project(self, name: str, stages: list) -> int:
        """Create project.project with stages aligned to Plane states"""
        pass

    def create_task(self, project_id: int, data: dict) -> int:
        """Create project.task"""
        pass

    def update_task(self, task_id: int, data: dict) -> bool:
        """Update task (stage, assigned users, time spent)"""
        pass

    def get_task_details(self, task_id: int) -> dict:
        """Get task with timesheets, costs, attachments"""
        pass

    def calculate_hash(self, task: dict) -> str:
        """Calculate deterministic hash of Odoo-owned fields"""
        # Hash: assigned users, timesheets, costs, attachments
        pass
```

**3. Sync Engine** (`sync_engine.py`):
```python
class SyncEngine:
    """Deterministic sync with field ownership enforcement"""

    def __init__(self, plane_client, odoo_client, supabase_client):
        self.plane = plane_client
        self.odoo = odoo_client
        self.supabase = supabase_client

    def plane_to_odoo(self, plane_issue: dict, idempotency_key: str):
        """Sync Plane commitment → Odoo task creation/update"""
        # 1. Check idempotency (query ops.work_item_events)
        # 2. Get or create mapping (ops.work_item_links)
        # 3. Calculate Plane hash (owned fields only)
        # 4. Compare with last_plane_hash
        # 5. If changed: create/update Odoo task
        # 6. Update mapping + append event
        pass

    def odoo_to_plane(self, odoo_task: dict, idempotency_key: str):
        """Sync Odoo completion → Plane state update"""
        # 1. Check idempotency
        # 2. Get mapping
        # 3. Calculate Odoo hash (execution signals only)
        # 4. If changed: update Plane issue (state/labels/comment)
        # 5. Update mapping + append event
        pass

    def reconcile(self, link_id: str):
        """Drift detection + repair using field ownership rules"""
        # 1. Fetch both Plane and Odoo records
        # 2. Calculate hashes
        # 3. Detect conflicts (both changed since last sync)
        # 4. Apply field ownership: Plane wins for plan fields, Odoo wins for exec fields
        # 5. Update both systems + mapping
        pass
```

### Phase 4: Implement n8n Orchestration Workflows

**Goal**: Create n8n workflows for event-driven sync and reconciliation

**Location**: `automations/n8n/workflows/`

**Workflows to Create**:

1. **`ppm-clarity-plane-to-odoo.json`** - Plane webhook handler
   ```json
   {
     "name": "PPM Clarity: Plane → Odoo",
     "nodes": [
       {
         "type": "n8n-nodes-base.webhook",
         "parameters": {
           "path": "ppm-clarity/plane-webhook",
           "responseMode": "onReceived"
         }
       },
       {
         "type": "n8n-nodes-base.function",
         "name": "Extract Commitment Signal",
         "parameters": {
           "functionCode": "// Check if state changed to Planned/In Progress or label 'commit' added"
         }
       },
       {
         "type": "n8n-nodes-base.supabase",
         "name": "Call Supabase RPC",
         "parameters": {
           "operation": "rpc",
           "function": "sync_plane_to_odoo",
           "arguments": "{{ JSON.stringify($json) }}"
         }
       }
     ],
     "connections": {...}
   }
   ```

2. **`ppm-clarity-odoo-to-plane.json`** - Odoo event handler
   ```json
   {
     "name": "PPM Clarity: Odoo → Plane",
     "nodes": [
       {
         "type": "n8n-nodes-base.cron",
         "parameters": {
           "cronExpression": "*/10 * * * *"  // Every 10 minutes
         }
       },
       {
         "type": "n8n-nodes-base.function",
         "name": "Query Odoo Completed Tasks",
         "parameters": {
           "functionCode": "// Query tasks where stage=Done since last run"
         }
       },
       {
         "type": "n8n-nodes-base.supabase",
         "name": "Sync Each Task",
         "parameters": {
           "operation": "rpc",
           "function": "sync_odoo_to_plane",
           "arguments": "{{ JSON.stringify($json) }}"
         }
       }
     ],
     "connections": {...}
   }
   ```

3. **`ppm-clarity-reconciliation.json`** - Nightly drift repair
   ```json
   {
     "name": "PPM Clarity: Reconciliation",
     "nodes": [
       {
         "type": "n8n-nodes-base.cron",
         "parameters": {
           "cronExpression": "0 2 * * *"  // 2 AM daily
         }
       },
       {
         "type": "n8n-nodes-base.supabase",
         "name": "Get Conflicts",
         "parameters": {
           "operation": "rpc",
           "function": "get_sync_conflicts"
         }
       },
       {
         "type": "n8n-nodes-base.function",
         "name": "Reconcile Each Conflict",
         "parameters": {
           "functionCode": "// Apply field ownership rules to resolve drift"
         }
       }
     ],
     "connections": {...}
   }
   ```

**Deployment**: Use `scripts/automations/deploy_n8n_all.py` for idempotent deployment

### Phase 5: Implement CI Guardrails
**Goal**: Add validation and testing workflows

**Location**: `.github/workflows/`

**Workflows to Create**:

1. **`ppm-clarity-lint.yml`** - Schema validation
   ```yaml
   name: PPM Clarity: Lint & Validate
   on:
     pull_request:
       paths:
         - 'spec/ppm-clarity-plane-odoo/**'
         - 'supabase/migrations/*_ppm_clarity*'
         - 'scripts/ppm/**'
         - 'automations/n8n/workflows/ppm-clarity-*'

   jobs:
     validate-spec:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Validate Spec Kit Bundle
           run: |
             ./scripts/check-spec-kit.sh spec/ppm-clarity-plane-odoo

     validate-schema:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Validate SQL Schema
           run: |
             # Check ops.work_item_links and ops.work_item_events tables exist
             grep -q "CREATE TABLE ops.work_item_links" supabase/migrations/*_ppm_clarity*.sql
             grep -q "CREATE TABLE ops.work_item_events" supabase/migrations/*_ppm_clarity*.sql

     test-field-ownership:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Test Field Ownership Contract
           run: |
             cd scripts/ppm
             python -m pytest tests/test_field_ownership.py -v
   ```

2. **`ppm-clarity-integration-test.yml`** - Mocked integration tests
   ```yaml
   name: PPM Clarity: Integration Tests
   on:
     pull_request:
       paths:
         - 'scripts/ppm/**'

   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Setup Python
           uses: actions/setup-python@v5
           with:
             python-version: '3.12'
         - name: Install Dependencies
           run: |
             pip install -r scripts/ppm/requirements.txt
         - name: Run Integration Tests
           run: |
             cd scripts/ppm
             # Test with mocked Plane and Odoo endpoints
             python -m pytest tests/test_integration.py -v
             # Test idempotency
             python -m pytest tests/test_idempotency.py -v
             # Test conflict resolution
             python -m pytest tests/test_conflicts.py -v
   ```

**Test Coverage Requirements**:
- Field ownership enforcement (Plane-owned vs Odoo-owned fields)
- Idempotency (duplicate events with same key return cached result)
- Conflict resolution (both systems changed → field ownership wins)
- Hash calculation determinism (same input → same hash)
- Event ledger completeness (every sync attempt logged)

### Phase 6: Create Operational Documentation

**Goal**: Document the integration architecture and operational procedures

**File:** `docs/ops/PPM_CLARITY_PLANE_ODOO.md` (NEW)

**Content:**
```markdown
# PPM Clarity: Plane + Odoo Integration — Operational Guide

## Overview

Azure-native automation for Odoo 19 development following "Odoo.sh-equivalent" patterns:
- **Build**: Azure Container Registry (ACR) builds from Dockerfile
- **Deploy**: Azure Container Apps with blue-green revisions
- **Upgrade**: Container Apps Jobs with evidence generation
- **Auth**: GitHub Actions → Azure OIDC (federated identity)

## Pipeline Stages

### 1. Build → Push

**Workflow:** `.github/workflows/odoo-azure-deploy.yml`
**Trigger:** Push to `main` branch (paths: `docker/**`, `config/**`, `addons/**`) OR manual dispatch
**Steps:**
1. Azure OIDC login (no secrets, federated identity)
2. `az acr build` - build Docker image in ACR
3. Tag with `$GITHUB_SHA` + `latest`
4. Push to ACR

**Artifacts:** `{ACR_NAME}.azurecr.io/odoo:{sha}` and `odoo:latest`

### 2. Deploy → Verify

**Steps:**
1. `az containerapp update` - deploy new revision with image `odoo:{sha}`
2. Revision suffix: `sha-{first-7-chars}`
3. Traffic split: 100% to new revision (blue-green switch)
4. Verification: List active revisions with traffic weight

**Zero-downtime:** Container Apps automatically routes traffic to new revision after health checks pass.

### 3. Upgrade → Evidence

**Workflow:** `.github/workflows/odoo-azure-upgrade-evidence.yml`
**Trigger:** Manual dispatch with inputs (db_name, modules, environment)
**Steps:**
1. Generate evidence stamp: `YYYYMMDD-HHMM+0800`
2. Create Container Apps Job (ephemeral)
3. Execute: `odoo-bin --database={db} --update={modules} --stop-after-init`
4. Capture logs: job start, status, execution output
5. Write evidence: `web/docs/evidence/{stamp}/odoo-upgrade/`
6. Commit evidence to repo
7. Delete job

**Evidence Structure:**
```
web/docs/evidence/20260305-1430+0800/odoo-upgrade/
├── summary.json          # Status, metadata, log paths
└── logs/
    ├── upgrade-job-start.log
    ├── upgrade-status.log
    └── upgrade-execution.log
```

## Required Azure Resources

| Resource | Naming | Purpose |
|----------|--------|---------|
| Resource Group | `rg-ipai-{env}` | Container for all resources |
| Container Registry | `acripai{env}` | Image artifact storage |
| Container App | `ca-odoo-ipai-{env}` | Odoo runtime |
| Container Apps Environment | `containerapp-env-ipai-{env}` | Shared environment for apps/jobs |
| PostgreSQL Flexible Server | `psql-ipai-{env}` | Odoo database |
| Key Vault | `kv-ipai-{env}` | Runtime secrets |
| Managed Identity | `id-ipai-{env}` | RBAC for Container Apps |

**Environments:** `dev`, `staging`, `production`

## Secrets Inventory

### GitHub Actions Secrets

| Secret | Purpose | Where Used |
|--------|---------|------------|
| `AZURE_SUBSCRIPTION_ID` | Azure subscription | All workflows |
| `AZURE_TENANT_ID` | Azure AD tenant | OIDC login |
| `AZURE_CLIENT_ID` | Managed Identity app ID | OIDC login |
| `ACR_NAME` | Container registry name | Build + deploy |
| `CONTAINERAPP_NAME` | Container app name | Deploy + upgrade |

**Note:** No long-lived credentials. OIDC uses federated identity tokens.

### Azure Key Vault (Runtime)

| Secret | Purpose | Used By |
|--------|---------|---------|
| `ODOO_ADMIN_PASSWORD` | Odoo master password | Container App |
| `POSTGRES_PASSWORD` | Database connection | Container App |
| `ODOO_DB_USER` | Database username | Container App |
| `ODOO_DB_HOST` | PostgreSQL FQDN | Container App |

## Evidence Format

All upgrade operations generate evidence bundles following repo standards:

**Path:** `web/docs/evidence/<YYYYMMDD-HHMM+0800>/<topic>/logs/`
**Timezone:** Asia/Manila (UTC+08:00)
**Summary:** `summary.json` with:
- `timestamp`: Evidence stamp
- `database`: Target database name
- `modules`: Upgraded modules (comma-separated)
- `environment`: Deployment environment
- `status`: `COMPLETE` | `PARTIAL` | `BLOCKED`
- `logs`: Object with paths to log files

**Example:**
```json
{
  "timestamp": "20260305-1430+0800",
  "database": "odoo_prod",
  "modules": "ipai_finance_ppm,ipai_ai_tools",
  "environment": "production",
  "status": "COMPLETE",
  "logs": {
    "job_start": "web/docs/evidence/20260305-1430+0800/odoo-upgrade/logs/upgrade-job-start.log",
    "status": "web/docs/evidence/20260305-1430+0800/odoo-upgrade/logs/upgrade-status.log",
    "execution": "web/docs/evidence/20260305-1430+0800/odoo-upgrade/logs/upgrade-execution.log"
  }
}
```

## OIDC Setup (One-Time)

### Prerequisites
1. Azure subscription with Owner role
2. GitHub repository with Actions enabled
3. Azure AD application registration

### Steps
```bash
# 1. Create Azure AD app registration
az ad app create --display-name "github-oidc-odoo"

# 2. Create service principal
APP_ID=$(az ad app list --display-name "github-oidc-odoo" --query "[0].appId" -o tsv)
az ad sp create --id $APP_ID

# 3. Create federated credential for GitHub Actions
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-main-branch",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:Insightpulseai/odoo:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# 4. Assign RBAC roles
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
az role assignment create \
  --assignee $APP_ID \
  --role "Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID"

# 5. Store secrets in GitHub
# AZURE_CLIENT_ID = $APP_ID
# AZURE_TENANT_ID = $(az account show --query tenantId -o tsv)
# AZURE_SUBSCRIPTION_ID = $SUBSCRIPTION_ID
```

### Verification
```bash
# Test OIDC login in GitHub Actions
# Should succeed without client secret
```

## Rollback Strategy

### Scenario 1: Bad Deployment
```bash
# List revisions
az containerapp revision list \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production

# Activate previous revision
az containerapp revision activate \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production \
  --revision {previous-revision-name}

# Deactivate bad revision
az containerapp revision deactivate \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production \
  --revision {bad-revision-name}
```

### Scenario 2: Failed Upgrade
Evidence in `web/docs/evidence/{stamp}/odoo-upgrade/logs/` will show:
- `upgrade-status.log`: Job status (Failed)
- `upgrade-execution.log`: Odoo upgrade errors

**Recovery:**
1. Fix module code locally
2. Commit + push to trigger deploy workflow
3. Re-run upgrade workflow after successful deploy

## Monitoring

### Key Metrics
- **Deployment Success Rate**: Track via GitHub Actions status
- **Revision Traffic Split**: Monitor Container Apps revisions
- **Upgrade Success Rate**: Parse evidence `status` field from `summary.json`
- **Build Time**: ACR build duration in workflow logs

### Health Checks
```bash
# Container App status
az containerapp show \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production \
  --query "properties.{status:runningStatus,replicas:replicaCount}"

# Recent revisions
az containerapp revision list \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production \
  --query "[?properties.trafficWeight > 0].{name:name,traffic:properties.trafficWeight,active:properties.active}"

# Database connectivity
az postgres flexible-server show \
  --name psql-ipai-production \
  --resource-group rg-ipai-production \
  --query "state"
```

## Troubleshooting

### Issue: OIDC Login Fails
**Symptoms:** `az login` fails with authentication error
**Fix:**
1. Verify federated credential exists: `az ad app federated-credential list --id {APP_ID}`
2. Check subject matches: `repo:Insightpulseai/odoo:ref:refs/heads/main`
3. Ensure RBAC role assigned: `az role assignment list --assignee {APP_ID}`

### Issue: ACR Build Timeout
**Symptoms:** `az acr build` exceeds timeout
**Fix:**
1. Optimize Dockerfile (multi-stage build, layer caching)
2. Increase job timeout in workflow
3. Use ACR Tasks for large builds

### Issue: Container App Not Starting
**Symptoms:** Revision shows 0 replicas
**Fix:**
1. Check logs: `az containerapp logs show --name {app} --resource-group {rg}`
2. Verify secrets in Key Vault: `az keyvault secret list --vault-name kv-ipai-{env}`
3. Check PostgreSQL connectivity: `az postgres flexible-server show`

### Issue: Evidence Not Committing
**Symptoms:** Evidence generated but not in repo
**Fix:**
1. Check git config in workflow (user.name, user.email)
2. Verify `contents: write` permission in workflow
3. Ensure evidence path exists before commit

## References

- **SSOT Model:** `infra/dns/subdomain-registry.yaml` (proven pattern)
- **Workflows:** `.github/workflows/odoo-azure-*.yml`
- **Azure Resources:** `ssot/azure/resources.yaml`
- **Evidence Standards:** `docs/agent_instructions/SSOT.md`
```

## Critical Files to Create/Modify

### Spec Kit Bundle
1. **`spec/ppm-clarity-plane-odoo/constitution.md`** - Governance framework
2. **`spec/ppm-clarity-plane-odoo/prd.md`** - Product requirements
3. **`spec/ppm-clarity-plane-odoo/plan.md`** - Implementation plan
4. **`spec/ppm-clarity-plane-odoo/tasks.md`** - Task breakdown

### Database Schema
5. **`supabase/migrations/<timestamp>_create_ppm_clarity_schema.sql`** - SSOT tables + RPC functions

### Integration Clients
6. **`scripts/ppm/plane_client.py`** - Plane API client (X-API-Key auth)
7. **`scripts/ppm/odoo_client.py`** - Odoo RPC client (XML-RPC/JSON-RPC)
8. **`scripts/ppm/sync_engine.py`** - Deterministic sync with field ownership
9. **`scripts/ppm/requirements.txt`** - Python dependencies

### n8n Workflows
10. **`automations/n8n/workflows/ppm-clarity-plane-to-odoo.json`** - Plane webhook handler
11. **`automations/n8n/workflows/ppm-clarity-odoo-to-plane.json`** - Odoo completion sync
12. **`automations/n8n/workflows/ppm-clarity-reconciliation.json`** - Nightly drift repair

### CI/CD
13. **`.github/workflows/ppm-clarity-lint.yml`** - Schema and spec validation
14. **`.github/workflows/ppm-clarity-integration-test.yml`** - Mocked integration tests

### Tests
15. **`scripts/ppm/tests/test_field_ownership.py`** - Field ownership contract tests
16. **`scripts/ppm/tests/test_idempotency.py`** - Idempotency enforcement tests
17. **`scripts/ppm/tests/test_conflicts.py`** - Conflict resolution tests
18. **`scripts/ppm/tests/test_integration.py`** - End-to-end integration tests (mocked)

### Documentation
19. **`docs/ops/PPM_CLARITY_PLANE_ODOO.md`** - Operational guide

## Existing Resources to Leverage

- **SSOT Pattern:** `infra/dns/subdomain-registry.yaml` (proven YAML → generator → CI validation pattern)
- **Spec Kit Framework:** 62+ existing spec bundles following constitution/PRD/plan/tasks structure
- **Supabase Schema:** `ops.*` tables with append-only event patterns (e.g., `ops.run_events`)
- **n8n Orchestration:** 14 canonical workflows with deployment automation via `scripts/automations/deploy_n8n_all.py`
- **Evidence Standards:** `web/docs/evidence/` path structure, Asia/Manila timezone, STATUS= semantics
- **CI Patterns:** 153 existing workflows for validation, testing, and guardrails

## Verification Strategy

### Pre-Implementation Validation
1. ✅ Spec Kit bundle complete with all 4 artifacts (constitution, PRD, plan, tasks)
2. ✅ Supabase migration SQL validates (no syntax errors)
3. ✅ Python clients have proper type hints and docstrings
4. ✅ n8n workflows deploy successfully via `deploy_n8n_all.py`
5. ✅ CI workflows have correct paths and triggers
6. ✅ No hardcoded credentials (all use environment variables)

### Unit Testing (Python)
```bash
cd scripts/ppm
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

**Required Coverage**:
- `test_field_ownership.py`: Verify Plane-owned vs Odoo-owned field separation
- `test_idempotency.py`: Duplicate idempotency_key returns cached result
- `test_conflicts.py`: Field ownership rules resolve drift correctly
- `test_hash_determinism.py`: Same input produces same hash

### Integration Testing (Mocked APIs)
```bash
cd scripts/ppm
python -m pytest tests/test_integration.py -v
```

**Test Scenarios**:
1. Plane issue → state=Planned → creates Odoo task + mapping
2. Odoo task → stage=Done → updates Plane state + event log
3. Concurrent changes → reconciliation → field ownership wins
4. Missing mapping → creates new link + both-way sync
5. Idempotent replay → returns cached response

### End-to-End Verification (Manual)

**Setup Prerequisites**:
1. Plane workspace with PPM Clarity template applied
2. Odoo instance with `project` module installed
3. Supabase migration applied (ops.work_item_links + ops.work_item_events exist)
4. n8n workflows deployed and active
5. Environment variables configured (PLANE_API_KEY, ODOO_URL, SUPABASE_URL)

**Verification Checklist** (from user specification):
- [ ] Creating Plane project from template → new Odoo project with aligned stages
- [ ] Plane work item → state=Planned → creates Odoo task + link row in ops.work_item_links
- [ ] Odoo task → stage=Done → updates Plane state + ledger row in ops.work_item_events
- [ ] Re-running same event → idempotent (no duplicate tasks)
- [ ] Drift reconciliation → detects mismatched title/state → resolves per field ownership
- [ ] All events recorded in ops.work_item_events (100% audit coverage)

### Success Criteria

- ✅ Spec Kit bundle exists with complete governance framework
- ✅ Supabase schema has bidirectional mapping + append-only event ledger
- ✅ Python clients implement field ownership contract correctly
- ✅ n8n workflows trigger on correct events (Plane webhook, Odoo completion, nightly reconciliation)
- ✅ CI guardrails prevent contract violations (field ownership, idempotency, schema drift)
- ✅ Integration tests pass with mocked APIs (>95% coverage)
- ✅ End-to-end manual verification completes all 6 checklist items
- ✅ Operational documentation provides complete troubleshooting guide

## Implementation Notes

### Architecture Decisions

**Why Supabase for SSOT?**
- Already the repo's "control plane" with 42 Edge Functions, Vault, Auth, Realtime
- Append-only `ops.*` schema pattern proven with `ops.run_events` (90-day retention)
- RPC functions provide service_role-only access for atomic operations
- PostgreSQL JSONB for flexible event data without schema rigidity

**Why n8n for Orchestration?**
- 14 canonical workflows already deployed with proven patterns
- Idempotent deployment via `scripts/automations/deploy_n8n_all.py`
- Webhook + cron trigger support for both real-time and batch sync
- Retry logic and error handling built-in

**Why Field Ownership?**
- Prevents "ping-pong" edits where both systems fight over same field
- Explicit contract: Plane = plan truth, Odoo = execution truth
- Deterministic conflict resolution without manual intervention
- Each system owns what it does best (Plane=workflow, Odoo=time/cost)

### Key Design Patterns

**Immutable ID Mapping**:
- Every Plane item gets persistent UUID in `ops.work_item_links`
- UNIQUE constraints on both (plane_project_id, plane_issue_id) and (odoo_project_id, odoo_task_id)
- Prevents duplicate mappings and orphaned records

**Hash-Based Change Detection**:
- Calculate deterministic hash of system-owned fields only
- Compare with `last_plane_hash` / `last_odoo_hash` to detect changes
- Only sync when hash differs (avoid no-op updates)
- Hashes stored in mapping table for drift detection

**Append-Only Event Ledger**:
- Every sync attempt logged to `ops.work_item_events` (success or failure)
- Idempotency via UNIQUE constraint on `idempotency_key`
- Full audit trail for compliance and debugging
- Event replay capability for disaster recovery

**Nightly Reconciliation**:
- Query `ops.work_item_links` for items with mismatched hashes
- Fetch both Plane and Odoo records
- Apply field ownership rules to resolve drift
- Update both systems + log reconciliation event
- Prevents slow drift accumulation over time

### Failure Modes & Mitigations

**Plane API Down**:
- n8n webhook returns 503 → Plane retries automatically
- Reconciliation job will catch up during next nightly run
- No data loss (events queued in Plane webhook queue)

**Odoo API Down**:
- Sync engine logs failure event with error_message
- n8n retry logic attempts up to 3 times with exponential backoff
- Manual investigation via `get_sync_conflicts()` RPC

**Concurrent Edits (Race Condition)**:
- Last-write-wins within same system (Plane or Odoo)
- Cross-system conflicts resolved by field ownership
- Example: User A changes title in Plane, User B changes assignee in Odoo → both succeed (different field owners)

**Schema Migration (Breaking Change)**:
- Add new fields as nullable initially
- Backfill existing records via data migration
- Update hash calculation to include new fields
- Remove old fields only after full sync cycle completes

### Future Enhancements

**Analytics Rollup** (not in MVP):
- Additional `ops.work_item_analytics` table
- Aggregate Odoo timesheets → Plane custom fields
- Plane dashboards visualize Odoo execution data
- Requires custom Plane API endpoints (may need Plane Pro plan feature request)

**Multi-Workspace Support**:
- Add `workspace_id` to mapping tables
- Support multiple Plane workspaces → single Odoo instance
- Workspace-level field ownership overrides

**Real-Time Sync** (alternative to webhooks):
- Plane Realtime API subscription (if available)
- Odoo `ir.cron` trigger → webhook to n8n
- Sub-minute sync latency vs. 10-minute polling
