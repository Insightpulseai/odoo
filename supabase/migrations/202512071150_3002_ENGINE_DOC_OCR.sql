-- 202512071150_3002_ENGINE_DOC_OCR.sql
-- Family: 3000 - Engines (Document OCR & Handwriting)
-- Purpose:
--   * Core document/receipt OCR engine used by TE-Cheq, Retail-Intel, Finance.
-- Safety:
--   * Additive only; no destructive RLS or DDL changes.

BEGIN;

CREATE SCHEMA IF NOT EXISTS doc;
CREATE SCHEMA IF NOT EXISTS ocr;
CREATE SCHEMA IF NOT EXISTS logs;

-- TODO: DOC / OCR TABLES
--   * doc.raw_documents
--   * doc.parsed_documents
--   * doc.user_corrections
--   * ocr.model_profile
--   * logs.doc_ocr_engine_events

-- TODO: DOC OCR FUNCTIONS / TOOLS
--   * doc_ocr_upload(...)
--   * doc_ocr_get_parsed(...)
--   * doc_ocr_submit_correction(...)

COMMIT;
