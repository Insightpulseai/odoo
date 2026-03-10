-- =============================================================================
-- ERD DOT Generator for PostgreSQL
-- =============================================================================
-- Generates a Graphviz DOT format ERD from pg_catalog
--
-- Usage:
--   psql -f scripts/erd_dot.sql -t -A > erd.dot
--   dot -Tpng erd.dot -o erd.png
--   dot -Tsvg erd.dot -o erd.svg
--
-- Customize schemas by modifying the WHERE clause below.
-- =============================================================================

WITH
-- Configuration: specify schemas to include
config AS (
  SELECT ARRAY['public'] AS schemas  -- Add more: ARRAY['public','app','bi']
),
-- Collect all tables in target schemas
tables AS (
  SELECT
    c.oid AS tbl_oid,
    n.nspname AS schema_name,
    c.relname AS table_name,
    CASE
      WHEN n.nspname = 'public' THEN c.relname
      ELSE n.nspname || '_' || c.relname
    END AS node_id
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  CROSS JOIN config
  WHERE c.relkind = 'r'
    AND n.nspname = ANY(config.schemas)
    AND c.relname NOT LIKE 'pg_%'
    AND c.relname NOT LIKE 'sql_%'
),
-- Collect columns for each table
columns AS (
  SELECT
    t.node_id,
    t.table_name,
    a.attname AS column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
    a.attnotnull AS not_null,
    COALESCE(
      (SELECT TRUE FROM pg_index i
       WHERE i.indrelid = t.tbl_oid
         AND i.indisprimary
         AND a.attnum = ANY(i.indkey)),
      FALSE
    ) AS is_pk,
    a.attnum AS col_order
  FROM tables t
  JOIN pg_attribute a ON a.attrelid = t.tbl_oid
  WHERE a.attnum > 0
    AND NOT a.attisdropped
  ORDER BY t.node_id, a.attnum
),
-- Aggregate columns into record labels
table_labels AS (
  SELECT
    node_id,
    table_name,
    '{' || table_name || '|' ||
    string_agg(
      CASE WHEN is_pk THEN '+ ' ELSE '  ' END ||
      column_name || ' : ' || data_type ||
      CASE WHEN not_null THEN ' NOT NULL' ELSE '' END,
      '\l'
      ORDER BY col_order
    ) || '\l}' AS label
  FROM columns
  GROUP BY node_id, table_name
),
-- Collect foreign keys
fks AS (
  SELECT
    t_src.node_id AS src_node,
    t_src.table_name AS src_table,
    t_tgt.node_id AS tgt_node,
    t_tgt.table_name AS tgt_table,
    con.conname AS fk_name,
    a_src.attname AS src_column,
    a_tgt.attname AS tgt_column
  FROM pg_constraint con
  JOIN tables t_src ON t_src.tbl_oid = con.conrelid
  JOIN tables t_tgt ON t_tgt.tbl_oid = con.confrelid
  JOIN pg_attribute a_src ON a_src.attrelid = con.conrelid
    AND a_src.attnum = ANY(con.conkey)
  JOIN pg_attribute a_tgt ON a_tgt.attrelid = con.confrelid
    AND a_tgt.attnum = ANY(con.confkey)
  WHERE con.contype = 'f'
),
-- Build DOT nodes
dot_nodes AS (
  SELECT
    format('  "%s" [label="%s"];', node_id, label) AS dot_line
  FROM table_labels
),
-- Build DOT edges
dot_edges AS (
  SELECT DISTINCT
    format('  "%s" -> "%s" [label="%s", fontsize=8];',
      src_node, tgt_node, src_column) AS dot_line
  FROM fks
)
-- Combine into final DOT output
SELECT
  'digraph ERD {' || E'\n' ||
  '  rankdir=LR;' || E'\n' ||
  '  node [shape=record, fontsize=10, fontname="Helvetica"];' || E'\n' ||
  '  edge [arrowsize=0.8];' || E'\n' ||
  E'\n' ||
  '  // Tables' || E'\n' ||
  COALESCE((SELECT string_agg(dot_line, E'\n') FROM dot_nodes), '') ||
  E'\n\n' ||
  '  // Foreign Keys' || E'\n' ||
  COALESCE((SELECT string_agg(dot_line, E'\n') FROM dot_edges), '') ||
  E'\n' ||
  '}' AS dot_graph;
