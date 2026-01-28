# CLAUDE.md

> Canonical instructions for how Claude agents access secrets using **macOS Keychain** (local) and **Supabase Vault** (remote/CI).
> All agent runs must have required secrets available via environment variables before any tools execute.

---

## 1. Scope & Responsibilities

This document defines:

- **Where** secrets are stored:
  - Local: **macOS Keychain**
  - Remote / CI / shared envs: **Supabase Vault**
- **How** secrets are **loaded into environment variables** before a Claude run.
- **What** environment variables are required for agents and tools to function.

Secrets are **never committed to Git**. Only references and loading scripts live in the repo.

---

## 2. Canonical Secret List

All Claude-compatible agents must treat this table as the **single source of truth** for required secrets.

| Purpose                    | Env var name                 | Source (local)        | Source (remote/CI)     |
|---------------------------|------------------------------|-----------------------|------------------------|
| Claude API key            | `CLAUDE_API_KEY`             | macOS Keychain        | Supabase Vault         |
| OpenAI API key (optional) | `OPENAI_API_KEY`             | macOS Keychain        | Supabase Vault         |
| Supabase URL              | `SUPABASE_URL`               | macOS Keychain        | Supabase Vault         |
| Supabase anon key         | `SUPABASE_ANON_KEY`          | macOS Keychain        | Supabase Vault         |
| Supabase service role key | `SUPABASE_SERVICE_ROLE_KEY`  | macOS Keychain        | Supabase Vault         |
| GitHub token (if needed)  | `GITHUB_TOKEN`               | macOS Keychain        | Supabase Vault         |

> **NOTE:** If additional secrets are introduced, they must be added to this table and wired into both Keychain and Vault loading flows.

---

## 3. Local Development: macOS Keychain

### 3.1 Storage Convention

Local secrets are stored as **generic passwords** in macOS Keychain with:

- **Service name**: `ipai_claude_secrets`
- **Account**: matches the env var name (e.g. `CLAUDE_API_KEY`)
- **Password**: the actual secret value

> If these names differ on your machine, update the `CLAUDE_SECRET_SERVICE` variable (see below) instead of editing scripts.

### 3.2 Setting a Secret (one-time per machine)

Run the following for each secret (example: `CLAUDE_API_KEY`):

```bash
security add-generic-password \
  -s ipai_claude_secrets \
  -a CLAUDE_API_KEY \
  -w "sk-********REPLACE_WITH_REAL_KEY********" \
  -U
```

Repeat for each variable (changing `-a` and `-w`):

```bash
# REQUIRED
security add-generic-password -s ipai_claude_secrets -a CLAUDE_API_KEY            -w "REPLACE"
security add-generic-password -s ipai_claude_secrets -a SUPABASE_URL             -w "REPLACE"
security add-generic-password -s ipai_claude_secrets -a SUPABASE_ANON_KEY        -w "REPLACE"
security add-generic-password -s ipai_claude_secrets -a SUPABASE_SERVICE_ROLE_KEY -w "REPLACE"

# OPTIONAL
security add-generic-password -s ipai_claude_secrets -a OPENAI_API_KEY           -w "REPLACE"
security add-generic-password -s ipai_claude_secrets -a GITHUB_TOKEN             -w "REPLACE"
```

### 3.3 Loading Secrets Into the Environment

Add this helper script in the repo (path can be adjusted as needed):

