# Secrets SSOT Runbook

> SSOT for secret identifiers: `ssot/secrets/registry.yaml`
> Policy: `CLAUDE.md § Secrets Policy`
> Supabase project: `spdtwktxdalcfigzeqrz`

---

## Stores at a glance

| Store | When to use | How values are accessed |
|-------|-------------|------------------------|
| **OS keychain/keyring** | Local dev, one-person ops | `security find-generic-password` / `secret-tool lookup` → env var |
| **GitHub Actions Secrets** | CI workflows | `${{ secrets.SECRET_NAME }}` |
| **Supabase Vault** | DB functions, Edge Functions, automation needing DB-side secrets | `vault.decrypted_secrets` view (SQL) or `supabase.rpc('vault_read', ...)` |

---

## OS keychain (local dev)

### Store a secret (macOS)

```bash
# Store
security add-generic-password \
  -a "$USER" \
  -s "cf_dns_read_token" \
  -w "YOUR_TOKEN_VALUE"

# Retrieve into env var
export CF_API_TOKEN=$(security find-generic-password -a "$USER" -s "cf_dns_read_token" -w)
```

### Store a secret (Linux — GNOME Keyring / secret-tool)

```bash
# Store
secret-tool store --label="cf_dns_read_token" service cf_dns_read_token username "$USER"

# Retrieve
export CF_API_TOKEN=$(secret-tool lookup service cf_dns_read_token username "$USER")
```

### Shell init pattern (`.zshrc` / `.bashrc`)

```bash
# Lazy-load secrets from keychain — avoids subshell on every prompt
_load_secret() {
  local key="$1" var="$2"
  command -v security &>/dev/null && \
    export "$var"="$(security find-generic-password -a "$USER" -s "$key" -w 2>/dev/null)"
}

_load_secret cf_dns_read_token   CF_API_TOKEN
_load_secret mailgun_api_key     MAILGUN_API_KEY
_load_secret n8n_api_key         N8N_API_KEY
```

---

## GitHub Actions Secrets (CI)

### Add a secret

```
GitHub → Insightpulseai/odoo
  → Settings → Secrets and variables → Actions
  → New repository secret
    Name:  CF_DNS_READ_TOKEN   (see ssot/secrets/registry.yaml for the exact name)
    Value: <paste once here only>
```

### Reference in a workflow

```yaml
env:
  CF_API_TOKEN: ${{ secrets.CF_DNS_READ_TOKEN }}
```

### Naming convention

Use the `github_secret_name` field from `ssot/secrets/registry.yaml` exactly.
This is the canonical reference — never invent new names.

---

## Cloudflare token split — read vs edit

Cloudflare API tokens for this repo are split by blast radius:

| Secret name | Cloudflare permission | Used by | Blast radius |
|-------------|----------------------|---------|--------------|
| `CF_DNS_READ_TOKEN` | Zone:DNS:Read (scoped to insightpulseai.com) | `cloudflare-dns-drift.yml`, `cloudflare-authority-gate.yml`, `verify_cloudflare_dns_drift.py` | Read-only — cannot modify records |
| `CF_DNS_EDIT_TOKEN` | Zone:DNS:Edit (scoped to insightpulseai.com) | `cloudflare-dns-apply.yml` only | Can create/update DNS records in the zone |
| `CF_DNS_ZONE_ID` | N/A (Zone ID string, not an API token) | All Cloudflare workflows | None — not a secret per se, but treated as one |

### Why split?

- The drift/authority gate workflows run on **every PR** including forks.
  A read-only token limits the damage if the token is extracted from CI logs.
- The edit token is used only by the **apply-on-merge** workflow (push to main),
  which runs in a protected environment with no fork access.
- This follows Cloudflare's **minimal-permission tokens** best practice.

### Create tokens in Cloudflare dashboard

```
Cloudflare → My Profile → API Tokens → Create Token

Read token (CF_DNS_READ_TOKEN):
  Template: "Read all resources" → customize:
  Permissions: Zone:DNS:Read
  Zone resources: Include → Specific zone → insightpulseai.com
  TTL: 1 year (or no expiry)

Edit token (CF_DNS_EDIT_TOKEN):
  Template: "Edit zone DNS" → customize:
  Permissions: Zone:DNS:Edit
  Zone resources: Include → Specific zone → insightpulseai.com
  IP filtering: (optional) restrict to GitHub Actions IP ranges
  TTL: 6 months (rotate regularly)
```

### Rotation schedule

