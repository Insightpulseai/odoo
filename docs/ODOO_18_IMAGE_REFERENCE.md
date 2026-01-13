# Odoo 18.0 Official Docker Image Reference

Complete reference for the official `odoo:18.0` Docker image - naming conventions, layers, configurations, and deployment patterns.

---

## Image Information

**Official Image**: `docker.io/library/odoo:18.0`
**Base OS**: Ubuntu 24.04 LTS
**Architecture**: Multi-arch (amd64, arm64)
**Maintainer**: Odoo S.A. <info@odoo.com>
**Image Size**: ~2 GB
**Release Date**: 2025-12-24

**Digest**: `sha256:1ba7ab9783cd2b08a875077dc3c744b0dcbe7eb0f78ac354a1c7a658f5455749`
**Image ID**: `sha256:87fb9d6c9a921c4c94d4c3c31831e32dd2cd51d2dd4b1b6a33253e57f2f6fa35`

---

## Naming Conventions

### Official Tags

**Version Tags**:
```
odoo:18.0           # Latest Odoo 18 (recommended for production)
odoo:18             # Alias for odoo:18.0
odoo:latest         # Latest stable release (currently 18.0)
```

**Specific Release Tags**:
```
odoo:18.0-20251222  # Date-stamped release (YYYYMMDD format)
odoo:18.0-latest    # Latest 18.0 release
```

**Edition Tags** (if available):
```
odoo:18.0           # Community Edition (default)
# Note: Enterprise edition not available via Docker Hub
```

### Custom Image Naming (Internal)

For custom builds based on official image:

```
# Project-specific
insightpulseai/odoo:18.0-ipai-v1.0.0
insightpulseai/odoo:18.0-prod-2025-01-13

# Environment-specific
odoo:18.0-dev       # Development with extra tools
odoo:18.0-staging   # Staging with seed data
odoo:18.0-prod      # Production optimized

# Feature-specific
odoo:18.0-finance   # Finance-focused modules
odoo:18.0-hr        # HR-focused modules
```

---

## Image Layers

### Layer Structure (9 layers total)

**Layer 1-3: Base OS** (~676 MB)
```
Ubuntu 24.04 LTS base image
System packages and dependencies
Locale configuration (en_US.UTF-8)
```

**Layer 4-6: Odoo Dependencies** (~58 MB)
```
Python 3.11+ runtime
PostgreSQL client libraries
Node.js and npm (for asset compilation)
wkhtmltopdf (PDF generation)
System dependencies (libxml2, libxslt, etc.)
```

**Layer 7: Odoo Core** (~1.28 GB)
```
Odoo 18.0 source code
Python packages (pip requirements)
Odoo addons (base, standard modules)
```

**Layer 8-9: Configuration** (~3 KB)
```
entrypoint.sh script
wait-for-psql.py script
odoo.conf configuration file
```

### Layer Commands Summary

```dockerfile
# Simplified Dockerfile representation
FROM ubuntu:24.04

# Environment setup
ENV LANG=en_US.UTF-8
ENV ODOO_VERSION=18.0
ENV ODOO_RC=/etc/odoo/odoo.conf

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip postgresql-client \
    wkhtmltopdf nodejs npm [...]

# Install Odoo
ARG ODOO_RELEASE=20251222
ARG ODOO_SHA=fc71ac3c039e84f1aa33ab2bf2a3922...
RUN curl -o odoo.deb [...] && apt install ./odoo.deb

# Configuration
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/
COPY ./wait-for-psql.py /usr/local/bin/

# Volumes
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose ports
EXPOSE 8069/tcp 8071/tcp 8072/tcp

# Runtime
USER odoo
ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
```

---

## Default Configuration

### File Location
**Path**: `/etc/odoo/odoo.conf`
**Owner**: `odoo:odoo`
**Permissions**: `644`

### Default Settings

```ini
[options]
# Addons
addons_path = /mnt/extra-addons
data_dir = /var/lib/odoo

# Database (all commented out by default)
; admin_passwd = admin
; db_maxconn = 64
; db_name = False
; db_template = template1
; dbfilter = .*

# Performance
; limit_memory_hard = 2684354560    # 2.5 GB
; limit_memory_soft = 2147483648    # 2 GB
; limit_request = 8192
; limit_time_cpu = 60
; limit_time_real = 120
; workers = 0                       # Single-process mode
; max_cron_threads = 2

# Logging
; log_level = info
; log_handler = [':INFO']
; logfile = None                    # Log to stdout

# Email (SMTP)
; smtp_server = localhost
; smtp_port = 25
; smtp_ssl = False
; smtp_user = False
; smtp_password = False
; email_from = False

# Web Server
; xmlrpc = True
; xmlrpc_port = 8069
; xmlrpc_interface =                # Bind to all interfaces
; xmlrpcs = True
; xmlrpcs_port = 8071               # SSL/TLS port
; longpolling_port = 8072           # WebSocket/long-polling

# Database Management
; list_db = True                    # Show database selector
; debug_mode = False
```

