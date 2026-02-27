# Contract: GitHub Copilot Usage & Guardrails

> Cross-domain contract between the Development (H) and Security (G+H) domains.
> SSOT: This file. Enforcement: `.github/workflows/copilot-guardrails.yml`
> Last updated: 2026-02-22

---

## 1. Allowed Usage

| Context | Copilot Allowed? | Notes |
|---------|-----------------|-------|
| General Odoo module development (`addons/ipai/`) | ✅ Yes | Standard code gen |
| Test generation (`tests/`) | ✅ Yes | Encouraged |
| OCA contrib and non-sensitive scripts | ✅ Yes | Review required |
| Database migrations (`supabase/migrations/`) | ⚠️ Review | Human must validate RLS policies |
| Infrastructure as code (`infra/`, `.github/workflows/`) | ⚠️ Review | Security-sensitive; CODEOWNERS required |
| Secrets, credentials, tokens (any path) | ❌ Never | Violates Contract 7 (Secrets) |
| Auth logic (`supabase/functions/*auth*`, `addons/ipai/ipai_auth_*`) | ⚠️ Review | Security team review required |

## 2. PR Disclosure Requirement

PRs where Copilot generated >30% of the diff **should** include this in the PR description:

```
## AI Assistance
- Copilot used for: [brief description]
- Human-reviewed sections: [paths]
- Not AI-generated: [security-critical sections]
```

This is advisory, not enforced by CI. The `copilot-guardrails.yml` workflow checks
for **security patterns** (secrets, unsafe env vars) regardless of AI usage.

## 3. Sensitive Path Rules

CODEOWNERS approval required (regardless of AI usage) for:

```
addons/ipai/ipai_auth_*/
supabase/migrations/
supabase/functions/
.github/workflows/
infra/policy/
config/odoo/
```

These paths have an active CODEOWNERS entry in `.github/CODEOWNERS`.

## 4. Security Constraints

Copilot **must not** be used to generate:
- Passwords, API keys, tokens, secrets of any kind
- Code that bypasses RLS policies
- Code that prints environment variables to logs

The `copilot-guardrails.yml` CI workflow scans every PR diff for:
- Known secret patterns (`password =`, `api_key =`, `token =`, etc.)
- Unsafe env var logging (`print(os.environ`, `console.log(process.env`, etc.)
- Policy file drift (if sensitive policy files change without CODEOWNERS approval)

## 5. Code Review Posture

- All Copilot-assisted security-sensitive code requires **at least 1 human senior reviewer**
- Automated tests must exist or be added for all Copilot-generated business logic
- Copilot suggestions are non-authoritative — the committing developer takes full responsibility

## 6. Enforcement

| Mechanism | Scope |
|-----------|-------|
| `copilot-guardrails.yml` CI workflow | All PRs to `main` |
| CODEOWNERS for sensitive paths | GitHub branch protection |
| Secret Scanning push protection | All branches (see GHAS spec) |
| Monthly audit (PR review sample) | Security team |

## 7. SSOT Drift Rule

Changes to this contract require:
1. PR to `main` with `docs/contracts/GITHUB_COPILOT_CONTRACT.md` in diff
2. CODEOWNERS approval
3. Update `copilot-guardrails.yml` if enforcement logic changes
