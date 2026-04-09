# Front Door Origin Cutover Evidence — #680

**Date**: 2026-04-05T06:41Z
**Issue**: Insightpulseai/odoo#680
**Revision**: `ipai-odoo-ha-web--0000012`
**Environment**: `ipai-odoo-ha-env` (grayhill-34461e89)

## Origin Target

- AFD origin: `ipai-odoo-ha-web.grayhill-34461e89.southeastasia.azurecontainerapps.io`
- Public hostname: `erp.insightpulseai.com`

## Fix Applied

**Root cause**: Odoo database selector exposed (`/web/login` → 303 → `/web/database/selector`).
The container image baked `list_db = False` into `odoo.conf`, but the CMD args
(`--addons-path=...`) override the config. Without explicit `--database` and
`--no-database-list` CLI args, Odoo fell back to showing the database selector.

**Resolution**: Updated container args via YAML patch:
```
args:
  - odoo
  - --addons-path=/mnt/extra-addons/ipai,/usr/lib/python3/dist-packages/odoo/addons
  - --database=odoo_dev
  - --no-database-list
  - --proxy-mode
```

## AFD Health Probe

```
/web/health → HTTP 200 (10/10 checks over 30s, stable)
```

## /web/login Verification

```
Before fix:  /web/login → HTTP 303 (redirect to /web/database/selector)
After fix:   /web/login → HTTP 200 (login page served, 4567 bytes)
```

## TLS Proof

```
Subject:   CN=erp.insightpulseai.com
Issuer:    DigiCert Inc / GeoTrust TLS RSA CA G1
Not Before: Mar 30 00:00:00 2026 GMT
Not After:  Sep 29 23:59:59 2026 GMT
SAN:       DNS:erp.insightpulseai.com
```

## WAF Check (No False Positives)

| Route | HTTP Code | Expected |
|-------|-----------|----------|
| /web/login | 200 | 200 (login page) |
| /web/health | 200 | 200 (health check) |
| /web/session/authenticate | 400 | 400 (missing POST body) |
| /web/dataset/call_kw | 400 | 400 (missing POST body) |
| /web/action/load | 400 | 400 (missing POST body) |
| /web/image | 200 | 200 |

No WAF-blocked responses (no 403/406/429). All 400s are expected Odoo behavior for unauthenticated GET on POST-only endpoints.

## Stable Probe Window (06:41:01 – 06:41:31 UTC)

```
06:41:01 /web/health → 200
06:41:05 /web/health → 200
06:41:08 /web/health → 200
06:41:11 /web/health → 200
06:41:14 /web/health → 200
06:41:18 /web/health → 200
06:41:21 /web/health → 200
06:41:24 /web/health → 200
06:41:27 /web/health → 200
06:41:31 /web/health → 200
```

## Revision Health

```json
{
  "name": "ipai-odoo-ha-web--0000012",
  "healthState": "Healthy",
  "runningState": "Running"
}
```

## Security Note

PG password is currently in plaintext env var (pre-existing state). Follow-up: migrate to Key Vault secret reference (`db-password` secret needs correct value set).

## Conclusion

All #680 acceptance criteria met:
- [x] AFD origin pointing to HA environment
- [x] `/web/login` returns 200 (not 303 database selector)
- [x] TLS certificate valid
- [x] WAF rules passing (no false positives)
- [x] Health probe stable
