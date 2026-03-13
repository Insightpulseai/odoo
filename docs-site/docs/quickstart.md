---
title: Quick start
description: Set up the InsightPulse AI development environment from scratch.
---

# Quick start

This guide brings up the full InsightPulse AI stack locally using the devcontainer.

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Docker | 24+ with Compose v2 |
| Git | 2.40+ |
| VS Code | Latest, with Dev Containers extension |

## Clone the repository

```bash
git clone git@github.com:Insightpulseai/odoo.git
cd odoo
```

## Start the devcontainer

Open the repository in VS Code. When prompted, select **Reopen in Container**. The devcontainer installs all dependencies and configures the workspace automatically.

Alternatively, use the CLI:

```bash
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . bash
```

!!! info "Path contract"
    Inside the devcontainer, the workspace mounts at `/workspaces/odoo`. Odoo CE installs at `/opt/odoo`. Configuration lives at `/etc/odoo/odoo.conf`. The database hostname is `db`.

## Bring up the stack

```bash
cd /workspaces/odoo/odoo19
docker compose up -d
```

This starts:

- **Odoo CE 19** on port 8069 (single database: `odoo_dev`, `list_db=False`)
- **PostgreSQL 16** on port 5432 (internal), 5433 (external)

To install base modules on first run:

```bash
docker compose exec -T web odoo -d odoo_dev -i base --stop-after-init
```

## Verify the stack

Run the health check:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health
```

Expected output: `200`.

## Key scripts

Run these before every commit:

```bash
# Check repository structure
./scripts/repo_health.sh

# Validate spec bundles
./scripts/spec_validate.sh

# Run local CI suite
./scripts/ci_local.sh
```

## Install a custom module

```bash
docker compose exec -T web odoo -d odoo_dev -i ipai_workspace_core --stop-after-init
```

## Run tests for a module

```bash
./scripts/ci/run_odoo_tests.sh ipai_finance_ppm
```

!!! warning "Test database isolation"
    Tests use a disposable database (`test_<module_name>`). Never test against `odoo_dev` or `odoo_prod`.

## Next steps

- Read the [architecture overview](architecture/index.md) to understand system topology and authority boundaries.
- Review the [module hierarchy](architecture/module-hierarchy.md) for the target module structure.
- Check [enterprise parity](modules/index.md) status for the current CE + OCA + ipai_* coverage.
