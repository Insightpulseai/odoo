# Database Initialization - Non-Interactive Workflow

**Purpose**: Initialize Odoo databases without UI interaction, following scripted/reproducible patterns for local → staging → prod environments.

**Philosophy**: No manual UI clicks, fully scripted, CI/CD friendly.

---

## Quick Start (Local Development)

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and customize (optional):
#   ODOO_DB_NAME=odoo_dev
#   ODOO_ADMIN_PASSWORD=admin
#   ODOO_ADMIN_EMAIL=admin@insightpulseai.com
```

### 2. Start Services

```bash
./scripts/dev/up.sh
```

### 3. Initialize Database (Non-Interactive)

```bash
# Initialize with production-like settings (no demo data)
./scripts/dev/init-db.sh

# OR initialize with demo data for testing
./scripts/dev/init-db.sh --with-demo
```

### 4. Access Odoo

```
URL: http://localhost:8069
Database: odoo_dev
Username: admin
Password: admin (or value from ODOO_ADMIN_PASSWORD)
```

---

## What the Script Does

The `init-db.sh` script performs these operations **non-interactively**:

1. ✅ Loads environment variables from `.env`
2. ✅ Verifies Docker container is running
3. ✅ Checks if database already exists (prompts for confirmation if it does)
4. ✅ Creates PostgreSQL database
5. ✅ Initializes Odoo with base modules:
   - `base` - Core framework
   - `web` - Web interface
   - `mail` - Email and messaging
   - `contacts` - Contact management
6. ✅ Configures admin user credentials
7. ✅ Stops after initialization (no daemon mode)

---

## Script Output Example

```
════════════════════════════════════════════════════════════════
Odoo Dev Sandbox - Database Initialization
════════════════════════════════════════════════════════════════

Configuration:
  Database Name: odoo_dev
  Admin Email: admin@insightpulseai.com
  Demo Data: False
  Container: odoo-dev

📦 Creating database 'odoo_dev'...
CREATE DATABASE

🚀 Initializing Odoo with base modules...
   This may take 3-5 minutes...

[... Odoo initialization logs ...]

════════════════════════════════════════════════════════════════
✅ Database initialization complete!
════════════════════════════════════════════════════════════════

Access your Odoo instance:
  URL: http://localhost:8069
  Database: odoo_dev
  Username: admin
  Password: admin

Next steps:
  1. Login at http://localhost:8069/web/login
  2. Install custom modules from Apps menu
  3. Configure settings as needed
```

---

## Advanced Usage

### Custom Module Installation During Init

Edit the script to add modules to the `--init` flag:

```bash
# In scripts/dev/init-db.sh, modify:
--init=base,web,mail,contacts,sale,purchase,account
```

### Recreate Database

```bash
# The script will detect existing database and prompt:
⚠️  Warning: Database 'odoo_dev' already exists

Do you want to DROP and recreate it? (yes/no): yes

# Or drop manually first:
export DOCKER_HOST="unix:///Users/tbwa/.colima/default/docker.sock"
docker exec odoo-dev-db psql -U odoo -d postgres -c "DROP DATABASE odoo_dev"
./scripts/dev/init-db.sh
```

### Include Demo Data

```bash
./scripts/dev/init-db.sh --with-demo
```

**Why use demo data?**
- Testing workflows without manual data entry
- Learning Odoo features
- Developing/testing custom modules

**Production rule**: NEVER use demo data in staging/prod environments.

---

## CI/CD Integration

### GitHub Actions Workflow (Future)

```yaml
name: Initialize Odoo Database
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment'
        required: true
        type: choice
        options:
          - local
          - staging
          - prod

jobs:
  init-db:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Load environment
        run: |
          cp deploy/18ce/${{ inputs.environment }}/.env.example .env
          # Load secrets from GitHub Secrets

      - name: Initialize database
        run: |
          cd deploy/18ce/${{ inputs.environment }}
          ./scripts/init-db.sh
