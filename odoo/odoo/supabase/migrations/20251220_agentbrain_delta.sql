-- =============================================================================
-- AGENTBRAIN DELTA: Docs KB + Parity Mapper + Module Factory
-- =============================================================================
-- Purpose: Versioned document storage + capability mapping + declarative pipelines
-- Created: 2025-12-20
-- Compatible with: 20251220085409_kapa_docs_copilot_hybrid_search.sql
-- =============================================================================

-- Extensions (ensure enabled)
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Schemas
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS runtime;
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS authz;
CREATE SCHEMA IF NOT EXISTS dev;

-- =============================================================================
-- RAG LAYER: Document Versions + Pages + Links
-- =============================================================================

-- Document Versions: Immutable snapshots (one per content_hash)
CREATE TABLE IF NOT EXISTS rag.document_versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    document_id uuid NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,
    version_at timestamptz NOT NULL DEFAULT now(),

    -- Normalized content
    content_md text NOT NULL,
    content_text text,
    content_hash text NOT NULL,

    -- Metadata
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

    -- Search indexing
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english'::regconfig, COALESCE(content_text, ''))
    ) STORED,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_doc_versions_doc
    ON rag.document_versions (tenant_id, document_id, version_at DESC);
CREATE INDEX IF NOT EXISTS ix_doc_versions_search
    ON rag.document_versions USING GIN(search_vector);
CREATE UNIQUE INDEX IF NOT EXISTS ux_doc_versions_hash
    ON rag.document_versions (tenant_id, document_id, content_hash);

-- Pages: HTTP metadata (status, etag, last-modified)
CREATE TABLE IF NOT EXISTS rag.pages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    document_id uuid NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,

    canonical_url text NOT NULL,
    resolved_url text,
    http_status int,
    etag text,
    last_modified text,

    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_rag_pages_url
    ON rag.pages (tenant_id, canonical_url);

