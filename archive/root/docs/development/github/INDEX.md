# GitHub Docs Index — Insightpulseai/odoo

> Curated reference: GitHub documentation pages mapped to concrete repo actions.
> Generated: 2026-03-02 | Updated: 2026-03-02 (added Authentication, Security/secrets, GitHub Apps, REST API, GraphQL API, Webhooks security) | Source: GitHub official docs
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
| **Repositories** | Dependabot options reference | <https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference> | Automated dependency security updates via PR. For Odoo 18 CE + OCA + pnpm monorepo: covers Python (`pip`), Node (`npm`), and GitHub Actions workflow action refs. | Create `.github/dependabot.yml` with `pip` (Odoo deps), `npm` (pnpm workspace apps), `github-actions` (pin all `uses: actions/xyz@v4`). Schedule: weekly. Assign to `@ipai/platform-team`. | `.github/dependabot.yml` |
| **Repositories** | Automatically generated release notes | <https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes> | GitHub generates changelogs from merged PR titles + labels when creating releases. Categorize by label: `feature`, `fix`, `security`, `chore`, `breaking`. Attach evidence logs, Docker image digests. | Create `.github/release.yml` with label-to-category mapping. On each deploy: `gh release create v<YYYY.M.N> --generate-notes --title "..."`. Reference `web/docs/evidence/<stamp>/deploy/` in body. | `.github/release.yml` |
| **Pull Requests** | About pull requests | <https://docs.github.com/en/pull-requests> | Canonical reference for PR lifecycle: draft → review → approval → merge. Governs the full PR-only workflow enforced by branch protection. | Read the sub-rows below; enforce PR-only policy in branch protection + rulesets. | Repository Settings |
| **Pull Requests** | Managing a merge queue | <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue> | Merge queue serializes merges to prevent race conditions and broken `main`. PRs pass all checks independently, then queue tests them as a group before applying. Critical when 153 workflows run in parallel. | Enable "Require merge queue" in branch protection rule for `main`. Add `merge_group` trigger to all critical CI workflows so queue tests batched PRs as a unit before merge. | `on: merge_group` in workflow YAML |
| **Pull Requests** | Creating a pull request template | <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests> | PR templates auto-populate description fields, guiding contributors to include spec bundle reference, CI evidence, secrets checklist, and rollback steps — enforcing the output contract. | Create `.github/pull_request_template.md` with sections: Change type, Spec bundle ref, Evidence log path, CI checklist, Secrets sign-off, Rollback strategy. | `.github/pull_request_template.md` |
| **Pull Requests** | Automatically merging a pull request | <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request> | Auto-merge allows PRs to self-merge once all reviews and CI gates pass. Reduces bottleneck of waiting for human button press after all checks are green. | Enable in Settings → Pull Requests → "Allow auto-merge". Use `gh pr merge --auto --squash` in CI automation or instruct contributors to click "Enable auto-merge" on ready PRs. Pair with merge queue. | Settings → Pull Requests |
| **Pull Requests** | Changing the stage of a pull request (Draft PRs) | <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/changing-the-stage-of-a-pull-request> | Draft PRs signal work-in-progress: merging is blocked even if all checks pass, CODEOWNERS review requests are suppressed, and the PR is visually marked as incomplete. Reduces reviewer noise on in-flight work. | Use `gh pr create --draft` for all WIP branches. Convert to ready with `gh pr ready`. Enforce convention: no non-draft PR should be opened without at least a test plan. | `gh pr create --draft`; PR page → "Ready for review" |
| **Pull Requests** | About merge methods | <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github> | Three strategies — merge commit (full history), squash (all commits → 1), rebase (linear, no merge commit). For a 43-module ERP monorepo, **squash** keeps `main` history readable; **rebase** gives linear graph; disabling merge commits enforces one consistent strategy. | Settings → Pull Requests → uncheck "Allow merge commits", enable "Allow squash merging" + "Default to PR title" for clean changelog. Enforce in branch protection: "Require linear history" disables merge commits entirely. | Settings → Pull Requests → merge strategy checkboxes |
| **Pull Requests** | Push rulesets (block secrets at push time) | <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets> | Push rulesets block commits before they reach a PR — catching secrets, large files, or forbidden paths at the earliest possible point. Complements branch protection (which only gates merge) with push-time enforcement across all branches. | Create push ruleset: Settings → Rules → New ruleset → "Push" type. Block file patterns: `*.env*`, `*.key`, `secrets/**`. Block files >10 MB. Enable "Restrict file paths" for `supabase/migrations/**` (require deliberate override). | Settings → Rules → Rulesets → Push type |
| **Integrations** | About integrations | <https://docs.github.com/en/integrations> | Three integration types: **GitHub Apps** (preferred — fine-grained permissions, bot identity, installable on org), **OAuth Apps** (user-level auth, broader scopes), **Webhooks** (event push to external URL). Choose GitHub App for any new automation. | All new integrations use GitHub App format. Existing: `ipai-integrations` App (webhook handler in `supabase/functions/ops-github-webhook-ingest/`). OAuth: avoid for new integrations. Document in `ssot/integrations/github_apps.yaml`. | `ssot/integrations/github_apps.yaml` |
| **Integrations** | Use GitHub in Slack | <https://docs.github.com/en/integrations/how-tos/slack/use-github-in-slack> | GitHub Slack app subscribes Slack channels to repo events (PR opens/closes, issue opens, CI failures). `/github subscribe Insightpulseai/odoo` enables notifications. `/github open`, `/github close`, `/github reopen` manage issues from Slack. | Install GitHub Slack app. In `#devops` channel: `/github subscribe Insightpulseai/odoo reviews comments`. In `#ci-alerts` channel: `/github subscribe Insightpulseai/odoo workflows:failure`. Document in `docs/runbooks/SLACK_INTEGRATION.md`. | Slack workspace admin → GitHub app |
| **Packages** | Working with the Container Registry | <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry> | GHCR hosts Docker images for Odoo CE (`ghcr.io/jgtolentino/odoo`), Superset (`ghcr.io/jgtolentino/ipai-superset`), devcontainer (`ghcr.io/jgtolentino/odoo-devcontainer`). GITHUB_TOKEN needs `packages: write` to push; `packages: read` to pull. | Add `permissions: packages: write` to every workflow job that pushes images (fixed in `insightpulse-cicd.yml` this session). Add `LABEL org.opencontainers.image.source` to all Dockerfiles for GHCR auto-linking (fixed in `docker/odoo/Dockerfile`). | `permissions: packages: write` in workflow YAML; `LABEL` in Dockerfile |
| **Webhooks** | About webhooks | <https://docs.github.com/en/webhooks> | GitHub sends HMAC-SHA256 signed POST to registered URL on events. Handler must: verify `X-Hub-Signature-256` with constant-time compare, handle `ping` event (sent on registration), deduplicate by `X-GitHub-Delivery`. | Webhook handler at `supabase/functions/ops-github-webhook-ingest/index.ts` — fixed `.on("conflict")` → `.upsert({onConflict})` and added ping handler (this session). Registered under `ipai-integrations` GitHub App. | `supabase/functions/ops-github-webhook-ingest/index.ts` |
| **Copilot** | Use Copilot coding agent | <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent> | Copilot Coding Agent creates PRs autonomously from GitHub Issues, Copilot Chat, or `/agent` CLI commands. It analyzes the issue, generates code, runs tests, and opens a PR for human review. Use `@copilot` in PR comments to request modifications. | Coding Agent is GitHub Copilot Enterprise feature. When enabled: annotate issues with `copilot:task` label. Agent respects CODEOWNERS assignments in generated PRs. Monitor via `agent-ssot-check.yml` workflow. All agent-created PRs still require human review (existing branch protection applies). | GitHub Copilot Enterprise settings |
| **Authentication** | About authentication | <https://docs.github.com/en/authentication> | Umbrella for all auth mechanisms: passwords, 2FA, passkeys, SSH keys, PATs (classic vs fine-grained), GitHub Apps tokens, OIDC. Each has distinct scope, lifetime, and audit properties — wrong choice is the most common source of CI/CD credential sprawl. | Token hierarchy for new automation: GitHub Apps (installation token) > Fine-Grained PAT > Classic PAT. Enable 2FA org-wide. Use `ssot/secrets/registry.yaml` to track all token names and approved stores. | Settings → Password and authentication; `ssot/secrets/registry.yaml` |
| **Authentication** | Connecting to GitHub with SSH | <https://docs.github.com/en/authentication/connecting-to-github-with-ssh> | SSH keys are required for Git operations in CI/CD. Covers generating ED25519 keys, adding to GitHub account, ssh-agent config, and testing the connection. Supersedes RSA 4096-bit for new setups. | Generate: `ssh-keygen -t ed25519 -C "email"`. Add public key to Settings → SSH and GPG keys. Test: `ssh -T git@github.com`. Add `~/.ssh/config` entry on macOS with `UseKeychain yes`. | `~/.ssh/id_ed25519`; `~/.ssh/config` |
| **Authentication** | Deploy keys | <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys> | Deploy keys are repo-scoped SSH keys for CI/CD automation — they survive contributor removal and isolate access to a single repo. Used in `insightpulse-cicd.yml` for `SSH_PRIVATE_KEY` → server deployment. Read-only by default; enable write for push. | Generate keypair per deployment target. Store private key in GitHub Actions secret (`SSH_PRIVATE_KEY`). Register public key in Repo Settings → Deploy keys. Run `ssh-keyscan $SSH_HOST >> ~/.ssh/known_hosts` in workflows to avoid host-key prompts. | Repo Settings → Deploy keys; GitHub Actions secret `SSH_PRIVATE_KEY` |
| **Authentication** | Personal access tokens | <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens> | Fine-grained PATs (preferred) scope to specific repos + granular permissions with mandatory expiry (max 1 year). Classic PATs (legacy) are broad and indefinite — avoid for new automation. GITHUB_TOKEN in Actions is auto-issued per-run and should be preferred when workflows don't need cross-repo access. | Audit existing classic PATs in Settings → Developer settings → Personal access tokens → Tokens (classic). Migrate CI/CD tokens to fine-grained or GitHub App installation tokens. Set org PAT policy to require fine-grained only. | Settings → Developer settings → Personal access tokens; Org Settings → Security → PAT policies |
| **Authentication** | GitHub Actions OIDC | <https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect> | OIDC tokens are short-lived (~15 min), single-use JWTs issued by GitHub Actions — eliminate stored credentials entirely for cloud-native CI/CD. Cloud providers (AWS, GCP, Azure, DO) can trust GitHub's OIDC issuer to grant access without stored secrets. | Add `permissions: id-token: write` to workflow jobs that need OIDC. Use cloud provider trust policies to validate `sub` claim (e.g. `repo:Insightpulseai/odoo:ref:refs/heads/main`). No secrets to rotate. Audit via `actions` audit log events. | `permissions: id-token: write` in workflow YAML |
| **Authentication** | Org auth enforcement | <https://docs.github.com/en/organizations/keeping-your-organization-secure> | Organization-level controls: require 2FA for all members, enforce SAML SSO (Enterprise), restrict PAT types, configure IP allowlists, review OAuth app access. Together these form a layered defence reducing insider and credential-theft risk. | Enable 2FA requirement: Org Settings → Security → Two-factor authentication. Set PAT policy to fine-grained only. Review OAuth apps quarterly. Export audit log for compliance. For GitHub Enterprise: configure SAML SSO IdP. | Org Settings → Security |
| **Enterprise / Billing** | Set up VS subscription with GitHub Enterprise | <https://docs.github.com/en/enterprise-cloud@latest/billing/how-tos/set-up-payment/set-up-vs-subscription> | Microsoft Visual Studio subscriptions can bundle GitHub Enterprise Cloud seats. Relevant if the org moves from Team tier to Enterprise Cloud — unlocks SAML SSO, IP allowlists, audit log streaming, and OIDC for all members. Seat assignment is managed via Microsoft admin portal + GitHub org invite reconciliation. | [MANUAL_REQUIRED] Assign VS licenses in Microsoft admin portal → invite subscribers to `Insightpulseai` org → reconcile accounts. Document seat count and renewal date in `ssot/billing/github.yaml` (to be created). | GitHub Enterprise org licensing page + Visual Studio admin portal |
| **Security** | Storing secrets safely | <https://docs.github.com/en/get-started/learning-to-code/storing-your-secrets-safely> | Covers risk of hardcoded secrets in git, principle of least privilege, env-var injection pattern, and GitHub Push Protection / Secret Scanning. Directly maps to this repo's SSOT secrets model — never commit values, only reference names from `ssot/secrets/registry.yaml`. | Verify: `gh api repos/Insightpulseai/odoo --jq '.security_and_analysis.secret_scanning_push_protection.status'` → expect `"enabled"`. `[MANUAL_REQUIRED]` if not enabled — tracked as convergence finding `github_push_protection_enabled` in `ssot/maintenance/convergence.yaml`. All CI secrets via `${{ secrets.NAME }}` — never `echo ${{ secrets.NAME }}`. | `ssot/secrets/registry.yaml`; `ssot/maintenance/convergence.yaml` |
| **GitHub Apps** | GitHub Apps — installation tokens & bot identity | <https://docs.github.com/en/enterprise-cloud@latest/apps> | GitHub Apps authenticate with short-lived installation tokens (~1 hr) and have fine-grained, per-repo permissions — no user credential dependency. Distinct from OAuth Apps (user-scoped, long-lived) and classic PATs (broad, no granularity). The `pulser-hub` and `ipai-integrations` apps in this repo are GitHub App format. | All new automation uses GitHub Apps, not OAuth Apps or PATs. Provision `ipai-integrations` via `scripts/github/create-app-from-manifest.sh`. Private key stored in Supabase Vault; webhook secret in `ssot/secrets/registry.yaml` (names only). | `ssot/integrations/github_apps.yaml`; `infra/github/apps/` |
| **APIs** | REST API versioning (2022-11-28) | <https://docs.github.com/en/enterprise-cloud@latest/rest?apiVersion=2022-11-28> | Versioned REST API (`Accept: application/vnd.github.2022-11-28+json`) prevents breaking changes across GitHub releases. PAT rate limit: 5,000 req/hr; unauthenticated: 60 req/hr. Endpoints cover Actions (trigger workflows, download artifacts), Packages (GHCR), Pull Requests, Issues, Webhooks. Pagination via `Link` header; conditional requests via `ETag`. | Prefix all `gh api` calls with `--header "X-GitHub-Api-Version: 2022-11-28"`. In automation scripts, check `X-RateLimit-Remaining` header before bulk calls. CI credential: `GITHUB_TOKEN` (Actions-issued) is sufficient for most endpoints; cross-repo ops need fine-grained PAT. | `Accept: application/vnd.github.2022-11-28+json` header; `scripts/automations/` |
| **APIs** | GraphQL API — nested queries, point-based limits | <https://docs.github.com/en/enterprise-cloud@latest/graphql> | Single endpoint `https://api.github.com/graphql`. Point-based rate limits (5,000 pts/hr) — one query can fetch PR + checks + reviews + comments in one round-trip vs 5+ REST calls. Queries: `repository`, `pullRequest`, `search`; mutations: `createIssue`, `addPullRequestReview`. Pagination via `first:`/`after:` cursors. | Use GraphQL in CI workflows for PR enrichment (fetch all check-run statuses + review counts in one call instead of chaining REST calls). Useful for automated merge gating and Supabase audit log population (`ops.github_webhook_deliveries`). Authentication: `Authorization: Bearer $GITHUB_TOKEN`. | `https://api.github.com/graphql`; `Authorization: Bearer` header |
| **Webhooks** | Securing webhooks — HMAC-SHA256 + delivery retries | <https://docs.github.com/en/enterprise-cloud@latest/webhooks/securing-your-webhooks> | All webhook payloads are signed with `X-Hub-Signature-256: sha256=<HMAC>`. Receivers must recompute the hash using the webhook secret + raw request body (UTF-8) and compare with **timing-safe comparison** (e.g. Node `crypto.timingSafeEqual`) to prevent timing attacks. Failed deliveries retry with exponential backoff; manual redelivery available via API. | `supabase/functions/ops-github-webhook-ingest/index.ts` must verify `X-Hub-Signature-256` with constant-time compare. Store webhook secret in Supabase Vault (key name in `ssot/secrets/registry.yaml`). Add `webhook-health-check.yml` CI guard that pings the handler endpoint. | `supabase/functions/ops-github-webhook-ingest/index.ts`; Supabase Vault |

