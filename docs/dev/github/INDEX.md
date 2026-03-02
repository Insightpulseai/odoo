# GitHub Docs Index — Insightpulseai/odoo

> Curated reference: GitHub documentation pages mapped to concrete repo actions.
> Generated: 2026-03-02 | Source: GitHub official docs
> Update: edit this file + `ssot/devex/github.yaml` together.

---

## Index

| Area | Doc page | URL | Why it matters | Repo action | Key setting / file |
|------|----------|-----|----------------|-------------|-------------------|
| **Account Types** | Types of GitHub accounts | <https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts> | Insightpulseai/odoo lives under an **Organization** account (not personal). Org accounts have role-based teams, org-level secrets, audit logs, and branch protection enforcement across all repos — critical for 43-module ERP monorepo with 10+ contributors. | Confirm repo is under `Insightpulseai` org (not `jgtolentino` personal namespace). Org-level secrets (CI/CD creds) are available to all repo workflows without per-repo duplication. | Organization Settings |
| **Repositories** | About repositories | <https://docs.github.com/en/repositories> | Canonical reference for repository-level features: visibility, branch protection, rulesets, CODEOWNERS, Dependabot, releases, topics. Each feature has a repo-action consequence for a CI-heavy monorepo. | See sub-rows below. | Repository Settings |
| **Repositories** | Branch protection rules | <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule> | Block direct pushes to `main`; require PRs, CI status checks, and peer reviews before merge. Core enforcement for PR-only workflow alongside 153 GitHub Actions workflows. | Settings → Branches → Add rule for `main`: require 1+ review, require status checks (link to CI job IDs), dismiss stale reviews, disallow force pushes. Upgrade to Rulesets for multi-pattern (`main`, `release/*`). | `settings.branches` |
| **Repositories** | About rulesets | <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets> | Rulesets supersede branch protection rules: multiple rulesets apply simultaneously, extend to tags, support org-level centralization. Recommended for monorepos with multiple branch patterns. | Create rulesets for: `main` (strictest — require review + CI), `release/*` (staging — require CI), push ruleset blocking `*.env*`, `*.key` across all branches. | Settings → Rules → Rulesets |
| **Repositories** | About code owners | <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners> | Auto-assigns reviewers based on file path ownership. For 43 ipai modules, maps each module area to responsible team — eliminates manual reviewer selection and enforces domain expertise in PRs. | Create `.github/CODEOWNERS` mapping: `addons/ipai/ipai_finance_*/ @ipai/finance-team`, `addons/oca/ @ipai/oca-maintainers`, `.github/workflows/ @ipai/devops`. Enable "Require review from Code Owners" in branch protection. | `.github/CODEOWNERS` |
| **Repositories** | Dependabot options reference | <https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference> | Automated dependency security updates via PR. For Odoo 19 CE + OCA + pnpm monorepo: covers Python (`pip`), Node (`npm`), and GitHub Actions workflow action refs. | Create `.github/dependabot.yml` with `pip` (Odoo deps), `npm` (pnpm workspace apps), `github-actions` (pin all `uses: actions/xyz@v4`). Schedule: weekly. Assign to `@ipai/platform-team`. | `.github/dependabot.yml` |
| **Repositories** | Automatically generated release notes | <https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes> | GitHub generates changelogs from merged PR titles + labels when creating releases. Categorize by label: `feature`, `fix`, `security`, `chore`, `breaking`. Attach evidence logs, Docker image digests. | Create `.github/release.yml` with label-to-category mapping. On each deploy: `gh release create v<YYYY.M.N> --generate-notes --title "..."`. Reference `web/docs/evidence/<stamp>/deploy/` in body. | `.github/release.yml` |
| **Pull Requests** | About pull requests | <https://docs.github.com/en/pull-requests> | Canonical reference for PR lifecycle: draft → review → approval → merge. Governs the full PR-only workflow enforced by branch protection. | Read the sub-rows below; enforce PR-only policy in branch protection + rulesets. | Repository Settings |
| **Pull Requests** | Managing a merge queue | <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue> | Merge queue serializes merges to prevent race conditions and broken `main`. PRs pass all checks independently, then queue tests them as a group before applying. Critical when 153 workflows run in parallel. | Enable "Require merge queue" in branch protection rule for `main`. Add `merge_group` trigger to all critical CI workflows so queue tests batched PRs as a unit before merge. | `on: merge_group` in workflow YAML |
| **Pull Requests** | Creating a pull request template | <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests> | PR templates auto-populate description fields, guiding contributors to include spec bundle reference, CI evidence, secrets checklist, and rollback steps — enforcing the output contract. | Create `.github/pull_request_template.md` with sections: Change type, Spec bundle ref, Evidence log path, CI checklist, Secrets sign-off, Rollback strategy. | `.github/pull_request_template.md` |
| **Pull Requests** | Automatically merging a pull request | <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request> | Auto-merge allows PRs to self-merge once all reviews and CI gates pass. Reduces bottleneck of waiting for human button press after all checks are green. | Enable in Settings → Pull Requests → "Allow auto-merge". Use `gh pr merge --auto --squash` in CI automation or instruct contributors to click "Enable auto-merge" on ready PRs. Pair with merge queue. | Settings → Pull Requests |
| **Integrations** | About integrations | <https://docs.github.com/en/integrations> | Three integration types: **GitHub Apps** (preferred — fine-grained permissions, bot identity, installable on org), **OAuth Apps** (user-level auth, broader scopes), **Webhooks** (event push to external URL). Choose GitHub App for any new automation. | All new integrations use GitHub App format. Existing: `ipai-integrations` App (webhook handler in `supabase/functions/ops-github-webhook-ingest/`). OAuth: avoid for new integrations. Document in `ssot/integrations/github_apps.yaml`. | `ssot/integrations/github_apps.yaml` |
| **Integrations** | Use GitHub in Slack | <https://docs.github.com/en/integrations/how-tos/slack/use-github-in-slack> | GitHub Slack app subscribes Slack channels to repo events (PR opens/closes, issue opens, CI failures). `/github subscribe Insightpulseai/odoo` enables notifications. `/github open`, `/github close`, `/github reopen` manage issues from Slack. | Install GitHub Slack app. In `#devops` channel: `/github subscribe Insightpulseai/odoo reviews comments`. In `#ci-alerts` channel: `/github subscribe Insightpulseai/odoo workflows:failure`. Document in `docs/runbooks/SLACK_INTEGRATION.md`. | Slack workspace admin → GitHub app |
| **Packages** | Working with the Container Registry | <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry> | GHCR hosts Docker images for Odoo CE (`ghcr.io/jgtolentino/odoo`), Superset (`ghcr.io/jgtolentino/ipai-superset`), devcontainer (`ghcr.io/jgtolentino/odoo-devcontainer`). GITHUB_TOKEN needs `packages: write` to push; `packages: read` to pull. | Add `permissions: packages: write` to every workflow job that pushes images (fixed in `insightpulse-cicd.yml` this session). Add `LABEL org.opencontainers.image.source` to all Dockerfiles for GHCR auto-linking (fixed in `docker/odoo/Dockerfile`). | `permissions: packages: write` in workflow YAML; `LABEL` in Dockerfile |
| **Webhooks** | About webhooks | <https://docs.github.com/en/webhooks> | GitHub sends HMAC-SHA256 signed POST to registered URL on events. Handler must: verify `X-Hub-Signature-256` with constant-time compare, handle `ping` event (sent on registration), deduplicate by `X-GitHub-Delivery`. | Webhook handler at `supabase/functions/ops-github-webhook-ingest/index.ts` — fixed `.on("conflict")` → `.upsert({onConflict})` and added ping handler (this session). Registered under `ipai-integrations` GitHub App. | `supabase/functions/ops-github-webhook-ingest/index.ts` |
| **Copilot** | Use Copilot coding agent | <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent> | Copilot Coding Agent creates PRs autonomously from GitHub Issues, Copilot Chat, or `/agent` CLI commands. It analyzes the issue, generates code, runs tests, and opens a PR for human review. Use `@copilot` in PR comments to request modifications. | Coding Agent is GitHub Copilot Enterprise feature. When enabled: annotate issues with `copilot:task` label. Agent respects CODEOWNERS assignments in generated PRs. Monitor via `agent-ssot-check.yml` workflow. All agent-created PRs still require human review (existing branch protection applies). | GitHub Copilot Enterprise settings |

