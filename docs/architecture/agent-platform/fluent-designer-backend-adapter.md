# Fluent Designer Backend Adapter

## Purpose

Provide a single TypeScript service boundary between the Designer Agent contract and Microsoft Foundry runtime.

## Runtime Model

The adapter targets Foundry's current runtime concepts:
- **agent** — the designer agent identity (reused or created on demand)
- **conversation** — a session context for multi-turn interaction
- **response** — a single agent response within a conversation

No legacy `thread` or `run` concepts are used. This aligns with Microsoft's current migration guidance.

## Architecture

```
HTTP Route (Express)
  → DesignerAgentService
    → FoundryAdapter
      → client.ts     (AIProjectClient wrapper)
      → agents.ts     (ensure/reuse/create agent)
      → execute.ts    (create conversation + response)
      → normalize.ts  (raw text → typed DesignerAgentResponse)
      → errors.ts     (provider error envelope)
```

## Rules

1. No direct SDK calls outside the adapter boundary
2. Normalize all provider responses into repo contracts in `normalize.ts`
3. Preserve correlation IDs and provider metadata in `response.metadata`
4. Allow mock/provider swap without frontend changes
5. Agent reuse strategy: explicit ID → name search → create new
6. All env config through `readDesignerAgentEnv()` — no hardcoded values

## Contracts

### Backend-specific (extends frontend contracts)

```typescript
// DesignerAgentResponse gains metadata field:
metadata: {
  provider: 'mock' | 'foundry';
  agentId?: string;
  conversationId?: string;
  responseId?: string;
  correlationId: string;
}

// DesignerAgentRequest adds:
conversationId?: string;  // reuse existing conversation
correlationId?: string;   // trace correlation
```

### Foundry adapter-specific

```typescript
FoundryAdapterConfig {
  endpoint, projectConnectionString?, modelDeploymentName?,
  agentId?, agentName, timeoutMs
}

FoundryExecutionResult {
  rawText, agentId?, conversationId?, responseId?, finishReason?
}

FoundryAgentEnsureResult {
  agentId, reused
}
```

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `AZURE_FOUNDRY_ENDPOINT` | Yes | — | Foundry project endpoint |
| `AZURE_FOUNDRY_PROJECT_CONNECTION_STRING` | No | — | Alternative connection method |
| `AZURE_FOUNDRY_MODEL_DEPLOYMENT` | No | — | Model deployment name |
| `AZURE_FOUNDRY_DESIGNER_AGENT_ID` | No | — | Explicit agent ID (skip search) |
| `AZURE_FOUNDRY_DESIGNER_AGENT_NAME` | Yes | — | Agent name for search/create |
| `DESIGNER_AGENT_TIMEOUT_MS` | No | 45000 | Request timeout |

## Auth

Uses `DefaultAzureCredential` — managed identity in Azure Container Apps, `az login` locally.

## Error Handling

| Error | Code | When |
|-------|------|------|
| `DesignerAgentProviderError` | `DESIGNER_AGENT_PROVIDER_ERROR` | Foundry call fails |
| `DesignerAgentResponseParseError` | `DESIGNER_AGENT_RESPONSE_PARSE_ERROR` | Response JSON parse fails |

## Output Format Rule

The backend adapter emits typed JSON only. The following are **invalid** provider outputs and must be rejected by `normalize.ts`:

- Markdown-wrapped JSON (e.g. ```json ... ```)
- Prose preambles before or after the JSON body
- Fenced code blocks of any language
- Partial or streaming text fragments

If the Foundry provider returns any of these, `normalize.ts` will fail schema validation and throw `DesignerAgentResponseParseError`. The prompt sent to the provider explicitly instructs "Return JSON only / No markdown fences" to prevent this.

## SDK Note

Exact method names in `@azure/ai-projects` preview SDK may shift. Only `client.ts`, `agents.ts`, and `execute.ts` need adjustment if the installed package version differs from docs. The adapter boundary is designed for this.

## Related

- Frontend: `web/apps/designer-agent/` (Next.js + Fluent UI v9)
- Contracts: `web/packages/fluent-designer-contract/`
- Spec: `spec/fluent-designer-agent/`
- SSOT: `ssot/agent-platform/foundry_designer_adapter.yaml`
