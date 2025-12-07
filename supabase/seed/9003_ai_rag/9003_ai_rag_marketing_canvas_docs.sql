-- 9003_ai_rag_marketing_canvas_docs.sql
-- Family: 9003_ai_rag - RAG docs seed
-- Purpose:
--   * Seed AI Marketing Canvas + Scout documentation into gold/gold.doc_chunks
--     or equivalent RAG store for NotebookLM-style assistant.
-- Safety:
--   * Demo docs only.

BEGIN;

-- TODO: INSERT CANVAS / DOCS
--   * gold.docs
--   * gold.doc_chunks
--
-- Pattern:
--   * 1 row in gold.docs per source doc (canvas, PRDs, dashboards).
--   * Many rows in gold.doc_chunks with embedding vectors (loaded in ETL).

COMMIT;
