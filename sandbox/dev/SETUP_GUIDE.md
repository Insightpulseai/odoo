# Odoo Dev Sandbox - Complete Setup Guide

## Full Ecosystem Configuration

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Odoo CE 19 + EE Parity Development Ecosystem               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   Odoo 19    │◄────►│ PostgreSQL   │                    │
│  │ (port 9069)  │      │   16-alpine  │                    │
│  │              │      │ (port 5433)  │                    │
│  └──────────────┘      └──────────────┘                    │
│         │                                                   │
│         ├─ /mnt/extra-addons → ./addons (ipai_* modules)   │
│         ├─ /mnt/oca → ./oca-addons (24 OCA modules)        │
│         └─ /etc/odoo/odoo.conf → ./config/odoo.conf        │
│                                                             │
│  Optional Tools (--profile tools):                          │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   pgAdmin    │      │   Mailpit    │                    │
│  │ (port 5050)  │      │ (port 8025)  │                    │
│  └──────────────┘      └──────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Prerequisites

### Required Software

- **Docker Desktop** (or alternative like Colima/OrbStack)
  - Download: https://www.docker.com/products/docker-desktop
  - Minimum: 4GB RAM, 20GB disk space

- **Git** (for version control)
  ```bash
  git --version  # Should show 2.x or higher
  ```

### Optional Tools

- **GitHub CLI** (for repo management)
  ```bash
  brew install gh
  ```

---

## 2. Installation Steps

### A. Clone Repository

```bash
# If starting fresh
git clone git@github.com:jgtolentino/odoo-ce.git
cd odoo-ce/sandbox/dev

# If already cloned, navigate to sandbox
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
```

### B. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (optional - defaults work out of the box)
nano .env
```

**Key Environment Variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `ODOO_IMAGE_TAG` | `19.0-ee-parity` | Odoo image version |
| `ODOO_PORT` | `9069` | Odoo web interface port |
| `POSTGRES_PORT` | `5433` | PostgreSQL external port |
| `POSTGRES_PASSWORD` | `odoo_dev_password` | Database password |

### C. Setup OCA Modules

The `ipai` module depends on **24 OCA modules**. You have two options:

**Option 1: Symlink to canonical OCA (Recommended)**
```bash
# If you have the full odoo-ce repo
ln -s ~/Documents/GitHub/odoo-ce/addons/external/oca oca-addons
```

**Option 2: Clone OCA repositories**
```bash
mkdir -p oca-addons
cd oca-addons

# Clone required OCA repos (example - see CLAUDE.md for full list)
git clone https://github.com/OCA/project.git --depth 1 --branch 18.0
git clone https://github.com/OCA/project-timesheet.git --depth 1 --branch 18.0
# ... (24 total repositories)
```

**Required OCA Modules**:
- project_timeline
- project_timeline_hr_timesheet
- project_timesheet_time_control
- project_task_dependencies
- project_task_parent_completion_blocking
- project_task_parent_due_auto
- project_type
- project_template
- hr_timesheet_sheet
- hr_timesheet_sheet_autodraft
- hr_timesheet_sheet_policy_project_manager
- hr_timesheet_sheet_warning
- hr_timesheet_task_domain
- helpdesk_mgmt
- helpdesk_mgmt_project
- helpdesk_ticket_type
- base_territory
- fieldservice
- fieldservice_project
- fieldservice_portal
- maintenance
- quality_control
- mgmtsystem
- mgmtsystem_quality
- dms
- knowledge
- mis_builder

---

## 3. Starting the Ecosystem

### Basic Startup

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev

# Start core services (Odoo + PostgreSQL)
docker compose up -d

# View logs
docker compose logs -f odoo
```

### With Optional Tools

```bash
# Start with pgAdmin and Mailpit
docker compose --profile tools up -d
```

### Using Helper Scripts

```bash
# Start services
./scripts/dev/up.sh

# View logs
./scripts/dev/logs.sh odoo

# Check health
./scripts/dev/health.sh

# Stop services
./scripts/dev/down.sh
```

---

## 4. Accessing Services

### Web Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| **Odoo** | http://localhost:9069 | Database: create new on first login |
| **pgAdmin** | http://localhost:5050 | Email: `admin@localhost.com` / Password: `admin` |
| **Mailpit** | http://localhost:8025 | No login required |

