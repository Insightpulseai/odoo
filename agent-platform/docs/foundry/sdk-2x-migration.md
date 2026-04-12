# Foundry SDK 2.x Migration — IPAI canonical reference

> **Canonical state:** `ipai-copilot-resource` is on the **new Foundry portal**. All clients must use SDK 2.x (`azure-ai-projects>=2.0.0`, `@azure/ai-projects@^2.0.1`).

## IPAI-specific endpoints

| Purpose | Endpoint |
|---|---|
| Foundry SDK (project) | `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot` |
| OpenAI-compat (raw OpenAI SDK / `ANTHROPIC_BASE_URL`) | `https://ipai-copilot-resource.openai.azure.com/openai/v1` |
| Auth scope | `https://ai.azure.com/.default` |
| Tools endpoint (OCR / Language / Content Safety) | `https://ipai-copilot-resource.cognitiveservices.azure.com` |

## What changed from 1.x

| | Classic 1.x (old) | New 2.x (current) |
|---|---|---|
| Package | `azure-ai-projects==1.0.0` | `azure-ai-projects>=2.0.0` |
| Project endpoint | `https://<res>.cognitiveservices.azure.com/` | `https://<res>.services.ai.azure.com/api/projects/<project>` |
| OpenAI-compat path | `<res>.openai.azure.com` | `<res>.openai.azure.com/openai/v1` |
| Auth | API key common | DefaultAzureCredential / MI only (keyless) |

## SDK choice matrix

| IPAI use case | SDK | Endpoint |
|---|---|---|
| `copilot_gateway.py` model calls | Foundry SDK 2.x (`AIProjectClient`) | `services.ai.azure.com/api/projects/ipai-copilot` |
| `azure-foundry-client.ts` (TypeScript) | `@azure/ai-projects@^2.0.1` | same |
| Claude Code (non-Max devs) | OpenAI SDK compat via `ANTHROPIC_BASE_URL` env | `openai.azure.com/openai/v1` |
| `ipai-pg-mcp-server` agent | Foundry SDK 2.x | same project endpoint |
| `pulser-rag-wire` (Azure AI Search) | `azure-search-documents` | Search-specific endpoint |
| `ipai-ocr-dev` (Document Intelligence) | `azure-ai-documentintelligence` | `cognitiveservices.azure.com` |

**Rule:** OCR, Language, Content Safety still use `cognitiveservices.azure.com` regardless of SDK version. Only model calls and agent orchestration move to `services.ai.azure.com`.

## Canonical `copilot_gateway.py` (SDK 2.x)

```python
# agents/copilot_gateway.py
# Foundry SDK 2.x — AIProjectClient + keyless DefaultAzureCredential
# Resource: ipai-copilot-resource | Project: ipai-copilot | RG: rg-data-intel-ph | East US 2

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

FOUNDRY_ENDPOINT = (
    "https://ipai-copilot-resource.services.ai.azure.com"
    "/api/projects/ipai-copilot"
)

project_client = AIProjectClient(
    endpoint=FOUNDRY_ENDPOINT,
    credential=DefaultAzureCredential()
)

def get_openai_client():
    """OpenAI-compatible client scoped to the IPAI Foundry project.
    Use for: model calls (Claude Sonnet/Haiku via Responses API), agent evals.
    NOT for: direct Anthropic API calls — those go via Claude Code Max."""
    return project_client.get_openai_client()

def call_model(deployment: str, prompt: str) -> str:
    with get_openai_client() as client:
        response = client.responses.create(
            model=deployment,   # e.g. "claude-sonnet-4-6" or "claude-haiku-4-5"
            input=prompt,
        )
        return response.output_text
```

## Infrastructure patches

### 1. Dockerfile pin (all ACA containers that call Foundry)

```dockerfile
# ipai-copilot-gateway, ipai-mcp-dev, agents/*
RUN pip install "azure-ai-projects>=2.0.0" azure-identity --no-cache-dir
```

TypeScript services:
```json
"dependencies": {
  "@azure/ai-projects": "^2.0.1",
  "@azure/identity": "^4.x"
}
```

### 2. Non-Max dev `settings.local.json`

