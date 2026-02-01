# Mailgun Integration Deployment Guide

**Status**: Code Ready - Deployment Required
**Date**: 2026-01-19
**Module**: ipai_enterprise_bridge
**Feature**: Mailgun inbound mailgate endpoint

---

## Executive Summary

The Mailgun → Odoo integration endpoint has been implemented in the `ipai_enterprise_bridge` module. All code changes are complete and ready for deployment to the production Odoo server at `erp.insightpulseai.com`.

**Root Cause (Resolved in Code)**:
- Odoo was returning HTTP 404 for `/mailgate/mailgun`
- No controller existed to handle Mailgun webhook POSTs

**Solution Implemented**:
- Created controller at `addons/ipai/ipai_enterprise_bridge/controllers/mailgun_mailgate.py`
- Added HTTP route: `/mailgate/mailgun` (POST, public, form-encoded)
- Parses Mailgun payload and creates `mail.message` records

---

## Files Changed

### 1. `addons/ipai/ipai_enterprise_bridge/controllers/__init__.py`
**Status**: Created
**Content**:
```python
from . import mailgun_mailgate
```

### 2. `addons/ipai/ipai_enterprise_bridge/controllers/mailgun_mailgate.py`
**Status**: Created
**Purpose**: Implements `/mailgate/mailgun` HTTP endpoint
**Key Features**:
- Accepts Mailgun form-encoded POSTs
- Extracts sender, recipient, subject, body-plain
- Creates mail.message records via `request.env['mail.message'].sudo().create()`
- Returns HTTP 200 "OK" on success
- Includes placeholder for signature verification (TODO)

### 3. `addons/ipai/ipai_enterprise_bridge/__init__.py`
**Status**: Modified
**Change**: Added `from . import controllers` line

---

## Deployment Steps

### Prerequisites
- SSH access to erp.insightpulseai.com (159.223.75.148)
- Odoo installed at `/opt/odoo-ce` (or known path)
- Database name: `production` (or known database name)

### Step 1: Sync Code to Production

```bash
# SSH to production server
ssh root@159.223.75.148

# Navigate to Odoo directory
cd /opt/odoo-ce

# Pull latest changes (if using Git)
git pull origin main

# OR manually copy files if not using Git
# scp -r addons/ipai/ipai_enterprise_bridge/controllers root@159.223.75.148:/opt/odoo-ce/addons/ipai/ipai_enterprise_bridge/
```

### Step 2: Upgrade Module in Odoo

```bash
# Option A: Docker Compose (if using Docker)
docker compose exec odoo-core odoo \
  -d production \
  -u ipai_enterprise_bridge \
  --stop-after-init

docker compose restart odoo-core

# Option B: Direct Odoo CLI (if not using Docker)
odoo -c /etc/odoo/odoo.conf \
  -d production \
  -u ipai_enterprise_bridge \
  --stop-after-init

systemctl restart odoo
```

### Step 3: Verify Endpoint Exists

```bash
# Test mailgate endpoint (should return HTTP 200, not 404)
curl -X POST https://erp.insightpulseai.com/mailgate/mailgun \
  -d "sender=test@example.com" \
  -d "recipient=test@mg.insightpulseai.com" \
  -d "subject=Deployment Test $(date +%s)" \
  -d "body-plain=Testing mailgate endpoint after deployment." \
  -d "Message-Id=<test-$(date +%s)@example.com>" \
  -w "\nHTTP_CODE: %{http_code}\n"

# Expected output:
# OK
# HTTP_CODE: 200
```

### Step 4: Check Odoo Logs

```bash
# Option A: Docker logs
docker compose logs -f odoo-core | grep "Mailgun inbound"

# Option B: System logs
tail -f /var/log/odoo/odoo-server.log | grep "Mailgun inbound"

# Expected log entry:
# INFO production odoo.addons.ipai_enterprise_bridge.controllers.mailgun_mailgate: Mailgun inbound received: sender=test@example.com recipient=test@mg.insightpulseai.com subject=Deployment Test... message_id=<test-...@example.com>
```

