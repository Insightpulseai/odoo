---
name: CI Workflow Audit
description: Audit GitHub Actions workflows for security, naming, reusability, and alignment with governance rules
---

# CI Workflow Audit Skill

## When to use
When creating, modifying, or reviewing `.github/workflows/*.yml` files.

## Checks

1. **Naming**: kebab-case filename, descriptive `name:` field
2. **Triggers**: appropriate `on:` events (no `workflow_dispatch` without purpose)
3. **Secrets**: use `${{ secrets.* }}` — never hardcoded values
4. **Runners**: use `ubuntu-latest` or GitHub-hosted (no self-hosted unless justified)
5. **Permissions**: explicit `permissions:` block with least-privilege
6. **Pinned actions**: use SHA-pinned `@v4` or `@<sha>` — not floating tags
7. **Reusability**: extract shared logic into reusable workflows under `.github/workflows/`
8. **No deprecated providers**: no Vercel deploy, no DigitalOcean, no Mailgun
9. **Evidence**: workflows that validate should produce artifacts or logs

## Governance rules
- See `.Codex/rules/github-governance.md`
- Branch protection requires status checks before merge
- CODEOWNERS is enforced
