# InsightPulse AI Authentication System

JWT-based service-to-service authentication for the InsightPulse AI platform.

## Overview

All platform services (n8n, Superset, MCP, OCR, AI brokers) use JWT bearer tokens for authentication:

- **Algorithm**: HS256 (HMAC-SHA256)
- **Issuer**: `https://auth.insightpulseai.com`
- **Audience**: `ipai-platform`
- **Secret**: `AUTH_JWT_HS256_SECRET` (stored in `.env.platform.local` and Supabase Vault)

## Quick Start

### 1. Mint a Service Token

```bash
# Default token (1 hour expiry)
python3 scripts/auth/mint_token.py --sub "svc:docflow"

# Custom scope and expiry (24 hours)
python3 scripts/auth/mint_token.py \
  --sub "svc:analytics" \
  --scope "ai:call,analytics:read,analytics:write" \
  --exp 86400
```

### 2. Verify an Existing Token

```bash
python3 scripts/auth/mint_token.py --verify "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Generate All Service Tokens

```bash
# Generate tokens for all platform services
./scripts/auth/generate_service_tokens.sh

# Custom expiry (24 hours)
./scripts/auth/generate_service_tokens.sh 86400
```

## Service Definitions

| Service | Subject | Default Scope |
|---------|---------|---------------|
| n8n | `svc:n8n` | `workflow:execute,ai:call,mcp:invoke,ocr:read` |
| Superset | `svc:superset` | `ai:call,mcp:invoke,analytics:read` |
| MCP | `svc:mcp` | `ai:call,ocr:read,workflow:trigger` |
| Docflow | `svc:docflow` | `ocr:read,ai:call,mcp:invoke,document:process` |
| Analytics | `svc:analytics` | `ai:call,analytics:read,analytics:write` |

## Available Scopes

| Scope | Description |
|-------|-------------|
| `ocr:read` | Read OCR results |
| `ocr:write` | Submit OCR jobs |
| `ai:call` | Call AI providers (Anthropic, OpenAI) |
| `mcp:invoke` | Invoke MCP server functions |
| `workflow:execute` | Execute n8n workflows |
| `workflow:trigger` | Trigger workflow execution |
| `analytics:read` | Read analytics data |
| `analytics:write` | Write analytics data |
| `document:process` | Process documents |

## Usage in Services

### n8n HTTP Request Node

```javascript
// HTTP Request node headers
{
  "Authorization": "Bearer {{$env.N8N_JWT_TOKEN}}"
}
```

### Superset SQL Lab

```python
# Custom SQL query with authentication
import requests

headers = {
    "Authorization": f"Bearer {os.environ['SUPERSET_JWT_TOKEN']}"
}
response = requests.get(
    "https://api.insightpulseai.com/v1/analytics",
    headers=headers
)
```

### Supabase Edge Function

```typescript
// Edge Function authentication
const token = Deno.env.get("MCP_JWT_TOKEN");
const response = await fetch("https://api.insightpulseai.com/v1/mcp", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
});
```

### Python Service

```python
import os
import requests

token = os.environ["DOCFLOW_JWT_TOKEN"]
headers = {"Authorization": f"Bearer {token}"}

# Call OCR service
response = requests.post(
    "https://api.insightpulseai.com/v1/ocr",
    headers=headers,
    files={"file": open("invoice.pdf", "rb")}
)
```

## Security Best Practices

1. **Token Storage**:
   - Store tokens in environment variables, never hardcode
   - Use Supabase Vault for cloud deployments
   - Use `.env.platform.local` for local development

2. **Token Rotation**:
   - Regenerate tokens regularly (recommended: weekly)
   - Use short expiry times for production (1-24 hours)
   - Implement automatic refresh for long-running services

3. **Scope Principle of Least Privilege**:
   - Grant only required scopes per service
   - Audit scope usage regularly
   - Remove unused scopes

4. **Secret Management**:
   - Never commit `AUTH_JWT_HS256_SECRET` to git
   - Rotate secret if compromised
   - Use different secrets per environment (dev/staging/prod)

## Troubleshooting

### Token Invalid

```bash
# Verify token expiry
python3 scripts/auth/mint_token.py --verify "$TOKEN"

# Check secret matches
echo "$AUTH_JWT_HS256_SECRET"
```

### Permission Denied

```bash
# Check token scope
python3 scripts/auth/mint_token.py --verify "$TOKEN" | grep Scope

# Regenerate with correct scope
python3 scripts/auth/mint_token.py --sub "svc:n8n" --scope "ai:call,mcp:invoke"
```

### Token Expired

```bash
# Generate new token with longer expiry
python3 scripts/auth/mint_token.py --sub "svc:analytics" --exp 86400
```

## Files

| File | Purpose |
|------|---------|
| `mint_token.py` | JWT token minting and verification |
| `generate_service_tokens.sh` | Batch token generation for all services |
| `README.md` | This documentation |

## Related Configuration

- `.env.platform.local` - Local environment secrets
- `scripts/odoo_configure_mail.sh` - Odoo mail configuration (uses same auth system)
- Supabase Vault - Cloud secret storage

## References

- [JWT.io](https://jwt.io/) - JWT debugger
- [PyJWT Documentation](https://pyjwt.readthedocs.io/) - Python JWT library
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JWT specification