### Step 5: Verify Database Record

```bash
# Connect to PostgreSQL
docker exec odoo-postgres-prod psql -U odoo -d production

# OR
psql -U odoo -d production

# Query for mail.message record
SELECT id, subject, email_from, email_to, create_date
FROM mail_message
WHERE subject ILIKE '%Deployment Test%'
ORDER BY create_date DESC
LIMIT 5;

# Expected: 1 row with the test message
```

---

## End-to-End Mailgun Test

Once the endpoint is deployed and verified, run the full integration test:

### Test 1: Send via Mailgun API

```bash
# Load API key
MAILGUN_API_KEY="key-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxx-xxxxxxxx"
MAILGUN_DOMAIN="mg.insightpulseai.com"
TIMESTAMP=$(date +%s)

# Test deploy@ route
curl -s --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/$MAILGUN_DOMAIN/messages \
  -F from="postmaster@$MAILGUN_DOMAIN" \
  -F to="deploy@insightpulseai.com" \
  -F subject="Mailgun Integration Test: Deploy Route $TIMESTAMP" \
  -F text="Testing Mailgun → Odoo integration for deploy route"

# Test support@ route
curl -s --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/$MAILGUN_DOMAIN/messages \
  -F from="postmaster@$MAILGUN_DOMAIN" \
  -F to="support@insightpulseai.com" \
  -F subject="Mailgun Integration Test: Support Route $TIMESTAMP" \
  -F text="Testing Mailgun → Odoo integration for support route"

# Test invoices@ route
curl -s --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/$MAILGUN_DOMAIN/messages \
  -F from="postmaster@$MAILGUN_DOMAIN" \
  -F to="invoices@insightpulseai.com" \
  -F subject="Mailgun Integration Test: Invoices Route $TIMESTAMP" \
  -F text="Testing Mailgun → Odoo integration for invoices route"

# Test catch-all route
curl -s --user "api:$MAILGUN_API_KEY" \
  https://api.mailgun.net/v3/$MAILGUN_DOMAIN/messages \
  -F from="postmaster@$MAILGUN_DOMAIN" \
  -F to="test-archive@mg.insightpulseai.com" \
  -F subject="Mailgun Integration Test: Catch-all Route $TIMESTAMP" \
  -F text="Testing Mailgun → Odoo integration for catch-all route"
```

### Test 2: Check Mailgun Events (wait 30-60 seconds)

```bash
# Query Mailgun events for delivery status
curl -s --user "api:$MAILGUN_API_KEY" \
  "https://api.mailgun.net/v3/$MAILGUN_DOMAIN/events?limit=20" | \
  jq '.items[] | select(.recipient | contains("insightpulseai.com")) | {
    event,
    recipient,
    timestamp: (.timestamp | tonumber | strftime("%Y-%m-%d %H:%M:%S")),
    "delivery-status": .["delivery-status"],
    url: .["delivery-status"].url
  }'

# Expected for each test message:
# - event: "accepted" (initial acceptance)
# - event: "delivered" (successful forward to mailgate with HTTP 200)
```

### Test 3: Verify All Messages in Odoo Database

```bash
# Connect to database
docker exec odoo-postgres-prod psql -U odoo -d production

# Query for all test messages
SELECT
    id,
    subject,
    email_from,
    email_to,
    message_id,
    create_date
FROM mail_message
WHERE subject ILIKE '%Mailgun Integration Test:%'
ORDER BY create_date DESC
LIMIT 10;

# Expected: 4 rows (one per test route)
# Subjects should match the test messages sent
```

---

## Acceptance Criteria

Integration is considered **OPERATIONAL** when:

