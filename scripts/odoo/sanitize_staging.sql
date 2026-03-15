-- ============================================================================
-- Staging PII Sanitization — OdooSH Equivalent
-- ============================================================================
-- Run after restoring prod dump to staging.
-- Masks PII, disables mail, suppresses crons.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Mask partner PII
-- ---------------------------------------------------------------------------
UPDATE res_partner
SET email = 'staging+' || id || '@insightpulseai.com'
WHERE email IS NOT NULL AND email != '';

UPDATE res_partner
SET phone = '+63900' || LPAD(id::text, 7, '0')
WHERE phone IS NOT NULL AND phone != '';

UPDATE res_partner
SET mobile = NULL
WHERE mobile IS NOT NULL;

UPDATE res_partner
SET street = 'Staging Address ' || id,
    street2 = NULL
WHERE street IS NOT NULL;

-- Keep company names intact for readability
-- UPDATE res_partner SET name = 'Partner ' || id WHERE is_company = false;

-- ---------------------------------------------------------------------------
-- 2. Reset user passwords (except admin uid=2)
-- ---------------------------------------------------------------------------
UPDATE res_users
SET password = 'staging_changeme'
WHERE id > 2;

-- ---------------------------------------------------------------------------
-- 3. Disable ALL outbound mail servers
-- ---------------------------------------------------------------------------
UPDATE ir_mail_server
SET active = false;

-- ---------------------------------------------------------------------------
-- 4. Disable non-essential cron jobs
-- ---------------------------------------------------------------------------
UPDATE ir_cron
SET active = false
WHERE id NOT IN (
    -- Keep only essential crons:
    SELECT id FROM ir_cron
    WHERE cron_name IN (
        'base: GC unlinked attachments',
        'base: Auto-vacuum internal data',
        'base: Run autovacuum on registry',
        'mail: garbage collect notifications'
    )
);

-- ---------------------------------------------------------------------------
-- 5. Clear mail queue (prevent accidental sends)
-- ---------------------------------------------------------------------------
DELETE FROM mail_mail WHERE state IN ('outgoing', 'exception');

-- ---------------------------------------------------------------------------
-- 6. Mark as staging environment
-- ---------------------------------------------------------------------------
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('ipai.environment', 'staging', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = 'staging', write_date = NOW();

-- Set ribbon text
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('ribbon.name', 'STAGING', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = 'STAGING', write_date = NOW();

-- ---------------------------------------------------------------------------
-- 7. Report sanitization counts
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    partner_count INTEGER;
    user_count INTEGER;
    mail_count INTEGER;
    cron_count INTEGER;
BEGIN
    SELECT count(*) INTO partner_count FROM res_partner WHERE email LIKE 'staging+%';
    SELECT count(*) INTO user_count FROM res_users WHERE password = 'staging_changeme';
    SELECT count(*) INTO mail_count FROM ir_mail_server WHERE active = false;
    SELECT count(*) INTO cron_count FROM ir_cron WHERE active = false;

    RAISE NOTICE 'Sanitization complete:';
    RAISE NOTICE '  Partners masked: %', partner_count;
    RAISE NOTICE '  Passwords reset: %', user_count;
    RAISE NOTICE '  Mail servers disabled: %', mail_count;
    RAISE NOTICE '  Cron jobs disabled: %', cron_count;
END $$;
