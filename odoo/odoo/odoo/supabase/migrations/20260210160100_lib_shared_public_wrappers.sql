-- LIB Hybrid Brain - Public RPC Wrappers
-- Purpose: Expose lib_shared functions through public schema (safer search_path)

-- Public wrapper for ingest_events
CREATE OR REPLACE FUNCTION public.lib_shared_ingest_events(batch JSONB)
RETURNS TABLE(inserted_events INT, upserted_entities INT) AS $$
BEGIN
    RETURN QUERY SELECT * FROM lib_shared.ingest_events(batch);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Public wrapper for pull_events
CREATE OR REPLACE FUNCTION public.lib_shared_pull_events(after_id BIGINT, limit_n INT)
RETURNS TABLE(
    id BIGINT,
    event_ulid TEXT,
    device_id TEXT,
    event_type TEXT,
    entity_type TEXT,
    entity_key TEXT,
    payload JSONB,
    vector_clock JSONB,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY SELECT * FROM lib_shared.pull_events(after_id, limit_n);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Public wrapper for webhook registration
CREATE OR REPLACE FUNCTION public.lib_shared_register_webhook(
    p_device_id TEXT,
    p_webhook_url TEXT,
    p_secret TEXT DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    webhook_id BIGINT;
BEGIN
    INSERT INTO lib_shared.device_webhooks (device_id, webhook_url, secret)
    VALUES (p_device_id, p_webhook_url, p_secret)
    ON CONFLICT (device_id) DO UPDATE
    SET webhook_url = EXCLUDED.webhook_url,
        secret = EXCLUDED.secret,
        active = TRUE,
        updated_at = NOW()
    RETURNING id INTO webhook_id;

    RETURN webhook_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Public wrapper for webhook deactivation
CREATE OR REPLACE FUNCTION public.lib_shared_deactivate_webhook(p_device_id TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE lib_shared.device_webhooks
    SET active = FALSE,
        updated_at = NOW()
    WHERE device_id = p_device_id;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Public wrapper to get active webhooks (for Edge Function)
CREATE OR REPLACE FUNCTION public.lib_shared_get_active_webhooks()
RETURNS TABLE(
    device_id TEXT,
    webhook_url TEXT,
    secret TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        w.device_id,
        w.webhook_url,
        w.secret
    FROM lib_shared.device_webhooks w
    WHERE w.active = TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Public wrapper to update webhook notification timestamp
CREATE OR REPLACE FUNCTION public.lib_shared_mark_webhook_notified(p_device_id TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE lib_shared.device_webhooks
    SET last_notified_at = NOW()
    WHERE device_id = p_device_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Revoke direct access to lib_shared schema from public
REVOKE ALL ON SCHEMA lib_shared FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA lib_shared FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA lib_shared FROM PUBLIC;

-- Grant execute on public wrappers (service role will use these)
GRANT EXECUTE ON FUNCTION public.lib_shared_ingest_events TO service_role;
GRANT EXECUTE ON FUNCTION public.lib_shared_pull_events TO service_role;
GRANT EXECUTE ON FUNCTION public.lib_shared_register_webhook TO service_role;
GRANT EXECUTE ON FUNCTION public.lib_shared_deactivate_webhook TO service_role;
GRANT EXECUTE ON FUNCTION public.lib_shared_get_active_webhooks TO service_role;
GRANT EXECUTE ON FUNCTION public.lib_shared_mark_webhook_notified TO service_role;
