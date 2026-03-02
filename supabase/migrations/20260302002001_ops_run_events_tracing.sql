-- Migration: 20260302002001_ops_run_events_tracing.sql
-- Purpose:   Add OpenTelemetry trace correlation columns to ops.run_events (MAF parity P0)
--
-- Rationale:
--   MAF emits distributed traces via OpenTelemetry. IPAI run events had no trace
--   correlation, making cross-service debugging require manual timestamp matching.
--   This migration adds standard W3C trace context fields:
--     • trace_id — W3C TraceContext trace-id (16-byte / UUID representation)
--     • span_id  — W3C TraceContext span-id (8-byte / UUID representation)
--
--   Using UUID type gives us: type safety, Supabase RLS equality checks,
--   and compatibility with PostgREST filtering without requiring a text cast.
--   Null is valid for legacy rows and for events from agents that do not yet
--   emit OTel context.
--
-- Contract:  docs/contracts/C-AGENT-WORKFLOWS-01.md
-- Backwards-compat: ADD COLUMN IF NOT EXISTS; existing rows get NULL (acceptable).
-- RLS:       Inherits existing ops.run_events RLS policies (no policy changes needed).
-- Rollback:  ALTER TABLE ops.run_events DROP COLUMN IF EXISTS trace_id, span_id;

-- ── Add trace_id ───────────────────────────────────────────────────────────
ALTER TABLE ops.run_events
    ADD COLUMN IF NOT EXISTS trace_id UUID;

COMMENT ON COLUMN ops.run_events.trace_id IS
    'W3C TraceContext trace-id as UUID. Null for pre-OTel events. '
    'All events within a single ops.runs run should share the same trace_id '
    'when the skill executor propagates W3C trace context.';

-- ── Add span_id ────────────────────────────────────────────────────────────
ALTER TABLE ops.run_events
    ADD COLUMN IF NOT EXISTS span_id UUID;

COMMENT ON COLUMN ops.run_events.span_id IS
    'W3C TraceContext span-id as UUID. Null for pre-OTel events. '
    'Each phase transition (PLAN→PATCH→VERIFY→PR) should emit a new span_id '
    'to enable phase-level latency analysis.';

-- ── Index: trace lookup ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_ops_run_events_trace_id
    ON ops.run_events (trace_id)
    WHERE trace_id IS NOT NULL;

-- ── Verification ──────────────────────────────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ops'
          AND table_name   = 'run_events'
          AND column_name  = 'trace_id'
    ) THEN
        RAISE EXCEPTION 'Migration 20260302002001: trace_id column not found after ALTER';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ops'
          AND table_name   = 'run_events'
          AND column_name  = 'span_id'
    ) THEN
        RAISE EXCEPTION 'Migration 20260302002001: span_id column not found after ALTER';
    END IF;
END $$;
