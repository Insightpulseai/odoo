# Examples — sample-to-contract-extraction

## Example 1: Extracting OpenAI + Entra + ACA pattern

**Source sample**: `azure-samples/openai-chat-app-entra-auth-builtin`

**Pattern identified**: Keyless Azure OpenAI access via Entra authentication on ACA

**Extraction**:
- Core pattern: ACA app → managed identity → Entra token → Azure OpenAI
- Security: managed identity (yes), VNet (optional), keyless (yes)
- Language-neutral: pattern works in Python, C#, TypeScript, Java
- Platform deviation: sample uses App Service; we use ACA

**Contract output**:
```markdown
# Contract: OPENAI_ENTRA_KEYLESS_ACCESS

## Source
- Sample: openai-chat-app-entra-auth-builtin
- URL: https://github.com/azure-samples/openai-chat-app-entra-auth-builtin
- Retrieved: 2026-03-17

## Pattern
Application on ACA uses system-assigned managed identity to obtain
Entra token for Azure OpenAI access. No API key needed.

## Guardrails
- Managed identity must have "Cognitive Services OpenAI User" role
- Token scope: https://cognitiveservices.azure.com/.default
- Never fall back to API key auth in production
```

---

## Example 2: Extracting Functions + Cosmos DB change feed pattern

**Source sample**: `azure-samples/functions-cosmosdb-change-feed`

**Pattern identified**: Cosmos DB change feed processing via Azure Functions

**Extraction**:
- Core pattern: Cosmos change feed → Functions trigger → process → write
- Security: managed identity for Cosmos access (check sample)
- Language-neutral: trigger binding is declarative
- Platform deviation: sample may use connection string — adapt to managed identity

---

## Anti-pattern: Adopting sample wholesale

**Wrong**: Copy entire sample repo into platform, customize in place
**Right**: Extract the pattern (3-5 sentences), write a contract, implement from contract
