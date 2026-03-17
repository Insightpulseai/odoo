-- =============================================================================
-- TICKETING + PIPELINES (CLEAN): HR/ITSM + Module Dev Automation
-- =============================================================================
-- Clean 3-layer mapping:
--   Enterprise SaaS capability → SAP product family → Odoo CE/OCA + sidecar
--
-- Separation of concerns:
--   - HR Onboarding/Offboarding → Odoo Project/Helpdesk + Supabase ticketing
--   - Engineering/Module Dev → GitHub Issues + Continue Mission Control
--   - Declarative Pipelines → Supabase runtime (Databricks-style DAG + run inspector)
-- =============================================================================

-- =============================================================================
-- TICKETING SCHEMA: HR + ITSM-Lite
-- =============================================================================
-- Practical rule:
--   Odoo = transactional UI + status (tasks/tickets + HR records)
--   Supabase = rules, automation, evidence, audit, docs packs
--   n8n = scheduler + retries + notifications
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS ticketing;

-- Tickets: HR Onboarding/Offboarding + IT Requests + Docs Fixes
CREATE TABLE IF NOT EXISTS ticketing.tickets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    -- Domain determines workflow
    domain text NOT NULL,
    -- CONSTRAINT valid_domain CHECK (
    --     domain IN ('hr_onboarding', 'hr_offboarding', 'it_request', 'module_dev', 'docs_fix', 'support')
    -- ),

    -- Ticket details
    title text NOT NULL,
    description text,
    requester_id uuid,
    requester_email text,

    -- Status + Priority
    status text NOT NULL DEFAULT 'open',
    -- CONSTRAINT valid_status CHECK (
    --     status IN ('open', 'in_progress', 'blocked', 'pending_approval', 'done', 'canceled')
    -- ),
    priority int NOT NULL DEFAULT 2,
    -- CONSTRAINT valid_priority CHECK (priority BETWEEN 1 AND 5),

    -- Assignment
    assignee text,
    team text,

    -- External references (multi-system linking)
    external_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [{"system": "github_issue", "ref": "OCA/hr-expense#123"},
    --           {"system": "odoo_task", "ref": "project.task,456"},
    --           {"system": "continue_task", "ref": "task-abc-123"}]

    -- SLA tracking
    due_at timestamptz,
    sla_breach_at timestamptz,

    -- Metadata
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_tickets_open
    ON ticketing.tickets (tenant_id, domain, status, updated_at DESC);
CREATE INDEX IF NOT EXISTS ix_tickets_assignee
    ON ticketing.tickets (tenant_id, assignee, status);
CREATE INDEX IF NOT EXISTS ix_tickets_sla
    ON ticketing.tickets (tenant_id, status, due_at)
    WHERE status NOT IN ('done', 'canceled');

-- Ticket Events: Audit trail for ticket lifecycle
CREATE TABLE IF NOT EXISTS ticketing.ticket_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    ticket_id uuid NOT NULL REFERENCES ticketing.tickets(id) ON DELETE CASCADE,

    event_type text NOT NULL,
    -- CONSTRAINT valid_event_type CHECK (
    --     event_type IN ('created', 'assigned', 'status_changed', 'comment', 'sla_warning', 'sla_breach', 'escalated', 'resolved', 'reopened')
    -- ),

    actor_id uuid,
    actor_email text,

    old_value text,
    new_value text,
    comment text,

    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_ticket_events_ticket
    ON ticketing.ticket_events (tenant_id, ticket_id, created_at DESC);

