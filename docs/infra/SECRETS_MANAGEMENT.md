# Secrets Management for Odoo-Supabase Integration

**Document:** Canonical secrets boundary pattern for Supabase Edge Functions → Odoo
**Policy:** No secrets in code, git, or frontends. All secrets in Supabase env or Vault.

---

## Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SECRETS BOUNDARY                                 │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│  │  Git Repo       │    │  Supabase       │    │  Vault          │    │
│  │  (NO SECRETS)   │    │  (Secrets Env)  │    │  (Optional)     │    │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘    │
│           │                      │                      │             │
│           │  ┌───────────────────▼──────────────────────▼─────┐       │
│           │  │           Edge Functions                        │       │
│           │  │   Deno.env.get("ODOO_PASSWORD")                │       │
│           │  │   await getVaultSecret("ODOO_PASSWORD")        │       │
│           │  └───────────────────┬────────────────────────────┘       │
│           │                      │                                     │
│           │                      ▼                                     │
│           │              ┌───────────────┐                            │
│           │              │  Odoo CE 18   │                            │
│           │              │  (JSON-RPC)   │                            │
│           │              └───────────────┘                            │
│           │                                                            │
└───────────┴────────────────────────────────────────────────────────────┘
```

---

## Option A: Supabase-Native Secrets (Recommended)

### Required Secrets

| Secret | Purpose | Example Value |
|--------|---------|---------------|
| `SUPABASE_URL` | Supabase API URL | `https://xxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role for RLS bypass | `eyJ...` |
| `ODOO_URL` | Odoo instance URL | `https://erp.insightpulseai.net` |
| `ODOO_DB` | Odoo database name | `production` |
| `ODOO_USER` | Odoo API user login | `seed_bot@insightpulseai.com` |
| `ODOO_PASSWORD` | Odoo API password | `<secret>` |
| `SEED_RUN_TOKEN` | Shared auth token for function calls | `<random-64-char>` |

### Setting Secrets (CLI)

```bash
# Set all secrets for Edge Functions
supabase functions secrets set \
  SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co" \
  SUPABASE_SERVICE_ROLE_KEY="<service-role-key>" \
  ODOO_URL="https://erp.insightpulseai.net" \
  ODOO_DB="production" \
  ODOO_USER="seed_bot@insightpulseai.com" \
  ODOO_PASSWORD="<super-secret-password>" \
  SEED_RUN_TOKEN="<long-random-token>"

# Verify secrets are set (shows names only, not values)
supabase functions secrets list
```

### Local Development

Create `.env.local` (gitignored):

```bash
# .env.local (NEVER COMMIT)
SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
SUPABASE_ANON_KEY="<anon-key>"
SUPABASE_SERVICE_ROLE_KEY="<service-role-key>"

ODOO_URL="https://erp.insightpulseai.net"
ODOO_DB="production"
ODOO_USER="seed_bot@insightpulseai.com"
ODOO_PASSWORD="<super-secret-password>"

SEED_RUN_TOKEN="<long-random-token>"
```

Run function locally:

```bash
supabase functions serve seed-odoo-finance --env-file .env.local
```

### Edge Function Pattern

```typescript
// Correct: Read from environment
const ODOO = {
  url: Deno.env.get("ODOO_URL") ?? "",
  db: Deno.env.get("ODOO_DB") ?? "",
  user: Deno.env.get("ODOO_USER") ?? "",
  password: Deno.env.get("ODOO_PASSWORD") ?? "",
};

// WRONG: Never hardcode secrets
const ODOO = {
  password: "my-secret-password",  // NEVER DO THIS
};
```

---

## Option B: HashiCorp Vault Integration

For centralized secrets management across multiple platforms.

### Vault Setup

```bash
# Store Odoo credentials in Vault KV
vault kv put secret/odoo \
  url="https://erp.insightpulseai.net" \
  db="production" \
  user="seed_bot@insightpulseai.com" \
  password="<super-secret-password>"

# Create policy
cat > odoo-seed-policy.hcl << 'EOF'
path "secret/data/odoo" {
  capabilities = ["read"]
}
EOF

vault policy write odoo-seed-policy odoo-seed-policy.hcl

# Create token for Supabase
vault token create -policy=odoo-seed-policy -ttl=24h
```

### Supabase Configuration

```bash
# Store only Vault connection info in Supabase
supabase functions secrets set \
  VAULT_ADDR="https://vault.insightpulseai.net" \
  VAULT_TOKEN="<short-lived-vault-token>"
```

### Edge Function Pattern

```typescript
async function getOdooSecretsFromVault(): Promise<OdooConfig> {
  const addr = Deno.env.get("VAULT_ADDR")!;
  const token = Deno.env.get("VAULT_TOKEN")!;

  const res = await fetch(`${addr}/v1/secret/data/odoo`, {
    headers: { "X-Vault-Token": token },
  });

  if (!res.ok) {
    throw new Error(`Vault error: ${res.status} ${res.statusText}`);
  }

  const json = await res.json();
  const data = json.data?.data ?? json.data;

  return {
    url: data.url as string,
    db: data.db as string,
    user: data.user as string,
    password: data.password as string,
  };
}

// Usage
const ODOO = await getOdooSecretsFromVault();
```

