# PPM Clarity — Task Breakdown

> Actionable task list for Plane + Odoo integration implementation.

**Spec Bundle**: `spec/ppm-clarity-plane-odoo/`
**Status**: Ready for implementation
**Last Updated**: 2026-03-05

---

## Phase 1: Supabase SSOT Schema

### Task 1.1: Create Supabase Migration for SSOT Tables

**Deliverable**: `supabase/migrations/<timestamp>_create_ppm_clarity_schema.sql`

**Implementation**:
```sql
-- ops.work_item_links: Bidirectional ID mapping
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

-- ops.work_item_events: Append-only event ledger
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

-- Indexes
CREATE INDEX idx_work_item_links_plane ON ops.work_item_links(plane_project_id, plane_issue_id);
CREATE INDEX idx_work_item_links_odoo ON ops.work_item_links(odoo_project_id, odoo_task_id);
CREATE INDEX idx_work_item_events_link ON ops.work_item_events(link_id);
CREATE INDEX idx_work_item_events_type ON ops.work_item_events(event_type);
CREATE INDEX idx_work_item_events_idempotency ON ops.work_item_events(idempotency_key);
```

**Validation**:
```bash
supabase db push
psql $SUPABASE_DB_URL -c "\d ops.work_item_links"
psql $SUPABASE_DB_URL -c "\d ops.work_item_events"
```

### Task 1.2: Create RLS Policies for SSOT Tables

**Deliverable**: RLS policies in same migration file

**Implementation**:
```sql
-- ops.work_item_links: service_role only
ALTER TABLE ops.work_item_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON ops.work_item_links
  FOR ALL USING (auth.role() = 'service_role');

-- ops.work_item_events: service_role append-only
ALTER TABLE ops.work_item_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_append" ON ops.work_item_events
  FOR INSERT WITH CHECK (auth.role() = 'service_role');
CREATE POLICY "service_role_read" ON ops.work_item_events
  FOR SELECT USING (auth.role() = 'service_role');
```

**Validation**:
```bash
# Test RLS enforcement
psql $SUPABASE_DB_URL -c "SELECT * FROM ops.work_item_links;"  # Should fail (anon role)
psql $SUPABASE_SERVICE_URL -c "SELECT * FROM ops.work_item_links;"  # Should succeed
```

### Task 1.3: Create Supabase RPC Functions

**Deliverable**: `supabase/functions/ppm_clarity_sync.sql` (or inline in migration)

**Functions**:
```sql
-- 1. Sync Plane → Odoo
CREATE OR REPLACE FUNCTION sync_plane_to_odoo(
  p_plane_issue jsonb,
  p_event_type text,
  p_action text,
  p_idempotency_key text
) RETURNS jsonb AS $$
DECLARE
  v_link_id uuid;
  v_odoo_task_id integer;
BEGIN
  -- Check idempotency
  IF EXISTS (SELECT 1 FROM ops.work_item_events WHERE idempotency_key = p_idempotency_key) THEN
    RETURN jsonb_build_object('status', 'duplicate', 'idempotency_key', p_idempotency_key);
  END IF;

  -- Get or create mapping
  SELECT id, odoo_task_id INTO v_link_id, v_odoo_task_id
  FROM ops.work_item_links
  WHERE plane_project_id = p_plane_issue->>'project'
    AND plane_issue_id = p_plane_issue->>'id';

  -- If no mapping and action is create/update, create Odoo task via external call
  -- (Implementation requires Odoo RPC client, handled in Python wrapper)

  -- Insert event
  INSERT INTO ops.work_item_events (link_id, event_type, source_system, event_data, idempotency_key, success)
  VALUES (v_link_id, 'plane_to_odoo', 'plane', p_plane_issue, p_idempotency_key, true);

  RETURN jsonb_build_object('status', 'success', 'link_id', v_link_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Get completed tasks since last sync
CREATE OR REPLACE FUNCTION get_completed_tasks_since_last_sync()
RETURNS TABLE (
  link_id uuid,
  plane_project_id text,
  plane_issue_id text,
  odoo_task_id integer,
  completed_at timestamptz
) AS $$
BEGIN
  -- Query logic: Find Odoo tasks marked Done since last sync
  -- (Requires integration with Odoo DB or API)
  RETURN QUERY
  SELECT wil.id, wil.plane_project_id, wil.plane_issue_id, wil.odoo_task_id, now()
  FROM ops.work_item_links wil
  WHERE wil.sync_state = 'ok'
    AND wil.last_synced_at < now() - interval '10 minutes';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Get sync conflicts
CREATE OR REPLACE FUNCTION get_sync_conflicts()
RETURNS TABLE (
  link_id uuid,
  plane_project_id text,
  plane_issue_id text,
  odoo_task_id integer,
  last_synced_at timestamptz
) AS $$
BEGIN
  RETURN QUERY
  SELECT id, plane_project_id, plane_issue_id, odoo_task_id, last_synced_at
  FROM ops.work_item_links
  WHERE sync_state = 'needs_review'
  ORDER BY updated_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute to service_role
GRANT EXECUTE ON FUNCTION sync_plane_to_odoo TO service_role;
GRANT EXECUTE ON FUNCTION get_completed_tasks_since_last_sync TO service_role;
GRANT EXECUTE ON FUNCTION get_sync_conflicts TO service_role;
```

