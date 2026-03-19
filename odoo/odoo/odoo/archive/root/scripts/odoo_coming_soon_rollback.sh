#!/usr/bin/env bash
# =============================================================================
# Rollback: uninstall ipai_website_coming_soon and restore default homepage.
#
# Strategy: use Odoo shell to uninstall the module, which triggers the
# uninstall_hook (clears homepage_id). Falls back to git revert advice.
# =============================================================================
set -euo pipefail

MODULE="ipai_website_coming_soon"

# ---------------------------------------------------------------------------
# Docker mode
# ---------------------------------------------------------------------------
if command -v docker &>/dev/null && docker compose ps --services 2>/dev/null | grep -q "web\|odoo"; then
    SERVICE=$(docker compose ps --services 2>/dev/null | grep -E "^(web|odoo-core|odoo)$" | head -1)
    DB=$(docker compose exec -T "$SERVICE" grep -oP '(?<=db_name\s=\s)\S+' /etc/odoo/odoo.conf 2>/dev/null || echo "odoo")

    echo "Uninstalling $MODULE on service=$SERVICE db=$DB ..."
    docker compose exec -T "$SERVICE" odoo shell -d "$DB" --stop-after-init <<PYEOF
module = env['ir.module.module'].search([('name', '=', '$MODULE'), ('state', '=', 'installed')])
if module:
    module.button_immediate_uninstall()
    env.cr.commit()
    print('OK: $MODULE uninstalled.')
else:
    print('SKIP: $MODULE not installed.')
PYEOF
    docker compose restart "$SERVICE"
    echo "Done."
    exit 0
fi

# ---------------------------------------------------------------------------
# Fallback: manual guidance
# ---------------------------------------------------------------------------
echo "Rollback options:"
echo "  1) Git revert:  git revert <commit-sha> && git push"
echo "  2) Odoo shell:  odoo shell -d \$DB --stop-after-init"
echo "     >>> env['ir.module.module'].search([('name','=','$MODULE')]).button_immediate_uninstall()"
echo "  3) Remove module directory and restart Odoo (module becomes uninstallable)."
