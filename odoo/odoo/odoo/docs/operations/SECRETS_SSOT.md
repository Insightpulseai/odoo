# Secrets SSOT Runbook

> How to manage, store, rotate, and audit secrets for InsightPulse AI.
> SSOT identifier registry: `ssot/secrets/registry.yaml`

---

## Quick Reference: Approved Stores

| Store | When to use | Access pattern |
|-------|-------------|----------------|
| macOS Keychain | Local dev — any secret | `security find-generic-password -s "key-name" -w` |
| GNOME Keyring | Local dev (Linux) | `secret-tool lookup key value` |
| GitHub Actions Secrets | CI/CD — build and deploy secrets | `${{ secrets.SECRET_NAME }}` |
| Supabase Vault | Runtime — Odoo/n8n/Edge Functions | `vault.decrypted_secrets` view |
| Vercel env vars | Ops Console deployment | Auto-injected at build/runtime |

---

## macOS Keychain (Local Dev)

### Store a secret
```bash
# Generic password entry
security add-generic-password \
  -s "GEMINI_API_KEY" \
  -a "insightpulseai-odoo" \
  -w "your-actual-key-here"
```

### Retrieve and inject at shell start
Add to `~/.zshrc`:
```bash
export GEMINI_API_KEY="$(security find-generic-password -s "GEMINI_API_KEY" -a "insightpulseai-odoo" -w 2>/dev/null)"
```

### Delete a secret
```bash
security delete-generic-password -s "GEMINI_API_KEY" -a "insightpulseai-odoo"
```

---

## GitHub Actions Secrets

### Add a secret via CLI
```bash
# Requires gh CLI authenticated with write:secrets scope
gh secret set GEMINI_API_KEY --repo Insightpulseai/odoo
# Prompts for value interactively (not echoed)
```

### Add a secret via pipe (for automation)
```bash
echo "value" | gh secret set GEMINI_API_KEY --repo Insightpulseai/odoo
```

### List all secrets (names only — values not accessible)
```bash
GITHUB_TOKEN="" gh secret list --repo Insightpulseai/odoo
```

### Reference in workflow
```yaml
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

---

## Supabase Vault

Supabase Vault stores secrets encrypted at rest, accessible via `vault.decrypted_secrets`.

### Create a secret (psql)
```bash
# Connect to Supabase
psql "$SUPABASE_DB_URL"

-- Create a secret
SELECT vault.create_secret('your-secret-value', 'secret_name', 'Description');
```

### Create a secret (Supabase CLI)
```bash
# Not yet supported via CLI — use psql or Edge Function
```

### Read a secret in Edge Function
```typescript
const { data, error } = await supabaseAdmin
  .from('vault.decrypted_secrets')
  .select('decrypted_secret')
  .eq('name', 'zoho_client_id')
  .single();

const secretValue = data?.decrypted_secret;
```

### Read a secret (psql)
```sql
-- Restricted to service_role
SELECT name, decrypted_secret, description
FROM vault.decrypted_secrets
WHERE name = 'zoho_client_id';
```

### Rotate a secret (psql)
```sql
-- Find the secret ID first
SELECT id, name FROM vault.secrets WHERE name = 'zoho_client_id';

-- Update the value
SELECT vault.update_secret('<uuid-from-above>', 'new-secret-value');
```

---

## Secret Identifier SSOT Workflow

The registry at `ssot/secrets/registry.yaml` tracks **names** only — never values.

### Add a new secret
1. Add an entry to `ssot/secrets/registry.yaml`:
   ```yaml
   my_new_secret:
     purpose: "What this secret does"
     approved_stores: [github_actions]
     github_secret_name: MY_NEW_SECRET
     consumers:
       - path/to/consumer/file.ts
   ```
2. Commit the registry update (safe — no values)
3. Add the value to the appropriate store(s) (GitHub Secrets, Vault, keychain)
4. Update consumer code to read from env var

### Remove a secret
1. Remove the consumer code
2. Remove from all stores (GitHub Secrets, Vault, keychain)
3. Remove from `ssot/secrets/registry.yaml`
4. Commit all three changes together

---

## Resolution Order for Scripts

When a script needs a secret, it should check in this order:
1. Environment variable (injected from store)
2. `.env.local` file (local dev only — gitignored)
3. Fail with a clear error message: `"SECRET_NAME is not set. See ssot/secrets/registry.yaml."`

**Never** fall back to a hardcoded default for a real secret.

---

## What to Do If a Secret Is Exposed

If a secret value appears in:
- Git history (committed file)
- CI logs (echoed/printed)
- Chat history (pasted)
- PR description

**Immediate response checklist**:
- [ ] **Rotate the secret immediately** — assume it is compromised
- [ ] Revoke the old credential at the provider (GitHub, Cloudflare, Zoho, Google, etc.)
- [ ] Generate and store a new credential
- [ ] Update all stores (GitHub Secrets, Vault, etc.) with the new value
- [ ] If in git history: use `git filter-repo` to purge (requires force push to main — get team approval)
- [ ] If in CI logs: delete the workflow run from GitHub Actions UI
- [ ] Document the incident in `docs/evidence/<stamp>/security-incident/`

**Do NOT**:
- Leave the exposed secret active "just for now"
- Assume no one saw it because the repo is private
- Skip the rotation step even if you believe no one accessed it

---

## Audit Checklist (Quarterly)

- [ ] Run `scripts/ci/check_domains_ssot.py` — 0 violations
- [ ] Run `gh secret list --repo Insightpulseai/odoo` — compare to `ssot/secrets/registry.yaml`
- [ ] Check for orphaned secrets (in GitHub but not in registry)
- [ ] Check for undocumented secrets (in registry but not in GitHub)
- [ ] Verify rotation dates — rotate any secrets past their `rotation_policy`
- [ ] Review `consumers` list — remove any decommissioned consumers

---

*Owner: Platform Engineering*
*SSOT file: `ssot/secrets/registry.yaml`*