**Validation**:
```bash
# Test RPC calls
psql $SUPABASE_SERVICE_URL -c "SELECT sync_plane_to_odoo('{}'::jsonb, 'test', 'create', 'test-key-1');"
```

---

## Phase 2: Odoo RPC Client

### Task 2.1: Create Odoo XML-RPC Client Module

**Deliverable**: `scripts/ppm/odoo_client.py`

**Implementation**:
```python
import xmlrpc.client
import hashlib
import json
from typing import Optional, Dict, List
import os

class OdooClient:
    """Odoo external RPC client for PPM Clarity sync."""

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password

        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = common.authenticate(db, username, password, {})

        if not self.uid:
            raise ValueError("Authentication failed")

        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    def create_project(self, name: str, description: str, stages: List[str]) -> int:
        """Create Odoo project with aligned stages."""
        project_id = self.models.execute_kw(
            self.db, self.uid, self.password,
            'project.project', 'create', [{
                'name': name,
                'description': description,
                'type_ids': [(0, 0, {'name': stage, 'sequence': i+1}) for i, stage in enumerate(stages)]
            }]
        )
        return project_id

    def create_task(self, project_id: int, data: Dict) -> int:
        """Create project.task from Plane work item."""
        task_vals = {
            'name': data['title'],
            'description': data.get('description', ''),
            'project_id': project_id,
            'stage_id': self._get_stage_id(project_id, data.get('stage', 'Backlog')),
            'priority': str(data.get('priority', '0')),
            'planned_hours': data.get('planned_hours', 0.0)
        }
        task_id = self.models.execute_kw(
            self.db, self.uid, self.password,
            'project.task', 'create', [task_vals]
        )
        return task_id

    def update_task(self, task_id: int, data: Dict) -> bool:
        """Update existing task with Plane-owned fields."""
        update_vals = {}
        if 'title' in data:
            update_vals['name'] = data['title']
        if 'description' in data:
            update_vals['description'] = data['description']
        if 'stage' in data:
            # Lookup stage ID by name
            update_vals['stage_id'] = self._get_stage_id(task_id, data['stage'])
        if 'priority' in data:
            update_vals['priority'] = str(data['priority'])

        if not update_vals:
            return True  # No changes

        self.models.execute_kw(
            self.db, self.uid, self.password,
            'project.task', 'write', [[task_id], update_vals]
        )
        return True

    def get_task_details(self, task_id: int) -> Dict:
        """Get task with Odoo-owned fields (timesheets, costs, attachments)."""
        task = self.models.execute_kw(
            self.db, self.uid, self.password,
            'project.task', 'read', [[task_id]], {
                'fields': ['name', 'description', 'user_ids', 'timesheet_ids',
                          'attachment_ids', 'planned_hours', 'effective_hours', 'stage_id']
            }
        )[0]
        return task

    def calculate_hash(self, task: Dict) -> str:
        """Calculate deterministic hash of Odoo-owned fields."""
        canonical_fields = {
            'users': sorted([u['id'] if isinstance(u, dict) else u for u in task.get('user_ids', [])]),
            'timesheets': sorted([t['id'] if isinstance(t, dict) else t for t in task.get('timesheet_ids', [])]),
            'attachments': sorted([a['id'] if isinstance(a, dict) else a for a in task.get('attachment_ids', [])]),
            'planned_hours': task.get('planned_hours', 0.0),
            'effective_hours': task.get('effective_hours', 0.0)
        }
        canonical_json = json.dumps(canonical_fields, sort_keys=True)
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    def _get_stage_id(self, project_id: int, stage_name: str) -> int:
        """Lookup stage ID by name in project."""
        # Implementation: Query project.task.type for stage by name
        pass
```

