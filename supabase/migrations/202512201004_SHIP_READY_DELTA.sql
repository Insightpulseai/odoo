-- =============================================================================
-- Ship-Ready Delta: Document Versioning + Capability Mapping + Declarative Pipelines
-- =============================================================================
-- Version: 1.1.0
--
-- Adds missing pieces for "SAP Concur + SRM → Odoo CE/OCA" parity:
--   * rag.document_versions - Versioned snapshots with diffs
--   * rag.page_links - URL graph for link analysis
--   * rag.source_acl - Per-source ACL constraints
--   * gold.capability_map - SAP→Odoo/OCA mapping registry
--   * runtime.pipeline_defs - Declarative pipeline definitions
--   * runtime.pipeline_runs - Pipeline execution history
--   * runtime.pipeline_stages - Stage-level tracking
--
-- Pattern: Databricks Lakeflow-style declarative pipelines for docs/knowledge
-- =============================================================================

BEGIN;

-- Ensure schemas exist
CREATE SCHEMA IF NOT EXISTS gold;

-- =============================================================================
-- 1. RAG.DOCUMENT_VERSIONS — Versioned Page Snapshots
-- =============================================================================

CREATE TABLE IF NOT EXISTS rag.document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,

    -- Version identity
    version_number INT NOT NULL,
    version_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Content snapshot (actual page content)
    content_md TEXT NOT NULL, -- Normalized markdown
    content_html TEXT, -- Original HTML if applicable
    content_hash TEXT NOT NULL, -- SHA256 for dedup

    -- Diff from previous version
    previous_version_id UUID REFERENCES rag.document_versions(id),
    diff_summary JSONB, -- {lines_added, lines_removed, sections_changed}
    diff_patch TEXT, -- Unified diff patch

    -- Metadata at time of capture
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- {
    --   "source_url": "...",
    --   "last_modified": "...",
    --   "etag": "...",
    --   "crawl_run_id": "..."
    -- }

    -- Quality signals
    word_count INT,
    link_count INT,
    heading_count INT,
    code_block_count INT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_doc_versions_document ON rag.document_versions(tenant_id, document_id, version_at DESC);
CREATE UNIQUE INDEX ux_doc_versions_hash ON rag.document_versions(tenant_id, document_id, content_hash);
CREATE INDEX idx_doc_versions_number ON rag.document_versions(document_id, version_number DESC);

-- Enable RLS
ALTER TABLE rag.document_versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY document_versions_tenant_isolation ON rag.document_versions
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE rag.document_versions IS 'Versioned page snapshots with diff tracking';

-- =============================================================================
-- 2. RAG.PAGE_LINKS — URL Link Graph
-- =============================================================================

CREATE TABLE IF NOT EXISTS rag.page_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- Link source
    from_document_id UUID NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,
    from_chunk_id UUID REFERENCES docs.chunks(id),

    -- Link target
    to_url TEXT NOT NULL,
    to_document_id UUID REFERENCES rag.documents(id), -- Resolved internal link

    -- Link metadata
    anchor_text TEXT,
    link_type TEXT DEFAULT 'hyperlink' CHECK (link_type IN (
        'hyperlink', 'image', 'import', 'reference', 'see_also', 'dependency'
    )),
    context_text TEXT, -- Surrounding text for semantic context

    -- Position
    position_start INT,
    position_end INT,

    -- Status
    is_internal BOOLEAN DEFAULT false, -- Points to another doc in our corpus
    is_broken BOOLEAN DEFAULT false,
    last_checked_at TIMESTAMPTZ,
    http_status INT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_page_links_from ON rag.page_links(tenant_id, from_document_id);
CREATE INDEX idx_page_links_to ON rag.page_links(to_document_id) WHERE to_document_id IS NOT NULL;
CREATE INDEX idx_page_links_url ON rag.page_links(to_url);
CREATE INDEX idx_page_links_broken ON rag.page_links(is_broken) WHERE is_broken = true;

-- Enable RLS
ALTER TABLE rag.page_links ENABLE ROW LEVEL SECURITY;

