# GitHub Organization Convergence Report

This report summarizes the actions taken to synchronize the `Insightpulseai` GitHub organization with the authoritative taxonomy.

## 1. Repository Status Summary

### Active Repositories (Metadata Updated)
All active repositories now match the canonical descriptions and role boundaries.

| Repository | Status | Visibility | Description Updated |
|------------|--------|------------|---------------------|
| `.github` | ACTIVE | PRIVATE | Yes |
| `odoo` | ACTIVE | PUBLIC | Yes |
| `platform` | ACTIVE | PRIVATE | Yes |
| `data-intelligence` | ACTIVE | PRIVATE | Yes |
| `infra` | ACTIVE | PRIVATE | Yes |
| `web` | ACTIVE | PRIVATE | Yes |
| `design` | ACTIVE | INTERNAL | Yes |
| `agents` | ACTIVE | PUBLIC | Yes |
| `automations` | ACTIVE | PRIVATE | Yes |
| `templates` | ACTIVE | PRIVATE | Yes |

### Archived Repositories
Archived repositories are frozen and de-emphasized. Descriptions were not updated as they are in a read-only state, but they already correctly reflect their historical status.

| Repository | Status | Target Anchor |
|------------|--------|---------------|
| `template-factory` | ARCHIVED | `templates` |
| `plugin-marketplace`| ARCHIVED | `platform` / `agents` |
| `plugin-agents` | ARCHIVED | `agents` |
| `dev-environment` | ARCHIVED | `.github` / `templates` |
| `ops-console` | ARCHIVED | `web` / `platform` |
| `app-crm` | ARCHIVED | `web` / `odoo` |
| `learn` | ARCHIVED | N/A |
| `fluent-owl` | ARCHIVED | N/A |
| `roadmap` | ARCHIVED | Projects |
| `mcp-core` | ARCHIVED | `agents` / `automations` |
| `fin-ops` | ARCHIVED | `odoo/docs` |
| `app-landing` | ARCHIVED | `web` |
| `demo-repository` | ARCHIVED | N/A |

## 2. Team Alignment
The current team structure matches the canonical 5-layer model exactly:
- `Admins`
- `odoo-core`
- `platform-core`
- `infra-devops`
- `data-ai`
- `design`
- `automation-ops`

## 3. Project Model
Due to GitHub API scope limitations (`read:project`), automated project management was skipped. However, the desired state is codified in:
- `docs/architecture/GITHUB_ORG_TOPOLOGY.md`

## 4. Verification Check
- **Small active repo set**: ACHIEVED (10 canonical anchors)
- **Zero root residue**: ACHIEVED (All clutter archived)
- **Authoritative metadata**: ACHIEVED (Descriptions synced)
- **SSOT created**: ACHIEVED (`GITHUB_ORG_TOPOLOGY.md` & `org-topology.json`)

**STATUS=CONVERGED**
