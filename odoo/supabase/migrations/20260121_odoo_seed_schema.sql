-- =============================================================================
-- Migration: Odoo Seed Schema
-- Purpose: Master seed tables for Odoo project/task seeding from Supabase
-- Pattern: Supabase as source-of-truth, Odoo as execution surface
-- Integration: Builds on ops.odoo_bindings (4502_OPS_ODOO_BINDINGS.sql)
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Schema: odoo_seed
-- Stores canonical project/task definitions that get pushed to Odoo
-- -----------------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS odoo_seed;

COMMENT ON SCHEMA odoo_seed IS
'Canonical seed definitions for Odoo projects/tasks. Supabase is master, Odoo is projection.';

-- -----------------------------------------------------------------------------
-- 1. Programs (OKR / Logframe / Portfolio level)
-- Maps to ipai_ppm program concept
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS odoo_seed.programs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug text UNIQUE NOT NULL,
    name text NOT NULL,
    description text,
    program_type text NOT NULL DEFAULT 'ppm' CHECK (program_type IN ('ppm', 'okr', 'logframe', 'portfolio')),

    -- Hierarchy
    parent_slug text REFERENCES odoo_seed.programs(slug),

    -- Status
    active boolean NOT NULL DEFAULT true,

    -- Audit
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_by uuid
);

CREATE INDEX IF NOT EXISTS idx_programs_slug ON odoo_seed.programs(slug);
CREATE INDEX IF NOT EXISTS idx_programs_parent ON odoo_seed.programs(parent_slug);

COMMENT ON TABLE odoo_seed.programs IS
'Master programs/portfolios that group related projects. Maps to Clarity PPM program concept.';

-- -----------------------------------------------------------------------------
-- 2. Projects (seed into Odoo project.project)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS odoo_seed.projects (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Program linkage
    program_slug text NOT NULL REFERENCES odoo_seed.programs(slug) ON DELETE CASCADE,

    -- External reference (maps to x_external_ref in Odoo)
    external_ref text UNIQUE NOT NULL,

    -- Project details
    name text NOT NULL,
    description text,

    -- Odoo target
    company_name text NOT NULL,  -- e.g., 'TBWA\SMP' - resolved to res.company.id
    manager_email text,          -- Odoo user login - resolved to res.users.id

    -- Project settings (CE-compatible only)
    visibility text NOT NULL DEFAULT 'employees' CHECK (visibility IN ('portal', 'employees', 'followers')),
    allow_dependencies boolean NOT NULL DEFAULT true,  -- CE field
    -- NOTE: allow_milestones, allow_timesheets, billing_type are Enterprise-only
    -- Use ipai_ppm for milestone support instead

    -- Dates
    date_start date,
    date_end date,

    -- Staging
    is_active boolean NOT NULL DEFAULT true,
    sync_enabled boolean NOT NULL DEFAULT true,

    -- Odoo sync state
    odoo_project_id int,         -- Populated after sync
    last_sync_at timestamptz,
    sync_error text,

    -- Audit
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_by uuid
);

CREATE INDEX IF NOT EXISTS idx_projects_program ON odoo_seed.projects(program_slug);
CREATE INDEX IF NOT EXISTS idx_projects_external_ref ON odoo_seed.projects(external_ref);
CREATE INDEX IF NOT EXISTS idx_projects_company ON odoo_seed.projects(company_name);

COMMENT ON TABLE odoo_seed.projects IS
'Canonical project definitions. Synced to Odoo project.project via edge function.';