**Validation**:
```python
# Test script
client = OdooClient(
    url='https://insightpulseai.com/odoo',
    db='odoo',
    username='plane_sync@insightpulseai.com',
    password=os.getenv('ODOO_SERVICE_PASSWORD')
)

# Create test project
project_id = client.create_project(
    name='Test Project',
    description='PPM Clarity test',
    stages=['Draft', 'Backlog', 'In Progress', 'Done']
)
print(f"Created project: {project_id}")

# Create test task
task_id = client.create_task(project_id, {
    'title': 'Test Task',
    'description': 'Test description',
    'stage': 'Backlog',
    'priority': 1,
    'planned_hours': 8.0
})
print(f"Created task: {task_id}")
```

### Task 2.2: Create Plane MCP Client Wrapper

**Deliverable**: `scripts/ppm/plane_mcp_client.py`

**Implementation**:
```python
import httpx
import hashlib
import json
from typing import Dict, List, Optional

class PlaneMCPClient:
    """Wrapper for Plane MCP Server via HTTP gateway."""

    def __init__(self, mcp_gateway_url: str = "http://localhost:8765"):
        self.gateway_url = mcp_gateway_url

    def _invoke_tool(self, tool: str, arguments: Dict) -> Dict:
        """Invoke MCP tool via HTTP gateway."""
        response = httpx.post(
            f"{self.gateway_url}/mcp/plane/invoke",
            json={"tool": tool, "arguments": arguments},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

    def list_projects(self) -> List[Dict]:
        """List all Plane projects."""
        result = self._invoke_tool("list_projects", {})
        return result.get("projects", [])

    def get_work_item(self, project_id: str, issue_id: str) -> Dict:
        """Get Plane work item by ID."""
        result = self._invoke_tool("get_work_item", {
            "project_id": project_id,
            "issue_id": issue_id
        })
        return result

    def update_work_item(self, project_id: str, issue_id: str, data: Dict) -> Dict:
        """Update Plane work item (facts-only writeback)."""
        result = self._invoke_tool("update_work_item", {
            "project_id": project_id,
            "issue_id": issue_id,
            "data": data
        })
        return result

    def create_comment(self, project_id: str, issue_id: str, comment: str) -> Dict:
        """Add comment to Plane work item."""
        result = self._invoke_tool("create_comment", {
            "project_id": project_id,
            "issue_id": issue_id,
            "comment": comment
        })
        return result

    def calculate_hash(self, issue: Dict) -> str:
        """Calculate deterministic hash of Plane-owned fields."""
        canonical_fields = {
            'title': issue.get('name', ''),
            'description': issue.get('description_html', ''),
            'priority': issue.get('priority', ''),
            'labels': sorted(issue.get('label_ids', [])),
            'cycle': issue.get('cycle_id'),
            'state': issue.get('state_id'),
            'estimate': issue.get('estimate_point')
        }
        canonical_json = json.dumps(canonical_fields, sort_keys=True)
        return hashlib.sha256(canonical_json.encode()).hexdigest()
```

**Validation**:
```python
# Test MCP client
client = PlaneMCPClient()

# List projects
projects = client.list_projects()
print(f"Found {len(projects)} projects")

# Get work item
issue = client.get_work_item(
    project_id="project-id-here",
    issue_id="issue-id-here"
)
print(f"Issue: {issue['name']}")
```

