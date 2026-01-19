#!/usr/bin/env bash
set -e

# Configuration
STAGE_DB="odoo_stage"
SOURCE_DB="odoo" # Or odoo_dev if prod backup not available locally
DB_HOST="db"
DB_USER="odoo"

echo "⚠️  WARNING: This will DESTROY all data in '$STAGE_DB'."
echo "Press Ctrl+C to cancel, or wait 3 seconds..."
sleep 3

export DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock"
cd sandbox/dev

echo "1. Terminating connections..."
docker compose exec -T db psql -U $DB_USER -d postgres -c "
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$STAGE_DB' AND pid <> pg_backend_pid();
"

echo "2. Dropping '$STAGE_DB'..."
docker compose exec -T db psql -U $DB_USER -d postgres -c "
DROP DATABASE IF EXISTS $STAGE_DB;
"

echo "2. Recreating '$STAGE_DB' from template '$SOURCE_DB'..."
# NOTE: In a real scenario, we would stream a pg_dump from prod.
# Here we clone the local dev DB as a proxy for the 'prod backup'.
docker compose exec -T db psql -U $DB_USER -d postgres -c "
CREATE DATABASE $STAGE_DB TEMPLATE $SOURCE_DB;
"

echo "3. Applying Sanitization..."
docker compose exec -T db psql -U $DB_USER -d $STAGE_DB -c "
-- Disable Crons
UPDATE ir_cron SET active=False;

-- Disable Outgoing Mail
UPDATE ir_mail_server SET active=False;

-- Anonymize Emails (Simple Masking)
UPDATE res_partner SET email = 'stage_' || id || '@example.com' WHERE email IS NOT NULL;
UPDATE res_users SET login = 'stage_' || id || '@example.com' WHERE login IS NOT NULL AND login != 'admin';

-- Set Staging Banner (if possible, commonly done via web_environment_ribbon)
-- INSERT INTO ir_config_parameter (key, value) VALUES ('ribbon.name', 'STAGING') ON CONFLICT (key) DO UPDATE SET value = 'STAGING';
"

echo "✓ Staging DB restored and sanitized."
