# Foundry Project Baseline

> Authority:
> - `platform/contracts/foundry/endpoints.yaml`
> - `platform/contracts/foundry/auth-policy.yaml`
>
> Scope: current canonical endpoint baseline for the `ipai-copilot` Foundry project.

## Current baseline

As of 2026-04-23, the current Foundry project coordinates are:

| Field | Value |
|---|---|
| Project name | `ipai-copilot` |
| Foundry resource | `ipai-foundry-sea` |
| Project endpoint | `https://ipai-foundry-sea.services.ai.azure.com/api/projects/ipai-copilot` |
| Azure OpenAI-compatible base URL | `https://ipai-foundry-sea.openai.azure.com/openai/v1` |

These values are the canonical endpoint contract for the current project baseline.

## What this baseline proves

- The Foundry project exists.
- The project-scoped endpoint is known.
- The Azure OpenAI-compatible base URL is known.
- Portal/API-key bootstrap is available for validation.

## What this baseline does not prove

- AI Toolkit can enumerate project connections.
- The signed-in principal has the required Azure RBAC on the Foundry resource/project.
- Every repo and client is already aligned to the same endpoint/auth contract.

Those are separate authorization and client-configuration concerns.

## Endpoint discipline

Use the project endpoint for:

- project-native APIs
- connection inventory
- agent/project-scoped tool operations

Use the Azure OpenAI-compatible base URL for:

- OpenAI SDK clients
- model inference on the Azure OpenAI surface
- embeddings and chat/completions clients that expect `/openai/v1`

Do not mix the two surfaces interchangeably.

## Known legacy drift

Older repo docs still reference `ipai-copilot-resource` as the Foundry resource and endpoint base.
That legacy documentation is not rewritten here. This runbook and
`platform/contracts/foundry/endpoints.yaml` are the narrow current-state authority until the
older references are reconciled.

## Verification focus

When a client still fails after endpoint alignment, check these in order:

1. Tenant context
2. Subscription context
3. Project endpoint selection
4. Ability to read project connections
5. Chosen auth mode against the client policy
