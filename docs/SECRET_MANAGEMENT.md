# Secret Management for Claude Agents

> **Canonical reference** for how Claude agents and tools access credentials securely.
> **Last updated**: 2026-01-28

---

## Overview

All Claude agent operations require access to credentials (API keys, database passwords, tokens). This document defines:

- **Where** secrets are stored (macOS Keychain for local, Supabase Vault for CI/remote)
- **How** secrets are loaded into environment variables before agent execution
- **What** environment variables are required for agents to function

**Zero secrets in Git**: Only loading scripts and documentation live in this repository.

---

## Required Secrets

| Purpose | Environment Variable | Source (Local) | Source (Remote/CI) |
|---------|---------------------|----------------|-------------------|
| Claude API | `CLAUDE_API_KEY` | macOS Keychain | Supabase Vault |
| Supabase URL | `SUPABASE_URL` | macOS Keychain | Supabase Vault |
| Supabase anon key | `SUPABASE_ANON_KEY` | macOS Keychain | Supabase Vault |
| Supabase service role | `SUPABASE_SERVICE_ROLE_KEY` | macOS Keychain | Supabase Vault |
| OpenAI API (optional) | `OPENAI_API_KEY` | macOS Keychain | Supabase Vault |
| GitHub token (optional) | `GITHUB_TOKEN` | macOS Keychain | Supabase Vault |
| Anthropic API (optional) | `ANTHROPIC_API_KEY` | macOS Keychain | Supabase Vault |
| Postgres password (optional) | `POSTGRES_PASSWORD` | macOS Keychain | Supabase Vault |

---

## Local Development (macOS Keychain)

### One-Time Setup

Run the interactive setup script:

```bash
./scripts/claude/setup_keychain.sh
```

This will prompt you for each secret and store it securely in macOS Keychain under service name `ipai_claude_secrets`.

**Manual setup** (if you prefer):

```bash
# Required secrets
security add-generic-password -s ipai_claude_secrets -a CLAUDE_API_KEY -w "sk-ant-***" -U
security add-generic-password -s ipai_claude_secrets -a SUPABASE_URL -w "https://***" -U
security add-generic-password -s ipai_claude_secrets -a SUPABASE_ANON_KEY -w "eyJ***" -U
security add-generic-password -s ipai_claude_secrets -a SUPABASE_SERVICE_ROLE_KEY -w "eyJ***" -U

# Optional secrets
security add-generic-password -s ipai_claude_secrets -a OPENAI_API_KEY -w "sk-***" -U
security add-generic-password -s ipai_claude_secrets -a GITHUB_TOKEN -w "ghp_***" -U
```

### Loading Secrets

Before running any Claude agent or tool:

```bash
# From repo root
source ./scripts/claude/load_secrets_local.sh
```

This exports all required environment variables from Keychain.

### Running Agents

Use the universal agent runner:

```bash
# Run with secret loading
./scripts/claude/run_agent.sh local <command>

# Examples:
./scripts/claude/run_agent.sh local claude-code run ./spec/agent_task.yaml
./scripts/claude/run_agent.sh local python -m tools.agent_entrypoint
./scripts/claude/run_agent.sh local npm run agent:run
```

---

## Remote / CI / Production (Supabase Vault)

### Prerequisites

1. **Supabase Vault** must be configured with all required secrets
2. **Edge Function** or RPC endpoint must expose secrets as JSON
3. **CI environment** must have these variables:
   - `SUPABASE_SECRETS_ENDPOINT` - URL of secrets loader endpoint
   - `SUPABASE_SECRETS_TOKEN` - Auth token for endpoint access

### Loading Secrets

In CI workflows or remote environments:

```bash
# Source the remote loader
source ./scripts/claude/load_secrets_remote.sh
```

This fetches secrets from Supabase Vault and exports them as environment variables.

### CI Workflow Integration

Example GitHub Actions workflow:

```yaml
name: Claude Agent Execution

on:
  workflow_dispatch:
  schedule:
    - cron: '0 */6 * * *'

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y jq curl

      - name: Load secrets from Supabase Vault
        env:
          SUPABASE_SECRETS_ENDPOINT: ${{ secrets.SUPABASE_SECRETS_ENDPOINT }}
          SUPABASE_SECRETS_TOKEN: ${{ secrets.SUPABASE_SECRETS_TOKEN }}
        run: |
          source ./scripts/claude/load_secrets_remote.sh

      - name: Run agent
        run: |
          ./scripts/claude/run_agent.sh remote claude-code run ./spec/scheduled_task.yaml
```

---

## Agent Runtime Contract