---

## Phase 3: n8n Orchestration Workflows

### Task 3.1: Create Plane → Odoo Webhook Workflow

**Deliverable**: `automations/n8n/workflows/ppm-clarity-plane-to-odoo.json`

**Workflow Nodes**:
1. **Webhook Trigger**: Receive Plane webhook
2. **Verify Signature**: HMAC-SHA256 validation
3. **Check Commitment**: Filter for state="Planned" OR label="Committed"
4. **Supabase RPC**: Call `sync_plane_to_odoo()`
5. **Odoo RPC**: Create/update task via Python client
6. **Update Hash**: Store Plane hash in link record

**Testing**:
```bash
# Trigger test webhook
curl -X POST https://n8n.insightpulseai.com/webhook/ppm-clarity/plane \
  -H "Content-Type: application/json" \
  -H "X-Plane-Signature: <hmac-sha256-signature>" \
  -d '{
    "event": "issue",
    "action": "update",
    "webhook_id": "test-webhook",
    "data": {
      "id": "issue-123",
      "project": "project-456",
      "name": "Test Issue",
      "state": {"name": "Planned"}
    }
  }'
```

### Task 3.2: Create Odoo → Plane Completion Workflow

**Deliverable**: `automations/n8n/workflows/ppm-clarity-odoo-to-plane.json`

**Workflow Nodes**:
1. **Cron Trigger**: Every 10 minutes
2. **Supabase RPC**: Call `get_completed_tasks_since_last_sync()`
3. **Loop Tasks**: For each completed task
4. **Plane MCP**: Update work item state to "Done"
5. **Plane MCP**: Add completion comment with metrics
6. **Update Hash**: Store Odoo hash in link record

**Testing**:
```bash
# Manually trigger workflow via n8n API
curl -X POST https://n8n.insightpulseai.com/webhook-test/ppm-clarity-odoo-to-plane
```

### Task 3.3: Create Nightly Reconciliation Workflow

**Deliverable**: `automations/n8n/workflows/ppm-clarity-reconciliation.json`

**Workflow Nodes**:
1. **Cron Trigger**: Daily at 2 AM
2. **Supabase RPC**: Call `get_sync_conflicts()`
3. **Loop Conflicts**: For each conflict
4. **Plane MCP**: Fetch current issue
5. **Odoo RPC**: Fetch current task
6. **Supabase RPC**: Call `reconcile_work_item()`
7. **Apply Resolution**: Update both systems per field ownership

**Testing**:
```bash
# Manually trigger reconciliation
curl -X POST https://n8n.insightpulseai.com/webhook-test/ppm-clarity-reconciliation
```

---

## Phase 4: CI Guardrails

### Task 4.1: Create Spec Validation Workflow

**Deliverable**: `.github/workflows/ppm-clarity-lint.yml`

**Checks**:
- Spec bundle completeness (constitution, PRD, plan, tasks)
- SQL schema validation (parse migration file)
- Python type checking (mypy on clients)
- n8n workflow JSON validation