CREATE POLICY page_links_tenant_isolation ON rag.page_links
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE rag.page_links IS 'URL link graph for page relationship analysis';

-- =============================================================================
-- 3. RAG.SOURCE_ACL — Per-Source Access Control
-- =============================================================================

CREATE TABLE IF NOT EXISTS rag.source_acl (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- What this ACL applies to
    source_id UUID REFERENCES sources.sources(id) ON DELETE CASCADE,
    source_type TEXT, -- Alternative: apply to all sources of this type

    -- Principal
    principal_type TEXT NOT NULL CHECK (principal_type IN ('role', 'user', 'team', 'service')),
    principal_id UUID NOT NULL,

    -- Permission
    permission TEXT NOT NULL DEFAULT 'read' CHECK (permission IN (
        'read', 'write', 'crawl', 'admin'
    )),
    allow BOOLEAN NOT NULL DEFAULT true,

    -- Constraints
    path_pattern TEXT, -- Glob pattern: "docs/internal/**"
    doc_type_filter TEXT[], -- Only applies to certain doc types

    -- Metadata
    granted_by UUID,
    granted_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ,
    reason TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_source_acl_source ON rag.source_acl(source_id);
CREATE INDEX idx_source_acl_principal ON rag.source_acl(principal_type, principal_id);
CREATE INDEX idx_source_acl_tenant ON rag.source_acl(tenant_id);

-- Enable RLS
ALTER TABLE rag.source_acl ENABLE ROW LEVEL SECURITY;

CREATE POLICY source_acl_tenant_isolation ON rag.source_acl
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE rag.source_acl IS 'Per-source access control constraints';

-- =============================================================================
-- 4. GOLD.CAPABILITY_MAP — SAP → Odoo/OCA Mapping Registry
-- =============================================================================

CREATE TABLE IF NOT EXISTS gold.capability_map (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- Source framework
    source_framework TEXT NOT NULL CHECK (source_framework IN (
        'sap_concur', 'sap_srm', 'sap_ariba', 'sap_fieldglass',
        'cheqroom', 'notion_ppm', 'clarity_ppm', 'ms_dynamics',
        'odoo_enterprise', 'other'
    )),
    source_category TEXT, -- e.g., "Expense Management", "Procurement"
    source_feature TEXT, -- e.g., "Receipt OCR", "3-Way Match"

    -- Capability identity
    capability_key TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,

    -- Target mapping
    target_modules JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- [
    --   {"type": "odoo_core", "module": "hr_expense", "version": "18.0"},
    --   {"type": "oca", "repo": "OCA/hr-expense", "module": "hr_expense_advance_clearing", "version": "18.0"}
    -- ]

    -- Implementation notes
    config_notes TEXT, -- Configuration steps
    implementation_notes TEXT, -- Custom implementation if needed
    workarounds TEXT, -- Known workarounds
    limitations TEXT[], -- Known limitations

    -- Parity level
    parity_level TEXT NOT NULL DEFAULT 'partial' CHECK (parity_level IN (
        'full', 'partial', 'alternative', 'workaround', 'gap', 'not_applicable'
    )),
    parity_score DECIMAL(3,2), -- 0-1 coverage score
    parity_notes TEXT,

    -- Evidence (docs references)
    docs_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- [
    --   {"source": "sap_help", "doc_id": "...", "url": "...", "section": "..."},
    --   {"source": "odoo_docs", "doc_id": "...", "url": "..."}
    -- ]

    -- Dependencies
    depends_on TEXT[], -- Other capability_keys this depends on
    conflicts_with TEXT[], -- Capability_keys this conflicts with

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('draft', 'active', 'deprecated', 'superseded')),
    superseded_by UUID REFERENCES gold.capability_map(id),
    verified_at TIMESTAMPTZ,
    verified_by UUID,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID
);

