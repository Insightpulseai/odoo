# Colima Setup Guide

> Lightweight, scriptable Docker runtime for Odoo development on macOS

## Overview

**Colima** is our recommended Docker runtime for local Odoo development, replacing Docker Desktop with:

- ✅ **Fully scriptable** (no GUI required)
- ✅ **Deterministic configuration** (version-controlled profile)
- ✅ **Lower resource overhead** (stops when not needed)
- ✅ **Open source** (MIT license, no commercial restrictions)
- ✅ **Faster** (Apple Virtualization Framework)

## Quick Start

### 1. Install Colima + Docker Tools

```bash
brew install colima docker docker-compose
```

**What this installs:**
- `colima`: Lightweight VM manager using Apple Virtualization
- `docker`: Docker CLI (without Docker Desktop)
- `docker-compose`: Compose CLI for multi-container apps

### 2. Start Colima

```bash
make colima-up
# or
./scripts/colima-up.sh
```

**What happens:**
- Starts Colima VM with `odoo` profile (4 CPU, 8GB RAM, 60GB disk)
- Configures Docker context to point to Colima
- Verifies Docker daemon is responding
- Shows current Docker Compose status

### 3. Start Odoo Services

```bash
make up
# or
docker compose up -d
```

### 4. Verify

```bash
# Check Colima status
make colima-status

# Check Docker daemon
docker info

# Check Odoo services
docker compose ps

# Test Odoo web
curl -I http://localhost:8069/web/health
```

## Daily Workflow

```bash
# Morning: Start VM
make colima-up

# Start Odoo services
make up

# Work...

# Evening: Stop VM (optional, to free resources)
make colima-down
```

## Configuration

### Profile Configuration

Colima uses a YAML profile at `.colima/odoo.yaml`:

```yaml
# VM resources
cpu: 4              # CPU cores
memory: 8           # GB
disk: 60            # GB

# Runtime
runtime: docker

# Fast filesystem (virtiofs)
mount:
  type: virtiofs

# Network
network:
  address: true

# DNS
dns:
  - 1.1.1.1
  - 8.8.8.8
```

### Override Resources

Set environment variables before starting:

```bash
export COLIMA_CPU=8
export COLIMA_MEMORY=16
export COLIMA_DISK=100
make colima-up
```

**Or edit** `.colima/odoo.yaml` directly and restart:

```bash
make colima-down
make colima-up
```

### Recommended Sizing

| Workload | CPU | Memory | Disk |
|----------|-----|--------|------|
| **Minimal** (testing) | 2-4 | 6-8GB | 40GB |
| **Standard** (daily dev) | 4-6 | 8-12GB | 60-80GB |
| **Heavy** (large datasets, many modules) | 8+ | 16GB+ | 100GB+ |

## Commands

### Lifecycle

```bash
# Start VM
make colima-up

# Stop VM gracefully
make colima-down

# Reset VM (DELETES all Docker data)
make colima-reset

# Check VM status
make colima-status
```

### Low-Level Colima Commands

```bash
# List all profiles
colima list

# Show specific profile status
colima status -p odoo

# View profile configuration
cat .colima/odoo.yaml

# View Colima logs
colima logs -p odoo

# Delete profile completely
colima delete -p odoo -f
```

## Troubleshooting

### Issue: Colima won't start

**Symptoms:**
```
Error: failed to start colima: error computing zones
```

**Solution:**
```bash
# Check status
colima status -p odoo

# View logs
colima logs -p odoo

# Nuclear reset
make colima-reset
```

### Issue: Docker context wrong

**Symptoms:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solution:**
```bash
# Check current context
docker context ls

# Switch to Colima
docker context use colima

# Verify
docker info
# Should show "Context: colima"
```

### Issue: Out of disk space

**Symptoms:**
```
Error: no space left on device
```

**Solutions:**

1. **Clean up Docker resources:**
   ```bash
   docker system prune -af --volumes
   ```

2. **Increase disk size** in `.colima/odoo.yaml`:
   ```yaml
   disk: 100  # was: 60
   ```

3. **Restart Colima:**
   ```bash
   make colima-down
   make colima-up
   ```

### Issue: Slow performance

**Possible causes:**
- Not enough CPU/memory allocated
- Wrong filesystem type (should be `virtiofs`)
- Resource contention with other apps

**Solutions:**

1. **Check current allocation:**
   ```bash
   colima list -p odoo
   ```

