#!/usr/bin/env bash
# Discover service names from docker-compose.yml
# Usage: source ./scripts/compose_vars.sh

set -euo pipefail

# Discover app service (odoo/app/odoo-core)
APP_SVC="${APP_SVC:-$(docker compose config --services | awk '/^(app|odoo|odoo-core)$/ {print; exit}')}"

# Discover database service (postgres/db/odoo-db)
DB_SVC="${DB_SVC:-$(docker compose config --services | awk '/^(postgres|db|odoo-db)$/ {print; exit}')}"

# Fallback: use first service if no match
[[ -n "${APP_SVC:-}" ]] || APP_SVC="$(docker compose config --services | head -1)"
[[ -n "${DB_SVC:-}" ]] || DB_SVC="$(docker compose config --services | awk 'NR==2{print}')"

export APP_SVC DB_SVC

# Silent export for sourcing
if [[ "${1:-}" != "--quiet" ]]; then
    echo "APP_SVC=$APP_SVC"
    echo "DB_SVC=$DB_SVC"
fi
