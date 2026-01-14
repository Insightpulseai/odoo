# Canonical Local Development Workflow

**Purpose**: Safe, reproducible local development with hot reload. Never touch production.

---

## Quick Start (Clean Reset)

```bash
cd ~/odoo-ce/sandbox/dev

# Hard reset (LOCAL ONLY - destroys local data)
docker compose down -v --remove-orphans

# Rebuild and start
docker compose up -d --build

# Verify
docker compose ps
docker compose logs -f --tail=200 odoo
curl -I http://localhost:8069/web/login
```

**Access**: http://localhost:8069
**Credentials**: admin / admin (after first database init)

---

## Module Installation/Updates (Hot Reload)

Install or update modules **without stopping** the container:

```bash
cd ~/odoo-ce/sandbox/dev

# Install new module
docker compose exec -T odoo odoo -d odoo -i ipai_finance_close_seed --stop-after-init

# Update module after code changes
docker compose exec -T odoo odoo -d odoo -u ipai_finance_close_seed --stop-after-init

# Update multiple modules
docker compose exec -T odoo odoo -d odoo -u base,web,ipai_finance_ppm --stop-after-init
```

**When to restart**:
- ✅ **No restart needed**: Python model changes, XML view changes, data files
- ⚠️ **Restart required**: JavaScript/SCSS asset changes

```bash
# Only if assets changed
docker compose restart odoo
```

---

## Development Settings (Hot Reload)

Canonical `odoo.conf` settings for development:

```ini
[options]
# Hot reload configuration
workers = 0
dev_mode = reload
limit_time_real = 600

# Database
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo

# Paths
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons

# Logging
log_level = info
log_handler = :INFO
```

**Verify settings**:
```bash
docker compose exec odoo odoo --version
docker compose exec odoo ps aux | grep odoo
```

---

## Asset Recovery (If Assets Break)

If JavaScript/CSS assets fail to load (rare):

```bash
cd ~/odoo-ce/sandbox/dev

# Nuclear option: fresh start
docker compose down -v
docker compose up -d

# Wait for startup
sleep 20
curl -I http://localhost:8069/web/login
```

This guarantees clean filestore and database for local development.

---

## Canonical Environment Setup

Add this to your shell for automatic sandbox navigation:

```bash
mkdir -p ~/.config/ipai
cat > ~/.config/ipai/canonical_env.sh <<'EOF'
# IPAI Canonical Environment
export IPAI_REPO="$HOME/odoo-ce"
export IPAI_SANDBOX="$IPAI_REPO/sandbox/dev"

# Auto-navigate to sandbox
[ -d "$IPAI_SANDBOX" ] && cd "$IPAI_SANDBOX" 2>/dev/null || true

# Load sandbox environment
if [ -f "$IPAI_SANDBOX/.env" ]; then
  set -a; . "$IPAI_SANDBOX/.env"; set +a
fi

# Print status
echo "📦 IPAI Sandbox: $IPAI_SANDBOX"
echo "🔧 Quick check:  docker compose ps"
echo "🎯 MCP Servers:  Desktop Commander | Docker | Docker Hub | GitHub | Kubernetes"
EOF

# Add to shell configs
grep -q "canonical_env.sh" ~/.zshrc 2>/dev/null || echo 'source ~/.config/ipai/canonical_env.sh' >> ~/.zshrc
grep -q "canonical_env.sh" ~/.bashrc 2>/dev/null || echo 'source ~/.config/ipai/canonical_env.sh' >> ~/.bashrc

# Reload current shell
source ~/.config/ipai/canonical_env.sh
```

Now every new terminal session:
- ✅ Auto-navigates to `~/odoo-ce/sandbox/dev`
- ✅ Loads sandbox environment variables
- ✅ Shows available MCP servers

---

## Common Workflows

### Add New Module

```bash
# 1. Create module structure
mkdir -p ~/odoo-ce/addons/ipai/my_new_module
cd ~/odoo-ce/addons/ipai/my_new_module

# 2. Create __manifest__.py and __init__.py
# (use module generator or copy from existing module)

# 3. Install in sandbox
cd ~/odoo-ce/sandbox/dev
docker compose exec -T odoo odoo -d odoo -i my_new_module --stop-after-init

# 4. Verify
docker compose logs odoo --tail=50 | grep my_new_module
```

### Update Module After Changes

```bash
cd ~/odoo-ce/sandbox/dev

# Python/XML changes (hot reload)
docker compose exec -T odoo odoo -d odoo -u my_module --stop-after-init

# JavaScript/SCSS changes (requires restart)
docker compose restart odoo
```

### Debug Mode

```bash
# Enable developer mode in Odoo UI
# Settings → Activate Developer Mode

# Or via command line
docker compose exec odoo odoo shell -d odoo <<'PYTHON'
env = odoo.api.Environment(cr, 1, {})
env['ir.config_parameter'].set_param('web.base.url.freeze', True)
env['ir.config_parameter'].set_param('web.base.url', 'http://localhost:8069')
cr.commit()
PYTHON
```

### View Logs

```bash
cd ~/odoo-ce/sandbox/dev

# Follow logs
docker compose logs -f odoo

# Last 100 lines
docker compose logs odoo --tail=100

# Search for errors
docker compose logs odoo 2>&1 | grep -i error
```

---

## Safety Rules

**✅ Safe (LOCAL ONLY)**:
- `docker compose down -v` (destroys local data)
- `docker compose restart`
- Module install/update via `--stop-after-init`
- Any Python/XML/data changes

**❌ NEVER on Production**:
- `docker compose down -v` on production
- Direct database modifications without backups
- Installing untested modules
- Changing worker configuration

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8069
lsof -i :8069

# Stop conflicting service
kill <PID>

# Or use different port in docker-compose.yml
```

### Database Connection Refused

```bash
# Check database container
docker compose ps db

# Restart database
docker compose restart db

# Check logs
docker compose logs db --tail=50
```

### Module Not Found

```bash
# Verify addons path
docker compose exec odoo odoo --addons-path

# Check module exists
ls -la ~/odoo-ce/addons/ipai/

# Restart to reload addons path
docker compose restart odoo
```

### Assets Not Loading

```bash
# Clear browser cache first (Cmd+Shift+R)

# If still broken, restart Odoo
docker compose restart odoo

# Nuclear option
docker compose down -v && docker compose up -d
```

---

## Performance Tips

**Development**:
- Use `workers = 0` for hot reload
- Enable `dev_mode = reload`
- Limit to essential modules for faster startup

**Testing**:
- Use `workers = 2` to test multi-worker behavior
- Disable `dev_mode` to test production-like performance
- Test with full module set

---

## Next Steps

- See `SANDBOX.md` for production deployment
- See `../DEVELOPMENT.md` for module development guide
- See `../../docs/ODOO_INTEGRATION.md` for n8n/Mattermost integration

---

**Last Updated**: 2026-01-14
**Odoo Version**: 18.0
**Docker Compose Version**: v2.x
