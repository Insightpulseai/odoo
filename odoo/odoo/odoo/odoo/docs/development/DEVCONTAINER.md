# Devcontainer

Devcontainer reuses the repo's canonical `docker-compose.yml` and adds minimal overrides in:
- `.devcontainer/docker-compose.devcontainer.yml`

## Design Intent

- Same services as local compose (no drift)
- Standardized tooling + workspace mount
- No requirement for Mac-only tooling (Colima not needed)
- Works with VS Code, GitHub Codespaces, and Claude Code

## How It Works

The devcontainer is configured in `.devcontainer/devcontainer.json`:

1. Extends `../docker-compose.yml` with `.devcontainer/docker-compose.devcontainer.yml`
2. Targets the `odoo` service
3. Mounts the repo at `/workspaces/odoo`
4. Installs dev tools: Python, Node LTS, Git, Docker-outside-of-Docker
5. Forwards ports: Odoo (8069, 8072), PostgreSQL (5432)

## Files

| File | Purpose |
|------|---------|
| `.devcontainer/devcontainer.json` | Devcontainer configuration |
| `.devcontainer/docker-compose.devcontainer.yml` | Dev-specific compose overrides |
| `.devcontainer/devcontainer.env.example` | Env var template |
| `.devcontainer/scripts/post-create.sh` | One-time setup after container creation |
| `.devcontainer/scripts/post-start.sh` | Runs each time the container starts |
