-- Migration: 20260303000002_rag_hybrid_search_rrf.sql
-- Purpose:   True Reciprocal Rank Fusion (RRF) hybrid search combining pgvector + FTS
--
-- Rationale:
--   The existing rag.search_hybrid uses weighted-average scoring which biases
--   toward whichever channel returns higher absolute scores. RRF normalizes by
--   converting scores to ranks, making the fusion robust to score-scale differences.
--
--   Formula: rrf_score = SUM(1 / (k + rank_in_channel))
--   where k=60 is the standard constant (from Cormack et al., 2009).
--
-- Reference:  Azure rag-postgres-openai-python (hybrid RRF pattern)
-- Contract:   ssot/knowledge/corpus_registry.yaml
-- Depends-on: 20251220085409_kapa_docs_copilot_hybrid_search.sql (base schema)
--             20260303000001_rag_corpus_linkage.sql (corpus_id column)
-- Rollback:   DROP FUNCTION IF EXISTS rag.hybrid_search_rrf;

-- ── Ensure extensions ────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ── RRF Hybrid Search Function ───────────────────────────────────────────────
CREATE OR REPLACE FUNCTION rag.hybrid_search_rrf(
    p_query            TEXT,
    p_query_embedding  vector(1536),
    p_top_k            INT     DEFAULT 10,
    p_rrf_k            INT     DEFAULT 60,
    p_corpus_id        TEXT    DEFAULT NULL,
    p_tenant_id        UUID    DEFAULT NULL
)
RETURNS TABLE (
    chunk_id       UUID,
    document_id    UUID,
    rrf_score      FLOAT,
    content        TEXT,
    repo_path      TEXT,
    corpus_id      TEXT,
    section_path   TEXT,
    canonical_url  TEXT,
    doc_version    TEXT,
    commit_sha     TEXT
)
LANGUAGE sql STABLE
AS $func$
WITH
-- ── Channel 1: Vector similarity (pgvector cosine distance) ──────────────────
vector_ranked AS (
    SELECT
        c.id AS chunk_id,
        c.document_id,
        ROW_NUMBER() OVER (ORDER BY c.embedding <=> p_query_embedding) AS rank_ix
    FROM rag.chunks c
    JOIN rag.documents d ON d.id = c.document_id
    WHERE c.embedding IS NOT NULL
      AND (p_tenant_id IS NULL OR c.tenant_id = p_tenant_id)
      AND (p_corpus_id IS NULL OR d.corpus_id = p_corpus_id)
    ORDER BY c.embedding <=> p_query_embedding
    LIMIT p_top_k * 4
),
-- ── Channel 2: Full-text search (tsvector ranking) ───────────────────────────
fts_ranked AS (
    SELECT
        c.id AS chunk_id,
        c.document_id,
        ROW_NUMBER() OVER (
            ORDER BY ts_rank(c.tsv, plainto_tsquery('simple', p_query)) DESC
        ) AS rank_ix
    FROM rag.chunks c
    JOIN rag.documents d ON d.id = c.document_id
    WHERE c.tsv @@ plainto_tsquery('simple', p_query)
      AND (p_tenant_id IS NULL OR c.tenant_id = p_tenant_id)
      AND (p_corpus_id IS NULL OR d.corpus_id = p_corpus_id)
    ORDER BY ts_rank(c.tsv, plainto_tsquery('simple', p_query)) DESC
    LIMIT p_top_k * 4
),
-- ── Reciprocal Rank Fusion ───────────────────────────────────────────────────
rrf AS (
    SELECT
        COALESCE(v.chunk_id, f.chunk_id) AS chunk_id,
        COALESCE(v.document_id, f.document_id) AS document_id,
        -- RRF formula: sum of 1/(k + rank) across channels
        COALESCE(1.0 / (p_rrf_k + v.rank_ix), 0.0)
      + COALESCE(1.0 / (p_rrf_k + f.rank_ix), 0.0) AS rrf_score
    FROM vector_ranked v
    FULL OUTER JOIN fts_ranked f
        ON v.chunk_id = f.chunk_id AND v.document_id = f.document_id
)
-- ── Final output with metadata ───────────────────────────────────────────────
SELECT
    r.chunk_id,
    r.document_id,
    r.rrf_score,
    c.content,
    d.repo_path,
    d.corpus_id,
    c.section_path,
    d.canonical_url,
    d.doc_version,
    d.commit_sha
FROM rrf r
JOIN rag.chunks c ON c.id = r.chunk_id
JOIN rag.documents d ON d.id = r.document_id
ORDER BY r.rrf_score DESC
LIMIT p_top_k;
$func$;

COMMENT ON FUNCTION rag.hybrid_search_rrf IS
    'Reciprocal Rank Fusion combining pgvector cosine similarity and full-text search. '
    'k=60 normalizes rank contributions. Supports per-corpus and per-tenant filtering. '
    'Reference: Cormack et al. 2009, Azure rag-postgres-openai-python.';

-- ── Convenience: text-only search (no embedding required) ────────────────────
CREATE OR REPLACE FUNCTION rag.fts_search(
    p_query      TEXT,
    p_top_k      INT   DEFAULT 10,
    p_corpus_id  TEXT  DEFAULT NULL,
    p_tenant_id  UUID  DEFAULT NULL
)
RETURNS TABLE (
    chunk_id       UUID,
    document_id    UUID,
    ts_score       FLOAT,
    content        TEXT,
    repo_path      TEXT,
    corpus_id      TEXT,
    section_path   TEXT
)
LANGUAGE sql STABLE
AS $func$
SELECT
    c.id AS chunk_id,
    c.document_id,
    ts_rank(c.tsv, plainto_tsquery('simple', p_query))::FLOAT AS ts_score,
    c.content,
    d.repo_path,
    d.corpus_id,
    c.section_path
FROM rag.chunks c
JOIN rag.documents d ON d.id = c.document_id
WHERE c.tsv @@ plainto_tsquery('simple', p_query)
  AND (p_tenant_id IS NULL OR c.tenant_id = p_tenant_id)
  AND (p_corpus_id IS NULL OR d.corpus_id = p_corpus_id)
ORDER BY ts_rank(c.tsv, plainto_tsquery('simple', p_query)) DESC
LIMIT p_top_k;
$func$;

COMMENT ON FUNCTION rag.fts_search IS
    'Pure full-text search fallback for when no embedding is available. '
    'Useful for smoke tests and text-only queries.';

-- ── Verification ─────────────────────────────────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'rag' AND p.proname = 'hybrid_search_rrf'
    ) THEN
        RAISE EXCEPTION 'Migration 20260303000002: rag.hybrid_search_rrf not found';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'rag' AND p.proname = 'fts_search'
    ) THEN
        RAISE EXCEPTION 'Migration 20260303000002: rag.fts_search not found';
    END IF;
END $$;
