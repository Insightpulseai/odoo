# Plane OKR Mapping to Odoo

**Status**: Active
**Created**: 2026-02-12
**Portfolio Initiative**: PORT-2026-011
**Evidence**: EVID-20260212-006

---

## Overview

This document defines the bidirectional sync mapping between Plane (project management) and Odoo (ERP) for OKR (Objectives and Key Results) tracking.

**Integration Architecture**:
- **Plane**: Workspace → Project → Issue → Custom Fields
- **Odoo**: `project.task` → `ipai_okr.objective` → `ipai_okr.key_result`
- **Sync Engine**: `supabase/functions/plane-sync/index.ts` (938-line Edge Function)
- **Storage**: `supabase/migrations/20250115000000_plane_sync.sql`

---

## Section 1: Plane Schema

### Workspace → Project → Issue Hierarchy

**Workspace** (`plane.workspaces`):
```typescript
interface PlaneWorkspace {
    id: UUID;
    slug: string;  // e.g., "insightpulseai-okr"
    name: string;  // e.g., "InsightPulse AI - OKRs"
    created_at: timestamp;
    updated_at: timestamp;
}
```

**Project** (`plane.projects`):
```typescript
interface PlaneProject {
    id: UUID;
    workspace_id: UUID;  // FK to workspace
    name: string;  // e.g., "OKRs - Q1 2026"
    identifier: string;  // e.g., "OKR"
    description: string;
    created_at: timestamp;
    updated_at: timestamp;
}
```

**Issue** (`plane.issues`):
```typescript
interface PlaneIssue {
    id: UUID;
    project_id: UUID;  // FK to project
    name: string;  // e.g., "Achieve 30% Revenue Growth in Q1 2026"
    description: string;
    state: string;  // "backlog" | "in_progress" | "completed"
    priority: string;  // "low" | "medium" | "high" | "urgent"
    parent_id: UUID | null;  // For Key Results (parent = Objective)
    custom_fields: {
        "OKR Type": "Objective" | "Key Result";
        "Target Value": number;
        "Current Value": number;
        "Progress %": number;
    };
    created_at: timestamp;
    updated_at: timestamp;
}
```

### Custom Fields for OKR Tracking

**Field 1: OKR Type** (Select):
- **Values**: `Objective`, `Key Result`
- **Purpose**: Distinguish Objectives from Key Results
- **Usage**: Objectives are top-level issues, Key Results are child issues

**Field 2: Target Value** (Number):
- **Purpose**: Target metric value for the OKR
- **Example**: 30 (for 30% revenue growth), 10 (for 10 new clients)

**Field 3: Current Value** (Number):
- **Purpose**: Current progress toward target
- **Example**: 5 (for 5 clients acquired out of 10 target)

**Field 4: Progress %** (Number):
- **Purpose**: Calculated percentage: (Current Value / Target Value) * 100
- **Example**: 50 (for 50% progress)

---

## Section 2: Odoo Schema

### `project.task` (Base Model)

**Used For**: Generic project tasks (not OKR-specific)

```python
class ProjectTask(models.Model):
    _name = 'project.task'

    name = fields.Char(string='Task Name', required=True)
    project_id = fields.Many2one('project.project', string='Project')
    user_ids = fields.Many2many('res.users', string='Assignees')
    stage_id = fields.Many2one('project.task.type', string='Stage')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1')
    description = fields.Html(string='Description')
    date_deadline = fields.Date(string='Deadline')
```

### `ipai_okr.objective` (OKR Objective)

**Module**: `addons/ipai/ipai_okr/`

```python
class OKRObjective(models.Model):
    _name = 'ipai_okr.objective'
    _description = 'OKR Objective'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Objective', required=True, tracking=True)
    description = fields.Html(string='Description', tracking=True)
    owner_id = fields.Many2one('res.users', string='Owner', required=True, tracking=True)
    quarter = fields.Selection([
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4')
    ], string='Quarter', required=True, default='Q1', tracking=True)
    year = fields.Integer(string='Year', required=True, default=lambda self: fields.Date.today().year, tracking=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    key_result_ids = fields.One2many('ipai_okr.key_result', 'objective_id', string='Key Results')
    progress = fields.Float(string='Progress %', compute='_compute_progress', store=True)
    plane_issue_id = fields.Char(string='Plane Issue ID', index=True)  # Sync field

    @api.depends('key_result_ids.progress')
    def _compute_progress(self):
        for objective in self:
            if objective.key_result_ids:
                objective.progress = sum(kr.progress for kr in objective.key_result_ids) / len(objective.key_result_ids)
            else:
                objective.progress = 0.0
```

