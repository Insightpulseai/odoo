# Deprecated CLI Surfaces — Registry

> Status: Active registry
> Last updated: 2026-03-17

## Canonical Rule

Deprecated CLI tools must not be included in the canonical stack. They are tracked here for assessment purposes and to prevent accidental adoption. Default stance: REJECT. Exception requires meeting ALL 5 criteria documented in `agents/skills/deprecated-cli-assessment/SKILL.md`.

## Registry

### odo (Red Hat OpenShift Developer CLI)

| Attribute | Value |
|-----------|-------|
| **Vendor** | Red Hat |
| **Status** | Officially deprecated |
| **GitHub** | `redhat-developer/odo` (archived) |
| **Deprecation date** | 2024 |
| **Last release** | v3.x |
| **Original purpose** | Simplified developer experience for OpenShift/Kubernetes |
| **IPAI relevance** | None — IPAI does not use OpenShift |
| **Canonical alternative** | Databricks CLI (data/ML), Azure CLI (infra), Odoo CLI (ERP) |
| **Exception status** | Permanent REJECT — no exception pathway |
| **Benchmark-only** | Allowed for historical comparison documentation |

**Why odo was deprecated:**
- Red Hat shifted focus to Podman Desktop and `oc` CLI
- Developer experience improvements were absorbed into other tools
- Community adoption did not reach critical mass
- Kubernetes-native tooling (kubectl, Helm, Kustomize) proved more flexible

**Impact on IPAI:**
- Zero impact — odo was never part of the IPAI stack
- Tracked only to prevent future accidental adoption
- If someone proposes odo, this registry provides the rejection basis

## Assessment Criteria for Future Deprecations

When a new CLI tool is suspected of being deprecated, evaluate:

1. **Official status**: Is the tool officially deprecated by its vendor?
2. **Repository status**: Is the GitHub/source repository archived or read-only?
3. **Last release date**: Has there been a release in the past 12 months?
4. **Vendor roadmap**: Does the vendor recommend an alternative?
5. **Community activity**: Are issues/PRs being addressed?

If 3+ of these indicate deprecation, add to this registry with REJECT status.

## Migration Paths

| Deprecated Tool | Use Case | Canonical Alternative |
|----------------|----------|----------------------|
| odo | Kubernetes app development | `kubectl`, `az containerapp`, Databricks CLI |
| odo | Inner loop development | Local Docker, devcontainer |
| odo | Service deployment | Azure CLI (`az containerapp`), `azd` |

## Tools Under Watch (Not Yet Deprecated)

| Tool | Concern | Status |
|------|---------|--------|
| (none currently) | — | — |

Tools are added to the watch list when deprecation signals appear but official deprecation has not been announced. Watch list tools remain canonical until moved to the deprecated registry.

## Related Documents

- `agents/skills/deprecated-cli-assessment/SKILL.md` — Assessment skill
- `agents/personas/deprecated-tool-reviewer.md` — Reviewer persona
- `agents/skills/cli-surface-selection/SKILL.md` — Routing judge that rejects deprecated tools