---

## Quick reference: highest-leverage settings per file

### `.github/CODEOWNERS`

```
# Fallback owner
* @ipai/core

# DevOps owns all workflows
.github/workflows/ @ipai/devops
.github/ @ipai/devops

# Odoo module teams
addons/ipai/ipai_finance_*/ @ipai/finance-team
addons/ipai/ipai_ai_*/ @ipai/ai-team
addons/ipai/ipai_auth_*/ @ipai/platform-team
addons/ipai/ipai_slack_*/ @ipai/platform-team
addons/oca/ @ipai/oca-maintainers

# Infrastructure
infra/ @ipai/devops
ssot/ @ipai/architects
docs/ai/ @ipai/architects
spec/ @ipai/architects
```

### `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
    assignees: [ipai/platform-team]
    labels: [dependencies, python]

  - package-ecosystem: npm
    directory: /web
    schedule:
      interval: weekly
    assignees: [ipai/platform-team]
    labels: [dependencies, node]

  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    assignees: [ipai/devops]
    labels: [dependencies, ci]
```

### `.github/pull_request_template.md`

```markdown
## Description
<!-- What does this PR do? Reference spec bundle if applicable. -->
Spec bundle: `spec/<slug>/prd.md` (link or N/A)

## Type of change
- [ ] feat — new feature
- [ ] fix — bug fix
- [ ] chore — maintenance
- [ ] docs — documentation only
- [ ] breaking — breaks existing behavior

