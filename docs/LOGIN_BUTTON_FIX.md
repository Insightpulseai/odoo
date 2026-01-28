# Login Button Fix & Header Cleanup - Production Deployment

## Issues Fixed
1. Login button on https://erp.insightpulseai.net/ was not properly styled or functioning
2. Header had too many menu items cluttering the interface

## Solution Implemented

### 1. Header Cleanup - Remove All Menu Items
**Files**:
- `addons/ipai/ipai_web_theme_tbwa/views/webclient_templates.xml`
- `addons/ipai/ipai_web_theme_tbwa/static/src/scss/components/navbar.scss`

**Changes**:
- Removed all navigation menu items (Platform, Overview, Channels, etc.)
- Hidden breadcrumbs and search bar
- Keep only TBWA logo (left) and user menu (right)
- Added XPath templates to remove menu sections
- CSS rules to hide menu elements

**Result**: Clean, minimal header with only essential elements

### 2. Enhanced Login Button Styling
**File**: `addons/ipai/ipai_web_theme_tbwa/static/src/scss/components/login.scss`

Added comprehensive button styling:
- TBWA primary color (#000000) for button background
- White text for contrast
- Proper z-index (100) to prevent overlap
- Cursor pointer for clickability
- Hover/focus/active states with animations
- Disabled state handling

### 2. Form Input Styling
Added proper styling for login form inputs:
- Border styles and padding
- Focus states with TBWA primary color
- Proper z-index and positioning

### 3. Button Selectors
Targeted multiple button selectors to ensure compatibility:
- `.btn-primary`
- `.o_login_button`
- `button[type="submit"]`
- `.btn.btn-primary`

## Deployment Steps

### Automated Deployment
Run the deployment script:
```bash
./scripts/deploy_theme_to_production.sh
```

This script will:
1. Connect to production server (root@178.128.112.214)
2. Pull latest code from git
3. Restart Odoo container
4. Wait for Odoo to come back online
5. Verify health endpoint

### Manual Deployment
If needed, deploy manually:
```bash
# 1. SSH to production
ssh root@178.128.112.214

# 2. Update code
cd /opt/odoo-ce/repo
git pull origin main

# 3. Restart Odoo
docker restart odoo-prod

# 4. Wait for startup (30-60 seconds)
docker logs -f odoo-prod
```

## Verification

### Automated Verification
```bash
./scripts/verify_login_button.sh
```

### Manual Verification
1. Open https://erp.insightpulseai.net/web/login

2. Check header cleanup:
   - ✅ Only TBWA logo visible on left
   - ✅ Only user menu visible on right
   - ✅ No menu items (Platform, Overview, Channels, etc.)
   - ✅ No breadcrumbs
   - ✅ No search bar

3. Check button appearance:
   - ✅ Button background is black (#000000)
   - ✅ Button text is white
   - ✅ Cursor changes to pointer on hover
   - ✅ Button darkens to #1a1a1a on hover
   - ✅ Subtle lift animation on hover
   - ✅ Button is clickable

4. Test login flow:
   - ✅ Enter valid credentials
   - ✅ Click login button
   - ✅ Successful authentication

### Screenshot Capture
```bash
./scripts/screenshot_production.sh
```

Screenshots saved to: `docs/screenshots/`

## CSS Implementation

### Button Styles
```scss
.btn-primary,
.o_login_button,
button[type="submit"] {
  background-color: var(--tbwa-primary) !important;  // #000000
  border-color: var(--tbwa-primary) !important;
  color: var(--tbwa-text-on-primary) !important;     // #FFFFFF
  font-weight: 600;
  padding: 0.75rem 2rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease-in-out;
  position: relative;
  z-index: 100;
  cursor: pointer;

  &:hover {
    background-color: #1a1a1a !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
}
```

## Files Modified

1. `addons/ipai/ipai_web_theme_tbwa/views/webclient_templates.xml`
   - Added navbar_hide_menu template
   - XPath to remove menu sections
   - XPath to remove breadcrumbs

2. `addons/ipai/ipai_web_theme_tbwa/static/src/scss/components/navbar.scss`
   - CSS rules to hide all menu items
   - Keep only logo and user menu visible
   - Hide search bar and breadcrumbs

3. `addons/ipai/ipai_web_theme_tbwa/static/src/scss/components/login.scss`
   - Added login button styles
   - Added form input styles
   - Enhanced with hover/focus states

4. `scripts/verify_login_button.sh` (NEW)
   - Automated verification script
   - Checks page accessibility
   - Validates theme CSS presence

5. `scripts/deploy_theme_to_production.sh` (NEW)
   - Automated deployment script
   - Handles git pull and Docker restart
   - Includes health checks

6. `scripts/screenshot_production.sh` (NEW)
   - Screenshot capture script
   - Verification checklist
   - Manual and automated modes

## Commit History

- `df21c592` - fix(theme): enhance login button visibility and styling
- `33a10454` - chore(scripts): add login button verification and deployment scripts
- `89fed573` - feat(theme): hide all header menu items, keep only logo and user menu

## Next Steps

To apply this fix to production:

1. Run deployment script:
   ```bash
   ./scripts/deploy_theme_to_production.sh
   ```

2. Verify the fix:
   ```bash
   ./scripts/verify_login_button.sh
   ```

3. Manual test at https://erp.insightpulseai.net/web/login

## Production Server Details

- **Server**: 178.128.112.214
- **Container**: odoo-prod
- **Repo Path**: /opt/odoo-ce/repo
- **URL**: https://erp.insightpulseai.net

---
*Last Updated*: 2026-01-28
*Status*: ✅ Code deployed to git, ready for production deployment
