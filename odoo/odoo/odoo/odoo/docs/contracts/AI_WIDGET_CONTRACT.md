# AI Widget — Bridge Contract

**Version**: 1.0.0
**Status**: Active
**Owner**: Platform Engineering
**SSOT**: `ssot/bridges/catalog.yaml#ipai_ai_widget`

---

## Request (Odoo → IPAI bridge)

```http
POST {ipai_ai_widget.bridge_url}
Content-Type: application/json

{"prompt": "<string, non-empty>"}
```

## Response (IPAI bridge → Odoo)

**Success (200)**:
```json
{
  "provider": "gemini",
  "text": "<LLM response>",
  "model": "gemini-2.0-flash-preview",
  "trace_id": "<uuid>",
  "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
}
```

**Failure (503 — key missing on bridge side)**:
```json
{"error": "GEMINI_API_KEY_MISSING", "hint": "Set GEMINI_API_KEY in Vercel env vars"}
```

## Error codes returned by Odoo controller

| Code | HTTP | Meaning |
|------|------|---------|
| `PROMPT_REQUIRED` | 400 | Empty or missing prompt |
| `BRIDGE_URL_NOT_CONFIGURED` | 503 | `ir.config_parameter` `ipai_ai_widget.bridge_url` is unset |
| `AI_KEY_NOT_CONFIGURED` | 503 | Bridge returned 503 (GEMINI_API_KEY missing on Vercel) |
| `BRIDGE_TIMEOUT` | 504 | Bridge did not respond in 30s |
| `BRIDGE_ERROR` | 500 | Any other bridge-side or network failure |

## Configuration

| Setting | Store | Value |
|---------|-------|-------|
| Bridge URL | `ir.config_parameter` key `ipai_ai_widget.bridge_url` | `https://ops.insightpulseai.com/api/ai/gemini` |
| API key | Vercel env var `GEMINI_API_KEY` | Registered in `ssot/secrets/registry.yaml#gemini_api_key` |

## Security

- Route `POST /ipai/ai/ask` requires `auth='user'` (authenticated Odoo session)
- No API key is stored in Odoo or passed through Odoo — key lives in Vercel env
- CSRF is disabled on JSON-RPC route (Odoo convention for type=json)

## No-IAP contract

`grep -r "iap" addons/ipai/ipai_ai_widget/` must return 0 matches.
Enforced by CI (planned T-7 in spec/ai-bridge/tasks.md).
