-- Test: ops.ingest_bridge_event() is idempotent on duplicate idempotency_key
--
-- Acceptance criteria (T4.5 from spec/ipai-llm-supabase-bridge/tasks.md):
--   Calling ops.ingest_bridge_event() twice with the same idempotency_key
--   must insert exactly 1 row into ops.run_events.
--
-- Run against the target Supabase database:
--   psql "$SUPABASE_DB_URL" -f supabase/tests/ops_ingest_bridge_event_idempotent.sql
--
-- Expected output (no RAISE EXCEPTION):
--   NOTICE:  Idempotency test PASSED: 1 row for key "test-idempotency-bridge-<uuid>"

BEGIN;

DO $$
DECLARE
    v_key   TEXT := 'test-idempotency-bridge-' || gen_random_uuid()::text;
    v_count BIGINT;
BEGIN
    -- First call — inserts a new row
    PERFORM ops.ingest_bridge_event(
        p_event_type      := 'tool.call',
        p_idempotency_key := v_key,
        p_odoo_db         := 'odoo_dev',
        p_odoo_model      := 'llm.tool',
        p_odoo_id         := 1,
        p_odoo_event_id   := 1,
        p_payload         := '{"test": true, "call": "first"}'::jsonb,
        p_timestamp       := now()
    );

    -- Second call — identical idempotency_key, must be a no-op
    PERFORM ops.ingest_bridge_event(
        p_event_type      := 'tool.call',
        p_idempotency_key := v_key,
        p_odoo_db         := 'odoo_dev',
        p_odoo_model      := 'llm.tool',
        p_odoo_id         := 1,
        p_odoo_event_id   := 1,
        p_payload         := '{"test": true, "call": "second"}'::jsonb,
        p_timestamp       := now()
    );

    -- Assert: exactly 1 row with this idempotency_key
    SELECT COUNT(*)
      INTO v_count
      FROM ops.run_events
     WHERE idempotency_key = v_key;

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'Idempotency test FAILED: expected 1 row, got % for key "%"',
            v_count, v_key;
    END IF;

    RAISE NOTICE 'Idempotency test PASSED: 1 row for key "%"', v_key;
END;
$$;

ROLLBACK; -- Always clean up; test is read-only against production data