CREATE UNIQUE INDEX ux_capability_map_key ON gold.capability_map(tenant_id, source_framework, capability_key);
CREATE INDEX idx_capability_map_framework ON gold.capability_map(source_framework);
CREATE INDEX idx_capability_map_parity ON gold.capability_map(parity_level);
CREATE INDEX idx_capability_map_category ON gold.capability_map(source_category);

-- Enable RLS
ALTER TABLE gold.capability_map ENABLE ROW LEVEL SECURITY;

CREATE POLICY capability_map_tenant_isolation ON gold.capability_map
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE gold.capability_map IS 'SAP/Enterprise → Odoo CE/OCA capability mapping registry';

-- =============================================================================
-- 5. RUNTIME.PIPELINE_DEFS — Declarative Pipeline Definitions
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.pipeline_defs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- Pipeline identity
    pipeline_key TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    pipeline_type TEXT NOT NULL CHECK (pipeline_type IN (
        'docs_ingestion', 'capability_mapping', 'entity_extraction',
        'embedding_refresh', 'link_validation', 'parity_audit'
    )),

    -- Version
    version INT NOT NULL DEFAULT 1,
    version_hash TEXT, -- SHA256 of definition

    -- Definition (YAML/JSON)
    definition JSONB NOT NULL,
    -- {
    --   "sources": [{"source_id": "...", "filters": {...}}],
    --   "stages": [
    --     {"name": "crawl", "type": "crawler", "config": {...}},
    --     {"name": "normalize", "type": "transformer", "config": {...}},
    --     {"name": "chunk", "type": "chunker", "config": {...}},
    --     {"name": "embed", "type": "embedder", "config": {...}},
    --     {"name": "extract_entities", "type": "extractor", "config": {...}},
    --     {"name": "publish", "type": "publisher", "config": {...}}
    --   ],
    --   "schedule": "0 2 * * *",
    --   "triggers": ["source_update", "manual"],
    --   "retry_policy": {...},
    --   "notifications": {...}
    -- }

    -- DAG (computed from definition)
    dag_json JSONB, -- {nodes: [...], edges: [...]}

    -- Scheduling
    schedule_cron TEXT,
    schedule_timezone TEXT DEFAULT 'UTC',
    triggers TEXT[], -- 'schedule', 'manual', 'webhook', 'source_update'

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('draft', 'active', 'paused', 'archived')),
    is_default BOOLEAN DEFAULT false,

    -- Stats
    total_runs INT DEFAULT 0,
    successful_runs INT DEFAULT 0,
    failed_runs INT DEFAULT 0,
    last_run_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID,

    UNIQUE (tenant_id, pipeline_key, version)
);

CREATE INDEX idx_pipeline_defs_tenant ON runtime.pipeline_defs(tenant_id);
CREATE INDEX idx_pipeline_defs_type ON runtime.pipeline_defs(pipeline_type);
CREATE INDEX idx_pipeline_defs_status ON runtime.pipeline_defs(status) WHERE status = 'active';

-- Enable RLS
ALTER TABLE runtime.pipeline_defs ENABLE ROW LEVEL SECURITY;

CREATE POLICY pipeline_defs_tenant_isolation ON runtime.pipeline_defs
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.pipeline_defs IS 'Declarative pipeline definitions (Databricks-style)';

