-- =============================================================================
-- Migration: 20260301000010_ops_advisor.sql
-- Schema:    ops (advisor engine tables), work (knowledge base tables)
-- Purpose:   Ops Advisor Engine — Azure-Advisor-style recommendations across
--            5 pillars: Security, Cost, Reliability, Ops Excellence, Performance
-- Branch:    feat/taskbus-agent-orchestration
-- Date:      2026-03-01
-- Author:    ipai execution agent
-- =============================================================================
--
-- Depends on:
--   - 20260301000002_work_schema.sql  (creates work schema)
--   - ops schema must exist (created in earlier migration)
--
-- RLS posture:
--   - ops.*  : RLS disabled (internal platform tables; access via service_role only)
--   - work.* : RLS enabled; service_role bypasses; anon/authenticated denied by default
--
-- DO NOT edit generated files directly; this migration is append-only per Rule 5.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. ops.advisor_scans
-- ---------------------------------------------------------------------------
-- One row per advisor scan run. A scan collects facts from a provider,
-- evaluates rulepack(s), and writes findings. status progresses:
--   running → completed | failed
-- summary_json holds a provider-specific snapshot (e.g. list of droplets
-- inspected, repos scanned, edge function counts, etc.)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops.advisor_scans (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  provider      TEXT        NOT NULL
                              CHECK (provider IN (
                                'digitalocean',
                                'vercel',
                                'supabase',
                                'github'
                              )),
  started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at   TIMESTAMPTZ,
  status        TEXT        NOT NULL DEFAULT 'running'
                              CHECK (status IN ('running', 'completed', 'failed')),
  summary_json  JSONB,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  ops.advisor_scans IS
  'One row per advisor scan run. A scan collects facts from a provider, '
  'evaluates rulepack(s), and writes findings.';
COMMENT ON COLUMN ops.advisor_scans.provider IS
  'Scan adapter: digitalocean | vercel | supabase | github';
COMMENT ON COLUMN ops.advisor_scans.status IS
  'Lifecycle: running → completed | failed';
COMMENT ON COLUMN ops.advisor_scans.summary_json IS
  'Provider-specific snapshot captured during the scan '
  '(e.g. droplet inventory, repo list, edge function counts).';

-- RLS: disabled for ops schema — internal platform use only
ALTER TABLE ops.advisor_scans DISABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 2. ops.advisor_findings
-- ---------------------------------------------------------------------------
-- Individual findings produced by a scan. Each finding references a scan,
-- belongs to a Well-Architected pillar, has a severity, and carries evidence
-- and a citation_url linking back to the authoritative source doc.
-- status progresses: open → dismissed | resolved
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops.advisor_findings (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id          UUID        NOT NULL
                                 REFERENCES ops.advisor_scans(id)
                                 ON DELETE CASCADE,
  pillar           TEXT        NOT NULL
                                 CHECK (pillar IN (
                                   'security',
                                   'cost',
                                   'reliability',
                                   'ops_excellence',
                                   'performance'
                                 )),
  severity         TEXT        NOT NULL
                                 CHECK (severity IN (
                                   'critical',
                                   'high',
                                   'medium',
                                   'low',
                                   'info'
                                 )),
  title            TEXT        NOT NULL,
  description      TEXT,
  resource_ref     TEXT,        -- e.g. 'droplet:ocr-service-droplet', 'repo:Insightpulseai/odoo'
  evidence_json    JSONB,       -- raw evidence payload captured during scan
  recommendation   TEXT,        -- human-readable remediation guidance
  citation_url     TEXT,        -- link to GitHub WAF / DO docs / Vercel docs
  status           TEXT        NOT NULL DEFAULT 'open'
                                 CHECK (status IN ('open', 'dismissed', 'resolved')),
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  ops.advisor_findings IS
  'Individual findings produced by an advisor scan. Each finding references '
  'a scan, a Well-Architected pillar, and carries a citation_url linking to '
  'the authoritative source document.';
COMMENT ON COLUMN ops.advisor_findings.pillar IS
  'Well-Architected pillar: security | cost | reliability | ops_excellence | performance';
COMMENT ON COLUMN ops.advisor_findings.severity IS
  'Severity tier: critical | high | medium | low | info';
COMMENT ON COLUMN ops.advisor_findings.resource_ref IS
  'Free-text resource identifier, e.g. "droplet:ocr-service-droplet" or '
  '"repo:Insightpulseai/odoo". Used for display and linking.';
COMMENT ON COLUMN ops.advisor_findings.evidence_json IS
  'Raw evidence payload captured during the scan (API response fragments, '
  'metric values, policy states, etc.).';
COMMENT ON COLUMN ops.advisor_findings.citation_url IS
  'Authoritative source URL (GitHub WAF, DO docs, Vercel docs, etc.) that '
  'explains why this finding matters and how to resolve it.';
COMMENT ON COLUMN ops.advisor_findings.status IS
  'Lifecycle: open → dismissed | resolved';

ALTER TABLE ops.advisor_findings DISABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS advisor_findings_scan_id_idx
  ON ops.advisor_findings (scan_id);
CREATE INDEX IF NOT EXISTS advisor_findings_pillar_severity_idx
  ON ops.advisor_findings (pillar, severity);
CREATE INDEX IF NOT EXISTS advisor_findings_status_idx
  ON ops.advisor_findings (status);

-- ---------------------------------------------------------------------------
-- 3. ops.workbooks
-- ---------------------------------------------------------------------------
-- A workbook is a curated remediation guide tied to a specific finding type.
-- Findings may reference a workbook via a remediation_workbook field in the
-- rulepack YAML. The Ops Console renders workbook steps interactively.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops.workbooks (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT        NOT NULL,
  source      TEXT,                    -- e.g. 'github_well_architected' | 'do_monitoring' | 'vercel'
  version     TEXT,
  pillar      TEXT
                CHECK (pillar IN (
                  'security',
                  'cost',
                  'reliability',
                  'ops_excellence',
                  'performance'
                )),
  description TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  ops.workbooks IS
  'Curated remediation guides. A workbook is composed of ordered steps. '
  'Findings reference workbooks via the rulepack YAML remediation_workbook field.';
COMMENT ON COLUMN ops.workbooks.source IS
  'Origin of the workbook guidance: github_well_architected | do_monitoring | vercel | internal';

ALTER TABLE ops.workbooks DISABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 4. ops.workbook_steps
-- ---------------------------------------------------------------------------
-- Ordered steps within a workbook. Each step may require captured evidence
-- and may reference an automation script in the repo.
-- status progresses: pending → in_progress → completed | skipped
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops.workbook_steps (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  workbook_id      UUID        NOT NULL
                                 REFERENCES ops.workbooks(id)
                                 ON DELETE CASCADE,
  step_no          INTEGER     NOT NULL,
  text             TEXT        NOT NULL,
  evidence_required BOOLEAN    NOT NULL DEFAULT false,
  automation_ref   TEXT,        -- repo-relative path, e.g. 'scripts/maintenance/rotate_logs.sh'
  status           TEXT        NOT NULL DEFAULT 'pending'
                                 CHECK (status IN (
                                   'pending',
                                   'in_progress',
                                   'completed',
                                   'skipped'
                                 )),
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  ops.workbook_steps IS
  'Ordered remediation steps within a workbook. Steps with evidence_required=true '
  'block workbook completion until the user captures proof.';
COMMENT ON COLUMN ops.workbook_steps.automation_ref IS
  'Repo-relative path to an automation script that executes this step, '
  'e.g. "scripts/maintenance/rotate_logs.sh". Null when step is manual-only.';
COMMENT ON COLUMN ops.workbook_steps.status IS
  'Step lifecycle: pending → in_progress → completed | skipped';

ALTER TABLE ops.workbook_steps DISABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS workbook_steps_workbook_id_idx
  ON ops.workbook_steps (workbook_id, step_no);

-- ---------------------------------------------------------------------------
-- 5. work.kb_sources
-- ---------------------------------------------------------------------------
-- Registry of knowledge base source URLs scraped / synced into the KB.
-- Each source maps to one or more documents (work.kb_documents).
-- pillar allows filtering the KB by Well-Architected pillar.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS work.kb_sources (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  name           TEXT        NOT NULL,
  base_url       TEXT        NOT NULL,
  description    TEXT,
  pillar         TEXT,
  last_synced_at TIMESTAMPTZ,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  work.kb_sources IS
  'Registry of knowledge base source URLs. Each source is periodically scraped '
  'or synced; documents land in work.kb_documents.';
COMMENT ON COLUMN work.kb_sources.pillar IS
  'Optional Well-Architected pillar affinity for this source.';
COMMENT ON COLUMN work.kb_sources.last_synced_at IS
  'Timestamp of the most recent successful sync/scrape of this source.';

-- RLS: enabled on work schema; default-deny for anon/authenticated;
-- service_role access is unrestricted (bypasses RLS).
ALTER TABLE work.kb_sources ENABLE ROW LEVEL SECURITY;

-- Deny all access by default (service_role bypasses RLS automatically in Supabase)
-- No explicit policies needed for service_role-only access pattern.
-- If future authenticated access is required, add policies here.

-- ---------------------------------------------------------------------------
-- 6. work.kb_documents
-- ---------------------------------------------------------------------------
-- Individual documents fetched from a kb_source. Content is stored as full
-- text and chunked into work.kb_chunks for full-text search.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS work.kb_documents (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id      UUID        NOT NULL
                               REFERENCES work.kb_sources(id)
                               ON DELETE CASCADE,
  title          TEXT        NOT NULL,
  url            TEXT        NOT NULL,
  pillar         TEXT,
  tags           TEXT[],
  content        TEXT,
  last_fetched_at TIMESTAMPTZ,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  work.kb_documents IS
  'Individual documents fetched from a kb_source. Full content is stored here '
  'and broken into chunks in work.kb_chunks for FTS indexing.';
COMMENT ON COLUMN work.kb_documents.tags IS
  'Array of free-form tags for additional filtering (e.g. {"rulesets","branch-protection"}).';
COMMENT ON COLUMN work.kb_documents.last_fetched_at IS
  'Timestamp of the most recent successful content fetch for this document.';

ALTER TABLE work.kb_documents ENABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS kb_documents_source_id_idx
  ON work.kb_documents (source_id);

-- ---------------------------------------------------------------------------
-- 7. work.kb_chunks (FTS-first; vector embeddings deferred to a later migration)
-- ---------------------------------------------------------------------------
-- Documents are split into chunks for efficient full-text search. The
-- search_vector column is a GENERATED column using GIN-indexed TSVECTOR.
-- No pgvector embeddings on day 1 — OTel/embedding pipeline added later.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS work.kb_chunks (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  doc_id        UUID        NOT NULL
                              REFERENCES work.kb_documents(id)
                              ON DELETE CASCADE,
  chunk_no      INTEGER     NOT NULL,
  content       TEXT        NOT NULL,
  search_vector TSVECTOR    GENERATED ALWAYS AS (
                              to_tsvector('english', content)
                            ) STORED,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  work.kb_chunks IS
  'Content chunks derived from kb_documents. search_vector is a GENERATED '
  'TSVECTOR column enabling GIN-indexed full-text search. '
  'Vector embeddings (pgvector) are deferred to a subsequent migration.';
COMMENT ON COLUMN work.kb_chunks.chunk_no IS
  'Sequential chunk index within the parent document, 0-based.';
COMMENT ON COLUMN work.kb_chunks.search_vector IS
  'Auto-generated tsvector from content using the "english" text search config. '
  'Used by GIN index kb_chunks_search_vector_idx for FTS queries.';

ALTER TABLE work.kb_chunks ENABLE ROW LEVEL SECURITY;

-- GIN index for full-text search
CREATE INDEX IF NOT EXISTS kb_chunks_search_vector_idx
  ON work.kb_chunks
  USING GIN (search_vector);

CREATE INDEX IF NOT EXISTS kb_chunks_doc_id_idx
  ON work.kb_chunks (doc_id, chunk_no);

-- =============================================================================
-- Migration complete.
-- Tables created:
--   ops.advisor_scans       (RLS disabled)
--   ops.advisor_findings    (RLS disabled)
--   ops.workbooks           (RLS disabled)
--   ops.workbook_steps      (RLS disabled)
--   work.kb_sources         (RLS enabled, service_role only)
--   work.kb_documents       (RLS enabled, service_role only)
--   work.kb_chunks          (RLS enabled, GIN FTS index)
-- =============================================================================
