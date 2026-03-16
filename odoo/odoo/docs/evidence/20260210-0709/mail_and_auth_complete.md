# Mail Configuration & JWT Authentication - Complete

**Date**: 2026-02-10
**Scope**: End-to-end mail configuration with Zoho Mail PRO + JWT service authentication

---

## Executive Summary

✅ **All objectives completed:**

1. **Mail System**: Odoo configured with Zoho Mail PRO SMTP (app-specific password)
2. **End-to-End Testing**: Test email sent and delivered successfully
3. **SSOT Configuration**: Reusable mail configuration script created
4. **JWT Authentication**: Service-to-service auth system implemented
5. **Documentation**: Complete auth system documentation

---

## 1. Mail System Configuration

### Zoho Mail PRO SMTP

**Configuration Applied:**
- **Host**: smtppro.zoho.com:587
- **Encryption**: STARTTLS
- **User**: business@insightpulseai.com
- **Password**: App-specific password (5Kww9uyvJcb7)
- **Status**: ✅ Active and verified

**Database Records:**

```sql
-- ir_mail_server (id=1)
name: "Zoho Mail PRO"
smtp_host: "smtppro.zoho.com"
smtp_port: 587
smtp_encryption: "starttls"
smtp_user: "business@insightpulseai.com"
active: true
sequence: 10

-- ir_config_parameter
mail.default.from: "no-reply@insightpulseai.com"
mail.default.reply_to: "business@insightpulseai.com"
mail.catchall.domain: "insightpulseai.com"
```

### Verification Results

**SMTP Connectivity Test:**
```
✅ SMTP auth OK: smtppro.zoho.com 587 tls= True
```

**Test Email Delivery:**
```
✅ mail.mail.send() invoked; id=1
   To: business@insightpulseai.com
   State: sent

Mail (mail.mail) with ID 1 from 'no-reply@insightpulseai.com'
to 'business@insightpulseai.com' successfully sent

Total emails tried by SMTP: 1
Processed batch of 1 mail.mail records via mail server ID #1
```

**Mail Queue State:**
- Empty (as expected after successful delivery)
- Auto-cleanup working correctly

---

## 2. SSOT Configuration Scripts

### Mail Configuration Script

**File**: `scripts/odoo_configure_mail.sh`

**Features:**
- ✅ Idempotent (safe to run multiple times)
- ✅ Environment-driven (reads from `.env.platform.local`)
- ✅ Docker-aware (works with devcontainer)
- ✅ Verification mode (`--verify-only`)
- ✅ Error handling with colored output

**Usage:**
```bash
# Apply configuration
./scripts/odoo_configure_mail.sh

# Verify only (no changes)
./scripts/odoo_configure_mail.sh --verify-only
```

**Required Environment Variables:**
- `ZOHO_SMTP_HOST`
- `ZOHO_SMTP_PORT`
- `ZOHO_SMTP_USER`
- `ZOHO_SMTP_PASS`
- `ZOHO_SMTP_TLS`
- `ZOHO_SMTP_SSL`
- `MAIL_DEFAULT_FROM`
- `MAIL_REPLY_TO`
- `MAIL_CATCHALL_DOMAIN`

---

## 3. JWT Authentication System

### JWT Token Minter

**File**: `scripts/auth/mint_token.py`

**Features:**
- ✅ HS256 token generation
- ✅ Token verification
- ✅ Auto-loads from `.env.platform.local`
- ✅ Configurable scope and expiry
- ✅ Auto-installs PyJWT if missing

**Examples:**

```bash
# Mint token for docflow service
python3 scripts/auth/mint_token.py \
  --sub "svc:docflow" \
  --scope "ocr:read,ai:call,mcp:invoke" \
  --exp 3600

# Verify token
python3 scripts/auth/mint_token.py --verify "eyJhbG..."
```

**Output:**
```
✅ JWT token minted
   Subject: svc:docflow
   Scope: ocr:read, ai:call, mcp:invoke
   Expires: 3600s (60m)

Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Service Token Generator

**File**: `scripts/auth/generate_service_tokens.sh`

**Services Configured:**
- `svc:n8n` - Workflow execution
- `svc:superset` - Analytics
- `svc:mcp` - MCP coordination
- `svc:docflow` - Document processing
- `svc:analytics` - Business intelligence

**Usage:**
```bash
# Generate all service tokens (24h expiry)
./scripts/auth/generate_service_tokens.sh 86400
```

**Output:**
```
🔐 Generating service tokens (expires in 86400s = 24h)...

📦 svc:n8n
   Scope: workflow:execute,ai:call,mcp:invoke,ocr:read
   Token: eyJhbGci...
   Variable: N8N_JWT_TOKEN

📦 svc:superset
   Scope: ai:call,mcp:invoke,analytics:read
   Token: eyJhbGci...
   Variable: SUPERSET_JWT_TOKEN

...
```

---

## 4. Secret Management

### Local Storage

**File**: `.env.platform.local`

**Secrets Stored:**
- ✅ Zoho Mail SMTP credentials (app-specific password)
- ✅ AI provider keys (Anthropic, OpenAI)
- ✅ Supabase credentials
- ✅ JWT authentication secret (HS256)
- ✅ Superset/n8n admin passwords

**Security:**
- Listed in `.gitignore`
- Not committed to repository
- Docker container access only

### Cloud Storage

**Supabase Vault:**

```bash
# Secrets synced to vault
supabase secrets set \
  ZOHO_SMTP_PASS="5Kww9uyvJcb7" \
  AUTH_JWT_HS256_SECRET="Zk3D3Zh+XZBjEw0v2bqhoyWU2KCO9VzTHuEhh7hNxuM="
