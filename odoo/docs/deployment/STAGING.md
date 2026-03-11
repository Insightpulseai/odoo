# Staging Environment Guide

**Staging** is a safe, isolated rehearsal environment for testing module upgrades, data migrations, and critical flows before deploying to Production.

## Architecture

*   **URL**: `http://localhost:9079` (Local staging mode)
*   **Database**: `odoo_stage` (Cloned from `prod` backup + sanitized)
*   **Container**: `odoo-stage` (Mirrors `odoo-dev` configuration)
*   **Isolation**: Enforced via `dbfilter=^odoo_stage$`

## Workflow

### 1. Reset Staging (Refresh Data)
Destroys current staging DB and refreshes it from the latest Production Backup (or local dev backup if prod is inaccessible). **Data is sanitized.**

```bash
./scripts/staging_restore_and_sanitize.sh
```

### 2. Start Staging
Starts the isolated staging container on port 9079.

```bash
./scripts/staging_up.sh
```

### 3. Stop Staging
Stops the staging container to free up resources.

```bash
./scripts/staging_down.sh
```

### 4. Verify
```bash
curl -I http://localhost:9079/web/login
```

## Sanitization Policy
The restore script automatically:
*   Deactivates cron jobs (ir.cron).
*   Deactivates outgoing mail servers.
*   Anonymizes customer emails and phones (e.g., `user@example.com` -> `user_stage_123@example.com`).
*   Changes admin password to a known staging secret.
