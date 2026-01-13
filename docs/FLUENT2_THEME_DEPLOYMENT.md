# Fluent 2 Finance Theme Deployment Guide

Complete deployment guide for `ipai_theme_fluent_finance` module on production Odoo 18.0 CE.

## Quick Summary

**Module**: `ipai_theme_fluent_finance`
**Target**: Finance PPM landing pages with Mattermost-inspired UI
**Design System**: Microsoft Fluent 2 Web (751+ design tokens)
**Theme Support**: Light + Dark with automatic switching
**Status**: Ready for deployment

---

## Prerequisites

- ✅ Odoo 18.0 CE running on production server (178.128.112.214)
- ✅ `ipai_finance_ppm` module installed (version 18.0.1.0.1+)
- ✅ Production database: `odoo_core`
- ✅ Docker container: `odoo-prod`
- ✅ SSH access to production server

---

## Deployment Steps

### 1. Pull Latest Code

SSH to production server and pull changes:

```bash
ssh root@178.128.112.214
cd /opt/odoo-ce/repo

# Pull latest code
git fetch origin
git checkout feat/deterministic-scss-verification
git pull origin feat/deterministic-scss-verification

# Verify theme module exists
ls -la addons/ipai/ipai_theme_fluent_finance/
# Expected: __init__.py, __manifest__.py, README.md, static/, views/
```

### 2. Install Module

Install the theme module in Odoo:

```bash
# Option A: Install with restart
docker exec odoo-prod odoo -d odoo_core -i ipai_theme_fluent_finance --stop-after-init
docker restart odoo-prod

# Option B: Install without restart (faster)
docker exec odoo-prod odoo -d odoo_core -i ipai_theme_fluent_finance --stop-after-init
# Then manually restart: docker restart odoo-prod
```

### 3. Verify Installation

Check module installation status:

```bash
# Verify module installed
docker exec odoo-prod odoo shell -d odoo_core << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
module = env['ir.module.module'].search([('name', '=', 'ipai_theme_fluent_finance')])
print(f"Module: {module.name}")
print(f"State: {module.state}")
print(f"Version: {module.latest_version}")
print(f"✅ Installed: {module.state == 'installed'}")
EOF

# Expected output:
# Module: ipai_theme_fluent_finance
# State: installed
# Version: 18.0.1.0.0
# ✅ Installed: True
```

### 4. Clear Assets Cache

Force Odoo to regenerate CSS assets:

```bash
# Clear assets cache
docker exec odoo-prod odoo -d odoo_core --dev=all --stop-after-init

# Restart Odoo
docker restart odoo-prod

# Wait for startup (check logs)
docker logs -f odoo-prod | grep -E "(Odoo|Ready|HTTP)"
# Expected: INFO odoo.service.server: HTTP service (werkzeug) running on 0.0.0.0:8069
```

### 5. Test in Browser

Open Finance PPM dashboard:

**URL**: https://erp.insightpulseai.net/web#action=ipai_finance_ppm.action_finance_ppm_dashboard

**Expected Visual Changes:**
1. **Kanban View**:
   - Mattermost-style cards with smooth hover effects
   - Status indicators via left border colors (green/amber/red)
   - Clean card shadows and spacing
   - Fluent 2 typography (Segoe UI)

2. **List View**:
   - Table header with Mattermost-style design
   - Hover effects on rows
   - Selected row highlighting with brand color accent

3. **Form View**:
   - Modal-style form with rounded corners
   - Primary/secondary button distinction
   - Status badges with semantic colors

