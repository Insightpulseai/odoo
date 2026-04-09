# Odoo Server Ops Skill

## Purpose

Manage Odoo server lifecycle via CLI. Covers odoo-bin start/stop, --http-port, --workers, --proxy-mode, --dev flags, config file options, and addons-path management.

## Owner

odoo-cli-operator

## Preconditions

- Odoo CE 19.0 installed (vendor/odoo/ for local, /opt/odoo/ for devcontainer)
- Python 3.11+ virtualenv (pyenv `odoo-18-dev` for local)
- PostgreSQL 16 accessible
- Addons paths configured

## Covered Operations

### Server Lifecycle

- Start server: `odoo-bin --database <db> --addons-path <paths> --http-port <port>`
- Start with dev mode: `odoo-bin --dev=xml,reload,qweb`
- Start with workers: `odoo-bin --workers=<n> --proxy-mode`
- Stop: send SIGTERM to odoo-bin process

### Configuration

- `--config <path>` — use specific config file
- `--save` — save current options to config file
- `--addons-path <path1,path2>` — comma-separated addons directories
- `--http-port <port>` — HTTP port (default: 8069)
- `--workers <n>` — number of worker processes (0 = no workers)
- `--proxy-mode` — enable reverse proxy mode (required behind Azure Front Door)
- `--dev <options>` — development mode (xml, reload, qweb, all)
- `--log-level <level>` — logging level (debug, info, warn, error, critical)
- `--data-dir <path>` — data directory for filestore

### Addons Path Management

- Local dev: `vendor/odoo/addons,addons/ipai`
- Devcontainer: `/opt/odoo/addons,/workspaces/odoo/addons/ipai,/workspaces/odoo/addons/oca`
- Production: managed via config file and Docker environment

## Environment-Specific Paths

| Environment | Binary | Config | Addons Base |
|------------|--------|--------|-------------|
| Local (Mac) | `vendor/odoo/odoo-bin` | N/A (flags) | `vendor/odoo/addons,addons/ipai` |
| Devcontainer | `/opt/odoo/odoo-bin` | `/etc/odoo/odoo.conf` | `/opt/odoo/addons,/workspaces/odoo/addons/*` |
| Production | Docker entrypoint | Container env | Docker volume mounts |

## Disallowed Operations

- Direct production server management (use Azure Container Apps)
- Modifying vendor/odoo/ files
- Running without specifying database
- Using production databases for development

## Verification

- After start: `curl -sf http://localhost:<port>/web/health` returns 200
- After module install: check `ir_module_module` state is `installed`
- After config change: restart and verify via `/web/health`
