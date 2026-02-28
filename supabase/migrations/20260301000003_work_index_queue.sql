-- =============================================================================
-- Migration: work.index_queue — deterministic async indexing queue
-- Replaces manual Supabase Dashboard DB Webhooks with a repo-owned queue.
--
-- Governance: no dashboard-only configuration allowed.
-- All automation is expressed as: migration + function + schedule + SSOT entry.
--
-- How it works:
--   1. Triggers on work.pages and work.blocks enqueue items automatically.
--   2. workspace-indexer Edge Function claims batches via work.claim_index_batch().
--   3. After processing (tsvector + optional embedding → work.search_index),
--      the function acks each item via work.ack_index().
--   4. Failed items are requeued with exponential backoff (max 5 attempts).
--   5. The function is invoked by Supabase Cron (every 2 min) — no DB webhook.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- work.index_queue table
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS work.index_queue (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  space_id        uuid NOT NULL REFERENCES work.spaces(id) ON DELETE CASCADE,
  source_table    text NOT NULL CHECK (source_table IN ('pages', 'blocks')),
  source_id       uuid NOT NULL,
  updated_at      timestamptz NOT NULL DEFAULT now(),

  -- Claim state
  claimed_at      timestamptz,
  claimed_by      text,       -- identifier of the worker that claimed it

  -- Outcome state
  status          text NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'processing', 'done', 'failed')),
  attempt_count   int NOT NULL DEFAULT 0,
  last_error      text,
  processed_at    timestamptz,

  created_at      timestamptz NOT NULL DEFAULT now(),

  -- Deduplicate: one pending/processing entry per (table, id)
  CONSTRAINT uq_index_queue_source UNIQUE (source_table, source_id)
);

CREATE INDEX IF NOT EXISTS idx_iq_pending
  ON work.index_queue (status, updated_at)
  WHERE status IN ('pending', 'failed');

CREATE INDEX IF NOT EXISTS idx_iq_space
  ON work.index_queue (space_id);

-- ---------------------------------------------------------------------------
-- RLS: only service_role may write; space members may read their items
-- ---------------------------------------------------------------------------

ALTER TABLE work.index_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_all_index_queue" ON work.index_queue
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "auth_read_index_queue" ON work.index_queue
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM work.permissions p
      WHERE p.space_id = work.index_queue.space_id
        AND p.user_id = auth.uid()
    )
  );

