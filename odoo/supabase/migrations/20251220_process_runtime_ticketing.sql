-- =============================================================================
-- PROCESS RUNTIME: Master Control for Hire-to-Retire + Ticketing
-- =============================================================================
-- Purpose: Process definitions, runs, work items (tickets), SLAs, escalations
-- Domain: Onboarding, Offboarding, and other lifecycle processes
-- Integration: Syncs with Odoo Helpdesk/Project via odoo_sync tables
-- Created: 2025-12-20
-- =============================================================================

-- Schemas
CREATE SCHEMA IF NOT EXISTS process;
CREATE SCHEMA IF NOT EXISTS control;
CREATE SCHEMA IF NOT EXISTS run;
CREATE SCHEMA IF NOT EXISTS odoo_sync;

-- =============================================================================
-- PROCESS: Definitions + Versions + Graph (Nodes/Edges/Lanes)
-- =============================================================================

-- Process Definitions (e.g., hire_to_retire, procure_to_pay, record_to_report)
CREATE TABLE IF NOT EXISTS process.definitions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    key text NOT NULL,                  -- hire_to_retire
    name text NOT NULL,                 -- Hire-to-Retire
    domain text,                        -- HR|Finance|IT|Operations
    description text,

    owner_role text,                    -- process_owner
    status text DEFAULT 'draft',        -- draft|active|deprecated

    metadata jsonb DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_process_defs_key
    ON process.definitions (tenant_id, key);

-- Process Versions (immutable per version)
CREATE TABLE IF NOT EXISTS process.versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    definition_id uuid NOT NULL REFERENCES process.definitions(id) ON DELETE CASCADE,

    version text NOT NULL,              -- 1.0, 1.1, 2.0
    version_number int NOT NULL,        -- Numeric for ordering

    -- Source (for audit)
    source_uri text,                    -- s3://bucket/bpmn/hire_to_retire_v1.0.html
    content_hash text,

    -- Status
    status text DEFAULT 'draft',        -- draft|published|superseded
    published_at timestamptz,
    superseded_at timestamptz,

    -- Change tracking
    change_summary text,
    author_id uuid,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_process_versions
    ON process.versions (tenant_id, definition_id, version);
CREATE INDEX IF NOT EXISTS ix_process_versions_published
    ON process.versions (tenant_id, definition_id, published_at DESC)
    WHERE status = 'published';

-- Lanes (roles/teams per process version)
CREATE TABLE IF NOT EXISTS process.lanes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    version_id uuid NOT NULL REFERENCES process.versions(id) ON DELETE CASCADE,

    lane_key text NOT NULL,             -- hr_team, finance_team, it_team, employee
    role_name text NOT NULL,            -- HR Team, Finance Team, IT Team, Employee
    department text,                    -- HR, Finance, IT

    -- Permissions
    can_execute boolean DEFAULT true,
    can_approve boolean DEFAULT false,

    display_order int DEFAULT 0,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_process_lanes
    ON process.lanes (tenant_id, version_id, lane_key);

-- Nodes (events, tasks, gateways, subprocesses)
CREATE TABLE IF NOT EXISTS process.nodes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    version_id uuid NOT NULL REFERENCES process.versions(id) ON DELETE CASCADE,

    node_key text NOT NULL,             -- onboard_start, create_employee_record, etc.
    node_type text NOT NULL,            -- start_event|end_event|task|gateway|subprocess|intermediate_event
    lane_key text,                      -- Which lane owns this node

    label text NOT NULL,                -- "Create Employee Record"
    description text,

    -- Task metadata
    task_type text,                     -- user_task|service_task|script_task|manual_task
    is_checkpoint boolean DEFAULT false, -- Milestone / SLA checkpoint

    -- Tags for filtering
    tags jsonb DEFAULT '[]'::jsonb,     -- ["onboarding", "statutory", "it_provisioning"]

    -- Additional metadata
    metadata jsonb DEFAULT '{}'::jsonb,
    -- {
    --   "estimated_duration_hours": 4,
    --   "required_artifacts": ["employment_contract", "id_documents"],
    --   "produces_artifacts": ["employee_id", "email_account"]
    -- }

    display_order int DEFAULT 0,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_process_nodes
    ON process.nodes (tenant_id, version_id, node_key);
CREATE INDEX IF NOT EXISTS ix_process_nodes_lane
    ON process.nodes (tenant_id, version_id, lane_key);
CREATE INDEX IF NOT EXISTS ix_process_nodes_type
    ON process.nodes (tenant_id, version_id, node_type);