-- =============================================================================
-- 6. RUNTIME.PIPELINE_RUNS — Pipeline Execution History
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    pipeline_id UUID NOT NULL REFERENCES runtime.pipeline_defs(id),
    pipeline_version INT NOT NULL,

    -- Run identity
    run_number INT NOT NULL,

    -- Trigger
    triggered_by TEXT NOT NULL DEFAULT 'manual', -- schedule, manual, webhook, source_update
    triggered_by_user UUID,
    trigger_metadata JSONB DEFAULT '{}'::jsonb,

    -- Scope (partial runs)
    scope TEXT DEFAULT 'full' CHECK (scope IN ('full', 'partial', 'single_source', 'single_doc')),
    scope_filter JSONB, -- {source_ids: [...], doc_ids: [...]}

    -- Status
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'cancelled', 'partial_success'
    )),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds DECIMAL(10,2),

    -- Progress
    current_stage TEXT,
    progress_pct INT DEFAULT 0,

    -- Metrics (aggregate)
    metrics JSONB DEFAULT '{}'::jsonb,
    -- {
    --   "sources_processed": 5,
    --   "documents_fetched": 150,
    --   "documents_created": 10,
    --   "documents_updated": 20,
    --   "chunks_created": 500,
    --   "embeddings_created": 500,
    --   "entities_extracted": 75,
    --   "links_discovered": 200,
    --   "bytes_processed": 1048576
    -- }

    -- Errors
    error_count INT DEFAULT 0,
    errors JSONB DEFAULT '[]'::jsonb,
    fatal_error TEXT,

    -- Artifacts
    artifacts JSONB DEFAULT '{}'::jsonb, -- {report_url, diff_url, logs_url}

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_pipeline_runs_pipeline ON runtime.pipeline_runs(pipeline_id, run_number DESC);
CREATE INDEX idx_pipeline_runs_tenant ON runtime.pipeline_runs(tenant_id, started_at DESC);
CREATE INDEX idx_pipeline_runs_status ON runtime.pipeline_runs(status) WHERE status IN ('pending', 'running');

-- Enable RLS
ALTER TABLE runtime.pipeline_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY pipeline_runs_tenant_isolation ON runtime.pipeline_runs
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.pipeline_runs IS 'Pipeline execution history with metrics';

-- =============================================================================
-- 7. RUNTIME.PIPELINE_STAGES — Stage-Level Execution Tracking
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.pipeline_stages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runtime.pipeline_runs(id) ON DELETE CASCADE,

    -- Stage identity
    stage_name TEXT NOT NULL,
    stage_type TEXT NOT NULL,
    stage_index INT NOT NULL,

    -- Status
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'skipped'
    )),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds DECIMAL(10,2),

    -- Input/Output counts
    input_count INT DEFAULT 0,
    output_count INT DEFAULT 0,
    error_count INT DEFAULT 0,

    -- Stage-specific metrics
    metrics JSONB DEFAULT '{}'::jsonb,

    -- Errors
    errors JSONB DEFAULT '[]'::jsonb,
    fatal_error TEXT,

    -- Logs
    logs_url TEXT,
    log_tail TEXT, -- Last N lines of log

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_pipeline_stages_run ON runtime.pipeline_stages(run_id, stage_index);

COMMENT ON TABLE runtime.pipeline_stages IS 'Stage-level execution tracking for pipelines';

-- =============================================================================
-- 8. RUNTIME.PIPELINE_ISSUES — Issues Panel
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.pipeline_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    run_id UUID REFERENCES runtime.pipeline_runs(id),
    stage_id UUID REFERENCES runtime.pipeline_stages(id),

    -- Issue details
    issue_type TEXT NOT NULL CHECK (issue_type IN (
        'broken_link', 'parse_failure', 'embedding_failure', 'acl_violation',
        'timeout', 'rate_limit', 'auth_failure', 'validation_error',
        'duplicate_content', 'missing_content', 'encoding_error'
    )),
    severity TEXT NOT NULL DEFAULT 'warning' CHECK (severity IN (
        'info', 'warning', 'error', 'critical'
    )),

    -- Context
    source_id UUID REFERENCES sources.sources(id),
    document_id UUID REFERENCES rag.documents(id),
    chunk_id UUID REFERENCES docs.chunks(id),
    url TEXT,

    -- Details
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    stack_trace TEXT,

    -- Resolution
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved', 'ignored')),
    resolved_at TIMESTAMPTZ,
    resolved_by UUID,
    resolution_notes TEXT,

    -- Recurrence
    occurrence_count INT DEFAULT 1,
    first_seen_at TIMESTAMPTZ DEFAULT now(),
    last_seen_at TIMESTAMPTZ DEFAULT now(),

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_pipeline_issues_run ON runtime.pipeline_issues(run_id);
CREATE INDEX idx_pipeline_issues_tenant ON runtime.pipeline_issues(tenant_id, created_at DESC);
CREATE INDEX idx_pipeline_issues_status ON runtime.pipeline_issues(status) WHERE status = 'open';
CREATE INDEX idx_pipeline_issues_type ON runtime.pipeline_issues(issue_type);

