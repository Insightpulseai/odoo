-- ============================================================================
-- Migration: Semantic Query Layer for AI Monthly Revenue Insights
-- Date: 2025-11-28
-- Description: Adds vector similarity search capabilities for natural language
--              querying of monthly revenue insights
-- ============================================================================

-- EXTENSIONS: Ensure vector extension is available
CREATE EXTENSION IF NOT EXISTS "vector";

-- SCHEMAS: Ensure AI schema exists
CREATE SCHEMA IF NOT EXISTS ai;

-- ============================================================================
-- CORE TABLE: ai.monthly_revenue_insights
-- Stores revenue data with embeddings for semantic search
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai.monthly_revenue_insights (
  id               bigserial PRIMARY KEY,
  company_id       bigint       NOT NULL,
  month            date         NOT NULL,
  revenue          numeric      NOT NULL,
  summary          text,
  embedding        vector(1536),
  last_embedded_at timestamptz,
  created_at       timestamptz  DEFAULT now(),
  updated_at       timestamptz  DEFAULT now(),
  UNIQUE (company_id, month)
);

-- INDEX: Vector similarity search using IVFFlat
-- Lists=100 is optimal for datasets up to ~1M rows
CREATE INDEX IF NOT EXISTS idx_ai_mri_embedding
ON ai.monthly_revenue_insights
USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);

-- INDEX: Fast lookups by company_id
CREATE INDEX IF NOT EXISTS idx_ai_mri_company_id
ON ai.monthly_revenue_insights(company_id);

-- INDEX: Fast lookups by month
CREATE INDEX IF NOT EXISTS idx_ai_mri_month
ON ai.monthly_revenue_insights(month);

-- ============================================================================
-- FUNCTION: ai.backfill_monthly_revenue_insights
-- Syncs data from gold layer to AI table (without embeddings)
-- ============================================================================
CREATE OR REPLACE FUNCTION ai.backfill_monthly_revenue_insights()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO ai.monthly_revenue_insights (company_id, month, revenue)
  SELECT
    g.company_id,
    g.month,
    g.revenue
  FROM odoo_gold.monthly_revenue AS g
  ON CONFLICT (company_id, month)
  DO UPDATE SET
    revenue    = EXCLUDED.revenue,
    updated_at = now();
END;
$$;

-- ============================================================================
-- FUNCTION: ai.search_monthly_revenue_insights
-- Semantic similarity search for monthly revenue insights
-- Uses L2 distance (Euclidean) for vector comparison
-- ============================================================================
CREATE OR REPLACE FUNCTION ai.search_monthly_revenue_insights (
  p_company_id          bigint,
  p_query_embedding     vector(1536),
  p_match_count         integer DEFAULT 10,
  p_max_distance        double precision DEFAULT 1.5
)
RETURNS TABLE (
  id                    bigint,
  company_id            bigint,
  month                 date,
  revenue               numeric,
  summary               text,
  distance              double precision
)
LANGUAGE sql
STABLE
AS $$
  SELECT
    m.id,
    m.company_id,
    m.month,
    m.revenue,
    m.summary,
    (m.embedding <-> p_query_embedding) AS distance
  FROM ai.monthly_revenue_insights AS m
  WHERE m.company_id = p_company_id
    AND m.embedding IS NOT NULL
    AND (m.embedding <-> p_query_embedding) <= p_max_distance
  ORDER BY m.embedding <-> p_query_embedding
  LIMIT p_match_count;
$$;

-- ============================================================================
-- FUNCTION: ai.search_monthly_revenue_insights_all_companies
-- Cross-company semantic search (for admin/service role use)
-- ============================================================================
CREATE OR REPLACE FUNCTION ai.search_monthly_revenue_insights_all_companies (
  p_query_embedding     vector(1536),
  p_match_count         integer DEFAULT 10,
  p_max_distance        double precision DEFAULT 1.5
)
RETURNS TABLE (
  id                    bigint,
  company_id            bigint,
  month                 date,
  revenue               numeric,
  summary               text,
  distance              double precision
)
LANGUAGE sql
STABLE
AS $$
  SELECT
    m.id,
    m.company_id,
    m.month,
    m.revenue,
    m.summary,
    (m.embedding <-> p_query_embedding) AS distance
  FROM ai.monthly_revenue_insights AS m
  WHERE m.embedding IS NOT NULL
    AND (m.embedding <-> p_query_embedding) <= p_max_distance
  ORDER BY m.embedding <-> p_query_embedding
  LIMIT p_match_count;
$$;

-- ============================================================================
-- RLS: Row Level Security Policies
-- ============================================================================
ALTER TABLE ai.monthly_revenue_insights ENABLE ROW LEVEL SECURITY;

-- Policy: Authenticated users can only SELECT their own company's data
CREATE POLICY "ai_insights_select_by_company"
ON ai.monthly_revenue_insights
FOR SELECT
TO authenticated
USING (company_id::text = auth.jwt()->> 'company_id');

-- Policy: Service role has full access (for Edge Functions / MCP workers)
CREATE POLICY "ai_insights_service_rw"
ON ai.monthly_revenue_insights
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- ============================================================================
-- CRON: Schedule daily sync of metric data into AI table
-- Runs at 03:00 UTC daily
-- ============================================================================
DO $$
BEGIN
  -- Check if pg_cron extension exists before scheduling
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
    PERFORM cron.schedule(
      'sync_ai_monthly_revenue_insights',
      '0 3 * * *',
      $cron$ SELECT ai.backfill_monthly_revenue_insights(); $cron$
    );
  END IF;
EXCEPTION
  WHEN undefined_function THEN
    RAISE NOTICE 'pg_cron not available, skipping cron schedule';
END;
$$;

-- ============================================================================
-- COMMENTS: Documentation for the semantic query layer
-- ============================================================================
COMMENT ON TABLE ai.monthly_revenue_insights IS
  'Stores monthly revenue data with AI-generated summaries and embeddings for semantic search';

COMMENT ON COLUMN ai.monthly_revenue_insights.embedding IS
  'OpenAI text-embedding-3-small vector (1536 dimensions)';

COMMENT ON COLUMN ai.monthly_revenue_insights.summary IS
  'AI-generated plain-English summary of the monthly revenue data';

COMMENT ON FUNCTION ai.search_monthly_revenue_insights IS
  'Semantic similarity search for monthly revenue insights by company. Uses L2 distance.';

COMMENT ON FUNCTION ai.backfill_monthly_revenue_insights IS
  'Syncs data from odoo_gold.monthly_revenue to ai.monthly_revenue_insights';