-- -----------------------------------------------------------------------------
-- 3. Tasks (seed into Odoo project.task)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS odoo_seed.tasks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Project linkage
    project_external_ref text NOT NULL REFERENCES odoo_seed.projects(external_ref) ON DELETE CASCADE,

    -- External reference
    external_ref text UNIQUE NOT NULL,

    -- Task details
    name text NOT NULL,
    description text,

    -- Stage (resolved to project.task.type by name)
    stage_name text DEFAULT 'To Do',

    -- Tags (array of tag names, resolved to project.tags)
    tag_names text[] DEFAULT '{}',

    -- Assignment
    assignee_email text,  -- Odoo user login

    -- Planning
    planned_hours numeric(10,2) DEFAULT 0,
    deadline date,
    sequence int DEFAULT 10,

    -- Milestone flag (requires ipai_ppm or similar)
    is_milestone boolean DEFAULT false,

    -- Dependencies (external_refs of other tasks)
    depends_on_refs text[] DEFAULT '{}',

    -- Parent task (for subtasks)
    parent_external_ref text REFERENCES odoo_seed.tasks(external_ref),

    -- Sync state
    is_active boolean NOT NULL DEFAULT true,
    odoo_task_id int,
    last_sync_at timestamptz,
    sync_error text,

    -- Audit
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_by uuid
);

CREATE INDEX IF NOT EXISTS idx_tasks_project ON odoo_seed.tasks(project_external_ref);
CREATE INDEX IF NOT EXISTS idx_tasks_external_ref ON odoo_seed.tasks(external_ref);
CREATE INDEX IF NOT EXISTS idx_tasks_stage ON odoo_seed.tasks(stage_name);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON odoo_seed.tasks(assignee_email);

COMMENT ON TABLE odoo_seed.tasks IS
'Canonical task definitions. Synced to Odoo project.task via edge function.';

-- -----------------------------------------------------------------------------
-- 4. Shadow Tables (mirror of actual Odoo state for verification)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS odoo_seed.shadow_projects (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Odoo identity
    odoo_id int NOT NULL,
    external_ref text,

    -- Snapshot
    name text,
    company_name text,
    manager_name text,
    active boolean,

    -- Raw Odoo record (all fields)
    raw jsonb NOT NULL,

    -- Sync metadata
    synced_at timestamptz NOT NULL DEFAULT now(),

    UNIQUE (odoo_id)
);

CREATE INDEX IF NOT EXISTS idx_shadow_projects_odoo ON odoo_seed.shadow_projects(odoo_id);
CREATE INDEX IF NOT EXISTS idx_shadow_projects_ref ON odoo_seed.shadow_projects(external_ref);

COMMENT ON TABLE odoo_seed.shadow_projects IS
'Mirror of Odoo project.project for verification. Enables seed vs actual diff.';

CREATE TABLE IF NOT EXISTS odoo_seed.shadow_tasks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Odoo identity
    odoo_id int NOT NULL,
    external_ref text,

    -- Snapshot
    name text,
    project_odoo_id int,
    stage_name text,
    assignee_name text,

    -- Raw Odoo record
    raw jsonb NOT NULL,

    -- Sync metadata
    synced_at timestamptz NOT NULL DEFAULT now(),

    UNIQUE (odoo_id)
);

CREATE INDEX IF NOT EXISTS idx_shadow_tasks_odoo ON odoo_seed.shadow_tasks(odoo_id);
CREATE INDEX IF NOT EXISTS idx_shadow_tasks_ref ON odoo_seed.shadow_tasks(external_ref);
CREATE INDEX IF NOT EXISTS idx_shadow_tasks_project ON odoo_seed.shadow_tasks(project_odoo_id);

COMMENT ON TABLE odoo_seed.shadow_tasks IS
'Mirror of Odoo project.task for verification. Enables seed vs actual diff.';

