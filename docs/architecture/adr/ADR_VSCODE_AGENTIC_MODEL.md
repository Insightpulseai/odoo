# VS Code Agentic Engineering Model

> Version: 1.0.0
> Canonical repo: `docs`

## Context
Developing a complex, composited Azure-native platform (ACA, Databricks, Foundry) as a lean team augmented by AI agents requires an ironclad, reproducible local developer environment. Drift between what the human runs, what the agent runs, and what CI/CD runs will severely degrade productivity.

## Decision
- **Primary Tooling**: VS Code with `.devcontainer` specifications is the absolute mandatory standard for all platform repositories.
- **Agent Execution**: AI coding agents must operate strictly within the bounds of the DevContainer or an authenticated remote runner, ensuring they have access to the exact same CLI tools (Azure CLI, Databricks CLI, Terraform, GH CLI) as the human developer.
- **Control Plane**: Azure DevOps will act as the sole source of truth for repository hosting, pipeline execution, and deployment approvals. GitHub may be used for upstream syncing of open-source components, but all enterprise deployments are gated through ADO.

## Consequences
- "Works on my machine" issues are eliminated. The AI agents are guaranteed a pristine, deterministic CLI and Python environment upon instantiation.
- Platform onboarding for new human engineers or new AI agent capabilities is instant (rebuilding the container).
- The team avoids branching strategy confusion by enforcing Azure Boards -> Azure Repos -> Azure Pipelines traceability.
