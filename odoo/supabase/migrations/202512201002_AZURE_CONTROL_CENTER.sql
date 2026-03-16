-- =============================================================================
-- Azure Control Center — InsightPulse Control Plane
-- =============================================================================
-- Version: 1.0.0
-- PRD Reference: Azure Control Center (InsightPulse Control Plane)
--
-- Implements:
--   * control schema - policies, routing, connectors, budgets
--   * runtime schema - sessions, retrievals, feedback, evidence
--   * acl system - document-level access control
--   * embedding model registry
--   * skill registry with versioning and execution tracking
--
-- Pattern: "Define once, enforce everywhere" governance
-- =============================================================================

BEGIN;

-- =============================================================================
-- SCHEMAS
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS control;
CREATE SCHEMA IF NOT EXISTS runtime;
-- Note: rag schema already exists from previous migrations

COMMENT ON SCHEMA control IS 'Control plane: policies, routing, connectors, budgets';
COMMENT ON SCHEMA runtime IS 'Runtime: sessions, retrievals, feedback, evidence packets';

-- =============================================================================
-- 1. EMBEDDING MODEL REGISTRY
-- =============================================================================
-- Required to track which embedding model created each vector

CREATE TABLE IF NOT EXISTS rag.embedding_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE, -- e.g., 'text-embedding-3-small', 'bge-m3'
    name TEXT NOT NULL,
    provider TEXT NOT NULL, -- openai, cohere, local, huggingface
    dimensions INT NOT NULL, -- 1536, 768, 1024, etc.
    version TEXT,
    max_tokens INT,

    -- Model properties
    properties JSONB DEFAULT '{}'::jsonb,
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE rag.embedding_models IS 'Registry of embedding models with dimension tracking';

-- Seed default embedding models
INSERT INTO rag.embedding_models (key, name, provider, dimensions, version, is_default) VALUES
    ('text-embedding-3-small', 'OpenAI Text Embedding 3 Small', 'openai', 1536, '3', true),
    ('text-embedding-3-large', 'OpenAI Text Embedding 3 Large', 'openai', 3072, '3', false),
    ('text-embedding-ada-002', 'OpenAI Ada 002 (Legacy)', 'openai', 1536, '002', false),
    ('bge-m3', 'BGE-M3 Multilingual', 'huggingface', 1024, '1.0', false),
    ('nomic-embed-text', 'Nomic Embed Text', 'nomic', 768, '1.5', false)
ON CONFLICT (key) DO NOTHING;

-- Add embedding_model_key to chunks if not exists
ALTER TABLE rag.chunks
    ADD COLUMN IF NOT EXISTS embedding_model_key TEXT REFERENCES rag.embedding_models(key);

-- =============================================================================
-- 2. CONTROL.ROUTING_POLICIES — Model Routing & Budgets
-- =============================================================================

CREATE TABLE IF NOT EXISTS control.routing_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- Policy identity
    policy_key TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,

    -- Provider chain (ordered fallback)
    provider_chain JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example: [
    --   {"provider": "local", "model": "llama3.2", "priority": 1},
    --   {"provider": "ollama", "model": "mistral", "priority": 2},
    --   {"provider": "openai", "model": "gpt-4o-mini", "priority": 3, "fallback_only": true}
    -- ]

    -- Budgets
    budgets JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Example: {
    --   "max_tokens_per_day": 1000000,
    --   "max_tokens_per_request": 8000,
    --   "max_tool_calls_per_run": 10,
    --   "p95_latency_target_ms": 3000,
    --   "cost_cap_usd_per_day": 50.00
    -- }

    -- Allowlists/Denylists
    provider_allowlist TEXT[],
    provider_denylist TEXT[],
    tool_allowlist TEXT[],
    tool_denylist TEXT[],
    source_allowlist TEXT[], -- Which connectors/sources are usable

    -- Redaction rules for logs/artifacts
    redaction_rules JSONB DEFAULT '[]'::jsonb,
    -- Example: [
    --   {"pattern": "\\b[A-Z]{2}\\d{9}\\b", "type": "tin", "action": "mask"},
    --   {"pattern": "\\b\\d{16}\\b", "type": "credit_card", "action": "redact"}
    -- ]

    -- Retention policies
    retention_days JSONB DEFAULT '{}'::jsonb,
    -- Example: {"events": 90, "memory": 365, "raw_ingests": 30}

    -- Version tracking for audit
    version INT DEFAULT 1,
    version_hash TEXT, -- SHA256 of policy content

    -- Status
    is_active BOOLEAN DEFAULT true,
    priority INT DEFAULT 100, -- Higher = evaluated first

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID,

    UNIQUE (tenant_id, policy_key)
);

