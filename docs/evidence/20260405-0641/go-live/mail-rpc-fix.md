# mail/discuss RPC 404 Fix Evidence

**Date**: 2026-04-05T08:30Z
**Claim**: "No blocking application RPC errors"
**Status**: proven

## Error (Before)

```
werkzeug.exceptions.NotFound: 404 Not Found
  File "mail/controllers/webclient.py", line 50, in _process_request_for_all
    raise NotFound()
```

Client: `RPC_ERROR: 404: Not Found` on `/mail/data` after login.

## Root Cause

The `mail` module's database schema was stale on `odoo_dev`. The HA container image
(`ipai-odoo:18.0-copilot`) ships mail module code from the Odoo 18 base image, but
the database had not been updated to match.

## Fix

Deployed revision `--0000013` with `-u mail` arg to trigger module update during startup:
```yaml
args:
  - odoo
  - --addons-path=/mnt/extra-addons/ipai,/usr/lib/python3/dist-packages/odoo/addons
  - --database=odoo_dev
  - --no-database-list
  - --proxy-mode
  - -u
  - mail
```

Then redeployed steady-state revision `--0000014` without `-u mail`.

## Verification

```
/mail/data → HTTP 200 (was 404)
/web/health → HTTP 200
/web/login → HTTP 200
```

Revision `--0000014`: Healthy, Running.
