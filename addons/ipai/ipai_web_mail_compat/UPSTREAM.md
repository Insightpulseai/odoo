# UPSTREAM — ipai_web_mail_compat

## What this module patches

| # | Upstream file (full asset path) | Bug | Odoo 19 fix |
|---|--------------------------------|-----|-------------|
| 1 | `mail_tracking/static/src/services/store_service_patch.esm.js` | Calls `Record.one("Thread")` in `Store.setup()`; `Record.one` was removed in Odoo 19 | Removed `setup()` override; `store.failed` initialised as plain object in `onStarted()` |
| 2 | `mail_tracking/static/src/core/discuss/discuss_sidebar_mailboxes.xml` | Inherits from `mail.Discuss.mobileTopbar` which was renamed in Odoo 19 | Changed `t-inherit` to `mail.DiscussContent.mobileTopbar` |

## Upstream references

- **OCA repository**: <https://github.com/OCA/mail>
- **Module**: `mail_tracking`
- **Broken version pinned in `oca-aggregate.yml`**: `19.0.1.0.8`
- **Errors produced**:
  - `TypeError: Record.one is not a function` (browser console)
  - `Missing (extension) parent templates: mail.Discuss.mobileTopbar` (browser console)

## Removal criteria

Delete `ipai_web_mail_compat` and uninstall it when **all** of the following are true:

1. OCA `mail_tracking` releases a version that removes `Record.one()` from `Store.setup()`.
2. OCA `mail_tracking` releases a version with `t-inherit="mail.DiscussContent.mobileTopbar"`.
3. `oca-aggregate.yml` is updated to pin the fixed OCA version.
4. Neither browser console error reappears after a full asset rebuild.

## How to confirm removal is safe

```bash
# 1. Check OCA module version in the DB
odoo shell -d odoo_dev -c config/dev/odoo.conf <<'EOF'
env['ir.module.module'].search([('name','=','mail_tracking')]).mapped('installed_version')
EOF

# 2. Assert probe no longer needed (errors gone without this module installed)
# In browser DevTools after uninstalling ipai_web_mail_compat:
#   window.__IPAI_COMPAT__   → should be undefined (module gone)
#   Check console for the two errors above → should not appear

# 3. Verify server-side marker absent (expected once removed)
#   grep "IPAI_COMPAT_ACTIVE" /var/log/odoo/odoo.log  → no match (clean)
```

## Contacts / tracking

- Opened: 2026-02-23
- Owner: devops@insightpulseai.com
- Related PR: (this commit)