| Token | Recommended rotation | Notes |
|-------|---------------------|-------|
| `CF_DNS_READ_TOKEN` | Annual | Low risk; rotate with other annual secrets |
| `CF_DNS_EDIT_TOKEN` | Every 6 months | Higher risk; more frequent rotation |
| `CF_DNS_ZONE_ID` | Never (it's a Zone ID, not a token) | Update only if zone changes |

---

## Supabase Vault (platform / automation)

Vault stores secrets encrypted at rest in `vault.secrets`. Decrypted values are
only available via the `vault.decrypted_secrets` view, which is restricted by
PostgreSQL privileges (see "Restrict access" below).

### Create a secret

```sql
-- Run in Supabase SQL editor or via psql
SELECT vault.create_secret(
  'YOUR_SECRET_VALUE',   -- plaintext value (encrypted on write)
  'zoho_client_secret',  -- name (matches vault_secret_name in registry.yaml)
  'Zoho Mail API OAuth2 client secret'  -- description
);
```

Returns a UUID. Store the UUID in `ssot/secrets/registry.yaml` as `vault_uuid` if needed.

### Read a secret (SQL)

```sql
-- Requires access to vault.decrypted_secrets
SELECT decrypted_secret
FROM vault.decrypted_secrets
WHERE name = 'zoho_client_secret';
```

### Read a secret (Edge Function / Deno)

```typescript
// Edge Functions have access to secrets via Deno.env.get() when set as
// Supabase Edge Function secrets (not the same as vault.secrets).
// For Vault, use the Supabase client with service role:

const { data } = await supabaseAdmin
  .rpc('vault_read_secret', { secret_name: 'zoho_client_secret' });
```

> Note: Edge Functions prefer `Deno.env.get('SECRET_NAME')` for secrets set
> in the Edge Function environment. Use Vault for secrets shared with SQL functions.

### Rotate a secret

```sql
-- Update value in Vault — no repo change needed
UPDATE vault.secrets
SET secret = vault._encrypt(
  'NEW_SECRET_VALUE',
  current_setting('pgsodium.secret_key')::bytea
)
WHERE name = 'zoho_client_secret';
```

Or use the Supabase dashboard: **Database → Vault → Edit secret**.

### Restrict access to `vault.decrypted_secrets`

The decrypted view exposes plaintext. Lock it down:

```sql
-- Revoke from public and anon role
REVOKE SELECT ON vault.decrypted_secrets FROM anon;
REVOKE SELECT ON vault.decrypted_secrets FROM authenticated;

-- Grant only to service_role (or a dedicated automation role)
GRANT SELECT ON vault.decrypted_secrets TO service_role;

-- Or create a wrapper function with SECURITY DEFINER for fine-grained access
CREATE OR REPLACE FUNCTION get_secret(secret_name text)
RETURNS text
LANGUAGE sql
SECURITY DEFINER
AS $$
  SELECT decrypted_secret
  FROM vault.decrypted_secrets
  WHERE name = secret_name
  LIMIT 1;
$$;

-- Grant function only to the roles that need it
GRANT EXECUTE ON FUNCTION get_secret(text) TO your_automation_role;
```

---

## Secret identifier SSOT

All secrets are registered in `ssot/secrets/registry.yaml` with:
- `purpose` — what it's for
- `approved_stores` — where it may live
- `github_secret_name` / `vault_secret_name` — canonical identifier per store
- `consumers` — files/modules that use it
- `notes` — rotation hints, sensitivity level

**When you add a new secret:**
1. Add an entry to `ssot/secrets/registry.yaml` (identifiers only)
2. Store the value in the approved store(s)
3. Reference by name in code (never inline the value)

---

## Scanner allowlist (SSOT)

The secrets scanner (`scripts/check_no_plaintext_secrets.py`) loads a runtime allowlist of
false-positive suppression patterns from:

```
ssot/secrets/allowlist_regex.txt
```

This file is the **single authoritative source** for patterns that are safe to ignore during
scanning. Do not hard-code allowlist patterns inside the scanner script itself — add them here.

### File format

One Python regex per line. Lines starting with `#` are comments. Blank lines are ignored.

```
# Env var references (never raw secrets)
\$\{[A-Z_][A-Z0-9_]*\}
\$\{\{[^}]*secrets\.[A-Z_][A-Z0-9_]*[^}]*\}\}

# Supabase Vault references
vault\.decrypted_secrets

# Example / placeholder markers
(EXAMPLE|example|placeholder|your[-_]|<YOUR_|MY_TOKEN|REPLACE_ME|CHANGEME|__REPLACE__)

# Test fixtures
(test_secret|fake_token|dummy_key|mock_key|test_key|sample_key|example_key|fixture_key)
```

### Adding a new allowlist entry

1. Open `ssot/secrets/allowlist_regex.txt`.
2. Add a regex with a comment explaining what it matches and why it is safe.
3. Commit the change. The scanner picks it up on the next run — no code change needed.

### Directories excluded from scanning

These paths are never scanned regardless of the allowlist (third-party / build artifacts):

```
addons/odoo/   addons/oca/   node_modules/   .pnpm-store/
vendor/        .next/        dist/           build/
__pycache__/   .tox/         .venv/          venv/
```

### Stable output format

The scanner emits one line per finding:

```
path/to/file.py:42:HIGH:github-pat-classic
    ghp_EXAMPLETOKEN...
```

Format: `<path>:<line>:<SEVERITY>:<pattern-id>` — grep- and annotation-safe.
CI converts these lines into GitHub PR annotations automatically.

---

## Resolution order for scripts

Scripts that need secrets should resolve in this order:

```python
# 1. CI / explicit env var (set by GitHub Secrets or local shell init)
token = os.environ.get("CF_API_TOKEN")

# 2. Fail with actionable message (never silently proceed)
if not token:
    print("ERROR: CF_API_TOKEN required. Store in keychain or GitHub Secrets.")
    print("  See: ssot/secrets/registry.yaml → cf_dns_read_token")
    sys.exit(2)
```

For server-side contexts with Supabase access, a Vault fallback can be added after
step 1. Never add Vault fallback in client-side or browser code.

---

## What to do if a secret is exposed

1. **Assess durability**: Is it in a committed file, CI log, or only in a transient
   chat/terminal session?
   - Committed to repo → **rotate immediately**, purge from git history if needed
   - CI log (GitHub) → rotate, then expire the log if possible
   - Transient chat/terminal → move to keychain now; rotate when convenient

2. **Rotate the secret** in the issuing system (Cloudflare, Zoho, Mailgun, etc.)

3. **Update all stores** where the old value lived (keychain, GitHub Secrets, Vault)

4. **Update `ssot/secrets/registry.yaml`** only if the secret name changed

5. **No repo commit needed** for value rotation — the registry only tracks identifiers