### `ipai_okr.key_result` (OKR Key Result)

```python
class OKRKeyResult(models.Model):
    _name = 'ipai_okr.key_result'
    _description = 'OKR Key Result'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Key Result', required=True, tracking=True)
    description = fields.Html(string='Description', tracking=True)
    objective_id = fields.Many2one('ipai_okr.objective', string='Objective', required=True, ondelete='cascade', tracking=True)
    owner_id = fields.Many2one('res.users', string='Owner', required=True, tracking=True)
    target_value = fields.Float(string='Target Value', required=True, tracking=True)
    current_value = fields.Float(string='Current Value', default=0.0, tracking=True)
    unit = fields.Char(string='Unit', default='%', tracking=True)
    progress = fields.Float(string='Progress %', compute='_compute_progress', store=True, tracking=True)
    state = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked')
    ], string='Status', default='not_started', tracking=True)
    plane_issue_id = fields.Char(string='Plane Issue ID', index=True)  # Sync field

    @api.depends('target_value', 'current_value')
    def _compute_progress(self):
        for kr in self:
            if kr.target_value > 0:
                kr.progress = min((kr.current_value / kr.target_value) * 100, 100.0)
            else:
                kr.progress = 0.0
```

---

## Section 3: Sync Logic

### Bidirectional Sync Architecture

**Supabase Edge Function**: `supabase/functions/plane-sync/index.ts` (938 lines)

**Trigger Methods**:
1. **Realtime CDC**: Postgres `LISTEN/NOTIFY` on `plane.issues` changes
2. **Webhook**: Plane sends webhook on issue update
3. **Scheduled**: Cron job every 15 minutes for reconciliation

**Sync Direction**:
- **Plane → Odoo**: Create/Update Objective or Key Result based on custom field "OKR Type"
- **Odoo → Plane**: Update progress, current value, state changes

### Sync Workflow (Plane → Odoo)

**Step 1: Receive Plane Issue Change**
```typescript
// Realtime CDC or Webhook
const planeIssue = {
    id: "uuid-123",
    name: "Achieve 30% Revenue Growth",
    custom_fields: {
        "OKR Type": "Objective",
        "Target Value": 30,
        "Current Value": 5,
        "Progress %": 16.67
    }
};
```

**Step 2: Determine OKR Type**
```typescript
const okrType = planeIssue.custom_fields["OKR Type"];

if (okrType === "Objective") {
    // Sync to ipai_okr.objective
    await syncToOdooObjective(planeIssue);
} else if (okrType === "Key Result") {
    // Sync to ipai_okr.key_result
    await syncToOdooKeyResult(planeIssue);
}
```

**Step 3: Upsert to Odoo**
```typescript
async function syncToOdooObjective(planeIssue: PlaneIssue) {
    // Check if Odoo objective exists
    const existingObjective = await odoo.search_read('ipai_okr.objective', [
        ['plane_issue_id', '=', planeIssue.id]
    ]);

    if (existingObjective.length > 0) {
        // Update existing
        await odoo.write('ipai_okr.objective', [existingObjective[0].id], {
            name: planeIssue.name,
            description: planeIssue.description,
            state: mapPlaneStateToOdoo(planeIssue.state),
            priority: mapPlanePriorityToOdoo(planeIssue.priority)
        });
    } else {
        // Create new
        await odoo.create('ipai_okr.objective', {
            name: planeIssue.name,
            description: planeIssue.description,
            owner_id: await getOdooUserId(planeIssue.assignee),
            quarter: 'Q1',
            year: 2026,
            priority: mapPlanePriorityToOdoo(planeIssue.priority),
            state: mapPlaneStateToOdoo(planeIssue.state),
            plane_issue_id: planeIssue.id
        });
    }
}
```

