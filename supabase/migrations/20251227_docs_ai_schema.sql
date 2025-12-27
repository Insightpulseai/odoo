-- Migration: InsightPulse Docs AI Schema
-- RAG-based technical documentation AI assistant

-- Enable pgvector (idempotent)
CREATE EXTENSION IF NOT EXISTS "vector";

-- =========================================
-- 1. Core content tables
-- =========================================

CREATE TABLE IF NOT EXISTS public.docs_ai_documents (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID        NOT NULL,
  source      TEXT        NOT NULL,        -- e.g. 'website', 'github', 'notion'
  external_id TEXT        NULL,            -- source-specific id (url, page id, etc.)
  title       TEXT        NOT NULL,
  url         TEXT        NULL,            -- canonical url if available
  body        TEXT        NOT NULL,
  metadata    JSONB       NOT NULL DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS docs_ai_documents_tenant_id_idx
  ON public.docs_ai_documents (tenant_id);

CREATE INDEX IF NOT EXISTS docs_ai_documents_source_idx
  ON public.docs_ai_documents (source);

CREATE INDEX IF NOT EXISTS docs_ai_documents_url_idx
  ON public.docs_ai_documents (url);

COMMENT ON TABLE public.docs_ai_documents IS 'Source documents for Docs AI RAG system';

-- -----------------------------------------

CREATE TABLE IF NOT EXISTS public.docs_ai_document_chunks (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID        NOT NULL,
  document_id  UUID        NOT NULL REFERENCES public.docs_ai_documents(id) ON DELETE CASCADE,
  chunk_index  INTEGER     NOT NULL,                  -- 0-based position in document
  content      TEXT        NOT NULL,
  headings     TEXT[]      NOT NULL DEFAULT '{}',     -- ordered list of headings
  metadata     JSONB       NOT NULL DEFAULT '{}'::jsonb,
  embedding    vector(1536),                          -- adjust dimension for your embedding model
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS docs_ai_document_chunks_tenant_doc_idx
  ON public.docs_ai_document_chunks (tenant_id, document_id, chunk_index);

CREATE INDEX IF NOT EXISTS docs_ai_document_chunks_tenant_idx
  ON public.docs_ai_document_chunks (tenant_id);

-- Vector index (IVFFlat over cosine distance)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM   pg_indexes
    WHERE  schemaname = 'public'
    AND    indexname = 'docs_ai_document_chunks_embedding_idx'
  ) THEN
    CREATE INDEX docs_ai_document_chunks_embedding_idx
      ON public.docs_ai_document_chunks
      USING ivfflat (embedding vector_cosine_ops)
      WITH (lists = 100);
  END IF;
END$$;

COMMENT ON TABLE public.docs_ai_document_chunks IS 'Chunked document content with embeddings for vector search';

-- =========================================
-- 2. Question / answer logging
-- =========================================

CREATE TABLE IF NOT EXISTS public.docs_ai_questions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   UUID        NOT NULL,
  user_id     TEXT        NULL,
  surface     TEXT        NOT NULL,        -- 'docs', 'product', 'support', 'slack', etc.
  question    TEXT        NOT NULL,
  context     JSONB       NOT NULL DEFAULT '{}'::jsonb,  -- route, page url, etc.
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS docs_ai_questions_tenant_surface_idx
  ON public.docs_ai_questions (tenant_id, surface, created_at);

COMMENT ON TABLE public.docs_ai_questions IS 'User questions logged for analytics and improvement';

-- -----------------------------------------

CREATE TABLE IF NOT EXISTS public.docs_ai_answers (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id      UUID        NOT NULL REFERENCES public.docs_ai_questions(id) ON DELETE CASCADE,
  tenant_id        UUID        NOT NULL,
  answer           TEXT        NOT NULL,
  citations        JSONB       NOT NULL DEFAULT '[]'::jsonb,  -- array of {document_id, url, title, score}
  confidence       NUMERIC     NOT NULL DEFAULT 0,
  model            TEXT        NOT NULL,                     -- e.g. 'gpt-4.1-mini', 'claude-3.5-sonnet'
  surface          TEXT        NOT NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  feedback_score   INTEGER     NULL,                         -- -1, 0, +1 or 1–5
  feedback_comment TEXT        NULL
);

CREATE INDEX IF NOT EXISTS docs_ai_answers_question_idx
  ON public.docs_ai_answers (question_id);

CREATE INDEX IF NOT EXISTS docs_ai_answers_tenant_surface_idx
  ON public.docs_ai_answers (tenant_id, surface, created_at);

COMMENT ON TABLE public.docs_ai_answers IS 'AI-generated answers with citations and feedback';

-- =========================================
-- 3. Connector configuration
-- =========================================

CREATE TABLE IF NOT EXISTS public.docs_ai_connectors (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID        NOT NULL,
  name         TEXT        NOT NULL,
  type         TEXT        NOT NULL,  -- 'website', 'github', 'notion', 'confluence', etc.
  config       JSONB       NOT NULL DEFAULT '{}'::jsonb,  -- source-specific config
  enabled      BOOLEAN     NOT NULL DEFAULT TRUE,
  sync_schedule TEXT       NULL,      -- cron expression
  last_sync_at TIMESTAMPTZ NULL,
  last_sync_status TEXT    NULL,      -- 'success', 'failed', 'in_progress'
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS docs_ai_connectors_tenant_idx
  ON public.docs_ai_connectors (tenant_id);

COMMENT ON TABLE public.docs_ai_connectors IS 'Data source connector configurations';

-- =========================================
-- 4. Vector search helper function (RPC)
-- =========================================

CREATE OR REPLACE FUNCTION public.docs_ai_match_chunks(
  match_tenant_id   UUID,
  query_embedding   vector(1536),
  match_count       INTEGER DEFAULT 8,
  max_distance      REAL    DEFAULT 0.4
)
RETURNS TABLE (
  chunk_id     UUID,
  document_id  UUID,
  tenant_id    UUID,
  content      TEXT,
  url          TEXT,
  title        TEXT,
  score        REAL
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    c.id          AS chunk_id,
    c.document_id AS document_id,
    c.tenant_id   AS tenant_id,
    c.content     AS content,
    d.url         AS url,
    d.title       AS title,
    (c.embedding <#> query_embedding) AS score   -- cosine distance
  FROM public.docs_ai_document_chunks c
  JOIN public.docs_ai_documents d
    ON d.id = c.document_id
  WHERE c.tenant_id = match_tenant_id
    AND c.embedding IS NOT NULL
    AND (c.embedding <#> query_embedding) <= max_distance
  ORDER BY c.embedding <#> query_embedding
  LIMIT match_count;
END;
$$;

-- Allow Edge Functions/service-role to call RPC
GRANT EXECUTE ON FUNCTION public.docs_ai_match_chunks(UUID, vector, INTEGER, REAL)
  TO authenticated, service_role, anon;

COMMENT ON FUNCTION public.docs_ai_match_chunks IS 'Vector similarity search for document chunks';

-- =========================================
-- 5. Hybrid search function (vector + keyword)
-- =========================================

CREATE OR REPLACE FUNCTION public.docs_ai_hybrid_search(
  match_tenant_id   UUID,
  query_text        TEXT,
  query_embedding   vector(1536),
  match_count       INTEGER DEFAULT 8,
  vector_weight     REAL DEFAULT 0.7,
  keyword_weight    REAL DEFAULT 0.3
)
RETURNS TABLE (
  chunk_id     UUID,
  document_id  UUID,
  content      TEXT,
  url          TEXT,
  title        TEXT,
  vector_score REAL,
  keyword_score REAL,
  combined_score REAL
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  WITH vector_results AS (
    SELECT
      c.id AS chunk_id,
      c.document_id,
      c.content,
      d.url,
      d.title,
      (1 - (c.embedding <#> query_embedding)) AS v_score  -- convert distance to similarity
    FROM public.docs_ai_document_chunks c
    JOIN public.docs_ai_documents d ON d.id = c.document_id
    WHERE c.tenant_id = match_tenant_id
      AND c.embedding IS NOT NULL
    ORDER BY c.embedding <#> query_embedding
    LIMIT match_count * 2
  ),
  keyword_results AS (
    SELECT
      c.id AS chunk_id,
      c.document_id,
      c.content,
      d.url,
      d.title,
      ts_rank_cd(to_tsvector('english', c.content), plainto_tsquery('english', query_text)) AS k_score
    FROM public.docs_ai_document_chunks c
    JOIN public.docs_ai_documents d ON d.id = c.document_id
    WHERE c.tenant_id = match_tenant_id
      AND to_tsvector('english', c.content) @@ plainto_tsquery('english', query_text)
    LIMIT match_count * 2
  ),
  combined AS (
    SELECT
      COALESCE(v.chunk_id, k.chunk_id) AS chunk_id,
      COALESCE(v.document_id, k.document_id) AS document_id,
      COALESCE(v.content, k.content) AS content,
      COALESCE(v.url, k.url) AS url,
      COALESCE(v.title, k.title) AS title,
      COALESCE(v.v_score, 0) AS vector_score,
      COALESCE(k.k_score, 0) AS keyword_score,
      (COALESCE(v.v_score, 0) * vector_weight + COALESCE(k.k_score, 0) * keyword_weight) AS combined_score
    FROM vector_results v
    FULL OUTER JOIN keyword_results k ON v.chunk_id = k.chunk_id
  )
  SELECT
    combined.chunk_id,
    combined.document_id,
    combined.content,
    combined.url,
    combined.title,
    combined.vector_score,
    combined.keyword_score,
    combined.combined_score
  FROM combined
  ORDER BY combined.combined_score DESC
  LIMIT match_count;
END;
$$;

GRANT EXECUTE ON FUNCTION public.docs_ai_hybrid_search(UUID, TEXT, vector, INTEGER, REAL, REAL)
  TO authenticated, service_role, anon;

COMMENT ON FUNCTION public.docs_ai_hybrid_search IS 'Hybrid search combining vector similarity and keyword matching';

-- =========================================
-- 6. Analytics views
-- =========================================

CREATE OR REPLACE VIEW public.docs_ai_question_stats AS
SELECT
  tenant_id,
  surface,
  DATE_TRUNC('day', created_at) AS day,
  COUNT(*) AS question_count,
  COUNT(DISTINCT user_id) AS unique_users
FROM public.docs_ai_questions
GROUP BY tenant_id, surface, DATE_TRUNC('day', created_at);

CREATE OR REPLACE VIEW public.docs_ai_answer_stats AS
SELECT
  a.tenant_id,
  a.surface,
  DATE_TRUNC('day', a.created_at) AS day,
  COUNT(*) AS answer_count,
  AVG(a.confidence) AS avg_confidence,
  COUNT(CASE WHEN a.feedback_score > 0 THEN 1 END) AS positive_feedback,
  COUNT(CASE WHEN a.feedback_score < 0 THEN 1 END) AS negative_feedback,
  COUNT(CASE WHEN a.feedback_score IS NOT NULL THEN 1 END) AS total_feedback
FROM public.docs_ai_answers a
GROUP BY a.tenant_id, a.surface, DATE_TRUNC('day', a.created_at);

CREATE OR REPLACE VIEW public.docs_ai_low_confidence_questions AS
SELECT
  q.id AS question_id,
  q.tenant_id,
  q.surface,
  q.question,
  q.created_at,
  a.confidence,
  a.answer
FROM public.docs_ai_questions q
JOIN public.docs_ai_answers a ON a.question_id = q.id
WHERE a.confidence < 0.5
ORDER BY q.created_at DESC;

-- =========================================
-- 7. RLS Policies
-- =========================================

ALTER TABLE public.docs_ai_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.docs_ai_document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.docs_ai_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.docs_ai_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.docs_ai_connectors ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role full access" ON public.docs_ai_documents
  FOR ALL TO service_role USING (TRUE);

CREATE POLICY "Service role full access" ON public.docs_ai_document_chunks
  FOR ALL TO service_role USING (TRUE);

CREATE POLICY "Service role full access" ON public.docs_ai_questions
  FOR ALL TO service_role USING (TRUE);

CREATE POLICY "Service role full access" ON public.docs_ai_answers
  FOR ALL TO service_role USING (TRUE);

CREATE POLICY "Service role full access" ON public.docs_ai_connectors
  FOR ALL TO service_role USING (TRUE);

-- =========================================
-- 8. Helper functions
-- =========================================

-- Log a question and return the ID
CREATE OR REPLACE FUNCTION public.docs_ai_log_question(
  p_tenant_id UUID,
  p_user_id TEXT,
  p_surface TEXT,
  p_question TEXT,
  p_context JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
  v_question_id UUID;
BEGIN
  INSERT INTO public.docs_ai_questions (tenant_id, user_id, surface, question, context)
  VALUES (p_tenant_id, p_user_id, p_surface, p_question, p_context)
  RETURNING id INTO v_question_id;

  RETURN v_question_id;
END;
$$;

-- Log an answer
CREATE OR REPLACE FUNCTION public.docs_ai_log_answer(
  p_question_id UUID,
  p_tenant_id UUID,
  p_answer TEXT,
  p_citations JSONB,
  p_confidence NUMERIC,
  p_model TEXT,
  p_surface TEXT
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
  v_answer_id UUID;
BEGIN
  INSERT INTO public.docs_ai_answers (question_id, tenant_id, answer, citations, confidence, model, surface)
  VALUES (p_question_id, p_tenant_id, p_answer, p_citations, p_confidence, p_model, p_surface)
  RETURNING id INTO v_answer_id;

  RETURN v_answer_id;
END;
$$;

-- Submit feedback for an answer
CREATE OR REPLACE FUNCTION public.docs_ai_submit_feedback(
  p_answer_id UUID,
  p_score INTEGER,
  p_comment TEXT DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE public.docs_ai_answers
  SET feedback_score = p_score,
      feedback_comment = p_comment
  WHERE id = p_answer_id;

  RETURN FOUND;
END;
$$;

GRANT EXECUTE ON FUNCTION public.docs_ai_log_question(UUID, TEXT, TEXT, TEXT, JSONB) TO service_role;
GRANT EXECUTE ON FUNCTION public.docs_ai_log_answer(UUID, UUID, TEXT, JSONB, NUMERIC, TEXT, TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION public.docs_ai_submit_feedback(UUID, INTEGER, TEXT) TO service_role, authenticated;
