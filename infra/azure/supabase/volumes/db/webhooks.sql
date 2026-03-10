-- =============================================================================
-- Supabase Database Webhooks
-- =============================================================================
-- Sets up the supabase_functions schema and net extension for database webhooks.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS supabase_functions;

CREATE EXTENSION IF NOT EXISTS http WITH SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS pg_net WITH SCHEMA extensions;

-- Webhook dispatcher function
CREATE OR REPLACE FUNCTION supabase_functions.http_request()
RETURNS trigger AS $$
DECLARE
  request_id bigint;
  payload jsonb;
  url text := TG_ARGV[0]::text;
  method text := TG_ARGV[1]::text;
  headers jsonb DEFAULT '{}'::jsonb;
  params jsonb DEFAULT '{}'::jsonb;
  timeout_ms integer DEFAULT 1000;
BEGIN
  IF url IS NULL OR url = 'null' THEN
    RAISE EXCEPTION 'url argument is missing';
  END IF;

  IF method IS NULL OR method = 'null' THEN
    RAISE EXCEPTION 'method argument is missing';
  END IF;

  IF TG_ARGV[2] IS NOT NULL THEN
    headers = TG_ARGV[2]::jsonb;
  END IF;

  IF TG_ARGV[3] IS NOT NULL THEN
    params = TG_ARGV[3]::jsonb;
  END IF;

  IF TG_ARGV[4] IS NOT NULL THEN
    timeout_ms = TG_ARGV[4]::integer;
  END IF;

  payload = jsonb_build_object(
    'old_record', OLD,
    'record', NEW,
    'type', TG_OP,
    'table', TG_TABLE_NAME,
    'schema', TG_TABLE_SCHEMA
  );

  SELECT http_post INTO request_id FROM net.http_post(
    url,
    payload,
    params,
    headers,
    timeout_ms
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
