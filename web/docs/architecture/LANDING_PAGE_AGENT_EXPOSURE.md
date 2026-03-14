# Landing Page Agent Exposure Architecture

## Purpose
Define the canonical architecture for exposing a public advisory copilot on the InsightPulseAI landing page.

## Status
Canonical. Governs how the public-facing AI assistant is wired from browser to model.

## Canonical Pattern
```
Browser -> Cloudflare Worker (optional edge proxy) -> self-hosted backend adapter -> Azure AI Foundry
```

Each layer has strict ownership boundaries. No layer may absorb responsibilities from another.

## Layer Responsibilities

### Browser (owned by `web`)
- **Launcher**: Button or trigger that opens the copilot interface
- **Chat panel**: Conversation UI rendering messages, typing indicators, error states
- **Prompt chips**: Pre-defined starter prompts the user can click
- **CTA integration**: Call-to-action elements that connect copilot interactions to conversion flows
- **Rendering**: All visual output, accessibility, responsive layout
- **Client-side state**: Conversation history for the current session, UI state

The browser must never hold API keys, model endpoints, or backend credentials. It communicates exclusively with the Worker or backend adapter via HTTPS.

### Cloudflare Worker (optional, owned by `infra`)
- **Edge/API facade**: Public endpoint that the browser calls
- **Request filtering**: Validates request structure, rejects malformed payloads
- **Rate limiting**: Enforces per-client request limits to protect the backend
- **CORS enforcement**: Returns appropriate CORS headers for allowed origins
- **Request forwarding**: Passes validated requests to the self-hosted backend adapter

The Worker is optional. If omitted, the browser calls the self-hosted backend adapter directly (with the backend exposed via Cloudflare DNS/CDN). The Worker adds edge-level protection but is not required for the pattern to function.

The Worker must never hold Foundry credentials, execute prompt logic, or make decisions about response content.

### Self-Hosted Backend Adapter (owned by `odoo` or `ops-platform`)
- **Secret-bearing integration**: Holds Azure AI Foundry API keys and endpoint configuration
- **Mode enforcement**: Ensures the public copilot operates in advisory-only mode (see rules below)
- **Prompt construction**: Assembles the final prompt from user input, system instructions, and mode constraints
- **Response normalization**: Transforms Foundry responses into the format expected by the browser
- **Guardrails**: Applies content filtering, length limits, and safety checks before returning responses
- **Logging and audit**: Records interactions for observability and compliance

### Azure AI Foundry (external managed service)
- **Model inference**: Processes prompts and returns completions
- **Model selection**: Backend adapter chooses the model; Foundry executes

## Public Advisory Mode Rules

The public copilot on the landing page operates under strict advisory-only constraints:

1. **Advisory only**: The copilot provides general information, answers questions about InsightPulseAI capabilities, and offers non-binding guidance. It does not execute actions, create records, or modify state.

2. **No private tenant retrieval**: The public copilot must never access tenant-specific data (customer records, financial data, internal documents). It operates with zero-context about any specific tenant.

3. **No mutations**: The copilot must never trigger writes to any system — no database inserts, no API calls that modify state, no workflow triggers. Read-only, advisory responses only.

4. **No internal system exposure**: Responses must not reveal internal architecture, database schemas, API endpoints, or operational details.

5. **Graceful boundaries**: When asked about topics outside its advisory scope, the copilot directs users to appropriate channels (contact form, sales team, documentation) rather than attempting to answer.

## Repo Ownership

| Concern | Owner Repo | Rationale |
|---------|-----------|-----------|
| Copilot UI components (launcher, chat panel, prompt chips) | `web` | Browser-side rendering and interaction |
| Worker deployment and configuration | `infra` | Edge infrastructure is an `infra` concern |
| Worker route and environment contract | `infra` | Per `infra/cloudflare/workers/env-contract.md` |
| Backend adapter service | `odoo` or `ops-platform` | Secret-bearing backend logic on self-hosted infra |
| Foundry contracts (prompts, models, modes) | `agents` | Prompt engineering and model configuration |
| Foundry evaluation and scoring | `agents` | Quality assurance for model outputs |

## Anti-Patterns

### Browser Calling Foundry Directly
```
Browser -> Azure AI Foundry  // BANNED
```
This exposes API keys to the browser. All Foundry communication must go through the self-hosted backend adapter.

### Worker Becoming Sole Backend
```
Browser -> Cloudflare Worker (holds secrets, runs logic) -> Azure AI Foundry  // BANNED
```
Workers are edge proxies, not application backends. Secrets and core logic belong on self-hosted infrastructure per the hosting policy.

### Public Assistant Using Private Context
```
Browser -> Backend -> Foundry (with tenant-specific RAG context)  // BANNED for public copilot
```
The public landing page copilot must never have access to private tenant data. Tenant-specific copilot features are a separate, authenticated product surface.

### Hardcoded Prompts in Browser
```javascript
// BANNED — prompt construction belongs in the backend adapter
const systemPrompt = "You are an InsightPulseAI advisor...";
fetch(endpoint, { body: JSON.stringify({ prompt: systemPrompt + userInput }) });
```
System prompts and mode constraints are backend concerns. The browser sends user input only.

### Worker Holding Model Credentials
```javascript
// BANNED — credentials belong on self-hosted backend
const FOUNDRY_KEY = env.AZURE_AI_KEY;
const response = await fetch("https://foundry.azure.com/...", {
  headers: { "Authorization": `Bearer ${FOUNDRY_KEY}` }
});
```
Even if injected via Wrangler secrets, Foundry credentials should not live at the edge. The Worker forwards to the backend adapter, which holds credentials.