`./scripts/claude/load_secrets_local.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Assumptions (update if you change Keychain service name)
: "${CLAUDE_SECRET_SERVICE:=ipai_claude_secrets}"

# List of env vars we care about
REQUIRED_SECRETS=(
  "CLAUDE_API_KEY"
  "SUPABASE_URL"
  "SUPABASE_ANON_KEY"
  "SUPABASE_SERVICE_ROLE_KEY"
)

OPTIONAL_SECRETS=(
  "OPENAI_API_KEY"
  "GITHUB_TOKEN"
)

fetch_secret() {
  local name="$1"
  security find-generic-password \
    -s "${CLAUDE_SECRET_SERVICE}" \
    -a "${name}" \
    -w 2>/dev/null || true
}

export_secret() {
  local name="$1"
  local value
  value="$(fetch_secret "${name}")"

  if [[ -z "${value}" ]]; then
    return 1
  fi

  export "${name}=${value}"
  return 0
}

# Load required secrets
for var in "${REQUIRED_SECRETS[@]}"; do
  if ! export_secret "${var}"; then
    echo "ERROR: Required secret ${var} not found in macOS Keychain (service=${CLAUDE_SECRET_SERVICE})." >&2
    exit 1
  fi
done

# Load optional secrets (best-effort)
for var in "${OPTIONAL_SECRETS[@]}"; do
  if export_secret "${var}"; then
    echo "Loaded optional secret: ${var}"
  fi
done

echo "All required Claude secrets loaded from macOS Keychain."
```

Make it executable:

```bash
chmod +x ./scripts/claude/load_secrets_local.sh
```

### 3.4 Using It in Local Runs

Prior to running Claude Code CLI / agent scripts:

```bash
# From repo root
source ./scripts/claude/load_secrets_local.sh

# Now run whatever agent or tool you want
claude-code run ./spec/agent_task.yaml
# or
python -m tools.agent_entrypoint
```

---

## 4. Remote / CI / Shared Environments: Supabase Vault

> **Assumption:** Supabase Vault is configured for the project and managed via SQL/Edge functions or CLI. This section defines the contract; the exact implementation can be refined per project.

### 4.1 Storage Convention in Vault

For Supabase Vault, each secret is stored under:

- **Name**: matches the env var name, e.g. `CLAUDE_API_KEY`
- **Scope**: project-specific
- **Access**: read access restricted to a dedicated **"secrets loader"** Edge Function or service role.

Required keys in Vault:

- `CLAUDE_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- Optional: `OPENAI_API_KEY`, `GITHUB_TOKEN`, etc.

> TODO: Add the exact SQL / RPC function definition for Vault reads when the Supabase project structure is finalized.

### 4.2 Edge Function Loader (Conceptual Contract)

All non-local runs (CI, remote agents) must obtain secrets by calling a **Supabase Edge Function** (or RPC) that returns a JSON payload:

```json
{
  "CLAUDE_API_KEY": "*****",
  "SUPABASE_URL": "*****",
  "SUPABASE_ANON_KEY": "*****",
  "SUPABASE_SERVICE_ROLE_KEY": "*****",
  "OPENAI_API_KEY": "*****",
  "GITHUB_TOKEN": "*****"
}
```

**Runtime contract:**

- The Edge Function **must be authenticated** (e.g., with a CI-specific JWT or service token).
- The caller converts this JSON into environment variables before invoking Claude or any agents.

### 4.3 CI Loader Script

Example script to be used in CI or remote shells:

`./scripts/claude/load_secrets_remote.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Assumptions / placeholders:
# - SUPABASE_SECRETS_ENDPOINT: URL of Edge Function / RPC that returns secret JSON
# - SUPABASE_SECRETS_TOKEN: token with permission to call this endpoint
: "${SUPABASE_SECRETS_ENDPOINT:?SUPABASE_SECRETS_ENDPOINT is required}"
: "${SUPABASE_SECRETS_TOKEN:?SUPABASE_SECRETS_TOKEN is required}"

json="$(curl -sS -H "Authorization: Bearer ${SUPABASE_SECRETS_TOKEN}" "${SUPABASE_SECRETS_ENDPOINT}")"

if [[ -z "${json}" ]]; then
  echo "ERROR: Empty response from Supabase Vault loader endpoint." >&2
  exit 1
fi

