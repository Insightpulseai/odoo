# Odoo 18 CE Dev Sandbox - Developer Runbook

**Version**: 1.0.0
**Last Updated**: 2026-01-18
**Purpose**: Reproducible Odoo 18 CE development environment with OCA integration

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [First-Time Setup](#first-time-setup)
4. [Daily Workflow](#daily-workflow)
5. [Common Operations](#common-operations)
6. [Troubleshooting](#troubleshooting)
7. [Architecture](#architecture)
8. [OCA Integration](#oca-integration)

---

## Quick Start

```bash
# Clone repo
git clone <repo-url> odoo-dev-sandbox
cd odoo-dev-sandbox

# Copy environment template
cp .env.example .env

# Verify setup
./scripts/verify.sh

# Start services
./scripts/dev/up.sh

# Access Odoo
open http://localhost:8069
```

**Expected Output**:
- Odoo login screen at `http://localhost:8069`
- Database creation wizard (first run)
- Default admin credentials: `admin` / `admin_dev_password`

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | 24.0+ | Container runtime |
| Git | 2.0+ | Version control |
| Bash | 4.0+ | Script execution |

### Optional Tools

| Tool | Purpose |
|------|---------|
| shellcheck | Script linting |
| pgAdmin | Database management (included in stack) |
| Mailpit | Email testing (included in stack) |

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **OS**: macOS, Linux, or Windows with WSL2

---

## First-Time Setup

### Step 1: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# (Optional) Customize ports
nano .env
```

**Default Ports**:
- Odoo Web: `8069`
- Odoo Longpolling: `8072`
- PostgreSQL: `5433` (mapped to avoid conflicts)
- pgAdmin: `5050` (optional, profile: tools)
- Mailpit Web: `8025` (optional, profile: tools)
- Mailpit SMTP: `1025` (optional, profile: tools)

### Step 2: Populate OCA Addons (Required)

The `ipai` module depends on 24 OCA modules. Choose one option:

**Option A: Symlink to Canonical Location** (Recommended)
```bash
# If you have odoo-ce/addons/external/oca
ln -s ~/Documents/GitHub/odoo-ce/addons/external/oca oca-addons

# Verify symlink
ls -la oca-addons/
```

**Option B: Git Submodules**
```bash
# Add OCA repos as submodules
cd oca-addons
git submodule add https://github.com/OCA/project.git project
git submodule add https://github.com/OCA/timesheet.git timesheet
# ... repeat for all 24 dependencies

# Update submodules
git submodule update --init --recursive
```

**Option C: Manual Clone**
```bash
# Clone required OCA repos into oca-addons/
mkdir -p oca-addons
cd oca-addons
git clone -b 18.0 https://github.com/OCA/project.git
git clone -b 18.0 https://github.com/OCA/timesheet.git
# ... repeat for all dependencies
```

**Required OCA Modules** (from `ipai/__manifest__.py`):
```
project_timeline, project_timeline_hr_timesheet,
project_timesheet_time_control, project_task_dependencies,
project_task_parent_completion_blocking, project_task_parent_due_auto,
project_type, project_template, hr_timesheet_sheet,
hr_timesheet_sheet_autodraft, hr_timesheet_sheet_policy_project_manager,
hr_timesheet_sheet_warning, hr_timesheet_task_domain,
helpdesk_mgmt, helpdesk_mgmt_project, helpdesk_ticket_type,
base_territory, fieldservice, fieldservice_project, fieldservice_portal,
maintenance, quality_control, mgmtsystem, mgmtsystem_quality,
dms, knowledge, mis_builder
```

### Step 3: Verify Setup

```bash
# Run verification script
./scripts/verify.sh
```

**Expected Output**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All checks passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to:
  ./scripts/dev/up.sh
```

### Step 4: Start Services

```bash
./scripts/dev/up.sh
```

**Expected Output**:
```
📦 Starting Odoo dev sandbox...
✅ Services starting...
🔍 Checking health...
NAME           IMAGE          STATUS         PORTS
odoo-dev       odoo:18.0      Up 10 seconds  0.0.0.0:8069->8069/tcp
odoo-dev-db    postgres:16    Up 10 seconds  0.0.0.0:5433->5432/tcp

🌐 Access Odoo:
   http://localhost:8069
```

### Step 5: Create Database

1. Navigate to `http://localhost:8069`
2. Click "Create Database"
3. **Database Name**: `odoo_dev`
4. **Email**: `admin@localhost.com`
5. **Password**: `admin` (or custom)
6. **Language**: English
7. **Country**: Philippines (for BIR compliance)
8. **Demo Data**: Load (recommended for development)

### Step 6: Install Custom Modules

```bash
# Access Odoo shell
docker compose exec odoo odoo shell -d odoo_dev

# In Odoo shell:
env['ir.module.module'].search([('name', '=', 'ipai')]).button_immediate_install()
env['ir.module.module'].search([('name', '=', 'ipai_enterprise_bridge')]).button_immediate_install()
```

**Or via UI**:
1. Navigate to Apps menu
2. Remove "Apps" filter
3. Search for "ipai"
4. Click "Install" on both modules

---

## Daily Workflow

### Start Development Session

```bash
# Start services
./scripts/dev/up.sh

# Check health
./scripts/dev/health.sh

# View logs
./scripts/dev/logs.sh odoo
```

### Make Code Changes

**Hot-reload is enabled** - changes to Python/XML files automatically restart Odoo.

1. Edit files in `addons/ipai/` or `addons/ipai_enterprise_bridge/`
2. Save changes
3. Watch logs for auto-restart:
   ```bash
   ./scripts/dev/logs.sh odoo
   ```
4. Refresh browser (Ctrl+Shift+R to clear cache)

### End Development Session

```bash
# Stop services (data preserved)
./scripts/dev/down.sh
```

---

## Common Operations

### View Logs

```bash
# All Odoo logs
./scripts/dev/logs.sh odoo

# Database logs
./scripts/dev/logs.sh db

# All services
./scripts/dev/logs.sh
```

### Database Operations

**Reset Database** (Destructive):
```bash
./scripts/dev/reset-db.sh
# Type 'yes' to confirm
```

**Direct psql Access**:
```bash
# Connect to database
docker compose exec db psql -U odoo -d odoo_dev

# List databases
docker compose exec db psql -U odoo -d postgres -c "\l"

# Backup database
docker compose exec db pg_dump -U odoo odoo_dev > backup.sql

# Restore database
cat backup.sql | docker compose exec -T db psql -U odoo -d odoo_dev
```

### Module Operations

**Update Module**:
```bash
docker compose exec odoo odoo -d odoo_dev -u ipai --stop-after-init
docker compose restart odoo
```

**Install New Module**:
```bash
docker compose exec odoo odoo -d odoo_dev -i <module_name> --stop-after-init
docker compose restart odoo
```

**Uninstall Module**:
```bash
docker compose exec odoo odoo shell -d odoo_dev
# In shell:
env['ir.module.module'].search([('name', '=', '<module_name>')]).button_immediate_uninstall()
```

### Start Optional Tools

```bash
# Start with pgAdmin and Mailpit
docker compose --profile tools up -d

# Access tools
open http://localhost:5050    # pgAdmin
open http://localhost:8025    # Mailpit
```

### Clean Up

```bash
# Stop and remove containers (preserves volumes)
docker compose down

# Stop and remove everything including volumes (DESTRUCTIVE)
docker compose down -v

# Remove unused images
docker image prune -a
```

---

## Troubleshooting

### Odoo Won't Start

**Symptom**: Container exits immediately

**Diagnosis**:
```bash
./scripts/dev/logs.sh odoo
```

**Common Causes**:

1. **Database connection failed**
   ```
   Solution: Check db container is healthy
   docker compose ps
   docker compose logs db
   ```

2. **Port already in use**
   ```
   Error: bind: address already in use
   Solution: Change ODOO_PORT in .env
   ```

3. **Invalid config file**
   ```
   Solution: Validate config/odoo.conf
   grep -E '^\[|^[a-z]' config/odoo.conf
   ```

### Database Connection Refused

**Symptom**: `FATAL: password authentication failed`

**Fix**:
```bash
# Reset database container
docker compose down
docker volume rm odoo-dev-db-data
docker compose up -d
```

### Module Install Fails

**Symptom**: "Module not found" or dependency errors

**Diagnosis**:
```bash
# Check addon paths
docker compose exec odoo odoo shell -d odoo_dev
# In shell:
import odoo
print(odoo.tools.config['addons_path'])
```

**Fix**:
```bash
# Ensure OCA modules present
ls -la oca-addons/

# Check volume mounts
docker compose exec odoo ls -la /mnt/oca
docker compose exec odoo ls -la /mnt/extra-addons
```

### Hot-Reload Not Working

**Symptom**: Code changes don't reflect in browser

**Fixes**:
1. **Hard refresh**: Ctrl+Shift+R (clears cache)
2. **Check dev mode**: Verify `--dev=reload` in docker-compose.yml
3. **Manual restart**: `docker compose restart odoo`
4. **Clear browser cache**: Developer Tools → Clear Storage

### Permission Denied Errors

**Symptom**: `Permission denied: '/var/lib/odoo/filestore'`

**Fix**:
```bash
# Fix volume permissions
docker compose exec odoo chown -R odoo:odoo /var/lib/odoo
```

---

## Architecture

### Container Stack

```
┌─────────────────────────────────────────────────┐
│ odoo-dev (Odoo 18.0)                            │
│ ├─ /mnt/extra-addons → ./addons (custom)       │
│ ├─ /mnt/oca → ./oca-addons (OCA modules)       │
│ └─ /etc/odoo/odoo.conf → ./config/odoo.conf    │
└─────────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────────┐
│ odoo-dev-db (PostgreSQL 16)                     │
│ └─ Volume: odoo-dev-db-data                     │
└─────────────────────────────────────────────────┘
```

### Directory Structure

```
odoo-dev-sandbox/
├── addons/                    # Custom modules (hot-reload)
│   ├── ipai/                  # Main module (18 CE → 19/EE parity)
│   └── ipai_enterprise_bridge/ # Enterprise bridge
├── oca-addons/                # OCA dependencies (symlink or clone)
├── config/
│   └── odoo.conf              # Odoo configuration
├── docs/
│   └── runbooks/
│       └── DEV_SANDBOX.md     # This file
├── scripts/
│   ├── dev/                   # Development scripts
│   │   ├── up.sh
│   │   ├── down.sh
│   │   ├── reset-db.sh
│   │   ├── health.sh
│   │   └── logs.sh
│   └── verify.sh              # Local verification
├── docker-compose.yml         # Stack definition
├── .env                       # Environment config (git-ignored)
├── .env.example               # Environment template
└── REPORT.md                  # Audit report
```

### Volume Persistence

| Volume | Purpose | Survives `down` | Survives `down -v` |
|--------|---------|-----------------|-------------------|
| odoo-dev-db-data | PostgreSQL data | ✅ Yes | ❌ No |
| odoo-dev-filestore | Odoo attachments | ✅ Yes | ❌ No |
| odoo-dev-pgadmin | pgAdmin config | ✅ Yes | ❌ No |

---

## OCA Integration

### Module Dependencies

The `ipai` module requires 24 OCA modules across 5 functional areas:

**Project Management** (14 modules):
- project_timeline, project_timeline_hr_timesheet
- project_timesheet_time_control, project_task_dependencies
- project_task_parent_completion_blocking, project_task_parent_due_auto
- project_type, project_template
- hr_timesheet_sheet, hr_timesheet_sheet_autodraft
- hr_timesheet_sheet_policy_project_manager, hr_timesheet_sheet_warning
- hr_timesheet_task_domain

**Helpdesk** (3 modules):
- helpdesk_mgmt, helpdesk_mgmt_project, helpdesk_ticket_type

**Field Service** (4 modules):
- base_territory, fieldservice, fieldservice_project, fieldservice_portal

**Quality Management** (4 modules):
- maintenance, quality_control, mgmtsystem, mgmtsystem_quality

**Documents & Reporting** (3 modules):
- dms, knowledge, mis_builder

### External Gantt Dependency

- **devjs_web_gantt**: Third-party Gantt view (not in OCA)
  - GitHub: [devjs-com/gantt_view](https://github.com/devjs-com/gantt_view)
  - Installation: Manual clone into `oca-addons/` or separate directory

### Updating OCA Modules

```bash
# If using symlink (recommended)
cd ~/Documents/GitHub/odoo-ce/addons/external/oca
git pull --all

# If using git submodules
cd oca-addons
git submodule update --remote --merge

# If using manual clones
cd oca-addons
for dir in */; do
  (cd "$dir" && git pull origin 18.0)
done

# Restart Odoo
docker compose restart odoo
```

---

## Verification Commands

Run these after setup to confirm working state:

```bash
# 1. Docker config valid
docker compose config

# 2. Services start cleanly
docker compose up -d

# 3. All containers healthy
docker compose ps

# 4. Odoo responds
curl -I http://localhost:8069

# 5. Logs show successful startup
docker compose logs --tail=200 odoo | grep -i "odoo.*running"

# 6. Database accessible
docker compose exec db psql -U odoo -d postgres -c "\l"

# 7. Run full verification
./scripts/verify.sh
```

**Expected Final Output**:
```
✅ All checks passed

Ready to:
  ./scripts/dev/up.sh
```

---

## Support & Resources

**Repository Issues**: File issues in GitHub repo
**Odoo Docs**: https://www.odoo.com/documentation/18.0
**OCA Guidelines**: https://github.com/OCA/odoo-community.org
**Docker Compose Docs**: https://docs.docker.com/compose

---

**Version History**:
- 1.0.0 (2026-01-18): Initial release with Odoo 18 CE + OCA baseline