**Key Notes**:
- All settings commented out (use defaults or environment variables)
- `addons_path` and `data_dir` are the only active settings
- Everything else inherits from Odoo defaults or must be configured via:
  - Environment variables
  - Command-line arguments
  - Custom configuration file

---

## Environment Variables

### Core Variables

**Required**:
```bash
HOST=postgres                # PostgreSQL host
PORT=5432                    # PostgreSQL port
USER=odoo                    # Database user
PASSWORD=secret              # Database password
```

**Optional**:
```bash
# Database
DB_NAME=odoo                 # Specific database name
DB_MAXCONN=64               # Max database connections
DB_TEMPLATE=template1       # Database template

# Performance
WORKERS=4                    # Multi-process mode (0 = single)
MAX_CRON_THREADS=2          # Background job workers
LIMIT_MEMORY_HARD=2684354560
LIMIT_MEMORY_SOFT=2147483648
LIMIT_TIME_CPU=60
LIMIT_TIME_REAL=120

# Email
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=password
SMTP_SSL=True

# Web
XMLRPC_PORT=8069
LONGPOLLING_PORT=8072

# Logging
LOG_LEVEL=info              # debug, info, warn, error, critical
LOG_HANDLER=:INFO

# Admin
ADMIN_PASSWD=strongpassword # Master password for database operations
```

### Custom Variables (InsightPulse AI)

**Production** (`deploy/.env`):
```bash
# Core
POSTGRES_HOST=private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
POSTGRES_PORT=25060
POSTGRES_USER=doadmin
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=odoo

# Performance (8GB RAM / 4 CPU)
WORKERS=12                   # 2 × CPU cores × 6
LIMIT_MEMORY_HARD=2684354560
LIMIT_MEMORY_SOFT=2147483648
MAX_CRON_THREADS=2

# Features
PROXY_MODE=True             # Behind nginx reverse proxy
SESSION_STORE=redis         # Redis session storage

# Email (Mailgun API)
MAILGUN_API_KEY=${MAILGUN_API_KEY}
MAILGUN_DOMAIN=mg.insightpulseai.net

# Integrations
N8N_WEBHOOK_URL=https://n8n.insightpulseai.net/webhook
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

---

## Exposed Ports

**Port Mapping**:

| Port | Protocol | Purpose | Usage |
|------|----------|---------|-------|
| **8069** | HTTP | Main web interface | Primary Odoo application |
| **8071** | HTTPS | SSL/TLS interface | Secure web interface (deprecated) |
| **8072** | HTTP | WebSocket/long-polling | Real-time notifications, chat |

**Production Setup**:
```yaml
services:
  odoo:
    ports:
      - "8069:8069"   # HTTP (behind nginx reverse proxy)
      - "8072:8072"   # WebSocket
    # Port 8071 not exposed (SSL handled by nginx)
```

**Port 8071 Note**:
- SSL/TLS on port 8071 is deprecated
- Use nginx/Traefik for SSL termination instead
- InsightPulse AI uses nginx for all SSL (port 443)

---

## Volume Mounts

### Required Volumes

**`/var/lib/odoo`** - Data Directory
```
Purpose: Odoo filestore, sessions, attachments
Priority: CRITICAL (must be backed up)
Growth: Growing (user files, attachments)
Backup: Daily recommended
Owner: odoo:odoo (UID 999, GID 999)
```

**`/mnt/extra-addons`** - Custom Addons
```
Purpose: Custom Odoo modules (ipai_*, OCA, etc.)
Priority: IMPORTANT (version controlled)
Growth: Static (code only)
Backup: Via git (not Docker volume)
Owner: odoo:odoo or root:root (read-only)
```

### Production Volume Configuration

```yaml
volumes:
  odoo-web-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/odoo-ce/data/filestore

services:
  odoo:
    volumes:
      - odoo-web-data:/var/lib/odoo           # Critical data
      - ../addons:/mnt/extra-addons:ro        # Custom modules (read-only)
      - ./odoo.conf:/etc/odoo/odoo.conf:ro    # Configuration (read-only)
```

**Volume Permissions**:
```bash
# Filestore must be writable by odoo user (UID 999)
chown -R 999:999 /opt/odoo-ce/data/filestore

