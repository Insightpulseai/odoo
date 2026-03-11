# OdooForge Sandbox - Codex Cloud Optimization

**Date**: 2026-01-10
**Commit**: edecf86

## Added Components

| Component | Purpose | Location |
|-----------|---------|----------|
| codex_setup.sh | Environment bootstrap | scripts/codex_setup.sh |
| codex_check.sh | Unified PR gate | scripts/codex_check.sh |
| AGENTS.md | Agent rules/invariants | AGENTS.md |
| devcontainer.json | VS Code parity | .devcontainer/devcontainer.json |
| odooforge.yml | CI workflow | .github/workflows/odooforge.yml |
| pre-commit-config | Linting hooks | .pre-commit-config.yaml |
| requirements.txt | Base deps | requirements.txt |
| requirements-dev.txt | Dev deps | requirements-dev.txt |

## Verification Checklist

| Check | Status |
|-------|--------|
| codex_setup.sh syntax | PASS |
| codex_check.sh syntax | PASS |
| AGENTS.md created | PASS |
| devcontainer.json valid JSON | PASS |
| CI workflow valid YAML | PASS |
| pre-commit config valid | PASS |
| Git commit successful | PASS |
| Git push successful | PASS |

## Codex Cloud Environment Contract

### Setup Script
```bash
./scripts/codex_setup.sh
```
- Installs pip, wheel, setuptools
- Installs requirements-dev.txt
- Configures pre-commit hooks
- Makes scripts executable
- Links kit CLI

### PR Gate Script
```bash
./scripts/codex_check.sh
```
- Runs pre-commit hooks
- Python syntax validation
- kit validate --strict
- pytest tests

### Same Gate Everywhere
- Local: `./scripts/codex_check.sh`
- Codex Cloud: `./scripts/codex_check.sh`
- Claude Code Web: `./scripts/codex_check.sh`
- CI: `bash scripts/codex_check.sh` in pr_gate job

## AGENTS.md Key Rules

1. **Odoo 18 View Syntax**: `<list>` not `<tree>`, `view_mode="list,form"`
2. **Smart Delta**: Never modify core, extend via `_inherit`
3. **OCA Compliance**: No brittle xpaths, version format 18.0.x.y.z
4. **Module Naming**: `ipai_<domain>_<feature>` pattern

## VS Code Dev Container

Features:
- Python 3.11 with pylance
- Black + isort formatting
- XML extension for views
- GitHub Copilot ready
- Auto-runs codex_setup.sh
- Forwards ports 8069 (Odoo), 5432 (PostgreSQL)

## CI Pipeline

Jobs:
1. **validate**: Syntax checks + kit validate
2. **test**: pytest with PostgreSQL service
3. **pr_gate**: Runs codex_check.sh (PR only)
4. **docker-build**: Builds kit container
