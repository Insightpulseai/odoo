# OCA Port CLI - Complete Reference

Source: https://github.com/OCA/oca-port
PyPI: https://pypi.org/project/oca-port/

## Installation

```bash
pip3 install oca-port
# Latest as of 2026-01: v0.18+
```

## Basic Command Syntax

```bash
oca-port <source_branch_or_path> <target_branch_or_path> <addon_path> [OPTIONS]
```

## Core Usage Patterns

### Check if addon can be migrated (dry-run)
```bash
oca-port origin/16.0 origin/18.0 <module_path> --verbose --dry-run
```

### Effective migration (creates branch automatically)
```bash
oca-port origin/16.0 origin/18.0 <module_path> --verbose
```

### Non-standard branches (requires explicit version flags)
```bash
oca-port origin/main origin/18.0-mig \
  --source-version=16.0 \
  --target-version=18.0 \
  --upstream-org=camptocamp \
  ./odoo/local-src/MY_MODULE \
  --verbose \
  --destination sebalix/18.0-mig-MY_MODULE
```

### Auto-fetch remote branches
```bash
oca-port origin/16.0 origin/18.0 <module_path> --fetch
```

## All Options

| Option | Description |
|--------|-------------|
| `--verbose` | Display detailed output |
| `--dry-run` | Preview changes without applying them |
| `--fetch` | Automatically fetch remote branches before processing |
| `--source-version` | Override source Odoo version (required for non-standard branch names) |
| `--target-version` | Override target Odoo version (required for non-standard branch names) |
| `--upstream-org` | GitHub organization for API requests (default: OCA) |
| `--destination` | Destination branch name (default: auto-generated) |
| `--move-to` | Move/rename module — uses git-filter-repo to preserve history |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub API token for PR lookups. Falls back to `gh` CLI if not set |

## What oca-port Does Internally

1. Compares two unrelated git histories for a given module
2. Produces a report of commits/PRs not yet ported
3. Groups missing changes by Pull Request
4. If new migration: follows OCA migration guide interactively
5. If existing migration: retrieves commits not fully ported and proposes porting them
6. When multiple PRs to port: asks whether to base next PR on previous (cumulate in one branch)
7. Creates draft PR against upstream if requested

## oca-port-pr Tool

```bash
# Blacklist PRs that should NOT be ported
oca-port-pr blacklist OCA/wms#250,OCA/wms#251 16.0 shopfloor

# With reason
oca-port-pr blacklist OCA/wms#250,OCA/wms#251 16.0 shopfloor \
  --reason "Refactored in 16.0, not needed anymore"
```

## Python API (programmatic use)

```python
from oca_port import App

app = App(
    source="origin/16.0",
    target="origin/18.0",
    addon_path="./my_module",
    upstream_org="OCA",
    repo_path="/path/to/repo",
    output="github",          # or "cli"
    fetch=True,
    github_token="ghp_..."
)
app.run()
```

## Integration with odoo-module-migrator (v0.18+)

As of version 0.18, oca-port automatically calls odoo-module-migrator when
migrating a module to apply automated code transformations.

## Branch Naming Convention

Auto-generated branch: `{target_version}-mig-{module_name}`

Example: `19.0-mig-server_environment`
