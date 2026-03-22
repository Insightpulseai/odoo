# Enterprise Target State Matrix

> **Status**: Approved
> **Date**: 2026-03-22
> **SSOT**: `ssot/governance/github-entra-target-state.yaml`, `ssot/governance/databricks-auth-target.yaml`

---

## Target Profile

- **Entra** = canonical identity authority
- **GitHub Enterprise** = SAML + secure 2FA enforced
- **GitHub Org** = lean execution/roadmap workflow
- **GitHub Packages** = selective SDK/contracts publishing only
- **Databricks auth** = Azure CLI (local), AzureCLI@2 (pipelines), OAuth M2M (bots)

---

## Enable Now / Defer / Ignore Matrix

| Surface | Setting | Target | Action |
|---------|---------|--------|--------|
| GitHub Enterprise | Require 2FA | Enabled | **Enable now** |
| GitHub Enterprise | Secure 2FA methods only | Enabled | **Enable now** |
| GitHub Enterprise | Require SAML SSO | Enabled with Entra | **Enable now** |
| GitHub Enterprise | IP allow list | Disabled | **Defer** |
| GitHub Enterprise | IP allow list for GitHub Apps | Disabled | **Defer** |
| GitHub Org | Projects enabled | Keep enabled | **Keep** |
| GitHub Org | Member project visibility changes | Keep disabled | **Keep** |
| GitHub Org | Project model | Template + Execution + Roadmap | **Keep** |
| GitHub Org | Issue types | Feature, Bug, Task, Incident, Spike | **Add now** |
| GitHub Org | Epic/Initiative issue types | Do not add | **Defer** |
| GitHub Packages | Strategy | Selective SDK/contracts only | **Set policy now** |
| GitHub Packages | Candidate repos | platform, agents, web, data-intelligence | **Define now** |
| GitHub Packages | ipai-superset | Review/grandfather/retire | **Review now** |
| Entra | License | P1 minimum, P2 preferred | **Target now** |
| Entra | External Identities | Enabled if B2B needed | **Conditional** |
| Entra | Cross-tenant sync | Not core | **Defer** |
| Entra | Entra Connect | Not core (cloud-native) | **Defer** |
| Entra | Backup/Recovery preview | Ignore | **Ignore** |
| Entra | Access reviews | Use with P2 | **Defer** |
| Entra | Agent ID / collections | Preview | **Defer** |
| M365 Admin | Copilot/agent admin | Bounded admin plane | **Keep bounded** |
| Databricks | Local dev auth | Azure CLI (user interactive) | **Enable now** |
| Databricks | Azure DevOps pipelines | AzureCLI@2 + service connection | **Enable now** |
| Databricks | GitHub Actions | OIDC / workload identity federation | **Defer** |
| Databricks | Unattended bots | Databricks OAuth M2M | **Enable now** |
| Databricks | Cross-service bots | Azure CLI + Entra SP | **Enable now** |

---

## Do Not Target

| Pattern | Why |
|---------|-----|
| Manual PAT auth as strategic standard | Use OAuth or Azure CLI |
| Long-lived Entra client secrets everywhere | Prefer federation/OIDC |
| Entra Connect / hybrid sync | Cloud-native — no on-prem AD |
| Cross-tenant sync | Single-tenant Entra |
| Broad GitHub Packages publishing | SDK/contracts only |
| Epic/Initiative in GitHub issue types | Use Azure Boards for portfolio |
| Every Microsoft admin surface as platform dependency | Keep bounded |
