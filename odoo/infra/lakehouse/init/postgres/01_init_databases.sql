-- =============================================================================
-- LAKEHOUSE POSTGRESQL INITIALIZATION
-- =============================================================================
-- Creates databases and extensions for the lakehouse stack
-- =============================================================================

-- Create databases for each service
CREATE DATABASE mlflow;
CREATE DATABASE n8n;

-- Enable extensions in main database
\c lakehouse;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable vector extension if available (for RAG)
-- Note: Requires postgres:15 with pgvector installed
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS runtime;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA rag TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA gold TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA runtime TO postgres;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Lakehouse databases initialized';
END;
$$;
