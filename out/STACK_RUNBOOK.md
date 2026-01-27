# Odoo 19 CE + OCA Stack Runbook

**Version:** 1.0.0
**Generated:** 2026-01-27
**Purpose:** CLI-only deployment and operations guide (no UI steps)

---

## Quick Start

```bash
# 1. Clone and prepare
git clone <repo-url> odoo-ce && cd odoo-ce

# 2. Pin OCA repositories
./scripts/stack/pin_oca_repos.sh

# 3. Start core services
docker compose up -d postgres odoo-core

# 4. Install stack
./scripts/stack/install_stack.sh

# 5. Verify
./scripts/stack/verify_stack.sh
```

---

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Storage | 50 GB | 100 GB |
| OS | Ubuntu 22.04+ | Ubuntu 24.04 |

### Software Dependencies

```bash
# Install system packages
sudo apt-get update && sudo apt-get install -y \
  git curl jq docker.io docker-compose-plugin \
  python3.11 python3.11-venv python3-pip

# Verify Docker
docker --version && docker compose version

# Verify Python
python3 --version
```

---

## Phase 1: Repository Setup

### Clone and Initialize

```bash
# Clone repository
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce

# Create required directories
mkdir -p addons/oca out docs/evidence

# Copy environment template
cp .env.example .env
# Edit .env with your settings
```

### Pin OCA Repositories

```bash
# Pin all OCA repos to current HEAD
./scripts/stack/pin_oca_repos.sh

# Update existing pins (fetch latest)
./scripts/stack/pin_oca_repos.sh --update

# Verify lockfile
cat oca19.lock.json | jq '.repositories | keys'
```

---

## Phase 2: Core Stack Deployment

### Start PostgreSQL

```bash
# Start database only first
docker compose up -d postgres

# Wait for healthy
docker compose exec postgres pg_isready -U odoo

# Verify connection
docker compose exec postgres psql -U odoo -d postgres -c "SELECT version();"
```

### Start Odoo CE

```bash
# Start Odoo
docker compose up -d odoo-core

# Watch startup logs
docker compose logs -f odoo-core

# Verify health
curl -s http://localhost:8069/web/health
# Expected: {"status": "pass"}
```

### Initialize Database

```bash
# Create database (if not exists)
docker compose exec odoo-core odoo \
  -d odoo_core \
  -i base \
  --stop-after-init \
  --no-http

# Verify database
docker compose exec postgres psql -U odoo -d odoo_core \
  -c "SELECT name, state FROM ir_module_module WHERE state = 'installed' LIMIT 5;"
```

---

## Phase 3: OCA Module Installation

### Install by Tier

```bash
# Install Foundation (Tier 0)
./scripts/stack/install_stack.sh --tier 0

# Install Platform UX (Tier 1)
./scripts/stack/install_stack.sh --tier 1

# Install Reporting (Tier 4)
./scripts/stack/install_stack.sh --tier 4

# Install all tiers (full stack)
./scripts/stack/install_stack.sh
```

### Install Single Module

```bash
# Install specific module
./scripts/stack/install_stack.sh --module mis_builder

# Update existing module
docker compose exec odoo-core odoo \
  -d odoo_core \
  -u mis_builder \
  --stop-after-init
```

### Manual Module Installation

```bash
# Direct Odoo command for multiple modules
docker compose exec odoo-core odoo \
  -d odoo_core \
  -i date_range,base_tier_validation,web_responsive \
  --stop-after-init \
  --no-http \
  --log-level=warn
```

---

## Phase 4: IPAI Modules

### Install IPAI Platform

```bash
# Core IPAI modules
docker compose exec odoo-core odoo \
  -d odoo_core \
  -i ipai_dev_studio_base,ipai_workspace_core,ipai_platform_approvals \
  --stop-after-init

# Finance modules
docker compose exec odoo-core odoo \
  -d odoo_core \
  -i ipai_finance_ppm_golive,ipai_month_end \
  --stop-after-init
```

---

## Phase 5: Verification

### Run Full Verification

```bash
# Standard verification
./scripts/stack/verify_stack.sh

# Verbose output
./scripts/stack/verify_stack.sh --verbose

# JSON output for CI
./scripts/stack/verify_stack.sh --json
```

### Manual Health Checks

```bash
# Odoo health
curl -s -w "\n%{http_code}\n" http://localhost:8069/web/health

# Login page response time
time curl -s -o /dev/null http://localhost:8069/web/login

# PostgreSQL status
docker compose exec postgres pg_isready -U odoo -d odoo_core

# Container status
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

### Module Verification

```bash
# Check installed modules
docker compose exec postgres psql -U odoo -d odoo_core -c "
SELECT name, state, latest_version
FROM ir_module_module
WHERE state = 'installed'
AND name LIKE '%tier%' OR name LIKE '%mis_%' OR name LIKE '%dms%'
ORDER BY name;
"

# Check module dependencies
docker compose exec postgres psql -U odoo -d odoo_core -c "
SELECT m.name, d.name as dependency
FROM ir_module_module m
JOIN ir_module_module_dependency dep ON m.id = dep.module_id
JOIN ir_module_module d ON d.name = dep.name
WHERE m.name = 'mis_builder';
"
```

---

## Phase 6: Analytics Stack (Optional)

### Deploy Minimal Analytics

```bash
# Start MinIO (S3 storage)
docker compose -f docker/analytics/docker-compose.yml up -d minio minio-init

# Verify buckets
docker compose -f docker/analytics/docker-compose.yml exec minio mc ls local/
```

### Deploy Full Analytics

```bash
# Core analytics: MinIO + Airbyte + Superset
docker compose -f docker/analytics/docker-compose.yml up -d \
  minio minio-init airbyte-server airbyte-webapp superset superset-db superset-init

