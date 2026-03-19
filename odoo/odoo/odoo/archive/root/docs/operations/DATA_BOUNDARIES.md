# Data Boundaries: Odoo vs Supabase System of Record

## Overview

OdooOps Sh operates in a hybrid architecture where **Odoo PostgreSQL** and **Supabase PostgreSQL** are separate databases with distinct responsibilities. Understanding which data lives where—and why—is critical for maintaining data integrity, avoiding duplication, and ensuring proper synchronization patterns.

**Core Principle**: Each system is the **System of Record (SOR)** for its domain. Cross-system references use external IDs, not foreign keys.

## System of Record Split

### Odoo PostgreSQL: Business Data SOR

**What Lives Here**:
- All business domain data (sales, purchases, accounting, HR, projects)
- Odoo internal tables (`res_users`, `res_partner`, `ir_model`, etc.)
- Custom module data (`ipai_*` modules)
- Transactional workflows (invoices, orders, timesheets)
- Master data (customers, suppliers, products, employees)

**Why Odoo Owns This**:
- Odoo ORM (BaseModel) provides business logic layer
- Complex constraints and triggers for business rules
- Integration with Odoo's security model (`ir.model.access`, `ir.rule`)
- Backwards compatibility with existing modules
- No need for real-time pub/sub (Odoo's polling is sufficient)

**Connection Details**:
- **Host**: `localhost` (self-hosted) or DigitalOcean managed database
- **Port**: 5432
- **Database**: `odoo`, `odoo_dev`, `odoo_staging`
- **Access**: Odoo server process only, no direct client connections

### Supabase PostgreSQL: Control Plane SOR

**What Lives Here**:
- OdooOps control plane (`ops.*` schema)
- Project/environment configuration
- Build/deploy run queue
- Artifact metadata (not files—S3 for blobs)
- Backup metadata (not dumps—S3 for files)
- User authentication (`auth.users`)
- Access control policies (`ops.project_members`, `ops.roles`)

**Why Supabase Owns This**:
- Real-time subscriptions for live dashboards (Supabase Realtime)
- Row Level Security (RLS) for multi-tenant access control
- Auto-generated REST API via PostgREST
- Edge Functions for webhooks and automation
- Independent scaling from Odoo workload
- No dependency on Odoo server uptime for control plane operations

**Connection Details**:
- **Host**: `spdtwktxdalcfigzeqrz.supabase.co`
- **Port**: 6543 (transaction pooler) or 5432 (direct)
- **Database**: `postgres`
- **Access**: Public API (filtered by RLS), Edge Functions, workers via service role key

## Data Ownership Rules

### Rule 1: No Cross-Database Foreign Keys

**Problem**: PostgreSQL foreign keys cannot span databases.

**Solution**: Use external identifiers for references.

**Example**:
```sql
-- ❌ WRONG: Cannot create FK to different database
CREATE TABLE ops.runs (
    odoo_user_id INTEGER REFERENCES odoo.res_users(id)  -- FAILS
);

-- ✅ CORRECT: Store external ID as text
CREATE TABLE ops.runs (
    created_by TEXT NOT NULL,  -- Maps to auth.users.id or odoo.res_users.login
    CONSTRAINT created_by_format CHECK (created_by ~ '^[a-z0-9_-]+@')
);
```

### Rule 2: Metadata in Supabase, Blobs in S3

**Problem**: Storing large files in PostgreSQL bloats database and slows queries.

**Solution**: Store metadata in `ops.artifacts`, actual files in S3.

**Example**:
```sql
-- ops.artifacts table
INSERT INTO ops.artifacts (run_id, artifact_type, storage_path, size_bytes, digest)
VALUES (
    'run-abc123',
    'image',
    'ghcr.io/org/odoo-ce:abc123',
    1234567890,
    'sha256:abcd1234...'
);
```

**Artifact Types and Storage Locations**:
| Type | Storage | Example Path |
|------|---------|--------------|
| `image` | GHCR | `ghcr.io/insightpulseai/odoo-ce:v1.2.3` |
| `sbom` | S3 | `s3://odooops-artifacts/proj-123/run-abc/sbom.json` |
| `logs` | S3 | `s3://odooops-artifacts/proj-123/run-abc/build.log.gz` |
| `evidence` | S3 | `s3://odooops-artifacts/proj-123/run-abc/deploy-evidence.json` |
| `manifest` | S3 | `s3://odooops-artifacts/proj-123/run-abc/manifest.yaml` |

### Rule 3: Supabase as Control Plane, Not Data Lake

**Problem**: Duplicating Odoo data to Supabase for analytics creates sync drift.

**Solution**: Query Odoo via foreign data wrapper (FDW) or export to data warehouse.

**Anti-Pattern**:
```sql
-- ❌ WRONG: Copying Odoo data to Supabase
CREATE TABLE ops.odoo_invoices_copy (
    invoice_id INTEGER,
    amount_total NUMERIC,
    state TEXT
);

-- Requires constant ETL sync, dual maintenance
```

**Correct Pattern**:
```sql
-- ✅ CORRECT: Use FDW for cross-database queries
CREATE EXTENSION postgres_fdw;

CREATE SERVER odoo_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'localhost', dbname 'odoo', port '5432');

CREATE FOREIGN TABLE ops.odoo_invoices (
    id INTEGER,
    amount_total NUMERIC,
    state TEXT
) SERVER odoo_server OPTIONS (schema_name 'public', table_name 'account_move');

-- Or: Export to ClickHouse/BigQuery for analytics
```

### Rule 4: User Identity Mapping

**Problem**: Odoo users (`res_users`) and Supabase users (`auth.users`) are separate.

**Solution**: Create mapping table in Supabase.

**Schema**:
```sql
-- Supabase: ops.odoo_users mapping
CREATE TABLE ops.odoo_users (
    auth_user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    odoo_user_id INTEGER NOT NULL,
    odoo_login TEXT NOT NULL UNIQUE,
    odoo_instance TEXT NOT NULL,  -- 'dev', 'staging', 'prod'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Example data
INSERT INTO ops.odoo_users (auth_user_id, odoo_user_id, odoo_login, odoo_instance)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',  -- Supabase auth.users.id
    123,                                       -- Odoo res_users.id
    'admin@insightpulseai.com',               -- Odoo login
    'prod'
);
```

**Usage**:
```typescript
// In Next.js console
const { data: user } = await supabase.auth.getUser();
const { data: odooUser } = await supabase
    .from('odoo_users')
    .select('odoo_user_id, odoo_login')
    .eq('auth_user_id', user.id)
    .single();

// Now you can reference odooUser.odoo_login in ops.runs metadata
```

## Synchronization Patterns

### Pattern 1: Event-Driven Sync (Recommended)

**Use Case**: Odoo triggers create corresponding Supabase records.

**Implementation**:
```python
# Odoo custom module: ipai_odoo_ops
from odoo import models, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        project = super().create(vals)

        # Trigger Supabase Edge Function
        self.env['ir.http']._rpc_api_call(
            url='https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/ops-ingest',
            method='POST',
            data={
                'event_type': 'project_created',
                'project_id': f'odoo-{project.id}',
                'name': project.name,
                'odoo_version': '19.0'
            }
        )

        return project
```

**Edge Function** (`supabase/functions/ops-ingest/index.ts`):
```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
    const { event_type, project_id, name, odoo_version } = await req.json();

    if (event_type === 'project_created') {
        const supabase = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);

        await supabase.from('projects').insert({
            project_id,
            name,
            repo_slug: `insightpulseai/${project_id}`,
            odoo_version
        });
    }

    return new Response(JSON.stringify({ ok: true }));
});
```

### Pattern 2: Periodic Reconciliation

**Use Case**: Ensure Supabase metadata matches Odoo reality.

**Implementation**:
```sql
-- Edge Function cron job (hourly)
CREATE OR REPLACE FUNCTION ops.reconcile_odoo_projects()
RETURNS void AS $$
DECLARE
    fdw_project RECORD;
    ops_project RECORD;
BEGIN
    -- Compare foreign table to ops.projects
    FOR fdw_project IN SELECT id, name FROM ops.odoo_projects_fdw LOOP
        SELECT * INTO ops_project FROM ops.projects WHERE project_id = 'odoo-' || fdw_project.id;

        IF NOT FOUND THEN
            -- Create missing project
            INSERT INTO ops.projects (project_id, name, repo_slug, odoo_version)
            VALUES ('odoo-' || fdw_project.id, fdw_project.name, 'auto-generated', '19.0');
        ELSIF ops_project.name != fdw_project.name THEN
            -- Update name mismatch
            UPDATE ops.projects SET name = fdw_project.name WHERE project_id = ops_project.project_id;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### Pattern 3: Read-Through Cache

**Use Case**: Cache Odoo data in Supabase for performance.

**Implementation**:
```sql
-- Materialized view refreshed nightly
CREATE MATERIALIZED VIEW ops.odoo_project_summary AS
SELECT
    'odoo-' || p.id AS project_id,
    p.name,
    COUNT(t.id) AS task_count,
    SUM(t.planned_hours) AS total_hours
FROM ops.odoo_projects_fdw p
LEFT JOIN ops.odoo_tasks_fdw t ON t.project_id = p.id
GROUP BY p.id, p.name;

CREATE UNIQUE INDEX ON ops.odoo_project_summary (project_id);

-- Refresh via Edge Function cron (daily at 2 AM)
REFRESH MATERIALIZED VIEW CONCURRENTLY ops.odoo_project_summary;
```

## Consistency Guarantees

### Strong Consistency (Within Same Database)

**Supabase**:
- `ops.runs` and `ops.run_events` are always consistent
- RPC functions use transactions to ensure atomicity
- Foreign keys enforced within `ops.*` schema

**Odoo**:
- Odoo ORM transactions ensure consistency
- Foreign keys enforced within Odoo schema

### Eventual Consistency (Cross-Database)

**Odoo → Supabase**:
- Webhook delivery is best-effort (retry on failure)
- Edge Functions may experience temporary downtime
- Reconciliation jobs detect and fix drift

**Supabase → Odoo**:
- Workers may fail during deployment
- Retry logic required for failed runs
- Idempotency keys prevent duplicate operations

### Conflict Resolution Strategy

**Last-Write-Wins**:
- Odoo is always authoritative for business data
- Supabase reflects Odoo state, not the reverse
- Reconciliation jobs always sync from Odoo → Supabase

**Example**:
```sql
-- If project name differs, Odoo wins
UPDATE ops.projects
SET name = (SELECT name FROM ops.odoo_projects_fdw WHERE id = CAST(project_id AS INTEGER))
WHERE project_id LIKE 'odoo-%';
```

## Data Retention Policies

### Supabase Control Plane

| Table | Retention | Cleanup Strategy |
|-------|-----------|------------------|
| `ops.runs` | 90 days (configurable) | Archive to S3, delete old runs |
| `ops.run_events` | 30 days | Partition by month, drop old partitions |
| `ops.artifacts` | 30 days (images), 90 days (SBOMs) | S3 lifecycle policies |
| `ops.backups` | 30 days (daily), 90 days (weekly), 1 year (monthly) | S3 Glacier transition |
| `ops.approvals` | Indefinite (audit requirement) | Never delete |

**Cleanup Edge Function** (`ops-cleanup`):
```typescript
// Run daily at 3 AM
const { data: oldRuns } = await supabase
    .from('runs')
    .select('run_id')
    .lt('created_at', new Date(Date.now() - 90 * 24 * 60 * 60 * 1000));

for (const run of oldRuns) {
    // Archive to S3
    await s3.putObject({
        Bucket: 'odooops-archives',
        Key: `runs/${run.run_id}.json`,
        Body: JSON.stringify(run)
    });

    // Delete from database
    await supabase.from('runs').delete().eq('run_id', run.run_id);
}
```

### Odoo Business Data

- Retention managed by Odoo's built-in archival system
- No automatic deletion (business requirement)
- Manual cleanup via Odoo UI (`action_archive`)

## Cross-System Query Patterns

### Query Odoo from Supabase (via FDW)

```sql
-- List Odoo projects with OdooOps run counts
SELECT
    o.name AS odoo_project_name,
    COUNT(r.run_id) AS total_runs,
    SUM(CASE WHEN r.status = 'success' THEN 1 ELSE 0 END) AS successful_runs
FROM ops.odoo_projects_fdw o
LEFT JOIN ops.runs r ON r.project_id = 'odoo-' || o.id
GROUP BY o.id, o.name;
```

### Query Supabase from Odoo (via External API)

```python
# Odoo model: ipai_odoo_ops.project
from odoo import models, fields, api
import requests

class OdooOpsProject(models.Model):
    _name = 'odoo_ops.project'

    name = fields.Char('Project Name')
    supabase_project_id = fields.Char('Supabase Project ID')
    run_count = fields.Integer('Total Runs', compute='_compute_run_count')

    def _compute_run_count(self):
        for project in self:
            # Query Supabase via PostgREST
            response = requests.get(
                f'https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/runs',
                params={'project_id': f'eq.{project.supabase_project_id}', 'select': 'count'},
                headers={'apikey': self.env['ir.config_parameter'].get_param('supabase.anon_key')}
            )
            project.run_count = response.json()[0]['count']
```

## Security Boundaries

### Supabase → Odoo

**No Direct Access**: Supabase cannot write to Odoo database.

**Communication Path**: Supabase Edge Function → Odoo JSONRPC API → Odoo writes to own DB.

### Odoo → Supabase

**Service Role Key**: Odoo uses Supabase service role key for API calls (bypasses RLS).

**Validation**: Edge Functions validate payloads before accepting from Odoo.

### Worker → Both Systems

**Odoo Access**: Workers connect via Odoo admin credentials (stored in GitHub Secrets).

**Supabase Access**: Workers use service role key for RPC calls.

## Best Practices

1. **Never Duplicate Data**: If data exists in Odoo, reference it—don't copy it.
2. **Use External IDs**: Cross-system references use text IDs, not integer foreign keys.
3. **Metadata vs Blobs**: Store metadata in PostgreSQL, large files in S3.
4. **Eventual Consistency is OK**: Design for idempotency and retry logic.
5. **Odoo is Authoritative**: For business data, Odoo always wins conflicts.
6. **Archive, Don't Delete**: Preserve audit trails by archiving to S3 before deletion.
7. **RLS Everywhere**: Enable Row Level Security on all Supabase tables.

## References

- **Supabase FDW Guide**: https://supabase.com/docs/guides/database/extensions/postgres_fdw
- **PostgREST Foreign Keys**: https://postgrest.org/en/stable/references/api/resource_embedding.html
- **Odoo External API**: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- **S3 Lifecycle Policies**: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html