CREATE INDEX idx_routing_policies_tenant ON control.routing_policies(tenant_id);
CREATE INDEX idx_routing_policies_active ON control.routing_policies(tenant_id, is_active, priority DESC);

-- Enable RLS
ALTER TABLE control.routing_policies ENABLE ROW LEVEL SECURITY;

CREATE POLICY routing_policies_tenant_isolation ON control.routing_policies
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE control.routing_policies IS 'Model routing policies with provider chains, budgets, and allowlists';

-- =============================================================================
-- 3. CONTROL.CONNECTORS — Data Source Connectors
-- =============================================================================

CREATE TABLE IF NOT EXISTS control.connectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- Connector identity
    connector_type TEXT NOT NULL CHECK (connector_type IN (
        'github', 'gitlab', 'notion', 'confluence', 'web',
        'odoo_api', 'sap_help', 'gdrive', 'sharepoint', 'file_drop',
        's3', 'gcs', 'azure_blob'
    )),
    name TEXT NOT NULL,
    description TEXT,

    -- Configuration (non-secret)
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Examples:
    -- GitHub: {"owner": "org", "repo": "docs", "branch": "main", "path_filter": "docs/**"}
    -- Web: {"base_url": "https://help.sap.com/", "include_patterns": ["**/concur/**"]}
    -- Notion: {"workspace_id": "...", "database_ids": [...]}

    -- Secrets reference (not stored in DB)
    secrets_ref TEXT, -- e.g., "vault:connectors/github/org-docs" or env var name

    -- Crawl configuration
    crawl_config JSONB DEFAULT '{}'::jsonb,
    -- Example: {
    --   "schedule": "0 2 * * *",
    --   "incremental": true,
    --   "max_depth": 5,
    --   "rate_limit_rpm": 60,
    --   "retry_attempts": 3,
    --   "retry_backoff_seconds": [10, 30, 60]
    -- }

    -- Chunking configuration
    chunk_config JSONB DEFAULT '{}'::jsonb,
    -- Example: {
    --   "strategy": "semantic", -- heading, token_size, semantic
    --   "max_chunk_tokens": 512,
    --   "overlap_tokens": 50,
    --   "split_on_headings": true
    -- }

    -- Embedding configuration
    embedding_model_key TEXT REFERENCES rag.embedding_models(key),

    -- Status
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'active', 'paused', 'failed', 'disabled'
    )),

    -- Stats
    last_crawl_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    last_error TEXT,
    document_count INT DEFAULT 0,
    chunk_count INT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID,

    UNIQUE (tenant_id, name)
);

CREATE INDEX idx_connectors_tenant ON control.connectors(tenant_id);
CREATE INDEX idx_connectors_status ON control.connectors(status) WHERE status IN ('active', 'pending');
CREATE INDEX idx_connectors_type ON control.connectors(connector_type);

-- Enable RLS
ALTER TABLE control.connectors ENABLE ROW LEVEL SECURITY;

CREATE POLICY connectors_tenant_isolation ON control.connectors
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE control.connectors IS 'Data source connectors with crawl and chunk configurations';

-- =============================================================================
-- 4. CONTROL.CONNECTOR_CURSORS — Incremental Crawl State
-- =============================================================================

CREATE TABLE IF NOT EXISTS control.connector_cursors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES control.connectors(id) ON DELETE CASCADE,

    -- Cursor identity (for multi-resource connectors)
    resource_key TEXT NOT NULL DEFAULT 'default', -- e.g., 'repo:main', 'db:123'

    -- Cursor state
    cursor_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Examples:
    -- GitHub: {"last_commit_sha": "abc123", "etag": "..."}
    -- Notion: {"last_edited_time": "2025-12-20T00:00:00Z"}
    -- Web: {"last_modified": "...", "visited_urls": [...]}

    -- Status
    last_run_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    last_error TEXT,
    consecutive_failures INT DEFAULT 0,

    -- Metrics
    items_processed INT DEFAULT 0,
    items_created INT DEFAULT 0,
    items_updated INT DEFAULT 0,
    items_deleted INT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (connector_id, resource_key)
);

