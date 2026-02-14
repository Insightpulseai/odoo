# Docker Setup Guide

Complete guide for Docker Desktop setup, Odoo startup, and troubleshooting.

---

## Quick Start

### One-Command Startup (Recommended)

```bash
./scripts/start-odoo.sh
```

This script:
- ✅ Checks if Docker Desktop is running
- ✅ Starts services if needed (`docker compose up -d`)
- ✅ Waits for PostgreSQL to be ready
- ✅ Waits for Odoo health check (max 90s)
- ✅ Opens browser to http://localhost:8069

**Flags:**
- `--no-browser` - Don't auto-open browser

---

## Manual Docker Desktop Startup

If Docker Desktop is not running:

1. **Open Docker Desktop**
   - Press `⌘ + Space` (Spotlight)
   - Type "Docker"
   - Press Enter

2. **Wait for Docker to start**
   - Look for "Docker Desktop is running" in menu bar (whale icon)
   - Usually takes 15-30 seconds

3. **Start Odoo services**
   ```bash
   docker compose up -d
   ```

4. **Wait for Odoo to be ready** (~60-90 seconds)
   ```bash
   # Check health
   curl -sf http://localhost:8069/web/health
   ```

5. **Access Odoo**
   - Open browser to http://localhost:8069

---

## Health Check

Run comprehensive health check:

```bash
./scripts/docker-health.sh
```

**Output shows:**
- ✅ Docker Desktop status
- ✅ Compose services (3/3 running)
- ✅ PostgreSQL readiness
- ✅ Redis connectivity
- ✅ Odoo web health

**Flags:**
- `--wait` - Wait for Docker Desktop to start (max 2 min)
- `--fix` - Auto-run `docker compose up -d` if services down

---

## Auto-Start Setup (Optional)

Enable Docker Desktop to start automatically on login:

```bash
# Check current status
./scripts/setup-docker-autostart.sh --status

# Enable auto-start
./scripts/setup-docker-autostart.sh --enable

# Disable auto-start
./scripts/setup-docker-autostart.sh --disable
```

**Trade-offs:**
- ✅ **Pro**: Docker always ready, no manual startup
- ❌ **Con**: Uses ~1-2GB RAM even when not developing

**Recommendation**: Enable if you work with Odoo daily, otherwise manual start is fine.

---

## Verification Steps

After startup, verify all services:

### 1. Check Docker Daemon
```bash
docker info
# Should output system info without errors
```

### 2. Check Services Status
```bash
docker compose ps
# Should show 3 services running:
#   - odoo-core (healthy)
#   - odoo-db (healthy)
#   - odoo-redis (healthy)
```

### 3. Check Database
```bash
docker compose exec db pg_isready -U odoo -d odoo_dev
# Expected: "odoo_dev:5432 - accepting connections"
```

### 4. Check Redis
```bash
docker compose exec redis redis-cli ping
# Expected: "PONG"
```

### 5. Check Odoo Web
```bash
curl -sf http://localhost:8069/web/health
# Should return 200 OK (no output is good)
```

### 6. Full Health Check
```bash
./scripts/docker-health.sh
# Should show all green checkmarks
```

---

## Troubleshooting

### Issue: `ERR_CONNECTION_REFUSED` on localhost:8069

**Cause**: Docker Desktop not running or services not started

**Fix**:
1. Check Docker Desktop is running (whale icon in menu bar)
2. If not running: Open Docker Desktop app
3. Wait for "Docker Desktop is running"
4. Run: `./scripts/start-odoo.sh`

---

### Issue: Docker Desktop won't start

**Symptoms**:
- Whale icon stuck in menu bar
- "Docker Desktop starting..." for >5 minutes
- Error messages in Docker Desktop

**Fixes**:

1. **Restart Docker Desktop**
   ```bash
   osascript -e 'quit app "Docker"'
   sleep 5
   open -a Docker
   ```

2. **Reset Docker Desktop** (nuclear option)
   - Click whale icon → Troubleshoot → Reset to factory defaults
   - **WARNING**: This deletes all containers, images, volumes

3. **Check system resources**
   - Docker needs at least 2GB RAM free
   - Check Activity Monitor → Memory tab
   - Close other applications if needed

4. **Check Docker Desktop logs**
   ```bash
   tail -f ~/Library/Containers/com.docker.docker/Data/log/vm/dockerd.log
   ```

---

### Issue: Services fail health checks

**Symptoms**:
- `docker compose ps` shows "unhealthy" status
- Health check script shows failures

**Diagnosis**:
```bash
# Check service logs
docker compose logs odoo    # Odoo logs
docker compose logs db      # PostgreSQL logs
docker compose logs redis   # Redis logs
```

**Common causes:**

1. **Odoo still starting**
   - Health check can take up to 90 seconds
   - Wait and retry: `./scripts/docker-health.sh`

2. **Database migration in progress**
   - Check logs: `docker compose logs odoo | grep -i migr`
   - Large migrations can take 5+ minutes
   - Be patient, wait for "HTTP service (werkzeug) running"

3. **Port conflict (8069 already in use)**
   ```bash
   # Check what's using port 8069
   lsof -i :8069

   # Kill the process if needed
   kill -9 <PID>

   # Restart Odoo
   docker compose restart odoo
   ```

