---
name: azure-foundry-architecture
description: Validate and align Foundry project configuration, SDK v2 integration, agent definitions, and model catalog bindings to canonical patterns
version: "1.0"
compatibility:
  hosts: [github-copilot, claude-code, codex-cli, cursor, gemini-cli]
tags: [foundry, architecture, governance, evals]
---

# azure-foundry-architecture

**Impact tier**: P1 -- Operational Readiness

## Purpose

Validate and align the Azure AI Foundry project configuration, SDK integration,
agent definitions, and model deployments against Microsoft Learn canonical
patterns. Covers Foundry project structure, agent service, SDK v2 Python,
model catalog bindings, and tool registration. Ensures the `ipai-copilot`
project and its agents are configured to the current SDK v2 contract and not
relying on deprecated v1 patterns.

## When to Use

- After a Foundry SDK upgrade or model deployment change.
- When agent registrations fail or return unexpected tool-binding errors.
- Before shipping any agent to production that uses Foundry Agent Service.
- During architecture reviews of the AI platform lane.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `ssot/agent-platform/foundry_tool_policy.yaml` | Tool preference order, allowed tool types, approval gates |
| `ssot/ai/agents.yaml` | Registered agent definitions, model assignments, tool bindings |
| `ssot/ai/models.yaml` | Model deployment names, versions, regions, quotas |
| `ssot/foundry/runtime_inventory.yaml` | Live Foundry resources, project/resource/endpoint references |
| `scripts/foundry/register_agent_v2.py` | SDK v2 agent registration call signatures, connection strings |
| `docs/architecture/ai/CONSOLIDATION_FOUNDRY.md` | Migration status from v1 classic to v2, pending items |

## Microsoft Learn MCP Usage

Run at least these queries:

1. `microsoft_docs_search("Azure AI Foundry project overview agent service SDK v2")`
   -- retrieves Foundry project structure, agent service concepts, SDK v2 intro.
2. `microsoft_docs_search("Azure AI Foundry Agent Service Python SDK create agent")`
   -- retrieves `AgentsClient`, `create_agent`, tool definitions, thread management.
3. `microsoft_docs_search("Azure AI Foundry model deployments catalog Python")`
   -- retrieves model deployment API, quota management, supported model families.
4. `microsoft_docs_search("Azure AI Foundry project connections managed identity")`
   -- retrieves connection types, credential-free auth via managed identity.
5. `microsoft_docs_search("Azure AI Foundry SDK v2 migration from v1")`
   -- retrieves breaking changes, removed APIs, migration checklist.

Optional:

6. `microsoft_code_sample_search("azure foundry agent python SDK v2", language="python")`
7. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/ai-services/agents/overview")`

## Workflow

1. **Inspect repo** -- Read `ssot/ai/agents.yaml`, `ssot/ai/models.yaml`, and
   `scripts/foundry/register_agent_v2.py`. Record: SDK import paths used
   (`azure.ai.projects` vs `azure.ai.agents`), connection method
   (`AIProjectClient` vs legacy `from_connection_string`), and whether each
   agent has a `model_deployment_name` that matches an entry in `ssot/ai/models.yaml`.
2. **Query MCP** -- Run queries 1-5. Capture the canonical import path for SDK v2,
   the correct `AgentsClient` constructor signature, and the current model catalog
   API shape.
3. **Compare** -- Identify: (a) any `from_connection_string` usage (v1 debt),
   (b) agents referencing model names not in the deployment catalog, (c) tool
   bindings missing `approval: required` for destructive tools, (d) missing
   managed identity credential chain.
4. **Patch** -- Update `scripts/foundry/register_agent_v2.py` to use
   `AIProjectClient` with `DefaultAzureCredential`. Update `ssot/ai/agents.yaml`
   to align agent/model references. Update `ssot/foundry/runtime_inventory.yaml`
   with current endpoint URLs.
5. **Verify** -- Python import check (`python -c "from azure.ai.projects import AIProjectClient"`).
   Lint `register_agent_v2.py` with `ruff`. Confirm no `from_connection_string`
   remains in any `scripts/foundry/*.py` file.

## Outputs

| File | Change |
|------|--------|
| `scripts/foundry/register_agent_v2.py` | SDK v2 migration, credential chain |
| `ssot/ai/agents.yaml` | Align model deployment names, tool bindings |
| `ssot/ai/models.yaml` | Add quota/version metadata if missing |
| `ssot/foundry/runtime_inventory.yaml` | Update endpoint references |
| `docs/architecture/ai/CONSOLIDATION_FOUNDRY.md` | Mark migrated items complete |
| `docs/evidence/<stamp>/azure-foundry-architecture/` | MCP excerpts, diff, lint output |

## Completion Criteria

- [ ] No `from_connection_string` usage in any `scripts/foundry/*.py` file.
- [ ] All agents in `ssot/ai/agents.yaml` reference a model deployment present in `ssot/ai/models.yaml`.
- [ ] `register_agent_v2.py` uses `DefaultAzureCredential` and `AIProjectClient`.
- [ ] Destructive agent tools have `approval: required` in `foundry_tool_policy.yaml`.
- [ ] `ssot/foundry/runtime_inventory.yaml` contains current project, resource, and endpoint entries.
- [ ] `ruff` lints `scripts/foundry/*.py` clean (zero errors).
- [ ] Evidence directory contains MCP excerpts and diff.
