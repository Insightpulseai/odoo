# OdooForge Sandbox

Containerized development environment for creating, validating, and deploying IPAI Odoo modules.

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
├── docker-compose.yml      # All services
├── Dockerfile.kit          # CLI container
├── install-sandbox.sh      # One-click setup
├── config/
│   └── odoo.conf          # Odoo configuration
├── kit-cli/
│   └── kit.py             # CLI implementation
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

## License

LGPL-3.0

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) in the main repository.
