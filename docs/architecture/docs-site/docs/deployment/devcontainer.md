# Devcontainer

All Odoo development runs inside the VS Code devcontainer defined in `.devcontainer/`. Never run Odoo processes on the host machine.

## Path contract

| Path | Purpose |
|------|---------|
| `/workspaces/odoo` | Workspace root (repo checkout) |
| `/opt/odoo` | Odoo CE installation (read-only) |
| `/opt/odoo/odoo-bin` | Odoo binary |
| `/etc/odoo/odoo.conf` | Odoo server configuration |
| `db` | PostgreSQL hostname (Docker service name) |
| `/workspaces/odoo/addons` | Custom addons (`ipai_*`, project-specific) |
| `/workspaces/odoo/oca_addons` | OCA addon repos (git submodules or clones) |
| `/workspaces/odoo/scripts/odoo` | Authoritative execution scripts |

## Rules

!!! danger "Hard rules"
    1. **Never run Odoo on the host machine.** All execution happens inside the devcontainer.
    2. **Never modify `/opt/odoo`.** It is the pinned Odoo CE installation and is read-only.
    3. **Container user is `vscode`**, not `root`. Do not escalate privileges unless absolutely required.

## Execution scripts

Scripts in `scripts/odoo/*.sh` are the **authoritative** execution interface. All tooling and automation references these scripts rather than invoking `odoo-bin` directly.

```bash
# Install a module
scripts/odoo/install_module.sh ipai_finance_ppm

# Update a module
scripts/odoo/update_module.sh ipai_finance_ppm

# Run the Odoo server
scripts/odoo/start.sh
```

!!! note "Script authority"
    Skills, agents, and CI pipelines reference `scripts/odoo/*.sh`. Never replace these scripts with inline commands.

## Test databases

Every test run uses a **disposable database** named `test_<module_name>`:

```bash
# Run tests for a module
scripts/odoo/test_module.sh ipai_finance_ppm
# Creates and uses database: test_ipai_finance_ppm
```

!!! warning "Test database policy"
    - **Never** use `odoo_dev` or `odoo` for tests.
    - Each test run creates a fresh `test_<module>` database.
    - Disposable databases are dropped after the test completes.

## Test failure classification

Classify every test failure before reporting:

| Classification | Meaning | Action |
|----------------|---------|--------|
| `passes locally` | Init and tests clean | Mark as compatible |
| `init only` | Installs but has no tests | Note; cannot claim tested |
| `env issue` | Fails due to test env (no-http, ordering, missing demo data) | Re-run with adjusted env or document limitation |
| `migration gap` | Fails due to incomplete 19.0 migration in OCA/core | Report upstream; do not patch locally |
| `real defect` | Functional failure in module logic | Fix or report with traceback |

## Opening the devcontainer

1. Open the repository in VS Code.
2. When prompted, select **Reopen in Container**.
3. VS Code builds the container and mounts the workspace at `/workspaces/odoo`.

Alternatively, from the command palette:

```
Dev Containers: Reopen in Container
```
