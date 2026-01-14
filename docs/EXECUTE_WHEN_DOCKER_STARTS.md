# Canonical Sandbox Quick Start

**Start here** every time you begin Odoo CE development.

---

## Single Command Sequence

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose up -d
docker compose logs -f odoo
```

**Access Odoo**: http://localhost:8069

---

## What This Does

1. **cd ~/Documents/GitHub/odoo-ce/sandbox/dev**
   Enters the canonical sandbox directory (required for all operations)

2. **docker compose up -d**
   Starts PostgreSQL and Odoo containers in detached mode

3. **docker compose logs -f odoo**
   Follows Odoo logs in real-time (Ctrl+C to stop tailing)

---

## Verification Commands

```bash
# Check stack status
docker compose ps

# Check Odoo accessibility
curl -sS http://localhost:8069/web/login | head -5

# View full logs
docker compose logs

# Restart Odoo service only
docker compose restart odoo
```

---

## Common Operations

### Install/Upgrade Module

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose exec odoo odoo -d odoo -u ipai_finance_ppm --stop-after-init
```

**Note**: No need to stop the main server for module operations.

### Install New Module

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose exec odoo odoo -d odoo -i ipai_new_module --stop-after-init
```

### Update Apps List

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose exec odoo odoo -d odoo --update-apps-list --stop-after-init
```

### Database Shell (psql)

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose exec postgres psql -U odoo -d odoo
```

### Odoo Shell (Python REPL)

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose exec odoo odoo shell -d odoo
```

### Rebuild Assets (if JS/CSS not updating)

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose restart odoo
# Then hard refresh browser: Cmd+Shift+R
```

---

## Stopping the Stack

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose down
```

**Note**: Data persists in Docker volumes. Use `docker compose down -v` to remove volumes (destructive).

---

## Automated Health Check

Run the doctor script to verify environment health:

```bash
cd ~/Documents/GitHub/odoo-ce
./scripts/doctor_sandbox.sh
```

This checks:
- Current working directory is canonical sandbox
- Docker Compose files exist
- Docker daemon is running
- Required ports (8069, 5432) status
- Container status and next steps

---

## Troubleshooting

### "Cannot connect to Docker daemon"

**Fix**: Start Docker
```bash
colima start
# or open Docker Desktop app
```

### "Port 8069 already in use"

**Fix**: Check what's using the port
```bash
lsof -i :8069
# Then either:
# 1. Stop the conflicting process
# 2. Or the stack is already running - check with: docker compose ps
```

### "Module not found"

**Fix**: Ensure module is in addons path
```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose exec odoo ls /mnt/extra-addons/ipai/
# Update apps list if module exists but not visible
docker compose exec odoo odoo -d odoo --update-apps-list --stop-after-init
```

### "Changes not visible in browser"

**Fix**: Clear caches
```bash
# 1. Restart Odoo
docker compose restart odoo

# 2. Hard refresh browser: Cmd+Shift+R (Chrome/Firefox)

# 3. If still not working, clear Odoo asset cache
docker compose exec odoo odoo -d odoo --update web --stop-after-init
```

---

## VS Code Integration

When you open the repo in VS Code:

1. **Terminals auto-start in canonical sandbox** (configured in `.vscode/settings.json`)
2. All commands run from `sandbox/dev` by default
3. Use Cmd+` to open integrated terminal

---

## direnv Integration (Optional)

If you have `direnv` installed, the repo will auto-cd to `sandbox/dev` when you enter the repo root.

**Enable direnv**:
```bash
# Install (macOS)
brew install direnv

# Add to shell config (~/.zshrc)
eval "$(direnv hook zsh)"

# Allow this repo
cd ~/Documents/GitHub/odoo-ce
direnv allow
```

**Without direnv**: The `.envrc` file is safely ignored if direnv is not installed.

---

## Claude Code Integration

**Launch Claude Code in canonical sandbox**:

```bash
cd ~/Documents/GitHub/odoo-ce
./bin/claude-odoo
```

This script:
- Changes to `sandbox/dev`
- Launches Claude Code if CLI is available
- Falls back to shell with instructions if not

---

## Additional Resources

- **Health Check**: `./scripts/doctor_sandbox.sh`
- **Module Operations**: `./scripts/deploy-odoo-modules.sh`
- **Full Documentation**: See `claude.md` and `sandbox/dev/README_CANONICAL.md`

---

**Last Updated**: 2025-01-14
**Canonical Path**: `~/Documents/GitHub/odoo-ce/sandbox/dev`