### Database Access

**Via psql (from host)**:
```bash
psql postgresql://odoo:odoo_dev_password@localhost:5433/postgres
```

**Via Docker exec**:
```bash
docker compose exec db psql -U odoo -d postgres
```

**Via pgAdmin**:
1. Open http://localhost:5050
2. Add Server:
   - Name: `Odoo Dev`
   - Host: `db` (or `host.docker.internal` from host)
   - Port: `5432` (internal) or `5433` (from host)
   - Username: `odoo`
   - Password: `odoo_dev_password`

---

## 5. Odoo Configuration Details

### Odoo.conf Breakdown

```ini
[options]
# Addon search paths (order matters)
addons_path = /mnt/extra-addons,/mnt/oca,/usr/lib/python3/dist-packages/odoo/addons

# Database connection
db_host = db                    # Container name
db_port = 5432                  # Internal port
db_user = odoo
db_password = odoo_dev_password
db_maxconn = 64

# Server ports
http_port = 8069                # Internal (mapped to 9069 externally)
longpolling_port = 8072

# Development mode
workers = 0                     # Single-process for hot-reload
max_cron_threads = 1

# Memory limits (relaxed for dev)
limit_memory_hard = 2684354560  # 2.5 GB
limit_memory_soft = 2147483648  # 2 GB
limit_time_cpu = 9999           # No CPU timeout
limit_time_real = 9999          # No real-time timeout

# Master password (for database management)
admin_passwd = admin_dev_password
```

### Development Mode Flags

Set via docker-compose command:
```yaml
command: >
  --dev=reload,qweb,werkzeug,xml
  --limit-time-real=9999
  --limit-time-cpu=9999
```

| Flag | Effect |
|------|--------|
| `reload` | Auto-reload Python code on file changes |
| `qweb` | Auto-reload QWeb templates |
| `werkzeug` | Enable Werkzeug debugger |
| `xml` | Auto-reload XML files (views, data) |

---

## 6. Image Details

### Odoo CE 19 + EE Parity Image

**Image**: `ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity`

**What's Included**:
- Odoo Community Edition 19.0
- 24 OCA modules (pre-installed dependencies)
- IPAI Enterprise Bridge (`ipai_enterprise_bridge`)
- ≥80% Odoo Enterprise Edition feature parity

**Differences from Official Odoo**:

| Aspect | Official `odoo:18.0` | Our `odoo-ce:19.0-ee-parity` |
|--------|---------------------|------------------------------|
| Version | 18.0 | **19.0** |
| OCA Modules | ❌ None | ✅ 24 modules |
| Enterprise Bridge | ❌ No | ✅ `ipai_enterprise_bridge` |
| EE Parity | 0% | **≥80%** |
| Custom Addons | ❌ None | ✅ All `ipai_*` modules |

**Source**: Single source of truth is `docker/docker-compose.ce19.yml` in main repo

---

## 7. Volume Persistence

### Data Volumes

```yaml
volumes:
  odoo-dev-db-data:       # PostgreSQL data
  odoo-dev-filestore:     # Odoo attachments/files
  odoo-dev-pgadmin:       # pgAdmin config
```

**Locations on Host**: Docker manages these (use `docker volume inspect`)

**Backup Volumes**:
```bash
# Backup database
docker compose exec db pg_dump -U odoo postgres > backup.sql

# Restore database
docker compose exec -T db psql -U odoo postgres < backup.sql
```

---

## 8. Network Configuration

**Network**: `odoo-dev-net` (isolated bridge network)

**Why Isolated**: Prevents conflicts with other Docker projects

**Container Hostnames**:
- `db` - PostgreSQL
- `odoo` - Odoo application
- `pgadmin` - pgAdmin (if tools profile)
- `mailpit` - Mailpit (if tools profile)

**Inter-container Communication**:
Containers reference each other by service name (e.g., Odoo connects to `db:5432`)

---

## 9. Development Workflow

### Hot-Reload Workflow

1. **Start services**:
   ```bash
   docker compose up -d
   ```

2. **Make changes** to files in `addons/ipai/` or `addons/ipai_enterprise_bridge/`

3. **Watch logs** for auto-reload:
   ```bash
   docker compose logs -f odoo
   # Look for: "Reloading..." messages
   ```

