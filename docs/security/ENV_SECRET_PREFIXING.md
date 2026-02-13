# Environment Secret Prefixing (Single Supabase Project)

## Overview

This document defines the **mandatory** secret naming and isolation strategy for running staging and production environments on a single Supabase project.

**Problem**: Single Supabase project = shared secret store = risk of accidentally using prod secrets in stage (or vice versa).

**Solution**: Strict prefix-based namespacing + runtime enforcement.

---

## Rules (Non-Negotiable)

### 1. Secret Naming

| Environment | Prefix | Example |
|-------------|--------|---------|
| **Staging** | `STAGE__` | `STAGE__OPENAI_API_KEY` |
| **Production** | `PROD__` | `PROD__OPENAI_API_KEY` |

**Rules**:
- ✅ **MUST** use prefix for all environment-specific secrets
- ❌ **NEVER** use bare names like `OPENAI_API_KEY` (ambiguous)
- ✅ **MUST** use different API keys/credentials per environment
- ❌ **NEVER** reuse the same credential across stage/prod

### 2. Runtime Enforcement

**All Edge Functions MUST**:
1. Import `supabase/functions/_shared/env.ts`
2. Use `getEnvSecret(key)` instead of `Deno.env.get()`
3. Require `ENVIRONMENT` variable at startup

**The runtime will throw** if `ENVIRONMENT` is not set or invalid.

### 3. Sync Process

**Use `scripts/secrets/sync_env.sh` with**:
- `ENVIRONMENT=staging|prod` (required)
- `SUPABASE_PROJECT_REF=<project-ref>` (required)
- Exported env vars matching the prefix

**Examples**:

```bash
# Staging sync
export ENVIRONMENT=staging
export SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
export STAGE__OPENAI_API_KEY="sk-staging-..."
export STAGE__ZOHO_SMTP_PASS="staging-password"
./scripts/secrets/sync_env.sh

# Production sync
export ENVIRONMENT=prod
export SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
export PROD__OPENAI_API_KEY="sk-prod-..."
export PROD__ZOHO_SMTP_PASS="prod-password"
./scripts/secrets/sync_env.sh
```

---

## Usage Patterns

### Edge Function Example

```typescript
// ✅ CORRECT: Use env resolver
import { getEnvSecret, getEnvironment } from "../_shared/env.ts";

const openaiKey = getEnvSecret("OPENAI_API_KEY");
// Automatically resolves to:
//   - STAGE__OPENAI_API_KEY (if ENVIRONMENT=staging)
//   - PROD__OPENAI_API_KEY (if ENVIRONMENT=prod)

const env = getEnvironment(); // "staging" or "prod"
```

```typescript
// ❌ WRONG: Direct env access (no protection)
const openaiKey = Deno.env.get("OPENAI_API_KEY"); // Ambiguous!
```

### Odoo Integration Example

```python
# In Odoo post_init_hook or runtime
import os

environment = os.environ.get("ENVIRONMENT", "").lower()
if environment == "staging":
    smtp_password = os.environ["STAGE__ZOHO_SMTP_PASS"]
elif environment == "prod":
    smtp_password = os.environ["PROD__ZOHO_SMTP_PASS"]
else:
    raise ValueError(f"Invalid ENVIRONMENT: {environment}")
```

---

## Registry Integration

**Location**: `infra/secrets/registry.yaml`

**Example Entry**:

```yaml
secrets:
  - name: STAGE__OPENAI_API_KEY
    description: OpenAI API key for staging environment.
    tier: runtime
    store: supabase_edge
    env_var: STAGE__OPENAI_API_KEY
    required: true
    rotation_days: 90
    scope: "environment:staging"
    used_by:
      - supabase/functions/* (env resolver)

  - name: PROD__OPENAI_API_KEY
    description: OpenAI API key for production environment.
    tier: runtime
    store: supabase_edge
    env_var: PROD__OPENAI_API_KEY
    required: true
    rotation_days: 90
    scope: "environment:prod"
    used_by:
      - supabase/functions/* (env resolver)
```

---

## Security Guarantees

### What This Prevents

✅ **Accidental secret mixing**: Can't use prod API key in staging by mistake
✅ **Runtime validation**: Functions refuse to start without ENVIRONMENT
✅ **Clear audit trail**: Prefix makes it obvious which environment a secret belongs to
✅ **Sync safety**: `sync_env.sh` only syncs secrets matching the prefix

### What This Does NOT Prevent

❌ **Compromised project**: Single Supabase project = shared blast radius
❌ **Malicious code**: Intentional `Deno.env.get("PROD__...")` bypass
❌ **Token theft**: If attacker has project access, they see all secrets

**Recommendation**: When feasible, migrate to separate Supabase projects for true isolation.

---

## Migration from Bare Names

If you have existing secrets without prefixes:

### 1. Identify Secrets

```bash
supabase secrets list | grep -v -E '^(STAGE__|PROD__)'
```

### 2. Duplicate with Prefix

```bash
# For each secret:
OLD_VALUE=$(supabase secrets get OLD_NAME)
supabase secrets set STAGE__OLD_NAME="${OLD_VALUE}"
supabase secrets set PROD__OLD_NAME="${DIFFERENT_PROD_VALUE}"
```

### 3. Update Code

```typescript
// Before
const key = Deno.env.get("OLD_NAME");

// After
import { getEnvSecret } from "../_shared/env.ts";
const key = getEnvSecret("OLD_NAME"); // Resolves to STAGE__/PROD__
```

### 4. Remove Old Secrets

```bash
supabase secrets unset OLD_NAME
```

---

## Troubleshooting

### Error: "ENVIRONMENT must be set"

**Cause**: Edge Function started without ENVIRONMENT variable

**Fix**: Set ENVIRONMENT in deployment config
```bash
# In deploy script or CI
supabase functions deploy my-function --env ENVIRONMENT=staging
```

### Error: "Missing required secret: STAGE__XXX"

**Cause**: Secret not synced for this environment

**Fix**: Run sync script
```bash
export STAGE__XXX="value"
ENVIRONMENT=staging ./scripts/secrets/sync_env.sh
```

### Wrong Secret Value in Runtime

**Diagnostic**: Check which prefix is being used
```typescript
import { envPrefix } from "../_shared/env.ts";
console.log("Using prefix:", envPrefix());
```

**Fix**: Verify ENVIRONMENT is set correctly at deploy/runtime

---

## Related Documentation

- `docs/security/SECRET_MANAGEMENT.md` - General secret management
- `docs/security/OPERATIONAL_RUNBOOK.md` - Day-to-day operations
- `infra/secrets/registry.yaml` - Secret registry (SSOT)

---

**Last Updated**: 2026-02-13
**Policy Version**: 1.0.0