---

## Quick reference: highest-leverage settings per file

### `.github/CODEOWNERS`

```text
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

### Main branch protection — recommended settings for 153-workflow monorepo

```text
Settings → Branches → Branch protection rule for "main":
  ✅ Require pull request before merging
  ✅ Require 1 approval (2 for breaking/* labels)
  ✅ Dismiss stale reviews when new commits pushed
  ✅ Require review from Code Owners
  ✅ Require status checks to pass (link all 153 workflow jobs)
  ✅ Require branches to be up to date before merging
  ✅ Require merge queue
  ✅ Include administrators (no bypass)

Settings → Pull Requests:
  ✅ Allow auto-merge
  ✅ Allow squash merging (default: PR title)
  ❌ Allow merge commits (disable for clean history)
  ❌ Allow rebase merging (optional; enable if contributors prefer linear)

Settings → Rules → New push ruleset (all branches):
  Block file patterns: *.env*, *.key, *.pem, secrets/**, credentials/**
  Block files > 10 MB
```

### `~/.ssh/config` (macOS — ED25519 + Keychain)

```text
Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
```

**Linux** (omit `UseKeychain yes`):

```text
Host github.com
  AddKeysToAgent yes
  IdentityFile ~/.ssh/id_ed25519
```

**Multiple deploy keys on one server** (one entry per repo):

```text
Host github-deploy-odoo
  HostName github.com
  User git
  IdentityFile ~/.ssh/deploy_odoo
  IdentitiesOnly yes
```
Then clone as: `git clone git@github-deploy-odoo:Insightpulseai/odoo.git`

### SSH new key setup (one-time)

```bash
# Generate (ED25519 preferred)
ssh-keygen -t ed25519 -C "your@email.com"

# Add to agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519          # Linux
ssh-add --apple-use-keychain ~/.ssh/id_ed25519  # macOS

# Test connection
ssh -T git@github.com
# Expected: "Hi USERNAME! You've successfully authenticated..."

# Prevent host-key prompts in CI
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

### GitHub Actions workflow: SSH deploy key pattern

```yaml
- name: Setup deploy key
  env:
    SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
    SSH_HOST: ${{ secrets.SSH_HOST }}
  run: |
    mkdir -p ~/.ssh
    echo "$SSH_PRIVATE_KEY" > ~/.ssh/deploy_key
    chmod 600 ~/.ssh/deploy_key
    ssh-keyscan -H "$SSH_HOST" >> ~/.ssh/known_hosts 2>/dev/null
```

### GitHub Actions OIDC (keyless, no stored secrets)

```yaml
permissions:
  id-token: write   # required for OIDC
  contents: read

steps:
  - name: Configure cloud credentials via OIDC
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-actions
      aws-region: ap-southeast-1
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
| `ssot/secrets/registry.yaml` | Secret names, approved stores, consumers (no values) |
| GitHub Actions secret `SSH_PRIVATE_KEY` | Deploy key private half — stored in repo secrets |
| GitHub Actions secret `SSH_HOST` / `SSH_USER` | Deployment target — DigitalOcean droplet 178.128.112.214 |

---

## See also

- [`docs/dev/vscode/INDEX.md`](../vscode/INDEX.md) — VS Code tooling reference
- [`docs/dev/vercel/INDEX.md`](../vercel/INDEX.md) — Vercel documentation reference
- [`docs/dev/odoo/DOCS_INDEX.md`](../odoo/DOCS_INDEX.md) — Odoo documentation reference
- [`ssot/integrations/github_apps.yaml`](../../../ssot/integrations/github_apps.yaml) — Machine-readable integration SSOT