**Step 4: Sync Key Results (with Parent Linkage)**
```typescript
async function syncToOdooKeyResult(planeIssue: PlaneIssue) {
    // Find parent Objective (Plane parent_id → Odoo objective_id)
    const parentObjective = await odoo.search_read('ipai_okr.objective', [
        ['plane_issue_id', '=', planeIssue.parent_id]
    ]);

    if (parentObjective.length === 0) {
        console.error('Parent Objective not found for Key Result:', planeIssue.id);
        return;
    }

    // Check if Key Result exists
    const existingKR = await odoo.search_read('ipai_okr.key_result', [
        ['plane_issue_id', '=', planeIssue.id]
    ]);

    if (existingKR.length > 0) {
        // Update existing
        await odoo.write('ipai_okr.key_result', [existingKR[0].id], {
            name: planeIssue.name,
            description: planeIssue.description,
            target_value: planeIssue.custom_fields["Target Value"],
            current_value: planeIssue.custom_fields["Current Value"],
            progress: planeIssue.custom_fields["Progress %"],
            state: mapPlaneStateToOdoo(planeIssue.state)
        });
    } else {
        // Create new
        await odoo.create('ipai_okr.key_result', {
            name: planeIssue.name,
            description: planeIssue.description,
            objective_id: parentObjective[0].id,  // Link to parent Objective
            owner_id: await getOdooUserId(planeIssue.assignee),
            target_value: planeIssue.custom_fields["Target Value"],
            current_value: planeIssue.custom_fields["Current Value"],
            unit: '%',
            state: mapPlaneStateToOdoo(planeIssue.state),
            plane_issue_id: planeIssue.id
        });
    }
}
```

### Sync Workflow (Odoo → Plane)

**Step 1: Odoo Key Result Progress Update**
```python
# User updates current_value in Odoo
key_result = self.env['ipai_okr.key_result'].browse(42)
key_result.write({'current_value': 7})  # Updated from 5 to 7
# Progress auto-calculates: (7 / 10) * 100 = 70%
```

**Step 2: Trigger Sync Edge Function**
```typescript
// Odoo webhook or scheduled sync
const odooKeyResult = {
    id: 42,
    name: "Acquire 10 new enterprise clients",
    target_value: 10,
    current_value: 7,
    progress: 70,
    plane_issue_id: "uuid-456"
};

// Update Plane issue custom fields
await planeRequest('PATCH', `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/issues/${odooKeyResult.plane_issue_id}/`, {
    custom_fields: {
        "Current Value": odooKeyResult.current_value,
        "Progress %": odooKeyResult.progress
    }
});
```

---

## Section 4: Field Mapping

### Issue → Objective Mapping

| Plane Issue | Odoo Objective | Notes |
|-------------|----------------|-------|
| `issue.id` | `objective.plane_issue_id` | Sync key |
| `issue.name` | `objective.name` | Direct copy |
| `issue.description` | `objective.description` | HTML preserved |
| `issue.state` | `objective.state` | See state mapping below |
| `issue.priority` | `objective.priority` | See priority mapping below |
| `issue.assignee` | `objective.owner_id` | User ID lookup |
| `custom_fields["OKR Type"]` | (filter) | Must be "Objective" |
| `custom_fields["Target Value"]` | (not used) | Objectives don't have target values |

### Issue → Key Result Mapping

| Plane Issue | Odoo Key Result | Notes |
|-------------|-----------------|-------|
| `issue.id` | `key_result.plane_issue_id` | Sync key |
| `issue.name` | `key_result.name` | Direct copy |
| `issue.description` | `key_result.description` | HTML preserved |
| `issue.parent_id` | `key_result.objective_id` | Lookup via `plane_issue_id` |
| `issue.state` | `key_result.state` | See state mapping below |
| `issue.assignee` | `key_result.owner_id` | User ID lookup |
| `custom_fields["OKR Type"]` | (filter) | Must be "Key Result" |
| `custom_fields["Target Value"]` | `key_result.target_value` | Direct copy |
| `custom_fields["Current Value"]` | `key_result.current_value` | Direct copy |
| `custom_fields["Progress %"]` | `key_result.progress` | Direct copy (computed in Odoo) |

