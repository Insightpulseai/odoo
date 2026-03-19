# Login Surface Contract

> Rules for Odoo login page branding, debranding, and CI enforcement.

## Branding Requirements

1. Login page must display the real company logo, not the Odoo placeholder
2. No "Your logo" or "My Company" placeholder text may appear
3. No "Powered by Odoo", "Odoo S.A.", "odoo.com", or Enterprise upsell text
4. Page title must not be the default "Odoo"
5. Expected brand name (e.g. "InsightPulse") must be visible on the page

## Module Ownership

| Concern | Owner | Source |
|---------|-------|--------|
| Company logo and name | `res.company` configuration | Settings > General Settings > Companies |
| Remove "Powered by Odoo" footer | `disable_odoo_online` | OCA/server-brand |
| Remove Enterprise upsell prompts | `remove_odoo_enterprise` | OCA/server-brand |
| Remove Odoo branding from emails | `mail_debrand` | OCA/social |
| Page title override | `web_debranding` or `disable_odoo_online` | OCA/server-brand |

### Required OCA Debranding Modules

These modules must be installed and active in all environments:

- **`disable_odoo_online`** -- Removes "Powered by Odoo" footer, database manager links, and odoo.com references from the login page and web client
- **`remove_odoo_enterprise`** -- Strips Enterprise upgrade prompts and "Upgrade" menu items
- **`mail_debrand`** -- Removes Odoo branding from outbound email templates and footers

All three are sourced from OCA repos (server-brand / social) on the 19.0 branch. They must not be modified locally. If customization is needed, create an `ipai_*` override module.

## Form Control Requirements

The login page must contain:

- An `<input>` with `name="login"` for the username/email field
- An `<input>` with `type="password"` for the password field
- A `<button>` or `<input>` with `type="submit"` for the login action

These are provided by core Odoo and should never be missing unless the login template is broken.

## CI Smoke Test

The `tests/test_login_surface_smoke.py` test validates all requirements above against a live Odoo instance. It uses `urllib` only (no external dependencies) and skips gracefully if Odoo is unreachable.

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ODOO_URL` | `http://localhost:8069` | Target Odoo instance |
| `ODOO_DB` | `odoo_dev` | Database name |
| `EXPECTED_BRAND` | `InsightPulse` | Brand text expected on login page |

### What the Test Checks

| Test | Fails If |
|------|----------|
| `test_login_returns_200` | /web/login does not return HTTP 200 |
| `test_login_has_username_input` | No `<input name="login">` found |
| `test_login_has_password_input` | No `<input type="password">` found |
| `test_login_has_submit_button` | No submit button found |
| `test_no_logo_placeholder` | "Your logo", "My Company", or similar placeholder text present |
| `test_no_odoo_branding` | Any Odoo branding marker found in page source |
| `test_no_powered_by_odoo` | "Powered by Odoo" in any form (including anchor tags) |
| `test_expected_brand_present` | Configured brand name not found on page |
| `test_page_title_not_default` | `<title>` is still "Odoo" |

## Common Failure Causes

| Cause | Symptom | Fix |
|-------|---------|-----|
| `disable_odoo_online` not installed | "Powered by Odoo" in footer | Install module: `-i disable_odoo_online` |
| `remove_odoo_enterprise` not installed | "Upgrade" prompts visible | Install module: `-i remove_odoo_enterprise` |
| Company logo not configured | "Your logo" placeholder | Upload logo in Settings > Companies |
| Company name not set | "My Company" on page | Set name in Settings > Companies |
| Brand not in page title | Title is "Odoo" | Configure via `disable_odoo_online` settings or `web.base.url.title` system parameter |
| Debranding module outdated | Partial branding remains | Update OCA submodule: `git submodule update --remote addons/oca/server-brand` |
| Custom login template override | Form controls missing | Check `ipai_*` modules overriding `web.login` template |
