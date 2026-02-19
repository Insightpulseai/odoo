# n8n Odoo Integration Reference

**Purpose**: Reference guide for n8n-Odoo integration configuration
**Status**: REFERENCE (not a completion claim)
**Timezone**: Asia/Manila (UTC+08:00)

---

## Overview

n8n provides official Odoo integration via OAuth2 authentication for REST API access. This integration enables workflow automation between n8n and Odoo instances.

**Prerequisites (Verified)**:
- ✅ n8n container running and healthy
- ✅ Database migrations completed
- ⏳ Admin account created (manual step - see IMPLEMENTATION_SUMMARY.md)

---

## Integration Architecture

**Authentication Method**: OAuth2 (recommended) or API Key
**Supported Operations**:
- Database queries (search, create, update, delete)
- RPC calls (execute model methods)
- Webhook triggers (real-time events)

**Network Flow**:
```
n8n (ipai-n8n) ←→ Odoo REST API (erp.insightpulseai.com)
       ↓
  Supabase PostgreSQL (credential storage)
```

---

## [MANUAL_REQUIRED]

### Odoo Credential Creation
**What**: Configure Odoo OAuth2 application and add credentials to n8n
**Why**: n8n requires UI-only credential setup (no API endpoint for credential creation)
**Evidence**: Official docs at https://n8n.io/integrations/odoo/

**Minimal human action**:
1. In Odoo instance (https://erp.insightpulseai.com):
   - Navigate to Settings → Users & Companies → OAuth Providers
   - Create new OAuth Provider with redirect URI from n8n
   - Copy Client ID and Client Secret

2. In n8n UI (https://n8n.insightpulseai.com):
   - Click "Credentials" in sidebar
   - Add new credential → Search "Odoo"
   - Select "OAuth2 API"
   - Enter Odoo URL, Client ID, Client Secret
   - Complete OAuth flow

**Then**: Credentials available for workflow nodes

---

## Available Odoo Nodes

### 1. Odoo Trigger Node
**Purpose**: Listen for Odoo events (webhooks)
**Use Cases**:
- New sale order created
- Contact updated
- Invoice status changed

### 2. Odoo Action Node
**Purpose**: Execute operations on Odoo database
**Operations**:
- **Create**: Insert new records
- **Delete**: Remove records
- **Get**: Retrieve single record
- **Get Many**: Retrieve multiple records
- **Update**: Modify existing records
- **Execute**: Run custom model methods

---

## Common Integration Patterns

### Pattern 1: Sync Contacts
**Trigger**: New contact in external system
**Action**: Create contact in Odoo via n8n
**Benefits**: Bidirectional sync, deduplication logic

### Pattern 2: Automated Invoicing
**Trigger**: Sale order reaches specific stage
**Action**: Generate and email invoice
**Benefits**: Reduce manual invoice creation

### Pattern 3: Inventory Alerts
**Trigger**: Product stock below threshold
**Action**: Send alert to procurement team
**Benefits**: Prevent stockouts

---

## Security Considerations

**Credential Storage**: n8n encrypts credentials in PostgreSQL (N8N_ENCRYPTION_KEY)
**API Access**: Odoo user permissions apply to API calls
**Network Security**: HTTPS required for OAuth callback URLs

**Best Practice**: Use dedicated "n8n Integration" user in Odoo with minimal permissions

---

## Troubleshooting

### Issue: OAuth Callback Fails
**Symptom**: "Redirect URI mismatch" error during OAuth flow
**Check**:
```bash
# Verify n8n webhook URL is correct
curl -I https://n8n.insightpulseai.com/rest/oauth2-credential/callback
# Expected: HTTP/2 200
```
**Solution**: Ensure Odoo OAuth provider redirect URI matches exactly

### Issue: API Calls Return 401
**Symptom**: "Unauthorized" errors in workflow execution
**Check**: Token expiration (OAuth tokens expire after configured lifetime)
**Solution**: Re-authenticate credential in n8n UI

### Issue: Workflow Timeout
**Symptom**: Long-running Odoo queries fail
**Check**: Workflow execution timeout settings
**Solution**: Increase timeout or optimize Odoo query (use filters, pagination)

---

## Related Documentation

- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md` (current status and manual steps)
- **Admin Setup**: `ADMIN_SETUP_REFERENCE.md` (first-time account creation)
- **AI Integration**: `AI_INTEGRATION_REFERENCE.md` (local AI capabilities)
- **Official n8n Docs**: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.odoo/
- **Odoo External API**: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html

---

**Note**: This is a reference document, not a claim of completion. See `IMPLEMENTATION_SUMMARY.md` for current implementation status and remaining manual steps.
