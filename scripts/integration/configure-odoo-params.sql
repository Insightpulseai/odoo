-- Configure Odoo system parameters for Supabase integration
-- Run this SQL directly if shell script is not available
--
-- Replace the placeholders before running:
--   {{WEBHOOK_URL}} - Supabase Edge Function URL
--   {{WEBHOOK_SECRET}} - HMAC signing secret (shared with Edge Function)

-- Create or update webhook URL parameter
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('ipai.webhook.url', '{{WEBHOOK_URL}}', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    write_date = NOW();

-- Create or update webhook secret parameter
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('ipai.webhook.secret', '{{WEBHOOK_SECRET}}', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    write_date = NOW();

-- Verify configuration
SELECT
    key,
    CASE
        WHEN key = 'ipai.webhook.secret' THEN LEFT(value, 8) || '****'
        ELSE value
    END as value_preview
FROM ir_config_parameter
WHERE key LIKE 'ipai.webhook.%';
