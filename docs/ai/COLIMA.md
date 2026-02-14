# Colima Setup - Docker Desktop Alternative

**Purpose**: Deterministic, reproducible Docker daemon for Odoo development on macOS

**Status**: ✅ Production-ready
**Profile**: `.colima/odoo.yaml`
**Scripts**: `scripts/colima-*.sh`
**Make Targets**: `make colima-{up,down,reset,status}`

---

## Quick Reference

| Task | Command |
|------|---------|
| **First-time setup** | `brew install colima docker docker-compose` |
| **Start Colima** | `make colima-up` |
| **Start Odoo stack** | `make up` |
| **Stop stack** | `make down` |
| **Stop Colima** | `make colima-down` |
| **Reset (nuclear)** | `make colima-reset` |
| **Check status** | `make colima-status` |

---

## Why Colima?

### vs Docker Desktop

| Feature | Colima | Docker Desktop |
|---------|--------|----------------|
| **Cost** | Free | Free (personal), Paid (enterprise) |
| **Performance** | virtiofs (2-3x faster) | gRPC FUSE |
| **Resources** | Lightweight | Heavy background processes |
| **Configuration** | YAML profiles in git | UI-based, not version-controlled |
| **Reproducibility** | 100% deterministic | Environment-dependent |
| **Updates** | brew upgrade | Manual downloads |

### Key Benefits

1. **Deterministic**: Profile in version control = same environment for all devs
2. **Fast**: virtiofs mounts eliminate filesystem overhead
3. **Lightweight**: Only runs when needed, minimal idle resources
4. **Enterprise-compatible**: No licensing restrictions
5. **DevContainer-compatible**: Works with VS Code DevContainers

---

## Architecture

```
macOS Host
  └─ Lima VM (Linux)
       ├─ Docker daemon
       ├─ containerd runtime
       └─ virtiofs mount (host <-> VM)
            └─ /Users/tbwa/Documents/GitHub/Insightpulseai/odoo
```

**Key Components**:
- **Colima**: CLI wrapper for Lima with Docker runtime
- **Lima**: Lightweight Linux VM on macOS (like WSL2 on Windows)
- **virtiofs**: Fast filesystem sharing between macOS and Linux VM
- **Docker CLI**: Standard Docker client (same as Docker Desktop)

---

## Profile Configuration

**File**: `.colima/odoo.yaml`

```yaml
# VM Resources
cpu: 4
memory: 8
disk: 60

# Filesystem (virtiofs = fastest)
mount:
  type: virtiofs

# Docker daemon
docker:
  features:
    buildkit: true
  config:
    log-driver: json-file
    log-opts:
      max-size: "10m"
      max-file: "5"
    storage-driver: overlay2
```

**Customization**: Edit `.colima/odoo.yaml`, then `make colima-down && make colima-up`

---

## Scripts Reference

### colima-up.sh

**Purpose**: Start Colima with odoo profile, verify Docker connection

**Process**:
1. Check if profile exists at `.colima/odoo.yaml`
2. Start Colima with profile (or skip if already running)
3. Verify Docker daemon accessible
4. Show Docker Compose status
5. Display VM resources

**Usage**:
```bash
./scripts/colima-up.sh
# or
make colima-up
```

**Exit codes**:
- `0`: Success (Colima running, Docker accessible)
- `1`: Failure (profile missing, startup failed, Docker inaccessible)

---

### colima-down.sh

**Purpose**: Gracefully stop Colima and Docker Compose services

**Process**:
1. Check if Colima is running
2. Stop Docker Compose services (if any)
3. Stop Colima VM
4. Verify shutdown

**Usage**:
```bash
./scripts/colima-down.sh
# or
make colima-down
```

