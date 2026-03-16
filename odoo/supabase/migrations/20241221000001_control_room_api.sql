-- Control Room API Schema
-- Databricks-style job orchestration and lineage tracking
-- Version: 1.0.0

-- Ensure runtime schema exists (may already exist from master_control)
CREATE SCHEMA IF NOT EXISTS runtime;

-- ============================================================================
-- Jobs Table
-- Stores job definitions submitted via API
-- ============================================================================

CREATE TABLE IF NOT EXISTS runtime.cr_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    job_type TEXT NOT NULL CHECK (job_type IN ('spark_etl', 'diagram_export', 'schema_migration', 'kb_catalog', 'code_validation')),
    spec JSONB NOT NULL DEFAULT '{}'::jsonb,
    code JSONB,
    repo JSONB,
    callbacks JSONB,
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE runtime.cr_jobs IS 'Control Room job definitions - stores specs, code, and callback config';
COMMENT ON COLUMN runtime.cr_jobs.job_type IS 'Type of job: spark_etl, diagram_export, schema_migration, kb_catalog, code_validation';
COMMENT ON COLUMN runtime.cr_jobs.spec IS 'Natural language spec with text and inputs';
COMMENT ON COLUMN runtime.cr_jobs.code IS 'Generated code files array';
COMMENT ON COLUMN runtime.cr_jobs.callbacks IS 'Webhook callbacks: on_complete, on_fail, on_progress';

-- ============================================================================
-- Runs Table
-- Tracks individual job executions
-- ============================================================================

