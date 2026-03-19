# Builder Surfaces

> Defines the three canonical builder surfaces and their roles in the InsightPulseAI platform.

---

## 1. Foundry Web (Browser)

**Role**: Primary agent-builder UI

**What you do here**:
- Create and manage Foundry projects
- Build agent workflows (visual + code)
- Deploy and test models
- Run eval suites
- View traces and monitoring dashboards
- Manage project-scoped API keys and endpoints

**Auth**: Entra SSO via Azure Portal

**URL**: Azure AI Foundry portal (project-scoped)

**When to use**: Agent design, workflow authoring, eval review, model selection, production monitoring.

---

## 2. VS Code (Local)

**Role**: Repo + local runtime + extension-assisted control

**What you do here**:
- Edit repo code (modules, contracts, configs, specs)
- Run local dev stack (devcontainer, Docker Compose)
- Use Azure extensions for resource visibility
- Use Foundry extension for project-scoped operations
- Run Claude Code / Copilot for assisted development
- Execute MCP-based automation

**Auth**: Entra app registration (see `docs/contracts/foundry-vscode-auth-contract.md`)

**Required extensions**:
- Azure Account
- Azure Resources
- Azure AI Foundry
- Azure DevOps (Boards)
- Docker
- Remote - Containers (devcontainer)

**When to use**: All code changes, local testing, CI prep, contract editing, spec kit authoring.

---

## 3. MCP (Automation/Control)

**Role**: Programmatic control surface for agents and pipelines

**What you do here**:
- Automate Azure resource operations (deploy, scale, configure)
- Automate Azure DevOps work item management (create, update, link)
- Automate Foundry project operations (run evals, deploy agents)
- Run browser automation (Playwright) for E2E testing
- Execute pipeline stages that need Azure context

**Auth**: Service principal or managed identity (see MCP baseline)

**Baseline**: `ssot/agents/mcp-baseline.yaml`

**When to use**: CI/CD pipelines, agent-driven operations, automated testing, scheduled maintenance.

---

## Surface boundaries

| Operation | Surface |
|-----------|---------|
| Design an agent workflow | Foundry Web |
| Write module code | VS Code |
| Run eval suite | Foundry Web or MCP (automated) |
| Create Azure Boards work item | VS Code (extension) or MCP |
| Deploy to staging | MCP (pipeline-triggered) |
| Review eval traces | Foundry Web |
| Edit a contract doc | VS Code |
| Run E2E tests | MCP (Playwright) |
| Monitor production agent | Foundry Web |
| Approve production release | Azure Pipelines (ManualValidation) |

---

## Anti-patterns

- Using Slack/chat as the primary control surface for deployments or releases
- Using the Azure Portal directly for resource changes without repo commit
- Using Foundry Web for code editing (use VS Code)
- Using VS Code for agent workflow design (use Foundry Web)
- Running MCP servers that are not in `ssot/agents/mcp-baseline.yaml`

---

## Cross-references

- `docs/contracts/foundry-vscode-auth-contract.md` — auth paths
- `ssot/agents/mcp-baseline.yaml` — MCP requirements
- `ssot/runtime/live-builder-surfaces.yaml` — current live surface inventory
- `docs/architecture/idea-to-release-pipeline.md` — where surfaces fit in the delivery pipeline

---

*Last updated: 2026-03-17*