Already updated in:
- `docs/setup/settings.local.template.json`
- `docs/developer-setup/settings.local.template.json`
- `docs/setup/vscode-setup.md`

Canonical value: `https://ipai-copilot-resource.openai.azure.com/openai/v1`

### 3. RBAC — least privilege

Managed identities on `ipai-copilot-gateway` and `ipai-odoo-dev-worker` should have **Azure AI User** on the `ipai-copilot` project, not Contributor.

Verify:
```bash
az role assignment list \
  --scope "/subscriptions/536d8cf6-89e1-4815-aef3-d5f2c5f4d070/resourceGroups/rg-data-intel-ph/providers/Microsoft.CognitiveServices/accounts/ipai-copilot-resource/projects/ipai-copilot" \
  --query "[].{principal:principalName, role:roleDefinitionName}" -o table
```

Reassign if wrong:
```bash
az role assignment create \
  --assignee-object-id <mi-principal-id> \
  --assignee-principal-type ServicePrincipal \
  --role "Azure AI User" \
  --scope "/subscriptions/.../projects/ipai-copilot"
```

## Migration checklist

- [x] Update `settings.local.template.json` (both locations) to `ipai-copilot-resource.openai.azure.com/openai/v1`
- [x] Update `docs/setup/vscode-setup.md` snippet
- [x] Add CI guard (`.github/workflows/foundry-name-guard.yml`) for old name + 1.x endpoint regressions
- [ ] **Migrate `web/ipai-landing/server.ts` from Assistants API → Responses API** (see section below)
- [ ] Audit all Dockerfiles for `azure-ai-projects>=2.0.0` pin
- [ ] Audit all Python sources for `AIProjectClient` instantiation (endpoint must use `services.ai.azure.com/api/projects/ipai-copilot`)
- [ ] Audit TypeScript sources for `@azure/ai-projects@^2.0.1` pin
- [ ] Run RBAC verification command above; downgrade any Contributor assignments to Azure AI User
- [ ] Register `ipai-copilot` in Foundry Control Plane with explicit quota limits per deployment

---

## Terminology migration (brand + API surface)

The rebrand to **Microsoft Foundry** is complete. Legacy terms to retire from docs and code comments:

| Deprecated | Current | Where IPAI still uses it |
|---|---|---|
| Azure AI Foundry / Azure AI Studio | Microsoft Foundry | docs, `copilot_gateway.py` comments |
| Azure AI Services | Foundry Tools | `ipai-ocr-dev` is a Foundry Tool client |
| Assistants API (threads/messages/runs) | Responses API (conversations/items/responses) | `web/ipai-landing/server.ts` L87-L128 ⚠️ |
| Monthly `api-version` query param | `/openai/v1` stable routes | `AZURE_OPENAI_API_VERSION` env var often unnecessary with SDK 2.x |
| Hub + Azure OpenAI + AI Services (three resources) | Single Foundry resource with projects | Already correct — `ipai-copilot-resource` / `ipai-copilot` |
| `azure-ai-inference`, `azure-ai-ml` | `azure-ai-projects>=2.0.0` | audit agent container requirements |

---

## Responses API migration (critical)

**Old (Assistants API — deprecated):**
```typescript
// Create thread
const thread = await fetch(`${baseUrl}/threads?api-version=${apiVersion}`, ...);
// Post message
await fetch(`${baseUrl}/threads/${threadId}/messages?api-version=${apiVersion}`, {
  body: JSON.stringify({ role: 'user', content: message })
});
// Run the assistant + poll
const run = await fetch(`${baseUrl}/threads/${threadId}/runs?api-version=${apiVersion}`, {
  body: JSON.stringify({ assistant_id: agentId, instructions: SYSTEM_PROMPT })
});
while (run.status === 'queued' || run.status === 'in_progress') { await sleep(500); ... }
```

**New (Responses API via Foundry SDK 2.x):**
```typescript
import { AIProjectClient } from '@azure/ai-projects';
import { DefaultAzureCredential } from '@azure/identity';

const project = new AIProjectClient(
  'https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot',
  new DefaultAzureCredential()
);
const openai = project.getOpenAIClient();

const response = await openai.responses.create({
  model: 'claude-sonnet-4-6',
  input: [
    { role: 'system', content: SYSTEM_PROMPT },
    { role: 'user', content: message }
  ]
});
// response.output_text
```

