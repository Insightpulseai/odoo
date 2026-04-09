# Skill: VS Code Dev Containers

## Metadata

| Field | Value |
|-------|-------|
| **id** | `vscode-devcontainers` |
| **domain** | `devops` |
| **source** | https://code.visualstudio.com/docs/devcontainers/create-dev-container |
| **extracted** | 2026-03-15 |
| **applies_to** | odoo, infra, agents |
| **tags** | devcontainer, docker, vscode, docker-compose, development-environment |

---

## What It Is

Dev Containers use Docker to provide reproducible development environments inside VS Code. Configuration lives in `.devcontainer/devcontainer.json`. The entire team gets the same environment — no "works on my machine."

## devcontainer.json Schema

### Minimal (Image-Based)

```json
{
  "image": "mcr.microsoft.com/devcontainers/python:0-3.12"
}
```

### Docker Compose (Multi-Container)

```json
{
  "name": "Odoo 18 Dev",
  "dockerComposeFile": ["../docker-compose.yml", "docker-compose.devcontainer.yml"],
  "service": "devcontainer",
  "workspaceFolder": "/workspaces/odoo",
  "shutdownAction": "stopCompose"
}
```

### Dockerfile (Custom Build)

```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": "..",
    "args": { "VARIANT": "3.12" }
  }
}
```

## Key Properties

| Property | Purpose | Example |
|----------|---------|---------|
| `image` | Base container image | `mcr.microsoft.com/devcontainers/python:0-3.12` |
| `build.dockerfile` | Custom Dockerfile path | `Dockerfile` |
| `dockerComposeFile` | Docker Compose file(s) | `["../docker-compose.yml", "devcontainer.yml"]` |
| `service` | Which compose service to attach to | `devcontainer` |
| `workspaceFolder` | Where code mounts inside container | `/workspaces/odoo` |
| `forwardPorts` | Ports to expose to localhost | `[8069, 5432]` |
| `remoteUser` | Non-root user inside container | `odoo` |
| `postCreateCommand` | Run once after container creation | `bash scripts/post-create.sh` |
| `postStartCommand` | Run every time container starts | `bash scripts/post-start.sh` |
| `customizations.vscode.extensions` | Auto-install extensions | `["ms-python.python"]` |
| `customizations.vscode.settings` | VS Code settings override | `{"python.defaultInterpreterPath": "/usr/bin/python3"}` |
| `features` | Modular tool installation | `{"ghcr.io/devcontainers/features/azure-cli:1": {}}` |
| `shutdownAction` | What happens when VS Code closes | `stopCompose` or `none` |

## Lifecycle Scripts

| Hook | When | Use Case |
|------|------|----------|
| `initializeCommand` | Before container starts (runs on host) | Validate prerequisites |
| `onCreateCommand` | After container created, before user attached | Install system packages |
| `postCreateCommand` | After container created + user attached | Install project deps, run migrations |
| `postStartCommand` | Every container start | Start background services |
| `postAttachCommand` | Every time VS Code attaches | Set up shell, show welcome |

### Interactive Shell for NVM/pyenv

```json
"postCreateCommand": "bash -i -c 'nvm install --lts'"
```

The `-i` flag sources `.bashrc`/`.profile` for tools that modify PATH.

## Features (Modular Tools)

```json
"features": {
  "ghcr.io/devcontainers/features/azure-cli:1": { "version": "latest" },
  "ghcr.io/devcontainers/features/github-cli:1": {},
  "ghcr.io/devcontainers/features/node:1": { "version": "20" },
  "ghcr.io/devcontainers/features/python:1": { "version": "3.12" },
  "ghcr.io/devcontainers/features/docker-in-docker:2": {}
}
```

Features are composable — add tools without modifying the Dockerfile.

## Docker Compose Integration

### Extend Without Modifying Base Compose

