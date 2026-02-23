# Odoo 18 CE Dev Sandbox

Clean, reproducible Odoo 18 CE development environment with OCA integration.

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Verify setup
./scripts/verify.sh

# 3. Start services
./scripts/dev/up.sh

# 4. Access Odoo
open http://localhost:8069
```

## What's Included

- **Odoo 18.0**: Latest Community Edition
- **PostgreSQL 16**: Alpine-based database
- **Hot Reload**: Auto-restart on code changes
- **OCA Integration**: 24+ community modules
- **Custom Modules**: `ipai` + `ipai_enterprise_bridge`
- **Dev Tools**: pgAdmin, Mailpit (optional)

## Documentation

- **[Developer Runbook](docs/runbooks/DEV_SANDBOX.md)**: Complete setup and usage guide
- **[Audit Report](REPORT.md)**: Current state vs canonical SSOT
- **[Project Instructions](CLAUDE.md)**: Claude Code integration

## Repository Structure

```
odoo-dev-sandbox/
├── addons/                    # Custom modules (hot-reload)
├── oca-addons/                # OCA dependencies (symlink/clone)
├── config/odoo.conf           # Odoo configuration
├── scripts/dev/               # Daily operation scripts
├── docker-compose.yml         # Stack definition
└── docs/runbooks/             # Documentation
```

## Development Workflow

**Start**:
```bash
./scripts/dev/up.sh
```

**Make Changes**: Edit `addons/ipai/` files → Auto-reload

**View Logs**:
```bash
./scripts/dev/logs.sh odoo
```

**Stop**:
```bash
./scripts/dev/down.sh
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/dev/up.sh` | Start all services |
| `scripts/dev/down.sh` | Stop all services |
| `scripts/dev/health.sh` | Check service health |
| `scripts/dev/logs.sh` | View container logs |
| `scripts/dev/reset-db.sh` | Reset database (destructive) |
| `scripts/verify.sh` | Run all verification checks |

## Requirements

- Docker Desktop 24.0+
- Git 2.0+
- 8GB RAM recommended
- 10GB free disk space

## OCA Modules

This sandbox requires **24 OCA modules** for full functionality. See [docs/runbooks/DEV_SANDBOX.md](docs/runbooks/DEV_SANDBOX.md) for installation options:

1. **Symlink** (recommended): `ln -s ~/path/to/oca oca-addons`
2. **Git submodules**: Add OCA repos as submodules
3. **Manual clone**: Clone each repo into `oca-addons/`

## Verification

```bash
# Run all checks
./scripts/verify.sh

# Expected output:
# ✅ All checks passed
# Ready to: ./scripts/dev/up.sh
```

## CI/CD

GitHub Actions workflow automatically validates:
- Docker Compose syntax
- Required files presence
- Script permissions
- Odoo 18 conventions
- Addon manifest syntax

See `.github/workflows/dev-sandbox-verify.yml`

## Support

- **Issues**: File in GitHub repository
- **Odoo Docs**: https://www.odoo.com/documentation/18.0
- **OCA Guidelines**: https://github.com/OCA/odoo-community.org

## License

AGPL-3 (following Odoo and OCA conventions)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-18
**Maintained By**: IPAI / TBWA
