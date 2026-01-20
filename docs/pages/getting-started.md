# Getting Started

This guide covers how to clone, bootstrap, and run the Odoo development environment.

## Prerequisites

- **Docker** & Docker Compose v2+
- **Node.js** >= 18.0.0
- **Python** 3.10+
- **Git**

## Clone the Repository

```bash
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce
```

## Environment Setup

1. **Copy environment template:**

```bash
cp .env.example .env
```

2. **Edit `.env` with your configuration:**

```bash
# Database
POSTGRES_USER=odoo
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=odoo_core

# Odoo
ODOO_ADMIN_PASSWORD=your-admin-password
```

## Start the Stack

```bash
# Start core services
docker compose up -d

# View logs
docker compose logs -f odoo-core
```

## Initialize Modules

```bash
# Run with init profile for first-time setup
docker compose --profile ce-init up

# Deploy IPAI modules
./scripts/deploy-odoo-modules.sh
```

## Verify Installation

```bash
# Health check
curl -s http://localhost:8069/web/health

# Run verification script
./scripts/repo_health.sh
```

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Odoo Core | http://localhost:8069 | admin / (your password) |
| Odoo Marketing | http://localhost:8070 | admin / (your password) |
| Odoo Accounting | http://localhost:8071 | admin / (your password) |
| PostgreSQL | localhost:5432 | odoo / (your password) |

## Next Steps

- Read the [Architecture](architecture.md) overview
- Review the [Developer Guide](developer-guide.md) for conventions
- Explore the [Modules](modules.md) documentation