4. **Module installation error**
   ```bash
   # Check for errors
   docker compose logs odoo | grep -i error

   # Common fix: reset addons path
   docker compose down
   docker compose up -d
   ```

---

### Issue: Slow startup performance

**Symptoms**:
- Takes >2 minutes for Odoo to be ready
- Health check times out

**Optimizations**:

1. **Increase Docker resources**
   - Docker Desktop → Settings → Resources
   - Increase CPUs to 4
   - Increase Memory to 8GB
   - Click "Apply & Restart"

2. **Disable unnecessary modules**
   - Edit `odoo19/odoo.conf`
   - Comment out unused modules in `addons_path`
   - Restart: `docker compose restart odoo`

3. **Use volume caching** (macOS optimization)
   - Already configured in `docker-compose.yml`:
     ```yaml
     volumes:
       - ./odoo19:/odoo:delegated
     ```

4. **Prune unused Docker data**
   ```bash
   # Remove old images/volumes
   docker system prune -a --volumes

   # WARNING: This deletes unused data
   # Confirm with 'y' when prompted
   ```

---

### Issue: Database connection errors

**Symptoms**:
- `FATAL: database "odoo_dev" does not exist`
- `could not connect to server`

**Fixes**:

1. **Check database exists**
   ```bash
   docker compose exec db psql -U odoo -l
   # Should show "odoo_dev" in the list
   ```

2. **Create database manually** (if missing)
   ```bash
   docker compose exec db psql -U odoo -c "CREATE DATABASE odoo_dev;"
   ```

3. **Reset database** (nuclear option)
   ```bash
   # WARNING: Deletes all data
   docker compose down -v
   docker compose up -d

   # Wait for Odoo to initialize new database
   ./scripts/start-odoo.sh
   ```

4. **Check PostgreSQL logs**
   ```bash
   docker compose logs db | tail -50
   ```

---

### Issue: Redis connection errors

**Symptoms**:
- `Error 111 connecting to redis:6379. Connection refused.`
- Cache not working

**Fixes**:

1. **Check Redis is running**
   ```bash
   docker compose ps redis
   # Should show "running" status
   ```

2. **Test Redis connection**
   ```bash
   docker compose exec redis redis-cli ping
   # Expected: "PONG"
   ```

3. **Restart Redis**
   ```bash
   docker compose restart redis
   ```

4. **Check Redis logs**
   ```bash
   docker compose logs redis
   ```

---

## Common Workflows

### Daily Development

```bash
# Morning startup
./scripts/start-odoo.sh

# Work on Odoo...

# Evening shutdown (optional, to free RAM)
docker compose down
```

### After Code Changes

Most changes auto-reload via Odoo's watchdog. If manual restart needed:

```bash
# Restart just Odoo (fast)
docker compose restart odoo

# Full restart (if needed)
docker compose down
docker compose up -d
```

### After Module Installation

```bash
# Install module via Odoo UI
# Then update module list:
docker compose exec odoo odoo -c /odoo/odoo.conf -u <module_name> --stop-after-init

# Restart Odoo
docker compose restart odoo
```

### Check Logs

```bash
# Follow all logs
docker compose logs -f

# Follow Odoo only
docker compose logs -f odoo

# Last 50 lines
docker compose logs odoo --tail 50
```

---

## Script Reference

| Script | Purpose |
|--------|---------|
| `./scripts/start-odoo.sh` | Smart one-command startup |
| `./scripts/docker-health.sh` | Comprehensive health check |
| `./scripts/setup-docker-autostart.sh` | Auto-start configuration |

**Recommended daily workflow:**
```bash
./scripts/start-odoo.sh    # Morning
# Work...
docker compose down        # Evening (optional)
```

---

## Architecture Notes

### Services

- **odoo-core**: Odoo 19.0 application server
  - Port: 8069 (HTTP)
  - Health check: `/web/health`
  - Startup: ~60-90 seconds

- **odoo-db**: PostgreSQL 16
  - Port: 5432 (internal)
  - Database: `odoo_dev`
  - Health check: `pg_isready`

- **odoo-redis**: Redis 7
  - Port: 6379 (internal)
  - Health check: `redis-cli ping`

### Volumes

- `./odoo19:/odoo:delegated` - Odoo configuration and addons (cached)
- `odoo_db_data` - PostgreSQL data (persistent)
- `odoo_redis_data` - Redis data (persistent)

### Networks

- `odoo_network` - Internal bridge network for service communication

---

## Additional Resources

- [Docker Desktop Documentation](https://docs.docker.com/desktop/mac/)
- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [PostgreSQL Docker Documentation](https://hub.docker.com/_/postgres)
- [Redis Docker Documentation](https://hub.docker.com/_/redis)

---

## Getting Help

If issues persist:

1. **Check health status**
   ```bash
   ./scripts/docker-health.sh
   ```

2. **Collect logs**
   ```bash
   docker compose logs > /tmp/odoo-logs.txt
   ```

3. **Check system resources**
   - Activity Monitor → Memory/CPU tabs
   - Ensure Docker has 4GB+ RAM allocated

4. **Try clean restart**
   ```bash
   docker compose down
   docker compose up -d --build
   ```

5. **Create GitHub issue** with:
   - Output of `./scripts/docker-health.sh`
   - Relevant logs from `docker compose logs`
   - macOS version and Docker Desktop version