-- Edges (sequence flows between nodes)
CREATE TABLE IF NOT EXISTS process.edges (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    version_id uuid NOT NULL REFERENCES process.versions(id) ON DELETE CASCADE,

    from_node_key text NOT NULL,
    to_node_key text NOT NULL,

    edge_type text DEFAULT 'sequence',  -- sequence|conditional|default|message
    condition text,                     -- Expression or label for conditional edges
    condition_expression text,          -- ${approved == true}

    display_order int DEFAULT 0,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_process_edges_from
    ON process.edges (tenant_id, version_id, from_node_key);
CREATE INDEX IF NOT EXISTS ix_process_edges_to
    ON process.edges (tenant_id, version_id, to_node_key);

-- =============================================================================
-- CONTROL: Rules, SLAs, Checklists
-- =============================================================================

-- Control Rules (SLAs, statutory requirements, internal policies)
CREATE TABLE IF NOT EXISTS control.rules (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    version_id uuid NOT NULL REFERENCES process.versions(id) ON DELETE CASCADE,

    rule_key text NOT NULL,             -- final_pay_sla, coe_sla, clearance_deadline
    rule_type text NOT NULL,            -- sla|statutory|internal|compliance

    -- Trigger
    trigger_node_key text,              -- Node that starts the timer
    trigger_event text,                 -- node_complete|node_start|process_start

    -- Deadline
    deadline_days int,                  -- Days from trigger
    deadline_hours int,                 -- Hours from trigger (for shorter SLAs)
    deadline_expression text,           -- For complex calculations

    -- Severity & escalation
    severity text DEFAULT 'medium',     -- low|medium|high|critical
    escalation_role text,               -- Who to notify on breach
    escalation_hours int,               -- Hours before escalation

    -- Proof requirements
    proof_required jsonb DEFAULT '[]'::jsonb,
    -- ["clearance_form", "asset_return_receipt", "exit_interview"]

    description text,
    legal_reference text,               -- "Labor Code Art. 297" for statutory

    is_active boolean DEFAULT true,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_control_rules
    ON control.rules (tenant_id, version_id, rule_key);
CREATE INDEX IF NOT EXISTS ix_control_rules_type
    ON control.rules (tenant_id, version_id, rule_type);

-- Checklists (per lane, per phase)
CREATE TABLE IF NOT EXISTS control.checklists (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    version_id uuid NOT NULL REFERENCES process.versions(id) ON DELETE CASCADE,

    lane_key text NOT NULL,
    phase text,                         -- onboarding|offboarding|provisioning|clearance
    item_key text NOT NULL,

    text text NOT NULL,                 -- "Collect government IDs"
    timing_hint text,                   -- "Day 1", "Before Last Day"

    is_required boolean DEFAULT true,
    display_order int DEFAULT 0,

    tags jsonb DEFAULT '[]'::jsonb,     -- ["statutory", "it", "hr"]

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_control_checklists
    ON control.checklists (tenant_id, version_id, lane_key, item_key);
CREATE INDEX IF NOT EXISTS ix_control_checklists_phase
    ON control.checklists (tenant_id, version_id, phase);

-- =============================================================================
-- RUN: Instances, Events, Work Items (Tickets), Evidence
-- =============================================================================

-- Process Instances (one per onboarding/offboarding case)
CREATE TABLE IF NOT EXISTS run.instances (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    definition_id uuid NOT NULL REFERENCES process.definitions(id),
    version_id uuid NOT NULL REFERENCES process.versions(id),

    -- Case reference
    case_number text NOT NULL,          -- ONB-2025-0001, OFF-2025-0001
    case_type text NOT NULL,            -- onboarding|offboarding|transfer|promotion

    -- Subject (employee)
    subject_ref uuid,                   -- Employee ID (Odoo res.users or hr.employee)
    subject_name text,
    subject_email text,

    -- Dates
    started_at timestamptz NOT NULL DEFAULT now(),
    target_completion_at timestamptz,
    completed_at timestamptz,

    -- Current state
    status text NOT NULL DEFAULT 'active',  -- active|completed|cancelled|on_hold|escalated
    current_node_keys text[],           -- Active nodes (parallel paths)

    -- Ownership
    initiator_id uuid,
    assignee_id uuid,                   -- Current primary assignee

    -- Metadata
    metadata jsonb DEFAULT '{}'::jsonb,
    -- {
    --   "start_date": "2025-01-15",
    --   "position": "Software Engineer",
    --   "department": "Engineering",
    --   "manager_id": "uuid"
    -- }

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_run_instances_case
    ON run.instances (tenant_id, case_number);
CREATE INDEX IF NOT EXISTS ix_run_instances_status
    ON run.instances (tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_run_instances_subject
    ON run.instances (tenant_id, subject_ref);
CREATE INDEX IF NOT EXISTS ix_run_instances_assignee
    ON run.instances (tenant_id, assignee_id, status)
    WHERE status = 'active';

-- Process Events (audit trail of all actions)
CREATE TABLE IF NOT EXISTS run.events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    instance_id uuid NOT NULL REFERENCES run.instances(id) ON DELETE CASCADE,

    -- Event details
    node_key text,
    event_type text NOT NULL,
    -- Types: instance_started|instance_completed|instance_cancelled|
    --        node_entered|node_completed|node_skipped|
    --        work_item_created|work_item_completed|work_item_reassigned|
    --        sla_warning|sla_breach|escalation|
    --        comment|attachment|status_change

    at timestamptz NOT NULL DEFAULT now(),

    actor_id uuid,
    actor_name text,
    actor_role text,

    -- Details
    payload jsonb DEFAULT '{}'::jsonb,
    comment text,

    -- Immutable (no updated_at)
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_run_events_instance
    ON run.events (tenant_id, instance_id, at DESC);
CREATE INDEX IF NOT EXISTS ix_run_events_node
    ON run.events (tenant_id, instance_id, node_key);
CREATE INDEX IF NOT EXISTS ix_run_events_type
    ON run.events (tenant_id, event_type, at DESC);

-- Work Items (Tickets) - individual tasks within a process instance
CREATE TABLE IF NOT EXISTS run.work_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    instance_id uuid NOT NULL REFERENCES run.instances(id) ON DELETE CASCADE,

    -- Work item identification
    work_item_number text NOT NULL,     -- ONB-2025-0001-001
    node_key text NOT NULL,             -- Which process node this represents
    lane_key text,                      -- Which lane (team) owns this

    title text NOT NULL,
    description text,

    -- Assignment
    assignee_id uuid,
    assignee_name text,
    assigned_at timestamptz,

    -- Status
    status text NOT NULL DEFAULT 'pending',
    -- pending|ready|in_progress|waiting|completed|cancelled|blocked

    -- Timing
    created_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz,
    due_at timestamptz,
    completed_at timestamptz,

    -- SLA
    sla_rule_key text,
    sla_due_at timestamptz,
    sla_status text DEFAULT 'on_track',  -- on_track|at_risk|breached

    -- Priority
    priority text DEFAULT 'medium',     -- low|medium|high|urgent

    -- Resolution
    resolution text,                    -- completed|skipped|cancelled|delegated
    resolution_notes text,

    -- Dependencies
    depends_on uuid[],                  -- Other work_item IDs that must complete first
    blocks uuid[],                      -- Work items blocked by this one

    -- Metadata
    metadata jsonb DEFAULT '{}'::jsonb,

    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_run_work_items_number
    ON run.work_items (tenant_id, work_item_number);
CREATE INDEX IF NOT EXISTS ix_run_work_items_instance
    ON run.work_items (tenant_id, instance_id, status);
CREATE INDEX IF NOT EXISTS ix_run_work_items_assignee
    ON run.work_items (tenant_id, assignee_id, status)
    WHERE status IN ('pending', 'ready', 'in_progress');
CREATE INDEX IF NOT EXISTS ix_run_work_items_due
    ON run.work_items (tenant_id, due_at)
    WHERE status IN ('pending', 'ready', 'in_progress');
CREATE INDEX IF NOT EXISTS ix_run_work_items_sla
    ON run.work_items (tenant_id, sla_status, sla_due_at)
    WHERE sla_status IN ('at_risk', 'breached');

-- Checklist Completions (per work item)
CREATE TABLE IF NOT EXISTS run.checklist_completions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    work_item_id uuid NOT NULL REFERENCES run.work_items(id) ON DELETE CASCADE,

    checklist_item_id uuid NOT NULL REFERENCES control.checklists(id),
    item_key text NOT NULL,

    completed boolean DEFAULT false,
    completed_at timestamptz,
    completed_by uuid,

    notes text,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_run_checklist_completions
    ON run.checklist_completions (tenant_id, work_item_id, item_key);

-- SLA Timers (active timers for monitoring)
CREATE TABLE IF NOT EXISTS run.sla_timers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    instance_id uuid NOT NULL REFERENCES run.instances(id) ON DELETE CASCADE,
    work_item_id uuid REFERENCES run.work_items(id) ON DELETE CASCADE,

    rule_id uuid NOT NULL REFERENCES control.rules(id),
    rule_key text NOT NULL,

    -- Timer state
    started_at timestamptz NOT NULL DEFAULT now(),
    due_at timestamptz NOT NULL,
    warning_at timestamptz,             -- When to send warning (e.g., 80% of time elapsed)

    status text NOT NULL DEFAULT 'active',  -- active|completed|breached|cancelled

    -- Completion
    completed_at timestamptz,
    breached_at timestamptz,

    -- Metadata
    metadata jsonb DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_run_sla_timers_due
    ON run.sla_timers (tenant_id, due_at)
    WHERE status = 'active';
CREATE INDEX IF NOT EXISTS ix_run_sla_timers_instance
    ON run.sla_timers (tenant_id, instance_id);
CREATE INDEX IF NOT EXISTS ix_run_sla_timers_warning
    ON run.sla_timers (tenant_id, warning_at)
    WHERE status = 'active' AND warning_at IS NOT NULL;

-- Escalations
CREATE TABLE IF NOT EXISTS run.escalations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    instance_id uuid NOT NULL REFERENCES run.instances(id) ON DELETE CASCADE,
    work_item_id uuid REFERENCES run.work_items(id) ON DELETE CASCADE,
    sla_timer_id uuid REFERENCES run.sla_timers(id),

    -- Escalation details
    reason text NOT NULL,               -- sla_breach|sla_warning|manual|blocked
    severity text NOT NULL,             -- warning|critical|emergency

    -- Assignment
    escalated_to_id uuid,
    escalated_to_role text,
    escalated_by_id uuid,

    -- Resolution
    status text DEFAULT 'open',         -- open|acknowledged|resolved|dismissed
    acknowledged_at timestamptz,
    resolved_at timestamptz,
    resolution_notes text,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_run_escalations_open
    ON run.escalations (tenant_id, status, created_at DESC)
    WHERE status = 'open';
CREATE INDEX IF NOT EXISTS ix_run_escalations_assignee
    ON run.escalations (tenant_id, escalated_to_id, status)
    WHERE status IN ('open', 'acknowledged');

-- Evidence (artifacts collected during process)
CREATE TABLE IF NOT EXISTS run.evidence (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    instance_id uuid NOT NULL REFERENCES run.instances(id) ON DELETE CASCADE,
    work_item_id uuid REFERENCES run.work_items(id) ON DELETE CASCADE,

    -- Artifact details
    artifact_type text NOT NULL,        -- contract|clearance_form|coe|id_document|asset_return
    artifact_name text NOT NULL,

    -- Storage
    storage_url text,                   -- s3://bucket/evidence/...
    content_hash text,                  -- SHA256 for integrity

    -- Metadata
    metadata jsonb DEFAULT '{}'::jsonb,
    -- {"file_type": "pdf", "size_bytes": 12345, "pages": 2}

    -- Collection
    collected_by uuid,
    collected_at timestamptz NOT NULL DEFAULT now(),

    -- Verification (optional)
    verified_by uuid,
    verified_at timestamptz,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_run_evidence_instance
    ON run.evidence (tenant_id, instance_id);
CREATE INDEX IF NOT EXISTS ix_run_evidence_type
    ON run.evidence (tenant_id, artifact_type);

-- =============================================================================
-- ODOO SYNC: Mapping to Odoo Helpdesk/Project
-- =============================================================================

-- Odoo Helpdesk Ticket Mapping
CREATE TABLE IF NOT EXISTS odoo_sync.helpdesk_tickets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    -- Supabase reference
    work_item_id uuid NOT NULL REFERENCES run.work_items(id) ON DELETE CASCADE,

    -- Odoo reference
    odoo_ticket_id int NOT NULL,
    odoo_ticket_name text,
    odoo_team_id int,
    odoo_stage_id int,

    -- Sync state
    last_synced_at timestamptz NOT NULL DEFAULT now(),
    sync_status text DEFAULT 'synced',  -- synced|pending|error
    sync_error text,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_odoo_helpdesk_work_item
    ON odoo_sync.helpdesk_tickets (tenant_id, work_item_id);
CREATE UNIQUE INDEX IF NOT EXISTS ux_odoo_helpdesk_ticket
    ON odoo_sync.helpdesk_tickets (tenant_id, odoo_ticket_id);

-- Odoo Project Task Mapping
CREATE TABLE IF NOT EXISTS odoo_sync.project_tasks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    -- Supabase reference
    work_item_id uuid NOT NULL REFERENCES run.work_items(id) ON DELETE CASCADE,

    -- Odoo reference
    odoo_task_id int NOT NULL,
    odoo_task_name text,
    odoo_project_id int,
    odoo_stage_id int,

    -- Sync state
    last_synced_at timestamptz NOT NULL DEFAULT now(),
    sync_status text DEFAULT 'synced',
    sync_error text,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_odoo_project_work_item
    ON odoo_sync.project_tasks (tenant_id, work_item_id);
CREATE UNIQUE INDEX IF NOT EXISTS ux_odoo_project_task
    ON odoo_sync.project_tasks (tenant_id, odoo_task_id);

-- Odoo Employee Mapping (for subject reference)
CREATE TABLE IF NOT EXISTS odoo_sync.employees (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    -- Supabase reference
    supabase_subject_ref uuid,

    -- Odoo reference
    odoo_employee_id int NOT NULL,
    odoo_user_id int,
    odoo_employee_name text,
    odoo_work_email text,

    -- Sync state
    last_synced_at timestamptz NOT NULL DEFAULT now(),

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_odoo_employees
    ON odoo_sync.employees (tenant_id, odoo_employee_id);

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Get active process version for a definition
CREATE OR REPLACE FUNCTION process.get_active_version(
    p_tenant_id uuid,
    p_definition_key text
)
RETURNS uuid
LANGUAGE sql STABLE
AS $func$
SELECT v.id
FROM process.versions v
JOIN process.definitions d ON v.definition_id = d.id
WHERE d.tenant_id = p_tenant_id
  AND d.key = p_definition_key
  AND v.status = 'published'
ORDER BY v.published_at DESC
LIMIT 1;
$func$;

-- Create work items from process nodes
CREATE OR REPLACE FUNCTION run.create_work_items_for_instance(
    p_tenant_id uuid,
    p_instance_id uuid,
    p_node_keys text[]
)
RETURNS int
LANGUAGE plpgsql
AS $func$
DECLARE
    v_count int := 0;
    v_instance run.instances%ROWTYPE;
    v_node process.nodes%ROWTYPE;
    v_item_number text;
    v_node_key text;
BEGIN
    SELECT * INTO v_instance FROM run.instances WHERE id = p_instance_id;

    FOREACH v_node_key IN ARRAY p_node_keys LOOP
        SELECT * INTO v_node
        FROM process.nodes
        WHERE tenant_id = p_tenant_id
          AND version_id = v_instance.version_id
          AND node_key = v_node_key;

        IF v_node.id IS NOT NULL AND v_node.node_type = 'task' THEN
            v_item_number := v_instance.case_number || '-' || LPAD((v_count + 1)::text, 3, '0');

            INSERT INTO run.work_items (
                tenant_id, instance_id, work_item_number, node_key, lane_key,
                title, description, status, priority
            ) VALUES (
                p_tenant_id, p_instance_id, v_item_number, v_node_key, v_node.lane_key,
                v_node.label, v_node.description, 'pending', 'medium'
            );

            v_count := v_count + 1;
        END IF;
    END LOOP;

    RETURN v_count;
END;
$func$;

-- Get pending work items for a user
CREATE OR REPLACE FUNCTION run.get_my_work_items(
    p_tenant_id uuid,
    p_user_id uuid,
    p_limit int DEFAULT 20
)
RETURNS TABLE (
    work_item_id uuid,
    work_item_number text,
    title text,
    case_number text,
    case_type text,
    subject_name text,
    status text,
    priority text,
    due_at timestamptz,
    sla_status text,
    created_at timestamptz
)
LANGUAGE sql STABLE
AS $func$
SELECT
    wi.id AS work_item_id,
    wi.work_item_number,
    wi.title,
    ri.case_number,
    ri.case_type,
    ri.subject_name,
    wi.status,
    wi.priority,
    wi.due_at,
    wi.sla_status,
    wi.created_at
FROM run.work_items wi
JOIN run.instances ri ON wi.instance_id = ri.id
WHERE wi.tenant_id = p_tenant_id
  AND wi.assignee_id = p_user_id
  AND wi.status IN ('pending', 'ready', 'in_progress')
ORDER BY
    CASE wi.priority
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        ELSE 4
    END,
    wi.due_at ASC NULLS LAST,
    wi.created_at ASC
LIMIT p_limit;
$func$;

-- Check SLA timers and create escalations
CREATE OR REPLACE FUNCTION run.check_sla_timers()
RETURNS int
LANGUAGE plpgsql
AS $func$
DECLARE
    v_count int := 0;
    v_timer run.sla_timers%ROWTYPE;
    v_rule control.rules%ROWTYPE;
BEGIN
    -- Check for breached timers
    FOR v_timer IN
        SELECT * FROM run.sla_timers
        WHERE status = 'active'
          AND due_at < now()
    LOOP
        -- Mark as breached
        UPDATE run.sla_timers
        SET status = 'breached', breached_at = now()
        WHERE id = v_timer.id;

        -- Get rule for escalation
        SELECT * INTO v_rule FROM control.rules WHERE id = v_timer.rule_id;

        -- Create escalation
        INSERT INTO run.escalations (
            tenant_id, instance_id, work_item_id, sla_timer_id,
            reason, severity, escalated_to_role
        ) VALUES (
            v_timer.tenant_id, v_timer.instance_id, v_timer.work_item_id, v_timer.id,
            'sla_breach', v_rule.severity, v_rule.escalation_role
        );

        -- Update work item SLA status
        IF v_timer.work_item_id IS NOT NULL THEN
            UPDATE run.work_items
            SET sla_status = 'breached'
            WHERE id = v_timer.work_item_id;
        END IF;

        v_count := v_count + 1;
    END LOOP;

    -- Check for at-risk timers (warning threshold)
    UPDATE run.work_items wi
    SET sla_status = 'at_risk'
    FROM run.sla_timers st
    WHERE st.work_item_id = wi.id
      AND st.status = 'active'
      AND st.warning_at < now()
      AND st.due_at > now()
      AND wi.sla_status = 'on_track';

    RETURN v_count;
END;
$func$;

-- =============================================================================
-- SEED: Hire-to-Retire Process Definition
-- =============================================================================

DO $$
DECLARE
    v_tenant_id uuid;
    v_def_id uuid;
    v_version_id uuid;
BEGIN
    SELECT id INTO v_tenant_id FROM core.tenants LIMIT 1;

    IF v_tenant_id IS NULL THEN
        RAISE NOTICE 'No tenant found, skipping process seeding';
        RETURN;
    END IF;

    -- Create definition
    INSERT INTO process.definitions (tenant_id, key, name, domain, description, status)
    VALUES (
        v_tenant_id,
        'hire_to_retire',
        'Hire-to-Retire',
        'HR',
        'End-to-end employee lifecycle from hiring to separation',
        'active'
    )
    ON CONFLICT (tenant_id, key) DO UPDATE SET updated_at = now()
    RETURNING id INTO v_def_id;

    -- Create version
    INSERT INTO process.versions (tenant_id, definition_id, version, version_number, status, published_at)
    VALUES (v_tenant_id, v_def_id, '1.0', 1, 'published', now())
    ON CONFLICT (tenant_id, definition_id, version) DO NOTHING
    RETURNING id INTO v_version_id;

    IF v_version_id IS NULL THEN
        SELECT id INTO v_version_id FROM process.versions
        WHERE tenant_id = v_tenant_id AND definition_id = v_def_id AND version = '1.0';
    END IF;

    -- Create lanes
    INSERT INTO process.lanes (tenant_id, version_id, lane_key, role_name, department, display_order)
    VALUES
        (v_tenant_id, v_version_id, 'employee', 'Employee', 'All', 1),
        (v_tenant_id, v_version_id, 'hr_team', 'HR Team', 'HR', 2),
        (v_tenant_id, v_version_id, 'it_team', 'IT Team', 'IT', 3),
        (v_tenant_id, v_version_id, 'finance_team', 'Finance Team', 'Finance', 4),
        (v_tenant_id, v_version_id, 'manager', 'Manager', 'All', 5)
    ON CONFLICT (tenant_id, version_id, lane_key) DO NOTHING;

    -- Create nodes (Onboarding)
    INSERT INTO process.nodes (tenant_id, version_id, node_key, node_type, lane_key, label, task_type, tags, display_order)
    VALUES
        (v_tenant_id, v_version_id, 'onboard_start', 'start_event', 'hr_team', 'Onboarding Started', NULL, '["onboarding"]', 1),
        (v_tenant_id, v_version_id, 'create_employee_record', 'task', 'hr_team', 'Create Employee Record', 'user_task', '["onboarding", "hr"]', 2),
        (v_tenant_id, v_version_id, 'collect_documents', 'task', 'hr_team', 'Collect Required Documents', 'user_task', '["onboarding", "hr", "statutory"]', 3),
        (v_tenant_id, v_version_id, 'setup_payroll', 'task', 'finance_team', 'Setup Payroll', 'user_task', '["onboarding", "finance"]', 4),
        (v_tenant_id, v_version_id, 'provision_accounts', 'task', 'it_team', 'Provision IT Accounts', 'user_task', '["onboarding", "it"]', 5),
        (v_tenant_id, v_version_id, 'assign_assets', 'task', 'it_team', 'Assign Equipment', 'user_task', '["onboarding", "it", "assets"]', 6),
        (v_tenant_id, v_version_id, 'orientation', 'task', 'hr_team', 'Conduct Orientation', 'user_task', '["onboarding", "hr"]', 7),
        (v_tenant_id, v_version_id, 'onboard_complete', 'end_event', 'hr_team', 'Onboarding Complete', NULL, '["onboarding"]', 8)
    ON CONFLICT (tenant_id, version_id, node_key) DO NOTHING;

    -- Create nodes (Offboarding)
    INSERT INTO process.nodes (tenant_id, version_id, node_key, node_type, lane_key, label, task_type, tags, display_order)
    VALUES
        (v_tenant_id, v_version_id, 'offboard_start', 'start_event', 'hr_team', 'Offboarding Started', NULL, '["offboarding"]', 20),
        (v_tenant_id, v_version_id, 'exit_interview', 'task', 'hr_team', 'Conduct Exit Interview', 'user_task', '["offboarding", "hr"]', 21),
        (v_tenant_id, v_version_id, 'knowledge_transfer', 'task', 'manager', 'Knowledge Transfer', 'user_task', '["offboarding"]', 22),
        (v_tenant_id, v_version_id, 'revoke_access', 'task', 'it_team', 'Revoke IT Access', 'user_task', '["offboarding", "it", "security"]', 23),
        (v_tenant_id, v_version_id, 'collect_assets', 'task', 'it_team', 'Collect Equipment', 'user_task', '["offboarding", "it", "assets"]', 24),
        (v_tenant_id, v_version_id, 'clearance', 'task', 'hr_team', 'Process Clearance', 'user_task', '["offboarding", "hr", "clearance"]', 25),
        (v_tenant_id, v_version_id, 'final_pay', 'task', 'finance_team', 'Calculate Final Pay', 'user_task', '["offboarding", "finance", "statutory"]', 26),
        (v_tenant_id, v_version_id, 'issue_coe', 'task', 'hr_team', 'Issue COE', 'user_task', '["offboarding", "hr", "statutory"]', 27),
        (v_tenant_id, v_version_id, 'offboard_complete', 'end_event', 'hr_team', 'Offboarding Complete', NULL, '["offboarding"]', 28)
    ON CONFLICT (tenant_id, version_id, node_key) DO NOTHING;

    -- Create control rules (SLAs)
    INSERT INTO control.rules (tenant_id, version_id, rule_key, rule_type, trigger_node_key, deadline_days, severity, escalation_role, description)
    VALUES
        (v_tenant_id, v_version_id, 'final_pay_internal', 'internal', 'clearance', 7, 'high', 'finance_manager', 'Final pay within 7 days of clearance'),
        (v_tenant_id, v_version_id, 'final_pay_statutory', 'statutory', 'offboard_start', 30, 'critical', 'hr_director', 'Final pay within 30 days of separation (Labor Code)'),
        (v_tenant_id, v_version_id, 'coe_sla', 'internal', 'offboard_complete', 3, 'medium', 'hr_manager', 'COE within 3 business days of request')
    ON CONFLICT (tenant_id, version_id, rule_key) DO NOTHING;

    -- Create checklists
    INSERT INTO control.checklists (tenant_id, version_id, lane_key, phase, item_key, text, timing_hint, tags, display_order)
    VALUES
        -- Onboarding HR
        (v_tenant_id, v_version_id, 'hr_team', 'onboarding', 'collect_gov_ids', 'Collect government IDs (SSS, PhilHealth, Pag-IBIG, TIN)', 'Day 1', '["statutory"]', 1),
        (v_tenant_id, v_version_id, 'hr_team', 'onboarding', 'employment_contract', 'Sign employment contract', 'Day 1', '["hr"]', 2),
        (v_tenant_id, v_version_id, 'hr_team', 'onboarding', 'company_policies', 'Review company policies', 'Day 1', '["hr"]', 3),
        (v_tenant_id, v_version_id, 'hr_team', 'onboarding', 'emergency_contacts', 'Collect emergency contacts', 'Day 1', '["hr"]', 4),
        -- Onboarding IT
        (v_tenant_id, v_version_id, 'it_team', 'onboarding', 'email_account', 'Create email account', 'Day 1', '["it"]', 1),
        (v_tenant_id, v_version_id, 'it_team', 'onboarding', 'sso_access', 'Setup SSO access', 'Day 1', '["it"]', 2),
        (v_tenant_id, v_version_id, 'it_team', 'onboarding', 'laptop_provision', 'Provision laptop', 'Day 1', '["it", "assets"]', 3),
        -- Offboarding
        (v_tenant_id, v_version_id, 'it_team', 'offboarding', 'disable_accounts', 'Disable all accounts', 'Last Day', '["it", "security"]', 1),
        (v_tenant_id, v_version_id, 'it_team', 'offboarding', 'collect_laptop', 'Collect laptop', 'Last Day', '["it", "assets"]', 2),
        (v_tenant_id, v_version_id, 'finance_team', 'offboarding', 'calculate_final_pay', 'Calculate final pay (including prorated 13th month)', 'Within 7 days', '["finance", "statutory"]', 1),
        (v_tenant_id, v_version_id, 'hr_team', 'offboarding', 'exit_interview_complete', 'Complete exit interview form', 'Before Last Day', '["hr"]', 1),
        (v_tenant_id, v_version_id, 'hr_team', 'offboarding', 'clearance_signed', 'Get clearance signed by all departments', 'Before Last Day', '["hr", "clearance"]', 2)
    ON CONFLICT (tenant_id, version_id, lane_key, item_key) DO NOTHING;

    RAISE NOTICE 'Seeded Hire-to-Retire process definition';
END;
$$;

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Active work items dashboard
CREATE OR REPLACE VIEW run.v_work_items_dashboard AS
SELECT
    wi.tenant_id,
    wi.id AS work_item_id,
    wi.work_item_number,
    wi.title,
    wi.status,
    wi.priority,
    wi.sla_status,
    wi.due_at,
    wi.assignee_id,
    wi.assignee_name,
    ri.case_number,
    ri.case_type,
    ri.subject_name,
    ri.subject_email,
    pd.name AS process_name,
    pl.role_name AS lane_name,
    CASE
        WHEN wi.sla_status = 'breached' THEN 'critical'
        WHEN wi.sla_status = 'at_risk' THEN 'warning'
        WHEN wi.due_at < now() + interval '1 day' THEN 'due_soon'
        ELSE 'normal'
    END AS urgency
FROM run.work_items wi
JOIN run.instances ri ON wi.instance_id = ri.id
JOIN process.definitions pd ON ri.definition_id = pd.id
LEFT JOIN process.lanes pl ON pl.version_id = ri.version_id AND pl.lane_key = wi.lane_key
WHERE wi.status IN ('pending', 'ready', 'in_progress');

-- Open escalations
CREATE OR REPLACE VIEW run.v_open_escalations AS
SELECT
    e.tenant_id,
    e.id AS escalation_id,
    e.reason,
    e.severity,
    e.escalated_to_role,
    e.created_at AS escalated_at,
    ri.case_number,
    ri.case_type,
    ri.subject_name,
    wi.work_item_number,
    wi.title AS work_item_title,
    st.rule_key AS sla_rule
FROM run.escalations e
JOIN run.instances ri ON e.instance_id = ri.id
LEFT JOIN run.work_items wi ON e.work_item_id = wi.id
LEFT JOIN run.sla_timers st ON e.sla_timer_id = st.id
WHERE e.status = 'open'
ORDER BY
    CASE e.severity WHEN 'emergency' THEN 1 WHEN 'critical' THEN 2 ELSE 3 END,
    e.created_at ASC;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

DO $verify$
DECLARE
    missing_tables text[];
BEGIN
    SELECT array_agg(tbl) INTO missing_tables
    FROM (VALUES
        ('process.definitions'),
        ('process.versions'),
        ('process.lanes'),
        ('process.nodes'),
        ('process.edges'),
        ('control.rules'),
        ('control.checklists'),
        ('run.instances'),
        ('run.events'),
        ('run.work_items'),
        ('run.sla_timers'),
        ('run.escalations'),
        ('run.evidence'),
        ('odoo_sync.helpdesk_tickets'),
        ('odoo_sync.project_tasks')
    ) AS required(tbl)
    WHERE NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema || '.' || table_name = required.tbl
    );

    IF array_length(missing_tables, 1) > 0 THEN
        RAISE WARNING 'Missing process runtime tables: %', missing_tables;
    ELSE
        RAISE NOTICE 'All process runtime tables verified ✓';
    END IF;
END;
$verify$;
