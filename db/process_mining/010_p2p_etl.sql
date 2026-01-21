-- P2P (Procure-to-Pay) Process Mining ETL
-- Extracts events from Odoo purchase/receiving/billing/payment flow
--
-- Usage:
--   -- Apply schema first
--   psql -f 001_pm_schema.sql
--   -- Then apply this ETL function
--   psql -f 010_p2p_etl.sql
--   -- Run backfill
--   SELECT pm.run_p2p_etl('1970-01-01'::timestamptz, now());
--   -- Run incremental (uses last_run_ts from job_state)
--   SELECT pm.run_p2p_etl();

BEGIN;

-- P2P ETL: builds pm.case + pm.event for impacted purchase orders,
-- then recomputes variants/edges/deviations.
--
-- Notes:
-- - Odoo table names assumed as default: purchase_order, stock_picking, account_move
-- - Some fields vary by version/customization; guarded with COALESCE where possible.
-- - Payment mapping is provided as "best-effort" via ref matching (see TODO for strict reconciliation).

CREATE OR REPLACE FUNCTION pm.run_p2p_etl(
  p_from timestamptz DEFAULT NULL,
  p_to timestamptz DEFAULT now()
)
RETURNS TABLE(cases_processed int, events_created int, deviations_found int)
LANGUAGE plpgsql
AS $$
DECLARE
  v_job text := 'p2p_etl';
  v_last timestamptz;
  v_from timestamptz;
  v_cases_count int := 0;
  v_events_count int := 0;
  v_deviations_count int := 0;
