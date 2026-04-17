# Architectural Doctrine: Microsoft Foundry SDK Validation

**Status:** Canonical (Adopted 2026-04-14)
**Scope:** Pulser Agent Plane / Control Code
**Source Authority:** Microsoft Learn (Foundry SDKs and Endpoints, v2.0+)

## Context

Microsoft's architectural split between Azure OpenAI and Azure AI Foundry requires explicit doctrine around SDK usage for the Pulser agent runtime. An Azure OpenAI resource provides only the `/openai/v1` endpoint. An **Azure AI Foundry resource** (`Microsoft.MachineLearningServices/workspaces`) provides unified endpoints for models, agents, tools, and tracing.

## Decision: Dual-Client SDK Architecture

The Pulser Agent Plane will adopt the **Foundry SDK** (`azure-ai-projects >=2.0.0`) as its canonical architectural dependency, effectively replacing legacy `openai` or `Semantic Kernel` boilerplate.

Our architecture mandates the **Dual-Client Pattern** exposed by the Foundry SDK:

1. **Project Client (`AIProjectClient`)**
   - **Endpoint:** `https://<resource-name>.services.ai.azure.com/api/projects/<project-name>`
   - **Usage:** Configuration, enabling app telemetry/tracing, managing Foundry Agent Service, and running batch evaluations.
   
2. **OpenAI-Compatible Client (`project_client.get_openai_client()`)**
   - **Endpoint:** Served centrally via the project routing matrix.
   - **Usage:** Chat Completions API, running models (including Foundry direct models), and interacting with the `microsoft/agent-framework`.

## Execution Enforcement

- **Python Requirement:** `pip install "azure-ai-projects>=2.0.0"`
- **Authentication:** Must use `DefaultAzureCredential` scoped to Entra ID (role: `Azure AI User` or `Azure AI Project Manager`). API keys are strictly forbidden in production.
- **Agent Framework Hook:** When initializing the `microsoft/agent-framework`, pass the `project_client` context so all underlying telemetry and evaluations are automatically captured in Foundry.

## Excluded Paths

- Do NOT directly instantiate the standalone `openai` client (`from openai import OpenAI`) configured to a bare `https://<resource-name>.openai.azure.com` base URL. This bypasses Foundry telemetry and agent tools.
- Do NOT use legacy `1.x` classic SDKs.

*This doctrine binds the Pulser backend directly to the unified project ecosystem, ensuring agents are traceable and evaluations are centralized.*
