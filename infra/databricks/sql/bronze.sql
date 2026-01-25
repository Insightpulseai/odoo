-- Bronze Layer Tables
-- Raw data with full JSON payloads and ETL metadata

-- Notion raw pages (all database types)
CREATE TABLE IF NOT EXISTS ${catalog}.bronze.notion_raw_pages (
    page_id STRING NOT NULL COMMENT 'Notion page UUID',
    source_table STRING NOT NULL COMMENT 'Source database type (programs, projects, etc.)',
    raw_json STRING NOT NULL COMMENT 'Full JSON payload from Notion API',
    ingested_at TIMESTAMP NOT NULL COMMENT 'UTC timestamp of ingestion',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp'
)
USING DELTA
COMMENT 'Raw Notion page data from all databases'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Azure Resource Graph raw results
CREATE TABLE IF NOT EXISTS ${catalog}.bronze.azure_rg_raw (
    recommendation_id STRING NOT NULL COMMENT 'Azure resource ID',
    raw_json STRING NOT NULL COMMENT 'Full JSON payload from Resource Graph',
    ingested_at TIMESTAMP NOT NULL COMMENT 'UTC timestamp of ingestion',
    _etl_loaded_at TIMESTAMP NOT NULL COMMENT 'ETL load timestamp'
)
USING DELTA
COMMENT 'Raw Azure Resource Graph query results'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Sync watermarks for incremental loads
CREATE TABLE IF NOT EXISTS ${catalog}.bronze.sync_watermarks (
    source STRING NOT NULL COMMENT 'Data source identifier',
    last_sync STRING NOT NULL COMMENT 'ISO timestamp of last successful sync',
    updated_at TIMESTAMP NOT NULL COMMENT 'Watermark update timestamp'
)
USING DELTA
COMMENT 'Watermark tracking for incremental data loads'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true'
);