**Exit codes**:
- `0`: Success (Colima stopped or wasn't running)

---

### colima-reset.sh

**Purpose**: Nuclear option - delete Colima VM and all Docker data

⚠️ **WARNING**: Destroys all containers, images, volumes, networks

**Process**:
1. Prompt for confirmation (`yes` required)
2. Stop Colima if running
3. Delete Colima profile (VM + all Docker data)
4. Start fresh Colima instance

**Usage**:
```bash
./scripts/colima-reset.sh
# or
make colima-reset
```

**Exit codes**:
- `0`: Reset complete
- `0`: Cancelled by user

**When to use**:
- Docker daemon corrupted or unresponsive
- Filesystem issues in VM
- Need to clear all Docker data
- After Colima/Lima version upgrade issues

---

## Daily Workflow

### Morning (start development)

```bash
# Start Colima + Odoo stack
make colima-up && make up

# Verify services
make ps
make health
```

### Evening (stop development)

```bash
# Stop Odoo stack (keep Colima running)
make down

# Or stop everything (free resources)
make colima-down
```

### When switching projects

```bash
# Colima supports multiple profiles
colima start -p project-a
colima start -p project-b

# This repo uses 'odoo' profile
make colima-status  # Shows 'odoo' profile
```

---

## Integration with CI/CD

**DevContainer**: Colima is **not** used in DevContainers (DevContainer manages its own Docker-in-Docker)

**GitHub Actions**: Colima is **not** used (Actions has Docker daemon)

**Local Development Only**: Colima is exclusively for local macOS development

---

## Troubleshooting

### Problem: `make colima-up` fails with "profile not found"

**Cause**: `.colima/odoo.yaml` missing

**Solution**:
```bash
# Verify file exists
ls -la .colima/odoo.yaml

# If missing, check git status
git status .colima/
```

---

### Problem: Docker commands fail with "Cannot connect to daemon"

**Cause**: Colima not running or wrong Docker context

**Solution**:
```bash
# Check Colima status
make colima-status

# Check Docker context
docker context ls
# Should show 'colima-odoo' as active

# Force restart
make colima-down && make colima-up
```

---

### Problem: Slow filesystem performance

**Cause**: Not using virtiofs mount type

**Solution**:
```bash
# Verify mount type in profile
grep -A2 "^mount:" .colima/odoo.yaml
# Should show: type: virtiofs

# If different, edit and restart
vim .colima/odoo.yaml
make colima-down && make colima-up
```

---

### Problem: Out of disk space in VM

**Cause**: Docker images/volumes accumulated

**Solution**:
```bash
# Clean up Docker data
docker system prune -a --volumes

# Or reset completely
make colima-reset
```

---

### Problem: Colima conflicts with Docker Desktop

**Cause**: Both running simultaneously

**Solution**:
```bash
# Stop Docker Desktop
# Uninstall Docker Desktop (optional)

# Start Colima
make colima-up

# Verify correct daemon
docker context ls  # Should show colima-odoo active
```

---

## Docker Desktop Migration

**Before migration**:
1. Export any important data from Docker Desktop volumes
2. Note down running containers and their configurations

**Migration steps**:
```bash
# 1. Stop Docker Desktop
# 2. Install Colima
brew install colima docker docker-compose

# 3. Start Colima with odoo profile
make colima-up

# 4. Verify
docker info  # Should show 'Colima' runtime
make ps      # Should work same as before

# 5. (Optional) Uninstall Docker Desktop
```

**Note**: Docker volumes from Docker Desktop are **not** automatically migrated

---

## Performance Tuning

### Adjust Resources

Edit `.colima/odoo.yaml`:

```yaml
# For powerful MacBook Pro
cpu: 8
memory: 16

# For MacBook Air
cpu: 4
memory: 8

# For M-series Macs (adjust based on model)
cpu: 6
memory: 12
```

Then restart: `make colima-down && make colima-up`

---

### Enable Registry Mirrors (optional)

For faster image pulls:

```yaml
docker:
  config:
    registry-mirrors:
      - https://mirror.gcr.io
```

---

### BuildKit Cache (enabled by default)

Profile already enables BuildKit for faster builds:

```yaml
docker:
  features:
    buildkit: true
```

---

## Advanced Usage

### Multiple Profiles

```bash
# Start different profile
colima start -p other-project

# Switch between profiles
colima stop -p odoo
colima start -p other-project

# List all profiles
colima list
```

---

### Custom Docker Daemon Config

Edit `.colima/odoo.yaml`:

```yaml
docker:
  config:
    # Custom settings
    log-level: debug
    insecure-registries:
      - my-registry:5000
```

---

### Auto-start on Login (optional)

Edit `.colima/odoo.yaml`:

```yaml
autoStart: true
```

**Note**: Not recommended for development (wastes resources when not coding)

---

## Related Documentation

- `.colima/README.md` - Profile documentation
- `docs/ai/DOCKER.md` - Docker Compose configuration
- `.devcontainer/devcontainer.json` - DevContainer setup
- `.github/templates/vscode/` - VS Code standards

---

## Resources

- [Colima GitHub](https://github.com/abiosoft/colima)
- [Lima Project](https://github.com/lima-vm/lima)
- [Docker CLI Documentation](https://docs.docker.com/engine/reference/commandline/cli/)
- [virtiofs Performance](https://github.com/lima-vm/lima/blob/master/docs/mount.md#virtiofs)

---

**Last Updated**: 2026-02-14
**Profile Version**: 1.0
**Tested**: macOS 14+ (Intel & Apple Silicon)
