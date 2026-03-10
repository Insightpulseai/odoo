-- =============================================================================
-- Supabase JWT Extension Setup
-- =============================================================================
-- Ensures pgjwt extension is available for JWT operations within PostgreSQL.
-- The supabase/postgres image ships with pgjwt pre-installed.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgjwt WITH SCHEMA extensions;