CREATE INDEX idx_connector_cursors_connector ON control.connector_cursors(connector_id);

COMMENT ON TABLE control.connector_cursors IS 'Incremental crawl cursor state for connectors';

-- =============================================================================
-- 5. CONTROL.CONNECTOR_RUNS — Crawl Job History
-- =============================================================================

CREATE TABLE IF NOT EXISTS control.connector_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID NOT NULL REFERENCES control.connectors(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Run metadata
    run_type TEXT NOT NULL DEFAULT 'incremental' CHECK (run_type IN (
        'full', 'incremental', 'reembed', 'rechunk'
    )),
    triggered_by TEXT, -- 'schedule', 'manual', 'webhook'
    triggered_by_user UUID,

    -- Status
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'cancelled'
    )),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Metrics
    documents_fetched INT DEFAULT 0,
    documents_created INT DEFAULT 0,
    documents_updated INT DEFAULT 0,
    documents_deleted INT DEFAULT 0,
    chunks_created INT DEFAULT 0,
    embeddings_created INT DEFAULT 0,

    -- Errors
    error_count INT DEFAULT 0,
    errors JSONB DEFAULT '[]'::jsonb,

    -- Performance
    duration_seconds DECIMAL(10,2),

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_connector_runs_connector ON control.connector_runs(connector_id, created_at DESC);
CREATE INDEX idx_connector_runs_status ON control.connector_runs(status) WHERE status IN ('pending', 'running');

-- Enable RLS
ALTER TABLE control.connector_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY connector_runs_tenant_isolation ON control.connector_runs
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE control.connector_runs IS 'Connector crawl job execution history';

-- =============================================================================
-- 6. RAG.DOCUMENT_ACLS — Document Access Control
-- =============================================================================

CREATE TABLE IF NOT EXISTS rag.document_acls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,

    -- Principal (who gets access)
    principal_type TEXT NOT NULL CHECK (principal_type IN ('role', 'user', 'team', 'service')),
    principal_id UUID NOT NULL, -- References roles.id, users.id, teams.id, or principals.id

    -- Permission
    permission TEXT NOT NULL DEFAULT 'read' CHECK (permission IN ('read', 'write', 'admin')),
    allow BOOLEAN NOT NULL DEFAULT true, -- true = allow, false = deny (deny wins)

    -- Scope (optional - for section-level ACLs later)
    section_path TEXT, -- e.g., "chapter1/section2"

    -- Metadata
    granted_by UUID,
    granted_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ,
    reason TEXT,

    created_at TIMESTAMPTZ DEFAULT now(),

    -- Unique constraint per document-principal-permission combo
    UNIQUE (tenant_id, document_id, principal_type, principal_id, permission)
);

CREATE INDEX idx_document_acls_document ON rag.document_acls(document_id);
CREATE INDEX idx_document_acls_principal ON rag.document_acls(principal_type, principal_id);
CREATE INDEX idx_document_acls_tenant ON rag.document_acls(tenant_id);

-- Enable RLS
ALTER TABLE rag.document_acls ENABLE ROW LEVEL SECURITY;

CREATE POLICY document_acls_tenant_isolation ON rag.document_acls
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE rag.document_acls IS 'Document-level access control with role/user/team principals';

-- =============================================================================
-- 7. CONTROL.SKILLS — Skill Registry
-- =============================================================================

CREATE TABLE IF NOT EXISTS control.skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES core.tenants(id), -- NULL = global skill

    -- Skill identity
    skill_key TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT, -- 'finance', 'hr', 'ops', 'data', etc.

    -- Ownership
    owner_id UUID,
    owner_type TEXT, -- 'user', 'team', 'system'

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT false, -- Visible to all tenants?

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE NULLS NOT DISTINCT (tenant_id, skill_key)
);

CREATE INDEX idx_skills_tenant ON control.skills(tenant_id);
CREATE INDEX idx_skills_category ON control.skills(category);
CREATE INDEX idx_skills_active ON control.skills(is_active) WHERE is_active = true;

COMMENT ON TABLE control.skills IS 'Skill registry with ownership and categorization';

