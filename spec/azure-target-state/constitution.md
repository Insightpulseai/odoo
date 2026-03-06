# Azure Target State — Constitution

> Non-negotiable boundary rules for Azure DevOps usage within InsightPulse AI.

## Primary Platform: GitHub Enterprise

GitHub is the **canonical and primary** platform for:
- **Source Control**: All repositories live on GitHub (`Insightpulseai/` org)
- **CI/CD**: GitHub Actions is the sole CI/CD engine
- **Code Review**: Pull requests on GitHub
- **Documentation**: In-repo docs (spec kits, architecture docs, CLAUDE.md)
- **Issue Tracking**: GitHub Issues for engineering work
- **Releases**: GitHub Releases + deployment workflows

## Azure DevOps: Bounded Role

Azure DevOps is **permitted only** for:
- **Boards**: Enterprise program management overlay (portfolio-level tracking)
- **Program Rollup**: Cross-project status aggregation for executive reporting

Azure DevOps is **prohibited** for:
- Repositories (no repos on Azure DevOps)
- Pipelines (no CI/CD on Azure DevOps)
- Artifacts (use GitHub Packages or npm registry)
- Test Plans (use GitHub Actions + test frameworks)
- Wiki (use in-repo docs)

## No Duplication Rule

| Asset | Canonical Location | Azure DevOps |
|-------|-------------------|--------------|
| Source code | GitHub | NEVER |
| CI/CD pipelines | GitHub Actions | NEVER |
| Documentation | In-repo (spec/, docs/) | NEVER |
| Code review | GitHub PRs | NEVER |
| Engineering issues | GitHub Issues / Plane | NEVER |
| Program boards | GitHub Projects OR Azure Boards | Optional overlay |
| Release artifacts | GitHub Releases | NEVER |

## Migration Direction

All movement is **toward GitHub, away from Azure DevOps**:
- Any existing Azure DevOps repos → migrate to GitHub
- Any existing Azure Pipelines → convert to GitHub Actions
- Any existing Azure Wiki → move to in-repo docs
- Azure Boards may persist only for enterprise program overlay

## Conflict Resolution

If Azure DevOps and GitHub contain conflicting information:
1. **GitHub is authoritative** — always
2. Azure DevOps data is considered stale until proven otherwise
3. Automated sync flows FROM GitHub TO Azure DevOps (never reverse)