-- Page Links: Link graph (for "related docs" + broken link detection)
CREATE TABLE IF NOT EXISTS rag.page_links (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    from_document_id uuid NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,
    from_anchor_text text,

    to_url text NOT NULL,
    to_document_id uuid REFERENCES rag.documents(id) ON DELETE SET NULL,

    link_type text DEFAULT 'internal',

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_page_links_from
    ON rag.page_links (tenant_id, from_document_id);
CREATE INDEX IF NOT EXISTS ix_page_links_to
    ON rag.page_links (tenant_id, to_document_id);

-- =============================================================================
-- AUTHZ: Document Access Control
-- =============================================================================

CREATE TABLE IF NOT EXISTS authz.document_acl (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    document_id uuid NOT NULL REFERENCES rag.documents(id) ON DELETE CASCADE,

    visibility text NOT NULL DEFAULT 'tenant',
    role text,
    user_id uuid,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT valid_visibility CHECK (
        visibility IN ('public', 'tenant', 'role', 'user')
    ),
    CONSTRAINT role_or_user CHECK (
        (visibility = 'role' AND role IS NOT NULL) OR
        (visibility = 'user' AND user_id IS NOT NULL) OR
        (visibility IN ('public', 'tenant'))
    )
);

CREATE INDEX IF NOT EXISTS ix_doc_acl_doc ON authz.document_acl (tenant_id, document_id);
CREATE INDEX IF NOT EXISTS ix_doc_acl_role
    ON authz.document_acl (tenant_id, role)
    WHERE visibility = 'role';

-- =============================================================================
-- GOLD LAYER: Capability Maps + Parity Packs
-- =============================================================================

-- Capability Map: SAP → Odoo/OCA contracts
CREATE TABLE IF NOT EXISTS gold.capability_map (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    source_framework text NOT NULL,
    capability_key text NOT NULL,

    title text NOT NULL,
    description text,

    -- Target modules (JSON array)
    target_modules jsonb NOT NULL DEFAULT '[]'::jsonb,

    config_notes text,

    -- Back-references to docs
    docs_refs jsonb NOT NULL DEFAULT '[]'::jsonb,

    -- Status tracking
    status text DEFAULT 'draft',

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_cap_map_key
    ON gold.capability_map (tenant_id, source_framework, capability_key);
CREATE INDEX IF NOT EXISTS ix_cap_map_status
    ON gold.capability_map (tenant_id, status);

-- Parity Packs: Filtered document + capability sets
CREATE TABLE IF NOT EXISTS gold.parity_packs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    key text NOT NULL,
    kind text NOT NULL,

    title text,
    description text,

    -- Content references
    documents jsonb NOT NULL DEFAULT '[]'::jsonb,
    capabilities jsonb NOT NULL DEFAULT '[]'::jsonb,

    -- Metadata
    spec jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_parity_packs_key
    ON gold.parity_packs (tenant_id, key);

-- =============================================================================
-- RUNTIME: Declarative Pipelines
-- =============================================================================

-- Pipeline Definitions
CREATE TABLE IF NOT EXISTS runtime.pipeline_defs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    key text NOT NULL,
    name text NOT NULL,
    description text,

    enabled boolean NOT NULL DEFAULT true,

    -- Full YAML spec
    spec_yaml text NOT NULL,

    -- Schedule (cron)
    schedule_cron text,

    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_pipeline_defs_key
    ON runtime.pipeline_defs (tenant_id, key);

-- Pipeline Runs: Execution history
CREATE TABLE IF NOT EXISTS runtime.pipeline_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    pipeline_def_id uuid NOT NULL REFERENCES runtime.pipeline_defs(id) ON DELETE CASCADE,

    status text NOT NULL DEFAULT 'queued',

    trigger text NOT NULL DEFAULT 'manual',

    started_at timestamptz,
    ended_at timestamptz,

    -- Summary metrics
    summary jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_pipeline_runs_def
    ON runtime.pipeline_runs (tenant_id, pipeline_def_id, created_at DESC);
CREATE INDEX IF NOT EXISTS ix_pipeline_runs_status
    ON runtime.pipeline_runs (tenant_id, status);

-- Pipeline Run Steps: DAG execution
CREATE TABLE IF NOT EXISTS runtime.pipeline_run_steps (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    pipeline_run_id uuid NOT NULL REFERENCES runtime.pipeline_runs(id) ON DELETE CASCADE,

    step_key text NOT NULL,
    step_index int NOT NULL,

    status text NOT NULL DEFAULT 'queued',

    started_at timestamptz,
    ended_at timestamptz,
    duration_ms int,

    -- Metrics + errors
    metrics jsonb NOT NULL DEFAULT '{}'::jsonb,

    error text,
    error_code text,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_run_steps_run
    ON runtime.pipeline_run_steps (tenant_id, pipeline_run_id, step_index);
CREATE INDEX IF NOT EXISTS ix_run_steps_status
    ON runtime.pipeline_run_steps (tenant_id, status);

-- Error Codes: Taxonomy
CREATE TABLE IF NOT EXISTS runtime.error_codes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    code text NOT NULL UNIQUE,

    title text NOT NULL,
    description text,

    -- Remediation path
    remediation jsonb NOT NULL DEFAULT '{}'::jsonb,

    edge_cases jsonb NOT NULL DEFAULT '[]'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now()
);

-- Audit Log
CREATE TABLE IF NOT EXISTS runtime.audit_log (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    action text NOT NULL,

    resource_type text,
    resource_id uuid,

    details jsonb NOT NULL DEFAULT '{}'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_audit_log_resource
    ON runtime.audit_log (tenant_id, resource_type, resource_id, created_at DESC);

-- =============================================================================
-- DEV: Feature Requests + Module Runs (Module Factory)
-- =============================================================================

CREATE TABLE IF NOT EXISTS dev.feature_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,

    feature_key text NOT NULL,
    source text NOT NULL,
    source_url text,

    payload jsonb NOT NULL,

    status text NOT NULL DEFAULT 'queued',

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_feature_requests_key
    ON dev.feature_requests (tenant_id, feature_key);

-- Module Runs: Stages of module development automation
CREATE TABLE IF NOT EXISTS dev.module_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    feature_request_id uuid NOT NULL REFERENCES dev.feature_requests(id) ON DELETE CASCADE,

    stage text NOT NULL,
    ok boolean NOT NULL DEFAULT false,

    logs text,

    artifact_refs jsonb NOT NULL DEFAULT '[]'::jsonb,

    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_module_runs_request
    ON dev.module_runs (tenant_id, feature_request_id, stage);

-- =============================================================================
-- SEED: Error Codes Taxonomy
-- =============================================================================

INSERT INTO runtime.error_codes (code, title, description, remediation, edge_cases)
VALUES
(
    'CRAWL_TIMEOUT',
    'Crawler timeout on URL',
    'n8n crawler exceeded max_timeout_sec (30s) on a URL',
    '{
        "automatic_retry": true,
        "backoff_ms": 2000,
        "max_retries": 3,
        "recovery_actions": [
            "Increase timeout_sec in pipeline spec",
            "Check target URL availability (HTTP status)",
            "Review crawler logs for stalled requests"
        ]
    }'::jsonb,
    '[
        {
            "condition": "URL returns 500 or 503",
            "behavior": "Crawler retries with exponential backoff",
            "workaround": "Add URL to blocklist, skip with respect_robots=false"
        },
        {
            "condition": "Large file (PDF > 10MB)",
            "behavior": "Timeout on PDF extraction phase",
            "workaround": "Increase max_content_size_mb in crawler config"
        }
    ]'::jsonb
),
(
    'PARSE_FAILURE',
    'HTML/Markdown parsing failed',
    'Boilerplate stripper or HTML→MD converter failed on content',
    '{
        "automatic_retry": false,
        "backoff_ms": 0,
        "max_retries": 0,
        "recovery_actions": [
            "Check HTML structure (malformed tags)",
            "Review headings_aware=true flag",
            "Add URL to manual_review_queue",
            "Check converter logs for specific CSS selectors"
        ]
    }'::jsonb,
    '[
        {
            "condition": "Page uses frames or JavaScript-rendered content",
            "behavior": "Parser fails to extract text (render_js=false)",
            "workaround": "Set render_js=true in crawler, add Playwright overhead"
        },
        {
            "condition": "Content encoded in non-UTF8",
            "behavior": "Character encoding error during normalization",
            "workaround": "Detect charset from HTTP headers, transcode before parsing"
        }
    ]'::jsonb
),
(
    'RATE_LIMIT',
    'Rate limit exceeded on source (429)',
    'n8n crawler hit rate limit on help.sap.com or other source',
    '{
        "automatic_retry": true,
        "backoff_ms": 5000,
        "max_retries": 5,
        "recovery_actions": [
            "Decrease rate_limit_rps in pipeline spec (2 → 1)",
            "Add jitter to request spacing (random 0-500ms)",
            "Request whitelisting from source (submit ticket)",
            "Add user-agent header to appear as browser"
        ]
    }'::jsonb,
    '[
        {
            "condition": "SAP Help portal blocks crawler user-agent",
            "behavior": "All requests return 403 Forbidden",
            "workaround": "Use residential proxy OR request crawl permission from SAP"
        },
        {
            "condition": "CDN (CloudFlare) returns 429 after 100 requests",
            "behavior": "Exponential backoff exceeds pipeline timeout",
            "workaround": "Schedule crawls during off-peak hours, split by domain partition"
        }
    ]'::jsonb
),
(
    'CHUNK_TOKENIZE_FAILURE',
    'Token counting failed on chunk',
    'OpenAI tokenizer or custom tokenizer raised exception',
    '{
        "automatic_retry": false,
        "backoff_ms": 0,
        "max_retries": 0,
        "recovery_actions": [
            "Check chunk content for special characters / encodings",
            "Use fallback tokenizer (word_count * 1.33)",
            "Split chunk by newlines instead of by tokens",
            "Log problematic chunk for manual review"
        ]
    }'::jsonb,
    '[
        {
            "condition": "Chunk contains emoji or rare Unicode",
            "behavior": "Tokenizer raises UnicodeDecodeError",
            "workaround": "Normalize Unicode before chunking, use precomposed forms"
        }
    ]'::jsonb
),
(
    'EMBED_API_FAILURE',
    'OpenAI embedding API error',
    'Rate limit, auth error, or service unavailable from OpenAI',
    '{
        "automatic_retry": true,
        "backoff_ms": 1000,
        "max_retries": 3,
        "recovery_actions": [
            "Check OpenAI API key and rate limits",
            "Switch to local embedder (Ollama) as fallback",
            "Queue chunks for retry in dedicated embedding queue",
            "Monitor OpenAI status page"
        ]
    }'::jsonb,
    '[
        {
            "condition": "API key invalid or expired",
            "behavior": "401 Unauthorized on every request",
            "workaround": "Rotate key in vault, redeploy n8n worker"
        },
        {
            "condition": "Rate limit (quota exhausted)",
            "behavior": "429 Too Many Requests, exponential retry",
            "workaround": "Use batch API, wait for quota reset, use cheaper model (3-small)"
        }
    ]'::jsonb
),
(
    'KG_EXTRACTION_EMPTY',
    'Knowledge graph extraction returned no entities',
    'LLM failed to extract entities/relationships from chunk',
    '{
        "automatic_retry": false,
        "backoff_ms": 0,
        "max_retries": 0,
        "recovery_actions": [
            "Check chunk length (too short?)",
            "Try different LLM model (Claude vs GPT-4)",
            "Lower entity confidence threshold",
            "Review chunk for low-quality content (nav, footer)"
        ]
    }'::jsonb,
    '[
        {
            "condition": "Chunk is from website footer (boilerplate not stripped)",
            "behavior": "No valid entities extracted (just links, copyright)",
            "workaround": "Improve boilerplate stripping regex, mark chunk as low-quality"
        }
    ]'::jsonb
),
(
    'DEDUP_CONFLICT',
    'Document deduplication conflict',
    'Same content_hash found for different canonical_url',
    '{
        "automatic_retry": false,
        "backoff_ms": 0,
        "max_retries": 0,
        "recovery_actions": [
            "Check for URL redirects (resolve final URL)",
            "Verify canonical_url normalization",
            "Mark one as canonical, other as alias"
        ]
    }'::jsonb,
    '[
        {
            "condition": "Multiple URLs point to same content (e.g., /docs/ vs /docs/index.html)",
            "behavior": "First URL wins, subsequent are skipped",
            "workaround": "Use URL normalization before hashing"
        }
    ]'::jsonb
),
(
    'ACL_VIOLATION',
    'Document access control violation',
    'User attempted to access document without proper permissions',
    '{
        "automatic_retry": false,
        "backoff_ms": 0,
        "max_retries": 0,
        "recovery_actions": [
            "Check user role vs document visibility",
            "Verify tenant_id matches",
            "Log access attempt for audit"
        ]
    }'::jsonb,
    '[
        {
            "condition": "User from tenant A tries to access tenant B docs",
            "behavior": "403 Forbidden, document not found in results",
            "workaround": "Ensure tenant_id filter in all queries"
        }
    ]'::jsonb
)
ON CONFLICT (code) DO NOTHING;