```yaml
# .devcontainer/docker-compose.devcontainer.yml
version: '3'
services:
  devcontainer:
    volumes:
      - .:/workspaces/odoo:cached
    cap_add:
      - SYS_PTRACE
    security_opt:
      - seccomp:unconfined
    command: /bin/sh -c "while sleep 1000; do :; done"
```

Reference both files:

```json
"dockerComposeFile": ["../docker-compose.yml", "docker-compose.devcontainer.yml"]
```

### Service Networking

Services in the same compose file share a network. Access `db` service from devcontainer via hostname `db`.

## IPAI Devcontainer Implementation

### Current Setup

| File | Path | Purpose |
|------|------|---------|
| `devcontainer.json` | `odoo/.devcontainer/devcontainer.json` | Main config |
| `docker-compose.devcontainer.yml` | `odoo/.devcontainer/docker-compose.devcontainer.yml` | Devcontainer + db sidecar |
| `post-create.sh` | `odoo/.devcontainer/post-create.sh` | Install deps, configure env |
| `Dockerfile` (if custom) | `odoo/.devcontainer/Dockerfile` | Custom image build |

### IPAI Two-Compose Doctrine

| File | Role | Services |
|------|------|----------|
| `docker-compose.yml` | Canonical Odoo runtime | `odoo` + `db` + `redis` |
| `.devcontainer/docker-compose.devcontainer.yml` | Editor/tooling shell | `devcontainer` + db sidecar |

**Rule**: Runtime config (`config/dev/odoo.conf`) references runtime paths, not devcontainer paths.

### IPAI Path Model

| Path | Inside Container | Purpose |
|------|-----------------|---------|
| `/workspaces/odoo` | Workspace root (repo checkout) | Source code |
| `/opt/odoo` | Odoo CE installation | Read-only upstream |
| `/opt/odoo/odoo-bin` | Odoo binary | Execution |
| `/etc/odoo/odoo.conf` | Config file | Server configuration |
| `db` | PostgreSQL hostname | Docker service name |

### Recommended Extensions

```json
"customizations": {
  "vscode": {
    "extensions": [
      "ms-python.python",
      "ms-python.vscode-pylance",
      "dbaeumer.vscode-eslint",
      "redhat.vscode-xml",
      "odoo-ide.odoo-ide",
      "ms-azuretools.vscode-docker"
    ]
  }
}
```

### Recommended Settings

```json
"customizations": {
  "vscode": {
    "settings": {
      "python.defaultInterpreterPath": "/usr/bin/python3",
      "python.analysis.typeCheckingMode": "basic",
      "editor.formatOnSave": true,
      "[python]": { "editor.defaultFormatter": "ms-python.python" },
      "[xml]": { "editor.defaultFormatter": "redhat.vscode-xml" }
    }
  }
}
```

## Best Practices

| Practice | Why |
|----------|-----|
| Use `remoteUser` (non-root) | Avoid permission issues with bind mounts |
| Use `features` over Dockerfile `RUN` | Composable, cacheable, community-maintained |
| Use `postCreateCommand` for deps | Runs once, survives rebuilds |
| Use `postStartCommand` for services | Runs every start, idempotent |
| Forward only needed ports | `[8069, 5432]` not `[8069, 5432, 8071, 8072]` |
| Cache pip/npm in named volumes | Faster rebuilds |
| Include `.devcontainer` in git | Team gets identical environment |
| Use `shutdownAction: stopCompose` | Clean up resources on close |
| Never modify `/opt/odoo` | Upstream mirror — create `ipai_*` overrides instead |

## Sharing

Add to README for one-click setup:

```markdown
[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Insightpulseai/odoo)
```

## Related Skills

- [odoo18-accounting-map](../../odoo/odoo18-accounting-map/SKILL.md) — Accounting features to configure in dev
- [n8n-odoo-supabase-etl](../../integration/n8n-odoo-supabase-etl/SKILL.md) — Docker Compose patterns