-- Enable RLS
ALTER TABLE runtime.pipeline_issues ENABLE ROW LEVEL SECURITY;

CREATE POLICY pipeline_issues_tenant_isolation ON runtime.pipeline_issues
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.pipeline_issues IS 'Pipeline issues panel for debugging';

-- =============================================================================
-- 9. HELPER FUNCTIONS
-- =============================================================================

-- Get latest document version
CREATE OR REPLACE FUNCTION rag.get_latest_version(
    p_document_id UUID
)
RETURNS rag.document_versions
LANGUAGE sql STABLE
AS $func$
    SELECT *
    FROM rag.document_versions
    WHERE document_id = p_document_id
    ORDER BY version_at DESC
    LIMIT 1;
$func$;

-- Get capability mapping for a source framework
CREATE OR REPLACE FUNCTION gold.get_capability_map(
    p_tenant_id UUID,
    p_source_framework TEXT,
    p_category TEXT DEFAULT NULL
)
RETURNS TABLE (
    capability_key TEXT,
    title TEXT,
    parity_level TEXT,
    parity_score DECIMAL,
    target_modules JSONB,
    source_category TEXT,
    source_feature TEXT
)
LANGUAGE sql STABLE
AS $func$
    SELECT
        cm.capability_key,
        cm.title,
        cm.parity_level,
        cm.parity_score,
        cm.target_modules,
        cm.source_category,
        cm.source_feature
    FROM gold.capability_map cm
    WHERE cm.tenant_id = p_tenant_id
      AND cm.source_framework = p_source_framework
      AND cm.status = 'active'
      AND (p_category IS NULL OR cm.source_category = p_category)
    ORDER BY cm.source_category, cm.title;
$func$;