-- =============================================================================
-- SEED: Sample Capability Maps (SAP Concur → Odoo)
-- =============================================================================

-- Get or create a default tenant for seeding
DO $$
DECLARE
    v_tenant_id uuid;
BEGIN
    -- Try to get existing tenant from core.tenants
    SELECT id INTO v_tenant_id FROM core.tenants LIMIT 1;

    IF v_tenant_id IS NULL THEN
        -- Skip seeding if no tenant exists
        RAISE NOTICE 'No tenant found, skipping capability map seeding';
        RETURN;
    END IF;

    -- Seed capability maps
    INSERT INTO gold.capability_map (
        tenant_id, source_framework, capability_key, title, description,
        target_modules, config_notes, status
    ) VALUES
    (
        v_tenant_id,
        'sap_concur',
        'expense.capture.receipts',
        'Expense Capture + Receipt Processing',
        'Employee photo capture of receipts, OCR extraction, data validation',
        '[
            {
                "odoo_module": "hr_expense",
                "oca_repo": "OCA/hr-expense",
                "oca_module": null,
                "gap_severity": "critical",
                "config": {"ocr_provider": "external_api"},
                "workaround": "Third-party OCR integration required"
            }
        ]'::jsonb,
        'OCR processing happens outside Odoo. Push structured expense lines via JSON-RPC.',
        'mapped'
    ),
    (
        v_tenant_id,
        'sap_concur',
        'expense.approval.workflow',
        'Expense Approval Workflow',
        'Multi-tier approval with configurable rules based on amount, category, policy',
        '[
            {
                "odoo_module": "hr_expense",
                "oca_repo": "OCA/hr-expense",
                "oca_module": "hr_expense_tier_validation",
                "gap_severity": "minor",
                "config": {"approval_tiers": 2},
                "workaround": null
            }
        ]'::jsonb,
        'OCA hr_expense_tier_validation provides multi-tier approval. Configure tiers in Odoo settings.',
        'mapped'
    ),
    (
        v_tenant_id,
        'sap_concur',
        'expense.policy.rules',
        'Expense Policy Rule Engine',
        'Define and enforce expense policies with complex conditions',
        '[
            {
                "odoo_module": "hr_expense",
                "oca_repo": null,
                "oca_module": null,
                "gap_severity": "critical",
                "config": {},
                "workaround": "Custom ipai_expense_policy module required"
            }
        ]'::jsonb,
        'No OCA equivalent. Requires GAP_DELTA module ipai_expense_policy.',
        'draft'
    ),
    (
        v_tenant_id,
        'sap_concur',
        'expense.reimbursement',
        'Expense Reimbursement',
        'Process employee expense reimbursements via payroll or direct payment',
        '[
            {
                "odoo_module": "hr_expense",
                "oca_repo": "OCA/account-payment",
                "oca_module": "account_payment_order",
                "gap_severity": "minor",
                "config": {},
                "workaround": null
            }
        ]'::jsonb,
        'Standard hr_expense + OCA payment order modules cover this.',
        'mapped'
    ),
    (
        v_tenant_id,
        'sap_srm',
        'procurement.requisition',
        'Purchase Requisition',
        'Employee-initiated purchase requests with approval workflow',
        '[
            {
                "odoo_module": "purchase",
                "oca_repo": "OCA/purchase-workflow",
                "oca_module": "purchase_request",
                "gap_severity": "closed",
                "config": {},
                "workaround": null
            }
        ]'::jsonb,
        'OCA purchase_request covers this fully.',
        'implemented'
    ),
    (
        v_tenant_id,
        'sap_srm',
        'vendor.management',
        'Vendor Management',
        'Vendor onboarding, qualification, and performance tracking',
        '[
            {
                "odoo_module": "purchase",
                "oca_repo": "OCA/partner-contact",
                "oca_module": "partner_contact_birthdate",
                "gap_severity": "moderate",
                "config": {},
                "workaround": "Partial coverage. Advanced vendor scoring requires custom module."
            }
        ]'::jsonb,
        'Basic vendor data in res.partner. Advanced vendor scorecards need GAP_DELTA.',
        'draft'
    )
    ON CONFLICT (tenant_id, source_framework, capability_key) DO NOTHING;

    RAISE NOTICE 'Seeded % capability maps', 6;