-- Ticket Checklists: Tasks within a ticket
CREATE TABLE IF NOT EXISTS ticketing.ticket_checklists (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    ticket_id uuid NOT NULL REFERENCES ticketing.tickets(id) ON DELETE CASCADE,

    seq int NOT NULL DEFAULT 0,
    title text NOT NULL,
    description text,

    is_required boolean NOT NULL DEFAULT true,
    is_completed boolean NOT NULL DEFAULT false,
    completed_at timestamptz,
    completed_by uuid,

    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_ticket_checklists
    ON ticketing.ticket_checklists (tenant_id, ticket_id, seq);

-- =============================================================================
-- ENHANCED PIPELINE SCHEMA: Databricks-style DAG + Run Inspector
-- =============================================================================

-- Add 'kind' column to existing pipeline_defs if not exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'runtime' AND table_name = 'pipeline_defs') THEN
        ALTER TABLE runtime.pipeline_defs
            ADD COLUMN IF NOT EXISTS kind text,
            ADD COLUMN IF NOT EXISTS definition jsonb;

        COMMENT ON COLUMN runtime.pipeline_defs.kind IS 'Pipeline type: docs|module_dev|etl|hr_workflow|other';
        COMMENT ON COLUMN runtime.pipeline_defs.definition IS 'Full pipeline definition as JSON (alternative to spec_yaml)';
    END IF;
END;
$$;

-- Pipeline Stages: Individual steps in a pipeline run
CREATE TABLE IF NOT EXISTS runtime.pipeline_stages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    pipeline_run_id uuid NOT NULL REFERENCES runtime.pipeline_runs(id) ON DELETE CASCADE,

    stage_key text NOT NULL,
    stage_order int NOT NULL,

    status text NOT NULL DEFAULT 'pending',
    -- CONSTRAINT valid_stage_status CHECK (
    --     status IN ('pending', 'running', 'succeeded', 'failed', 'skipped', 'canceled')
    -- ),

    started_at timestamptz,
    finished_at timestamptz,
    duration_ms int,

    -- Input/Output artifacts
    input_refs jsonb NOT NULL DEFAULT '[]'::jsonb,
    output_refs jsonb NOT NULL DEFAULT '[]'::jsonb,

    -- Metrics + Errors
    metrics jsonb NOT NULL DEFAULT '{}'::jsonb,
    error_code text,
    error_message text,

    logs_url text,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_pipeline_stages_run
    ON runtime.pipeline_stages (tenant_id, pipeline_run_id, stage_order);

-- Pipeline Artifacts: Outputs from pipeline stages
CREATE TABLE IF NOT EXISTS runtime.pipeline_artifacts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    pipeline_run_id uuid NOT NULL REFERENCES runtime.pipeline_runs(id) ON DELETE CASCADE,
    stage_id uuid REFERENCES runtime.pipeline_stages(id) ON DELETE SET NULL,

    artifact_key text NOT NULL,
    artifact_type text NOT NULL,
    -- CONSTRAINT valid_artifact_type CHECK (
    --     artifact_type IN ('document', 'chunk', 'embedding', 'module', 'test_report', 'pr_url', 'evidence_pack')
    -- ),

    storage_url text,
    content_hash text,
    size_bytes bigint,

    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_pipeline_artifacts_run
    ON runtime.pipeline_artifacts (tenant_id, pipeline_run_id);
CREATE INDEX IF NOT EXISTS ix_pipeline_artifacts_key
    ON runtime.pipeline_artifacts (tenant_id, artifact_key);

-- =============================================================================
-- DOMAIN-SPECIFIC TEMPLATES: Onboarding/Offboarding Checklists
-- =============================================================================

