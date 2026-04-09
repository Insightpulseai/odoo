# CP-7: Final Smoke Test — 10/10 PASS

> **Date:** 2026-03-20T00:10:55Z
> **Status:** DONE

## Result

```
Odoo 18 Go-Live Smoke Test
Target: https://erp.insightpulseai.com
Date: 2026-03-20T00:10:55Z
---

PASS: Health endpoint /web/health
PASS: Login page /web/login
PASS: Login form present
PASS: Login button visible
PASS: Asset bundles serve compressed
PASS: Database manager blocked
PASS: Azure Front Door routing
PASS: Security headers present
PASS: Session cookie HttpOnly
PASS: X-Frame-Options set
---
Total: 10 | Pass: 10 | Fail: 0
SMOKE TEST: PASS
```

## Method

```bash
bash scripts/odoo/smoke_test.sh https://erp.insightpulseai.com
```

## Notes

- Asset bundle failure from earlier session (2026-03-20T06:00+08:00) is now resolved
- Resolution: stale ir_attachment records cleared, assets regenerated server-side
- The Asset_Flush_Dev pipeline stage will prevent recurrence on future deploys