END;
$$;

-- =============================================================================
-- VIEWS: API Surface
-- =============================================================================

-- View: Latest document versions + ACL-aware
CREATE OR REPLACE VIEW rag.v_documents_latest AS
SELECT DISTINCT ON (d.id)
    d.id,
    d.tenant_id,
    d.source_type,
    d.source_url,
    d.title,
    dv.id AS version_id,
    dv.version_at,
    dv.content_md,
    dv.content_text,
    dv.content_hash
FROM rag.documents d
LEFT JOIN rag.document_versions dv ON d.id = dv.document_id
ORDER BY d.id, dv.version_at DESC;

-- View: Chunks with parent document + version
CREATE OR REPLACE VIEW rag.v_chunks_searchable AS
SELECT
    c.id AS chunk_id,
    c.tenant_id,
    c.document_id,
    d.source_url,
    d.title AS document_title,
    c.section_path,
    c.content,
    c.embedding,
    c.embedding_model
FROM rag.chunks c
JOIN rag.documents d ON c.document_id = d.id;

-- =============================================================================
-- RPC: Capability Map Search
-- =============================================================================

CREATE OR REPLACE FUNCTION gold.search_capabilities(
    p_tenant_id uuid,
    p_framework text DEFAULT NULL,
    p_query text DEFAULT NULL,
    p_status text DEFAULT NULL,
    p_limit int DEFAULT 20
)
RETURNS TABLE (
    id uuid,
    source_framework text,
    capability_key text,
    title text,
    description text,
    target_modules jsonb,
    config_notes text,
    status text,
    docs_refs jsonb
)
LANGUAGE sql STABLE
AS $func$
SELECT
    cm.id,
    cm.source_framework,
    cm.capability_key,
    cm.title,
    cm.description,
    cm.target_modules,
    cm.config_notes,
    cm.status,
    cm.docs_refs
