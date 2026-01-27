# MCP Secrets Management Strategy

**Goal:** Never duplicate secrets across clients.

## Storage Hierarchy

### 1. Development (Local)

**Primary:** Shell RC files
```bash
# ~/.zshrc or ~/.bashrc
export ANTHROPIC_API_KEY="sk-ant-..."
export SUPABASE_ACCESS_TOKEN="sbp_..."
export GITHUB_TOKEN="ghp_..."
export VERCEL_TOKEN="..."
export DIGITALOCEAN_API_TOKEN="dop_v1_..."
```

**Backup:** Encrypted vault
```bash
# 1Password
op item get "Anthropic API Key" --fields password

# SOPS (age-encrypted)
sops -d secrets.yaml | grep ANTHROPIC_API_KEY

# Doppler
doppler secrets get ANTHROPIC_API_KEY --plain
```

### 2. CI/CD (GitHub Actions)

**GitHub Secrets:**
- Settings → Secrets and variables → Actions
- Add all required env vars from `secrets/schema.json`

**Usage in workflow:**
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: python3 scripts/probe_capabilities.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

### 3. Production (Vercel/E2B)

**Vercel Environment Variables:**
```bash
vercel env add ANTHROPIC_API_KEY production
vercel env add SUPABASE_ACCESS_TOKEN production
```

**E2B Sandbox Env:**
```typescript
import { Sandbox } from '@e2b/sdk';

const sandbox = await Sandbox.create({
  template: 'node-20',
  env: {
    ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
    SUPABASE_ACCESS_TOKEN: process.env.SUPABASE_ACCESS_TOKEN,
  }
});
```

## Schema Validation

`secrets/schema.json` defines **names and formats only**:

```json
{
  "required": {
    "anthropic": {
      "ANTHROPIC_API_KEY": {
        "format": "sk-ant-...",
        "required_for": ["pulser"]
      }
    }
  }
}
```

Validate secrets exist:
```bash
python3 scripts/validate_secrets.py
```

## Security Rules

### ✅ Do

- Store secrets in shell RC + encrypted vault
- Use `$VAR_NAME` placeholders in MCP configs
- Validate format: `echo ${TOKEN:0:10}` (prefix only)
- Rotate tokens quarterly

### ❌ Don't

- Commit secrets to Git (ever)
- Hardcode tokens in MCP configs
- Share `.env.local` files
- Log full token values

## Secret Rotation

1. Generate new token
2. Update in vault + shell RC
3. Update in CI secrets
4. Update in Vercel/E2B env
5. Revoke old token
