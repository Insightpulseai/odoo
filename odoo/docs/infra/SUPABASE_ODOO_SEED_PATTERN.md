# Supabase-Driven Odoo Seeding Pattern

**Document:** Canonical pattern for Supabase as master, Odoo as execution surface
**Stack:** Supabase (PostgreSQL + Edge Functions) → Odoo CE 18 (JSON-RPC)
**Integration:** Builds on `ops.odoo_bindings` context layer

---

## Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                    SUPABASE → ODOO SEEDING FLOW                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐                      ┌─────────────────┐          │
│  │  odoo_seed.*    │ ─── Edge Function ──▶│  Odoo CE 18     │          │
│  │  (Master)       │     (JSON-RPC)       │  (Execution)    │          │
│  ├─────────────────┤                      ├─────────────────┤          │
│  │ programs        │                      │ project.project │          │
│  │ projects        │ ◀── Shadow Sync ──── │ project.task    │          │
│  │ tasks           │     (Verification)   │ x_external_ref  │          │
│  │ shadow_*        │                      │                 │          │
│  └─────────────────┘                      └─────────────────┘          │
│                                                                         │
│  GitHub Actions / n8n ─── Triggers ──▶ Edge Functions                  │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Source of Truth: Supabase

| Schema | Table | Purpose |
|--------|-------|---------|
| `odoo_seed` | `programs` | OKR/Logframe/Portfolio definitions |
| `odoo_seed` | `projects` | Canonical project definitions |
| `odoo_seed` | `tasks` | Canonical task definitions |
| `odoo_seed` | `shadow_projects` | Mirror of actual Odoo state |
| `odoo_seed` | `shadow_tasks` | Mirror of actual Odoo state |
| `odoo_seed` | `sync_runs` | Audit log of sync operations |

### Execution Surface: Odoo

| Model | Custom Field | Purpose |
|-------|--------------|---------|
| `project.project` | `x_external_ref` | Links to `odoo_seed.projects.external_ref` |
| `project.task` | `x_external_ref` | Links to `odoo_seed.tasks.external_ref` |

### Edge Functions

| Function | Direction | Purpose |
|----------|-----------|---------|
| `seed-odoo-finance` | Supabase → Odoo | Push seed data to Odoo |
| `shadow-odoo-finance` | Odoo → Supabase | Pull actual state for verification |

---

## Database Schema

### Migration: `20260121_odoo_seed_schema.sql`

```sql
-- Programs (OKR / Logframe / Portfolio)
CREATE TABLE odoo_seed.programs (
    id uuid PRIMARY KEY,
    slug text UNIQUE NOT NULL,
    name text NOT NULL,
    program_type text DEFAULT 'ppm',  -- 'ppm', 'okr', 'logframe', 'portfolio'
    parent_slug text REFERENCES odoo_seed.programs(slug),
    active boolean DEFAULT true
);

-- Projects (maps to project.project)
CREATE TABLE odoo_seed.projects (
    id uuid PRIMARY KEY,
    program_slug text REFERENCES odoo_seed.programs(slug),
    external_ref text UNIQUE NOT NULL,
    name text NOT NULL,
    company_name text NOT NULL,
    manager_email text,
    visibility text DEFAULT 'employees',  -- CE field
    allow_dependencies boolean DEFAULT true,  -- CE field
    odoo_project_id int,  -- Populated after sync
    sync_enabled boolean DEFAULT true
);

-- Tasks (maps to project.task)
CREATE TABLE odoo_seed.tasks (
    id uuid PRIMARY KEY,
    project_external_ref text REFERENCES odoo_seed.projects(external_ref),
    external_ref text UNIQUE NOT NULL,
    name text NOT NULL,
    stage_name text DEFAULT 'To Do',
    tag_names text[],
    assignee_email text,
    depends_on_refs text[],  -- Task dependency refs
    odoo_task_id int  -- Populated after sync
);
```

---

## Edge Function: seed-odoo-finance

### Endpoint

```bash
POST ${SUPABASE_URL}/functions/v1/seed-odoo-finance
Authorization: Bearer ${SEED_RUN_TOKEN}
```

### Flow

1. Load active projects from `odoo_seed.projects`
2. For each project:
   - Resolve `company_name` → `res.company.id`
   - Resolve `manager_email` → `res.users.id`
   - Upsert to `project.project` using `x_external_ref`
   - Update `odoo_project_id` in seed table
3. For each task:
   - Upsert to `project.task` using `x_external_ref`
   - Set dependencies via `depend_on_ids`
4. Log run to `odoo_seed.sync_runs`

### Response

```json
{
  "ok": true,
  "run_id": "uuid",
  "status": "success",
  "projects_synced": 5,
  "tasks_synced": 42,
  "results": {
    "projects": [
      { "external_ref": "FIN_CLOSE_PROJ", "odoo_id": 123, "action": "created" }
    ]
  }
}
```

---

## Edge Function: shadow-odoo-finance

### Endpoint

```bash
POST ${SUPABASE_URL}/functions/v1/shadow-odoo-finance
Authorization: Bearer ${SEED_RUN_TOKEN}
```

### Flow

1. Query Odoo for all `project.project` with `x_external_ref`
2. Upsert to `odoo_seed.shadow_projects`
3. Query Odoo for all `project.task` with `x_external_ref`
4. Upsert to `odoo_seed.shadow_tasks`
5. Run verification queries
6. Log run to `odoo_seed.sync_runs`

### Verification Views

```sql
-- Missing in Odoo (seed exists, shadow doesn't)
SELECT * FROM odoo_seed.v_missing_in_odoo;

-- Orphan in Odoo (shadow exists, seed doesn't)
SELECT * FROM odoo_seed.v_orphan_in_odoo;

-- Name drift (seed name != odoo name)
SELECT * FROM odoo_seed.v_name_drift;
```

