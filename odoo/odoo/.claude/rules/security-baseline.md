# Security Baseline

> Full secrets policy, GitHub security integration, and allowed tools list.

---

## Secrets & Tokens Policy (Non-Negotiable)

**Core Directive**: Never ask users to expose secrets in chat. Assume secret management infrastructure exists.

### 2.1 Never Request Raw Secrets

You MUST NOT ask users to paste:
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ACCESS_TOKEN`
- `GITHUB_TOKEN`, `GITHUB_PERSONAL_ACCESS_TOKEN`
- `MAILGUN_API_KEY`, SMTP passwords
- Any database passwords, connection strings, API keys, or client secrets

You MUST NOT suggest putting secrets directly into `.py`, `.ts`, `.json`, `.yml` checked into git.

### 2.2 How to Handle Missing Secrets

Instead of asking for secret values:

**Correct approach**:
```
Missing required environment variable OPENAI_API_KEY.
Expected to be set in runtime/CI secrets.
Action: add it to your secret store and redeploy.
```

**Wrong approach**:
- "Please paste your API key here..."
- "Enter your token in the following field..."
- "What is your OPENAI_API_KEY?"

### 2.3 Secret Storage Conventions

Assume secrets live in ONE of these layers:

**Local dev**:
- `.env` / `.env.local` / `.env.prod` (gitignored)

**CI/CD**:
- GitHub Actions secrets, n8n credentials, Azure Key Vault, Codespaces secrets

**Runtime**:
- Environment variables injected by Docker / Compose / Supabase / Azure / n8n

### 2.4 Code Patterns

Always design for env-driven configuration:

```python
# Correct
import os
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not set in environment")

# Wrong
api_key = "sk-hardcoded..."  # Never do this
```

### 2.5 Token Chatter - Forbidden

Never add filler like:
- "Make sure your token is safe"
- "Never commit your API keys"
- "Ensure your credentials are secure"

Security guidance should be **implicit in design** (env vars, secrets) and **short and targeted** when necessary.

### 2.6 Violation Examples

**Hard Violations** (never do):
1. Asking user to paste any secret/token/password
2. Hard-coding realistic secret keys into generated source
3. Logging or echoing secrets in debug output, evidence docs, CI logs
4. Repeatedly warning about "keep your keys safe" instead of assuming secret management

**If a behavior requires a violation**: Fail fast with precise error, design code so config can be provided outside chat.

---

## GitHub Security Integration (GHAS)

### GitHub Plan: Enterprise (Solo Developer — Owner/Admin/Member)

Single seat, all roles: owner + admin + billing manager + developer.

| Feature | Status |
|---------|--------|
| Protected branches | Active |
| Required status checks | Active |
| CODEOWNERS | Active |
| Secret scanning (GHAS) | Active |
| Code scanning (GHAS) | Active |
| Dependency review | Active |
| SAML SSO | Active (Keycloak) |
| Actions minutes | 50,000/mo |
| Audit log API | Active |
| Copilot Enterprise (SWE agent) | Active |

Self-hosted security tooling (GitLeaks, Semgrep, Trivy) supplements GHAS as defense-in-depth.

### Self-Hosted Security Pipeline

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]
jobs:
  secrets:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: gitleaks/gitleaks-action@v2

  sast:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - uses: returntocorp/semgrep-action@v1
        with:
          config: p/owasp-top-ten p/python

  deps:
    runs-on: self-hosted
    steps:
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
```

---

## Allowed Tools (Safety)

Claude Code is restricted to these tools (see `.claude/settings.json`):

```json
{
  "allowedTools": [
    "Edit", "Read", "Write", "Glob", "Grep",
    "Bash(git status)", "Bash(git diff*)", "Bash(git add*)",
    "Bash(git commit*)", "Bash(git push*)", "Bash(git log*)",
    "Bash(git branch*)", "Bash(gh *)",
    "Bash(npm run lint*)", "Bash(npm run typecheck*)",
    "Bash(npm run test*)", "Bash(npm run build*)",
    "Bash(pnpm -s lint*)", "Bash(pnpm -s typecheck*)",
    "Bash(pnpm -s test*)", "Bash(pnpm -s build*)",
    "Bash(python3 -m py_compile*)",
    "Bash(black --check*)", "Bash(black *)",
    "Bash(isort --check*)", "Bash(isort *)", "Bash(flake8*)",
    "Bash(./scripts/repo_health.sh)",
    "Bash(./scripts/spec_validate.sh)",
    "Bash(./scripts/verify.sh)",
    "Bash(./scripts/ci_local.sh*)",
    "Bash(./scripts/ci/*)"
  ]
}
```

---

*Last updated: 2026-03-16*