CREATE TABLE IF NOT EXISTS ticketing.checklist_templates (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    domain text NOT NULL,
    name text NOT NULL,
    description text,

    items jsonb NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [
    --   {"seq": 1, "title": "IT: Create accounts", "required": true, "team": "IT"},
    --   {"seq": 2, "title": "HR: Welcome email", "required": true, "team": "HR"},
    --   {"seq": 3, "title": "Manager: Schedule 1:1", "required": false, "team": "Manager"}
    -- ]

    is_active boolean NOT NULL DEFAULT true,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_checklist_templates
    ON ticketing.checklist_templates (tenant_id, domain, name);

-- =============================================================================
-- SEED: Default Checklist Templates
-- =============================================================================

INSERT INTO ticketing.checklist_templates (tenant_id, domain, name, description, items)
SELECT
    t.id,
    d.domain,
    d.name,
    d.description,
    d.items::jsonb
FROM core.tenants t
CROSS JOIN (VALUES
    ('hr_onboarding', 'Standard Onboarding', 'Default onboarding checklist for new employees', '[
        {"seq": 1, "title": "HR: Create employee record in Odoo", "required": true, "team": "HR"},
        {"seq": 2, "title": "IT: Create email account", "required": true, "team": "IT"},
        {"seq": 3, "title": "IT: Provision laptop/workstation", "required": true, "team": "IT"},
        {"seq": 4, "title": "IT: Set up VPN access", "required": true, "team": "IT"},
        {"seq": 5, "title": "IT: Add to Slack/Mattermost channels", "required": true, "team": "IT"},
        {"seq": 6, "title": "HR: Send welcome email with links", "required": true, "team": "HR"},
        {"seq": 7, "title": "HR: Schedule benefits enrollment", "required": true, "team": "HR"},
        {"seq": 8, "title": "Manager: Schedule day-one 1:1", "required": true, "team": "Manager"},
        {"seq": 9, "title": "Manager: Assign onboarding buddy", "required": false, "team": "Manager"},
        {"seq": 10, "title": "Training: Complete compliance training", "required": true, "team": "Training"},
        {"seq": 11, "title": "Training: Sign policy acknowledgments", "required": true, "team": "Training"},
        {"seq": 12, "title": "Finance: Set up expense reimbursement", "required": false, "team": "Finance"}
    ]'),

    ('hr_offboarding', 'Standard Offboarding', 'Default offboarding checklist for departing employees', '[
        {"seq": 1, "title": "HR: Initiate exit interview", "required": true, "team": "HR"},
        {"seq": 2, "title": "HR: Calculate final pay", "required": true, "team": "HR"},
        {"seq": 3, "title": "IT: Disable email account", "required": true, "team": "IT"},
        {"seq": 4, "title": "IT: Revoke VPN/SSO access", "required": true, "team": "IT"},
        {"seq": 5, "title": "IT: Collect laptop/equipment", "required": true, "team": "IT"},
        {"seq": 6, "title": "IT: Transfer files/ownership", "required": true, "team": "IT"},
        {"seq": 7, "title": "IT: Remove from Slack/Mattermost", "required": true, "team": "IT"},
        {"seq": 8, "title": "Manager: Knowledge transfer sessions", "required": true, "team": "Manager"},
        {"seq": 9, "title": "Manager: Reassign projects/tasks", "required": true, "team": "Manager"},
        {"seq": 10, "title": "Finance: Process final expense reports", "required": true, "team": "Finance"},
        {"seq": 11, "title": "HR: Update employee status in Odoo", "required": true, "team": "HR"},
        {"seq": 12, "title": "HR: Send COBRA/benefits info", "required": false, "team": "HR"}
    ]'),

    ('it_request', 'IT Support Request', 'Default IT service request checklist', '[
        {"seq": 1, "title": "Triage: Categorize request", "required": true, "team": "IT"},
        {"seq": 2, "title": "Triage: Assign priority", "required": true, "team": "IT"},
        {"seq": 3, "title": "Resolution: Investigate issue", "required": true, "team": "IT"},
        {"seq": 4, "title": "Resolution: Implement fix", "required": true, "team": "IT"},
        {"seq": 5, "title": "QA: Verify with requester", "required": true, "team": "IT"},
        {"seq": 6, "title": "Documentation: Update KB if needed", "required": false, "team": "IT"}
    ]'),

    ('module_dev', 'OCA Module Development', 'Module development automation checklist', '[
        {"seq": 1, "title": "Spec: Write feature specification", "required": true, "team": "Engineering"},
        {"seq": 2, "title": "Scaffold: Generate module skeleton", "required": true, "team": "Engineering"},
        {"seq": 3, "title": "Develop: Implement feature", "required": true, "team": "Engineering"},
        {"seq": 4, "title": "Test: Write unit tests", "required": true, "team": "Engineering"},
        {"seq": 5, "title": "Test: Run OCA CI checks", "required": true, "team": "CI"},
        {"seq": 6, "title": "Review: Create PR", "required": true, "team": "Engineering"},
        {"seq": 7, "title": "Review: Code review", "required": true, "team": "Engineering"},
        {"seq": 8, "title": "Merge: Approve and merge", "required": true, "team": "Engineering"},
        {"seq": 9, "title": "Docs: Update documentation", "required": true, "team": "Engineering"},
        {"seq": 10, "title": "Publish: Update capability map", "required": false, "team": "Engineering"}
    ]'),

    ('docs_fix', 'Documentation Fix', 'Documentation update checklist', '[
        {"seq": 1, "title": "Identify: Locate outdated/incorrect content", "required": true, "team": "Docs"},
        {"seq": 2, "title": "Draft: Write corrected content", "required": true, "team": "Docs"},
        {"seq": 3, "title": "Review: Technical review", "required": true, "team": "Engineering"},
        {"seq": 4, "title": "Publish: Update docs site", "required": true, "team": "Docs"},
        {"seq": 5, "title": "RAG: Re-embed updated chunks", "required": true, "team": "AI"}
    ]')
) AS d(domain, name, description, items)
ON CONFLICT (tenant_id, domain, name) DO NOTHING;

-- =============================================================================
-- FUNCTIONS: Ticket Operations
-- =============================================================================

-- Create ticket from template
CREATE OR REPLACE FUNCTION ticketing.create_ticket_from_template(
    p_tenant_id uuid,
    p_domain text,
    p_title text,
    p_description text DEFAULT NULL,
    p_requester_email text DEFAULT NULL,
    p_assignee text DEFAULT NULL,
    p_priority int DEFAULT 2,
    p_metadata jsonb DEFAULT '{}'::jsonb
)
RETURNS uuid
LANGUAGE plpgsql
AS $func$
DECLARE
    v_ticket_id uuid;
    v_template_items jsonb;
    v_item jsonb;
BEGIN
    -- Create ticket
    INSERT INTO ticketing.tickets (
        tenant_id, domain, title, description,
        requester_email, assignee, priority, metadata
    ) VALUES (
        p_tenant_id, p_domain, p_title, p_description,
        p_requester_email, p_assignee, p_priority, p_metadata
    )
    RETURNING id INTO v_ticket_id;

    -- Get template items
    SELECT items INTO v_template_items
    FROM ticketing.checklist_templates
    WHERE tenant_id = p_tenant_id
      AND domain = p_domain
      AND is_active = true
    LIMIT 1;

    -- Create checklist items from template
    IF v_template_items IS NOT NULL THEN
        FOR v_item IN SELECT * FROM jsonb_array_elements(v_template_items)
        LOOP
            INSERT INTO ticketing.ticket_checklists (
                tenant_id, ticket_id, seq, title, is_required, metadata
            ) VALUES (
                p_tenant_id,
                v_ticket_id,
                (v_item->>'seq')::int,
                v_item->>'title',
                COALESCE((v_item->>'required')::boolean, true),
                jsonb_build_object('team', v_item->>'team')
            );
        END LOOP;
    END IF;

    -- Log creation event
    INSERT INTO ticketing.ticket_events (
        tenant_id, ticket_id, event_type, actor_email, new_value
    ) VALUES (
        p_tenant_id, v_ticket_id, 'created', p_requester_email, p_title
    );

    RETURN v_ticket_id;
END;
$func$;

-- Update ticket status
CREATE OR REPLACE FUNCTION ticketing.update_ticket_status(
    p_ticket_id uuid,
    p_new_status text,
    p_actor_email text DEFAULT NULL,
    p_comment text DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
AS $func$
DECLARE
    v_tenant_id uuid;
    v_old_status text;
BEGIN
    SELECT tenant_id, status INTO v_tenant_id, v_old_status
    FROM ticketing.tickets
    WHERE id = p_ticket_id;

    IF v_old_status = p_new_status THEN
        RETURN;
    END IF;

    -- Update ticket
    UPDATE ticketing.tickets
    SET status = p_new_status,
        updated_at = now()
    WHERE id = p_ticket_id;

    -- Log status change
    INSERT INTO ticketing.ticket_events (
        tenant_id, ticket_id, event_type, actor_email,
        old_value, new_value, comment
    ) VALUES (
        v_tenant_id, p_ticket_id, 'status_changed', p_actor_email,
        v_old_status, p_new_status, p_comment
    );
END;
$func$;

-- Complete checklist item
CREATE OR REPLACE FUNCTION ticketing.complete_checklist_item(
    p_checklist_id uuid,
    p_completed_by uuid DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
AS $func$
DECLARE
    v_ticket_id uuid;
    v_tenant_id uuid;
    v_all_complete boolean;
BEGIN
    -- Mark item complete
    UPDATE ticketing.ticket_checklists
    SET is_completed = true,
        completed_at = now(),
        completed_by = p_completed_by
    WHERE id = p_checklist_id
    RETURNING ticket_id, tenant_id INTO v_ticket_id, v_tenant_id;

    -- Check if all required items are complete
    SELECT NOT EXISTS (
        SELECT 1 FROM ticketing.ticket_checklists
        WHERE ticket_id = v_ticket_id
          AND is_required = true
          AND is_completed = false
    ) INTO v_all_complete;

    -- Auto-complete ticket if all required items done
    IF v_all_complete THEN
        PERFORM ticketing.update_ticket_status(
            v_ticket_id,
            'done',
            NULL,
            'All required checklist items completed'
        );
    END IF;
END;
$func$;

-- =============================================================================
-- VIEWS: Ticket Dashboard
-- =============================================================================

-- View: Tickets with checklist progress
CREATE OR REPLACE VIEW ticketing.v_tickets_with_progress AS
SELECT
    t.id,
    t.tenant_id,
    t.domain,
    t.title,
    t.status,
    t.priority,
    t.assignee,
    t.team,
    t.due_at,
    t.created_at,
    t.updated_at,
    COUNT(c.id) AS total_items,
    COUNT(c.id) FILTER (WHERE c.is_completed) AS completed_items,
    COUNT(c.id) FILTER (WHERE c.is_required AND NOT c.is_completed) AS pending_required,
    CASE
        WHEN COUNT(c.id) = 0 THEN 0
        ELSE ROUND(100.0 * COUNT(c.id) FILTER (WHERE c.is_completed) / COUNT(c.id))
    END AS progress_percent
FROM ticketing.tickets t
LEFT JOIN ticketing.ticket_checklists c ON t.id = c.ticket_id
GROUP BY t.id;

-- View: Open tickets by domain
CREATE OR REPLACE VIEW ticketing.v_open_by_domain AS
SELECT
    tenant_id,
    domain,
    COUNT(*) AS open_count,
    COUNT(*) FILTER (WHERE due_at < now()) AS overdue_count,
    AVG(EXTRACT(EPOCH FROM (now() - created_at)) / 3600)::int AS avg_age_hours
FROM ticketing.tickets
WHERE status NOT IN ('done', 'canceled')
GROUP BY tenant_id, domain;

-- =============================================================================
-- SEPARATION OF CONCERNS: HR vs Engineering Tickets
-- =============================================================================

COMMENT ON SCHEMA ticketing IS 'HR + ITSM-lite ticketing for Odoo Project/Helpdesk integration';

COMMENT ON TABLE ticketing.tickets IS '
Ticket domains and their routing:
- hr_onboarding, hr_offboarding: Odoo Project tasks + Supabase checklists
- it_request, support: Odoo Helpdesk + Supabase SLA tracking
- module_dev: GitHub Issues + Continue Mission Control (external_refs)
- docs_fix: GitHub + Supabase RAG pipeline

Engineering tickets (module_dev) should link to:
- GitHub Issues via external_refs: [{"system": "github_issue", "ref": "OCA/hr-expense#123"}]
- Continue Mission Control task IDs
- Pipeline runs via runtime.pipeline_runs
';

-- =============================================================================
-- VERIFICATION
-- =============================================================================

DO $verify$
DECLARE
    ticket_count int;
    template_count int;
BEGIN
    SELECT COUNT(*) INTO ticket_count FROM ticketing.tickets;
    SELECT COUNT(*) INTO template_count FROM ticketing.checklist_templates;

    RAISE NOTICE 'Ticketing schema ready: % tickets, % templates', ticket_count, template_count;
END;
$verify$;
