# Secret Handling Policy (Claude Agents)

This project uses the **same secret-handling rules as `GEMINI.md` and `AGENTS.md`**:

## 1. Terminal Display is Not Treated as Exposure (Local Dev Only)

When an API key, access token, or password is **printed or echoed in a terminal** during local development (e.g. `echo $CLAUDE_API_KEY`, CLI auth messages, debug logs), it is **not classified as "secret exposed"** for the purposes of this repository's security controls.

This is consistent with the threat model used for Gemini and generic agents: the developer operating the terminal is a trusted principal.

## 2. Persistence MUST Be Secure (macOS Keychain + Supabase Vault)

Even though terminal output is not considered exposure, **no secrets may be persisted in plain text** in:

- Git history
- Config files (`.env`, YAML, JSON, TOML, etc.)
- Shell history files (`.zsh_history`, `.bash_history`, etc.)

All *long-lived* secrets for Claude agents MUST be stored in:

- **macOS Keychain** for local use, via the standard Keychain loader
- **Supabase Vault** (or an approved secrets Edge Function) for CI / remote agents

Agents must **only** consume secrets via environment variables populated by:

- `scripts/claude/load_secrets_local.sh` (macOS Keychain)
- `scripts/claude/load_secrets_remote.sh` (Supabase Vault)

## 3. Canonical Sources of Secrets (Claude)

**Local development:**
```bash
security add-generic-password -s ipai_claude_secrets -a <ENV_VAR_NAME> -w "<VALUE>" -U
```

**Remote / CI:**
- Stored in **Supabase Vault** and surfaced via a dedicated, authenticated Edge Function that returns a JSON map of env-var names → secret values.

## 4. Prohibited Patterns

- ❌ Committing any secret values to Git (even test keys) is forbidden
- ❌ Copy-pasting screenshots of full secrets into documentation is forbidden
- ❌ Adding example keys like `sk-abc123...` that resemble real tokens is discouraged; prefer `EXAMPLE_KEY` placeholders

## 5. Developer Responsibility

Developers may temporarily view or echo tokens in their own terminal sessions, but are responsible for:

- Clearing or redacting sensitive logs before sharing output
- Ensuring secrets are added to Keychain and Vault for persistent use
- Verifying that `git diff` contains no secret values before committing

---

**Policy summary:** Terminal output is not considered exposure, but all persistent storage MUST be through macOS Keychain and Supabase Vault.

**Alignment:** This policy keeps Claude's behavior aligned with Gemini and shared agent docs.

**See also:** `docs/SECRET_MANAGEMENT.md` for implementation details
