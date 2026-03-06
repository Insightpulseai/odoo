# Azure Target State — Product Requirements

> Minimizing Azure DevOps footprint while preserving enterprise program management.

## Current State

Mixed platform usage creates:
- Duplicate repositories across GitHub and Azure DevOps
- Parallel CI/CD pipelines (GitHub Actions + Azure Pipelines)
- Documentation fragmented across Azure Wiki, GitHub docs, Confluence
- Confusion about which platform is authoritative

## Target State

### GitHub (Primary — 95%+ of work)
| Capability | Tool | Status |
|-----------|------|--------|
| Source control | GitHub repos | Active |
| CI/CD | GitHub Actions (153 workflows) | Active |
| Code review | GitHub PRs | Active |
| Issue tracking | GitHub Issues + Plane | Active |
| Documentation | In-repo spec kits + docs/ | Active |
| Releases | GitHub Releases | Active |
| Package registry | npm (pnpm workspaces) | Active |
| Security | Dependabot + CodeQL | Active |

### Azure DevOps (Bounded — program overlay only)
| Capability | Tool | Status |
|-----------|------|--------|
| Program boards | Azure Boards | Optional |
| Executive reporting | Azure Dashboards | Optional |
| Cross-project tracking | Portfolio backlog | Optional |

### Neither (Eliminated)
| Capability | Previous | Replacement |
|-----------|----------|-------------|
| Chat/messaging | Mattermost | Slack |
| Wiki | Azure Wiki | In-repo docs |
| Artifact storage | Azure Artifacts | GitHub Packages / npm |
| Test management | Azure Test Plans | GitHub Actions + pytest/jest |

## Migration Tasks

1. **Audit**: Identify all Azure DevOps repos, pipelines, and wikis
2. **Repos**: Migrate any remaining Azure repos to GitHub
3. **Pipelines**: Convert Azure Pipelines to GitHub Actions
4. **Wiki**: Extract Azure Wiki content to spec kits
5. **Boards**: Configure Azure Boards as read-only sync from GitHub (if retained)
6. **Document**: Update all onboarding to reference GitHub-only workflow

## Success Metrics

- Zero active repositories on Azure DevOps
- Zero active pipelines on Azure DevOps
- Zero documentation on Azure Wiki
- Azure DevOps cost reduced to Boards-only tier (if retained) or $0
