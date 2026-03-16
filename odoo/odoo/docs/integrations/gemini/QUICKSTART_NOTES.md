# Google Gemini API Integration — Quick Start Notes

**Last Updated:** 2026-02-20
**Status:** PRODUCTION-READY (server-side only)
**API Reference:** [Google AI for Developers — Gemini API](https://ai.google.dev/gemini-api/docs/quickstart)

---

## Overview

This document defines the operational contract for integrating Google Gemini API within the InsightPulse AI platform, emphasizing **server-side only execution** (Supabase Edge Functions/workers) with strict secret handling and audit trail requirements.

---

## Environment Contract

### Required Environment Variable

```bash
GEMINI_API_KEY=<your-api-key>
```

**Storage:**
- **Local Dev:** macOS Keychain (`ipai_claude_secrets` service)
- **CI/Remote:** Supabase Vault (`gemini/api_key`)
- **Never:** Committed to git, exposed in client-side code, logged in plaintext

**Rotation Cadence:** 90 days (recommended)

**Verification:**
```bash
# Local (macOS)
security find-generic-password -s ipai_claude_secrets -a GEMINI_API_KEY -w

# Supabase Vault (via Edge Function)
# No direct CLI access - must query via authenticated RPC
```

---

## REST API Contract

### Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/<model>:generateContent
```

**Available Models:**
- `gemini-1.5-pro` (recommended for complex reasoning)
- `gemini-1.5-flash` (faster, cost-optimized)
- `gemini-pro-vision` (multimodal: text + images)

### Request Headers

```http
Content-Type: application/json
x-goog-api-key: ${GEMINI_API_KEY}
```

### Minimal Request Payload

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {"text": "Explain the concept of Systems of Record vs Systems of Truth"}
      ]
    }
  ],
  "generationConfig": {
    "temperature": 0.7,
    "topK": 40,
    "topP": 0.95,
    "maxOutputTokens": 1024
  }
}
```

### Response Structure

```json
{
  "candidates": [
    {
      "content": {
        "role": "model",
        "parts": [
          {"text": "A System of Record (SOR) is..."}
        ]
      },
      "finishReason": "STOP"
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 15,
    "candidatesTokenCount": 234,
    "totalTokenCount": 249
  }
}
```

---

## SSOT/SOR Boundary Notes

### Gemini API Integration Category

**Classification:** **SSOT Extension Surface** (AI/ML tool layer)

**Rationale:**
- Gemini API is a **generative AI capability**, not an authoritative source of truth or ledger
- Used for: analysis, summarization, content generation, code assistance
- Not used for: accounting postings, ERP transactions, legal audit artifacts

### Boundary Rules

| **Capability** | **Allowed** | **Forbidden** |
|---------------|-------------|---------------|
| Text generation | ✅ SSOT (operational content) | ❌ SOR (invoices, journal entries) |
| Code assistance | ✅ SSOT (developer tools) | ❌ SOR (critical business logic) |
| Summarization | ✅ SSOT (analytics, insights) | ❌ SOR (authoritative financial reports) |
| Data enrichment | ✅ SSOT (category suggestions, tags) | ❌ SOR (canonical master data) |

**Conflict Policy:**
- Gemini-generated content MUST NOT be written directly to Odoo SOR domains (ledger, posted docs)
- Gemini MAY be used for SSOT tasks (enrichment tags, analytics views, draft content)
- Any Gemini → Odoo write path MUST be human-reviewed OR restricted to non-SOR fields (e.g., notes, tags)

---

## Server-Side Only Policy (Non-Negotiable)

### Execution Environments

| **Environment** | **Allowed** | **Justification** |
|----------------|-------------|-------------------|
| Supabase Edge Functions | ✅ | Service-role keys, audit trail, no client exposure |
| Background Workers (Node.js) | ✅ | Server-side, vault access, run_events tracking |
| CI/CD Pipelines | ✅ | Controlled env, no user input, logged |
| **Client-Side (Browser)** | ❌ | **API key exposure risk** |
| **Mobile Apps** | ❌ | **API key exposure risk** |

**Enforcement:**
- CI linter MUST flag any `GEMINI_API_KEY` usage in client-side code (React, Vue, etc.)
- API key MUST NOT appear in browser DevTools, bundle source maps, or client-side env vars

---

## Observability

### ops.* Audit Trail

All Gemini API calls MUST emit structured events to Supabase `ops.*` tables:

**Required Fields:**
```sql
-- ops.runs (correlation with agent/task)
INSERT INTO ops.runs (correlation_id, agent_id, task_name, status, metadata)
VALUES (
  'corr-123',
  'gemini-assistant',
  'summarize-meeting-notes',
  'running',
  jsonb_build_object('model', 'gemini-1.5-pro')
);

-- ops.run_events (detailed API call log)
INSERT INTO ops.run_events (run_id, event_type, event_data, created_at)
VALUES (
  <run_id>,
  'gemini_api_call',
  jsonb_build_object(
    'model', 'gemini-1.5-pro',
    'prompt_tokens', 15,
    'completion_tokens', 234,
    'total_tokens', 249,
    'finish_reason', 'STOP',
    'latency_ms', 1234
  ),
  now()
);
```

**Metadata Storage:**
- Store prompts (sanitized, no PII) and responses in `ops.artifacts` table
- Link to `ops.runs` via `correlation_id`
- Retention: 30 days in `ops.*`, 90 days in artifact storage (compressed)

---

## Error Handling & Retry Logic

### Common Error Codes

| **HTTP Status** | **Reason** | **Retry Strategy** |
|----------------|-----------|-------------------|
| 400 Bad Request | Invalid request payload | ❌ No retry (fix request) |
| 401 Unauthorized | Invalid API key | ❌ No retry (rotate key) |
| 403 Forbidden | Quota exceeded | ⏱️ Exponential backoff (up to 3 retries) |
| 429 Too Many Requests | Rate limit exceeded | ⏱️ Exponential backoff (up to 5 retries) |
| 500 Server Error | Gemini API issue | ✅ Retry with backoff (up to 3 retries) |

### Retry Pattern (TypeScript)

```typescript
import { exponentialBackoff } from '@/lib/retry';

async function callGeminiWithRetry(prompt: string, model: string) {
  return exponentialBackoff(async () => {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': process.env.GEMINI_API_KEY!,
        },
        body: JSON.stringify({
          contents: [{ role: 'user', parts: [{ text: prompt }] }],
        }),
      }
    );

    if (!response.ok && [429, 500, 502, 503].includes(response.status)) {
      throw new Error(`Gemini API error: ${response.status}`);
    }

    return response.json();
  }, {
    maxRetries: 3,
    initialDelay: 1000,  // 1s, 2s, 4s
    maxDelay: 10000,
  });
}
```

---

## Example: Supabase Edge Function Integration

**File:** `supabase/functions/gemini-summarize/index.ts`

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const { prompt, model = 'gemini-1.5-flash' } = await req.json();

  // 1. Validate input
  if (!prompt) {
    return new Response(JSON.stringify({ error: 'Missing prompt' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // 2. Call Gemini API (server-side only)
  const geminiResponse = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-goog-api-key': Deno.env.get('GEMINI_API_KEY')!,
      },
      body: JSON.stringify({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
      }),
    }
  );

  const result = await geminiResponse.json();

  // 3. Emit audit event to ops.run_events
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  );

  await supabase.from('ops.run_events').insert({
    run_id: req.headers.get('x-correlation-id'),
    event_type: 'gemini_api_call',
    event_data: {
      model,
      prompt_tokens: result.usageMetadata?.promptTokenCount,
      completion_tokens: result.usageMetadata?.candidatesTokenCount,
      total_tokens: result.usageMetadata?.totalTokenCount,
    },
  });

  // 4. Return response
  return new Response(JSON.stringify(result), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
});
```

**Deployment:**
```bash
supabase functions deploy gemini-summarize --no-verify-jwt
```

**Invocation (from client):**
```typescript
const { data } = await supabase.functions.invoke('gemini-summarize', {
  body: { prompt: 'Summarize this meeting transcript...' },
  headers: { 'x-correlation-id': 'corr-456' },
});
```

---

## Security Checklist

- [ ] `GEMINI_API_KEY` stored in Supabase Vault (not git)
- [ ] API key never exposed to client-side code (browser, mobile)
- [ ] All API calls logged to `ops.run_events` with token usage
- [ ] Retry logic implemented with exponential backoff
- [ ] Error responses sanitized (no key leakage in logs)
- [ ] Rate limit monitoring configured (alert if >80% quota)
- [ ] Key rotation schedule defined (90 days recommended)

---

## Cross-References

- **API Documentation:** [Google AI for Developers — Gemini API](https://ai.google.dev/gemini-api/docs/quickstart)
- **SSOT Policy:** `spec/odoo-ee-parity-seed/constitution.md` (Article: Supabase SSOT)
- **Secret Handling:** `sandbox/dev/CLAUDE.md` (macOS Keychain + Supabase Vault)
- **Audit Trail:** `docs/architecture/AUTOMATION_AUDIT_TRAIL.md` (to be created)