BEGIN
  -- Initialize job state if not exists
  INSERT INTO pm.job_state(job_name) VALUES (v_job)
  ON CONFLICT (job_name) DO NOTHING;

  -- Get last run timestamp with row lock
  SELECT last_run_ts INTO v_last FROM pm.job_state WHERE job_name = v_job FOR UPDATE;
  v_from := COALESCE(p_from, v_last);

  -- Buffer window to catch late writes (Odoo async updates)
  v_from := v_from - interval '10 minutes';

  -- 1) Identify impacted purchase orders by write_date/create_date in window
  DROP TABLE IF EXISTS tmp_impacted_po;
  CREATE TEMP TABLE tmp_impacted_po (po_id bigint PRIMARY KEY) ON COMMIT DROP;

  INSERT INTO tmp_impacted_po(po_id)
  SELECT po.id AS po_id
  FROM purchase_order po
  WHERE COALESCE(po.write_date, po.create_date) >= v_from
    AND COALESCE(po.write_date, po.create_date) < p_to;

  -- Also include POs whose related docs changed recently (receipt or bill)
  INSERT INTO tmp_impacted_po(po_id)
  SELECT DISTINCT po.id
  FROM purchase_order po
  JOIN stock_picking sp
    ON (sp.origin = po.name OR sp.origin ILIKE '%' || po.name || '%')
  WHERE COALESCE(sp.write_date, sp.create_date) >= v_from
    AND COALESCE(sp.write_date, sp.create_date) < p_to
  ON CONFLICT (po_id) DO NOTHING;

  INSERT INTO tmp_impacted_po(po_id)
  SELECT DISTINCT po.id
  FROM purchase_order po
  JOIN account_move am
    ON (am.invoice_origin = po.name OR am.invoice_origin ILIKE '%' || po.name || '%')
  WHERE COALESCE(am.write_date, am.create_date) >= v_from
    AND COALESCE(am.write_date, am.create_date) < p_to
  ON CONFLICT (po_id) DO NOTHING;

  GET DIAGNOSTICS v_cases_count = ROW_COUNT;

  -- 2) Upsert pm.case for impacted POs
  INSERT INTO pm.case(case_id, process, source_model, source_id, company_id, attrs_json, updated_at)
  SELECT
    'p2p:po:' || po.id::text AS case_id,
    'p2p' AS process,
    'purchase.order' AS source_model,
    po.id AS source_id,
    po.company_id,
    jsonb_build_object(
      'po_name', po.name,
      'state', po.state,
      'partner_id', po.partner_id,
      'user_id', po.user_id,
      'amount_total', po.amount_total,
      'currency_id', po.currency_id
    ) AS attrs_json,
    now() AS updated_at
  FROM purchase_order po
  JOIN tmp_impacted_po t ON t.po_id = po.id
  ON CONFLICT (case_id) DO UPDATE
    SET company_id = EXCLUDED.company_id,
        attrs_json = EXCLUDED.attrs_json,
        updated_at = now();

  -- 3) Rebuild events for impacted cases (idempotent: delete + insert)
  DELETE FROM pm.event e
  WHERE e.case_id IN (
    SELECT 'p2p:po:' || t.po_id::text FROM tmp_impacted_po t
  )
  AND e.process = 'p2p';

  -- 3A) PO Created
  INSERT INTO pm.event(case_id, process, activity, ts, resource, source_model, source_id, attrs_json)
  SELECT
    'p2p:po:' || po.id::text,
    'p2p',
    'PO Created',
    po.create_date,
    NULL,
    'purchase.order',
    po.id,
    jsonb_build_object('po_name', po.name, 'state', po.state)
  FROM purchase_order po
  JOIN tmp_impacted_po t ON t.po_id = po.id
  WHERE po.create_date IS NOT NULL;

  -- 3B) PO Confirmed/Approved (best-effort: use date_approve if available, else write_date)
  INSERT INTO pm.event(case_id, process, activity, ts, resource, source_model, source_id, attrs_json)
  SELECT
    'p2p:po:' || po.id::text,
    'p2p',
    'PO Approved',
    COALESCE(po.date_approve, po.write_date, po.create_date),
    NULL,
    'purchase.order',
    po.id,
    jsonb_build_object('po_name', po.name, 'state', po.state)
  FROM purchase_order po
  JOIN tmp_impacted_po t ON t.po_id = po.id
  WHERE po.state IN ('purchase','done')
    AND COALESCE(po.date_approve, po.write_date, po.create_date) IS NOT NULL;

  -- 3C) Goods Receipt Done (incoming pickings linked by origin)
  INSERT INTO pm.event(case_id, process, activity, ts, resource, source_model, source_id, attrs_json)
  SELECT
    'p2p:po:' || po.id::text,
    'p2p',
    'Goods Received',
    COALESCE(sp.date_done, sp.scheduled_date, sp.write_date, sp.create_date),
    NULL,
    'stock.picking',
    sp.id,
    jsonb_build_object('picking_name', sp.name, 'state', sp.state, 'origin', sp.origin)
  FROM purchase_order po
  JOIN tmp_impacted_po t ON t.po_id = po.id
  JOIN stock_picking sp
    ON (sp.origin = po.name OR sp.origin ILIKE '%' || po.name || '%')
  WHERE sp.state = 'done';

  -- 3D) Vendor Bill Posted (in_invoice) linked by invoice_origin
  INSERT INTO pm.event(case_id, process, activity, ts, resource, source_model, source_id, attrs_json)
  SELECT
    'p2p:po:' || po.id::text,
    'p2p',
    'Vendor Bill Posted',
    COALESCE(am.invoice_date, am.date, am.write_date, am.create_date),
    NULL,
    'account.move',
    am.id,
    jsonb_build_object('move_name', am.name, 'state', am.state, 'invoice_origin', am.invoice_origin, 'amount_total', am.amount_total)
  FROM purchase_order po
  JOIN tmp_impacted_po t ON t.po_id = po.id
  JOIN account_move am
    ON (am.invoice_origin = po.name OR am.invoice_origin ILIKE '%' || po.name || '%')
  WHERE am.move_type = 'in_invoice'
    AND am.state = 'posted';

  -- 3E) Payment Posted (best-effort heuristic)
  -- TODO: For strict accuracy, implement reconciliation via account_partial_reconcile
  -- Current approach: match payment ref to PO name or vendor bill name
  INSERT INTO pm.event(case_id, process, activity, ts, resource, source_model, source_id, attrs_json)
  SELECT DISTINCT ON (po.id, pay.id)
    'p2p:po:' || po.id::text,
    'p2p',
    'Payment Posted',
    COALESCE(pay.date, pay.write_date, pay.create_date),
    NULL,
    'account.payment',
    pay.id,
    jsonb_build_object('payment_ref', pay.ref, 'amount', pay.amount, 'state', pay.state)
  FROM purchase_order po
  JOIN tmp_impacted_po t ON t.po_id = po.id
  JOIN account_payment pay
    ON (
      pay.ref ILIKE '%' || po.name || '%'
      OR EXISTS (
        SELECT 1
        FROM account_move am
        WHERE (am.invoice_origin = po.name OR am.invoice_origin ILIKE '%' || po.name || '%')
          AND am.move_type = 'in_invoice'
          AND (pay.ref ILIKE '%' || am.name || '%' OR pay.ref ILIKE '%' || COALESCE(am.payment_reference, '') || '%')
      )
    )
  WHERE pay.state IN ('posted','reconciled');

  -- Count events created
  SELECT COUNT(*) INTO v_events_count
  FROM pm.event
  WHERE case_id IN (SELECT 'p2p:po:' || po_id::text FROM tmp_impacted_po);

  -- 4) Compute start/end/duration for impacted cases
  UPDATE pm.case c
  SET start_ts = x.min_ts,
      end_ts   = x.max_ts,
      duration_s = EXTRACT(EPOCH FROM (x.max_ts - x.min_ts))::bigint,
      updated_at = now()
  FROM (
    SELECT case_id, MIN(ts) AS min_ts, MAX(ts) AS max_ts
    FROM pm.event
    WHERE process = 'p2p'
      AND case_id IN (SELECT 'p2p:po:' || po_id::text FROM tmp_impacted_po)
    GROUP BY case_id
  ) x
  WHERE c.case_id = x.case_id;

  -- 5) Compute variants for impacted cases
  DROP TABLE IF EXISTS tmp_case_seq;
  CREATE TEMP TABLE tmp_case_seq AS
  SELECT
    e.case_id,
    array_agg(e.activity ORDER BY e.ts, e.event_id) AS seq
  FROM pm.event e
  WHERE e.process = 'p2p'
    AND e.case_id IN (SELECT 'p2p:po:' || po_id::text FROM tmp_impacted_po)
  GROUP BY e.case_id;

  -- Upsert variant catalog
  INSERT INTO pm.variant(variant_id, process, sequence, sequence_hash, case_count, updated_at)
  SELECT
    md5(array_to_string(seq, '→')) AS variant_id,
    'p2p' AS process,
    seq AS sequence,
    md5(array_to_string(seq, '→')) AS sequence_hash,
    0,
    now()
  FROM tmp_case_seq
  ON CONFLICT (variant_id) DO UPDATE
    SET sequence = EXCLUDED.sequence,
        updated_at = now();

  -- Assign variant_id to cases
  UPDATE pm.case c
  SET variant_id = v.variant_id,
      updated_at = now()
  FROM (
    SELECT case_id, md5(array_to_string(seq, '→')) AS variant_id
    FROM tmp_case_seq
  ) v
  WHERE c.case_id = v.case_id;

  -- Recount variant case_count (process-wide)
  UPDATE pm.variant pv
  SET case_count = x.cnt,
      updated_at = now()
  FROM (
    SELECT variant_id, COUNT(*)::bigint AS cnt
    FROM pm.case
    WHERE process = 'p2p'
      AND variant_id IS NOT NULL
    GROUP BY variant_id
  ) x
  WHERE pv.variant_id = x.variant_id;

  -- 6) Recompute DFG edges (process-wide for simplicity)
  -- For high volume, switch to incremental aggregation by impacted cases
  DELETE FROM pm.edge WHERE process = 'p2p';

  WITH ordered AS (
    SELECT
      case_id,
      ts,
      event_id,
      activity,
      LEAD(activity) OVER (PARTITION BY case_id ORDER BY ts, event_id) AS next_activity,
      LEAD(ts)       OVER (PARTITION BY case_id ORDER BY ts, event_id) AS next_ts
    FROM pm.event
    WHERE process = 'p2p'
  ),
  edges AS (
    SELECT
      'p2p'::text AS process,
      activity AS activity_from,
      next_activity AS activity_to,
      COUNT(*)::bigint AS edge_count,
      percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (next_ts - ts))) AS p50,
      percentile_cont(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (next_ts - ts))) AS p95
    FROM ordered
    WHERE next_activity IS NOT NULL AND next_ts IS NOT NULL
    GROUP BY activity, next_activity
  )
  INSERT INTO pm.edge(process, activity_from, activity_to, edge_count, p50_s, p95_s, updated_at)
  SELECT process, activity_from, activity_to, edge_count, p50::bigint, p95::bigint, now()
  FROM edges;

  -- 7) Recompute deviations for impacted cases (delete+insert)
  DELETE FROM pm.deviation d
  WHERE d.process = 'p2p'
    AND d.case_id IN (SELECT 'p2p:po:' || po_id::text FROM tmp_impacted_po);

  -- Rule: Bill before Receipt (if both exist and bill_ts < receipt_ts)
  INSERT INTO pm.deviation(process, case_id, rule_id, severity, details_json)
  WITH t AS (
    SELECT
      case_id,
      MIN(ts) FILTER (WHERE activity='Goods Received') AS receipt_ts,
      MIN(ts) FILTER (WHERE activity='Vendor Bill Posted') AS bill_ts
    FROM pm.event
    WHERE process='p2p'
      AND case_id IN (SELECT 'p2p:po:' || po_id::text FROM tmp_impacted_po)
    GROUP BY case_id
  )
  SELECT
    'p2p',
    case_id,
    'BILL_BEFORE_RECEIPT',
    'high',
    jsonb_build_object('receipt_ts', receipt_ts, 'bill_ts', bill_ts)
  FROM t
  WHERE receipt_ts IS NOT NULL AND bill_ts IS NOT NULL AND bill_ts < receipt_ts;

  -- Rule: Missing Receipt (bill posted but no receipt)
  INSERT INTO pm.deviation(process, case_id, rule_id, severity, details_json)
  WITH t AS (
    SELECT
      case_id,
      COUNT(*) FILTER (WHERE activity='Goods Received') AS receipt_cnt,
      COUNT(*) FILTER (WHERE activity='Vendor Bill Posted') AS bill_cnt
    FROM pm.event
    WHERE process='p2p'
      AND case_id IN (SELECT 'p2p:po:' || po_id::text FROM tmp_impacted_po)
    GROUP BY case_id
  )
  SELECT
    'p2p',
    case_id,
    'MISSING_RECEIPT',
    'medium',
    jsonb_build_object('bill_cnt', bill_cnt, 'receipt_cnt', receipt_cnt)
  FROM t
  WHERE bill_cnt > 0 AND receipt_cnt = 0;

  -- Rule: Missing Bill (receipt exists but no vendor bill posted)
  INSERT INTO pm.deviation(process, case_id, rule_id, severity, details_json)
  WITH t AS (
    SELECT
      case_id,
      COUNT(*) FILTER (WHERE activity='Goods Received') AS receipt_cnt,
      COUNT(*) FILTER (WHERE activity='Vendor Bill Posted') AS bill_cnt
    FROM pm.event
    WHERE process='p2p'
      AND case_id IN (SELECT 'p2p:po:' || po_id::text FROM tmp_impacted_po)
    GROUP BY case_id
  )
  SELECT
    'p2p',
    case_id,
    'MISSING_VENDOR_BILL',
    'medium',
    jsonb_build_object('bill_cnt', bill_cnt, 'receipt_cnt', receipt_cnt)
  FROM t
  WHERE receipt_cnt > 0 AND bill_cnt = 0;

  -- Count deviations
  SELECT COUNT(*) INTO v_deviations_count
  FROM pm.deviation
  WHERE process = 'p2p'
    AND case_id IN (SELECT 'p2p:po:' || po_id::text FROM tmp_impacted_po);

  -- Finalize job state
  UPDATE pm.job_state
  SET last_run_ts = p_to,
      updated_at = now()
  WHERE job_name = v_job;

  -- Return stats
  RETURN QUERY SELECT v_cases_count, v_events_count, v_deviations_count;
END;
$$;

COMMENT ON FUNCTION pm.run_p2p_etl IS 'Incremental P2P process mining ETL - extracts events from purchase/receiving/billing/payment flow';

COMMIT;
