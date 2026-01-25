-- Unity Catalog Schema Definitions
-- Deploy with: databricks bundle deploy

-- Create catalog (if permissions allow)
-- CREATE CATALOG IF NOT EXISTS ${catalog};

-- Bronze schema: Raw data layer
CREATE SCHEMA IF NOT EXISTS ${catalog}.bronze
COMMENT 'Raw data layer - stores unmodified source data with full payload';

-- Silver schema: Normalized data layer
CREATE SCHEMA IF NOT EXISTS ${catalog}.silver
COMMENT 'Cleaned and normalized data layer - schema enforcement and type casting';

-- Gold schema: Business marts
CREATE SCHEMA IF NOT EXISTS ${catalog}.gold
COMMENT 'Business-ready data marts and aggregations for analytics';