### State Mapping

| Plane State | Odoo Objective State | Odoo Key Result State |
|-------------|----------------------|-----------------------|
| `backlog` | `draft` | `not_started` |
| `in_progress` | `active` | `in_progress` |
| `completed` | `completed` | `completed` |
| `cancelled` | `cancelled` | `blocked` |

### Priority Mapping

| Plane Priority | Odoo Priority |
|----------------|---------------|
| `low` | `low` |
| `medium` | `medium` |
| `high` | `high` |
| `urgent` | `urgent` |

---

## Section 5: Conflict Resolution

### Last-Write-Wins Strategy

**Rule**: Most recent update (by `updated_at` timestamp) wins.

**Example**:
1. **Plane**: Issue updated at `2026-02-12 10:00 UTC`
2. **Odoo**: Key Result updated at `2026-02-12 10:05 UTC`
3. **Sync**: Odoo change overwrites Plane change

**Implementation**:
```typescript
async function resolveConflict(planeIssue: PlaneIssue, odooKeyResult: OdooKeyResult) {
    const planeTimestamp = new Date(planeIssue.updated_at);
    const odooTimestamp = new Date(odooKeyResult.write_date);

    if (odooTimestamp > planeTimestamp) {
        // Odoo is newer → update Plane
        await syncOdooToPlane(odooKeyResult);
    } else {
        // Plane is newer → update Odoo
        await syncPlaneToOdoo(planeIssue);
    }
}
```

### Manual Merge for Conflicts

**Trigger**: If both Plane and Odoo updated within 5 seconds (potential race condition)

**Action**:
1. Log conflict in `docs/evidence/20260212-2000/plane-bootstrap/conflicts.log`
2. Create Odoo activity: "OKR Sync Conflict - Manual Merge Required"
3. Provide conflict resolution UI in Odoo (show both versions)

---

## Section 6: Verification

### SQL Queries to Verify Sync Integrity

**Check Orphaned Objectives** (Plane issues deleted but Odoo records remain):
```sql
SELECT o.id, o.name, o.plane_issue_id
FROM ipai_okr_objective o
LEFT JOIN plane.issues p ON o.plane_issue_id = p.id
WHERE p.id IS NULL AND o.plane_issue_id IS NOT NULL;
-- Expected: 0 rows (no orphaned records)
```

**Check Missing Sync Keys**:
```sql
SELECT o.id, o.name
FROM ipai_okr_objective o
WHERE o.plane_issue_id IS NULL;
-- Expected: Only manually-created Objectives (not synced from Plane)
```

**Verify Progress Calculation**:
```sql
SELECT
    o.name AS objective,
    o.progress AS objective_progress,
    AVG(kr.progress) AS avg_key_result_progress
FROM ipai_okr_objective o
JOIN ipai_okr_key_result kr ON kr.objective_id = o.id
GROUP BY o.id
HAVING ABS(o.progress - AVG(kr.progress)) > 1;
-- Expected: 0 rows (progress is calculated correctly)
```

**Check Sync Lag** (how stale is data):
```sql
SELECT
    p.id,
    p.name,
    p.updated_at AS plane_updated_at,
    o.write_date AS odoo_updated_at,
    EXTRACT(EPOCH FROM (NOW() - GREATEST(p.updated_at, o.write_date))) AS lag_seconds
FROM plane.issues p
JOIN ipai_okr_objective o ON p.id = o.plane_issue_id
WHERE EXTRACT(EPOCH FROM (NOW() - GREATEST(p.updated_at, o.write_date))) > 900;
-- Expected: 0 rows (all syncs within 15 minutes)
```

---

## Related Documentation

- `supabase/functions/plane-sync/index.ts` - 938-line Edge Function (sync logic)
- `addons/ipai/ipai_okr/__manifest__.py` - Odoo OKR module
- `supabase/migrations/20250115000000_plane_sync.sql` - Supabase schema
- `scripts/plane/bootstrap-workspace.ts` - Workspace bootstrap automation

---

*Mapping documentation created: 2026-02-12*
*Status: Active*
*Portfolio Initiative: PORT-2026-011*