-- =============================================================================
-- 8. CONTROL.SKILL_VERSIONS — Versioned Skill Definitions
-- =============================================================================

CREATE TABLE IF NOT EXISTS control.skill_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES control.skills(id) ON DELETE CASCADE,

    -- Version
    version TEXT NOT NULL, -- semver: "1.0.0", "1.1.0"
    version_number INT NOT NULL, -- Auto-incrementing for ordering

    -- Schema
    input_schema JSONB NOT NULL, -- JSON Schema for inputs
    output_schema JSONB, -- JSON Schema for outputs

    -- Implementation
    implementation_type TEXT NOT NULL CHECK (implementation_type IN (
        'function', 'workflow', 'agent', 'api_call', 'script'
    )),
    implementation_ref TEXT, -- Function name, workflow ID, API endpoint, etc.

    -- Configuration
    config JSONB DEFAULT '{}'::jsonb,
    timeout_seconds INT DEFAULT 60,
    retry_config JSONB,

    -- Status
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN (
        'draft', 'published', 'deprecated', 'archived'
    )),
    published_at TIMESTAMPTZ,
    deprecated_at TIMESTAMPTZ,

    -- Changelog
    changelog TEXT,

    created_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID,

    UNIQUE (skill_id, version)
);

CREATE INDEX idx_skill_versions_skill ON control.skill_versions(skill_id, version_number DESC);
CREATE INDEX idx_skill_versions_status ON control.skill_versions(status);

COMMENT ON TABLE control.skill_versions IS 'Versioned skill definitions with input/output schemas';

-- =============================================================================
-- 9. CONTROL.SKILL_PERMISSIONS — Who Can Execute Skills
-- =============================================================================

CREATE TABLE IF NOT EXISTS control.skill_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES control.skills(id) ON DELETE CASCADE,

    -- Principal
    principal_type TEXT NOT NULL CHECK (principal_type IN ('role', 'user', 'team', 'service')),
    principal_id UUID NOT NULL,

    -- Permission scope
    permission TEXT NOT NULL DEFAULT 'execute' CHECK (permission IN (
        'execute', 'view', 'edit', 'admin'
    )),

    -- Constraints
    max_executions_per_day INT,
    allowed_versions TEXT[], -- NULL = all versions

    granted_by UUID,
    granted_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ,

    UNIQUE (skill_id, principal_type, principal_id, permission)
);

CREATE INDEX idx_skill_permissions_skill ON control.skill_permissions(skill_id);
CREATE INDEX idx_skill_permissions_principal ON control.skill_permissions(principal_type, principal_id);

COMMENT ON TABLE control.skill_permissions IS 'RBAC permissions for skill execution';

-- =============================================================================
-- 10. RUNTIME.SESSIONS — Search/Chat Sessions
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- User context
    user_id UUID,
    anonymous_id TEXT, -- For unauthenticated users

    -- Channel
    channel TEXT NOT NULL CHECK (channel IN (
        'docs_portal', 'ide', 'api', 'chat', 'slack', 'mattermost', 'n8n'
    )),

    -- Session metadata
    started_at TIMESTAMPTZ DEFAULT now(),
    ended_at TIMESTAMPTZ,

    -- Context
    context JSONB DEFAULT '{}'::jsonb,
    -- Example: {"workspace": "...", "file": "...", "project": "..."}

    -- Stats
    query_count INT DEFAULT 0,
    retrieval_count INT DEFAULT 0,
    tool_call_count INT DEFAULT 0,

    -- Routing policy used
    routing_policy_id UUID REFERENCES control.routing_policies(id),
    routing_policy_version INT,

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_sessions_tenant ON runtime.sessions(tenant_id, started_at DESC);
CREATE INDEX idx_sessions_user ON runtime.sessions(user_id, started_at DESC);
CREATE INDEX idx_sessions_channel ON runtime.sessions(channel);

-- Enable RLS
ALTER TABLE runtime.sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY sessions_tenant_isolation ON runtime.sessions
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.sessions IS 'User search/chat sessions across channels';