# Parse and export known keys. Using jq is recommended.
required_vars=(
  "CLAUDE_API_KEY"
  "SUPABASE_URL"
  "SUPABASE_ANON_KEY"
  "SUPABASE_SERVICE_ROLE_KEY"
)

optional_vars=(
  "OPENAI_API_KEY"
  "GITHUB_TOKEN"
)

for var in "${required_vars[@]}"; do
  value="$(printf '%s' "${json}" | jq -r --arg k "${var}" '.[$k] // empty')"
  if [[ -z "${value}" ]]; then
    echo "ERROR: Required secret ${var} missing from Vault payload." >&2
    exit 1
  fi
  export "${var}=${value}"
done

for var in "${optional_vars[@]}"; do
  value="$(printf '%s' "${json}" | jq -r --arg k "${var}" '.[$k] // empty')"
  if [[ -n "${value}" ]]; then
    export "${var}=${value}"
    echo "Loaded optional secret: ${var}"
  fi
done

echo "All required Claude secrets loaded from Supabase Vault."
```

Make executable:

```bash
chmod +x ./scripts/claude/load_secrets_remote.sh
```

---

## 5. Agent Runtime Contract

Any Claude-compatible agent or tool **must** follow this sequence:

1. **Load secrets** (local or remote):
   - Local macOS: `source ./scripts/claude/load_secrets_local.sh`
   - Remote/CI: `source ./scripts/claude/load_secrets_remote.sh`

2. **Verify env** (example gate):
   ```bash
   : "${CLAUDE_API_KEY:?CLAUDE_API_KEY is required but not set}"
   : "${SUPABASE_URL:?SUPABASE_URL is required but not set}"
   : "${SUPABASE_ANON_KEY:?SUPABASE_ANON_KEY is required but not set}"
   : "${SUPABASE_SERVICE_ROLE_KEY:?SUPABASE_SERVICE_ROLE_KEY is required but not set}"
   ```

3. **Run agent / tool** (Claude, Supabase, GitHub, etc.) only after step 2 passes.

No agent should attempt to read secrets directly from Keychain or Vault; they operate **only** on environment variables loaded by the scripts above.

---

## 6. Integration with Claude Code / Agent Runners

Example wrapper script for an agent run:

`./scripts/claude/run_agent.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-local}"  # "local" or "remote"

if [[ "${MODE}" == "local" ]]; then
  # macOS development
  source ./scripts/claude/load_secrets_local.sh
else
  # CI / remote
  source ./scripts/claude/load_secrets_remote.sh
fi

# Guardrails: ensure critical vars are present
: "${CLAUDE_API_KEY:?CLAUDE_API_KEY is required}"
: "${SUPABASE_URL:?SUPABASE_URL is required}"
: "${SUPABASE_ANON_KEY:?SUPABASE_ANON_KEY is required}"

# Example: run a Claude task file or agent CLI
# Replace with the actual entrypoint you use.
claude-code run ./spec/agent_task.yaml
```

Usage:

```bash
# Local dev
./scripts/claude/run_agent.sh local

# CI / remote
./scripts/claude/run_agent.sh remote
```

---

## 7. Rotation & Auditing (High-Level)

- **Rotation:**
  - Update Keychain entries via `security add-generic-password -U ...` (same commands as initial set).
  - Update Supabase Vault via the configured process (Edge Function, SQL, or CLI).

- **Audit:**
  - Search repo to ensure secrets are **not** in Git:
    ```bash
    git grep -n "sk-" || true
    git grep -n "SUPABASE_SERVICE_ROLE_KEY" || true
    ```

- **Policy:**
  - Any new tool/agent that introduces a secret **must**:
    1. Add it to the table in §2.
    2. Add it to **both** loader scripts.
    3. Document usage in its own module README if needed.

---

This file (`CLAUDE.md`) is the canonical reference for Claude-related secret handling. Any divergence in other docs or scripts should be treated as a bug and corrected to match this specification.
