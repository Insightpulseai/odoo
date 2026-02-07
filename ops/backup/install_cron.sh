#!/usr/bin/env bash
# install_cron.sh — Install daily PostgreSQL backup cron job
# Usage: ENV_FILE=/etc/ipai/backup.env REPO_ROOT=/opt/odoo-ce/repo ./ops/backup/install_cron.sh
set -euo pipefail

: "${ENV_FILE:?ENV_FILE required (e.g. /etc/ipai/backup.env)}"
: "${REPO_ROOT:?REPO_ROOT required (absolute path to repo root)}"

LINE="15 1 * * * . ${ENV_FILE} && ${REPO_ROOT}/ops/backup/pg_backup_to_s3.sh >> /var/log/ipai_pg_backup.log 2>&1"

( crontab -l 2>/dev/null | grep -v "ipai_pg_backup_to_s3" || true
  echo "# ipai_pg_backup_to_s3"
  echo "${LINE}"
) | crontab -

echo "Installed cron entry:"
crontab -l | tail -n 3
