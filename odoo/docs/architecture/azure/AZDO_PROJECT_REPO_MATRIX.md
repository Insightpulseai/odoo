# Azure DevOps Project-Repo Matrix

> SSOT for Azure DevOps organization structure, project-to-repo mapping, and execution surface boundaries.
> Machine-readable companion: `ssot/governance/azdo-project-repo-alignment.yaml`
>
> Last updated: 2026-03-14

---

## 1. Azure DevOps Org Model

| Property | Value |
|----------|-------|
| Organization | `insightpulseai` |
| Active projects | 2 (`ipai-platform`, `data-intelligence`) |
| Role | Selective execution surface (pipelines, boards, artifacts) |
| Primary source control | GitHub (`Insightpulseai` org) |
| Primary CI/CD | GitHub Actions |
| Azure DevOps CI/CD | Additive, not competing -- used when Azure-native integration is required |

GitHub remains the canonical location for source hosting, pull request review, and default CI/CD via GitHub Actions. Azure DevOps Pipelines are used selectively where Azure-native service connections, variable groups, or deployment targets make Azure Pipelines the better execution surface.

---

## 2. Project to Repo Matrix

### ipai-platform

**Purpose**: Platform control plane, runtime services, infrastructure, and automation.

| GitHub Repo | Azure DevOps Visibility | Pipeline Use Cases |
|-------------|------------------------|-------------------|
| `odoo` | Linked | Container image build, ACA deployment |
| `infra` | Linked | Terraform plan/apply, infrastructure provisioning |
| `platform` | Linked | Ops console deployment, health checks |
| `agents` | Linked | Agent runtime deployment, model gateway routing |
| `.github` | Linked | Org-level workflow templates (consumed by GH Actions) |
| `automations` | Linked | n8n workflow deployment, automation orchestration |
| `web` | Linked | Web frontend build and deployment |

**Service connection**: `sc-azure-dev-platform` (ARM, workload identity federation)
**Variable groups**: Key Vault-backed (`kv-ipai-dev`)

### data-intelligence

**Purpose**: Databricks analytics, medallion data pipelines, data intelligence.

| GitHub Repo | Azure DevOps Visibility | Pipeline Use Cases |
|-------------|------------------------|-------------------|
| `data-intelligence` | Linked | Databricks job deployment, notebook sync, Unity Catalog provisioning |

**Service connection**: `sc-azure-dev-lakehouse` (ARM, workload identity federation)

> **Note**: The AzDO project name and service connection name may still reference `lakehouse` until renamed in Azure DevOps. The GitHub repo canonical name is `data-intelligence`.
**Databricks workspace**: `dbw-ipai-dev`

---

## 3. Agent Pool Strategy

| Pool Name | Resource Group | Type | Current Use |
|-----------|---------------|------|-------------|
| `ipai-build-pool` | `rg-ipai-devops` | Self-hosted | Shared across both projects |

Both `ipai-platform` and `data-intelligence` share the single `ipai-build-pool`. A dedicated pool per project is not warranted at current scale. If pipeline concurrency becomes a bottleneck, split into `ipai-build-pool-platform` and `ipai-build-pool-data-intelligence`.

**Dev Center**: `ipai-devcenter` (in `rg-ipai-devops`) provides dev box and environment definitions. Not currently used for pipeline agents.

---

## 4. Service Connection Strategy

| Connection Name | Project | Type | Auth Mechanism | Target |
|-----------------|---------|------|---------------|--------|
| `sc-azure-dev-platform` | ipai-platform | ARM | Workload identity federation | Platform Azure resources |
| `sc-azure-dev-lakehouse` | data-intelligence | ARM | Workload identity federation | Data intelligence Azure resources + Databricks |

**Rules**:
- All ARM service connections use workload identity federation (no long-lived client secrets).
- Each project has its own scoped service connection. No shared cross-project connections.
- Service connections are protected resources with approval checks on production environments.
- Workload identity federation from Azure DevOps to Azure AD is the only supported auth pattern.

---

## 5. Secret Management

Secrets are managed exclusively through Key Vault-backed variable groups.

| Variable Group | Key Vault | Project | Scope |
|---------------|-----------|---------|-------|
| `vg-ipai-platform-secrets` | `kv-ipai-dev` | ipai-platform | Platform service credentials |
| `vg-ipai-lakehouse-secrets` | `kv-ipai-dev` | data-intelligence | Databricks tokens, storage keys |

**Rules**:
- No long-lived service principal secrets stored in Azure DevOps variable groups directly.
- All secret-bearing variable groups are Key Vault-backed.
- Variable groups are not open to all pipelines -- explicit pipeline authorization is required.
- Protected resources (environments, service connections, variable groups) require permissions, checks, and approvals before use in pipelines.
- No secrets in Git, no secrets in pipeline YAML, no secrets echoed in logs.

---

## 6. What Stays GitHub-Primary

| Capability | Surface | Rationale |
|-----------|---------|-----------|
| Source control | GitHub | Canonical repo hosting |
| Pull request review | GitHub | PR workflow, code review, status checks |
| Default CI/CD | GitHub Actions | `anthropics/claude-code-action@v1`, standard test/lint/build |
| Issue tracking | GitHub Issues + Plane | Project management surfaces |
| Release management | GitHub Releases | Tag-based releases with changelog |
| Org-level templates | `.github` repo | Reusable workflow templates |
| Security scanning | GitHub Advanced Security | Dependabot, CodeQL, secret scanning |

Azure DevOps Pipelines are used only when:
1. Azure-native deployment targets require ARM service connections.
2. Key Vault-backed variable groups provide secret injection.
3. Databricks workspace integration requires Azure DevOps-native connectors.
4. Self-hosted agent pools are needed for network-restricted builds.

---

## 7. Deployment Pools

Deployment pools (distinct from agent pools) are **not currently in use**. If deployment group-based release strategies are needed (e.g., rolling deployments to VM scale sets), deployment pools will be created under `rg-ipai-devops` with the naming convention `ipai-deploy-pool-<target>`.

For now, all deployments target Azure Container Apps via service connections, not deployment agents.
