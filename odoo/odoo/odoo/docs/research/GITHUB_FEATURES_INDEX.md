# GitHub Features -- Comprehensive Index & IPAI Stack Relevance

**Source URL**: `https://github.com/features`
**Research Date**: 2026-03-07
**Branch**: `claude/review-signavio-url-HffM8`

> GitHub is the world's leading software development platform (150M+ users, 420M+ projects). This index catalogs all products, features, and pricing tiers with IPAI stack relevance mapping.

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Pricing Plans](#2-pricing-plans)
3. [GitHub Copilot](#3-github-copilot)
4. [GitHub Actions](#4-github-actions)
5. [GitHub Codespaces](#5-github-codespaces)
6. [Security & Advanced Security](#6-security--advanced-security)
7. [GitHub Packages](#7-github-packages)
8. [Collaboration Features](#8-collaboration-features)
9. [Enterprise Features](#9-enterprise-features)
10. [GitHub Copilot Plans & Pricing](#10-github-copilot-plans--pricing)
11. [IPAI Stack Usage & Recommendations](#11-ipai-stack-usage--recommendations)

---

## 1. Platform Overview

| Attribute | Value |
|-----------|-------|
| **Users** | 150M+ |
| **Projects** | 420M+ |
| **ROI** | 433% (Forrester study) |
| **Owner** | Microsoft (acquired 2018) |
| **Plans** | Free, Team ($4/user/mo), Enterprise ($21/user/mo) |
| **IPAI Plan** | GitHub Team ($4/user/mo) per CLAUDE.md |

---

## 2. Pricing Plans

| Feature | Free ($0) | Team ($4/user/mo) | Enterprise ($21/user/mo) |
|---------|-----------|-------------------|--------------------------|
| **Public + Private Repos** | Unlimited | Unlimited | Unlimited |
| **Actions Minutes** | 2,000/mo | 3,000/mo | 50,000/mo |
| **Packages Storage** | 500 MB | 2 GB | 50 GB |
| **Protected Branches** | Public only | Yes | Yes |
| **Code Owners** | No | Yes | Yes |
| **Required Reviewers** | No | Yes | Yes |
| **Draft PRs** | No | Yes | Yes |
| **CODEOWNERS** | No | Yes | Yes |
| **SSO/SCIM** | No | No | Yes |
| **Audit Log Streaming** | No | No | Yes |
| **IP Allow List** | No | No | Yes |
| **Advanced Security** | No | Add-on | Included |
| **Self-hosted (GHES)** | No | No | Yes |
| **Support** | Community | Standard | Premium |

### Overage Costs

| Resource | Rate |
|----------|------|
| Actions (Linux) | $0.008/min |
| Actions (Windows) | $0.016/min |
| Actions (macOS) | $0.08/min |
| Packages Storage | $0.008/GB/day |

### IPAI Choice: GitHub Team

Per CLAUDE.md, GitHub Team at $4/user/mo provides everything needed:
- Protected branches, required reviewers, CODEOWNERS, Draft PRs
- 3,000 Actions minutes (supplemented by self-hosted runners on DO)
- Annual savings of ~$6,600/yr vs Enterprise + GHAS

---

## 3. GitHub Copilot

### Overview

GitHub Copilot provides contextualized AI assistance throughout the software development lifecycle: inline suggestions, chat, code review, CLI, coding agents, and Autofix.

### Copilot Products

| Product | Price | Key Capability |
|---------|-------|----------------|
| **Copilot Free** | $0 | 2,000 completions/mo + 50 chat messages/mo |
| **Copilot Pro** | $10/user/mo | Unlimited completions + chat; multi-model |
| **Copilot Business** | $19/user/mo | + Organization management, policy controls, audit logs |
| **Copilot Enterprise** | $39/user/mo | + Copilot for pull requests, Bing search in chat, fine-tuning |

### Copilot Features (2026)

| Feature | Description | Status |
|---------|-------------|--------|
| **Code Completion** | Autocomplete in VS Code, JetBrains, Xcode, Eclipse, Vim | GA |
| **Copilot Chat** | Chat in IDE, GitHub.com, Mobile, Windows Terminal | GA |
| **Coding Agent** | Assign GitHub issues to Copilot; autonomous PR creation | GA |
| **Copilot CLI** | Terminal-native coding agent | GA (Jan 2026) |
| **Code Review** | AI-generated review suggestions; context gathering; CodeQL + ESLint | GA |
| **Copilot Autofix** | Auto-fix security vulnerabilities found by CodeQL | GA |
| **Copilot Spaces** | Project-specific context (replaces knowledge bases) | GA |
| **Cross-Agent Memory** | Agents learn across coding agent, CLI, and code review | GA |
| **Custom Agents** | Specialized agents (Explore, Task) | GA |
| **Multi-Model** | GPT-5.2 (GA), Claude Opus 4.5 (GA), model picker | GA |
| **MCP Server** | GitHub MCP server with Copilot Spaces tools | GA |
| **Security Scanning** | Built-in code/secret/dependency scanning in agent workflow | GA |

### Agentic Workflows

Describe outcomes in Markdown → add as automated workflow → executes via coding agent in GitHub Actions. "Continuous AI" integrates AI into SDLC without replacing build/test/release pipelines.

Supported agents: GitHub Copilot, Claude (Anthropic), OpenAI Codex.

---

## 4. GitHub Actions

### Overview

CI/CD automation platform directly in GitHub repositories. Automate builds, tests, deployments, and any workflow.

### Key Capabilities

| Capability | Description |
|-----------|-------------|
| **Hosted Runners** | Linux, macOS, Windows, ARM, GPU |
| **Self-Hosted Runners** | Run on your own machines (unlimited minutes) |
| **Marketplace** | Thousands of community actions |
| **Workflow Templates** | Pre-configured templates; organization-wide sharing |
| **Events** | Push, PR, issue, schedule, webhook, workflow_dispatch |
| **Matrix Builds** | Test across multiple OS/language versions |
| **Secrets** | Encrypted secrets management |
| **Environments** | Deployment environments with protection rules |
| **Artifacts** | Upload/download build artifacts |
| **Caching** | Dependency caching for faster builds |
| **Concurrency** | Control parallel execution |
| **Reusable Workflows** | Share workflows across repositories |

### IPAI Usage

Per CLAUDE.md, we use GitHub Actions extensively:
- 47 workflows in `.github/workflows/`
- Self-hosted runners on DigitalOcean (unlimited minutes)
- Core pipelines: CI, spec validation, repo structure, security, deployment

---

## 5. GitHub Codespaces

### Overview

Cloud development environments native to GitHub. Instant, pre-configured, secure.

### Key Features

| Feature | Description |
|---------|-------------|
| **Pre-configured** | Dev containers with project-specific tooling |
| **Access** | Browser + VS Code Desktop |
| **Compute** | 2-core to 32-core machines |
| **Persistent Storage** | Survives container restarts |
| **Prebuilds** | Instant startup from pre-built images |
| **Copilot Integration** | Copilot included in Codespaces image |
| **Security** | Role-based access, audit logs, secret management |

### Pricing

| Machine | Per Hour |
|---------|----------|
| 2-core | $0.18 |
| 4-core | $0.36 |
| 8-core | $0.72 |
| 16-core | $1.44 |
| 32-core | $2.88 |

Free tier: 120 core hours/month (60 hrs on 2-core).

### IPAI Relevance

We use Claude Code on the web (similar to Codespaces). For local development, VS Code + Docker is our standard. Codespaces is a reasonable option for onboarding new contributors.

---

## 6. Security & Advanced Security

### Free Security Features (All Plans)

| Feature | Description |
|---------|-------------|
| **Dependabot Alerts** | Automatic vulnerability notifications for dependencies |
| **Dependabot Updates** | Auto-PRs to update vulnerable dependencies |
| **Dependency Graph** | Visualize project dependencies |
| **Security Advisories** | Report and manage vulnerabilities |
| **Secret Scanning (public repos)** | Detect leaked secrets in public repos |

### GitHub Advanced Security (GHAS) -- Paid Add-on

Now unbundled into two standalone products (April 2025):

#### GitHub Secret Protection -- $19/active committer/month

| Feature | Description |
|---------|-------------|
| **Secret Scanning** | Detect 200+ token types from 100+ providers |
| **Push Protection** | Block pushes containing secrets |
| **AI Secret Detection** | ML-powered detection of passwords and elusive secrets |
| **Custom Patterns** | Define organization-specific secret patterns |

#### GitHub Code Security -- $30/active committer/month

| Feature | Description |
|---------|-------------|
| **CodeQL Code Scanning** | Semantic static analysis; hundreds of vulnerability types |
| **Copilot Autofix** | AI-generated fixes for 90% of alert types (JS, TS, Java, Python) |
| **Security Campaigns** | Target and auto-fix up to 1,000 alerts at once |
| **Dependency Review** | Block PRs introducing vulnerable dependencies |

#### Combined (Legacy Bundle): $49/active committer/month

### IPAI Security Approach (per CLAUDE.md)

| GHAS Feature | IPAI Free Alternative | Annual Savings (5 devs) |
|-------------|----------------------|------------------------|
| Secret scanning ($19/mo) | Gitleaks (free) | $1,140/yr |
| Code scanning ($30/mo) | Semgrep (free) | $1,800/yr |
| Dependabot | Free on all plans | $0 |
| **Total** | | **$2,940/yr** |

---

## 7. GitHub Packages

### Overview

Host software packages alongside your code. Supports:

| Registry | Format |
|----------|--------|
| **npm** | Node.js packages |
| **Maven** | Java packages |
| **Gradle** | Java/Kotlin packages |
| **RubyGems** | Ruby packages |
| **Docker (GHCR)** | Container images |
| **NuGet** | .NET packages |

### IPAI Usage

We use GitHub Container Registry (GHCR) for Docker images in CI/CD workflows.

---

## 8. Collaboration Features

### Core (All Plans)

| Feature | Description |
|---------|-------------|
| **Pull Requests** | Code review, discussions, inline comments |
| **Issues** | Bug tracking, feature requests |
| **Projects** | Kanban boards, roadmaps, custom fields |
| **Discussions** | Community forums per repository |
| **Wikis** | Documentation per repository |
| **Pages** | Static site hosting |
| **Notifications** | Configurable email/web notifications |
| **Mobile** | GitHub Mobile app (iOS/Android) |

### Team+ Features

| Feature | Plan |
|---------|------|
| **Protected Branches** | Team+ |
| **Code Owners** | Team+ |
| **Required Reviewers** | Team+ |
| **Draft PRs** | Team+ |
| **Deployment Protection Rules** | Team+ |
| **Scheduled PR Reminders** | Team+ |

### Enterprise Features

| Feature | Plan |
|---------|------|
| **SAML SSO** | Enterprise |
| **SCIM Provisioning** | Enterprise |
| **Audit Log Streaming** | Enterprise |
| **IP Allow Lists** | Enterprise |
| **Enterprise Accounts** | Enterprise |
| **Rulesets** | Enterprise |

---

## 9. Enterprise Features

| Feature | Description |
|---------|-------------|
| **Enterprise Cloud** | Hosted by GitHub; 100+ user organizations |
| **Enterprise Server (GHES)** | Self-hosted; full control; GHES 3.20 latest |
| **SAML SSO** | Okta, Azure AD, OneLogin, PingIdentity |
| **SCIM** | Automated user provisioning/deprovisioning |
| **Audit Log** | Full audit trail; streaming to SIEM |
| **IP Allow Lists** | Restrict access by IP range |
| **Advanced Security** | Included (CodeQL, secret scanning, dependency review) |
| **Premium Support** | 24/7 with SLA |
| **60-day Free Trial** | Available for evaluation |

### Why IPAI Uses Team Instead (per CLAUDE.md)

| Enterprise Feature | IPAI Alternative | Cost |
|-------------------|-----------------|------|
| SAML SSO | Keycloak (self-hosted, free) | $0 |
| Secret scanning | Gitleaks (free) | $0 |
| Code scanning | Semgrep (free) | $0 |
| Audit logs | `ipai_platform_audit` | $0 |
| **Annual savings** | | **~$6,600/yr** |

---

## 10. GitHub Copilot Plans & Pricing

### Plan Comparison

| Feature | Free | Pro ($10) | Business ($19) | Enterprise ($39) |
|---------|------|-----------|----------------|-------------------|
| **Completions** | 2,000/mo | Unlimited | Unlimited | Unlimited |
| **Chat** | 50 msgs/mo | Unlimited | Unlimited | Unlimited |
| **Models** | GPT-4o | Multi-model | Multi-model | Multi-model |
| **Coding Agent** | Limited | Yes | Yes | Yes |
| **CLI** | No | Yes | Yes | Yes |
| **Code Review** | No | Yes | Yes | Yes |
| **Org Management** | No | No | Yes | Yes |
| **Policy Controls** | No | No | Yes | Yes |
| **Audit Logs** | No | No | Yes | Yes |
| **IP Indemnity** | No | No | No | Yes |
| **Fine-tuning** | No | No | No | Yes |
| **Bing Search** | No | No | No | Yes |

### IPAI Copilot Assessment

We use Claude Code (Anthropic) as our primary AI coding assistant, not GitHub Copilot. Per CLAUDE.md, Claude is installed in Slack and used for PR generation, code review, and task automation.

If Copilot were to be evaluated:
- **Copilot Free** covers basic needs at $0
- **Copilot Pro** ($10/mo) for individual power users
- **Copilot Business** ($19/mo) only if org-wide policy controls needed
- **Copilot Enterprise** ($39/mo) not justified for our team size

---

## 11. IPAI Stack Usage & Recommendations

### What We Currently Use from GitHub

| GitHub Feature | IPAI Usage | Plan |
|---------------|-----------|------|
| **Repositories** | All code hosting (odoo, ipai modules, apps) | Team |
| **Actions** (47 workflows) | CI/CD, testing, deployment, security | Team + self-hosted runners |
| **Pull Requests** | Code review, collaboration | Team |
| **Issues** | Bug tracking, feature requests | Team |
| **Projects v2** | Roadmap, execution board | Team |
| **Packages (GHCR)** | Docker image hosting | Team |
| **Dependabot** | Dependency vulnerability alerts | Free |
| **Branch Protection** | Required reviewers, CODEOWNERS | Team |
| **GitHub App** (pulser-hub) | Webhooks → n8n → Odoo task creation | Team |

### What We Don't Use (And Why)

| GitHub Feature | Why Not | Alternative |
|---------------|---------|------------|
| **Copilot** | Use Claude Code instead | Claude (Anthropic) |
| **Codespaces** | Use local Docker + VS Code | Docker Compose |
| **Advanced Security** | Too expensive ($49/committer) | Gitleaks + Semgrep + Trivy (free) |
| **Enterprise** | Too expensive ($21/user) | Team ($4/user) + Keycloak for SSO |
| **Pages** | Use Vercel for web hosting | Vercel ($0-$20/mo) |
| **Wikis** | Use docs/ directory in repo | Markdown in Git |

### Recommendations

1. **Stay on GitHub Team** ($4/user/mo) -- covers all essential features.

2. **Maximize self-hosted runners** -- unlimited Actions minutes on DO droplet; saves ~$360/yr vs hosted.

3. **Keep free security stack** (Gitleaks + Semgrep + Trivy) -- saves $2,940/yr vs GHAS.

4. **Use Keycloak for SSO** instead of GitHub Enterprise -- saves ~$6,600/yr.

5. **Evaluate Copilot Free** for supplementing Claude Code -- $0/mo for basic completions.

6. **Monitor GitHub Agentic Workflows** -- potential future integration for Claude agents via GitHub Actions.

### Total GitHub Cost (IPAI)

| Item | Monthly | Annual |
|------|---------|--------|
| **GitHub Team** (5 users) | $20 | $240 |
| **Self-hosted runners** (DO) | $0 (included in $50-100/mo infra) | $0 |
| **GHAS alternative** (OSS) | $0 | $0 |
| **Copilot** | $0 (use Claude) | $0 |
| **Total** | **$20** | **$240** |

vs GitHub Enterprise + GHAS + Copilot Business:

| Item | Monthly | Annual |
|------|---------|--------|
| Enterprise (5 users) | $105 | $1,260 |
| GHAS (5 committers) | $245 | $2,940 |
| Copilot Business (5) | $95 | $1,140 |
| **Total** | **$445** | **$5,340** |

**Annual savings: $5,100** by using Team + free tools.

---

## Sources

- [GitHub Features](https://github.com/features)
- [GitHub Pricing](https://github.com/pricing)
- [GitHub Copilot](https://github.com/features/copilot)
- [GitHub Copilot Plans](https://github.com/features/copilot/plans)
- [GitHub Copilot What's New](https://github.com/features/copilot/whats-new)
- [GitHub Copilot CLI](https://github.com/features/copilot/cli)
- [GitHub Copilot Agents](https://github.com/features/copilot/agents)
- [GitHub Codespaces](https://github.com/features/codespaces/)
- [GitHub Code Security](https://github.com/security/advanced-security/code-security)
- [GitHub Enterprise](https://github.com/enterprise)
- [GitHub Pricing Calculator](https://github.com/pricing/calculator)
- [GitHub Plans Docs](https://docs.github.com/get-started/learning-about-github/githubs-products)
- [GitHub Copilot Features Docs](https://docs.github.com/en/copilot/get-started/features)
- [Evolving GitHub Advanced Security](https://resources.github.com/evolving-github-advanced-security/)
- [GitHub Secret Protection & Code Security](https://github.blog/changelog/2025-03-04-introducing-github-secret-protection-and-github-code-security/)
- [GitHub Agentic Workflows Blog](https://github.blog/ai-and-ml/automate-repository-tasks-with-github-agentic-workflows/)
- [GitHub Copilot Coding Agent Updates](https://github.blog/ai-and-ml/github-copilot/whats-new-with-github-copilot-coding-agent/)
- [GitHub Copilot CLI GA](https://github.blog/changelog/2026-01-14-github-copilot-cli-enhanced-agents-context-management-and-new-ways-to-install/)
- [GitHub Dec 2025-Jan 2026 Ships](https://dev.to/andreagriffiths11/githubs-december-2025-january-2026-the-ships-that-matter-2bgi)
- [GitHub Pricing Guide 2026 (PullNotifier)](https://pullnotifier.com/tools/github-pricing)
- [GitHub Pricing 2026 (Vendr)](https://www.vendr.com/marketplace/github)
- [GitHub Pricing Guide (eesel.ai)](https://www.eesel.ai/blog/github-pricing)
- [GitHub Enterprise Review 2026](https://www.linktly.com/it-software/githubenterprise-review/)

---

*Index compiled: 2026-03-07*
*Branch: claude/review-signavio-url-HffM8*
*See also: [GHAZDO_AZURE_DEVOPS_SECURITY_REVIEW.md](./GHAZDO_AZURE_DEVOPS_SECURITY_REVIEW.md) for GHAzDO-specific review*
