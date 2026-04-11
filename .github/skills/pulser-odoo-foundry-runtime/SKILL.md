---
name: pulser-odoo-foundry-runtime
description: Validate Foundry-side agent definitions, model baseline, SDK v2 control plane, and runtime governance for Pulser for Odoo
version: "1.0"
compatibility:
  hosts: [github-copilot, claude-code, codex-cli, cursor, gemini-cli]
tags: [foundry, agents, sdk, pulser, runtime, governance, models]
---

# pulser-odoo-foundry-runtime

**Impact tier**: P1 -- Operational Readiness

## Purpose

Validate and maintain the Foundry-side runtime for Pulser for Odoo: canonical
agent naming, minimal model baseline (`gpt-4.1`, `wg-pulser`,
`text-embedding-3-small`), SDK v2 control plane (`AIProjectClient` +
`DefaultAzureCredential`), bounded tool use (File Search before MCP/OpenAPI),
and metadata hygiene (no stale Odoo 19 references). Keeps Foundry minimal,
governed, and clearly subordinate to Odoo as business system of record.

## When to Use

- After any Foundry SDK upgrade, model deployment change, or agent definition edit.
- When agent registrations fail, return stale metadata, or reference wrong models.
- Before promoting any Foundry agent alongside a Pulser for Odoo release.
- When adding a new tool binding to a Pulser agent.

## When Not to Use

- For Odoo module deployment (use `pulser-odoo-deploy`).
- For architecture boundary decisions (use `pulser-odoo-architecture`).
- For grounding/RAG configuration (use `azure-foundry-grounding`).
- When Foundry IQ / AI Search / stored completions are not in the SSOT scope.

## Inputs Expected

- Access to `ssot/ai/agents.yaml`, `ssot/ai/models.yaml`, and Foundry scripts.
- The `AZURE_AI_PROJECT_ENDPOINT` env var (project-scoped, not resource endpoint).
- Managed identity or `DefaultAzureCredential` chain available in the runtime.

## Source Priority

1. Repo SSOT / `ssot/ai/agents.yaml` / `ssot/ai/models.yaml` / release docs
2. Existing architecture anchor docs (`docs/architecture/ai/CONSOLIDATION_FOUNDRY.md`)
3. Microsoft Learn MCP official documentation
4. Official Microsoft GitHub samples only when needed
5. Anything else only if absolutely necessary, clearly marked secondary

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `ssot/ai/agents.yaml` | Agent names, model refs, tool bindings, approval gates |
| `ssot/ai/models.yaml` | Deployment names, model families, versions, regions |
| `ssot/foundry/runtime_inventory.yaml` | Project/resource/endpoint references, live state |
| `ssot/agent-platform/foundry_tool_policy.yaml` | Tool preference order, allowed types, approval gates |
| `ssot/agent-platform/mcp_policy.yaml` | MCP tool scope, allowed servers, approval rules |
| `scripts/foundry/register_agent_v2.py` | SDK v2 import paths, constructor, credential chain |
| `scripts/foundry/run_cloud_eval.py` | Eval dataset, metric thresholds, output path |
| `scripts/foundry/enable_monitoring.py` | Log Analytics workspace ID, diagnostic settings |

## Microsoft Learn MCP Usage

Run at least these queries:

1. `microsoft_docs_search("Azure AI Foundry overview agent service SDK v2 Python")`
   -- retrieves Foundry project structure, agent service, SDK v2 constructor.
2. `microsoft_docs_search("Azure AI Foundry Agent Service create agent Python AIProjectClient")`
   -- retrieves `AIProjectClient`, `create_agent`, tool definitions, thread management.
3. `microsoft_docs_search("Azure AI Foundry grounding Foundry IQ knowledge base optional")`
   -- retrieves when Foundry IQ / AI Search grounding is needed vs optional.
4. `microsoft_docs_search("Azure AI evaluation SDK cloud eval metrics groundedness")`
   -- retrieves eval pipeline, built-in evaluators, score thresholds.
5. `microsoft_docs_search("Azure Monitor AI Foundry diagnostics logging agent observability")`
   -- retrieves diagnostic settings, Log Analytics integration, token usage metrics.

Optional:

6. `microsoft_code_sample_search("azure foundry agent python sdk v2 create thread run", language="python")`
7. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/ai-services/agents/overview")`

## Microsoft Learn MCP Topic Keys

- foundry_overview
- foundry_agent_service
- foundry_iq
- azure_ai_evaluations
- azure_monitor_observability

## Workflow

1. **Inspect repo** -- Read `ssot/ai/agents.yaml`. Record each agent's:
   `name` (must follow canonical Pulser naming), `model_deployment_name` (must
   exist in `ssot/ai/models.yaml`), tool bindings (type, approval gate),
   and any grounding references. Check `scripts/foundry/register_agent_v2.py`
   for SDK import paths and constructor: must use `AIProjectClient(endpoint=...,
   credential=DefaultAzureCredential())`, not `from_connection_string`.
