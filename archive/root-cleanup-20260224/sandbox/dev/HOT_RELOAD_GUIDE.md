# Hot-Reload Development Guide

**Canonical rules for efficient Odoo development with mounted addons.**

---

## 🔥 Hot-Reload Matrix

| Change Type | Action Required | Command |
|-------------|----------------|---------|
| **Python code** (models, wizards, controllers) | Restart Odoo container | `docker compose restart odoo` |
| **XML/QWeb views** | Upgrade module | `docker compose exec -T odoo odoo -d odoo -u MODULE --stop-after-init && docker compose restart odoo` |
| **Security CSV** | Upgrade module | `docker compose exec -T odoo odoo -d odoo -u MODULE --stop-after-init && docker compose restart odoo` |
| **Data files** | Upgrade module | `docker compose exec -T odoo odoo -d odoo -u MODULE --stop-after-init && docker compose restart odoo` |
| **Static assets** (JS/SCSS) | Upgrade module + restart | `docker compose exec -T odoo odoo -d odoo -u MODULE --stop-after-init && docker compose restart odoo` |
| **New module** | Install module | `docker compose exec -T odoo odoo -d odoo -i MODULE --stop-after-init && docker compose restart odoo` |
| **docker-compose.yml** | Stop and restart stack | `docker compose down && docker compose up -d` |
| **odoo.conf** | Stop and restart stack | `docker compose down && docker compose up -d` |

---

## Python Code Changes

**Files affected:**
- `models/*.py`
- `wizards/*.py`
- `controllers/*.py`
- `__init__.py`
- `__manifest__.py`

**Action:** Restart Odoo container only (no need to stop entire stack)

```bash
cd sandbox/dev
docker compose restart odoo
```

**Why:** Python code is loaded when Odoo starts. Restarting reloads the modules.

**Note:** Main server keeps running during restart. Downtime: ~5-10 seconds.

---

## XML/QWeb View Changes

**Files affected:**
- `views/*.xml`
- `security/ir.model.access.csv`
- `data/*.xml`
- Menu definitions
- Report templates

**Action:** Upgrade module, then restart

```bash
cd sandbox/dev
docker compose exec -T odoo odoo -d odoo -u ipai_finance_ppm --stop-after-init
docker compose restart odoo
```

**Why:** XML data must be re-imported to the database. Upgrade applies changes.

**Note:** `--stop-after-init` runs upgrade then exits. Main server unaffected.

---

## Static Assets (JS/SCSS)

**Files affected:**
- `static/src/js/*.js`
- `static/src/scss/*.scss`
- `static/src/xml/*.xml` (QWeb JS templates)

**Best Practice:** Enable dev mode for automatic asset reloading

### Enable Dev Mode (Recommended)

Add to `odoo.conf`:
```ini
# Development settings
dev_mode = all
```

Or set environment variable in `docker-compose.yml`:
```yaml
environment:
  ODOO_DEV: all
```

**Then restart:**
```bash
docker compose restart odoo
```

### Manual Asset Update (Without Dev Mode)

```bash
docker compose exec -T odoo odoo -d odoo -u ipai_finance_ppm --stop-after-init
docker compose restart odoo
```

**Why:** Assets are bundled and cached. Dev mode disables caching for faster iteration.

---

## Installing New Modules

**Action:** Install via CLI (preferred for deterministic dev)

```bash
cd sandbox/dev
docker compose exec -T odoo odoo -d odoo -i ipai_finance_ppm --stop-after-init
docker compose restart odoo
```

**Alternative:** Install via UI (Apps → Update Apps List → Install)

**Why:** CLI installation is reproducible and scriptable. UI installation requires manual steps.

**Note:** You can install modules while Odoo is running. The install command starts a short-lived process.

---

## When to Stop Entire Stack

**Only for infrastructure changes:**

### docker-compose.yml Changes
```bash
docker compose down
docker compose up -d
```

### odoo.conf Changes (Paths/Mounts)
```bash
docker compose down
docker compose up -d
```

### PostgreSQL Settings
```bash
docker compose down
docker compose up -d
```

### Port/Network Changes
```bash
docker compose down
docker compose up -d
```

**Why:** These changes affect Docker configuration, not just Odoo application code.

---

## Makefile Shortcuts

Add these shortcuts to `Makefile`:

```makefile
# Hot-reload development commands

.PHONY: dev-restart
dev-restart: ## Restart Odoo only (Python changes)
	docker compose restart odoo

.PHONY: dev-upgrade
dev-upgrade: ## Upgrade module (usage: make dev-upgrade MODULE=ipai_finance_ppm)
	@if [ -z "$(MODULE)" ]; then \
		echo "Error: MODULE not specified"; \
		echo "Usage: make dev-upgrade MODULE=module_name"; \
		exit 1; \
	fi
	docker compose exec -T odoo odoo -d odoo -u $(MODULE) --stop-after-init
	docker compose restart odoo

.PHONY: dev-install
dev-install: ## Install module (usage: make dev-install MODULE=ipai_finance_ppm)
	@if [ -z "$(MODULE)" ]; then \
		echo "Error: MODULE not specified"; \
		echo "Usage: make dev-install MODULE=module_name"; \
		exit 1; \
	fi
	docker compose exec -T odoo odoo -d odoo -i $(MODULE) --stop-after-init
	docker compose restart odoo

.PHONY: dev-enable-assets
dev-enable-assets: ## Enable dev mode for automatic asset reloading
	@echo "Enabling dev mode in odoo.conf..."
	@grep -q "^dev_mode = all" odoo.conf || echo "dev_mode = all" >> odoo.conf
	docker compose restart odoo
	@echo "✓ Dev mode enabled. Assets will reload automatically."

.PHONY: dev-disable-assets
dev-disable-assets: ## Disable dev mode
	@sed -i.bak '/^dev_mode = all/d' odoo.conf
	docker compose restart odoo
	@echo "✓ Dev mode disabled."
```

