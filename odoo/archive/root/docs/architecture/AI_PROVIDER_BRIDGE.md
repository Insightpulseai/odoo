# AI Provider Bridge — Architecture

> Contract document for InsightPulse AI's provider-agnostic AI integration layer.
> All AI API calls from Ops Console and Odoo modules MUST route through this bridge layer.

---

## Overview

The AI Provider Bridge (`platform/ai/providers/`) is a thin abstraction layer that:
1. Wraps AI provider APIs with a consistent interface
2. Injects API keys from environment variables (never hardcoded)
3. Attaches trace IDs for observability
4. Returns structured, typed responses

---

## Providers

| Provider | Module | Env Var | Model | Status |
|----------|--------|---------|-------|--------|
| Google Gemini | `platform/ai/providers/gemini.ts` | `GEMINI_API_KEY` | `gemini-2.0-flash-preview` | Active |
| (future) OpenAI | `platform/ai/providers/openai.ts` | `OPENAI_API_KEY` | `gpt-4o` | Planned |
| (future) Anthropic | `platform/ai/providers/anthropic.ts` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-6` | Planned |

To add a new provider:
1. Create `platform/ai/providers/<provider>.ts`
2. Export `generateText(prompt: string): Promise<{ text, model, trace_id }>`
3. Add an entry to this table
4. Register `<PROVIDER>_API_KEY` in `ssot/secrets/registry.yaml`
5. Create a corresponding API route in `apps/ops-console/app/api/ai/<provider>/route.ts`

---

## Route Contracts

### POST /api/ai/gemini

**File**: `apps/ops-console/app/api/ai/gemini/route.ts`

**Request**:
```json
{
  "prompt": "string (required, non-empty)"
}
```

**Response (200)**:
```json
{
  "text": "string",
  "model": "gemini-2.0-flash-preview",
  "trace_id": "uuid-v4"
}
```

**Error Responses**:
| Status | Body | Cause |
|--------|------|-------|
| 400 | `{ "error": "prompt is required..." }` | Missing or empty prompt |
| 400 | `{ "error": "Invalid JSON body" }` | Malformed request |
| 500 | `{ "error": "GEMINI_API_KEY env var not set" }` | Missing API key |
| 500 | `{ "error": "Gemini API error: 403 ..." }` | API auth failure |

**Vercel configuration**: `maxDuration: 60` (set in route.ts via `export const maxDuration`)

---

## Security

### API Key Management

API keys are **never** committed to the repository. They are managed through:

| Environment | Store | How to set |
|-------------|-------|-----------|
| Local dev | `.env.local` (gitignored) | Copy from secure store |
| Staging/Preview | Vercel environment variables | Vercel dashboard |
| Production | Vercel environment variables | Same as staging |
| CI (GitHub Actions) | GitHub Actions Secrets | `${{ secrets.GEMINI_API_KEY }}` |

### Secret Registry

All AI provider API key identifiers are registered in `ssot/secrets/registry.yaml`:
- `gemini_api_key` -- Google Gemini API key
- (future) `openai_api_key` -- OpenAI API key

### No Credentials in Logs

The bridge layer MUST NOT log:
- API key values (even partial)
- Request bodies containing sensitive user data
- Error responses that echo back API keys

---

## Thin Odoo Connector (Planned)

A future `ipai_ai_bridge` Odoo module will allow Odoo to call the Gemini bridge:

```python
# EXAMPLE: Future addons/ipai/ipai_ai_bridge/models/ai_mixin.py
import requests

class AIBridgeMixin(models.AbstractModel):
    _name = 'ipai.ai.bridge.mixin'

    def _call_ai(self, prompt: str) -> str:
        bridge_url = self.env['ir.config_parameter'].sudo().get_param(
            'ipai_ai_bridge.url',
            default='https://ops.insightpulseai.com/api/ai/gemini'
        )
        response = requests.post(bridge_url, json={'prompt': prompt}, timeout=60)
        response.raise_for_status()
        return response.json()['text']
```

This keeps Odoo CE clean of direct API dependencies while routing through the
standardized bridge layer.

---

## Observability

Every response includes a `trace_id` (UUID v4) for correlating logs across services.

Future work:
- Emit `trace_id` to Supabase `ops.platform_events` table
- Add latency metrics per provider
- Add token usage tracking (Gemini supports `usageMetadata` in response)

---

## SSOT References

- Secret registry: `ssot/secrets/registry.yaml` -> `gemini_api_key`
- Bridge catalog: `ssot/bridges/catalog.yaml` -> `ipai_ai_tools_bridge`
- EE parity matrix: `ssot/parity/ee_to_oca_matrix.yaml` -> `enterprise_ai` row

---

*Owner: Platform Engineering*
*Last updated: see `git log --oneline -1 docs/architecture/AI_PROVIDER_BRIDGE.md`*
