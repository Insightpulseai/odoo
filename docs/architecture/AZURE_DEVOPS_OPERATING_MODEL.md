# Azure DevOps & VS Code Target Operating Model

> **Version:** 1.0.0
> **Scope:** Defines the deterministic engineering cockpit unifying local VS Code development and remote Azure DevOps execution for the InsightPulseAI monorepo.

## 1. Executive Summary
This document establishes a **deterministic engineering cockpit** where local VS Code development and remote Azure DevOps execution behave as one coherent system. The architecture relies on GitHub for source control and PR truth, while Azure DevOps serves as the strict control plane for portfolio planning (Boards), continuous integration, and governed deployments (Pipelines). By sharing the exact same containerized toolchains (`.devcontainer`), environment names (`dev`, `staging`, `prod`), and execution scripts, we eliminate environment drift between the solo developer and the CI/CD runners. 

## 2. Target Local/Remote Operating Model
### Local Developer Workflow (The Inner Loop)
- **Environment**: Visual Studio Code using Docker-backed `.devcontainer` isolated boundaries (`infra` and `erp`).
- **Execution**: Developers use `make` targets and VS Code tasks to run linters, spin up Odoo locally, or run Terraform plans.
- **Rules**: Repo-scoped `.vscode/settings.json` enforces Python formatting (Black) and terraform linting. Local development must pass the exact same scripts that run in CI.

### Remote execution Workflow (The Outer Loop)
- **Portfolio & Planning**: Azure Boards acts as the single source of truth for all Epics, Features, and Tasks.
- **Source of Truth**: GitHub holds the code. Developers branch from `main`, push to GitHub, and open PRs.
- **CI Workflow**: A PR in GitHub triggers an Azure Pipeline (via GitHub Checks integration). The pipeline spins up an Ubuntu hosted agent, invokes the exact same `make test` or `make lint` targets used locally, and reports status back to the GitHub PR.
- **CD Workflow**: Merging an approved PR to `main` triggers the deployment pipeline. Azure Pipelines promotes the artifact logically through environment gates (`dev` -> `staging` -> `prod`).
- **Gate Workflow**: `dev` deploys automatically from `main`. `staging` and `prod` require manual Environment Approvals in Azure DevOps.

## 3. Target Repo Artifact Map
- **`.github/workflows/`**: Lightweight triggers or GitHub-specific checks (e.g., taxonomy enforcement).
- **`.azure/pipelines/`**: Canonical Azure DevOps YAML definitions (`ci.yml`, `cd-infra.yml`, `cd-odoo.yml`).
- **`.devcontainer/`**: Isolated engineering environments (`infra/`, `erp/`).
- **`.vscode/`**: Deterministic local launch configs (`launch.json`, `tasks.json`, `settings.json`).
- **`ssot/azure/`**: Machine-readable state definitions for the DevOps setup (`azure_devops.yaml`).
- **`Makefile`**: Universal execution wrapper bridging local terminal and Azure Pipelines.

## 4. Azure DevOps Setup Specification
- **Project**: `InsightPulseAI` (Visibility: Private)
- **Boards Structure**: Agile template (Epic -> Feature -> User Story -> Task).
- **GitHub Integration**: Azure Boards GitHub app installed to automatically link `AB#123` mentions in commits/PRs to work items.
- **Pipelines Strategy**: YAML-based pipelines stored in the GitHub repo under `.azure/pipelines/`. Default to Microsoft-hosted `ubuntu-latest` agent pools to reduce maintenance overhead.
- **Environments**: Registered in ADO as `insightpulseai-dev`, `insightpulseai-staging`, and `insightpulseai-prod`. 
- **Service Connections**: Workload Identity Federation (OIDC) between Azure DevOps and Azure Resource Manager to eliminate long-lived secrets.

## 5. VS Code / DevContainer Local Setup Specification
- **Workspace Structure**: Single VS Code workspace at the repo root.
- **DevContainers**: Split isolation. `infra` contains `azd`, `terraform`, `az cli`. `erp` contains Python 3.12, Node, and Odoo C-dependencies.
- **Run/Debug**: `launch.json` must be configured to automatically attach to the Odoo Python process, and `tasks.json` must expose `make run-odoo` and `make tf-plan`.

## 6. Local-to-Remote Contract Matrix

| Concept | Local (VS Code) | Remote (Azure DevOps) | Drift Prevention |
| :--- | :--- | :--- | :--- |
| **Toolchain** | `.devcontainer` definition | Hosted Ubuntu agent + setup scripts | ADO pipeline uses identical container or setup scripts |
| **Task Execution** | `make lint`, `make test` | `make lint`, `make test` | The `Makefile` is the single source of truth |
| **Environment Names** | `.env.dev`, `.env.staging` | ADO Environment variables (`dev`, `staging`) | Mapped explicitly in the Azure Pipeline YAML |
| **Validation** | Pre-commit hooks / VS Code format-on-save | CI Pipeline PR gate | GitHub branch policy blocks merging if CI fails |

## 7. File-by-File Patch Plan
1. **`ssot/azure/azure_devops.yaml`**: Define the ADO configuration explicitly.
2. **`.vscode/tasks.json`**: Add deterministic execution commands.
3. **`.vscode/launch.json`**: Add Odoo Python debugging.
4. **`Makefile`**: Universal bridge for `lint`, `test`, `plan`, `apply`.
5. **`.azure/pipelines/pr-validation.yml`**: CI pipeline triggered by GitHub PRs.
6. **`.azure/pipelines/cd-deployment.yml`**: Multi-stage CD pipeline triggered by `main` merges.

## 8. Validation Checklist
- [ ] DevContainers build and launch correctly in VS Code.
- [ ] VS Code `tasks.json` can execute `make lint` without errors.
- [ ] Azure Boards can successfully link to a GitHub PR via the `AB#<id>` syntax.
- [ ] Opening a GitHub PR triggers the ADO `pr-validation.yml` pipeline.
- [ ] The ADO pipeline successfully executes the exact same `make lint` target used locally.
- [ ] Merging to `main` triggers `cd-deployment.yml` and successfully pauses at the `staging` environment approval gate.

## 9. Azure Pipelines Role

> **Ref**: [Azure Pipelines](https://azure.microsoft.com/en-us/products/devops/pipelines/)

Azure Pipelines is the governed CI/CD and release-execution plane. It owns build,
test, packaging, deployment stages, approvals, and deployment evidence.

| Capability | Detail |
|-----------|--------|
| Cross-platform agents | Linux, macOS, Windows (Microsoft-hosted or self-hosted) |
| Container-native jobs | Build and test inside container images for environment consistency |
| Stages, gates, approvals | Multi-stage YAML with environment approval gates per promotion |
| Deployment targets | Azure (ACA, Functions, Databricks) and non-Azure targets |
| GitHub integration | PR checks/statuses reported back to GitHub; AB# traceability |
| Parallel execution | Parallel jobs and test splitting for faster feedback |

**Authority boundaries remain unchanged**:

- GitHub = source control and PR truth
- Azure Boards = planning and execution coordination
- Azure Pipelines = CI/CD and release execution
- Repo docs/SSOT = architecture, governance, contracts, runtime truth

## 10. Risks and Assumptions
- **Assumption**: Microsoft-hosted Ubuntu agents in Azure DevOps have sufficient CPU/RAM to compile Odoo dependencies.
- **Risk**: GitHub and Azure DevOps synchronization limits. If the Azure Boards app loses connection, traceability breaks.
- **Risk**: Environment variables mismatch. Secrets management must strictly rely on Azure Key Vault rather than `.env` files for remote execution.