---

## GitHub Actions Workflow

### `seed-odoo-finance.yml`

Triggers:
- Manual dispatch with action choice: `seed`, `shadow`, `both`
- Push to `main` when seed files change

```yaml
on:
  workflow_dispatch:
    inputs:
      action:
        type: choice
        options: [seed, shadow, both]
  push:
    branches: [main]
    paths:
      - 'supabase/migrations/20260121_odoo_seed_schema.sql'
      - 'supabase/seed/odoo/**'
```

---

## Usage Examples

### 1. Insert Seed Data

```sql
-- Insert program
INSERT INTO odoo_seed.programs (slug, name, program_type)
VALUES ('fin-close', 'Finance Close & Tax Compliance', 'ppm');

-- Insert project
INSERT INTO odoo_seed.projects (
  program_slug, external_ref, name, company_name, manager_email
) VALUES (
  'fin-close',
  'FIN_CLOSE_PROJ',
  'Month-End Financial Closing Standardization',
  'TBWA\SMP',
  'rey.meran@tbwa-smp.com'
);

-- Insert task
INSERT INTO odoo_seed.tasks (
  project_external_ref, external_ref, name, stage_name, assignee_email
) VALUES (
  'FIN_CLOSE_PROJ',
  'FIN_CLOSE_T001',
  'Configure chart of accounts',
  'To Do',
  'beng.manalo@tbwa-smp.com'
);
```

### 2. Trigger Seed

```bash
# Via curl
curl -X POST \
  -H "Authorization: Bearer $SEED_RUN_TOKEN" \
  "${SUPABASE_URL}/functions/v1/seed-odoo-finance"

# Via GitHub Actions
gh workflow run seed-odoo-finance.yml -f action=both
```

### 3. Verify in Odoo DB

```bash
ssh root@178.128.112.214

docker exec odoo-erp-prod psql -U odoo -d production -c "
  SELECT id, name, x_external_ref
  FROM project_project
  WHERE x_external_ref = 'FIN_CLOSE_PROJ';
"
```

### 4. Check Verification Views

```sql
-- In Supabase
SELECT * FROM odoo_seed.v_missing_in_odoo;
SELECT * FROM odoo_seed.v_name_drift;
```

---

## Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `SUPABASE_URL` | Edge Functions (auto) | Supabase API URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Edge Functions (auto) | Service role key |
| `ODOO_URL` | Supabase secrets | Odoo instance URL |
| `ODOO_DB` | Supabase secrets | Odoo database name |
| `ODOO_USER` | Supabase secrets | Odoo API user login |
| `ODOO_PASSWORD` | Supabase secrets | Odoo API password |
| `SEED_RUN_TOKEN` | Supabase secrets + GitHub | Shared auth token |

---

## Prerequisites

### 1. Custom Fields in Odoo

Add `x_external_ref` field to `project.project` and `project.task`:

```python
# In ipai_ppm or custom module
class ProjectProject(models.Model):
    _inherit = 'project.project'

    x_external_ref = fields.Char(
        string='External Reference',
        index=True,
        copy=False,
        help='Unique reference for external system integration'
    )

class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_external_ref = fields.Char(
        string='External Reference',
        index=True,
        copy=False,
        help='Unique reference for external system integration'
    )
```

### 2. Odoo API User

Create a service user in Odoo:
- Login: `seed_bot@insightpulseai.com`
- Groups: `Project / Administrator`
- Generate API password

---

## Rollback

### Stop Seeding

```bash
# Delete workflow
rm .github/workflows/seed-odoo-finance.yml

# Delete functions
supabase functions delete seed-odoo-finance
supabase functions delete shadow-odoo-finance
```

### Remove Schema (DESTRUCTIVE)

```sql
DROP SCHEMA IF EXISTS odoo_seed CASCADE;
```

### Revert Odoo Data

```sql
-- Clear x_external_ref (keeps projects/tasks)
UPDATE project_project SET x_external_ref = NULL WHERE x_external_ref IS NOT NULL;
UPDATE project_task SET x_external_ref = NULL WHERE x_external_ref IS NOT NULL;
```

---

## Secrets Management

**CRITICAL:** All secrets must be managed via Supabase secrets or Vault. See [SECRETS_MANAGEMENT.md](./SECRETS_MANAGEMENT.md) for:

- Setting secrets via CLI (`supabase functions secrets set`)
- Local development with `.env.local`
- HashiCorp Vault integration (optional)
- Secret rotation procedures
- Emergency response procedures

**Quick Setup:**

```bash
# Set all required secrets
supabase functions secrets set \
  ODOO_URL="https://erp.insightpulseai.com" \
  ODOO_DB="production" \
  ODOO_USER="seed_bot@insightpulseai.com" \
  ODOO_PASSWORD="<password>" \
  SEED_RUN_TOKEN="$(openssl rand -hex 32)"

# Verify
supabase functions secrets list
```

---

## Related Documentation

- [SECRETS_MANAGEMENT.md](./SECRETS_MANAGEMENT.md) - **Secrets boundary pattern**
- [ops.odoo_bindings](../migrations/202601080003_4502_OPS_ODOO_BINDINGS.sql) - Context resolution layer
- [CE_OCA_PROJECT_STACK.md](../CE_OCA_PROJECT_STACK.md) - Project module parity
- [MCP_JOBS_SYSTEM.md](./MCP_JOBS_SYSTEM.md) - Job queue pattern

---

*Last Updated: 2026-01-21*
*Version: 1.0.0*