✅ Mailgate endpoint returns HTTP 200 (not 404)
✅ Direct curl test creates mail.message record in database
✅ Odoo logs show "Mailgun inbound received" entries
✅ All 4 Mailgun routes successfully deliver to Odoo
✅ Mailgun events show `delivered` status with HTTP 200 for route forwards
✅ Database contains mail.message records for all test emails
✅ No soft bounces or 404 errors in Mailgun event logs

---

## Rollback Strategy

### Quick Rollback (Comment Out Route)

If issues occur, comment out the HTTP route temporarily:

```python
# In addons/ipai/ipai_enterprise_bridge/controllers/mailgun_mailgate.py
# Comment out the @http.route decorator:

# @http.route('/mailgate/mailgun', type='http', auth='public', methods=['POST'], csrf=False)
def mailgun_mailgate(self, **post):
    ...
```

Then restart Odoo:
```bash
docker compose restart odoo-core
# OR
systemctl restart odoo
```

Mailgate will return 404 again (safe state).

### Full Rollback

```bash
# Remove controller files
cd /opt/odoo-ce/addons/ipai/ipai_enterprise_bridge
rm -rf controllers/mailgun_mailgate.py

# Edit controllers/__init__.py and remove import line

# Edit __init__.py and remove controllers import

# Restart Odoo
docker compose restart odoo-core
```

---

## Security Notes

**Current Implementation**:
- Public endpoint (no authentication required)
- CSRF protection disabled (required for webhook POST)
- No signature verification (TODO placeholder exists)
- Logs all inbound mail metadata for debugging

**Future Enhancements**:
- Implement Mailgun signature verification (HMAC-SHA256)
- Add IP allowlist for Mailgun servers
- Implement rate limiting per sender
- Consider adding spam detection

---

## Troubleshooting

### Issue: HTTP 404 Still Occurring

**Symptoms**: curl test returns 404, Mailgun events show 404 status

**Diagnosis**:
```bash
# Check if module was upgraded
docker compose exec odoo-core odoo shell -d production

# In Odoo shell:
>>> env['ir.module.module'].search([('name', '=', 'ipai_enterprise_bridge')]).state
# Should return: 'installed'

# Check controller registration
>>> from odoo.http import _routing_map
>>> [r for r in _routing_map.get('default', []) if '/mailgate' in r]
# Should show: ['/mailgate/mailgun', ...]
```

**Resolution**:
```bash
# Force module upgrade
docker compose exec odoo-core odoo \
  -d production \
  -u ipai_enterprise_bridge \
  --stop-after-init \
  --log-level=debug

# Restart Odoo
docker compose restart odoo-core
```

### Issue: Mail.message Not Created

**Symptoms**: HTTP 200 received but no database record

**Diagnosis**:
```bash
# Check Odoo logs for errors
docker compose logs odoo-core | grep -A 10 "Mailgun mailgate error"

# Common causes:
# - Missing 'mail' module dependency
# - Database permissions issue
# - Invalid field values
```

**Resolution**:
```bash
# Verify 'mail' module is installed
docker compose exec odoo-core odoo shell -d production

>>> env['ir.module.module'].search([('name', '=', 'mail')]).state
# Should return: 'installed'

# Check database permissions
>>> env['mail.message'].check_access_rights('create')
# Should not raise exception
```

### Issue: Mailgun Signature Verification

**Note**: Signature verification is currently a TODO. To implement:

1. Get signing key from Mailgun dashboard
2. Add to environment:
   ```bash
   export MAILGUN_SIGNING_KEY="your-signing-key"
   ```
3. Uncomment signature verification code in controller
4. Test with valid Mailgun webhooks (not curl)

---

## References

- **Mailgun Events API**: https://api.mailgun.net/v3/mg.insightpulseai.com/events
- **Odoo Mail Documentation**: https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html#mail
- **Mailgun Webhook Format**: https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/#tracking-webhooks
- **Diagnosis Report**: `./config/mailgun_odoo_diagnosis.json`
- **Route Validation**: `./config/mailgun_route_validation.json`

---

**Deployment Status**: Code ready, awaiting production deployment and verification