-- =============================================================================
-- 11. RUNTIME.QUERIES — Individual Queries Within Sessions
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES runtime.sessions(id) ON DELETE CASCADE,

    -- Query
    query_text TEXT NOT NULL,
    query_embedding vector(1536),
    embedding_model_key TEXT REFERENCES rag.embedding_models(key),

    -- Response
    response_text TEXT,
    response_model TEXT, -- Which model generated response
    response_provider TEXT,

    -- Timing
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    latency_ms INT,

    -- Token usage
    prompt_tokens INT,
    completion_tokens INT,
    total_tokens INT,

    -- Cost (if available from provider)
    cost_usd DECIMAL(10,6),

    -- Quality signals
    confidence_score DECIMAL(5,4),
    citations_count INT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_queries_session ON runtime.queries(session_id, created_at);
CREATE INDEX idx_queries_tenant ON runtime.queries(tenant_id, created_at DESC);

-- Enable RLS
ALTER TABLE runtime.queries ENABLE ROW LEVEL SECURITY;

CREATE POLICY queries_tenant_isolation ON runtime.queries
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.queries IS 'Individual queries within sessions with response tracking';

-- =============================================================================
-- 12. RUNTIME.RETRIEVAL_EVENTS — What Was Retrieved for Each Query
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.retrieval_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    query_id UUID NOT NULL REFERENCES runtime.queries(id) ON DELETE CASCADE,

    -- What was retrieved
    chunk_id UUID REFERENCES rag.chunks(id),
    document_id UUID REFERENCES rag.documents(id),

    -- Relevance
    similarity_score DECIMAL(5,4),
    rank INT, -- Position in results

    -- ACL check result
    acl_allowed BOOLEAN NOT NULL,
    acl_denied_reason TEXT, -- If denied, why

    -- Was it used in the response?
    used_in_response BOOLEAN DEFAULT false,
    cited_in_response BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_retrieval_events_query ON runtime.retrieval_events(query_id);
CREATE INDEX idx_retrieval_events_chunk ON runtime.retrieval_events(chunk_id);
CREATE INDEX idx_retrieval_events_tenant ON runtime.retrieval_events(tenant_id, created_at DESC);

-- Enable RLS
ALTER TABLE runtime.retrieval_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY retrieval_events_tenant_isolation ON runtime.retrieval_events
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.retrieval_events IS 'Retrieval events with ACL check results and usage tracking';

-- =============================================================================
-- 13. RUNTIME.TOOL_CALLS — Tool/Skill Executions
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    query_id UUID REFERENCES runtime.queries(id) ON DELETE CASCADE,
    session_id UUID REFERENCES runtime.sessions(id),

    -- What was called
    tool_type TEXT NOT NULL CHECK (tool_type IN ('skill', 'function', 'api', 'mcp')),
    tool_name TEXT NOT NULL,
    skill_version_id UUID REFERENCES control.skill_versions(id),

    -- Input/Output (may be redacted per policy)
    input_params JSONB,
    output_result JSONB,
    output_redacted BOOLEAN DEFAULT false,

    -- Execution
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'timeout', 'denied'
    )),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INT,

    -- Errors
    error_message TEXT,
    error_code TEXT,

    -- Artifacts
    artifact_urls TEXT[],
    artifact_storage_refs JSONB,

    -- Policy check
    policy_allowed BOOLEAN,
    policy_denied_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_tool_calls_query ON runtime.tool_calls(query_id);
CREATE INDEX idx_tool_calls_session ON runtime.tool_calls(session_id);
CREATE INDEX idx_tool_calls_tenant ON runtime.tool_calls(tenant_id, created_at DESC);
CREATE INDEX idx_tool_calls_tool ON runtime.tool_calls(tool_name);

-- Enable RLS
ALTER TABLE runtime.tool_calls ENABLE ROW LEVEL SECURITY;

CREATE POLICY tool_calls_tenant_isolation ON runtime.tool_calls
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.tool_calls IS 'Tool/skill execution log with inputs, outputs, and artifacts';

-- =============================================================================
-- 14. RUNTIME.FEEDBACK — User Feedback on Responses
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- What the feedback is about
    query_id UUID REFERENCES runtime.queries(id) ON DELETE CASCADE,
    session_id UUID REFERENCES runtime.sessions(id),

    -- Who gave feedback
    user_id UUID,

    -- Rating
    rating INT CHECK (rating BETWEEN -1 AND 1), -- -1 = bad, 0 = neutral, 1 = good

    -- Detailed feedback
    feedback_type TEXT CHECK (feedback_type IN (
        'helpful', 'not_helpful', 'incorrect', 'missing_info',
        'wrong_source', 'outdated', 'other'
    )),
    notes TEXT,

    -- Specific issues
    labels TEXT[], -- ['missing_citation', 'hallucination', 'truncated']

    -- Follow-up
    requires_review BOOLEAN DEFAULT false,
    reviewed_at TIMESTAMPTZ,
    reviewed_by UUID,
    review_notes TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_feedback_query ON runtime.feedback(query_id);
