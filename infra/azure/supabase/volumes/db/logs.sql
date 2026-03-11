-- =============================================================================
-- Supabase Analytics Schema
-- =============================================================================
-- Creates the _analytics schema used by the Logflare analytics service.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS _analytics;

GRANT ALL ON SCHEMA _analytics TO supabase_admin;
