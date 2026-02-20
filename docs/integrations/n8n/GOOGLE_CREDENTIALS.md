# n8n Google Credentials Integration — Policy & Implementation

**Last Updated:** 2026-02-20
**Status:** PRODUCTION-READY
**n8n Documentation:** [Google OAuth2 Credentials](https://docs.n8n.io/integrations/builtin/credentials/google/oauth-generic/)

---

## Overview

This document defines operational policies and automation-first setup for n8n's Google credential types. It establishes **Supabase as SSOT** for integration state/audit while treating n8n credentials as operational config (not SSOT).

---

## Credential Type Matrix

n8n supports two primary Google authentication modes with distinct operational/security footprints:

| **Mode** | **Use Case** | **User Interaction** | **Token Scope** | **Rotation** |
|----------|-------------|---------------------|----------------|-------------|
| **OAuth2 Single Service** | Interactive user delegation (Drive, Gmail, Calendar) | Yes (browser OAuth flow) | User-scoped, delegated | Automatic (refresh tokens) |
| **Service Account** | Server-to-server (Drive APIs, BigQuery, Admin SDK) | No (key-based auth) | Service-scoped, static | Manual (key rotation) |

### Decision Matrix

| **Scenario** | **Recommended Mode** | **Justification** |
|-------------|---------------------|-------------------|
| User accesses their own Drive files | OAuth2 Single Service | User delegation, audit trail per user |
| Background sync of shared Drive | Service Account | No user interaction, consistent identity |
| Send email on behalf of user | OAuth2 Single Service | Gmail requires user context |
| Query BigQuery datasets | Service Account | Server-to-server, no user delegation |
| Admin SDK (user management) | Service Account | Administrative operations |

---

## SSOT/SOR Boundary Policy

### n8n Credentials as Operational Config

**Classification:** **Operational Configuration** (not SSOT, not SOR)

**Rationale:**
- n8n credentials are **execution context**, not authoritative data
- SSOT for integration **state** lives in Supabase (`ops.integration_state`, `ops.run_events`)
- SOR for **ERP transactions** lives in Odoo (if integration writes to accounting/ledger)

### Boundary Rules

| **Aspect** | **n8n Role** | **Supabase SSOT Role** | **Odoo SOR Role** |
|-----------|-------------|----------------------|------------------|
| Credential storage | ✅ Stores encrypted tokens | ❌ Never stores raw tokens | ❌ N/A |
| Integration state | ❌ Transient execution only | ✅ Canonical state (cursors, checkpoints) | ❌ N/A |
| Audit trail | ❌ Basic execution logs | ✅ Structured audit (`ops.run_events`) | ❌ N/A |
| ERP postings | ❌ N/A | ❌ Never authoritative | ✅ Canonical ledger |

**Policy Enforcement:**
- n8n credentials MUST NOT be version-controlled (git)
- Credential references MUST be stored in Supabase Vault or n8n secret store
- All n8n → Odoo write paths MUST be audited in `ops.run_events`
- n8n MUST NOT create "shadow ledger" entries in Supabase (read SOR → write SSOT only)

---

## OAuth2 Single Service Setup (Automation-First)

### Prerequisites

1. **Google Cloud Project** with APIs enabled (Drive, Gmail, Calendar, etc.)
2. **OAuth 2.0 Client ID** (type: Web application)
3. **Authorized redirect URIs**: `https://<n8n-instance>/rest/oauth2-credential/callback`

### Setup Checklist

**Automated Steps:**
```bash
# 1. Store credentials in Supabase Vault (server-side)
# (No CLI - use Edge Function or manual UI one-time setup)

# 2. Configure n8n OAuth2 credential via API (automation-friendly)
curl -X POST https://n8n.insightpulseai.com/api/v1/credentials \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Google OAuth2 - Drive Access",
    "type": "googleOAuth2",
    "data": {
      "clientId": "${GOOGLE_CLIENT_ID}",
      "clientSecret": "${GOOGLE_CLIENT_SECRET}",
      "scope": "https://www.googleapis.com/auth/drive.readonly"
    }
  }'

# 3. Trigger OAuth flow programmatically (requires user interaction once)
# (n8n UI: click "Connect" button → browser OAuth → callback)

# 4. Verify token refresh automation (n8n handles this automatically)
```

**Manual Steps (One-Time Only):**
- [ ] User clicks "Connect" in n8n credential UI → OAuth browser flow
- [ ] Google consent screen → grant permissions → redirect to n8n
- [ ] n8n stores refresh token (encrypted)

**Verification:**
```bash
# Test credential via n8n API
curl -X POST https://n8n.insightpulseai.com/api/v1/workflows/test \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "nodes": [
        {
          "type": "n8n-nodes-base.googleDrive",
          "credentials": {
            "googleDriveOAuth2Api": "Google OAuth2 - Drive Access"
          }
        }
      ]
    }
  }'
```

---

## Service Account Setup (Fully Automated)

### Prerequisites

1. **Google Cloud Project** with APIs enabled (Drive, BigQuery, Admin SDK, etc.)
2. **Service Account** created with appropriate IAM roles
3. **Service Account Key** (JSON file) downloaded

### Setup Checklist

**Automated Steps:**
```bash
# 1. Store service account key in Supabase Vault
# File: service-account-key.json
# Vault path: google/service_account_key

# 2. Configure n8n Service Account credential via API
curl -X POST https://n8n.insightpulseai.com/api/v1/credentials \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "name": "Google Service Account - Drive Sync",
  "type": "googleServiceAccount",
  "data": {
    "email": "service-account@project-id.iam.gserviceaccount.com",
    "privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
  }
}
EOF

# 3. Test credential immediately (no user interaction needed)
curl -X POST https://n8n.insightpulseai.com/api/v1/workflows/test \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {
      "nodes": [
        {
          "type": "n8n-nodes-base.googleDrive",
          "credentials": {
            "googleDriveServiceAccount": "Google Service Account - Drive Sync"
          }
        }
      ]
    }
  }'
```

**No Manual Steps Required** (fully automated)

---

## Scope Minimization & Least Privilege

### OAuth2 Scope Best Practices

**Principle:** Request only the minimum required scope for the task.

| **Task** | **Scope** | **Justification** |
|---------|----------|-------------------|
| Read-only Drive access | `https://www.googleapis.com/auth/drive.readonly` | Prevents accidental file deletion |
| Create/modify Drive files | `https://www.googleapis.com/auth/drive.file` | Limited to app-created files only |
| Full Drive access | `https://www.googleapis.com/auth/drive` | ❌ Avoid unless absolutely necessary |
| Send email (Gmail) | `https://www.googleapis.com/auth/gmail.send` | Sending only, no inbox read |
| Read Calendar | `https://www.googleapis.com/auth/calendar.readonly` | Read events, no modifications |

**Enforcement:**
- CI lint MUST flag any workflow using `drive` (full scope) without justification
- Credentials MUST be reviewed quarterly for scope creep

### Service Account Role Best Practices

| **Task** | **IAM Role** | **Justification** |
|---------|-------------|-------------------|
| Read Shared Drive files | `Viewer` | Read-only access |
| Write to specific Drive folder | Custom role with `drive.files.create` only | Least privilege |
| Query BigQuery datasets | `BigQuery Data Viewer` | Read-only queries |
| Admin SDK (user management) | `User Administrator` | User provisioning only |

---

## Credential Rotation & Revocation

### OAuth2 Token Refresh (Automatic)

**n8n Behavior:**
- Access tokens expire every 1 hour (Google default)
- n8n automatically refreshes using stored refresh token
- No manual intervention required

**Monitoring:**
```sql
-- Supabase audit: track OAuth refresh failures
SELECT * FROM ops.run_events
WHERE event_type = 'oauth_refresh_failed'
  AND event_data->>'provider' = 'google'
ORDER BY created_at DESC
LIMIT 10;
```

**Remediation (if refresh fails):**
1. User re-authenticates via n8n UI (OAuth flow)
2. New refresh token issued and stored

### Service Account Key Rotation (Manual)

**Cadence:** Every 90 days (recommended), every 180 days (minimum)

**Automation Workflow:**
```bash
#!/bin/bash
# scripts/rotate_google_service_account.sh

# 1. Generate new service account key
gcloud iam service-accounts keys create new-key.json \
  --iam-account=service-account@project-id.iam.gserviceaccount.com

# 2. Update Supabase Vault
# (No CLI - use Edge Function or manual UI)

# 3. Update n8n credential via API
NEW_KEY=$(cat new-key.json | jq -r '.private_key')
curl -X PATCH https://n8n.insightpulseai.com/api/v1/credentials/{credential_id} \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"data\": {\"privateKey\": \"${NEW_KEY}\"}}"

# 4. Verify new key works
# (Run test workflow)

# 5. Delete old key
gcloud iam service-accounts keys delete OLD_KEY_ID \
  --iam-account=service-account@project-id.iam.gserviceaccount.com
```

**Tracking:**
```sql
-- Store rotation events in Supabase
INSERT INTO ops.credential_rotations (
  credential_type, provider, rotated_at, rotated_by
) VALUES (
  'service_account', 'google', now(), 'automation'
);
```

---

## Integration State Audit Trail (Supabase SSOT)

### Required Audit Fields

**Every n8n → Google API call MUST emit:**
```sql
INSERT INTO ops.run_events (
  run_id, event_type, event_data, created_at
) VALUES (
  <run_id>,
  'google_api_call',
  jsonb_build_object(
    'credential_type', 'oauth2',  -- or 'service_account'
    'service', 'drive',  -- drive, gmail, calendar, etc.
    'operation', 'files.list',
    'request_id', <correlation_id>,
    'response_status', 200,
    'quota_consumed', 1  -- API quota units
  ),
  now()
);
```

**Tracking Integration State:**
```sql
-- Example: Track Drive sync cursor
CREATE TABLE IF NOT EXISTS ops.integration_state (
  id uuid primary key default gen_random_uuid(),
  integration_name text not null,  -- e.g., 'google-drive-sync'
  state_key text not null,  -- e.g., 'last_sync_token'
  state_value jsonb not null,  -- e.g., {"token": "abc123", "timestamp": "2026-02-20T12:00:00Z"}
  updated_at timestamptz not null default now(),
  unique(integration_name, state_key)
);

-- Update sync cursor after each run
INSERT INTO ops.integration_state (integration_name, state_key, state_value)
VALUES ('google-drive-sync', 'last_sync_token', '{"token": "xyz789"}')
ON CONFLICT (integration_name, state_key)
DO UPDATE SET state_value = EXCLUDED.state_value, updated_at = now();
```

---

## Security Checklist

**OAuth2 Credentials:**
- [ ] Client ID and secret stored in Supabase Vault (not git)
- [ ] Authorized redirect URIs limited to `https://<n8n-instance>/rest/oauth2-credential/callback`
- [ ] Scopes minimized (no `drive` full scope unless justified)
- [ ] Refresh token rotation monitored (alert if failing)
- [ ] User consent screen configured with branding

**Service Account Credentials:**
- [ ] Service account key stored in Supabase Vault (not git)
- [ ] IAM roles follow least privilege (no `roles/owner` or `roles/editor`)
- [ ] Key rotation schedule defined (90 days)
- [ ] Service account email documented (for audit trail)
- [ ] Shared Drive access granted explicitly (no org-wide permissions)

**n8n Workflow Security:**
- [ ] Credentials never logged in plaintext (n8n env var redaction enabled)
- [ ] Workflow JSON never contains raw tokens (uses credential references)
- [ ] CI lint checks for hardcoded credentials (`client_secret`, `private_key`)
- [ ] All Google API calls logged to `ops.run_events`

---

## Troubleshooting

### Common Issues

**Issue:** OAuth refresh fails after 7 days
- **Cause:** User revoked access in Google Account settings
- **Fix:** Re-authenticate via n8n UI (OAuth flow)

**Issue:** Service account "Access denied" error
- **Cause:** Shared Drive not shared with service account email
- **Fix:** Add service account as Viewer/Editor to Shared Drive

**Issue:** n8n workflow times out calling Google API
- **Cause:** Rate limit exceeded (Google quota)
- **Fix:** Implement exponential backoff, reduce request frequency

**Issue:** Credential not found in n8n workflow
- **Cause:** Credential deleted or renamed
- **Fix:** Re-create credential, update workflow JSON

---

## Cross-References

- **n8n Documentation:** [Google OAuth2 Credentials](https://docs.n8n.io/integrations/builtin/credentials/google/oauth-generic/)
- **SSOT Policy:** `spec/odoo-ee-parity-seed/constitution.md` (Article: Supabase SSOT)
- **n8n ↔ Odoo Bridge:** `spec/odoo-sh/prd.md` (FR6: n8n Workflow Automation Layer)
- **Secret Handling:** `sandbox/dev/CLAUDE.md` (Supabase Vault + macOS Keychain)
- **Audit Trail:** `docs/architecture/AUTOMATION_AUDIT_TRAIL.md` (to be created)
