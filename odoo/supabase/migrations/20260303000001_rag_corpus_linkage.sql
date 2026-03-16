-- Migration: 20260303000001_rag_corpus_linkage.sql
-- Purpose:   Add corpus_id linkage to rag.documents for corpus_registry traceability
--
-- Rationale:
--   The knowledge copilot retrieves from corpora defined in
--   ssot/knowledge/corpus_registry.yaml. Each document ingested into Supabase
--   must be traceable to a specific corpus_id (e.g. "spec_bundles", "ssot_yaml").
--   This enables per-corpus filtering in hybrid search and audit of corpus coverage.
--
-- Contract:  ssot/knowledge/corpus_registry.yaml
-- Backwards-compat: ADD COLUMN IF NOT EXISTS; existing rows get NULL.
-- Rollback:  ALTER TABLE rag.documents DROP COLUMN IF EXISTS corpus_id;
--            ALTER TABLE rag.documents DROP COLUMN IF EXISTS repo_path;
--            DROP INDEX IF EXISTS idx_documents_corpus;
--            DROP INDEX IF EXISTS idx_documents_repo_path;

-- ── Ensure rag schema exists ─────────────────────────────────────────────────
CREATE SCHEMA IF NOT EXISTS rag;

-- ── Add corpus_id column ─────────────────────────────────────────────────────
ALTER TABLE rag.documents
    ADD COLUMN IF NOT EXISTS corpus_id TEXT;

COMMENT ON COLUMN rag.documents.corpus_id IS
    'Identifier from ssot/knowledge/corpus_registry.yaml (e.g. spec_bundles, ssot_yaml, docs_ai). '
    'Used for per-corpus filtering in hybrid search. NULL for legacy rows.';

-- ── Add repo_path for file-level dedup ───────────────────────────────────────
ALTER TABLE rag.documents
    ADD COLUMN IF NOT EXISTS repo_path TEXT;

COMMENT ON COLUMN rag.documents.repo_path IS
    'Repo-relative file path (e.g. spec/ai-copilot/constitution.md). '
    'Used for upsert deduplication — one document row per unique repo file.';

-- ── Indexes ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_documents_corpus
    ON rag.documents (tenant_id, corpus_id)
    WHERE corpus_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_documents_repo_path
    ON rag.documents (tenant_id, repo_path)
    WHERE repo_path IS NOT NULL;

-- ── Add metadata column to chunks if missing ─────────────────────────────────
ALTER TABLE rag.chunks
    ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- ── Verification ─────────────────────────────────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'rag'
          AND table_name   = 'documents'
          AND column_name  = 'corpus_id'
    ) THEN
        RAISE EXCEPTION 'Migration 20260303000001: corpus_id column not found';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'rag'
          AND table_name   = 'documents'
          AND column_name  = 'repo_path'
    ) THEN
        RAISE EXCEPTION 'Migration 20260303000001: repo_path column not found';
    END IF;
END $$;
