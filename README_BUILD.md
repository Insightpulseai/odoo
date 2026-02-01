# Odoo CE v1.2.0 - Full Build Bundle

## Overview

This bundle contains the complete Odoo CE 18.0 build with:
- Docker orchestration (Dockerfile, docker-compose.yml)
- Bootstrap scripts for automated setup
- All custom modules including ipai_ce_branding
- Production-ready configuration

## Quick Start

### 1. Extract Bundle

```bash
# Extract the bundle
unzip odoo-v1.2.0-build.zip
cd odoo-ce
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required environment variables:
- `POSTGRES_PASSWORD`: PostgreSQL password
- `ODOO_ADMIN_PASSWD`: Odoo master password
- `ODOO_DB_NAME`: Database name (default: production)

### 3. Build and Run

```bash
# Build Docker images
docker compose build

# Start services
docker compose up -d

# Check logs
docker compose logs -f odoo
```

### 4. Install Modules

```bash
# Install custom modules (one-time setup)
docker compose exec odoo odoo \
  -d production \
  -i ipai_ce_branding,ipai_ce_cleaner \
  --stop-after-init

# Restart Odoo service
docker compose restart odoo
```

**Important**: When using `--stop-after-init`, make sure to:
1. Run the install command with `docker compose exec` (not in the compose file)
2. Restart the service after installation completes
3. Avoid combining `--stop-after-init` with `restart: unless-stopped` for always-on services

### 5. Access Odoo

- **Web Interface**: http://localhost:8069
- **Default Admin**: admin / [your ODOO_ADMIN_PASSWD]

## Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| odoo | 8069 | Odoo application |
| db | 5432 | PostgreSQL database |
| redis | 6379 | Session store |

## Module Management

### Install New Module

```bash
# Install a module
docker compose exec odoo odoo \
  -d production \
  -i module_name \
  --stop-after-init

# Restart
docker compose restart odoo
```

### Update Module

```bash
# Update a module
docker compose exec odoo odoo \
  -d production \
  -u module_name \
  --stop-after-init

# Restart
docker compose restart odoo
```

### List Installed Modules

```bash
# Connect to database
docker compose exec db psql -U odoo -d production

# Query modules
SELECT name, state FROM ir_module_module WHERE state='installed';
```

## Branding Customization

### Replace Login Background

**Option A: Replace SVG file (no code changes)**

```bash
# Replace the placeholder image
cp your-image.svg addons/ipai_ce_branding/static/src/img/login_bg.svg

# Restart Odoo
docker compose restart odoo
```

**Option B: Use different format (.webp, .jpg, .png)**

1. Add your image:
```bash
cp your-image.webp addons/ipai_ce_branding/static/src/img/login_bg.webp
```

2. Edit `addons/ipai_ce_branding/static/src/scss/login.scss` (line 15):
```scss
$ipai-login-bg-url: "/ipai_ce_branding/static/src/img/login_bg.webp" !default;
```

3. Update module:
```bash
docker compose exec odoo odoo -d production -u ipai_ce_branding --stop-after-init
docker compose restart odoo
```

## Production Deployment

### Environment Configuration

For production, update `.env`:

```bash
# Production settings
ODOO_WORKERS=12
ODOO_MAX_CRON_THREADS=2
ODOO_LIMIT_MEMORY_HARD=2684354560
ODOO_LIMIT_MEMORY_SOFT=2147483648
ODOO_PROXY_MODE=True
```

### Database Backup

```bash
# Backup database
docker compose exec db pg_dump -U odoo production > backup_$(date +%Y%m%d).sql

# Restore database
docker compose exec -T db psql -U odoo production < backup_20240101.sql
```

### Log Management

```bash
# View logs
docker compose logs -f odoo

# View last 100 lines
docker compose logs --tail=100 odoo

# Export logs
docker compose logs odoo > odoo_logs_$(date +%Y%m%d).txt
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
docker compose ps

# Check logs for errors
docker compose logs odoo
docker compose logs db

# Restart services
docker compose restart
```

### Module Installation Fails

```bash
# Check module syntax
python -m compileall addons/module_name

# Check Odoo logs
docker compose logs odoo | grep ERROR

# Clear cache and retry
docker compose exec odoo rm -rf ~/.local/share/Odoo/sessions/*
docker compose restart odoo
```

### Database Connection Issues

```bash
# Check database is running
docker compose exec db psql -U odoo -d production -c "SELECT version();"

# Check connection from Odoo container
docker compose exec odoo psql -h db -U odoo -d production -c "SELECT 1;"
```

## File Structure

```
odoo-ce/
├── addons/                    # Custom modules
│   ├── ipai_ce_branding/     # Login branding module
│   └── ipai_ce_cleaner/      # Cleaner module
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Odoo container image
├── scripts/                   # Bootstrap and utility scripts
├── patches/                   # Git patches
└── .env.example              # Environment template
```

## Version Information

- **Odoo**: 18.0 CE
- **Python**: 3.11
- **PostgreSQL**: 15
- **Redis**: 7

## License

AGPL-3.0

## Support

For issues or questions, contact: support@insightpulseai.com