CREATE TABLE IF NOT EXISTS runtime.cr_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES runtime.cr_jobs(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    result JSONB,
    logs_url TEXT,
    executor TEXT,  -- k8s_job, do_runner, local
    executor_ref TEXT,  -- Reference to external executor (job ID, droplet ID, etc.)
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE runtime.cr_runs IS 'Control Room job runs - tracks execution status and results';
COMMENT ON COLUMN runtime.cr_runs.status IS 'Run status: queued, running, completed, failed, cancelled';
COMMENT ON COLUMN runtime.cr_runs.result IS 'Execution result including output and errors';
COMMENT ON COLUMN runtime.cr_runs.executor IS 'Execution backend: k8s_job, do_runner, local';

-- ============================================================================
-- Artifacts Table
-- Stores references to job outputs
-- ============================================================================

CREATE TABLE IF NOT EXISTS runtime.cr_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runtime.cr_runs(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    path TEXT NOT NULL,
    content_type TEXT DEFAULT 'application/octet-stream',
    size_bytes BIGINT DEFAULT 0,
    storage_url TEXT NOT NULL,
    checksum TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE runtime.cr_artifacts IS 'Control Room artifacts - job outputs stored in external storage';
COMMENT ON COLUMN runtime.cr_artifacts.path IS 'Logical path of artifact (e.g., output/result.csv)';
COMMENT ON COLUMN runtime.cr_artifacts.storage_url IS 'URL to artifact in storage (S3, Supabase Storage, etc.)';

-- ============================================================================
-- Lineage Edges Table
-- Tracks data flow relationships between entities
-- ============================================================================

CREATE TABLE IF NOT EXISTS runtime.cr_lineage_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    source_entity TEXT NOT NULL,  -- schema.table or uri
    target_entity TEXT NOT NULL,  -- schema.table or uri
    job_id UUID REFERENCES runtime.cr_jobs(id) ON DELETE SET NULL,
    run_id UUID REFERENCES runtime.cr_runs(id) ON DELETE SET NULL,
    edge_type TEXT NOT NULL DEFAULT 'data_flow' CHECK (edge_type IN ('data_flow', 'transformation', 'dependency')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ  -- Soft delete for lineage preservation
);

COMMENT ON TABLE runtime.cr_lineage_edges IS 'Control Room lineage graph - tracks data flow between entities';
COMMENT ON COLUMN runtime.cr_lineage_edges.source_entity IS 'Source entity (schema.table, file://path, supabase://schema.table)';
COMMENT ON COLUMN runtime.cr_lineage_edges.target_entity IS 'Target entity (schema.table, file://path, supabase://schema.table)';
COMMENT ON COLUMN runtime.cr_lineage_edges.edge_type IS 'Relationship type: data_flow, transformation, dependency';
COMMENT ON COLUMN runtime.cr_lineage_edges.deleted_at IS 'Soft delete timestamp (lineage is append-only)';

-- ============================================================================
-- Run Events Table
-- Stores streaming events during job execution
-- ============================================================================

CREATE TABLE IF NOT EXISTS runtime.cr_run_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runtime.cr_runs(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('log', 'progress', 'artifact', 'status', 'metric')),
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE runtime.cr_run_events IS 'Control Room run events - streaming logs and progress updates';

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Jobs indexes
CREATE INDEX IF NOT EXISTS idx_cr_jobs_tenant_id ON runtime.cr_jobs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cr_jobs_job_type ON runtime.cr_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_cr_jobs_created_at ON runtime.cr_jobs(created_at DESC);

-- Runs indexes
CREATE INDEX IF NOT EXISTS idx_cr_runs_job_id ON runtime.cr_runs(job_id);
CREATE INDEX IF NOT EXISTS idx_cr_runs_tenant_id ON runtime.cr_runs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cr_runs_status ON runtime.cr_runs(status);
CREATE INDEX IF NOT EXISTS idx_cr_runs_created_at ON runtime.cr_runs(created_at DESC);

-- Artifacts indexes
CREATE INDEX IF NOT EXISTS idx_cr_artifacts_run_id ON runtime.cr_artifacts(run_id);
CREATE INDEX IF NOT EXISTS idx_cr_artifacts_tenant_id ON runtime.cr_artifacts(tenant_id);

-- Lineage indexes (critical for graph queries)
CREATE INDEX IF NOT EXISTS idx_cr_lineage_source ON runtime.cr_lineage_edges(source_entity);
CREATE INDEX IF NOT EXISTS idx_cr_lineage_target ON runtime.cr_lineage_edges(target_entity);
CREATE INDEX IF NOT EXISTS idx_cr_lineage_tenant_id ON runtime.cr_lineage_edges(tenant_id);
CREATE INDEX IF NOT EXISTS idx_cr_lineage_not_deleted ON runtime.cr_lineage_edges(source_entity, target_entity) WHERE deleted_at IS NULL;

-- Run events indexes
CREATE INDEX IF NOT EXISTS idx_cr_run_events_run_id ON runtime.cr_run_events(run_id);
CREATE INDEX IF NOT EXISTS idx_cr_run_events_created_at ON runtime.cr_run_events(created_at DESC);

-- ============================================================================
-- Updated At Trigger
-- ============================================================================

CREATE OR REPLACE FUNCTION runtime.cr_jobs_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS cr_jobs_updated_at ON runtime.cr_jobs;
CREATE TRIGGER cr_jobs_updated_at
    BEFORE UPDATE ON runtime.cr_jobs
    FOR EACH ROW
    EXECUTE FUNCTION runtime.cr_jobs_update_timestamp();

-- ============================================================================
-- RPC Functions
-- ============================================================================

-- Get lineage graph with depth traversal
CREATE OR REPLACE FUNCTION runtime.get_lineage_graph(
    p_entity TEXT,
    p_direction TEXT DEFAULT 'both',  -- 'upstream', 'downstream', 'both'
    p_depth INT DEFAULT 2,
    p_tenant_id UUID DEFAULT NULL
)
RETURNS TABLE (
    entity TEXT,
    relation TEXT,  -- 'upstream' or 'downstream'
    distance INT,
    job_id UUID,
    edge_type TEXT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE lineage AS (
        -- Base case: direct connections
        SELECT
            CASE
                WHEN le.target_entity = p_entity THEN le.source_entity
                ELSE le.target_entity
            END AS entity,
            CASE
                WHEN le.target_entity = p_entity THEN 'upstream'
                ELSE 'downstream'
            END AS relation,
            1 AS distance,
            le.job_id,
            le.edge_type,
            le.created_at
        FROM runtime.cr_lineage_edges le
        WHERE le.deleted_at IS NULL
          AND (le.source_entity = p_entity OR le.target_entity = p_entity)
          AND (p_tenant_id IS NULL OR le.tenant_id = p_tenant_id)
          AND (p_direction = 'both'
               OR (p_direction = 'upstream' AND le.target_entity = p_entity)
               OR (p_direction = 'downstream' AND le.source_entity = p_entity))

        UNION ALL

        -- Recursive case: traverse graph
        SELECT
            CASE
                WHEN l.relation = 'upstream' THEN le.source_entity
                ELSE le.target_entity
            END AS entity,
            l.relation,
            l.distance + 1 AS distance,
            le.job_id,
            le.edge_type,
            le.created_at
        FROM lineage l
        JOIN runtime.cr_lineage_edges le ON (
            (l.relation = 'upstream' AND le.target_entity = l.entity)
            OR (l.relation = 'downstream' AND le.source_entity = l.entity)
        )
        WHERE l.distance < p_depth
          AND le.deleted_at IS NULL
          AND (p_tenant_id IS NULL OR le.tenant_id = p_tenant_id)
    )
    SELECT DISTINCT ON (lineage.entity, lineage.relation)
        lineage.entity,
        lineage.relation,
        lineage.distance,
        lineage.job_id,
        lineage.edge_type,
        lineage.created_at
    FROM lineage
    ORDER BY lineage.entity, lineage.relation, lineage.distance;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION runtime.get_lineage_graph IS 'Traverse lineage graph from an entity with configurable depth and direction';

-- Get run statistics
CREATE OR REPLACE FUNCTION runtime.get_cr_run_stats(
    p_tenant_id UUID DEFAULT NULL,
    p_days INT DEFAULT 7
)
RETURNS TABLE (
    job_type TEXT,
    total_runs BIGINT,
    completed_runs BIGINT,
    failed_runs BIGINT,
    avg_duration_seconds NUMERIC,
    success_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        j.job_type,
        COUNT(r.id) AS total_runs,
        COUNT(r.id) FILTER (WHERE r.status = 'completed') AS completed_runs,
        COUNT(r.id) FILTER (WHERE r.status = 'failed') AS failed_runs,
        AVG(EXTRACT(EPOCH FROM (r.completed_at - r.started_at))) FILTER (WHERE r.completed_at IS NOT NULL AND r.started_at IS NOT NULL) AS avg_duration_seconds,
        CASE
            WHEN COUNT(r.id) FILTER (WHERE r.status IN ('completed', 'failed')) > 0
            THEN ROUND(COUNT(r.id) FILTER (WHERE r.status = 'completed')::NUMERIC / COUNT(r.id) FILTER (WHERE r.status IN ('completed', 'failed'))::NUMERIC * 100, 2)
            ELSE 0
        END AS success_rate
    FROM runtime.cr_runs r
    JOIN runtime.cr_jobs j ON r.job_id = j.id
    WHERE r.created_at >= now() - (p_days || ' days')::INTERVAL
      AND (p_tenant_id IS NULL OR r.tenant_id = p_tenant_id)
    GROUP BY j.job_type;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION runtime.get_cr_run_stats IS 'Get run statistics grouped by job type';
