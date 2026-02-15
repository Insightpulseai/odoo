# Archived Legacy Configurations

These are outdated Odoo 18 configurations kept for reference only.

**Date archived:** 2026-02-13

## Contents

- `devcontainer.json.backup` - Old compose-based devcontainer config
- `docker-compose.yml.backup` - Old custom compose file

## Why Archived

The devcontainer has been migrated to:
- Spec Kit base image pattern (Python 3.12-bookworm)
- Docker-outside-of-docker feature for Docker socket access
- Tool bootstrap integration (uv, specify-cli, pnpm)
- Direct reference to SSOT compose file: `docker-compose.yml`

See parent `.devcontainer/devcontainer.json` for current configuration.