4. **Color Palette**:
   - Brand primary: Microsoft Blue (#0F548C)
   - Success: Green (#0E700E)
   - Warning: Amber (#8A5D00)
   - Error: Red (#C50F1F)

### 6. Test Dark Mode

Toggle dark mode to verify theme switching:

```bash
# Navigate to: User Menu > Preferences
# Change Theme: Light → Dark
# Refresh Finance PPM page
```

**Expected Dark Theme Colors:**
- Background: Dark gray (#1E1E1E)
- Brand primary: Light blue (#479EF5)
- Text: White (#FFFFFF)
- Status indicators adapt to dark theme

---

## Verification Checklist

Run all checks before marking deployment complete:

- [ ] **Module Installed**: `docker exec odoo-prod odoo shell -d odoo_core -c "env['ir.module.module'].search([('name','=','ipai_theme_fluent_finance')]).state"` returns `installed`

- [ ] **Assets Loaded**: Browser DevTools > Network > CSS shows:
  - `ipai_theme_fluent_finance/static/src/css/tokens.css` (200 OK)
  - `ipai_theme_fluent_finance/static/src/css/finance_landing.css` (200 OK)

- [ ] **Visual Parity**: Finance PPM dashboard shows Mattermost-style UI

- [ ] **Light Theme**: Default theme shows Microsoft Blue brand color

- [ ] **Dark Theme**: Dark mode activates with adapted colors

- [ ] **Responsive**: Mobile view (< 768px) shows stacked layout

- [ ] **No Errors**: Browser console shows no CSS errors

- [ ] **Performance**: Page load time < 3 seconds

---

## Troubleshooting

### Issue 1: Theme Not Applied

**Symptoms**: Finance PPM still shows default Odoo theme

**Check 1: Module Installed**
```bash
docker exec odoo-prod odoo shell -d odoo_core << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
module = env['ir.module.module'].search([('name', '=', 'ipai_theme_fluent_finance')])
if module.state != 'installed':
    print(f"❌ Module not installed: {module.state}")
else:
    print("✅ Module installed")
EOF
```

**Solution**: Install module with `docker exec odoo-prod odoo -d odoo_core -i ipai_theme_fluent_finance --stop-after-init`

**Check 2: Assets Generated**
```bash
# Check if CSS files exist in Odoo assets
docker exec odoo-prod ls -la /var/lib/odoo/filestore/odoo_core/assets/
# Should see: web.assets_backend*.css files with recent timestamps
```

**Solution**: Force asset regeneration with `docker exec odoo-prod odoo -d odoo_core --dev=all --stop-after-init` then `docker restart odoo-prod`

**Check 3: Browser Cache**
```bash
# Hard refresh in browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
# Or clear browser cache completely
```

### Issue 2: Styles Conflict

**Symptoms**: Some elements show mixed old/new styles

**Check**: CSS specificity conflicts

**Solution**: The theme uses moderate specificity. If conflicts occur, increase specificity in `finance_landing.css`:

```css
/* Before */
.o_kanban_record {
  background-color: var(--ipai-component-card-bg);
}

/* After (higher specificity) */
.o_action[data-model="finance.ppm.dashboard"] .o_kanban_record {
  background-color: var(--ipai-component-card-bg);
}
```

### Issue 3: Dark Mode Not Working

**Symptoms**: Dark mode toggle doesn't change theme

**Check 1: Odoo Theme Setting**
```bash
# Navigate to: User Menu > Preferences > Theme
# Should have options: Light, Dark
```

**Check 2: CSS Class Applied**
```bash
# Browser DevTools > Elements > <html>
# In dark mode, should have class: o_web_client dark
```

**Check 3: Token Variables**
```bash
# Browser DevTools > Elements > Computed
# Search for: --ipai-color-brand-primary
# Light: #0F548C
# Dark: #479EF5
```

**Solution**: Clear browser cache and ensure theme preference saved in Odoo

### Issue 4: Missing Fonts

**Symptoms**: Fonts look wrong, not using Segoe UI

**Check**: Font family applied

**Browser DevTools > Elements > Computed > font-family**
Should show: `"Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue", sans-serif`

**Solution**: Fonts fallback correctly - if Segoe UI not available, system fonts used

---

## Rollback Plan

If issues occur and rollback is needed:

```bash
# Uninstall theme module
docker exec odoo-prod odoo -d odoo_core -u ipai_theme_fluent_finance --stop-after-init

# Force asset rebuild
docker exec odoo-prod odoo -d odoo_core --dev=all --stop-after-init

# Restart Odoo
docker restart odoo-prod

# Verify rollback
docker exec odoo-prod odoo shell -d odoo_core << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
module = env['ir.module.module'].search([('name', '=', 'ipai_theme_fluent_finance')])
print(f"Module state after rollback: {module.state}")
# Should return: uninstalled
EOF
```

**Note**: Rolling back removes theme but doesn't affect data - Finance PPM records remain intact.

---

## Post-Deployment Tasks

### Monitor for 24 Hours

```bash
# Check Odoo error logs
docker logs odoo-prod --since 24h | grep -i "error\|exception"

# Check browser console errors (via user reports)
# Ask users to report any visual glitches

# Monitor page load times
# Finance PPM should load in < 3 seconds
```

### Gather User Feedback

**Questions to Ask**:
1. "Does the Finance PPM page look cleaner/more modern?"
2. "Do the colors match Mattermost's familiar interface?"
3. "Is dark mode comfortable to use?"
4. "Are there any visual glitches or misaligned elements?"

### Iterate Based on Feedback

Common customization requests:

**Request**: "Brand color doesn't match our company colors"
**Solution**: Override `--ipai-color-brand-primary` in custom CSS

**Request**: "Spacing too tight/loose"
**Solution**: Adjust `--ipai-spacing-*` tokens

**Request**: "Need bigger fonts"
**Solution**: Increase `--ipai-typography-font-size-*` tokens

---

## Performance Metrics

**Target Metrics**:
- **CSS File Size**: < 100KB (current: ~50KB)
- **Load Time**: < 50ms for CSS (cached)
- **First Paint**: < 1 second
- **Time to Interactive**: < 3 seconds

**Actual Production Metrics** (to be measured):
```bash
# Use browser DevTools > Network > CSS tab
# Check: ipai_theme_fluent_finance/static/src/css/tokens.css
# Check: ipai_theme_fluent_finance/static/src/css/finance_landing.css
# Record: Size (KB) and Load Time (ms)
```

---

## Next Steps (Optional Enhancements)

### 1. Extend to Other Modules

Apply Fluent 2 theme to other finance modules:

```bash
# Create extended theme
cp -r addons/ipai/ipai_theme_fluent_finance addons/ipai/ipai_theme_fluent_extended

# Update __manifest__.py depends
"depends": [
    "web",
    "ipai_finance_ppm",
    "ipai_finance_bir_compliance",  # Add more modules
    "ipai_finance_month_end",
],
```

### 2. Custom Brand Colors

Create company-specific color overrides:

```css
/* addons/ipai/ipai_theme_fluent_custom/static/src/css/custom.css */
:root {
  /* Override with company brand colors */
  --ipai-color-brand-primary: #YOUR_PRIMARY_COLOR;
  --ipai-color-brand-secondary: #YOUR_SECONDARY_COLOR;
}
```

### 3. Add More Mattermost Patterns

Enhance with additional Mattermost UI elements:

- **Notification badges** for updates
- **Thread views** for related records
- **Emoji reactions** for approval workflows
- **@mentions** for user assignments

### 4. Analytics Integration

Track theme adoption and user preferences:

```python
# addons/ipai/ipai_theme_fluent_finance/models/theme_analytics.py
class ThemeAnalytics(models.Model):
    _name = 'theme.analytics'

    user_id = fields.Many2one('res.users', string='User')
    theme_preference = fields.Selection([('light', 'Light'), ('dark', 'Dark')])
    last_used = fields.Datetime(default=fields.Datetime.now)
```

---

## Documentation References

- **Module README**: `addons/ipai/ipai_theme_fluent_finance/README.md`
- **Token Reference**: `addons/ipai/ipai_theme_fluent_finance/static/src/css/tokens.css`
- **Finance Landing CSS**: `addons/ipai/ipai_theme_fluent_finance/static/src/css/finance_landing.css`
- **Fluent 2 Design System**: https://www.figma.com/community/file/1159318952063191910
- **Mattermost UI Patterns**: https://mattermost.com/

---

## Support

For deployment issues:
1. Check this guide's troubleshooting section
2. Review browser DevTools > Console for errors
3. Check Odoo logs: `docker logs odoo-prod | grep -i theme`
4. Escalate to DevOps if infrastructure issue

---

**Deployment Date**: [To be filled after deployment]
**Deployed By**: [To be filled]
**Verification Status**: [To be filled]
**Production URL**: https://erp.insightpulseai.net

---

*Last updated: 2025-01-14*
