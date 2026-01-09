# VSCode/Cursor/Claude Code Workspace Configuration

## Canonical Workspace Name

**`ipai_workspace`** - InsightPulseAI mono workspace (odoo-ce)

## Opening the Workspace

### VSCode/Cursor
```bash
code .vscode/ipai_workspace.code-workspace
# or
cursor .vscode/ipai_workspace.code-workspace
```

### Claude Code
Claude Code will automatically detect and use the workspace configuration.

## Quick Tasks (Ctrl+Shift+P → "Tasks: Run Task")

| Task | Purpose |
|------|---------|
| `odoo:compose up (prod file)` | Start Odoo stack with docker-compose.prod.yml |
| `odoo:compose ps` | Check running containers |
| `odoo:logs (tail)` | View last 200 lines of Odoo logs |
| `aiux:verify install` | Verify AIUX module installation |
| `aiux:verify assets` | Check AIUX assets (CSS/JS) |
| `odoo:rebuild assets (fix 500)` | Fix 500 error on /web/assets/* |
| `odoo:check assets endpoint` | Test /web endpoint and list assets |

## Local Development Workflow

### 1. Start Stack
```bash
docker compose -f docker-compose.prod.yml up -d
```

### 2. Verify Assets
```bash
curl -I http://localhost:8069/web
curl -s http://localhost:8069/web | grep -Eo '/web/assets/[^"]+' | head -n 1
```

### 3. Fix 500 Asset Errors
```bash
docker compose -f docker-compose.prod.yml exec odoo odoo -d odoo_core -u web,ipai_theme_aiux,ipai_aiux_chat --stop-after-init
docker compose -f docker-compose.prod.yml up -d
```

## MCP Naming Consistency

| Component | Name |
|-----------|------|
| Workspace | `ipai_workspace` |
| Repo | `odoo-ce` |
| MCP Gateway | `mcp_docker` |
| Environments | `local`, `staging`, `prod` |

## Recommended Extensions

- Docker (ms-azuretools.vscode-docker)
- Python (ms-python.python)
- Prettier (esbenp.prettier-vscode)
- ESLint (dbaeumer.vscode-eslint)
- YAML (redhat.vscode-yaml)
- TOML (tamasfe.even-better-toml)
- Makefile Tools (ms-vscode.makefile-tools)

## Settings Overview

- **Editor**: 100-char ruler, word wrap, no minimap
- **Formatting**: Auto-format on save, 2-space tabs
- **Line endings**: Unix (LF)
- **Python**: /usr/bin/python3 (system Python 3)
- **File associations**: XML, YAML, TOML, MJS
- **Search exclusions**: .git, .venv, node_modules, artifacts, .odoo

## Ports (Local Development)

| Service | Port | URL |
|---------|------|-----|
| Odoo Core | 8069 | http://localhost:8069 |
| PostgreSQL | 5432 | localhost:5432 |
| Mattermost | 8065 | http://localhost:8065 |
| n8n | 5678 | http://localhost:5678 |

## Troubleshooting

### Assets 500 Error
**Symptom**: `/web/assets/web.assets_web.min.js` returns 500

**Solution**:
```bash
# Run task: "odoo:rebuild assets (fix 500)"
# or manually:
docker compose -f deploy/docker-compose.prod.yml exec odoo-ce odoo -d odoo -u web,ipai_theme_aiux,ipai_aiux_chat --stop-after-init
docker compose -f deploy/docker-compose.prod.yml restart odoo-ce
```

### 502 Bad Gateway
**Symptom**: nginx returns 502, Odoo unreachable

**Triage**:
```bash
# Run task: "odoo:502 triage (nginx upstream + odoo crash)"
# or manually:
docker compose -f deploy/docker-compose.prod.yml ps
docker compose -f deploy/docker-compose.prod.yml logs --tail=200 odoo-ce
```

**Common Causes**:
- Odoo container crash-loop or not healthy
- Upstream misrouted (wrong container name/port)
- Proxy timeouts too low during module upgrade/asset build
- WebSocket/longpoll routing misconfiguration
- DB connection saturation

### Module Not Found
**Symptom**: Module not appearing in Odoo

**Solution**:
```bash
docker compose -f deploy/docker-compose.prod.yml exec odoo-ce ls /mnt/extra-addons/ipai/
docker compose -f deploy/docker-compose.prod.yml exec odoo-ce odoo -d odoo -u base --stop-after-init
```

### Database Connection Issues
**Symptom**: Odoo can't connect to PostgreSQL

**Solution**:
```bash
# Run task: "odoo:db connectivity"
# or manually:
docker compose -f deploy/docker-compose.prod.yml ps odoo-db
docker compose -f deploy/docker-compose.prod.yml logs odoo-db
docker compose -f deploy/docker-compose.prod.yml restart odoo-db
```

## End-State Specification

**AIUX Ship PRD v1.1.0**: `docs/prd/end_state/AIUX_SHIP_v1.1.0.json`

This JSON file defines:
- Module scope and integration points
- Deployment configuration (compose file, containers, DB)
- CI gates and verification steps
- Failure modes (502, 500) with causes and prevention
- Workspace tasks (canonical task names)
- Rollback strategy

**Why this matters**: Turns "debugging" into "run checks". All failure modes documented with deterministic fix tasks.

---

*Last updated: 2026-01-08*