# Add Trino query engine
docker compose -f docker/analytics/docker-compose.yml up -d trino

# With DataHub (governance)
docker compose -f docker/analytics/docker-compose.yml --profile datahub up -d
```

### Initialize dbt

```bash
# Install dbt
pip install dbt-postgres dbt-trino

# Copy profile
mkdir -p ~/.dbt
cp dbt/profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml with credentials

# Install packages
cd dbt && dbt deps

# Test connection
dbt debug

# Run models
dbt run --select staging
dbt run --select marts.finance
```

---

## Operations

### Restart Services

```bash
# Restart Odoo only
docker compose restart odoo-core

# Restart all services
docker compose restart

# Full rebuild (destructive)
docker compose down && docker compose up -d
```

### View Logs

```bash
# Odoo logs (tail)
docker compose logs -f --tail=100 odoo-core

# All service logs
docker compose logs -f

# Filter by keyword
docker compose logs odoo-core 2>&1 | grep -i error
```

### Database Operations

```bash
# Backup database
docker compose exec postgres pg_dump -U odoo -Fc odoo_core > backup_$(date +%Y%m%d).dump

# Restore database
docker compose exec -T postgres pg_restore -U odoo -d odoo_core < backup_20260127.dump

# Run SQL query
docker compose exec postgres psql -U odoo -d odoo_core -c "SELECT COUNT(*) FROM res_partner;"
```

### Module Operations

```bash
# List all modules
docker compose exec postgres psql -U odoo -d odoo_core -c "
SELECT name, state, shortdesc FROM ir_module_module ORDER BY name;"

# Uninstall module (careful!)
docker compose exec odoo-core odoo shell -d odoo_core -c "
env['ir.module.module'].search([('name', '=', 'module_name')]).button_immediate_uninstall()
"

# Clear cache
docker compose exec odoo-core odoo shell -d odoo_core -c "
env['ir.ui.view'].sudo().clear_caches()
"
```

---

## Troubleshooting

### Odoo Won't Start

```bash
# Check container logs
docker compose logs odoo-core | tail -50

# Check for port conflicts
lsof -i :8069

# Rebuild container
docker compose build odoo-core && docker compose up -d odoo-core
```

### Module Installation Fails

```bash
# Check dependencies
docker compose exec odoo-core odoo \
  -d odoo_core \
  -i <module_name> \
  --stop-after-init \
  --log-level=debug 2>&1 | grep -i "depend\|error"

# Check manifest syntax
python3 -c "import ast; ast.literal_eval(open('addons/oca/<repo>/<module>/__manifest__.py').read())"
```

### Database Connection Issues

```bash
# Test PostgreSQL
docker compose exec postgres pg_isready -U odoo -d odoo_core

# Check connection from Odoo container
docker compose exec odoo-core python3 -c "
import psycopg2
conn = psycopg2.connect(host='postgres', dbname='odoo_core', user='odoo', password='odoo')
print('Connected:', conn.server_version)
"
```

### Permission Errors

```bash
# Fix addons permissions
sudo chown -R 101:101 addons/
sudo chmod -R 755 addons/

# Restart after permission fix
docker compose restart odoo-core
```

---

## CI/CD Integration

### Run CI Gates Locally

```bash
# Full CI suite
./scripts/ci_local.sh

# Stack-specific gates
act -j validate-manifest -j lint-modules -j test-pinning
```

### Trigger Full Install Test

```bash
# Via GitHub Actions (manual dispatch)
gh workflow run stack-gates.yml -f full_install=true

# Watch workflow
gh run watch
```

---

## Upgrade Procedure

### Upgrade OCA Modules

```bash
# 1. Update lockfile
./scripts/stack/pin_oca_repos.sh --update

# 2. Stop Odoo
docker compose stop odoo-core

# 3. Backup database
docker compose exec postgres pg_dump -U odoo -Fc odoo_core > pre_upgrade_$(date +%Y%m%d).dump

# 4. Update modules
docker compose exec odoo-core odoo \
  -d odoo_core \
  -u all \
  --stop-after-init

# 5. Restart and verify
docker compose start odoo-core
./scripts/stack/verify_stack.sh
```

### Upgrade Odoo Version

```bash
# TODO: Requires OpenUpgrade migration
# See: https://github.com/OCA/OpenUpgrade
```

---

## Reference

### Key Paths

| Path | Purpose |
|------|---------|
| `stack/odoo19_stack.yaml` | Stack manifest (SSOT) |
| `oca19.lock.json` | OCA repository pins |
| `addons/oca/` | OCA modules |
| `addons/ipai/` | IPAI custom modules |
| `scripts/stack/` | Stack automation scripts |
| `docker/analytics/` | Analytics stack compose |
| `dbt/` | dbt project |
| `docs/evidence/` | Verification evidence |

### Key Commands

| Command | Purpose |
|---------|---------|
| `./scripts/stack/pin_oca_repos.sh` | Pin OCA repos |
| `./scripts/stack/install_stack.sh` | Install modules |
| `./scripts/stack/verify_stack.sh` | Verify installation |
| `docker compose logs -f odoo-core` | View Odoo logs |
| `docker compose exec odoo-core odoo -d db -i mod` | Install module |
| `docker compose exec odoo-core odoo -d db -u mod` | Update module |

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ODOO_DB` | `odoo_core` | Database name |
| `ODOO_URL` | `http://localhost:8069` | Odoo URL |
| `DOCKER_MODE` | `true` | Run in Docker |
| `ODOO_CONTAINER` | `odoo-core` | Container name |

---

## Support

- **Documentation:** `docs/` directory
- **Issues:** https://github.com/jgtolentino/odoo-ce/issues
- **OCA:** https://odoo-community.org/
