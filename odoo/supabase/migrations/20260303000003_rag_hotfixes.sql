-- Migration: RAG post-deploy hotfixes
-- Applied: 2026-03-03 (post-merge of PR #506)
--
-- Fixes discovered during first production upsert:
-- 1. trigger used 'simple' stemmer → changed to 'english'
-- 2. fts_search/hybrid_search_rrf referenced wrong column (fts_content → tsv)
-- 3. btree index on section_path exceeded row size limit → hash index
-- 4. public wrapper functions needed for PostgREST exposure

-- Fix 1: Replace trigger function to use English stemmer (was 'simple')
CREATE OR REPLACE FUNCTION rag.chunks_tsv_update()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.tsv := to_tsvector('pg_catalog.english', coalesce(NEW.content, ''));
  RETURN NEW;
END;
$$;

-- Fix 2: Replace btree index with hash index (btree max row 2704 bytes exceeded)
DROP INDEX IF EXISTS rag.idx_chunks_section_path;
CREATE INDEX IF NOT EXISTS idx_chunks_section_path ON rag.chunks USING hash (section_path);

-- Fix 3: Recreate fts_search with correct column name (tsv, not fts_content)
CREATE OR REPLACE FUNCTION rag.fts_search(
  p_query      text,
  p_top_k      int DEFAULT 10,
  p_corpus_id  text DEFAULT NULL,
  p_tenant_id  uuid DEFAULT NULL
)
RETURNS TABLE(
  chunk_id     uuid,
  document_id  uuid,
  corpus_id    text,
  section_path text,
  content      text,
  repo_path    text,
  ts_score     float4
)
LANGUAGE sql STABLE AS $$
  SELECT
    c.id          AS chunk_id,
    c.document_id,
    c.corpus_id,
    c.section_path,
    c.content,
    d.repo_path,
    ts_rank_cd(c.tsv, websearch_to_tsquery('english', p_query)) AS ts_score
  FROM rag.chunks c
  JOIN rag.documents d ON d.id = c.document_id
  WHERE c.tsv @@ websearch_to_tsquery('english', p_query)
    AND (p_corpus_id IS NULL OR c.corpus_id = p_corpus_id)
    AND (p_tenant_id IS NULL OR c.tenant_id = p_tenant_id)
  ORDER BY ts_score DESC
  LIMIT p_top_k;
$$;

-- Fix 4: Recreate hybrid_search_rrf with correct column name
CREATE OR REPLACE FUNCTION rag.hybrid_search_rrf(
  p_query_text      text,
  p_query_embedding vector(1536) DEFAULT NULL,
  p_top_k           int          DEFAULT 10,
  p_rrf_k           int          DEFAULT 60,
  p_corpus_id       text         DEFAULT NULL,
  p_tenant_id       uuid         DEFAULT NULL
)
RETURNS TABLE(
  chunk_id     uuid,
  document_id  uuid,
  corpus_id    text,
  section_path text,
  content      text,
  repo_path    text,
  rrf_score    float4,
  vec_rank     int,
  fts_rank     int
)
LANGUAGE sql STABLE AS $$
  WITH fts AS (
    SELECT c.id AS chunk_id,
           ts_rank_cd(c.tsv, websearch_to_tsquery('english', p_query_text)) AS score,
           ROW_NUMBER() OVER (ORDER BY ts_rank_cd(c.tsv, websearch_to_tsquery('english', p_query_text)) DESC) AS rn
    FROM rag.chunks c
    WHERE c.tsv @@ websearch_to_tsquery('english', p_query_text)
      AND (p_corpus_id IS NULL OR c.corpus_id = p_corpus_id)
      AND (p_tenant_id IS NULL OR c.tenant_id = p_tenant_id)
    LIMIT p_top_k * 3
  ),
  vec AS (
    SELECT c.id AS chunk_id,
           1 - (c.embedding <=> p_query_embedding) AS score,
           ROW_NUMBER() OVER (ORDER BY c.embedding <=> p_query_embedding) AS rn
    FROM rag.chunks c
    WHERE p_query_embedding IS NOT NULL
      AND c.embedding IS NOT NULL
      AND (p_corpus_id IS NULL OR c.corpus_id = p_corpus_id)
      AND (p_tenant_id IS NULL OR c.tenant_id = p_tenant_id)
    ORDER BY c.embedding <=> p_query_embedding
    LIMIT p_top_k * 3
  ),
  combined AS (
    SELECT COALESCE(f.chunk_id, v.chunk_id) AS chunk_id,
           (COALESCE(1.0 / (p_rrf_k + f.rn), 0) +
            COALESCE(1.0 / (p_rrf_k + v.rn), 0))::float4 AS rrf_score,
           v.rn::int AS vec_rank,
           f.rn::int AS fts_rank
    FROM fts f
    FULL OUTER JOIN vec v ON f.chunk_id = v.chunk_id
  )
  SELECT cm.chunk_id,
         c.document_id,
         c.corpus_id,
         c.section_path,
         c.content,
         d.repo_path,
         cm.rrf_score,
         cm.vec_rank,
         cm.fts_rank
  FROM combined cm
  JOIN rag.chunks    c ON c.id = cm.chunk_id
  JOIN rag.documents d ON d.id = c.document_id
  ORDER BY cm.rrf_score DESC
  LIMIT p_top_k;
$$;

-- Fix 5: Public wrapper functions for PostgREST exposure
CREATE OR REPLACE FUNCTION public.fts_search(
  p_query      text,
  p_top_k      int DEFAULT 10,
  p_corpus_id  text DEFAULT NULL,
  p_tenant_id  uuid DEFAULT NULL
)
RETURNS TABLE(
  chunk_id     uuid,
  document_id  uuid,
  corpus_id    text,
  section_path text,
  content      text,
  repo_path    text,
  ts_score     float4
)
LANGUAGE sql STABLE SECURITY DEFINER AS $$
  SELECT * FROM rag.fts_search(p_query, p_top_k, p_corpus_id, p_tenant_id);
$$;

CREATE OR REPLACE FUNCTION public.hybrid_search_rrf(
  p_query_text      text,
  p_query_embedding vector(1536) DEFAULT NULL,
  p_top_k           int          DEFAULT 10,
  p_rrf_k           int          DEFAULT 60,
  p_corpus_id       text         DEFAULT NULL,
  p_tenant_id       uuid         DEFAULT NULL
)
RETURNS TABLE(
  chunk_id     uuid,
  document_id  uuid,
  corpus_id    text,
  section_path text,
  content      text,
  repo_path    text,
  rrf_score    float4,
  vec_rank     int,
  fts_rank     int
)
LANGUAGE sql STABLE SECURITY DEFINER AS $$
  SELECT * FROM rag.hybrid_search_rrf(p_query_text, p_query_embedding, p_top_k, p_rrf_k, p_corpus_id, p_tenant_id);
$$;

-- Grant execute to service_role and anon
GRANT EXECUTE ON FUNCTION public.fts_search TO service_role, anon;
GRANT EXECUTE ON FUNCTION public.hybrid_search_rrf TO service_role, anon;
GRANT EXECUTE ON FUNCTION rag.fts_search TO service_role, anon;
GRANT EXECUTE ON FUNCTION rag.hybrid_search_rrf TO service_role, anon;