CREATE INDEX idx_feedback_session ON runtime.feedback(session_id);
CREATE INDEX idx_feedback_tenant ON runtime.feedback(tenant_id, created_at DESC);
CREATE INDEX idx_feedback_rating ON runtime.feedback(rating);

-- Enable RLS
ALTER TABLE runtime.feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY feedback_tenant_isolation ON runtime.feedback
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.feedback IS 'User feedback on query responses with review workflow';

-- =============================================================================
-- 15. RUNTIME.EVIDENCE_PACKETS — Exportable Lineage Bundles
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.evidence_packets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- What this evidence is for
    query_id UUID REFERENCES runtime.queries(id),
    session_id UUID REFERENCES runtime.sessions(id),

    -- Packet content
    packet_type TEXT NOT NULL DEFAULT 'query_trace' CHECK (packet_type IN (
        'query_trace', 'session_summary', 'audit_export', 'compliance_report'
    )),

    -- The actual evidence bundle
    evidence JSONB NOT NULL,
    -- Contains: session, query, retrievals, tool_calls, response, feedback

    -- Integrity
    content_hash TEXT NOT NULL, -- SHA256 of evidence JSON

    -- Export metadata
    exported_at TIMESTAMPTZ DEFAULT now(),
    exported_by UUID,
    export_format TEXT DEFAULT 'json', -- json, pdf (future)

    -- Storage
    storage_url TEXT, -- If exported to object storage

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_evidence_packets_query ON runtime.evidence_packets(query_id);
CREATE INDEX idx_evidence_packets_session ON runtime.evidence_packets(session_id);
CREATE INDEX idx_evidence_packets_tenant ON runtime.evidence_packets(tenant_id, created_at DESC);

-- Enable RLS
ALTER TABLE runtime.evidence_packets ENABLE ROW LEVEL SECURITY;

CREATE POLICY evidence_packets_tenant_isolation ON runtime.evidence_packets
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.evidence_packets IS 'Exportable evidence bundles for compliance and audit';

-- =============================================================================
-- 16. CONTROL.BUDGET_USAGE — Track Budget Consumption
-- =============================================================================

CREATE TABLE IF NOT EXISTS control.budget_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    routing_policy_id UUID REFERENCES control.routing_policies(id),

    -- Period
    period_start DATE NOT NULL,
    period_type TEXT NOT NULL DEFAULT 'day' CHECK (period_type IN ('hour', 'day', 'week', 'month')),

    -- Usage
    tokens_used BIGINT DEFAULT 0,
    tool_calls_used INT DEFAULT 0,
    cost_usd DECIMAL(12,6) DEFAULT 0,
    request_count INT DEFAULT 0,

    -- Latency stats
    p50_latency_ms INT,
    p95_latency_ms INT,
    p99_latency_ms INT,

    -- Denials
    budget_denials INT DEFAULT 0,
    policy_denials INT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, routing_policy_id, period_start, period_type)
);

CREATE INDEX idx_budget_usage_tenant ON control.budget_usage(tenant_id, period_start DESC);
CREATE INDEX idx_budget_usage_policy ON control.budget_usage(routing_policy_id);

-- Enable RLS
ALTER TABLE control.budget_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY budget_usage_tenant_isolation ON control.budget_usage
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE control.budget_usage IS 'Budget consumption tracking per period';

-- =============================================================================
-- 17. HELPER FUNCTIONS
-- =============================================================================