2. **Increase resources** in `.colima/odoo.yaml`:
   ```yaml
   cpu: 8     # was: 4
   memory: 16 # was: 8
   ```

3. **Verify filesystem type:**
   ```bash
   cat .colima/odoo.yaml | grep -A2 mount
   # Should show: type: virtiofs
   ```

4. **Restart:**
   ```bash
   make colima-down
   make colima-up
   ```

### Issue: Port conflicts (8069, 5432, 6379)

**Symptoms:**
```
Error: Bind for 0.0.0.0:8069 failed: port is already allocated
```

**Solution:**

1. **Find conflicting process:**
   ```bash
   lsof -ti:8069
   # Kill if safe: kill -9 $(lsof -ti:8069)
   ```

2. **Or change ports** in `docker-compose.yml`:
   ```yaml
   services:
     odoo:
       ports:
         - "8070:8069"  # Changed from 8069:8069
   ```

### Issue: Can't connect to services from host

**Symptoms:**
```
curl: (7) Failed to connect to localhost port 8069
```

**Check:**
```bash
# 1. Services running?
docker compose ps

# 2. Port forwarding correct?
docker compose ps --format "table {{.Name}}\t{{.Ports}}"

# 3. Container logs
docker compose logs odoo

# 4. Network connectivity
docker network ls
docker network inspect ipai_default
```

## Migrating from Docker Desktop

### 1. Stop Docker Desktop

```bash
# Quit Docker Desktop app
# (Optional) Uninstall Docker Desktop
```

### 2. Install Colima

```bash
brew install colima docker docker-compose
```

### 3. Start Colima

```bash
make colima-up
```

### 4. Verify Migration

```bash
# Check context
docker info
# Should show "Context: colima-odoo" (not "desktop-linux")

# Test services
make up
docker compose ps
```

### 5. Clean Up (Optional)

Remove Docker Desktop completely:

```bash
# Uninstall Docker Desktop app
# Remove Docker Desktop data
rm -rf ~/Library/Group\ Containers/group.com.docker
rm -rf ~/Library/Containers/com.docker.docker
```

## What Changes After Migration

| Aspect | Docker Desktop | Colima |
|--------|----------------|--------|
| **Startup** | Manual GUI | `make colima-up` |
| **Shutdown** | Manual GUI | `make colima-down` |
| **Configuration** | Settings UI | `.colima/odoo.yaml` |
| **Resource Usage (idle)** | ~1-2GB RAM | 0 (stopped) |
| **Licensing** | Commercial restrictions | MIT (free) |
| **Automation** | Limited | Full CI/CD support |
| **Docker commands** | Same | Same |
| **docker-compose** | Same | Same |

## Advanced Topics

### Multiple Profiles

Create separate profiles for different projects:

```bash
# Create new profile
colima start my-other-project --cpu 2 --memory 4

# Switch between profiles
colima stop -p odoo
colima start -p my-other-project
```

### Auto-Start on Login

Edit `.colima/odoo.yaml`:

```yaml
autoStart: true  # Uncomment this line
```

**Warning:** This will auto-start Colima VM on every login (uses resources even when idle).

### Kubernetes (Not Needed for Odoo)

Colima supports Kubernetes, but we disable it for Docker-only workflow:

```yaml
kubernetes:
  enabled: false  # Keep this false
```

### Custom Docker Daemon Config

Edit `.colima/odoo.yaml`:

```yaml
docker:
  config:
    # Custom daemon settings
    log-driver: json-file
    log-opts:
      max-size: "10m"
      max-file: "5"

    # Registry mirrors (faster pulls)
    registry-mirrors:
      - https://mirror.gcr.io
```

## Comparison: Colima vs Docker Desktop

### When to Use Colima

✅ **Local development** (recommended)
✅ **CI/CD pipelines** (scriptable)
✅ **Resource-constrained machines**
✅ **Commercial use without licensing concerns**
✅ **Open-source projects**

### When Docker Desktop Might Be Preferred

- GUI preference (some users prefer visual interface)
- Kubernetes integration (if you need K8s locally)
- Official Docker support channels

## Resources

- [Colima GitHub](https://github.com/abiosoft/colima)
- [Colima Documentation](https://github.com/abiosoft/colima/blob/main/README.md)
- [Apple Virtualization Framework](https://developer.apple.com/documentation/virtualization)

## Related Documentation

- [Docker Compose Stack](../docker-compose.yml) - Service definitions
- [Makefile](../Makefile) - Quick commands
- [DevContainer](../.devcontainer/) - VS Code integration