FROM gold.capability_map cm
WHERE cm.tenant_id = p_tenant_id
  AND (p_framework IS NULL OR cm.source_framework = p_framework)
  AND (p_status IS NULL OR cm.status = p_status)
  AND (p_query IS NULL OR
       cm.title ILIKE '%' || p_query || '%' OR
       cm.description ILIKE '%' || p_query || '%' OR
       cm.capability_key ILIKE '%' || p_query || '%')
ORDER BY cm.source_framework, cm.capability_key
LIMIT p_limit;
$func$;

COMMENT ON FUNCTION gold.search_capabilities IS
'Search capability maps by framework, query text, or status';

-- =============================================================================
-- RPC: Error Code Lookup
-- =============================================================================

CREATE OR REPLACE FUNCTION runtime.lookup_error_code(
    p_pattern text
)
RETURNS TABLE (
    code text,
    title text,
    description text,
    remediation jsonb,
    edge_cases jsonb
)
LANGUAGE sql STABLE
AS $func$
SELECT
    ec.code,
    ec.title,
    ec.description,
    ec.remediation,
    ec.edge_cases
FROM runtime.error_codes ec
WHERE ec.code ILIKE '%' || p_pattern || '%'
   OR ec.title ILIKE '%' || p_pattern || '%'
ORDER BY ec.code
LIMIT 10;
$func$;

