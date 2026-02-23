# UPSTREAM — ipai_web_mail_compat

## What this module patches

| # | Upstream file (full asset path) | Bug | Fix |
|---|--------------------------------|-----|-----|
| 1 | `mail_tracking/static/src/services/store_service_patch.esm.js` | Calls `Record.one("Thread")` in `Store.setup()` — removed in Odoo 19 | Drops `setup()` override; `store.failed` set as plain object in `onStarted()` |
| 2 | `mail_tracking/static/src/core/discuss/discuss_sidebar_mailboxes.xml` | Inherits from `mail.Discuss.mobileTopbar` — renamed in Odoo 19 | `t-inherit` changed to `mail.DiscussContent.mobileTopbar` |

## Upstream references

- **OCA repository**: <https://github.com/OCA/mail>
- **Module**: `mail_tracking`
- **Broken version**: `19.0.1.0.8` (pinned in `oca-aggregate.yml`)
- **Errors produced**:
  - `TypeError: Record.one is not a function` (browser console)
  - `Missing (extension) parent templates: mail.Discuss.mobileTopbar` (browser console)

## Removal criteria

Delete this module (and uninstall it) when **all** conditions are met:

1. OCA `mail_tracking` publishes a fix that removes `Record.one()` from `Store.setup()`.
2. OCA `mail_tracking` publishes a fix with `t-inherit="mail.DiscussContent.mobileTopbar"`.
3. `oca-aggregate.yml` is updated to pin the fixed version.
4. The CI verifier script exits 0 **without** this module installed.
5. The smoke tests pass **without** this module installed.

## CI validation (primary)

```bash
# 1. Install module
odoo -d odoo_dev -i ipai_web_mail_compat --stop-after-init

# 2. Run smoke tests (blocks template regressions)
odoo -d odoo_dev --test-enable --stop-after-init -i ipai_web_mail_compat

# 3. Run asset verifier (no browser / no UI)
python3 scripts/verify_ipai_web_mail_compat.py \
    -d odoo_dev -c config/dev/odoo.conf

# 4. Grep server-side install marker
grep "IPAI_COMPAT_ACTIVE" /var/log/odoo/odoo.log | tail -3
```

All four must pass. This is the authoritative validation path.

## Secondary troubleshooting (browser)

Only needed when investigating a suspected asset caching issue after the
above checks already pass:

```
window.__IPAI_COMPAT__.mail_tracking.loaded  // → true
Store.prototype.__ipai_web_mail_compat_store_patched__  // → true
```

If the probe global is absent after CI passes, **rebuild assets and restart
Odoo** — do not trust a stale browser cache.

## Contacts / tracking

- Opened: 2026-02-23
- Owner: devops@insightpulseai.com
- Related issue: OCA/mail `mail_tracking` Odoo 19 JS store API + template rename