**All Claude-compatible agents MUST follow this sequence:**

1. **Load secrets** (local or remote):
   ```bash
   source ./scripts/claude/load_secrets_local.sh   # Local macOS
   # OR
   source ./scripts/claude/load_secrets_remote.sh  # Remote/CI
   ```

2. **Verify environment**:
   ```bash
   : "${CLAUDE_API_KEY:?CLAUDE_API_KEY is required}"
   : "${SUPABASE_URL:?SUPABASE_URL is required}"
   : "${SUPABASE_ANON_KEY:?SUPABASE_ANON_KEY is required}"
   : "${SUPABASE_SERVICE_ROLE_KEY:?SUPABASE_SERVICE_ROLE_KEY is required}"
   ```

3. **Run agent/tool** only after verification passes.

**No agent should:**
- Read secrets directly from Keychain or Vault
- Hardcode credentials
- Log full secret values

---

## Secret Rotation

### Local (macOS Keychain)

Update existing secrets:

```bash
# Re-run setup script (will prompt to overwrite)
./scripts/claude/setup_keychain.sh

# Or update manually
security add-generic-password -s ipai_claude_secrets -a CLAUDE_API_KEY -w "NEW_VALUE" -U
```

### Remote (Supabase Vault)

1. Update secrets in Supabase Vault (via dashboard or CLI)
2. No code changes required - next agent run will fetch new values

### Verification After Rotation

```bash
# Local
source ./scripts/claude/load_secrets_local.sh
echo "CLAUDE_API_KEY present: ${CLAUDE_API_KEY:+YES}"

# Remote (in CI)
source ./scripts/claude/load_secrets_remote.sh
echo "CLAUDE_API_KEY present: ${CLAUDE_API_KEY:+YES}"
```

---

## Security Audit

### Check for leaked secrets in Git

```bash
# Scan for common secret patterns
git grep -n "sk-ant-" || echo "✅ No Claude API keys found"
git grep -n "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" || echo "✅ No JWT tokens found"
git grep -n "SUPABASE_SERVICE_ROLE_KEY" || echo "✅ No service role keys found"

# Check for hardcoded passwords
git grep -ni "password.*=.*['\"]" || echo "✅ No hardcoded passwords found"
```

### Verify Keychain storage

```bash
# List all secrets for this service
security find-generic-password -s ipai_claude_secrets -g 2>&1 | grep "acct"
```

### Audit secret access

```bash
# Check which scripts source secret loaders
grep -r "load_secrets" scripts/ || echo "No references found"
```

---

## Troubleshooting

### "Required secret not found in Keychain"

**Cause**: Secret not stored or service name mismatch

**Fix**:
```bash
# Re-run setup
./scripts/claude/setup_keychain.sh

# Or verify service name
security find-generic-password -s ipai_claude_secrets -a CLAUDE_API_KEY -w
```

### "Empty response from Supabase Vault"

**Cause**: Endpoint unreachable or auth token invalid

**Fix**:
```bash
# Test endpoint manually
curl -H "Authorization: Bearer $SUPABASE_SECRETS_TOKEN" "$SUPABASE_SECRETS_ENDPOINT"

# Verify CI secrets are set
echo "Endpoint: ${SUPABASE_SECRETS_ENDPOINT:+SET}"
echo "Token: ${SUPABASE_SECRETS_TOKEN:+SET}"
```

### "jq: command not found"

**Cause**: Missing dependency for JSON parsing

**Fix**:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install -y jq
```

---

## File Reference

| File | Purpose |
|------|---------|
| `scripts/claude/load_secrets_local.sh` | Load secrets from macOS Keychain |
| `scripts/claude/load_secrets_remote.sh` | Load secrets from Supabase Vault |
| `scripts/claude/run_agent.sh` | Universal agent runner with secret loading |
| `scripts/claude/setup_keychain.sh` | Interactive Keychain setup wizard |
| `docs/SECRET_MANAGEMENT.md` | This document |

---

## Policy

1. **Never commit secrets to Git** - use `.gitignore` for any local credential files
2. **Rotate regularly** - at least quarterly or after any exposure incident
3. **Least privilege** - agents should only have access to secrets they need
4. **Audit trail** - log secret access (not values) for security monitoring
5. **New secrets** - must be added to:
   - This document (required secrets table)
   - Both loader scripts (`load_secrets_local.sh`, `load_secrets_remote.sh`)
   - Setup script (`setup_keychain.sh`)
   - Agent verification checks

---

**Last reviewed**: 2026-01-28
**Next review**: 2026-04-28 (quarterly)