-- ---------------------------------------------------------------------------
-- RPC: work.enqueue_index — upsert a queue item (idempotent)
-- Called by triggers; also safe to call directly for manual reindex.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION work.enqueue_index(
  p_table_name text,
  p_pk         uuid,
  p_space_id   uuid,
  p_updated_at timestamptz DEFAULT now()
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO work.index_queue (source_table, source_id, space_id, updated_at, status)
  VALUES (p_table_name, p_pk, p_space_id, p_updated_at, 'pending')
  ON CONFLICT (source_table, source_id) DO UPDATE
    SET updated_at    = EXCLUDED.updated_at,
        status        = CASE
                          WHEN work.index_queue.status = 'done' THEN 'pending'
                          ELSE work.index_queue.status
                        END,
        claimed_at    = CASE
                          WHEN work.index_queue.status = 'done' THEN NULL
                          ELSE work.index_queue.claimed_at
                        END,
        claimed_by    = CASE
                          WHEN work.index_queue.status = 'done' THEN NULL
                          ELSE work.index_queue.claimed_by
                        END;
END;
$$;

GRANT EXECUTE ON FUNCTION work.enqueue_index TO service_role;
-- Note: triggers execute as SECURITY DEFINER so no grant needed for trigger path.

-- ---------------------------------------------------------------------------
-- RPC: work.claim_index_batch — atomically claim N items for processing
-- Safe under concurrent callers (FOR UPDATE SKIP LOCKED).
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION work.claim_index_batch(
  p_batch_size int DEFAULT 10,
  p_worker_id  text DEFAULT 'workspace-indexer'
)
RETURNS SETOF work.index_queue
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  max_attempts CONSTANT int := 5;
BEGIN
  RETURN QUERY
  UPDATE work.index_queue q
  SET
    status      = 'processing',
    claimed_at  = now(),
    claimed_by  = p_worker_id,
    attempt_count = q.attempt_count + 1
  WHERE q.id IN (
    SELECT id
    FROM work.index_queue
    WHERE status IN ('pending', 'failed')
      AND attempt_count < max_attempts
      -- exponential backoff: 1m, 2m, 4m, 8m after failures
      AND (
        status = 'pending'
        OR (status = 'failed' AND processed_at < now() - (INTERVAL '1 minute' * power(2, attempt_count - 1)))
      )
    ORDER BY updated_at ASC
    LIMIT p_batch_size
    FOR UPDATE SKIP LOCKED
  )
  RETURNING q.*;
END;
$$;

GRANT EXECUTE ON FUNCTION work.claim_index_batch TO service_role;

-- ---------------------------------------------------------------------------
-- RPC: work.ack_index — mark item done or requeue on failure
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION work.ack_index(
  p_id    uuid,
  p_ok    bool,
  p_error text DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  max_attempts CONSTANT int := 5;
  v_attempts int;
BEGIN
  SELECT attempt_count INTO v_attempts FROM work.index_queue WHERE id = p_id;

  IF p_ok THEN
    UPDATE work.index_queue
    SET status       = 'done',
        last_error   = NULL,
        processed_at = now()
    WHERE id = p_id;
  ELSE
    UPDATE work.index_queue
    SET status       = CASE WHEN v_attempts >= max_attempts THEN 'failed' ELSE 'pending' END,
        last_error   = p_error,
        processed_at = now(),
        claimed_at   = NULL,
        claimed_by   = NULL
    WHERE id = p_id;
  END IF;
END;
$$;

GRANT EXECUTE ON FUNCTION work.ack_index TO service_role;

-- ---------------------------------------------------------------------------
-- Trigger: auto-enqueue on work.pages INSERT / UPDATE
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION work.tg_enqueue_page()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Skip if content hasn't changed meaningfully (avoid spurious re-indexing)
  IF TG_OP = 'UPDATE' AND NEW.title IS NOT DISTINCT FROM OLD.title
     AND NEW.content IS NOT DISTINCT FROM OLD.content THEN
    RETURN NEW;
  END IF;

  PERFORM work.enqueue_index('pages', NEW.id, NEW.space_id, now());
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS tg_enqueue_page ON work.pages;
CREATE TRIGGER tg_enqueue_page
  AFTER INSERT OR UPDATE ON work.pages
  FOR EACH ROW EXECUTE FUNCTION work.tg_enqueue_page();

-- ---------------------------------------------------------------------------
-- Trigger: auto-enqueue on work.blocks INSERT / UPDATE
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION work.tg_enqueue_block()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  IF TG_OP = 'UPDATE' AND NEW.content IS NOT DISTINCT FROM OLD.content THEN
    RETURN NEW;
  END IF;

  PERFORM work.enqueue_index('blocks', NEW.id, NEW.space_id, now());
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS tg_enqueue_block ON work.blocks;
CREATE TRIGGER tg_enqueue_block
  AFTER INSERT OR UPDATE ON work.blocks
  FOR EACH ROW EXECUTE FUNCTION work.tg_enqueue_block();

-- ---------------------------------------------------------------------------
-- DB-side tsvector indexer function
-- Called by pg_cron every 2 minutes. Handles tsvector computation only.
-- Embedding computation (requires OPENAI_API_KEY) is done by the
-- workspace-indexer Edge Function, invoked via:
--   - Supabase scheduled functions (supabase/config.toml)
--   - OR: supabase functions invoke workspace-indexer (manual/taskbus)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION work.process_index_queue_tsvector(p_batch_size int DEFAULT 20)
RETURNS TABLE(processed int, succeeded int, failed int)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  item        work.index_queue%ROWTYPE;
  v_processed int := 0;
  v_succeeded int := 0;
  v_failed    int := 0;
  v_title     text;
  v_body      text;
  v_tsv       tsvector;
BEGIN
  FOR item IN
    SELECT * FROM work.claim_index_batch(p_batch_size, 'pg-cron-tsvector')
  LOOP
    BEGIN
      -- Fetch text from source table
      IF item.source_table = 'pages' THEN
        SELECT
          coalesce(p.title, ''),
          coalesce(p.title, '') || ' ' || coalesce(p.content::text, '')
        INTO v_title, v_body
        FROM work.pages p WHERE p.id = item.source_id;

      ELSIF item.source_table = 'blocks' THEN
        SELECT
          NULL,
          coalesce(b.content->>'text', b.content->>'value', b.content->>'expression', '')
        INTO v_title, v_body
        FROM work.blocks b WHERE b.id = item.source_id;
      END IF;

      IF v_body IS NULL OR trim(v_body) = '' THEN
        -- Nothing to index; ack as done
        PERFORM work.ack_index(item.id, true, NULL);
        v_succeeded := v_succeeded + 1;
      ELSE
        v_tsv := to_tsvector('english', trim(coalesce(v_title,'') || ' ' || v_body));

        INSERT INTO work.search_index (source_table, source_id, space_id, title, body, search_vec, updated_at)
        VALUES (item.source_table, item.source_id, item.space_id, v_title, trim(v_body), v_tsv, now())
        ON CONFLICT (source_table, source_id) DO UPDATE
          SET title      = EXCLUDED.title,
              body       = EXCLUDED.body,
              search_vec = EXCLUDED.search_vec,
              updated_at = EXCLUDED.updated_at;
        -- Note: embedding column is left unchanged — updated by workspace-indexer Edge Function

        PERFORM work.ack_index(item.id, true, NULL);
        v_succeeded := v_succeeded + 1;
      END IF;

    EXCEPTION WHEN OTHERS THEN
      PERFORM work.ack_index(item.id, false, SQLERRM);
      v_failed := v_failed + 1;
    END;

    v_processed := v_processed + 1;
  END LOOP;

  RETURN QUERY SELECT v_processed, v_succeeded, v_failed;
END;
$$;

GRANT EXECUTE ON FUNCTION work.process_index_queue_tsvector TO service_role;

-- ---------------------------------------------------------------------------
-- pg_cron schedule — DB-side tsvector maintenance (no HTTP call)
-- Requires pg_cron extension (enabled by default on Supabase Pro+).
-- Schedules work.process_index_queue_tsvector() — a pure SQL function.
--
-- Embedding computation is NOT done here; it is done by the
-- workspace-indexer Edge Function on its own schedule (supabase/config.toml).
-- ---------------------------------------------------------------------------

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
    -- Idempotent: unschedule if already exists, then recreate
    BEGIN
      PERFORM cron.unschedule('workspace-tsvector-poll');
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    PERFORM cron.schedule(
      'workspace-tsvector-poll',
      '*/2 * * * *',
      $cron$ SELECT work.process_index_queue_tsvector(20) $cron$
    );
  END IF;
  -- If pg_cron is not available, tsvector updates happen when the
  -- workspace-indexer Edge Function is invoked (it also handles tsvector via upsert).
END $$;

-- ---------------------------------------------------------------------------
-- Monitoring view: queue health
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW work.v_index_queue_health AS
SELECT
  status,
  count(*)                               AS item_count,
  max(attempt_count)                     AS max_attempts,
  min(updated_at)                        AS oldest_pending,
  max(processed_at)                      AS latest_processed
FROM work.index_queue
GROUP BY status;

GRANT SELECT ON work.v_index_queue_health TO service_role, authenticated;