**Implementation**:
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
      - name: Check Spec Bundle
        run: |
          ./scripts/check-spec-kit.sh spec/ppm-clarity-plane-odoo

  validate-schema:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate SQL Schema
        run: |
          grep -q "CREATE TABLE ops.work_item_links" supabase/migrations/*_ppm_clarity*.sql
          grep -q "CREATE TABLE ops.work_item_events" supabase/migrations/*_ppm_clarity*.sql

  test-python-clients:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Type Check
        run: |
          pip install mypy
          mypy scripts/ppm/odoo_client.py
          mypy scripts/ppm/plane_mcp_client.py
```

### Task 4.2: Create Integration Test Workflow

**Deliverable**: `.github/workflows/ppm-clarity-integration-test.yml`

**Tests**:
```python
# scripts/ppm/tests/test_integration.py
import pytest
from unittest.mock import Mock, patch

def test_plane_to_odoo_sync():
    """Test Plane → Odoo sync with commitment signal."""
    # Mock Plane webhook payload
    plane_payload = {
        "event": "issue",
        "action": "update",
        "data": {
            "id": "test-issue-1",
            "project": "test-project-1",
            "name": "Test Work Item",
            "state": {"name": "Planned"}
        }
    }

    # Test sync logic
    with patch('scripts.ppm.odoo_client.OdooClient') as mock_odoo:
        mock_odoo.create_task.return_value = 123
        # Run sync
        # Assert task created
        # Assert link record created

def test_odoo_to_plane_completion():
    """Test Odoo → Plane completion writeback."""
    # Mock Odoo completed task
    # Test Plane update
    # Assert state changed to Done
    # Assert comment added with metrics

def test_conflict_resolution():
    """Test field ownership conflict resolution."""
    # Mock conflict scenario
    # Test reconciliation logic
    # Assert Plane-owned fields → Odoo
    # Assert Odoo-owned fields → Plane comment
```

---

## Phase 5: Operational Documentation

### Task 5.1: Create Deployment Runbook

**Deliverable**: `docs/ops/PPM_CLARITY_DEPLOYMENT.md`

**Sections**:
- Self-hosted Plane setup (Docker Compose)
- MCP server installation (uvx, environment variables)
- Webhook endpoint configuration (n8n + nginx)
- Supabase migration application
- n8n workflow deployment
- Monitoring setup (Superset dashboards)

### Task 5.2: Create Troubleshooting Guide

**Deliverable**: `docs/ops/PPM_CLARITY_TROUBLESHOOTING.md`

**Sections**:
- Sync failure diagnosis (query ops.work_item_events)
- Webhook signature validation errors
- MCP server connectivity issues
- Odoo RPC authentication failures
- Conflict resolution manual intervention

---

## Phase 6: Verification & Validation

### Task 6.1: End-to-End Smoke Test

**Checklist**:
- [ ] Create Plane project from Portfolio template
- [ ] Create work item with state="Planned"
- [ ] Verify Odoo task created automatically
- [ ] Add timesheet to Odoo task
- [ ] Mark Odoo task as Done
- [ ] Verify Plane state updated to "Done"
- [ ] Verify comment added with timesheet metrics
- [ ] Check ops.work_item_links for mapping
- [ ] Check ops.work_item_events for sync events

### Task 6.2: Performance Testing

**Metrics to Validate**:
- Sync latency: <5 minutes (Plane → Odoo)
- Webhook processing: <2 seconds
- Conflict reconciliation: <30 seconds per conflict
- Database query performance: <100ms for link lookups

### Task 6.3: Security Audit

**Checklist**:
- [ ] RLS policies enforce service_role-only access
- [ ] Webhook signatures verified (reject invalid)
- [ ] Secrets stored in Supabase Vault (not git)
- [ ] Idempotency keys prevent duplicate syncs
- [ ] Audit trail complete (100% event coverage)

---

## Dependencies

| Task | Depends On | Blocker |
|------|------------|---------|
| 1.1 | None | - |
| 1.2 | 1.1 | Tables must exist |
| 1.3 | 1.1, 1.2 | Schema + RLS ready |
| 2.1 | None | - |
| 2.2 | Plane MCP server installed | uvx + PLANE_API_KEY |
| 3.1 | 1.3, 2.1, 2.2 | All clients ready |
| 3.2 | 1.3, 2.1, 2.2 | All clients ready |
| 3.3 | 3.1, 3.2 | Sync workflows deployed |
| 4.1 | None | - |
| 4.2 | 2.1, 2.2 | Clients for mocking |
| 5.1 | 3.1, 3.2, 3.3 | Workflows deployed |
| 5.2 | 3.1, 3.2, 3.3 | Workflows deployed |
| 6.1 | All previous | Full system ready |
| 6.2 | 6.1 | Smoke test passed |
| 6.3 | 6.1 | Smoke test passed |

---

## Completion Criteria

- [ ] All 6 phases completed
- [ ] All 19 tasks marked complete
- [ ] Smoke test checklist 100% passed
- [ ] Performance metrics within targets
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] PR opened with spec bundle + implementation
- [ ] Evidence bundle generated in `web/docs/evidence/<timestamp>/ppm-clarity/`

---

**Status**: Ready for implementation execution (`/speckit.implement`)