-- Check source ACL for retrieval
CREATE OR REPLACE FUNCTION rag.check_source_access(
    p_tenant_id UUID,
    p_source_id UUID,
    p_user_id UUID,
    p_user_roles UUID[]
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $func$
DECLARE
    v_denied BOOLEAN := false;
    v_allowed BOOLEAN := false;
BEGIN
    -- Check for explicit denies
    SELECT true INTO v_denied
    FROM rag.source_acl
    WHERE tenant_id = p_tenant_id
      AND source_id = p_source_id
      AND permission = 'read'
      AND allow = false
      AND (expires_at IS NULL OR expires_at > now())
      AND (
          (principal_type = 'user' AND principal_id = p_user_id) OR
          (principal_type = 'role' AND principal_id = ANY(p_user_roles))
      )
    LIMIT 1;

    IF v_denied THEN
        RETURN false;
    END IF;

    -- Check for allows
    SELECT true INTO v_allowed
    FROM rag.source_acl
    WHERE tenant_id = p_tenant_id
      AND source_id = p_source_id
      AND permission = 'read'
      AND allow = true
      AND (expires_at IS NULL OR expires_at > now())
      AND (
          (principal_type = 'user' AND principal_id = p_user_id) OR
          (principal_type = 'role' AND principal_id = ANY(p_user_roles))
      )
    LIMIT 1;

    -- If no ACL rules, default to allow (source-level control only)
    RETURN COALESCE(v_allowed, true);
END;
$func$;

-- =============================================================================
-- 10. VIEWS FOR PIPELINE UI
-- =============================================================================

-- Pipeline overview with run stats
CREATE OR REPLACE VIEW runtime.pipeline_overview AS
SELECT
    p.id,
    p.tenant_id,
    p.pipeline_key,
    p.name,
    p.pipeline_type,
    p.status,
    p.schedule_cron,
    p.total_runs,
    p.successful_runs,
    p.failed_runs,
    p.last_run_at,
    p.last_success_at,
    CASE
        WHEN p.status = 'paused' THEN 'paused'
        WHEN p.failed_runs > p.successful_runs AND p.total_runs > 5 THEN 'unhealthy'
        WHEN p.last_success_at < now() - interval '7 days' THEN 'stale'
        ELSE 'healthy'
    END AS health_status,
    (SELECT COUNT(*) FROM runtime.pipeline_issues i
     JOIN runtime.pipeline_runs r ON r.id = i.run_id
     WHERE r.pipeline_id = p.id AND i.status = 'open') AS open_issues
FROM runtime.pipeline_defs p
WHERE p.status != 'archived';

-- Run details with stage breakdown
CREATE OR REPLACE VIEW runtime.run_details AS
SELECT
    r.id AS run_id,
    r.tenant_id,
    r.pipeline_id,
    p.name AS pipeline_name,
    r.run_number,
    r.status,
    r.triggered_by,
    r.started_at,
    r.completed_at,
    r.duration_seconds,
    r.metrics,
    r.error_count,
    (SELECT COUNT(*) FROM runtime.pipeline_stages s WHERE s.run_id = r.id AND s.status = 'completed') AS stages_completed,
    (SELECT COUNT(*) FROM runtime.pipeline_stages s WHERE s.run_id = r.id) AS stages_total,
    (SELECT jsonb_agg(jsonb_build_object(
        'name', s.stage_name,
        'status', s.status,
        'duration', s.duration_seconds,
        'input', s.input_count,
        'output', s.output_count,
        'errors', s.error_count
    ) ORDER BY s.stage_index)
     FROM runtime.pipeline_stages s WHERE s.run_id = r.id) AS stages
FROM runtime.pipeline_runs r
JOIN runtime.pipeline_defs p ON p.id = r.pipeline_id;

-- Capability parity summary
CREATE OR REPLACE VIEW gold.capability_parity_summary AS
SELECT
    tenant_id,
    source_framework,
    COUNT(*) AS total_capabilities,
    COUNT(*) FILTER (WHERE parity_level = 'full') AS full_parity,
    COUNT(*) FILTER (WHERE parity_level = 'partial') AS partial_parity,
    COUNT(*) FILTER (WHERE parity_level = 'alternative') AS alternative,
    COUNT(*) FILTER (WHERE parity_level = 'workaround') AS workaround,
    COUNT(*) FILTER (WHERE parity_level = 'gap') AS gaps,
    AVG(COALESCE(parity_score, 0.5))::DECIMAL(3,2) AS avg_parity_score
FROM gold.capability_map
WHERE status = 'active'
GROUP BY tenant_id, source_framework;

-- =============================================================================
-- 11. SEED SAP CONCUR → ODOO CE/OCA CAPABILITY MAPPINGS
-- =============================================================================

-- Note: These will be tenant-specific. Insert with a specific tenant_id in practice.
-- This is a template showing the structure.

COMMENT ON TABLE gold.capability_map IS 'Seed with mappings like:

-- Expense Management (SAP Concur → Odoo CE/OCA)
INSERT INTO gold.capability_map (tenant_id, source_framework, source_category, source_feature, capability_key, title, parity_level, target_modules, config_notes) VALUES
(''<tenant_id>'', ''sap_concur'', ''Expense Management'', ''Expense Entry'', ''concur_expense_entry'', ''Expense Line Item Entry'', ''full'',
 ''[{"type": "odoo_core", "module": "hr_expense", "version": "18.0"}]''::jsonb,
 ''Standard Odoo CE Expenses app. Configure expense categories, policies.''),

(''<tenant_id>'', ''sap_concur'', ''Expense Management'', ''Receipt Capture'', ''concur_receipt_ocr'', ''Receipt OCR and Attachment'', ''partial'',
 ''[{"type": "odoo_core", "module": "hr_expense", "version": "18.0"},
   {"type": "external", "service": "paddleocr", "note": "OCR in Supabase Edge Function"}]''::jsonb,
 ''Odoo provides attachment. OCR runs in Supabase, pushes structured data via API.''),

(''<tenant_id>'', ''sap_concur'', ''Expense Management'', ''Multi-Level Approval'', ''concur_approval_workflow'', ''Expense Approval Workflow'', ''partial'',
 ''[{"type": "oca", "repo": "OCA/hr-expense", "module": "hr_expense_tier_validation", "version": "18.0"}]''::jsonb,
 ''Use OCA tier validation for multi-level approvals.''),

(''<tenant_id>'', ''sap_concur'', ''Expense Management'', ''Policy Enforcement'', ''concur_policy_rules'', ''Expense Policy Rules'', ''alternative'',
 ''[{"type": "external", "service": "supabase", "table": "gold.assertions", "note": "Policy rules in Supabase"}]''::jsonb,
 ''Complex policy rules in Supabase gold.assertions. Odoo for basic validation.'');

-- Procurement (SAP SRM → Odoo CE/OCA)
INSERT INTO gold.capability_map (tenant_id, source_framework, source_category, source_feature, capability_key, title, parity_level, target_modules) VALUES
(''<tenant_id>'', ''sap_srm'', ''Procurement'', ''Purchase Requisition'', ''srm_pr'', ''Purchase Requisition'', ''full'',
 ''[{"type": "oca", "repo": "OCA/purchase-workflow", "module": "purchase_request", "version": "18.0"}]''::jsonb),

(''<tenant_id>'', ''sap_srm'', ''Procurement'', ''3-Way Match'', ''srm_3way_match'', ''PO/Receipt/Invoice Match'', ''full'',
 ''[{"type": "odoo_core", "module": "purchase", "version": "18.0"},
   {"type": "odoo_core", "module": "stock", "version": "18.0"},
   {"type": "odoo_core", "module": "account", "version": "18.0"}]''::jsonb),

(''<tenant_id>'', ''sap_srm'', ''Procurement'', ''Supplier Portal'', ''srm_supplier_portal'', ''Supplier Self-Service Portal'', ''gap'',
 ''[]''::jsonb);';

-- =============================================================================
-- 12. SEED DEFAULT PIPELINE DEFINITIONS
-- =============================================================================

-- These are templates - actual insertion requires tenant_id
COMMENT ON TABLE runtime.pipeline_defs IS 'Default pipelines to create per tenant:

-- Docs Ingestion Pipeline
{
  "pipeline_key": "docs_ingestion_main",
  "name": "Main Documentation Ingestion",
  "pipeline_type": "docs_ingestion",
  "definition": {
    "sources": [{"source_type": "all_active"}],
    "stages": [
      {"name": "crawl", "type": "crawler", "config": {"mode": "incremental"}},
      {"name": "normalize", "type": "normalizer", "config": {"strip_boilerplate": true, "extract_headings": true}},
      {"name": "chunk", "type": "chunker", "config": {"strategy": "heading_aware", "max_tokens": 512, "overlap": 50}},
      {"name": "embed", "type": "embedder", "config": {"model": "text-embedding-3-small", "batch_size": 100}},
      {"name": "extract_entities", "type": "entity_extractor", "config": {"types": ["module", "model", "feature"]}},
      {"name": "build_links", "type": "link_builder", "config": {"check_broken": true}},
      {"name": "publish", "type": "publisher", "config": {"update_search_index": true}}
    ],
    "schedule": "0 2 * * *",
    "triggers": ["schedule", "manual", "source_update"]
  }
}

-- Capability Mapping Pipeline
{
  "pipeline_key": "capability_mapping",
  "name": "SAP → Odoo/OCA Capability Mapping",
  "pipeline_type": "capability_mapping",
  "definition": {
    "sources": [{"source_framework": "sap_concur"}, {"source_framework": "sap_srm"}],
    "stages": [
      {"name": "extract_features", "type": "feature_extractor", "config": {}},
      {"name": "match_modules", "type": "module_matcher", "config": {"threshold": 0.7}},
      {"name": "verify_parity", "type": "parity_verifier", "config": {}},
      {"name": "publish_map", "type": "map_publisher", "config": {}}
    ],
    "triggers": ["manual"]
  }
}';

COMMIT;