---

## GitHub Actions Secrets

For CI/CD workflows that call Edge Functions:

```yaml
# Required secrets in GitHub repository settings
SUPABASE_URL: https://spdtwktxdalcfigzeqrz.supabase.co
SEED_RUN_TOKEN: <same-token-as-supabase-functions>
DROPLET_SSH_PRIVATE_KEY: <ssh-key-for-verification>
DROPLET_IP: 178.128.112.214
```

Usage in workflow:

```yaml
- name: Trigger seed function
  run: |
    curl -X POST \
      -H "Authorization: Bearer ${{ secrets.SEED_RUN_TOKEN }}" \
      "${{ secrets.SUPABASE_URL }}/functions/v1/seed-odoo-finance"
```

---

## Secret Rotation

### Rotate Odoo Password

```bash
# 1. Update in Odoo (via UI or XML-RPC)
# 2. Update in Supabase
supabase functions secrets set ODOO_PASSWORD="<new-password>"

# 3. Verify function still works
curl -X POST \
  -H "Authorization: Bearer $SEED_RUN_TOKEN" \
  "${SUPABASE_URL}/functions/v1/seed-odoo-finance"
```

### Rotate SEED_RUN_TOKEN

```bash
# 1. Generate new token
NEW_TOKEN=$(openssl rand -hex 32)

# 2. Update in Supabase
supabase functions secrets set SEED_RUN_TOKEN="$NEW_TOKEN"

# 3. Update in GitHub Secrets (via UI or CLI)
gh secret set SEED_RUN_TOKEN --body "$NEW_TOKEN"

# 4. Update any n8n webhooks that use the token
```

### Rotate Vault Token (if using Vault)

```bash
# 1. Create new token
vault token create -policy=odoo-seed-policy -ttl=24h
# Copy new token

# 2. Update in Supabase
supabase functions secrets set VAULT_TOKEN="<new-token>"

# 3. Revoke old token
vault token revoke <old-token>
```

---

## Security Checklist

### Never Do

- [ ] Hardcode secrets in TypeScript/Python code
- [ ] Commit `.env` files to git
- [ ] Log secrets (even in error messages)
- [ ] Store service role keys in frontend code
- [ ] Share production secrets in Slack/email

### Always Do

- [x] Use `Deno.env.get()` for all secrets in Edge Functions
- [x] Use `supabase functions secrets set` for deployment
- [x] Create `.env.example` with placeholder values
- [x] Add `.env*` to `.gitignore`
- [x] Rotate secrets periodically (quarterly minimum)
- [x] Use short-lived tokens where possible

### Verification

```bash
# Check no secrets in git history
git log -p --all -S "ODOO_PASSWORD" -- . | head -50
# Should return empty or only .env.example references

# Check .gitignore includes env files
grep -E "^\.env" .gitignore
# Should show: .env, .env.local, .env*.local

# List function secrets (names only)
supabase functions secrets list
```

---

## Audit Trail

All secret access is logged:

| Layer | Log Location | What's Logged |
|-------|--------------|---------------|
| Supabase Edge | Supabase Dashboard → Logs | Function invocations |
| Vault | Vault Audit Log | Secret reads/writes |
| Odoo | `ir.logging` | JSON-RPC calls from seed_bot |
| GitHub Actions | Workflow runs | Trigger timestamps |

---

## Emergency Procedures

### Compromised ODOO_PASSWORD

```bash
# 1. Immediately disable in Odoo
ssh root@178.128.112.214
docker exec odoo-erp-prod odoo-bin shell -d production << 'EOF'
env['res.users'].search([('login', '=', 'seed_bot@insightpulseai.com')]).write({'active': False})
EOF

# 2. Rotate password and re-enable
# 3. Update Supabase secrets
# 4. Review ir.logging for unauthorized access
```

### Compromised SEED_RUN_TOKEN

```bash
# 1. Immediately rotate
NEW_TOKEN=$(openssl rand -hex 32)
supabase functions secrets set SEED_RUN_TOKEN="$NEW_TOKEN"

# 2. Update GitHub secrets
gh secret set SEED_RUN_TOKEN --body "$NEW_TOKEN"

# 3. Review Supabase function logs for unauthorized calls
```

---

## Related Documentation

- [SUPABASE_ODOO_SEED_PATTERN.md](./SUPABASE_ODOO_SEED_PATTERN.md) - Seeding pattern
- [MCP_JOBS_SYSTEM.md](./MCP_JOBS_SYSTEM.md) - Job queue (also uses secrets)
- [../../SECURITY.md](../../SECURITY.md) - Repository security policy

---

*Last Updated: 2026-01-21*
*Version: 1.0.0*
