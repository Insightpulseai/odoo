# AI Platform

> **Benchmark**: Microsoft Foundry
> **Canonical source**: `platform/docs/ai-platform/` and `agents/docs/ai-platform/`

## Purpose

Cross-repo entry point for the AI platform documentation family. Full content lives in the subsystem directories that own the executable truth.

## Doc Ownership

| Topic | Canonical Location | Owner |
|---|---|---|
| AI platform operating model (full) | [platform/docs/ai-platform/index.md](../../../platform/docs/ai-platform/index.md) | `platform` |
| Foundry control plane | `platform/docs/ai-platform/foundry-control-plane.md` | `platform` |
| Retrieval and grounding | `platform/docs/ai-platform/retrieval-and-grounding.md` | `platform` |
| AI safety and operations | `platform/docs/ai-platform/ai-safety-and-operations.md` | `platform` |
| Agent runtime patterns | `agents/docs/ai-platform/agent-runtime-patterns.md` | `agents` |
| Model orchestration boundaries | `agents/docs/ai-platform/model-orchestration-boundaries.md` | `agents` |

## Benchmark Position

| Foundry Capability | IPAI Equivalent | Status |
|---|---|---|
| Model catalog and deployment | Azure OpenAI + Foundry project | Operational |
| Agent runtime | `agent-platform/` + copilot gateway | Partial |
| Grounding and retrieval | AI Search + knowledge bases | Scaffold |
| Evaluation and red-teaming | `agents/evals/` | Scaffold |
| Safety and content filtering | Azure AI Content Safety | Not started |
| Governance and model inventory | SSOT bridge matrix | Scaffold |

## Key Rule

All AI runtime, orchestration, and model logic stays **outside Odoo addons**. Odoo surfaces are thin connectors only. See `ssot/odoo/custom_module_policy.yaml`.

## Related Documents

- `docs/architecture/ODOO_ON_AZURE_REFERENCE_ARCHITECTURE.md` — Layer 6
- `docs/odoo-on-azure/reference/doc-authority.md` — ownership model

---

*Created: 2026-04-05 | Version: 1.0*
