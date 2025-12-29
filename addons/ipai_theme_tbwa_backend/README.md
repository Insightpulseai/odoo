# TBWA Backend Theme - Installation Guide

## Quick Install (Docker - DigitalOcean)

### Step 1: Copy module to server

```bash
# From your local machine
scp -r ipai_theme_tbwa_backend root@159.223.75.148:/opt/odoo/addons/
```

Or using git (recommended):
```bash
# SSH into server
ssh root@159.223.75.148

# Clone/copy to addons path
cd /opt/odoo/addons
# If using git submodule or direct copy
```

### Step 2: Verify addons path includes the module location

```bash
# Check odoo.conf
cat /opt/odoo/odoo.conf | grep addons_path

# Should show something like:
# addons_path = /opt/odoo/addons,/mnt/extra-addons
```

### Step 3: Install the module

```bash
# Method A: Docker exec (recommended)
docker exec -it odoo-web odoo -c /etc/odoo/odoo.conf \
    -d odoo_core \
    -i ipai_theme_tbwa_backend \
    --stop-after-init

# Method B: If using docker-compose
docker-compose exec web odoo -d odoo_core -i ipai_theme_tbwa_backend --stop-after-init
```

### Step 4: Restart and clear assets

```bash
# Restart container
docker restart odoo-web

# Force asset regeneration (if needed)
docker exec -it odoo-web odoo -c /etc/odoo/odoo.conf \
    -d odoo_core \
    -u ipai_theme_tbwa_backend \
    --stop-after-init
```

### Step 5: Clear browser cache

```
Ctrl+Shift+R (hard refresh)
```

---

## Troubleshooting

### Module not found in Apps

```bash
# Update module list first
docker exec -it odoo-web odoo shell -d odoo_core << 'EOF'
env['ir.module.module'].update_list()
env.cr.commit()
EOF

# Then search in Apps → Update Apps List → Search "TBWA"
```

### Assets not loading / old styles

```bash
# Clear asset cache
docker exec -it odoo-web psql -U odoo -d odoo_core -c "
DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%';
"

# Restart
docker restart odoo-web
```

### Check if module is installed

```bash
docker exec -it odoo-web psql -U odoo -d odoo_core -c "
SELECT name, state FROM ir_module_module WHERE name = 'ipai_theme_tbwa_backend';
"
```

### View asset bundles

```bash
# Check if SCSS is being loaded
docker exec -it odoo-web psql -U odoo -d odoo_core -c "
SELECT name, path FROM ir_asset WHERE path LIKE '%tbwa%';
"
```

---

## Install via Odoo UI (Alternative)

1. **Go to Apps** → Click "Update Apps List" (in top menu)
2. **Remove "Apps" filter** (click the X on the filter)
3. **Search**: `TBWA`
4. **Click Install** on "TBWA Backend Theme (IPAI)"
5. **Refresh browser** (Ctrl+Shift+R)

---

## File Structure

```
ipai_theme_tbwa_backend/
├── __init__.py
├── __manifest__.py
└── static/
    └── src/
        ├── scss/
        │   ├── variables.scss      # Odoo/Bootstrap var overrides
        │   ├── variables_dark.scss # Dark mode vars
        │   ├── fonts.scss          # @font-face declarations
        │   └── backend.scss        # UI component styling
        └── fonts/
            ├── IBMPlexSans-Regular.woff2
            ├── IBMPlexSans-Medium.woff2
            ├── IBMPlexSans-SemiBold.woff2
            └── IBMPlexSans-Bold.woff2
```

---

## What Changes

| Element | Before | After |
|---------|--------|-------|
| Primary color | Odoo Purple (#714B67) | TBWA Yellow (#FFD800) |
| Navbar | Purple gradient | Solid Black |
| Buttons | Purple bg, white text | Yellow bg, **black text** |
| Font | Roboto | IBM Plex Sans |
| Border radius | 4px | 14-16px (rounded) |
| Cards | Flat | Subtle shadow + rounded |

---

## With MuK Theme (Optional)

If you have `muk_web_theme` installed, this theme works alongside it.
The TBWA variables will override MuK's defaults.

Install order:
1. `muk_web_theme` (base theme)
2. `ipai_theme_tbwa_backend` (branding layer)

```bash
docker exec -it odoo-web odoo -d odoo_core \
    -i muk_web_theme,ipai_theme_tbwa_backend \
    --stop-after-init
```
