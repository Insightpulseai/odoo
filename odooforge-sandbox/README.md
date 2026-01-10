# OdooForge Sandbox

Containerized development environment for creating, validating, and deploying IPAI Odoo modules.

**Optimized for**: Codex Cloud, Claude Code Web, VS Code Dev Containers, GitHub Codespaces

## Quick Start

```bash
# One-command setup
chmod +x install-sandbox.sh
./install-sandbox.sh

# Access Odoo
open http://localhost:8069

# Enter CLI container
docker compose exec kit bash

# Create your first module
kit init ipai_hello
```

## Codex Cloud / Claude Code Web

This sandbox is optimized for AI-assisted development:

```bash
# Environment setup (auto-runs in devcontainer)
./scripts/codex_setup.sh

# PR gate check (same as CI)
./scripts/codex_check.sh
```

**Agent rules**: See [AGENTS.md](./AGENTS.md) for Odoo/OCA invariants and code review expectations.

## VS Code Dev Container

Open in VS Code with Dev Containers extension:

1. Install "Dev Containers" extension
2. Open command palette: `Dev Containers: Open Folder in Container`
3. Select this directory

Or use GitHub Codespaces - the devcontainer is pre-configured.

## Components

| Service | Port | Description |
|---------|------|-------------|
| odoo | 8069 | Odoo 18.0 CE instance |
| db | 5432 | PostgreSQL 15 database |
| kit | - | CLI development container |

## Kit CLI Commands

| Command | Description |
|---------|-------------|
| `kit version` | Show version information |
| `kit init <module>` | Create new IPAI module |
| `kit validate [module]` | Validate module structure |
| `kit validate --strict` | Full OCA compliance check |
| `kit build <module>` | Build module package |
| `kit deploy <module>` | Deploy to Odoo |
| `kit list` | List all modules |
| `kit status` | Show environment status |

## Module Naming

All modules must follow IPAI naming convention:

```
ipai_<name>          # e.g., ipai_hello
ipai_<domain>_<name> # e.g., ipai_finance_ppm
```

## Directory Structure

```
odooforge-sandbox/
├── .devcontainer/          # VS Code Dev Container config
├── .github/workflows/      # CI/CD pipelines
├── docker-compose.yml      # All services
├── Dockerfile.kit          # CLI container
├── install-sandbox.sh      # One-click setup
├── AGENTS.md               # AI agent rules
├── config/
│   └── odoo.conf          # Odoo configuration
├── kit-cli/
│   └── kit.py             # CLI implementation
├── scripts/
│   ├── codex_setup.sh     # Codex environment setup
│   └── codex_check.sh     # PR gate script
├── tests/
│   ├── UAT_TEST_PLAN.md   # Test plan (38 tests)
│   ├── test_uat.py        # Automated tests
│   └── run-uat.sh         # Quick smoke test
├── addons/                 # Your modules here
├── templates/              # Module templates
├── specs/                  # AI generation specs
└── reports/                # Test reports output
```

## Testing

```bash
# Quick smoke test (from host)
./tests/run-uat.sh

# Full UAT suite (in container)
docker compose exec kit pytest tests/test_uat.py -v

# Generate HTML report
docker compose exec kit pytest tests/test_uat.py --html=reports/uat.html

# Run Codex-style PR gate
./scripts/codex_check.sh
```

## Development Workflow

1. **Create module**: `kit init ipai_myfeature`
2. **Develop**: Edit files in `addons/ipai_myfeature/`
3. **Validate**: `kit validate --strict`
4. **Test**: `kit test` or `pytest tests/`
5. **PR Gate**: `./scripts/codex_check.sh`
6. **Deploy**: `kit deploy ipai_myfeature`

## Pre-commit Hooks

```bash
# Install hooks
pip install pre-commit
pre-commit install

# Run all hooks
pre-commit run -a
```

## Credentials

| Service | Username | Password |
|---------|----------|----------|
| Odoo | admin | admin |
| PostgreSQL | odoo | odoo |

## Troubleshooting

### Odoo not starting?
```bash
docker compose logs odoo
# Wait for "HTTP service running"
```

### Port in use?
```bash
lsof -i :8069
# Stop conflicting service
```

### Reset everything
```bash
docker compose down -v
./install-sandbox.sh
```

### Codex/Claude Code issues?
```bash
# Re-run setup
./scripts/codex_setup.sh

# Check kit is working
kit version
kit status
```

## License

LGPL-3.0

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) in the main repository.

Read [AGENTS.md](./AGENTS.md) before submitting PRs - it contains OCA compliance rules.