# Addons can be read-only
chown -R root:root /opt/odoo-ce/repo/addons
chmod -R 755 /opt/odoo-ce/repo/addons
```

---

## Entrypoint Script

### Location
**Path**: `/entrypoint.sh`
**Owner**: `root:root`
**Permissions**: `755`

### Behavior

**Script Flow**:
1. **Wait for PostgreSQL**: Calls `wait-for-psql.py` to ensure DB is ready
2. **Check Command**: Determine if running Odoo or custom command
3. **Process Environment Variables**: Convert to Odoo config format
4. **Execute Command**: Launch Odoo with merged configuration

**Common Usage**:
```bash
# Default: Start Odoo
docker run odoo:18.0

# Custom command: Run shell
docker run -it odoo:18.0 bash

# Odoo with arguments
docker run odoo:18.0 odoo -d mydb -i base --stop-after-init

# Run specific Odoo command
docker run odoo:18.0 odoo shell -d mydb
```

### wait-for-psql.py

**Purpose**: Block until PostgreSQL is ready to accept connections

**Location**: `/usr/local/bin/wait-for-psql.py`

**Usage**:
```bash
# Automatic (called by entrypoint.sh)
wait-for-psql.py --db_host=postgres --db_port=5432 --timeout=30

# Manual
python3 /usr/local/bin/wait-for-psql.py --db_host=$HOST --db_port=$PORT
```

---

## User & Permissions

**Default User**: `odoo`
**UID/GID**: `999:999`

**File Ownership**:
```
/etc/odoo/odoo.conf       → root:root (644)
/entrypoint.sh            → root:root (755)
/usr/local/bin/wait-for-psql.py → root:root (755)
/mnt/extra-addons         → odoo:odoo or root:root
/var/lib/odoo             → odoo:odoo (must be writable)
```

**Process User**:
```bash
# Odoo runs as non-root user 'odoo'
docker exec odoo-prod whoami
# Output: odoo

docker exec odoo-prod id
# Output: uid=999(odoo) gid=999(odoo) groups=999(odoo)
```

**Security Best Practice**:
- Never run Odoo as root
- Keep volumes owned by odoo:odoo (999:999)
- Use read-only mounts for configuration and addons

---

## Configuration Precedence

**Priority Order** (highest to lowest):

1. **Command-line arguments**: `odoo -d mydb --workers=4`
2. **Environment variables**: `WORKERS=4`
3. **Custom config file**: `/etc/odoo/odoo.conf` (volume mount)
4. **Default config file**: `/etc/odoo/odoo.conf` (in image)
5. **Odoo built-in defaults**

**Example Override**:
```bash
# Default config has workers=0 (single-process)
# Override with environment variable
docker run -e WORKERS=4 odoo:18.0

# Or with custom config file
docker run -v ./my-odoo.conf:/etc/odoo/odoo.conf odoo:18.0

# Or with command-line argument
docker run odoo:18.0 odoo --workers=4
```

---

## Production Deployment Patterns

### Pattern 1: External Database + Custom Addons

```yaml
services:
  odoo:
    image: odoo:18.0
    environment:
      HOST: postgres.example.com
      PORT: 5432
      USER: odoo
      PASSWORD: ${DB_PASSWORD}
      WORKERS: 4
    volumes:
      - odoo-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons:ro
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
    ports:
      - "8069:8069"
      - "8072:8072"
    restart: unless-stopped
```

### Pattern 2: Behind Reverse Proxy (InsightPulse AI)

```yaml
services:
  odoo:
    image: odoo:18.0
    environment:
      HOST: private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
      PORT: 25060
      USER: doadmin
      PASSWORD: ${DB_PASSWORD}
      WORKERS: 12
      PROXY_MODE: "True"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ../addons:/mnt/extra-addons:ro
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
    networks:
      - deploy_default
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    ports:
      - "80:80"
      - "443:443"
    networks:
      - deploy_default
    restart: unless-stopped
```

### Pattern 3: Multi-Instance (Development)

```yaml
services:
  odoo-core:
    image: odoo:18.0
    environment:
      DB_NAME: odoo_core
    ports:
      - "8069:8069"

  odoo-marketing:
    image: odoo:18.0
    environment:
      DB_NAME: odoo_marketing
    ports:
      - "8070:8069"

  odoo-accounting:
    image: odoo:18.0
    environment:
      DB_NAME: odoo_accounting
    ports:
      - "8071:8069"
```

---

## Image Customization

### Option 1: Runtime Configuration (Recommended)

Use volumes and environment variables (no custom image):

```bash
docker run \
  -e HOST=postgres \
  -e USER=odoo \
  -e PASSWORD=secret \
  -e WORKERS=4 \
  -v odoo-data:/var/lib/odoo \
  -v ./addons:/mnt/extra-addons:ro \
  -v ./odoo.conf:/etc/odoo/odoo.conf:ro \
  odoo:18.0
```

### Option 2: Derived Image

Create custom image for specific needs:

```dockerfile
FROM odoo:18.0

# Install additional system packages
USER root
RUN apt-get update && apt-get install -y \
    vim curl htop \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install requests boto3

