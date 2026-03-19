#!/usr/bin/env bash
# Example: Start Odoo for local development
set -euo pipefail

echo "=== Start Odoo dev server ==="
~/.pyenv/versions/odoo-19-dev/bin/python vendor/odoo/odoo-bin \
  --database=odoo_dev \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --http-port=8069 \
  --addons-path=vendor/odoo/addons,addons/ipai \
  --dev=xml,reload,qweb \
  --data-dir=/tmp/odoo-data

# Example: Start with workers (production-like)
# ~/.pyenv/versions/odoo-19-dev/bin/python vendor/odoo/odoo-bin \
#   --database=odoo_dev \
#   --workers=4 --proxy-mode \
#   --http-port=8069
