-- =============================================================================
-- QMS-LITE: Controlled Document Layer (MasterControl-style)
-- =============================================================================
-- Purpose: Add regulated document control primitives without full QMS overhead
-- Features: Controlled docs, approval workflows, audit trail, read receipts
-- Created: 2025-12-20
-- Rationale: RAG/KG indexes only "effective" versions; agents can draft but
--            cannot mark documents effective without approval workflow completion
-- =============================================================================

-- Schema
CREATE SCHEMA IF NOT EXISTS qms;

-- =============================================================================
-- 1. CONTROLLED DOCUMENTS
-- =============================================================================
-- Document types: SOP, POLICY, WI (Work Instruction), FORM, SPEC, RECORD

CREATE TABLE IF NOT EXISTS qms.controlled_docs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    -- Document identification
    doc_number text NOT NULL,           -- e.g., "SOP-FIN-001"
    doc_type text NOT NULL,             -- SOP|POLICY|WI|FORM|SPEC|RECORD
    title text NOT NULL,
    description text,

    -- Ownership
    owner_id uuid,                      -- Document owner (res.users)
    department text,                    -- e.g., "Finance", "Operations"

    -- Classification
    classification text DEFAULT 'internal',  -- public|internal|confidential|restricted

    -- Lifecycle
    status text NOT NULL DEFAULT 'draft',   -- draft|pending_approval|effective|superseded|obsolete

    -- Review cycle
    review_period_months int DEFAULT 12,
    next_review_at timestamptz,

    -- Metadata
    tags jsonb DEFAULT '[]'::jsonb,
    metadata jsonb DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT valid_doc_type CHECK (
        doc_type IN ('SOP', 'POLICY', 'WI', 'FORM', 'SPEC', 'RECORD')
    ),
    CONSTRAINT valid_status CHECK (
        status IN ('draft', 'pending_approval', 'effective', 'superseded', 'obsolete')
    ),
    CONSTRAINT valid_classification CHECK (
        classification IN ('public', 'internal', 'confidential', 'restricted')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_controlled_docs_number
    ON qms.controlled_docs (tenant_id, doc_number);
CREATE INDEX IF NOT EXISTS ix_controlled_docs_status
    ON qms.controlled_docs (tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_controlled_docs_type
    ON qms.controlled_docs (tenant_id, doc_type);
CREATE INDEX IF NOT EXISTS ix_controlled_docs_review
    ON qms.controlled_docs (tenant_id, next_review_at)
    WHERE status = 'effective';

-- =============================================================================
-- 2. DOCUMENT VERSIONS (Immutable Snapshots)
-- =============================================================================
-- Each version is immutable once created; new changes = new version

CREATE TABLE IF NOT EXISTS qms.doc_versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    doc_id uuid NOT NULL REFERENCES qms.controlled_docs(id) ON DELETE CASCADE,

    -- Version identification
    version_number text NOT NULL,       -- e.g., "1.0", "2.1"
    revision_number int NOT NULL,       -- Numeric for ordering

    -- Content (immutable once created)
    content_md text NOT NULL,           -- Markdown content
    content_html text,                  -- Rendered HTML
    content_hash text NOT NULL,         -- SHA256 for integrity

    -- Version status
    status text NOT NULL DEFAULT 'draft',   -- draft|pending|approved|effective|superseded

    -- Lifecycle dates
    created_at timestamptz NOT NULL DEFAULT now(),
    submitted_at timestamptz,           -- When sent for approval
    approved_at timestamptz,            -- When approved (all approvals complete)
    effective_at timestamptz,           -- When became effective
    superseded_at timestamptz,          -- When superseded by newer version

    -- Reason for revision
    revision_reason text,
    change_summary text,

    -- Author
    author_id uuid,

    -- Metadata
    metadata jsonb DEFAULT '{}'::jsonb,

    CONSTRAINT valid_version_status CHECK (
        status IN ('draft', 'pending', 'approved', 'effective', 'superseded', 'rejected')
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_doc_versions_number
    ON qms.doc_versions (tenant_id, doc_id, version_number);
CREATE INDEX IF NOT EXISTS ix_doc_versions_status
    ON qms.doc_versions (tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_doc_versions_effective
    ON qms.doc_versions (tenant_id, doc_id, effective_at DESC)
    WHERE status = 'effective';

-- =============================================================================
-- 3. APPROVAL ROUTES (Workflow Templates)
-- =============================================================================
-- Define multi-step approval routes by document type

CREATE TABLE IF NOT EXISTS qms.approval_routes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    -- Route identification
    name text NOT NULL,
    description text,

    -- Trigger conditions
    applies_to_types text[] NOT NULL,   -- e.g., ['SOP', 'POLICY']
    applies_to_departments text[],       -- NULL = all departments

    -- Route steps (ordered JSON array)
    steps jsonb NOT NULL,
    -- Example: [
    --   {"step": 1, "role": "author_manager", "action": "review", "required": true},
    --   {"step": 2, "role": "quality_assurance", "action": "approve", "required": true},
    --   {"step": 3, "role": "department_head", "action": "approve", "required": true}
    -- ]

    -- Settings
    sequential boolean DEFAULT true,     -- Steps must complete in order
    allow_delegation boolean DEFAULT true,
    escalation_hours int DEFAULT 72,     -- Escalate after N hours

    is_active boolean DEFAULT true,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_approval_routes_active
    ON qms.approval_routes (tenant_id, is_active)
    WHERE is_active = true;

-- =============================================================================
-- 4. APPROVALS (Actual Approval Records)
-- =============================================================================

CREATE TABLE IF NOT EXISTS qms.approvals (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    doc_version_id uuid NOT NULL REFERENCES qms.doc_versions(id) ON DELETE CASCADE,

    -- Route reference
    route_id uuid REFERENCES qms.approval_routes(id),
    step_number int NOT NULL,

    -- Approver
    approver_id uuid NOT NULL,          -- res.users
    approver_role text,                 -- Role at time of approval
    delegated_from uuid,                -- If delegated, original approver

    -- Decision
    action text NOT NULL,               -- review|approve|reject|delegate
    decision text,                      -- approved|rejected|returned|delegated
    comments text,

    -- Timing
    requested_at timestamptz NOT NULL DEFAULT now(),
    due_at timestamptz,
    completed_at timestamptz,

    -- E-signature placeholder (Part 11 style)
    signature_meaning text,             -- e.g., "I approve this document"
    signature_hash text,                -- Hash of (user_id + doc_version_id + meaning + timestamp)

    CONSTRAINT valid_action CHECK (
        action IN ('review', 'approve', 'reject', 'delegate', 'acknowledge')
    ),
    CONSTRAINT valid_decision CHECK (
        decision IS NULL OR decision IN ('approved', 'rejected', 'returned', 'delegated')
    )
);

CREATE INDEX IF NOT EXISTS ix_approvals_version
    ON qms.approvals (tenant_id, doc_version_id, step_number);
CREATE INDEX IF NOT EXISTS ix_approvals_approver
    ON qms.approvals (tenant_id, approver_id, completed_at)
    WHERE completed_at IS NULL;

-- =============================================================================
-- 5. READ RECEIPTS (Training Acknowledgment)
-- =============================================================================
-- Track "I have read and understood this document"

CREATE TABLE IF NOT EXISTS qms.read_receipts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    doc_version_id uuid NOT NULL REFERENCES qms.doc_versions(id) ON DELETE CASCADE,

    -- Reader
    user_id uuid NOT NULL,

    -- Assignment (if required reading)
    assignment_id uuid,                 -- Link to training assignment
    assigned_at timestamptz,
    due_at timestamptz,

    -- Acknowledgment
    acknowledged_at timestamptz,
    acknowledgment_text text DEFAULT 'I have read and understood this document',

    -- Verification (optional quiz)
    quiz_score float,
    quiz_passed boolean,

    -- Metadata
    ip_address text,
    user_agent text,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_read_receipts_unique
    ON qms.read_receipts (tenant_id, doc_version_id, user_id);
CREATE INDEX IF NOT EXISTS ix_read_receipts_pending
    ON qms.read_receipts (tenant_id, user_id, acknowledged_at)
    WHERE acknowledged_at IS NULL;
CREATE INDEX IF NOT EXISTS ix_read_receipts_overdue
    ON qms.read_receipts (tenant_id, due_at)
    WHERE acknowledged_at IS NULL AND due_at IS NOT NULL;

-- =============================================================================
-- 6. AUDIT EVENTS (Append-Only Audit Trail)
-- =============================================================================
-- Immutable audit log for all QMS actions

CREATE TABLE IF NOT EXISTS qms.audit_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    -- Event identification
    event_type text NOT NULL,
    -- Types: doc_created|doc_updated|version_created|version_submitted|
    --        approval_requested|approval_completed|version_effective|
    --        version_superseded|read_assigned|read_acknowledged|
    --        access_granted|access_revoked

    -- Entity reference
    entity_type text NOT NULL,          -- controlled_doc|doc_version|approval|read_receipt
    entity_id uuid NOT NULL,

    -- Actor
    actor_id uuid,                      -- User who performed action
    actor_role text,                    -- Role at time of action

    -- Change details
    old_values jsonb,                   -- Previous state (for updates)
    new_values jsonb,                   -- New state
    reason text,                        -- Why the change was made

    -- Context
    ip_address text,
    user_agent text,
    session_id text,

    -- Timestamp (immutable, no updated_at)
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Append-only: no UPDATE or DELETE allowed via RLS
CREATE INDEX IF NOT EXISTS ix_audit_events_entity
    ON qms.audit_events (tenant_id, entity_type, entity_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_audit_events_actor
    ON qms.audit_events (tenant_id, actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_audit_events_type
    ON qms.audit_events (tenant_id, event_type, created_at DESC);

-- =============================================================================
-- 7. CHANGE CONTROLS (Optional - for MasterControl parity)
-- =============================================================================

CREATE TABLE IF NOT EXISTS qms.change_controls (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    -- Change identification
    change_number text NOT NULL,        -- e.g., "CC-2025-001"
    title text NOT NULL,
    description text,

    -- Affected documents
    affected_docs jsonb DEFAULT '[]'::jsonb,
    -- [{"doc_id": "uuid", "doc_number": "SOP-FIN-001", "current_version": "1.0"}]

    -- Impact assessment
    impact_assessment text,
    risk_level text,                    -- low|medium|high|critical

    -- Workflow
    status text DEFAULT 'draft',        -- draft|submitted|approved|implemented|closed|rejected

    -- Key dates
    requested_at timestamptz,
    approved_at timestamptz,
    target_implementation_at timestamptz,
    implemented_at timestamptz,
    verification_completed_at timestamptz,

    -- Ownership
    requester_id uuid,
    approver_id uuid,
    implementer_id uuid,

    -- Metadata
    metadata jsonb DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_change_controls_number
    ON qms.change_controls (tenant_id, change_number);
CREATE INDEX IF NOT EXISTS ix_change_controls_status
    ON qms.change_controls (tenant_id, status);

-- =============================================================================
-- 8. EVIDENCE PACKS (Snapshots for Audits)
-- =============================================================================
-- Package of docs + citations + approvals for audit/compliance

CREATE TABLE IF NOT EXISTS qms.evidence_packs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    -- Pack identification
    pack_number text NOT NULL,
    title text NOT NULL,
    purpose text,                       -- audit|compliance|training|investigation

    -- Contents
    contents jsonb NOT NULL,
    -- {
    --   "documents": [{"doc_id": "uuid", "version_id": "uuid", "snapshot_hash": "..."}],
    --   "approvals": [{"approval_id": "uuid", "completed_at": "..."}],
    --   "read_receipts": [{"receipt_id": "uuid", "user_id": "uuid"}],
    --   "audit_events": [{"event_id": "uuid", "event_type": "..."}]
    -- }

    -- Integrity
    pack_hash text NOT NULL,            -- SHA256 of entire contents
    signed_at timestamptz,
    signed_by uuid,

    -- Lifecycle
    status text DEFAULT 'draft',        -- draft|finalized|submitted|archived
    finalized_at timestamptz,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_evidence_packs_number
    ON qms.evidence_packs (tenant_id, pack_number);

-- =============================================================================
-- 9. HELPER FUNCTIONS
-- =============================================================================

-- Get effective version for a document
CREATE OR REPLACE FUNCTION qms.get_effective_version(
    p_tenant_id uuid,
    p_doc_id uuid
)
RETURNS uuid
LANGUAGE sql STABLE
AS $func$
SELECT id
FROM qms.doc_versions
WHERE tenant_id = p_tenant_id
  AND doc_id = p_doc_id
  AND status = 'effective'
ORDER BY effective_at DESC
LIMIT 1;
$func$;

-- Check if all approvals complete for a version
CREATE OR REPLACE FUNCTION qms.is_fully_approved(
    p_tenant_id uuid,
    p_version_id uuid
)
RETURNS boolean
LANGUAGE sql STABLE
AS $func$
SELECT NOT EXISTS (
    SELECT 1
    FROM qms.approvals
    WHERE tenant_id = p_tenant_id
      AND doc_version_id = p_version_id
      AND completed_at IS NULL
);
$func$;

-- Get pending approvals for user
CREATE OR REPLACE FUNCTION qms.get_pending_approvals(
    p_tenant_id uuid,
    p_user_id uuid,
    p_limit int DEFAULT 20
)
RETURNS TABLE (
    approval_id uuid,
    doc_version_id uuid,
    doc_number text,
    doc_title text,
    version_number text,
    step_number int,
    requested_at timestamptz,
    due_at timestamptz
)
LANGUAGE sql STABLE
AS $func$
SELECT
    a.id AS approval_id,
    a.doc_version_id,
    cd.doc_number,
    cd.title AS doc_title,
    dv.version_number,
    a.step_number,
    a.requested_at,
    a.due_at
FROM qms.approvals a
JOIN qms.doc_versions dv ON a.doc_version_id = dv.id
JOIN qms.controlled_docs cd ON dv.doc_id = cd.id
WHERE a.tenant_id = p_tenant_id
  AND a.approver_id = p_user_id
  AND a.completed_at IS NULL
ORDER BY a.due_at ASC NULLS LAST, a.requested_at ASC
LIMIT p_limit;
$func$;

-- Get overdue read receipts for user
CREATE OR REPLACE FUNCTION qms.get_overdue_reads(
    p_tenant_id uuid,
    p_user_id uuid
)
RETURNS TABLE (
    receipt_id uuid,
    doc_version_id uuid,
    doc_number text,
    doc_title text,
    assigned_at timestamptz,
    due_at timestamptz,
    days_overdue int
)
LANGUAGE sql STABLE
AS $func$
SELECT
    rr.id AS receipt_id,
    rr.doc_version_id,
    cd.doc_number,
    cd.title AS doc_title,
    rr.assigned_at,
    rr.due_at,
    EXTRACT(DAY FROM (now() - rr.due_at))::int AS days_overdue
FROM qms.read_receipts rr
JOIN qms.doc_versions dv ON rr.doc_version_id = dv.id
JOIN qms.controlled_docs cd ON dv.doc_id = cd.id
WHERE rr.tenant_id = p_tenant_id
  AND rr.user_id = p_user_id
  AND rr.acknowledged_at IS NULL
  AND rr.due_at < now()
ORDER BY rr.due_at ASC;
$func$;

-- Log audit event (helper)
CREATE OR REPLACE FUNCTION qms.log_event(
    p_tenant_id uuid,
    p_event_type text,
    p_entity_type text,
    p_entity_id uuid,
    p_actor_id uuid,
    p_old_values jsonb DEFAULT NULL,
    p_new_values jsonb DEFAULT NULL,
    p_reason text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
AS $func$
DECLARE
    v_event_id uuid;
BEGIN
    INSERT INTO qms.audit_events (
        tenant_id, event_type, entity_type, entity_id,
        actor_id, old_values, new_values, reason
    ) VALUES (
        p_tenant_id, p_event_type, p_entity_type, p_entity_id,
        p_actor_id, p_old_values, p_new_values, p_reason
    )
    RETURNING id INTO v_event_id;

    RETURN v_event_id;
END;
$func$;

-- =============================================================================
-- 10. VIEWS FOR RAG INTEGRATION
-- =============================================================================

-- Only index effective versions in RAG
CREATE OR REPLACE VIEW qms.v_effective_docs_for_rag AS
SELECT
    cd.id AS doc_id,
    cd.tenant_id,
    cd.doc_number,
    cd.doc_type,
    cd.title,
    cd.department,
    cd.classification,
    dv.id AS version_id,
    dv.version_number,
    dv.content_md,
    dv.content_hash,
    dv.effective_at,
    dv.revision_reason
FROM qms.controlled_docs cd
JOIN qms.doc_versions dv ON cd.id = dv.doc_id
WHERE cd.status = 'effective'
  AND dv.status = 'effective';

COMMENT ON VIEW qms.v_effective_docs_for_rag IS
'Only effective document versions - use this view to feed RAG indexers';

-- Documents pending approval (for dashboards)
CREATE OR REPLACE VIEW qms.v_pending_approvals AS
SELECT
    cd.tenant_id,
    cd.doc_number,
    cd.title,
    dv.version_number,
    a.approver_id,
    a.step_number,
    a.requested_at,
    a.due_at,
    CASE
        WHEN a.due_at < now() THEN 'overdue'
        WHEN a.due_at < now() + interval '24 hours' THEN 'due_soon'
        ELSE 'on_track'
    END AS urgency
FROM qms.approvals a
JOIN qms.doc_versions dv ON a.doc_version_id = dv.id
JOIN qms.controlled_docs cd ON dv.doc_id = cd.id
WHERE a.completed_at IS NULL;

-- =============================================================================
-- 11. RLS POLICIES
-- =============================================================================

ALTER TABLE qms.controlled_docs ENABLE ROW LEVEL SECURITY;
ALTER TABLE qms.doc_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE qms.approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE qms.read_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE qms.audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE qms.change_controls ENABLE ROW LEVEL SECURITY;
ALTER TABLE qms.evidence_packs ENABLE ROW LEVEL SECURITY;

-- Audit events: APPEND-ONLY (no update, no delete)
CREATE POLICY audit_events_insert_only ON qms.audit_events
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY audit_events_select ON qms.audit_events
    FOR SELECT
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- Note: No UPDATE or DELETE policies = effectively immutable

-- =============================================================================
-- 12. SEED: Sample Approval Routes
-- =============================================================================

DO $$
DECLARE
    v_tenant_id uuid;
BEGIN
    SELECT id INTO v_tenant_id FROM core.tenants LIMIT 1;

    IF v_tenant_id IS NULL THEN
        RAISE NOTICE 'No tenant found, skipping approval route seeding';
        RETURN;
    END IF;

    INSERT INTO qms.approval_routes (
        tenant_id, name, description, applies_to_types, steps
    ) VALUES
    (
        v_tenant_id,
        'Standard SOP Approval',
        'Two-tier review for standard operating procedures',
        ARRAY['SOP', 'WI'],
        '[
            {"step": 1, "role": "department_manager", "action": "review", "required": true},
            {"step": 2, "role": "quality_assurance", "action": "approve", "required": true}
        ]'::jsonb
    ),
    (
        v_tenant_id,
        'Policy Approval',
        'Three-tier approval for company policies',
        ARRAY['POLICY'],
        '[
            {"step": 1, "role": "author_manager", "action": "review", "required": true},
            {"step": 2, "role": "legal", "action": "review", "required": false},
            {"step": 3, "role": "executive", "action": "approve", "required": true}
        ]'::jsonb
    ),
    (
        v_tenant_id,
        'Form Approval',
        'Single approval for forms and templates',
        ARRAY['FORM'],
        '[
            {"step": 1, "role": "department_manager", "action": "approve", "required": true}
        ]'::jsonb
    )
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Seeded 3 approval routes';
END;
$$;

-- =============================================================================
-- 13. VERIFICATION
-- =============================================================================

DO $verify$
DECLARE
    missing_tables text[];
    table_count int;
BEGIN
    SELECT array_agg(tbl) INTO missing_tables
    FROM (VALUES
        ('qms.controlled_docs'),
        ('qms.doc_versions'),
        ('qms.approval_routes'),
        ('qms.approvals'),
        ('qms.read_receipts'),
        ('qms.audit_events'),
        ('qms.change_controls'),
        ('qms.evidence_packs')
    ) AS required(tbl)
    WHERE NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema || '.' || table_name = required.tbl
    );

    IF array_length(missing_tables, 1) > 0 THEN
        RAISE WARNING 'Missing QMS tables: %', missing_tables;
    ELSE
        RAISE NOTICE 'All QMS-lite tables verified ✓';
    END IF;

    -- Count tables
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'qms';

    RAISE NOTICE 'QMS schema has % tables', table_count;
END;
$verify$;
