# Skill: GitHub Integrations — Apps, Actions, Webhooks

## Metadata

| Field | Value |
|-------|-------|
| **id** | `github-integrations` |
| **domain** | `integration` |
| **source** | https://docs.github.com/en/integrations/concepts/about-building-integrations |
| **extracted** | 2026-03-15 |
| **applies_to** | .github, agents, automations |
| **tags** | github, github-apps, actions, webhooks, oauth, integrations |

---

## Integration Types

| Type | Runs Where | Auth Model | Publish to Marketplace | Best For |
|------|-----------|------------|----------------------|----------|
| **GitHub Apps** | App owner's server or user device | Fine-grained permissions, short-lived tokens, installation tokens | Yes | Webhook-driven automation, cross-repo operations |
| **GitHub Actions Workflows** | GitHub-hosted or self-hosted runners | GITHUB_TOKEN (scoped per workflow) | No | CI/CD, event-driven automation |
| **Custom Actions** | Within Actions workflows | Inherits workflow token | Yes | Reusable automation components |
| **OAuth Apps** | External server | Long-lived OAuth tokens | Yes | User-facing apps needing GitHub login (legacy — prefer GitHub Apps) |
| **Webhooks** | Your endpoint receives events | Secret-based HMAC verification | N/A | Event notifications to external systems |

## GitHub Apps vs OAuth Apps

GitHub Apps are **preferred over OAuth Apps** for all new integrations.

| Feature | GitHub Apps | OAuth Apps |
|---------|-----------|------------|
| Token lifetime | Short-lived (1 hour) | Long-lived |
| Permissions | Fine-grained (per endpoint) | Broad scopes |
| Repository access | User controls which repos | All repos in scope |
| Webhook events | Dedicated per app | Per-user subscriptions |
| Rate limits | Higher (5,000/hr per installation) | Lower (5,000/hr per user) |
| Security posture | Better (leaked token = limited blast) | Worse (leaked token = full scope) |

## Custom Action Types

| Type | Platform | Speed | Isolation | Best For |
|------|----------|-------|-----------|----------|
| **JavaScript** | Linux, macOS, Windows | Fast | None (runs on runner) | Cross-platform, simple logic |
| **Docker** | Linux only | Slower (build + pull) | Full container | Dependencies, complex env |
| **Composite** | All platforms | Fast | None | Bundle multiple steps |

### Action Metadata (`action.yml`)

```yaml
name: 'My Custom Action'
description: 'Does something useful'
inputs:
  my-input:
    description: 'Input parameter'
    required: true
    default: 'default-value'
outputs:
  my-output:
    description: 'Output value'
runs:
  using: 'node20'  # or 'docker' or 'composite'
  main: 'dist/index.js'
```

## IPAI GitHub Integration Map

### Current Integrations

| Integration | Type | Purpose | Location |
|------------|------|---------|----------|
| CI/CD workflows | Actions Workflows | Build, test, deploy Odoo | `.github/workflows/` |
| n8n GitHub webhook | Webhook | Git events → n8n routing | `automations/n8n/workflows/github-events-handler.json` |
| GitHub OAuth callback | OAuth flow | n8n OAuth for GitHub API | `automations/n8n/workflows/05-github-oauth-callback.json` |
| `gh-safe` CLI wrapper | Custom Action (shell) | Policy-constrained `gh` commands | `agents/skills/github-cli-safe/bin/gh-safe` |

### Recommended New Integrations

| Integration | Type | Purpose | Priority |
|------------|------|---------|----------|
| **IPAI GitHub App** | GitHub App | Fine-grained access for agent operations (create issues, PRs, reviews) | High |
| **Coding Agent Action** | Custom Action (composite) | Triggered by `agent:coding` label → runs agent → creates PR | High |
| **SRE Issue Creator** | GitHub App webhook | Azure Monitor alert → GitHub issue with structured context | Medium |
| **PR Quality Gate** | Custom Action (JavaScript) | Run eval + lint + security on agent-generated PRs | Medium |
| **Spec-to-Issue** | Custom Action (composite) | Parse spec tasks → create scoped GitHub issues | Medium |

### Why Build a GitHub App (not just Actions)

Current n8n GitHub integration uses **OAuth** (long-lived tokens). Migrating to a **GitHub App** provides:

1. **Short-lived tokens** — auto-rotated, reduced blast radius if leaked
2. **Fine-grained permissions** — only the endpoints the agent needs
3. **Installation-level access** — operates across repos without per-user tokens
4. **Higher rate limits** — 5,000/hr per installation vs per-user
5. **Webhook delivery** — events delivered to app endpoint, not user subscriptions

### GitHub App Setup for IPAI

```
1. Create GitHub App in Insightpulseai org settings
   - Name: ipai-agent-bot
   - Permissions:
     - Issues: Read & Write (create, comment, label)
     - Pull Requests: Read & Write (create, review, merge)
     - Contents: Read & Write (push to branches)
     - Checks: Read & Write (report CI status)
     - Metadata: Read-only
   - Webhook events: issues, pull_request, push, check_run
   - Webhook URL: https://n8n.insightpulseai.com/webhook/github-app

2. Install on Insightpulseai org → select repos: odoo, agents, infra

3. Store credentials in Azure Key Vault:
   - github-app-id
   - github-app-private-key
   - github-app-webhook-secret

4. n8n: Replace OAuth GitHub credential with App installation token
```

### Integration Architecture (Target State)

```
GitHub Events (push, issue, PR, check)
    ↓ Webhook
GitHub App (ipai-agent-bot)
    ↓ Installation token
n8n (https://n8n.insightpulseai.com)
    ├── Route by event type:
    │   ├── issue.labeled "agent:coding" → coding-agent-from-issue workflow
    │   ├── push to main → deploy-azure.yml (GitHub Actions)
    │   ├── check_run.completed → update ops.run_events
    │   └── pull_request.opened → quality gate notification
    ↓
Supabase ops.* (SSOT) ←→ Odoo (SOR)
```

## Webhook Security

```python
import hmac
import hashlib

def verify_github_webhook(payload, signature, secret):
    """Verify GitHub webhook HMAC signature."""
    expected = 'sha256=' + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

Always verify `X-Hub-Signature-256` header. Never trust unverified webhooks.

## Related Skills

- [github-well-architected](../../github-well-architected/SKILL.md) — Org governance, Actions, CI/CD
- [azure-pipelines](../../ci-cd/azure-pipelines/SKILL.md) — When to use ADO vs GitHub Actions
- [agentic-sdlc-msft-pattern](../../sdlc/agentic-sdlc-msft-pattern/SKILL.md) — Full SDLC loop using GitHub issues + PRs
- [coding-agent-from-issue](../../../workflows/coding-agent-from-issue.yaml) — Workflow triggered by GitHub issue
