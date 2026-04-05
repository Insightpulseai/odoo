# Skill: azdo.project.settings

## Reasoning Strategy

You configure Azure DevOps project-level settings for the IPAI platform. This skill covers the administrative surface documented in Microsoft Learn's "About settings for users, teams, projects, or organizations."

### Role Model

| Role | Scope | Key Actions |
|------|-------|-------------|
| Team Administrator | Team-scoped | Backlog levels, sprint paths, dashboards, notifications |
| Project Administrator | Project-scoped | Area/iteration paths, teams, security, services, repos, wikis |
| Project Collection Administrator | Org-scoped | Process customization, billing, extensions, policies |

IPAI operates with a single user (Platform Admin) who holds PCA-level access.

### Area Paths

Area paths organize work by domain. IPAI canonical areas should map to the 7 spec bundles:
- `ipai-platform\Odoo on Azure`
- `ipai-platform\AI Platform`
- `ipai-platform\AI-Led Engineering`
- `ipai-platform\Data Intelligence`
- `ipai-platform\Governance`
- `ipai-platform\Assessment Harness`
- `ipai-platform\Odoo SDK`

```bash
# Create area path
az boards area project create --name "Odoo on Azure" --org {org} --project {project}

# List area paths
az boards area project list --org {org} --project {project} --output table
```

### Iteration Paths (Sprints)

```bash
# Create iteration
az boards iteration project create --name "Sprint 1" --start-date 2026-04-07 --finish-date 2026-04-18 --org {org} --project {project}

# List iterations
az boards iteration project list --org {org} --project {project} --output table
```

### Team Configuration

```bash
# List teams
az devops team list --org {org} --project {project} --output table

# Show team details
az devops team show --team {team_name} --org {org} --project {project}
```

### Services (Enable/Disable)

Available services: Boards, Repos, Pipelines, Test Plans, Artifacts. Services not in use can be disabled to simplify the UI.

### Security Policies (Org Level)

Key policies from the Microsoft Learn doc:
- **Application access policies** — control OAuth/PAT access
- **External user policy** — allow/restrict guest access
- **Conditional Access** — enforce MFA via Entra (requires Entra P1+)
- **Request access policy** — enable/disable access requests

### Authentication Hierarchy (from Microsoft Learn)

Priority order (most to least secure):
1. Microsoft Entra tokens (recommended)
2. SSH keys
3. Personal Access Tokens (PATs) — minimize usage

### Process Template

IPAI uses **Basic** process. Available types: Epic, Issue, Task.
To change the process template, use the org-level Process settings (PCA only).

## Edge Cases

- Area/iteration path commands use `az boards area` and `az boards iteration`, not `az boards work-item`
- `--depth` controls how many child levels to show in area/iteration listings
- Service toggle requires project admin; security policy changes require org admin
- Process customization (adding custom fields/states) requires PCA and is org-level, not project-level

## Notes

- IPAI project `ipai-platform` is in the `insightpulseai` org
- The project uses Basic process — no customization to Agile/Scrum/CMMI is planned
- Service hooks can integrate with Slack, n8n, and other external services