**Why this matters for IPAI:**
- Responses API is stateless by default — no thread/run state to poll or clean up
- Conversation state lives in `ops.run_events` via `pulser-run-trace`, not in Foundry-managed threads
- No `api-version` coupling — stable `/openai/v1` route
- Lower latency (no polling loop)

**Files to migrate:**
- `web/ipai-landing/server.ts` (confirmed Assistants API usage at lines 87-128)
- `documentation/server.ts` (audit)
- Any other `threads/runs` calls surfaced by the CI guard

---

## Playground as prototyping surface (do not wire direct to gateway)

The Agents playground at `ai.azure.com` → Project `ipai-copilot` is the correct prototyping surface **before** anything reaches `ipai-copilot-gateway`.

Workflow:
```
Foundry portal → ai.azure.com → Project: ipai-copilot
  → Build → Models → deploy claude-sonnet-4-6
  → Agents playground (prototype tool config, knowledge, memory)
  → "Open in VS Code for the Web" → verify code pattern
  → Promote to copilot_gateway.py with DefaultAzureCredential
```

**Rules:**
- **Compare mode** — run `claude-sonnet-4-6` vs `claude-haiku-4-5` side-by-side on Odoo finance / BIR prompts before picking the deployment
- **AgentOps tracing is dev-only** — playground tracing is for validation; production runs MUST emit to `ops.run_events` via `pulser-run-trace`
- **Turn evaluations OFF by default** — playground evaluators are billed against `ipai-copilot` project. Unselect all in the metrics panel unless actively running evals

---

## Document Intelligence endpoint is separate

`ipai-ocr-dev` is a **Foundry Tools** client — its endpoint is **not** the project endpoint:

```
Foundry project endpoint (agents, models, Responses API):
  https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot

Document Intelligence (Foundry Tool):
  https://<doc-intel-resource>.cognitiveservices.azure.com/
```

IPAI Document Intelligence use cases:

| Use case | Model | Output target |
|---|---|---|
| BIR Form 2307 extraction | Prebuilt Financial | Odoo `account.withholding` |
| Invoice/bill parsing | Prebuilt Layout | Odoo `account.move` line items |
| OR receipt capture | Prebuilt Read | Odoo expense entry |
| Custom PO extraction | Custom field extraction | IPAI-trained model |

**RAG chunking path** — Document Intelligence runs on `stipaidevlake/bronze/` PDFs before indexing into Azure AI Search via `pulser-rag-wire`. Preserves table structure and form field labels that plain text extraction loses.

```python
# ipai-ocr-dev canonical pattern — cognitiveservices.azure.com, NOT project endpoint
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential

client = DocumentIntelligenceClient(
    endpoint="https://<doc-intel-resource>.cognitiveservices.azure.com/",
    credential=DefaultAzureCredential()
)
```

---

## Production patterns (missing: Control Plane quotas)

From `microsoft/Deploy-Your-AI-Application-In-Production`:

- **Managed identity everywhere** — no API keys in container specs ✅ already correct
- **Single Foundry resource as control plane** — `ipai-copilot-resource` / `ipai-copilot` ✅ already correct
- **AI gateway layer** — `ipai-copilot-gateway` should enforce rate limiting, cost controls, and structured logging BEFORE requests reach deployments (not pass-through)
- **Observability via App Insights** — `appi-ipai-dev` wired, but structured telemetry (request/response pairs, latency, token counts) must flow to Log Analytics, not just availability pings
- **Control Plane quota registration** — currently missing. Register `ipai-copilot` in the Foundry Control Plane with explicit per-deployment quota limits to prevent runaway inference costs from agent loops.

```bash
# Example quota registration (run after project deployment stabilizes)
az cognitiveservices account deployment create \
  --resource-group rg-data-intel-ph \
  --name ipai-copilot-resource \
  --deployment-name claude-sonnet-4-6 \
  --model-name claude-sonnet-4-6 \
  --model-version <version> \
  --sku-capacity <TPM-limit> \
  --sku-name GlobalStandard
```