# Copy custom configuration
COPY ./odoo.conf /etc/odoo/odoo.conf

# Copy custom addons (baked into image)
COPY ./addons /mnt/extra-addons

# Back to odoo user
USER odoo

# Custom entrypoint (optional)
COPY ./custom-entrypoint.sh /
ENTRYPOINT ["/custom-entrypoint.sh"]
CMD ["odoo"]
```

**Build and Tag**:
```bash
docker build -t insightpulseai/odoo:18.0-ipai-v1.0.0 .
docker push insightpulseai/odoo:18.0-ipai-v1.0.0
```

### Option 3: Multi-Stage Build

Optimize image size with multi-stage:

```dockerfile
# Stage 1: Build dependencies
FROM odoo:18.0 AS builder
USER root
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/OCA/web.git /tmp/oca-web

# Stage 2: Runtime
FROM odoo:18.0
COPY --from=builder /tmp/oca-web /mnt/extra-addons/oca-web
USER odoo
```

---

## Troubleshooting

### Common Issues

**Issue 1: Permission Denied on /var/lib/odoo**
```bash
# Symptom: Odoo cannot write to filestore
# Fix: Ensure volume owned by odoo user (UID 999)
chown -R 999:999 /path/to/odoo/data
```

**Issue 2: Addons Not Loading**
```bash
# Symptom: Custom modules not appearing in Apps
# Fix 1: Check addons_path in config
docker exec odoo-prod odoo -c /etc/odoo/odoo.conf --addons-path

# Fix 2: Update module list
docker exec odoo-prod odoo -d odoo -u base --stop-after-init
```

**Issue 3: Database Connection Failed**
```bash
# Symptom: wait-for-psql times out
# Fix: Verify PostgreSQL reachable
docker exec odoo-prod psql -h $HOST -p $PORT -U $USER -d postgres -c "SELECT 1"
```

**Issue 4: Port Already in Use**
```bash
# Symptom: Cannot start container (port 8069 in use)
# Fix: Check for conflicting services
lsof -i :8069
docker ps | grep 8069
```

---

## Performance Tuning

### Worker Configuration

**Formula**: `workers = 2 × CPU_cores + 1` (for I/O-bound)
**Or**: `workers = 2 × CPU_cores × 6` (InsightPulse AI pattern)

```ini
[options]
workers = 12                    # For 4 CPU cores (2 × 4 × 6)
limit_memory_hard = 2684354560  # 2.5 GB per worker max
limit_memory_soft = 2147483648  # 2 GB per worker soft limit
max_cron_threads = 2            # Background jobs
```

### Memory Limits

**Per-Worker Memory**:
```
limit_memory_soft = 2147483648  # 2 GB (warning threshold)
limit_memory_hard = 2684354560  # 2.5 GB (force restart)
```

**Total RAM Calculation**:
```
Total = (workers × limit_memory_hard) + overhead
Total = (12 × 2.5 GB) + 1 GB = 31 GB (requires 32 GB RAM minimum)
```

**Docker Memory Limit**:
```yaml
services:
  odoo:
    mem_limit: 32g
    mem_reservation: 16g
```

### Request Timeouts

```ini
[options]
limit_time_cpu = 60      # CPU time per request (seconds)
limit_time_real = 120    # Wall-clock time per request (seconds)
limit_request = 8192     # Max request size (lines)
```

---

## Security Hardening

### 1. Non-Root User
```yaml
services:
  odoo:
    user: "999:999"  # Explicit UID/GID
```

### 2. Read-Only Filesystem
```yaml
services:
  odoo:
    read_only: true
    tmpfs:
      - /tmp
      - /run
    volumes:
      - odoo-data:/var/lib/odoo:rw  # Only writable volume
      - ./addons:/mnt/extra-addons:ro
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
```

### 3. Resource Limits
```yaml
services:
  odoo:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 32G
        reservations:
          cpus: '2'
          memory: 16G
```

### 4. Network Isolation
```yaml
services:
  odoo:
    networks:
      - backend  # No direct internet access
    # Only nginx in frontend network
```

### 5. Admin Password Protection
```ini
[options]
admin_passwd = ${ADMIN_PASSWD}  # Strong master password
list_db = False                 # Hide database selector
```

---

## References

**Official Documentation**:
- Docker Hub: https://hub.docker.com/_/odoo
- Odoo Documentation: https://www.odoo.com/documentation/18.0/
- GitHub Repository: https://github.com/odoo/docker

**InsightPulse AI Implementation**:
- Production Config: `deploy/odoo.conf`
- Docker Compose: `deploy/docker-compose.yml`
- Infrastructure Reference: `deploy/INFRASTRUCTURE.yaml`

---

*Last updated: 2026-01-13*
*Odoo Version: 18.0*
*Image Release: 20251222*
