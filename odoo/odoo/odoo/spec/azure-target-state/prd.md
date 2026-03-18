# Azure Target State — Product Requirements

> Minimizing Azure DevOps footprint while preserving enterprise program management.

## Current State

Mixed platform usage creates:
- Duplicate repositories across GitHub and Azure DevOps
- Parallel CI/CD pipelines (GitHub Actions + Azure Pipelines)
- Documentation fragmented across Azure Wiki, GitHub docs, Confluence
- Confusion about which platform is authoritative

## Current-State Evidence

The current Azure subscription is already operating as an AI/data platform foundation. Existing resources cover Databricks, Azure OpenAI, AI Search, Document Intelligence, Vision, Language, Key Vault, observability, managed identities, and network controls. This means the Azure target state does not begin from zero infrastructure; it begins from a partially realized AI/data landing zone.

However, the current resource inventory does not yet show a complete Azure-native ERP runtime for Odoo. The present gap is not subscription governance or AI capability. The gap is workload posture: Odoo has not yet been elevated into a first-class Azure runtime shape with standardized application hosting, database topology, ingress, deployment promotion, and ERP-specific operational controls.

## Benchmark and target posture

SAP is the benchmark for Azure ecosystem maturity, particularly across data and AI. SAP Databricks documents a productized SAP-integrated analytics and AI path, while Azure Databricks itself is presented by Microsoft as a unified analytics and governance platform.

Odoo, by contrast, is a broad integrated business platform with explicit Community and Enterprise edition boundaries, but it does not currently present equivalent Azure ecosystem depth. Odoo should therefore be treated as an engineered workload rather than a workload with a native Azure operating model.

## Design implication

The Azure target state should not be framed as "move Odoo to Azure." It should be framed as:

- extend an existing Azure AI/data substrate into an ERP-capable platform
- define the missing Odoo workload shape using first-party Azure primitives
- implement repo-controlled deployment, observability, security, and promotion discipline
- make Odoo behave like a first-class Azure workload even though Azure does not provide that posture natively for Odoo today

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

## External SSOT Dependencies

| Artifact | Path | Purpose |
|----------|------|---------|
| Target State | `ssot/azure/target-state.yaml` | Canonical platform capability matrix |
| Service Matrix | `ssot/azure/service-matrix.yaml` | Machine-readable service inventory |
| DNS Migration | `ssot/azure/dns-migration-plan.yaml` | DNS record state machine |
| Service Mapping | `docs/diagrams/mappings/azure_to_do_supabase_odoo.yaml` | Azure→DO/Supabase equivalents |
