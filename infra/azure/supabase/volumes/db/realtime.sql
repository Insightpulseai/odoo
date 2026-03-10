-- =============================================================================
-- Supabase Realtime Schema
-- =============================================================================
-- Creates the _realtime schema used by the Realtime service.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS _realtime;

CREATE OR REPLACE FUNCTION _realtime.subscription_check_filters()
RETURNS trigger AS $$
BEGIN
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