COMMENT ON FUNCTION runtime.lookup_error_code IS
'Lookup error codes by code pattern or title substring';

-- =============================================================================
-- VERIFICATION
-- =============================================================================

DO $verify$
DECLARE
    missing_tables text[];
BEGIN
    SELECT array_agg(tbl) INTO missing_tables
    FROM (VALUES
        ('rag.document_versions'),
        ('rag.pages'),
        ('rag.page_links'),
        ('authz.document_acl'),
        ('gold.capability_map'),
        ('gold.parity_packs'),
        ('runtime.pipeline_defs'),
        ('runtime.pipeline_runs'),
        ('runtime.pipeline_run_steps'),
        ('runtime.error_codes'),
        ('runtime.audit_log'),
        ('dev.feature_requests'),
        ('dev.module_runs')
    ) AS required(tbl)
    WHERE NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema || '.' || table_name = required.tbl
    );

    IF array_length(missing_tables, 1) > 0 THEN
        RAISE WARNING 'Missing tables: %', missing_tables;
    ELSE
        RAISE NOTICE 'All AgentBrain delta tables verified ✓';
    END IF;
END;
$verify$;

-- Count seeded data
DO $$
DECLARE
    error_count int;
    cap_count int;
BEGIN
    SELECT COUNT(*) INTO error_count FROM runtime.error_codes;
    SELECT COUNT(*) INTO cap_count FROM gold.capability_map;

    RAISE NOTICE 'Seeded: % error codes, % capability maps', error_count, cap_count;
END;
$$;