2. **Query MCP** -- Run queries 1-5. Capture: v2 constructor signature,
   grounding optionality guidance, eval pipeline shape, monitoring diagnostic
   categories.
3. **Compare** -- Identify: (a) `from_connection_string` usage (v1 debt);
   (b) agents referencing model names absent from `ssot/ai/models.yaml`;
   (c) any stale "Odoo 19" reference in agent instructions or SSOT (correct
   to Odoo 18); (d) tool bindings missing `approval: required` for Odoo-write
   tools; (e) Foundry IQ / stored completions added without SSOT justification;
   (f) new model deployments beyond the `gpt-4.1` / `wg-pulser` /
   `text-embedding-3-small` baseline without explicit approval.
4. **Patch** -- Replace `from_connection_string` with `AIProjectClient(endpoint=...)`
   in `scripts/foundry/register_agent_v2.py`. Align all agent/model refs in
   `ssot/ai/agents.yaml`. Correct stale Odoo 19 metadata. Add `approval: required`
   to any tool that writes to Odoo. Remove non-baseline model deployments unless
   SSOT explicitly requires them.
5. **Verify** -- Python import check: `python -c "from azure.ai.projects import AIProjectClient"`.
   No `from_connection_string` in any `scripts/foundry/*.py`. Lint with `ruff`.
   All agents in `ssot/ai/agents.yaml` reference a model deployment in
   `ssot/ai/models.yaml`. No Odoo 19 string in any SSOT file.

## Output Contract

| Artifact | Location | Format |
|----------|----------|--------|
| Agent registration script (patched) | `scripts/foundry/register_agent_v2.py` | Python |
| Agent definitions (aligned) | `ssot/ai/agents.yaml` | YAML |
| Model deployments (confirmed) | `ssot/ai/models.yaml` | YAML |
| Runtime inventory (updated) | `ssot/foundry/runtime_inventory.yaml` | YAML |
| Foundry migration status (updated) | `docs/architecture/ai/CONSOLIDATION_FOUNDRY.md` | Markdown |
| Evidence pack | `docs/evidence/<stamp>/pulser-odoo-foundry-runtime/` | Logs + diffs |

## Safety and Guardrails

- Never add model deployments beyond the baseline (`gpt-4.1`, `wg-pulser`,
  `text-embedding-3-small`) without explicit SSOT entry and architecture approval.
- Never use `from_connection_string` or any SDK v1 pattern.
- Never add API key auth. `DefaultAzureCredential` is the only credential type.
- Never add stored completions by default.
- Never force Foundry IQ / AI Search unless `ssot/agent-platform/foundry_tool_policy.yaml`
  explicitly requires grounding for a specific agent.
- Never allow a Foundry agent tool to write Odoo records without `approval: required`.
- Tool preference order (per `foundry_tool_policy.yaml`): File Search > Function Tool /
  OpenAPI > MCP. MCP tools require explicit justification.

## Verification

- [ ] No `from_connection_string` in any `scripts/foundry/*.py`.
- [ ] All agents in `ssot/ai/agents.yaml` reference a model deployment in `ssot/ai/models.yaml`.
- [ ] `register_agent_v2.py` uses `DefaultAzureCredential` and `AIProjectClient(endpoint=...)`.
- [ ] All Odoo-write tools have `approval: required` in `foundry_tool_policy.yaml`.
- [ ] No stale "Odoo 19" string in `ssot/ai/agents.yaml` or agent instruction text.
- [ ] `ruff` lints `scripts/foundry/*.py` clean (zero errors).
- [ ] No non-baseline model deployment without an explicit SSOT entry.
- [ ] Evidence directory contains diffs, lint output, and MCP excerpts.

## Related Skills

- `pulser-odoo-architecture` -- service-plane boundary decisions (consult first)
- `pulser-odoo-deploy` -- Odoo-side deployment doctrine
- `azure-foundry-architecture` -- Foundry SDK v2, agent registration, model catalog
- `azure-ai-evals-governance` -- eval pipelines, content safety, governance gates
- `azure-foundry-grounding` -- RAG/grounding config, KB bindings, retrieval eval

## Completion Criteria

- [ ] No `from_connection_string` usage in any `scripts/foundry/*.py` file.
- [ ] All agents reference model deployments present in `ssot/ai/models.yaml`.
- [ ] All Odoo-write agent tools have `approval: required` gates.
- [ ] No stale Odoo 19 metadata in any SSOT file or agent instruction.
- [ ] Model baseline constrained to `gpt-4.1`, `wg-pulser`, `text-embedding-3-small`.
- [ ] `ruff` lints `scripts/foundry/*.py` clean.
- [ ] `ssot/foundry/runtime_inventory.yaml` contains current project/resource/endpoint.
- [ ] Evidence directory contains MCP excerpts, lint output, and aligned diffs.