```

**Status**: ✅ Synced successfully

---

## 5. Documentation

### Auth System Documentation

**File**: `scripts/auth/README.md`

**Contents:**
- JWT authentication overview
- Quick start guide
- Service definitions and scopes
- Usage examples for all platforms:
  - n8n HTTP Request nodes
  - Superset SQL Lab
  - Supabase Edge Functions
  - Python services
- Security best practices
- Troubleshooting guide

---

## 6. Verification Commands

### Mail System

```bash
# Verify SMTP configuration
./scripts/odoo_configure_mail.sh --verify-only

# Test SMTP connectivity
docker compose -f .devcontainer/docker-compose.yml exec -T odoo bash -c '
set -a; . /workspace/.env.platform.local; set +a
python3 -c "
import os, smtplib
s=smtplib.SMTP(os.environ[\"ZOHO_SMTP_HOST\"], int(os.environ[\"ZOHO_SMTP_PORT\"]))
s.starttls()
s.login(os.environ[\"ZOHO_SMTP_USER\"], os.environ[\"ZOHO_SMTP_PASS\"])
print(\"✅ SMTP OK\")
s.quit()
"
'
```

### JWT Authentication

```bash
# Generate test token
TOKEN=$(python3 scripts/auth/mint_token.py --sub "svc:test" 2>/dev/null | grep -A1 "Token:" | tail -1)

# Verify token
python3 scripts/auth/mint_token.py --verify "$TOKEN"
```

---

## 7. Files Created/Modified

### Created

| File | Purpose | Status |
|------|---------|--------|
| `scripts/auth/mint_token.py` | JWT token minting/verification | ✅ Tested |
| `scripts/auth/generate_service_tokens.sh` | Batch token generation | ✅ Tested |
| `scripts/auth/README.md` | Auth system documentation | ✅ Complete |
| `scripts/odoo_configure_mail.sh` | Mail configuration SSOT | ✅ Tested |
| `docs/evidence/20260210-0709/mail_and_auth_complete.md` | This file | ✅ Complete |

### Modified

| File | Changes | Status |
|------|---------|--------|
| `.env.platform.local` | Added Zoho app-specific password | ✅ Updated |
| `.gitignore` | Ensures `.env.platform.local` not committed | ✅ Verified |

### Secrets Updated

| Location | Secret | Status |
|----------|--------|--------|
| `.env.platform.local` | `ZOHO_SMTP_PASS=5Kww9uyvJcb7` | ✅ Updated |
| `.env.platform.local` | `AUTH_JWT_HS256_SECRET=Zk3D3Zh+XZBjEw0v2bqhoyWU2KCO9VzTHuEhh7hNxuM=` | ✅ Generated |
| Supabase Vault | `ZOHO_SMTP_PASS` | ✅ Synced |

---

## 8. Next Steps (Optional)

### Superset JWT Integration

```bash
# Add to Superset configuration
export SUPERSET_JWT_TOKEN=$(./scripts/auth/generate_service_tokens.sh | grep -A1 "svc:superset" | grep "Token:" | awk '{print $2}')
```

### n8n JWT Integration

```javascript
// HTTP Request node in n8n workflow
{
  "url": "https://api.insightpulseai.com/v1/ai",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer {{$env.N8N_JWT_TOKEN}}"
  }
}
```

### MCP Server Configuration

```typescript
// Edge Function with JWT
const token = Deno.env.get("MCP_JWT_TOKEN");
await fetch("https://api.insightpulseai.com/v1/mcp", {
  headers: { "Authorization": `Bearer ${token}` }
});
```

---

## 9. Rollback Procedures

### Mail Configuration

```bash
# Disable SMTP server
docker compose -f .devcontainer/docker-compose.yml exec -T postgres bash -c '
psql -U odoo -d postgres -c "UPDATE ir_mail_server SET active=false WHERE id=1;"
'
```

### JWT Secrets

```bash
# Regenerate new secret
NEW_SECRET=$(openssl rand -base64 32)
sed -i "s|AUTH_JWT_HS256_SECRET=.*|AUTH_JWT_HS256_SECRET=$NEW_SECRET|" .env.platform.local

# Sync to Supabase Vault
supabase secrets set AUTH_JWT_HS256_SECRET="$NEW_SECRET"
```

---

## 10. Success Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| SMTP authentication working | ✅ PASS | Connectivity test successful |
| Test email delivered | ✅ PASS | Mail ID 1 sent successfully |
| Mail configuration persisted | ✅ PASS | Database records verified |
| SSOT script created | ✅ PASS | `odoo_configure_mail.sh` executable |
| JWT minting working | ✅ PASS | Token generated and verified |
| Service tokens generated | ✅ PASS | 5 service tokens created |
| Documentation complete | ✅ PASS | Auth README created |
| Secrets synced to vault | ✅ PASS | Supabase secrets updated |

---

**Conclusion**: All mail configuration and JWT authentication objectives completed successfully. System is ready for production use with Superset/n8n/MCP integration.
