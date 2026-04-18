# Foundry Adoption Matrix — Per Repo

> Short reference: which Microsoft resource applies to which IPAI repo. Maps
> the Azure AI Foundry SDK (application contract) and the "Deploy Your AI
> Application in Production" accelerator (infrastructure contract) to IPAI's
> repo structure.

---

## Endpoints in use

```
Foundry project endpoint:
  https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot

OpenAI-compatible endpoint:
  https://ipai-copilot-resource.openai.azure.com/openai/v1
```

## Matrix

| IPAI repo / path | Microsoft reference | What to adopt | What to skip |
|---|---|---|---|
| `agent-platform/` | [Azure AI Foundry SDK overview](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview) | Foundry SDK 2.x preview for Python; project endpoint for runtime; unified tool access | Hub-based projects (deprecated pattern) |
| `agents/` | Foundry SDK | Agent definitions, skills, prompt contracts, evals | Infra deployment code |
| `platform/` | [Deploy Your AI Application in Production](https://github.com/microsoft/deploy-your-ai-application-in-production) | Foundry account + project + vNet isolation baseline; WAF-aligned composition | Anything that would duplicate existing Sub A infra |
| `infra/` | Production accelerator (same repo) | Bicep modules for network isolation, private endpoints, managed identity, Key Vault wiring | Whole-repo copy — adapt only the pieces you need for Foundry runtime |
| `addons/` + `odoo18/` | Neither reference applies | N/A — Odoo stays separate | Don't force Odoo into Foundry templates |
| `data-intelligence/` | Neither reference applies | N/A — Databricks+Unity stays separate | Don't move data-engineering workloads into Foundry production repo |
| `apps/` | Foundry SDK (for Pulser-consuming apps) | OpenAI-compatible endpoint when app uses `openai` library directly | Foundry project endpoint unless unified access needed |

## Endpoint selection rule

```
Default for Pulser runtime (agent-platform, agents):
  Foundry project endpoint
  (unified access to models + tools + project-scoped Foundry capabilities)

Use OpenAI-compatible endpoint when:
  - existing code uses `openai` Python library unchanged
  - third-party library expects openai/v1 surface
  - you want model calls decoupled from Foundry project context
```

## Adoption sequence (recommended, T-150 from today)

1. **Week 1** — stand up `agent-platform/pulser-core` using Foundry SDK 2.x preview + Foundry project endpoint. Reference existing `ipai-copilot-resource` + `ipai-copilot` project.
2. **Week 2-3** — fork relevant Bicep modules from the production accelerator into `infra/finops-hub/vendor/` OR `infra/foundry-prod/vendor/`. Do NOT adopt whole-repo — copy only the modules you need (vNet isolation, private endpoints, managed identity role assignments).
3. **Week 4** — deploy Foundry production-hardened environment as Sub B `536d8cf6` overlay. Validate with smoke test from pulser-core.
4. **Week 5+** — migrate existing `ipai-copilot-resource` from Sub A dev posture to Sub B production posture (or dual-run with clean cutover).

## Boundary summary — never merge these

| Plane | Repo | Don't do |
|---|---|---|
| Agent runtime | `agent-platform/` | Put Odoo connection strings into Foundry project config |
| Agent definitions | `agents/` | Ship business rules that should live in Odoo |
| Production infra | `infra/` + `platform/` | Adopt the production repo for non-Foundry workloads (e.g., Odoo hosting) |
| Business SoR | `addons/` + `odoo18/` | Force Odoo runtime into Foundry vNet template |
| Analytics plane | `data-intelligence/` | Move Databricks workloads into Foundry production repo |

Odoo and Databricks have their own production patterns. The Foundry production accelerator is specifically for the Foundry/agent layer.

## Decision checkpoint

Use this adoption matrix as a gate when any new Microsoft reference hits your feed. Ask:

1. Does this replace a layer I already have? (Odoo? Databricks?) → Skip.
2. Does this harden the agent layer? → Evaluate for `agent-platform/` + `infra/`.
3. Does this extend the SDK surface for Pulser? → Evaluate for `agents/`.
4. Otherwise → Log as reference, don't adopt.

## References

- [Azure AI Foundry SDK overview](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview)
- [microsoft/deploy-your-ai-application-in-production](https://github.com/microsoft/deploy-your-ai-application-in-production)
- `docs/architecture/plane-separation.md` — 4-plane model (agent-platform lives in the AI access / runtime layer)
- `docs/architecture/ipai-governance-model.md` — adoption sits inside the Engineering execution layer
- CLAUDE.md Invariants #10, #11, #22, #23 (MCP first, SaaS authority, Odoo adoption, execution doctrine)
