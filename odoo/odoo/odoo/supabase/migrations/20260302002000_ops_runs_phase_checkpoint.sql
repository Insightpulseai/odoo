-- Migration: 20260302002000_ops_runs_phase_checkpoint.sql
-- Purpose:   Add phase checkpoint columns to ops.runs (MAF parity P0)
--
-- Rationale:
--   Microsoft Agent Framework (MAF) Durable Task Scheduler persists phase state so that
--   agent runs are resumable across failures. IPAI runs that span multiple phases
--   (PLAN→PATCH→VERIFY→PR) had no durable checkpoint. This migration adds:
--     • last_phase  — the most recently completed workflow phase (VARCHAR to match
--                     the state_machine enum in ssot/agents/skills.yaml)
--     • checkpoint_at — when the last phase checkpoint was written (UTC)
--
-- Contract:  docs/contracts/C-AGENT-WORKFLOWS-01.md
-- Schema:    ssot/agents/interface_schema.yaml (valid_phases)
-- Backwards-compat: ADD COLUMN IF NOT EXISTS; existing rows get NULL (acceptable).
-- RLS:       Inherits existing ops.runs RLS policies (no policy changes needed).
-- Rollback:  ALTER TABLE ops.runs DROP COLUMN IF EXISTS last_phase, checkpoint_at;

-- ── Add last_phase ─────────────────────────────────────────────────────────
ALTER TABLE ops.runs
    ADD COLUMN IF NOT EXISTS last_phase VARCHAR(64);

COMMENT ON COLUMN ops.runs.last_phase IS
    'Most recently completed workflow phase (PLAN|PATCH|VERIFY|PR|MONITOR). '
    'Null until the first phase completes. Set by ops_complete_run() RPC.';

-- ── Add checkpoint_at ─────────────────────────────────────────────────────
ALTER TABLE ops.runs
    ADD COLUMN IF NOT EXISTS checkpoint_at TIMESTAMPTZ;

COMMENT ON COLUMN ops.runs.checkpoint_at IS
    'UTC timestamp when last_phase was last written. Used to detect stale runs '
    'and enforce max_duration_s timeouts at the scheduler level.';

-- ── Index: stale-run detection query (last_phase IS NULL AND old created_at) ─
CREATE INDEX IF NOT EXISTS idx_ops_runs_checkpoint_at
    ON ops.runs (checkpoint_at)
    WHERE checkpoint_at IS NOT NULL;

-- ── Verification ──────────────────────────────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ops'
          AND table_name   = 'runs'
          AND column_name  = 'last_phase'
    ) THEN
        RAISE EXCEPTION 'Migration 20260302002000: last_phase column not found after ALTER';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ops'
          AND table_name   = 'runs'
          AND column_name  = 'checkpoint_at'
    ) THEN
        RAISE EXCEPTION 'Migration 20260302002000: checkpoint_at column not found after ALTER';
    END IF;
END $$;
