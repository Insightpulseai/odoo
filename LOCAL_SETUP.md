# Local Odoo Development Setup

## Quick Start

### 1. Start Docker Desktop

Make sure Docker Desktop is running:
- Open Docker Desktop from Applications
- Wait for the Docker icon in the menu bar to show "Docker Desktop is running"

### 2. Start Odoo Locally

```bash
cd /Users/tbwa/odoo-ce
./scripts/start_local_odoo.sh
```

Or manually:
```bash
docker compose -f docker-compose.dev.yml up -d postgres odoo-core
```

### 3. Access Local Odoo

- **URL**: http://localhost:8069
- **Username**: admin
- **Password**: admin (or check your local .env file)

## Manual Docker Commands

### Start Services
```bash
cd /Users/tbwa/odoo-ce
docker compose -f docker-compose.dev.yml up -d postgres odoo-core
```

### Check Status
```bash
docker compose -f docker-compose.dev.yml ps
```

### View Logs
```bash
docker compose -f docker-compose.dev.yml logs -f odoo-core
```

### Stop Services
```bash
docker compose -f docker-compose.dev.yml down
```

### Restart Services
```bash
docker compose -f docker-compose.dev.yml restart odoo-core
```

## Theme Development Workflow

### 1. Make Changes to Theme
Edit files in:
- `addons/ipai/ipai_web_theme_tbwa/static/src/scss/`
- `addons/ipai/ipai_web_theme_tbwa/views/`

### 2. Restart Odoo to Apply Changes
```bash
docker compose -f docker-compose.dev.yml restart odoo-core
```

### 3. Clear Browser Cache
- **Mac**: `Cmd + Shift + R`
- **Windows/Linux**: `Ctrl + Shift + R`

### 4. Refresh Login Page
Open: http://localhost:8069/web/login

## Verify Theme Changes Locally

### Header Cleanup
- ✅ Only TBWA logo visible (left)
- ✅ Only user menu visible (right)
- ✅ No navigation menu items
- ✅ No breadcrumbs
- ✅ No search bar

### Login Button
- ✅ Black background (#000000)
- ✅ White text
- ✅ Hover effect (darkens to #1a1a1a)
- ✅ Clickable

### Footer
- ✅ TBWA branding visible
- ✅ Social media links

## Troubleshooting

### Docker Not Running
```bash
# Start Docker Desktop
open -a Docker

# Wait 30 seconds, then check
docker ps
```

### Port 8069 Already in Use
```bash
# Find what's using the port
lsof -i :8069

# Stop the process or use different port in docker-compose.dev.yml
```

### Odoo Won't Start
```bash
# Check logs
docker compose -f docker-compose.dev.yml logs odoo-core

# Remove old containers and start fresh
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d postgres odoo-core
```

### Database Issues
```bash
# Connect to PostgreSQL
docker compose -f docker-compose.dev.yml exec postgres psql -U odoo

# List databases
\l

# Connect to odoo database
\c odoo_core
```

### Theme Not Loading
```bash
# Restart Odoo
docker compose -f docker-compose.dev.yml restart odoo-core

# Clear Odoo assets cache
docker compose -f docker-compose.dev.yml exec odoo-core rm -rf /var/lib/odoo/.local/share/Odoo/filestore/*/assets/*

# Restart again
docker compose -f docker-compose.dev.yml restart odoo-core
```

## Deploy to Production

Once you've tested locally and everything works:

```bash
# Commit changes
git add .
git commit -m "feat(theme): your changes"
git push origin main

# Deploy to production
./scripts/deploy_theme_to_production.sh

# Force asset regeneration
./scripts/force_asset_regeneration.sh
```

## Architecture

```
Local Development:
  Your Mac (/Users/tbwa/odoo-ce)
    ↓ docker-compose.dev.yml
  Docker Containers:
    - postgres (port 5432)
    - odoo-core (port 8069)

  Volume Mounts:
    /Users/tbwa/odoo-ce/addons → /mnt/extra-addons

Production:
  DigitalOcean Server (178.128.112.214)
    ↓ docker-compose.prod.yml
  Docker Containers:
    - odoo-prod (port 8069)

  Volume Mounts:
    /opt/odoo-ce/repo/addons → /mnt/extra-addons
```

## Next Steps

1. **Start Docker Desktop** (if not running)
2. **Run**: `./scripts/start_local_odoo.sh`
3. **Open**: http://localhost:8069/web/login
4. **Verify**: Theme changes are visible
5. **Develop**: Make changes, restart, test
6. **Deploy**: Push to GitHub and deploy to production