**Usage:**
```bash
# Python changes
make dev-restart

# XML/view changes
make dev-upgrade MODULE=ipai_finance_ppm

# New module
make dev-install MODULE=ipai_finance_ppm

# Enable asset hot-reload
make dev-enable-assets
```

---

## Development Workflow Examples

### Example 1: Modifying Python Business Logic

```bash
# 1. Edit Python file
vim ../../addons/ipai/ipai_finance_ppm/models/bir_schedule.py

# 2. Restart Odoo
make dev-restart

# 3. Test in browser
open http://localhost:8069
```

---

### Example 2: Adding New View

```bash
# 1. Edit XML file
vim ../../addons/ipai/ipai_finance_ppm/views/bir_schedule_views.xml

# 2. Upgrade module
make dev-upgrade MODULE=ipai_finance_ppm

# 3. Test in browser
open http://localhost:8069
```

---

### Example 3: Modifying JavaScript Widget

```bash
# 1. Enable dev mode (first time only)
make dev-enable-assets

# 2. Edit JS file
vim ../../addons/ipai/ipai_finance_ppm/static/src/js/widget.js

# 3. Refresh browser (assets reload automatically)
# No restart needed in dev mode!
```

---

### Example 4: Creating New Module

```bash
# 1. Create module structure
mkdir -p ../../addons/ipai/ipai_new_module
# ... create files ...

# 2. Update apps list (if not auto-detected)
docker compose exec -T odoo odoo -d odoo -u base --stop-after-init

# 3. Install module
make dev-install MODULE=ipai_new_module

# 4. Verify
open http://localhost:8069/web#action=base.open_module_tree
```

---

## Troubleshooting

### Module Changes Not Appearing

**Symptom:** Code changes don't reflect in Odoo

**Check:**
1. Did you restart Odoo? `make dev-restart`
2. Did you upgrade module? `make dev-upgrade MODULE=your_module`
3. Is module installed? Check Apps list
4. Are logs showing errors? `make logs-odoo`

**Fix:**
```bash
# Force module upgrade
docker compose exec -T odoo odoo -d odoo -u your_module --stop-after-init
docker compose restart odoo

# Check logs
make logs-odoo
```

---

### Assets Not Reloading

**Symptom:** JS/CSS changes not visible

**Check:**
1. Is dev mode enabled? `grep dev_mode odoo.conf`
2. Did you clear browser cache? (Ctrl+Shift+R)
3. Did you upgrade module? `make dev-upgrade MODULE=your_module`

**Fix:**
```bash
# Enable dev mode
make dev-enable-assets

# Clear browser cache
# Ctrl+Shift+R (hard reload)

# Or upgrade module manually
make dev-upgrade MODULE=your_module
```

---

### "Module not found" Error

**Symptom:** Odoo can't find your module

**Check:**
1. Is module in correct directory? `ls ../../addons/ipai/`
2. Does `__manifest__.py` exist? `cat ../../addons/ipai/your_module/__manifest__.py`
3. Is addons path correct? `make check-addons`

**Fix:**
```bash
# Verify module exists
ls -la ../../addons/ipai/your_module/

# Update apps list
docker compose exec -T odoo odoo -d odoo -u base --stop-after-init

# Check addons path
docker compose exec odoo cat /etc/odoo/odoo.conf | grep addons_path

# Restart Odoo
docker compose restart odoo
```

---

## Performance Tips

### 1. Use Dev Mode Selectively

**Enable during asset development:**
```bash
make dev-enable-assets
```

**Disable for Python development:**
```bash
make dev-disable-assets
```

**Why:** Dev mode disables asset caching, which slows down page loads.

---

### 2. Restart Only What's Needed

**Python changes:**
```bash
docker compose restart odoo  # Fast (~5-10 seconds)
```

**Not:**
```bash
docker compose down && docker compose up -d  # Slow (~30-60 seconds)
```

---

### 3. Use `-T` Flag for Non-Interactive Commands

**Correct:**
```bash
docker compose exec -T odoo odoo -d odoo -u module --stop-after-init
```

**Why:** `-T` disables TTY allocation for faster execution in scripts.

---

### 4. Batch Module Operations

**Install multiple modules at once:**
```bash
docker compose exec -T odoo odoo -d odoo -i module1,module2,module3 --stop-after-init
```

**Upgrade multiple modules:**
```bash
docker compose exec -T odoo odoo -d odoo -u module1,module2,module3 --stop-after-init
```

---

## Quick Reference

| Task | Command | Downtime |
|------|---------|----------|
| **Python change** | `make dev-restart` | ~5-10s |
| **View change** | `make dev-upgrade MODULE=x` | ~5-10s |
| **New module** | `make dev-install MODULE=x` | ~5-10s |
| **Asset dev** | `make dev-enable-assets` | ~5-10s |
| **Stack change** | `docker compose down && up -d` | ~30-60s |

---

## Best Practices

1. ✅ **Enable dev mode** during frontend development
2. ✅ **Disable dev mode** for Python/backend work (faster)
3. ✅ **Use Makefile shortcuts** for consistency
4. ✅ **Restart only Odoo** for code changes (not entire stack)
5. ✅ **Upgrade modules** for XML/data changes
6. ✅ **Check logs** when changes don't appear
7. ✅ **Clear browser cache** if assets don't update
8. ❌ **Don't stop entire stack** unless changing infrastructure

---

**Last Updated:** 2026-01-14
**Odoo Version:** 18.0
**Environment:** Local Development Sandbox
