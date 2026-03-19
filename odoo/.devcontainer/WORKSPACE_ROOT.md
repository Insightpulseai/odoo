# DevContainer Canonical Root

The devcontainer workspace root is **`/workspaces/odoo`** (= repo root bind-mounted).

All Odoo addons in the devcontainer are loaded from paths under `/workspaces/odoo/`:
- IPAI: `/workspaces/odoo/addons/ipai/`
- OCA:  `/workspaces/odoo/addons/oca/<repo>/`

**Do not** reference `/opt/odoo` or `/mnt/oca` in dev — those paths apply to production
or the base compose layer only. Hot-reload (`--dev=all`) is deterministic against
`/workspaces/odoo/addons/...`.