4. **Refresh browser** (Ctrl+Shift+R to clear cache)

### Module Installation

**First Time Setup**:
1. Access http://localhost:9069
2. Create database
3. Apps → Search for module → Install

**Via CLI**:
```bash
docker compose exec odoo odoo \
  -d <database_name> \
  -i <module_name> \
  --stop-after-init
```

### Database Management

**Create New Database**:
```bash
curl -X POST http://localhost:9069/web/database/create \
  -d "master_pwd=admin_dev_password&name=mydb&lang=en_US&password=admin"
```

**List Databases**:
```bash
docker compose exec db psql -U odoo -l
```

**Drop Database**:
```bash
docker compose exec db dropdb -U odoo <database_name>
```

---

## 10. Troubleshooting

### Common Issues

**Port Already in Use**:
```bash
# Check what's using port 9069
lsof -i :9069

# Kill process or change ODOO_PORT in .env
```

**Database Connection Refused**:
```bash
# Check PostgreSQL health
docker compose exec db pg_isready -U odoo

# Restart database
docker compose restart db
```

**Module Not Found**:
```bash
# Verify addons path
docker compose exec odoo ls /mnt/extra-addons
docker compose exec odoo ls /mnt/oca

# Check odoo.conf addons_path
docker compose exec odoo cat /etc/odoo/odoo.conf | grep addons_path
```

**CSS Error / Old Content**:
```bash
# Run health check
~/Documents/GitHub/odoo-ce/scripts/health/odoo_local_9069.sh

# If healthy, it's browser cache - clear it:
# Chrome: Command + Shift + R
```

### Health Check

**Canonical Health Check**:
```bash
~/Documents/GitHub/odoo-ce/scripts/health/odoo_local_9069.sh
```

Expected output:
- ✅ /web/login HTTP 200
- ✅ Detected Odoo HTML
- ✅ Auto-detected CSS asset
- ✅ CSS content looks normal
- **RESULT: Odoo 9069 HEALTHY**

### Reset Everything

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev

# Stop and remove containers
docker compose down

# Remove volumes (⚠️ deletes all data)
docker volume rm odoo-dev-db-data odoo-dev-filestore odoo-dev-pgadmin

# Start fresh
docker compose up -d
```

---

## 11. Upgrade to Odoo 19

**If running Odoo 18**, use the upgrade script:

```bash
~/Documents/GitHub/odoo-ce/sandbox/dev/upgrade-to-odoo19.sh
```

This will:
1. Stop old Odoo 18 containers
2. Remove old image
3. Pull `ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity`
4. Start Odoo 19.0 + OCA + IPAI Enterprise Bridge

**After upgrade**: Clear browser cache (Command + Shift + R)

---

## 12. Reference Documentation

- **Daily Operations**: `docs/runbooks/DEV_SANDBOX.md`
- **Health Policy**: `~/Documents/GitHub/odoo-ce/docs/runbooks/ODOO_LOCAL_9069_HEALTH.md`
- **Image Alignment**: `IMAGE_ALIGNMENT.md`
- **Sync Guide**: `SYNC_GUIDE.md`
- **Main Project**: `~/Documents/GitHub/odoo-ce/CLAUDE.md`

---

## Quick Commands Cheat Sheet

```bash
# Start/Stop
docker compose up -d                    # Start services
docker compose down                     # Stop services
docker compose restart odoo             # Restart Odoo only

# Logs
docker compose logs -f odoo             # Follow Odoo logs
docker compose logs --tail 50 db        # Last 50 PostgreSQL logs

# Status
docker compose ps                       # List running services
docker ps                               # List all Docker containers

# Database
docker compose exec db psql -U odoo     # Connect to database
docker compose exec db pg_dump -U odoo postgres > backup.sql

# Odoo CLI
docker compose exec odoo odoo --help    # Show Odoo CLI help
docker compose exec odoo odoo -d mydb -i module_name --stop-after-init

# Health
~/Documents/GitHub/odoo-ce/scripts/health/odoo_local_9069.sh

# Upgrade
~/Documents/GitHub/odoo-ce/sandbox/dev/upgrade-to-odoo19.sh
```

---

**Last Updated**: 2026-01-28
**Version**: Odoo 19.0 CE + EE Parity
**Maintained By**: Jake Tolentino
