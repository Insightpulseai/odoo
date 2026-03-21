# Dev Container Guide

Complete guide to using the Odoo Dev Container for development.

## Quick Start

### Prerequisites

1. **Install Required Software**:
   - [VS Code](https://code.visualstudio.com/)
   - [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop) (or Docker + Docker Compose)

2. **Verify Docker is Running**:
   ```bash
   docker --version
   docker compose version
   ```

### Open in Container

**Method 1: Command Palette**
1. Open project in VS Code: `code .`
2. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
3. Select: "Dev Containers: Reopen in Container"
4. Wait for setup to complete (~3-5 minutes first time)

**Method 2: Workspace File**
1. Open workspace: `code odoo.code-workspace`
2. Use Command Palette: "Dev Containers: Reopen in Container"

**Method 3: Notification Popup**
- VS Code may show popup: "Reopen in Container"
- Click the button to start

### Verify Setup

After container builds and post-create completes:

```bash
# Check PostgreSQL
psql -U odoo -d odoo_dev -c "SELECT version();"

# Check Odoo accessibility
curl -I http://localhost:8069/web/login

# Check Docker access (Docker-outside-of-Docker)
docker ps

# Check installed tools
python --version  # Should be 3.12+
node --version    # Should be LTS
pnpm --version
uv --version
specify --version
```

## Features

### Development Tools

- **Python 3.12** with development tools:
  - black (formatter)
  - flake8 (linter)
  - isort (import organizer)
  - pytest (testing framework)
  - pre-commit (Git hooks)

- **Node.js LTS** with package managers:
  - pnpm (via corepack)
  - npm

- **Docker-outside-of-Docker** (DOOD):
  - Access host Docker daemon from container
  - Manage Docker containers and images
  - Run Docker Compose commands

- **Spec Kit Integration**:
  - specify-cli pre-installed
  - Spec kit commands available (`/speckit.*`)

### VS Code Extensions

Pre-installed extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- Docker (ms-azuretools.vscode-docker)
- GitLens (eamodio.gitlens)
- Git Graph (mhutchie.git-graph)
- GitHub Copilot (GitHub.copilot)
- Claude Code (anthropic.claude-code)

### Workspace Organization

The workspace file (`odoo.code-workspace`) organizes folders logically:

```
📁 Odoo (Root)           # Root directory
📁 IPAI Modules          # addons/ipai/
📁 OCA Modules           # addons/oca/
📁 Infrastructure        # infra/
📁 Scripts               # scripts/
📁 Documentation         # docs/
📁 Specs                 # spec/
```

Benefits:
- Logical folder separation in sidebar
- Folder-specific settings
- Better navigation for monorepo
- Shared workspace configuration

## Services

### Default Services (Auto-Start)

Only essential services start automatically:

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL 16 | 5432 (internal), 5433 (host) | Database backend |
| Redis 7 | 6379 (internal) | Session store / cache |
| Odoo 19 CE | 8069, 8072 | ERP application |

### Optional Services (Profile: tools)

Start additional tools with profile flag:

```bash
docker compose --profile tools up -d
```

| Service | Port | Purpose |
|---------|------|---------|
| pgAdmin 4 | 5050 | Database admin UI |
| Mailpit | 8025 (web), 1025 (SMTP) | Email testing |

**Access URLs**:
- pgAdmin: http://localhost:5050
- Mailpit: http://localhost:8025
- Odoo: http://localhost:8069

### Service Management

```bash
# Start all default services
docker compose up -d

# Start with tools profile
docker compose --profile tools up -d

# View running services
docker compose ps

# View logs
docker compose logs -f odoo
docker compose logs -f db

# Restart a service
docker compose restart odoo

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ data loss)
docker compose down -v
```

## Database Management

### Three Databases Created Automatically

The post-create script creates three databases:

| Database | Purpose | Created By |
|----------|---------|------------|
| `odoo_dev` | Default development database | post-create.sh |
| `odoo_stage` | Staging/testing database | post-create.sh |
| `odoo_prod` | Production-like testing | post-create.sh |

### Switch Database

**Method 1: Environment Variable**
```bash
# Edit .devcontainer/devcontainer.env
ODOO_DB=odoo_stage

# Rebuild container
# Command Palette: "Dev Containers: Rebuild Container"
```

**Method 2: Command Line**
```bash
docker compose exec odoo odoo -d odoo_stage -u all
```

**Method 3: Direct Connection**
```bash
# Connect to specific database
psql -U odoo -d odoo_stage

# List all databases
psql -U odoo -l
```

### Database Operations

```bash
# Create new database
docker compose exec db createdb -U odoo my_custom_db

# Drop database (⚠️ data loss)
docker compose exec db dropdb -U odoo my_custom_db

# Backup database
docker compose exec db pg_dump -U odoo odoo_dev > backup.sql

# Restore database
docker compose exec -T db psql -U odoo odoo_dev < backup.sql

# Connect to PostgreSQL
docker compose exec db psql -U odoo -d odoo_dev
```

## Customization

### Environment Variables

1. Copy template:
   ```bash
   cp .devcontainer/devcontainer.env.example .devcontainer/devcontainer.env
   ```

2. Edit values:
   ```env
   # Example customizations
   ODOO_DB=my_custom_db
   ODOO_LOG_LEVEL=warn
   POSTGRES_PASSWORD=securepassword
   ```

3. Rebuild container:
   - Command Palette: "Dev Containers: Rebuild Container"

### Available Variables

See `.devcontainer/devcontainer.env.example` for complete list:

- **Odoo**: ODOO_DB, ODOO_LOG_LEVEL, ODOO_DEV_MODE, ODOO_PORT
- **PostgreSQL**: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT
- **Tools**: PGADMIN_EMAIL, PGADMIN_PASSWORD, MAILPIT_WEB_PORT

### Custom Addons Path

Add custom addon directories (advanced):

1. Edit `.devcontainer/devcontainer.env`:
   ```env
   CUSTOM_ADDONS_PATH=/workspace/my_addons
   ```

2. Mount volume in `.devcontainer/docker-compose.devcontainer.yml`:
   ```yaml
   services:
     odoo:
       volumes:
         - ./my_addons:/workspace/my_addons:ro
   ```

3. Update Odoo command with new path

## Odoo Development Workflow

### Install Modules

```bash
# Install single module
docker compose exec odoo odoo -d odoo_dev -i ipai_expense --stop-after-init

# Install multiple modules
docker compose exec odoo odoo -d odoo_dev -i base,sale,purchase --stop-after-init

# Install all IPAI modules (⚠️ may take time)
docker compose exec odoo odoo -d odoo_dev -i all --stop-after-init
```

### Update Modules

```bash
# Update single module
docker compose exec odoo odoo -d odoo_dev -u ipai_expense --stop-after-init

# Update all modules
docker compose exec odoo odoo -d odoo_dev -u all --stop-after-init
```

### Development Mode

The Dev Container runs Odoo in full development mode:

- **Auto-reload**: Code changes trigger automatic reload
- **Debug logging**: All log levels enabled
- **Asset regeneration**: CSS/JS automatically rebuilt
- **No caching**: Avoid stale cached data

Override in `.devcontainer/devcontainer.env`:
```env
ODOO_DEV_MODE=all
ODOO_LOG_LEVEL=debug
```

### Run Tests

```bash
# Run Odoo module tests
docker compose exec odoo odoo -d odoo_dev --test-enable --stop-after-init

# Run Python tests with pytest
pytest

# Run tests with coverage
pytest --cov=addons/ipai --cov-report=html
```

### Access Odoo Shell

```bash
# Odoo shell (Python REPL with ORM access)
docker compose exec odoo odoo shell -d odoo_dev

# PostgreSQL shell
docker compose exec db psql -U odoo -d odoo_dev
```

## Troubleshooting

### PostgreSQL Connection Fails

**Symptoms**: `psql: connection refused` or `database does not exist`

**Solutions**:

1. Check database service health:
   ```bash
   docker compose ps
   # db service should show "healthy"
   ```

2. View database logs:
   ```bash
   docker compose logs db
   ```

3. Retry post-create setup:
   ```bash
   ./.devcontainer/scripts/post-create.sh
   ```

4. Verify database exists:
   ```bash
   docker compose exec db psql -U odoo -l
   ```

### Docker Socket Not Accessible

**Symptoms**: `docker: command not found` or `permission denied`

**Solutions**:

1. Ensure Docker Desktop is running on host

2. Check Docker access from container:
   ```bash
   docker ps
   ```

3. On Linux, may need Docker group permissions:
   ```bash
   sudo usermod -aG docker $USER
   ```

### Odoo Not Starting

**Symptoms**: `curl: connection refused` to localhost:8069

**Solutions**:

1. Check Odoo logs:
   ```bash
   docker compose logs odoo
   ```

2. Verify database exists:
   ```bash
   docker compose exec db psql -U odoo -l | grep odoo_dev
   ```

3. Check addons path:
   ```bash
   docker compose exec odoo ls -la /mnt/extra-addons/ipai
   ```

4. Restart Odoo service:
   ```bash
   docker compose restart odoo
   docker compose logs -f odoo
   ```

### Port Already in Use

**Symptoms**: `bind: address already in use`

**Solutions**:

1. Find process using port:
   ```bash
   # macOS/Linux
   lsof -i :8069

   # Windows
   netstat -ano | findstr :8069
   ```

2. Change port in `.devcontainer/devcontainer.env`:
   ```env
   ODOO_PORT=8070
   ```

3. Rebuild container

### Post-Create Script Hangs

**Symptoms**: Dev Container setup stuck during post-create

**Solutions**:

1. Check Docker Compose status:
   ```bash
   docker compose -f /workspace/docker-compose.yml ps
   ```

2. Manual service start:
   ```bash
   docker compose -f /workspace/docker-compose.yml up -d
   ```

3. Skip post-create temporarily:
   - Comment out `postCreateCommand` in `devcontainer.json`
   - Rebuild container
   - Run post-create manually after startup

### Slow Performance

**Symptoms**: Odoo slow to load, database queries slow

**Solutions**:

1. **Increase Docker resources** (Docker Desktop settings):
   - CPU: 4+ cores
   - Memory: 8GB+ RAM
   - Disk: Use cached volumes

2. **Optimize PostgreSQL settings** (already tuned in docker-compose.yml):
   - shared_buffers: 256MB
   - effective_cache_size: 1GB
   - work_mem: 16MB

3. **Use volume caching** (already configured):
   - `:cached` flag on volume mounts
   - Named volumes for databases

4. **Disable unnecessary services**:
   ```bash
   # Stop tools profile
   docker compose --profile tools down
   ```

## Advanced Topics

### Multiple Odoo Versions

Run different Odoo versions side-by-side:

1. Create version-specific compose file: `docker-compose.odoo18.yml`
2. Change image: `odoo:18`
3. Use different ports: `8068:8069`
4. Separate database: `odoo18_dev`

### Custom Python Packages

Install additional Python packages:

1. Add to `requirements.txt` in project root
2. Rebuild container:
   ```bash
   # Command Palette: "Dev Containers: Rebuild Container"
   ```

OR install interactively:
```bash
pip install package-name
```

### Pre-commit Hooks

The post-create script installs pre-commit hooks automatically.

**Verify hooks**:
```bash
pre-commit --version
pre-commit run --all-files
```

**Update hooks**:
```bash
pre-commit autoupdate
pre-commit install
```

### Remote Container (Cloud Development)

Use Dev Container on remote machine:

1. Install "Remote - SSH" extension
2. Connect to remote host
3. Open project folder
4. Use "Reopen in Container" command

**Benefits**:
- Powerful cloud resources
- Consistent environment
- Develop from anywhere

## VS Code Tips

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+Shift+P` / `Ctrl+Shift+P` | Command Palette |
| `Cmd+P` / `Ctrl+P` | Quick file open |
| `Cmd+Shift+F` / `Ctrl+Shift+F` | Search across files |
| `F5` | Start debugging |
| `Cmd+B` / `Ctrl+B` | Toggle sidebar |

### Workspace Tasks

Pre-configured tasks (accessible via `Cmd+Shift+B`):

- **Odoo: Start Dev** - Start Docker Compose services
- **Odoo: Logs** - Tail Odoo logs
- **Odoo: Restart** - Restart Odoo service
- **Lint: Python** - Run black + flake8
- **Test: Run All** - Execute pytest

### Launch Configurations

Debug Odoo directly from VS Code:

1. Press `F5` or use "Run and Debug" sidebar
2. Select "Odoo: Debug" configuration
3. Set breakpoints in Python files
4. Debug with full IDE integration

## Best Practices

### Daily Workflow

1. **Open workspace**: `code odoo.code-workspace`
2. **Reopen in container** if not already
3. **Start services**: Usually auto-started
4. **Verify health**: Check http://localhost:8069
5. **Develop**: Edit code, changes auto-reload
6. **Test**: Run tests before committing
7. **Commit**: Pre-commit hooks run automatically

### Database Hygiene

- **Use odoo_dev** for regular development
- **Use odoo_stage** for testing migrations/updates
- **Use odoo_prod** for production-like validation
- **Backup before risky operations**: `pg_dump` to file
- **Reset when needed**: Drop and recreate database

### Performance Tips

- **Use cached volumes** (already configured)
- **Allocate sufficient Docker resources** (4+ cores, 8GB+ RAM)
- **Close unused services** (stop tools profile if not needed)
- **Use selective module updates** (avoid `-u all`)
- **Enable query logging only when debugging** (performance impact)

### Security

- **Never commit** `.devcontainer/devcontainer.env` (gitignored)
- **Use strong passwords** for production-like databases
- **Rotate credentials** regularly
- **Limit exposed ports** (only forward what you need)
- **Review Docker Compose** before running unknown configurations

## Resources

### Documentation

- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [Dev Containers Specification](https://containers.dev/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Project Documentation

- [CLAUDE.md](../../CLAUDE.md) - Odoo project SSOT
- [SANDBOX.md](../../SANDBOX.md) - Sandbox environments guide
- [ODOO_EXECUTION.md](../ODOO_EXECUTION.md) - Odoo execution patterns
- [Spec Kit Guide](../.specify/README.md) - Spec-driven development

### Tools & Extensions

- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [pgAdmin 4](https://www.pgadmin.org/)
- [Mailpit](https://mailpit.axllent.org/)

---

**Questions?** Create an issue in the project repository or consult [TROUBLESHOOTING.md](../TROUBLESHOOTING.md).