-- Check document ACL for a user
CREATE OR REPLACE FUNCTION rag.check_document_access(
    p_tenant_id UUID,
    p_document_id UUID,
    p_user_id UUID,
    p_user_roles UUID[],
    p_permission TEXT DEFAULT 'read'
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
AS $func$
DECLARE
    v_denied BOOLEAN := false;
    v_allowed BOOLEAN := false;
BEGIN
    -- Check for explicit denies first (deny wins)
    SELECT true INTO v_denied
    FROM rag.document_acls
    WHERE tenant_id = p_tenant_id
      AND document_id = p_document_id
      AND permission = p_permission
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
    FROM rag.document_acls
    WHERE tenant_id = p_tenant_id
      AND document_id = p_document_id
      AND permission = p_permission
      AND allow = true
      AND (expires_at IS NULL OR expires_at > now())
      AND (
          (principal_type = 'user' AND principal_id = p_user_id) OR
          (principal_type = 'role' AND principal_id = ANY(p_user_roles))
      )
    LIMIT 1;

    RETURN COALESCE(v_allowed, false);
END;
$func$;

COMMENT ON FUNCTION rag.check_document_access IS 'Check if user has permission to access document (deny wins over allow)';

-- ACL-filtered search function
CREATE OR REPLACE FUNCTION rag.search_with_acl(
    p_tenant_id UUID,
    p_query_embedding vector(1536),
    p_user_id UUID,
    p_user_roles UUID[],
    p_top_k INT DEFAULT 10,
    p_source_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    content TEXT,
    similarity_score FLOAT,
    acl_allowed BOOLEAN,
    source_type TEXT,
    source_url TEXT
)
LANGUAGE plpgsql
STABLE
AS $func$
BEGIN
    RETURN QUERY
    WITH ranked_chunks AS (
        SELECT
            c.id AS chunk_id,
            c.document_id,
            c.content,
            1 - (c.embedding <=> p_query_embedding) AS similarity_score,
            d.source_type,
            d.source_url
        FROM rag.chunks c
        JOIN rag.documents d ON d.id = c.document_id
        WHERE c.tenant_id = p_tenant_id
          AND c.embedding IS NOT NULL
          AND (p_source_type IS NULL OR d.source_type = p_source_type)
        ORDER BY c.embedding <=> p_query_embedding
        LIMIT p_top_k * 2 -- Fetch extra to account for ACL filtering
    )
    SELECT
        rc.chunk_id,
        rc.document_id,
        rc.content,
        rc.similarity_score::FLOAT,
        rag.check_document_access(p_tenant_id, rc.document_id, p_user_id, p_user_roles) AS acl_allowed,
        rc.source_type,
        rc.source_url
    FROM ranked_chunks rc
    ORDER BY rc.similarity_score DESC
    LIMIT p_top_k;
END;
$func$;

COMMENT ON FUNCTION rag.search_with_acl IS 'Vector search with ACL filtering and access status';

-- Generate evidence packet for a query
CREATE OR REPLACE FUNCTION runtime.generate_evidence_packet(
    p_query_id UUID
)
RETURNS UUID
LANGUAGE plpgsql
AS $func$
DECLARE
    v_tenant_id UUID;
    v_evidence JSONB;
    v_hash TEXT;
    v_packet_id UUID;
BEGIN
    -- Get tenant
    SELECT tenant_id INTO v_tenant_id FROM runtime.queries WHERE id = p_query_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Query not found: %', p_query_id;
    END IF;

    -- Build evidence packet
    SELECT jsonb_build_object(
        'query', (
            SELECT jsonb_build_object(
                'id', q.id,
                'text', q.query_text,
                'response', q.response_text,
                'model', q.response_model,
                'tokens', q.total_tokens,
                'latency_ms', q.latency_ms,
                'timestamp', q.created_at
            )
            FROM runtime.queries q WHERE q.id = p_query_id
        ),
        'session', (
            SELECT jsonb_build_object(
                'id', s.id,
                'channel', s.channel,
                'started_at', s.started_at
            )
            FROM runtime.sessions s
            JOIN runtime.queries q ON q.session_id = s.id
            WHERE q.id = p_query_id
        ),
        'retrievals', (
            SELECT jsonb_agg(jsonb_build_object(
                'chunk_id', r.chunk_id,
                'score', r.similarity_score,
                'allowed', r.acl_allowed,
                'used', r.used_in_response,
                'cited', r.cited_in_response
            ))
            FROM runtime.retrieval_events r WHERE r.query_id = p_query_id
        ),
        'tool_calls', (
            SELECT jsonb_agg(jsonb_build_object(
                'tool', t.tool_name,
                'type', t.tool_type,
                'status', t.status,
                'duration_ms', t.duration_ms
            ))
            FROM runtime.tool_calls t WHERE t.query_id = p_query_id
        ),
        'feedback', (
            SELECT jsonb_agg(jsonb_build_object(
                'rating', f.rating,
                'type', f.feedback_type,
                'notes', f.notes
            ))
            FROM runtime.feedback f WHERE f.query_id = p_query_id
        ),
        'generated_at', now()
    ) INTO v_evidence;

    -- Calculate hash
    v_hash := encode(sha256(v_evidence::text::bytea), 'hex');

    -- Insert packet
    INSERT INTO runtime.evidence_packets (
        tenant_id, query_id, packet_type, evidence, content_hash
    ) VALUES (
        v_tenant_id, p_query_id, 'query_trace', v_evidence, v_hash
    ) RETURNING id INTO v_packet_id;

    RETURN v_packet_id;
END;
$func$;

COMMENT ON FUNCTION runtime.generate_evidence_packet IS 'Generate exportable evidence packet for a query';

-- =============================================================================
-- 18. ADD CONNECTOR_ID TO RAG.DOCUMENTS
-- =============================================================================

ALTER TABLE rag.documents
    ADD COLUMN IF NOT EXISTS connector_id UUID REFERENCES control.connectors(id),
    ADD COLUMN IF NOT EXISTS last_crawl_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS crawl_status TEXT DEFAULT 'pending';

CREATE INDEX IF NOT EXISTS idx_documents_connector ON rag.documents(connector_id);

-- =============================================================================
-- 19. VIEWS FOR CONTROL CENTER UI
-- =============================================================================

-- Connector health overview
CREATE OR REPLACE VIEW control.connector_health AS
SELECT
    c.id,
    c.tenant_id,
    c.connector_type,
    c.name,
    c.status,
    c.last_success_at,
    c.last_error,
    c.document_count,
    c.chunk_count,
    COALESCE(cc.consecutive_failures, 0) AS consecutive_failures,
    CASE
        WHEN c.status = 'disabled' THEN 'disabled'
        WHEN c.status = 'failed' OR COALESCE(cc.consecutive_failures, 0) >= 3 THEN 'critical'
        WHEN c.last_success_at < now() - interval '24 hours' THEN 'warning'
        ELSE 'healthy'
    END AS health_status
FROM control.connectors c
LEFT JOIN control.connector_cursors cc ON cc.connector_id = c.id;

COMMENT ON VIEW control.connector_health IS 'Connector health status for monitoring';

-- Session summary with metrics
CREATE OR REPLACE VIEW runtime.session_summary AS
SELECT
    s.id,
    s.tenant_id,
    s.user_id,
    s.channel,
    s.started_at,
    s.ended_at,
    s.query_count,
    s.retrieval_count,
    s.tool_call_count,
    COUNT(DISTINCT q.id) AS actual_query_count,
    AVG(q.latency_ms) AS avg_latency_ms,
    SUM(q.total_tokens) AS total_tokens,
    SUM(q.cost_usd) AS total_cost_usd,
    COUNT(DISTINCT f.id) FILTER (WHERE f.rating = 1) AS positive_feedback,
    COUNT(DISTINCT f.id) FILTER (WHERE f.rating = -1) AS negative_feedback
FROM runtime.sessions s
LEFT JOIN runtime.queries q ON q.session_id = s.id
LEFT JOIN runtime.feedback f ON f.session_id = s.id
GROUP BY s.id;

COMMENT ON VIEW runtime.session_summary IS 'Session summary with aggregated metrics';

-- Daily budget usage
CREATE OR REPLACE VIEW control.daily_budget_summary AS
SELECT
    tenant_id,
    period_start AS date,
    SUM(tokens_used) AS total_tokens,
    SUM(tool_calls_used) AS total_tool_calls,
    SUM(cost_usd) AS total_cost_usd,
    SUM(request_count) AS total_requests,
    AVG(p95_latency_ms) AS avg_p95_latency_ms,
    SUM(budget_denials) AS total_budget_denials,
    SUM(policy_denials) AS total_policy_denials
FROM control.budget_usage
WHERE period_type = 'day'
GROUP BY tenant_id, period_start
ORDER BY period_start DESC;

COMMENT ON VIEW control.daily_budget_summary IS 'Daily budget usage summary per tenant';

COMMIT;