-- -----------------------------------------------------------------------------
-- 5. Sync Runs Log (audit trail)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS odoo_seed.sync_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Run metadata
    run_type text NOT NULL CHECK (run_type IN ('seed', 'shadow', 'verify')),
    started_at timestamptz NOT NULL DEFAULT now(),
    completed_at timestamptz,

    -- Results
    status text NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'success', 'partial', 'failed')),
    projects_processed int DEFAULT 0,
    tasks_processed int DEFAULT 0,
    errors_count int DEFAULT 0,

    -- Details
    error_log jsonb DEFAULT '[]'::jsonb,
    results jsonb DEFAULT '{}'::jsonb,

    -- Trigger
    triggered_by text,  -- 'workflow', 'manual', 'cron'

    CONSTRAINT sync_runs_completed_check CHECK (
        status = 'running' OR completed_at IS NOT NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_sync_runs_status ON odoo_seed.sync_runs(status);
CREATE INDEX IF NOT EXISTS idx_sync_runs_type ON odoo_seed.sync_runs(run_type);

COMMENT ON TABLE odoo_seed.sync_runs IS
'Audit log of all seed/shadow sync operations.';

-- -----------------------------------------------------------------------------
-- 6. Verification Views
-- -----------------------------------------------------------------------------

-- Projects that exist in seed but not in shadow (missing in Odoo)
CREATE OR REPLACE VIEW odoo_seed.v_missing_in_odoo AS
SELECT
    p.external_ref,
    p.name,
    p.company_name,
    p.program_slug,
    p.created_at AS seed_created,
    p.last_sync_at,
    p.sync_error
FROM odoo_seed.projects p
LEFT JOIN odoo_seed.shadow_projects sp ON sp.external_ref = p.external_ref
WHERE sp.id IS NULL
  AND p.sync_enabled = true
  AND p.is_active = true;

COMMENT ON VIEW odoo_seed.v_missing_in_odoo IS
'Projects defined in seed but not found in Odoo shadow. Indicates sync gap.';

-- Projects in Odoo not in seed (orphans or manual creates)
CREATE OR REPLACE VIEW odoo_seed.v_orphan_in_odoo AS
SELECT
    sp.odoo_id,
    sp.name,
    sp.company_name,
    sp.external_ref,
    sp.synced_at
FROM odoo_seed.shadow_projects sp
LEFT JOIN odoo_seed.projects p ON p.external_ref = sp.external_ref
WHERE p.id IS NULL
  AND sp.external_ref IS NOT NULL;

COMMENT ON VIEW odoo_seed.v_orphan_in_odoo IS
'Projects in Odoo with external_ref not in seed. May be manually created or deleted from seed.';

-- Drift detection: seed vs shadow name mismatch
CREATE OR REPLACE VIEW odoo_seed.v_name_drift AS
SELECT
    p.external_ref,
    p.name AS seed_name,
    sp.name AS odoo_name,
    p.last_sync_at
FROM odoo_seed.projects p
JOIN odoo_seed.shadow_projects sp ON sp.external_ref = p.external_ref
WHERE p.name != sp.name;

COMMENT ON VIEW odoo_seed.v_name_drift IS
'Projects where seed name differs from Odoo name. Indicates manual edit or sync issue.';

-- -----------------------------------------------------------------------------
-- 7. Updated_at Trigger
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION odoo_seed.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_programs_updated
    BEFORE UPDATE ON odoo_seed.programs
    FOR EACH ROW EXECUTE FUNCTION odoo_seed.set_updated_at();

CREATE TRIGGER trg_projects_updated
    BEFORE UPDATE ON odoo_seed.projects
    FOR EACH ROW EXECUTE FUNCTION odoo_seed.set_updated_at();

CREATE TRIGGER trg_tasks_updated
    BEFORE UPDATE ON odoo_seed.tasks
    FOR EACH ROW EXECUTE FUNCTION odoo_seed.set_updated_at();

-- -----------------------------------------------------------------------------
-- 8. RLS Policies (service role only for now)
-- -----------------------------------------------------------------------------

ALTER TABLE odoo_seed.programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_seed.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_seed.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_seed.shadow_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_seed.shadow_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_seed.sync_runs ENABLE ROW LEVEL SECURITY;

-- Service role can do everything
CREATE POLICY "Service role full access to programs"
    ON odoo_seed.programs FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to projects"
    ON odoo_seed.projects FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to tasks"
    ON odoo_seed.tasks FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to shadow_projects"
    ON odoo_seed.shadow_projects FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to shadow_tasks"
    ON odoo_seed.shadow_tasks FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to sync_runs"
    ON odoo_seed.sync_runs FOR ALL
    USING (auth.role() = 'service_role');

COMMIT;
