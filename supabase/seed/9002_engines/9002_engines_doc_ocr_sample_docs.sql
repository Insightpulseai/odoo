-- 9002_engines_doc_ocr_sample_docs.sql
-- Family: 9002_engines - Doc-OCR seed
-- Purpose:
--   * Seed synthetic documents (receipts, invoices, IDs) for OCR regression.
-- Safety:
--   * Demo only; do not use with real PII.

BEGIN;

-- TODO: INSERT SAMPLE DOC METADATA
--   * doc.raw_documents
--   * doc.parsed_documents
--
-- Binary payloads should live in object storage; these seeds reference
-- storage keys / URLs only.

COMMIT;
