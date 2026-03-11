# ipai-platform

Production-ready Odoo 18 platform with Nginx reverse proxy, Redis session storage, and optional local Supabase stack.

## Quick Start

### Prerequisites

- Docker & Docker Compose v2
- Colima (macOS) or Docker Desktop
- TLS certificates (Let's Encrypt or self-signed)

### Development

```bash
# Start Colima (macOS)
colima start --cpu 6 --memory 12 --disk 80
docker context use colima

# Create secrets
mkdir -p secrets
echo "your-db-password" > secrets/db_password.txt
echo "your-supabase-db-password" > secrets/supabase_db_password.txt
echo "your-jwt-secret" > secrets/supabase_jwt_secret.txt

# Start core stack (HTTP only)
docker compose up -d

# Access Odoo
open http://localhost:8069
```

### Production

```bash
# Setup TLS certificates
./scripts/setup-tls.sh letsencrypt  # or selfsigned for dev

# Start with production overlay
docker compose -f compose.yaml -f compose.prod.yaml up -d

# Verify health
./scripts/health.sh
```

### With Local Supabase

```bash
# Start with Supabase profile
docker compose --profile supabase up -d

# PostgREST available at localhost:3000
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ipai-platform (Docker)                           │
├─────────────────────────────────────────────────────────────────────┤
│  [edge network]                                                     │
│    Nginx (443/80) ─┬─► Odoo (8069/8072)                            │
│         │          └─► PostgREST (3000) ─► Supabase Local DB       │
│         │                                                           │
│  [backend network]                                                  │
│    Odoo ◄──► PostgreSQL 16 ◄──► Redis 7                            │
│                                                                     │
│  [supabase network] (optional profile)                              │
│    PostgREST ◄──► Supabase PostgreSQL                              │
└─────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
ipai-platform/
├── compose.yaml              # Base Docker Compose (development)
├── compose.prod.yaml         # Production overlay
├── .env.example              # Environment template
├── nginx/
│   ├── nginx.conf            # Main Nginx config
│   ├── conf.d/
│   │   ├── default.conf      # Development (HTTP)
│   │   └── sites/
│   │       └── odoo-prod.conf  # Production (HTTPS)
│   └── certs/                # TLS certificates
├── odoo/
│   └── odoo.conf             # Production Odoo config
├── scripts/
│   ├── health.sh             # Platform health check
│   └── setup-tls.sh          # TLS certificate setup
└── secrets/                  # Docker secrets (gitignored)
    ├── db_password.txt
    ├── supabase_db_password.txt
    └── supabase_jwt_secret.txt
```

## Configuration

### Nginx Features

**Development** (`default.conf`):
- HTTP only (port 80)
- Basic proxy to Odoo
- Health check endpoint

**Production** (`odoo-prod.conf`):
- TLS 1.2/1.3 with modern ciphers
- HTTP/2 support
- Rate limiting (10r/s per IP)
- Connection limiting (50 concurrent)
- Security headers (HSTS, X-Frame-Options, etc.)
- Static file caching (24h)
- WebSocket support for Odoo realtime

### Odoo Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `proxy_mode` | True | Trust X-Forwarded headers from Nginx |
| `workers` | 4 | 2 × CPU cores (adjust per server) |
| `max_cron_threads` | 2 | Background job threads |
| `limit_memory_hard` | 2.5GB | Per-worker memory limit |
| `limit_time_real` | 1200s | Request timeout (20 min) |
| `gevent_port` | 8072 | Longpolling/WebSocket port |

### PostgreSQL Tuning (Production)

| Setting | Value | Purpose |
|---------|-------|---------|
| `shared_buffers` | 1GB | Memory for caching |
| `effective_cache_size` | 3GB | OS cache estimate |
| `max_worker_processes` | 4 | Parallel query workers |

## Security

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=odoo_limit:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=odoo_conn:10m;
```

- 10 requests/second per IP
- Burst of 20 requests allowed
- 50 concurrent connections max

### Security Headers

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Secrets Management

Secrets are stored in files (not environment variables) for Docker secrets support:

```bash
# Create secrets directory
mkdir -p secrets

# Generate strong passwords
openssl rand -base64 32 > secrets/db_password.txt
openssl rand -base64 32 > secrets/supabase_db_password.txt
openssl rand -base64 64 > secrets/supabase_jwt_secret.txt

# Secure permissions
chmod 600 secrets/*.txt
```

## TLS Setup

### Let's Encrypt (Production)

```bash
# Ensure DNS points to your server
# Port 80 must be accessible for ACME challenge

./scripts/setup-tls.sh letsencrypt

# Auto-renewal cron (add to server crontab)
0 0 1 * * certbot renew --quiet && docker compose restart nginx
```

### Self-Signed (Development)

```bash
./scripts/setup-tls.sh selfsigned

# Browser will show security warning (expected for self-signed)
```

## Health Checks

```bash
# Run health check
./scripts/health.sh

# Expected output:
# === Platform Health Check ===
# Nginx: ✓ OK
# Odoo (proxy): ✓ OK
# Odoo (container): ✓ OK
# PostgreSQL: ✓ OK
# Redis: ✓ OK
# === Summary ===
# All services healthy
```

## Integration with Supabase Cloud

The local Supabase stack (`--profile supabase`) is for development only.
Production uses Supabase Cloud (`spdtwktxdalcfigzeqrz`).

For MCP Jobs integration, see `supabase/migrations/` for schema and `supabase/functions/run-executor/` for Edge Function.

## Commands Reference

```bash
# Start/Stop
docker compose up -d                              # Start (dev)
docker compose -f compose.yaml -f compose.prod.yaml up -d  # Start (prod)
docker compose down                               # Stop
docker compose down -v                            # Stop + remove volumes

# Logs
docker compose logs -f                            # All services
docker compose logs -f nginx                      # Nginx only
docker compose logs -f odoo                       # Odoo only

# Exec
docker compose exec odoo bash                     # Shell into Odoo
docker compose exec odoo_db psql -U odoo -d odoo  # PostgreSQL shell

# Module Management
docker compose exec odoo odoo -d odoo -i module_name --stop-after-init
docker compose exec odoo odoo -d odoo -u module_name --stop-after-init

# Backup
docker compose exec odoo_db pg_dump -U odoo odoo > backup.sql

# Health
./scripts/health.sh
```

## Troubleshooting

### Odoo won't start

```bash
# Check logs
docker compose logs odoo

# Common issues:
# - PostgreSQL not ready: Wait or restart
# - Permission issues: Check volume ownership
# - Module errors: Check addon paths
```

### 502 Bad Gateway

```bash
# Check if Odoo is running
docker compose ps odoo
docker compose logs odoo --tail 50

# Check Nginx config
docker compose exec nginx nginx -t
```

### Database Connection Issues

```bash
# Test PostgreSQL
docker compose exec odoo_db pg_isready -U odoo

# Check credentials
docker compose exec odoo_db psql -U odoo -d odoo -c "SELECT 1"
```

## Related Documentation

- [Supabase Maximization Plan](../.claude/plans/cozy-petting-fountain.md)
- [MCP Jobs System](../mcp/servers/mcp-jobs/)
- [Odoo 19 Canonical Setup](../odoo19/CANONICAL_SETUP.md)
