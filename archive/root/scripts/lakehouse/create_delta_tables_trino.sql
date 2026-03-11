-- =============================================================================
-- Delta Lake Table DDL for Trino
-- =============================================================================
-- Run this in Trino to create the lakehouse tables.
-- Assumes Delta connector configured with MinIO backend.
--
-- Usage:
--   docker exec -it lakehouse-trino trino < scripts/lakehouse/create_delta_tables_trino.sql
--
-- Or via Trino CLI:
--   trino --server http://localhost:8082 --file scripts/lakehouse/create_delta_tables_trino.sql
-- =============================================================================

-- Create schemas
CREATE SCHEMA IF NOT EXISTS delta.bronze;
CREATE SCHEMA IF NOT EXISTS delta.silver;
CREATE SCHEMA IF NOT EXISTS delta.gold;

-- =============================================================================
-- BRONZE: Raw crawled pages
-- =============================================================================
CREATE TABLE IF NOT EXISTS delta.bronze.raw_pages (
  tenant_id uuid,
  source varchar,
  canonical_url varchar,
  resolved_url varchar,
  http_status integer,
  content_hash varchar,
  content_type varchar,
  raw_object_path varchar,
  raw_text varchar,
  headers varchar,
  crawled_at timestamp,
  crawled_date date
)
WITH (
  location = 's3a://lakehouse/bronze/raw_pages/',
  partitioned_by = ARRAY['source', 'crawled_date']
);

-- =============================================================================
-- SILVER: Normalized documents
-- =============================================================================
CREATE TABLE IF NOT EXISTS delta.silver.normalized_docs (
  tenant_id uuid,
  source varchar,
  canonical_url varchar,
  title varchar,
  content_hash varchar,
  content_md varchar,
  content_text varchar,
  language varchar,
  product varchar,
  version varchar,
  version_at timestamp,
  metadata varchar,
  normalized_at timestamp,
  normalized_date date
)
WITH (
  location = 's3a://lakehouse/silver/normalized_docs/',
  partitioned_by = ARRAY['source', 'normalized_date']
);

-- =============================================================================
-- GOLD: Semantic chunks
-- =============================================================================
CREATE TABLE IF NOT EXISTS delta.gold.chunks (
  tenant_id uuid,
  source varchar,
  document_id uuid,
  document_version_id uuid,
  chunk_id uuid,
  ord integer,
  heading varchar,
  content varchar,
  tokens integer,
  char_start integer,
  char_end integer,
  metadata varchar,
  created_at timestamp,
  chunk_date date
)
WITH (
  location = 's3a://lakehouse/gold/chunks/',
  partitioned_by = ARRAY['source', 'chunk_date']
);

-- =============================================================================
-- GOLD: Vector embeddings
-- =============================================================================
CREATE TABLE IF NOT EXISTS delta.gold.embeddings (
  tenant_id uuid,
  embedding_id uuid,
  chunk_id uuid,
  model varchar,
  model_version varchar,
  dims integer,
  v array(double),
  norm double,
  created_at timestamp,
  embed_date date
)
WITH (
  location = 's3a://lakehouse/gold/embeddings/',
  partitioned_by = ARRAY['model', 'embed_date']
);

-- =============================================================================
-- Verification queries
-- =============================================================================
-- After running, verify tables exist:
-- SHOW TABLES IN delta.bronze;
-- SHOW TABLES IN delta.silver;
-- SHOW TABLES IN delta.gold;
--
-- Check schema:
-- DESCRIBE delta.gold.chunks;
-- DESCRIBE delta.gold.embeddings;
