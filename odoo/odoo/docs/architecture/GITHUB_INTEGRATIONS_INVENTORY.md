# GitHub Integrations Inventory

> **Snapshot date**: 2026-02-12
> **Organization**: Insightpulseai
> **Account**: jgtolentino
> **Machine-readable**: `ops/github/integrations/github_apps.json`, `ops/github/integrations/authorized_apps.json`

---

## Org-Level Installed GitHub Apps (9)

Apps installed at the **Insightpulseai** organization level. These apply to all org repositories.

| App | Owner | Category | Purpose |
|-----|-------|----------|---------|
| Azure Boards | microsoft | Project Management | Azure DevOps work item linking |
| ChatGPT Codex Connector | openai | AI Coding | OpenAI Codex code generation |
| Claude | anthropics | AI Coding | Claude agent for code review, PRs, autonomous coding |
| Cloudflare Workers and Pages | cloudflare | Deployment | Edge deployment and CDN |
| Cursor | cursor | AI Coding | AI-powered IDE integration |
| Databricks | databricks | Data Platform | Lakehouse and data engineering |
| Figma | figma | Design | Design file linking in PRs |
| Slack | github | Communication | GitHub notifications in Slack |
| Vercel | vercel | Deployment | Frontend deployment previews |

---

## Personal Authorized GitHub Apps (33)

Apps authorized by **jgtolentino** at the personal account level.

### AI & Coding (12)

| App | Owner | Last Used | Notes |
|-----|-------|-----------|-------|
| ChatGPT Codex Connector | openai | ~1 week | |
| Claude | anthropics | ~1 week | |
| Continue | continuedev | unknown | Permission update requested |
| Cursor | cursor | ~1 week | |
| Google AI Studio | google-gemini | ~2 months | |
| Google Labs Jules | google-labs-code | unknown | Permission update requested |
| lovable.dev | GPT-Engineer-App | ~3 months | |
| Replit | replit | ~8 months | |
| Rork-Agent | rorkai | ~5 months | |
| Smithery | smithery-ai | ~5 months | OAuth only |
| pulser-hub | jgtolentino | ~2 weeks | Custom App (ID: 2191216) |
| Pieces for Developers | pieces-app | ~5 months | OAuth only |

### Deployment & Infrastructure (9)

| App | Owner | Last Used | Notes |
|-----|-------|-----------|-------|
| Cloudflare Workers and Pages | cloudflare | never | OAuth only |
| DigitalOcean | digitalocean | ~2 months | |
| docker | docker | never | |
| Netlify | netlify | unknown | |
| Railway App | railwayapp | never | |
| Render | renderinc | ~5 months | Permission update requested |
| Velo App | velo | unknown | |
| Vercel | vercel | ~1 week | |
| Vercel Toolbar | vercel | never | |

### Data Platform (4)

| App | Owner | Last Used | Notes |
|-----|-------|-----------|-------|
| Databricks | databricks | never | |
| Neon Postgres | neondatabase | never | |
| Prisma | prisma | never | OAuth only |
| Supabase | supabase | ~3 weeks | |

### Design & Diagramming (4)

| App | Owner | Last Used | Notes |
|-----|-------|-----------|-------|
| Builder.io Integration | BuilderIO | ~3 months | Permission update requested |
| draw.io App | jgraph | unknown | |
| Figma | figma | ~2 weeks | |
| Mermaid Chart | mermaid-js | unknown | |

### Project Management (3)

| App | Owner | Last Used | Notes |
|-----|-------|-----------|-------|
| Azure Boards | microsoft | ~4 months | |
| Linear | linear | never | |
| monday.com + GitHub | mondaycom | never | Permission update requested |

### Productivity (2)

| App | Owner | Last Used | Notes |
|-----|-------|-----------|-------|
| Notion AI Connector | notion | unknown | |
| Notion Workspace | notion | unknown | |

### Other (2)

| App | Owner | Last Used | Notes |
|-----|-------|-----------|-------|
| Percy | percy | never | Visual testing |
| Renovate | renovatebot | unknown | Dependency management |

---

## Personal Authorized OAuth Apps (39)

OAuth apps authorized by **jgtolentino**. Includes GitHub-native Copilot apps.

### GitHub-Native (6)

| App | Last Used |
|-----|-----------|
| Copilot Chat App | ~1 week |
| Copilot SWE Agent | ~1 week |
| Copilot Pull Request Reviewer | ~2 weeks |
| GitHub Codespaces | ~1 week |
| GitHub Copilot Plugin | ~3 months |
| Copilot Spark | never |

### Third-Party (33)

See "Personal Authorized GitHub Apps" above — OAuth authorization mirrors the GitHub App list with additions: Claude for GitHub (~6 months), Docker Inc (~4 months), Sentry (never), Slack (never).

---

## Apps Requiring Attention

### Permission Update Requests

These apps have pending permission update requests that should be reviewed:

1. **Builder.io Integration** — Review and approve/deny
2. **Continue** — Review and approve/deny
3. **Google Labs Jules** — Review and approve/deny
4. **monday.com + GitHub** — Review and approve/deny
5. **Render** — Review and approve/deny

### Never-Used Apps (Candidates for Revocation)

Apps authorized but never used — consider revoking to reduce attack surface:

| App | Type |
|-----|------|
| Cloudflare Workers and Pages | OAuth |
| Copilot Spark | OAuth |
| Databricks | GitHub App + OAuth |
| docker | GitHub App + OAuth |
| Linear | GitHub App + OAuth |
| monday.com + GitHub | GitHub App + OAuth |
| Neon Postgres | GitHub App + OAuth |
| Percy | GitHub App + OAuth |
| Prisma | OAuth |
| Railway App | GitHub App + OAuth |
| Sentry | OAuth |
| Slack | OAuth |
| Vercel Toolbar | GitHub App + OAuth |

---

## Category Summary

| Category | Org Apps | Personal Apps | OAuth Apps |
|----------|----------|---------------|------------|
| AI & Coding | 3 | 12 | 14 |
| Deployment | 2 | 9 | 5 |
| Data Platform | 1 | 4 | 4 |
| Design | 1 | 4 | 2 |
| Project Management | 1 | 3 | 3 |
| Communication | 1 | 0 | 1 |
| Productivity | 0 | 2 | 1 |
| Testing | 0 | 1 | 1 |
| Monitoring | 0 | 0 | 1 |
| Custom | 0 | 1 | 1 |
| GitHub-Native | 0 | 0 | 6 |
| **Total** | **9** | **33** | **39** |
