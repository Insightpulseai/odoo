# Colima Profiles for Odoo Development

Colima is a lightweight Docker Desktop alternative for macOS with deterministic configuration and minimal resource overhead.

## Why Colima?

- **Deterministic**: Profile-based configuration in version control
- **Fast**: virtiofs mounts are 2-3x faster than Docker Desktop
- **Lightweight**: Minimal resource usage when idle
- **Free**: Open source, no licensing restrictions
- **Reproducible**: Same environment across all developer machines

## Profile: `odoo`

Optimized for Odoo CE 19.0 development with PostgreSQL 16, Redis, and all IPAI modules.

**Resources**:
- **CPU**: 4 cores
- **Memory**: 8 GB
- **Disk**: 60 GB
- **Filesystem**: virtiofs (fastest for macOS)

**Docker Daemon Configuration**:
- BuildKit enabled (faster multi-stage builds)
- JSON file logging (10MB max, 5 files rotation)
- Overlay2 storage driver (performance)

## Quick Start

### Installation

```bash
# Install Colima and Docker CLI
brew install colima docker docker-compose

# Start Colima with odoo profile
make colima-up

# Verify Docker connection
docker info

# Start Odoo stack
make up
```

### Daily Workflow

```bash
# Start Colima + Odoo stack
make colima-up && make up

# Check status
make ps
make colima-status

# Stop stack (keep Colima running)
make down

# Stop Colima (free resources)
make colima-down
```

## Management Commands

| Command | Purpose |
|---------|---------|
| `make colima-up` | Start Colima with odoo profile |
| `make colima-down` | Stop Colima gracefully |
| `make colima-reset` | Reset Colima (deletes all data) |
| `make colima-status` | Check Colima status |

## Profile Customization

To adjust resources, edit `.colima/odoo.yaml`:

```yaml
cpu: 4      # Adjust based on your Mac
memory: 8   # Adjust based on available RAM
disk: 60    # Adjust based on disk space
```

Then restart:

```bash
make colima-down
make colima-up
```

## Troubleshooting

### Colima won't start

```bash
# Check for conflicting Docker contexts
docker context ls

# Reset to clean state
make colima-reset
```

### Docker daemon not accessible

```bash
# Verify Colima is running
make colima-status

# Restart Colima
make colima-down && make colima-up
```

### Performance issues

```bash
# Check VM resources
colima list -p odoo

# Increase resources in .colima/odoo.yaml
# Then: make colima-down && make colima-up
```

### Disk space issues

```bash
# Clean up Docker data
docker system prune -a --volumes

# Or reset completely
make colima-reset
```

## Docker Desktop Migration

If migrating from Docker Desktop:

1. Stop Docker Desktop
2. Uninstall Docker Desktop (optional)
3. Install Colima: `brew install colima docker docker-compose`
4. Start: `make colima-up`
5. Existing Docker Compose files work unchanged

**Note**: Docker volumes from Docker Desktop are not migrated. Export/import data if needed.

## Technical Details

**Colima Architecture**:
- Lima VM (Linux virtual machine on macOS)
- containerd or Docker runtime
- virtiofs for filesystem mounts (host <-> VM)
- Automatic Docker context management

**Profile Location**: `.colima/odoo.yaml`
**Scripts**: `scripts/colima-*.sh`
**Make Targets**: See `make help`

## Resources

- [Colima GitHub](https://github.com/abiosoft/colima)
- [Lima Project](https://github.com/lima-vm/lima)
- [Docker CLI Documentation](https://docs.docker.com/engine/reference/commandline/cli/)

## Related Documentation

- `docs/ai/DOCKER.md` - Docker Compose configuration
- `.devcontainer/devcontainer.json` - VS Code DevContainer setup
- `docker-compose.yml` - Odoo stack configuration
- `.github/templates/vscode/` - VS Code standards