```

---

## Staging Environment

**Coming Soon**: Staging-specific initialization script with:
- Production-like settings (no demo data)
- SSL/TLS configuration
- Nginx reverse proxy setup
- Database backup/restore from production

**Placeholder**:
```bash
# Future command
./scripts/staging/init-db.sh --from-prod-backup
```

---

## Production Environment

**Critical Rules**:
1. ❌ **NEVER** initialize fresh database in production
2. ✅ **ALWAYS** restore from tested backup
3. ✅ **ALWAYS** test in staging first
4. ✅ **ALWAYS** have rollback plan

**Production Init Pattern**:
```bash
# 1. Backup existing production database (if any)
./scripts/prod/backup-db.sh

# 2. Restore from staging backup
./scripts/prod/restore-db.sh --from-staging

# 3. Verify health
./scripts/prod/health-check.sh

# 4. If issues, rollback
./scripts/prod/rollback-db.sh
```

---

## Troubleshooting

### Error: Container not running

```
❌ Error: Container odoo-dev is not running
   Run: ./scripts/dev/up.sh
```

**Solution**: Start Docker services first.

### Error: Database already exists

```
⚠️  Warning: Database 'odoo_dev' already exists
```

**Solution**:
- Type `yes` to drop and recreate
- OR manually drop: `docker exec odoo-dev-db psql -U odoo -d postgres -c "DROP DATABASE odoo_dev"`

### Error: PostgreSQL connection failed

**Check database health**:
```bash
./scripts/dev/health.sh
```

**Verify PostgreSQL is running**:
```bash
export DOCKER_HOST="unix:///Users/tbwa/.colima/default/docker.sock"
docker exec odoo-dev-db psql -U odoo -d postgres -c "SELECT 1"
```

### Error: Initialization timeout

**Symptom**: Script hangs for >5 minutes

**Solutions**:
1. Check container logs: `./scripts/dev/logs.sh odoo`
2. Verify disk space: `df -h`
3. Check resource limits in docker-compose.yml
4. Restart Docker: `./scripts/dev/down.sh && ./scripts/dev/up.sh`

---

## What's Different from UI-Based Init?

| Aspect | UI-Based (❌ Avoided) | Script-Based (✅ Preferred) |
|--------|----------------------|---------------------------|
| **Reproducibility** | Manual, error-prone | Automated, consistent |
| **CI/CD Integration** | Not possible | Fully integrated |
| **Version Control** | Settings lost | Settings in `.env` tracked |
| **Audit Trail** | No logs | Full initialization logs |
| **Automation** | Requires human | Fully automated |
| **Environment Parity** | Drift likely | Identical across envs |

---

## Script Reference

**Location**: `scripts/dev/init-db.sh`

**Dependencies**:
- Docker and Docker Compose
- Running `odoo-dev` and `odoo-dev-db` containers
- `.env` file with configuration

**Exit Codes**:
- `0` - Success
- `1` - Configuration error or user aborted
- `2` - Database operation failed

**Environment Variables**:
```bash
ODOO_DB_NAME          # Database name (default: odoo_dev)
ODOO_ADMIN_PASSWORD   # Admin password (default: admin)
ODOO_ADMIN_EMAIL      # Admin email
POSTGRES_USER         # PostgreSQL username
POSTGRES_PASSWORD     # PostgreSQL password
ODOO_PORT            # HTTP port (default: 8069)
```

---

## Related Documentation

- **Daily Operations**: `DEV_SANDBOX.md`
- **Health Checks**: `scripts/dev/health.sh`
- **Backup/Restore**: `scripts/dev/backup-db.sh` (future)
- **Environment Matrix**: Main repo `docs/infra/DOCKER_DESKTOP_SSOT.yaml`

---

**Last Updated**: 2026-01-28
**Author**: InsightPulse AI Engineering
**Version**: 1.0.0