## Evidence
<!-- Required for non-trivial changes. -->
- Evidence log: `web/docs/evidence/<YYYYMMDD-HHMM+0800>/<scope>/logs/`
- CI run: (link to GitHub Actions run)

## Checklist
- [ ] No secrets hardcoded (`ssot/secrets/registry.yaml` updated if new secret)
- [ ] `pre-commit` passes locally
- [ ] Tests added/updated for functional changes
- [ ] `docs/` updated if behavior changed
- [ ] Rollback strategy documented (if DB migration or infra change)

## Rollback
<!-- How to revert if this breaks production. -->
```

### `.github/release.yml` (auto-generated release notes)

```yaml
changelog:
  categories:
    - title: "Breaking Changes"
      labels: [breaking]
    - title: "New Features"
      labels: [feat, feature]
    - title: "Bug Fixes"
      labels: [fix, bugfix]
    - title: "Security"
      labels: [security]
    - title: "Dependencies"
      labels: [dependencies]
    - title: "CI/Infrastructure"
      labels: [ci, chore(ci), chore(deploy)]
    - title: "Documentation"
      labels: [docs]
```

---

## Related files in this repo

| File | Purpose |
|------|---------|
| `ssot/integrations/github_apps.yaml` | GitHub App registrations SSOT |
| `.github/workflows/claude-settings-auth-guard.yml` | Guard against GH_TOKEN 401 regression |
| `.github/workflows/github-auth-surface-guard.yml` | GitHub auth surface governance |
| `.github/workflows/github-apps-ssot-guard.yml` | GitHub App SSOT compliance |
| `scripts/ci/check_claude_settings_auth.py` | Detect/fix bad env keys in settings.json |
| `supabase/functions/ops-github-webhook-ingest/index.ts` | Webhook handler (HMAC-SHA256 + delivery ledger) |
| `docs/runbooks/GITHUB_APP_PROVISIONING.md` | GitHub App setup runbook |

---

## See also

- [`docs/dev/vscode/INDEX.md`](../vscode/INDEX.md) — VS Code tooling reference
- [`docs/dev/odoo/DOCS_INDEX.md`](../odoo/DOCS_INDEX.md) — Odoo documentation reference
- [`ssot/integrations/github_apps.yaml`](../../../ssot/integrations/github_apps.yaml) — Machine-readable integration SSOT
