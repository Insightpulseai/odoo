# Azure AI Security and Responsible AI Baseline

Reference source:
- `jamesmcroft/Security-and-Responsible-AI-Guide`

This reference informs:
- Pulser policy defaults
- shared responsible AI judge rules
- release readiness criteria for AI-enabled surfaces
- identity and least-privilege expectations for AI workloads

It is a policy and governance source, not a runtime architecture source.

## Where it lands

| Artifact | Role |
|---|---|
| [platform/ssot/policy/azure-ai-governance-baseline.yaml](../../platform/ssot/policy/azure-ai-governance-baseline.yaml) | Policy principles + control requirements (tool access, identity, observability, governance, content safety) |
| [agents/judges/policy/responsible-ai.manifest.yaml](../../agents/judges/policy/responsible-ai.manifest.yaml) | Shared `responsible_ai_judge` with 4 rule predicates |
| [platform/ssot/agents/pulser-pack-matrix.yaml](../../platform/ssot/agents/pulser-pack-matrix.yaml) | `responsible_ai_judge` added to shared judges; attached to `pulser_release_ops`, `pulser_identity_ops`, `pulser_prismalab_research` |

## What it does NOT govern

- `agent-platform/` runtime structure
- `addons/` (Odoo) data model
- `web/apps/` topology
- `platform/` runtime bindings

## Layering rule

| Source class | Purpose |
|---|---|
| Architecture sources | Azure Architecture Center, Foundry / Agent Framework, IPAI SSOTs |
| Governance sources | Dynamics go-live, **Security and Responsible AI Guide**, Entra/External ID/Agent ID guidance |
| Runtime sources | `agent-platform/`, `platform/`, `agents/` |

Never mix governance docs into runtime design without a clean translation layer — that is exactly the role of `agents/judges/policy/*` and `platform/ssot/policy/*`.

## Related

- Go-live readiness: [`ssot/release/go-live-readiness.yaml`](../../ssot/release/go-live-readiness.yaml)
- Identity matrix: [`ssot/identity/entra-identity-matrix.yaml`](../../ssot/identity/entra-identity-matrix.yaml)
- Directory authority: [`platform/ssot/identity/directory-authority-matrix.yaml`](../../platform/ssot/identity/directory-authority-matrix.yaml)
- Pulser pack matrix: [`platform/ssot/agents/pulser-pack-matrix.yaml`](../../platform/ssot/agents/pulser-pack-matrix.yaml)
