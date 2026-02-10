# InsightPulseAI AI Platform

**Phase 5: SaaS Platform Kit - AI × Odoo Integration + SDKs**

Comprehensive guide to InsightPulseAI's AI capabilities for Odoo backend, frontend, and external integrations.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Odoo Backend Integration](#odoo-backend-integration)
- [Frontend SDK (TypeScript)](#frontend-sdk-typescript)
- [Backend SDK (Python)](#backend-sdk-python)
- [Authentication](#authentication)
- [Limits & Billing](#limits--billing)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│ Frontend (Browser)                                              │
│  ├─ Next.js App                                                 │
│  ├─ Chat Widget                                                 │
│  └─ @ipai/ai-sdk (TypeScript)                                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ HTTPS (anon key)
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Supabase Edge Functions                                        │
│  ├─ docs-ai-ask (NOT DEPLOYED - fallback to OpenAI)            │
│  ├─ Auth (RLS policies)                                        │
│  └─ Org-scoped context                                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Vector Search (if deployed)
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ AI Backend                                                      │
│  ├─ OpenAI GPT-4 (primary - via Odoo fallback)                 │
│  ├─ pgvector (embeddings - future)                             │
│  └─ Usage tracking (cms_artifacts)                             │
└─────────────────────────────────────────────────────────────────┘
                     ↑
                     │ Service role key
                     │
┌─────────────────────────────────────────────────────────────────┐
│ Odoo Backend                                                    │
│  ├─ ipai_ai_platform module                                    │
│  ├─ ai.client model (HTTP client)                              │
│  └─ OpenAI API fallback (when Edge Function unavailable)       │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

**User Ask Question:**
1. Frontend calls SDK with question
2. SDK sends request to Edge Function (or Odoo backend)
3. Edge Function retrieves context (RAG) or OpenAI direct (fallback)
4. OpenAI generates answer
5. Response with answer + sources returned
6. Usage logged to cms_artifacts (audit trail)

---

## Quick Start

### 1. Odoo Backend (5 minutes)

```bash
# Install module
./scripts/odoo_install.sh ipai_ai_platform

# Configure system parameters
# Navigate to: Settings → Technical → System Parameters
# Set these keys:
# - ipai.supabase.url = https://spdtwktxdalcfigzeqrz.supabase.co
# - ipai.supabase.service_role_key = <from ~/.zshrc>
# - ipai.org.id = <UUID from organizations table>
# - ipai.openai.api_key = <OpenAI API key for fallback>

# Test in Python shell
./scripts/odoo_shell.sh "result = env['ai.client'].ask_question('What is RAG?'); print(result)"
```

### 2. Frontend SDK (3 minutes)

```bash
# Install TypeScript SDK
pnpm add @ipai/ai-sdk

# Or from monorepo
pnpm add file:./packages/ipai-ai-sdk
```

```typescript
import { AIClient } from '@ipai/ai-sdk';

const client = new AIClient({
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL!,
  apiKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
});

const result = await client.askQuestion({
  question: 'What is RAG?'
});

console.log(result.answer);
```

### 3. Python SDK (3 minutes)

```bash
# Install Python SDK
pip install ipai-ai-sdk

# Or from monorepo
pip install -e ./packages/ipai-ai-sdk-python
```

```python
from ipai_ai_sdk import AIClient

client = AIClient(
    supabase_url='https://spdtwktxdalcfigzeqrz.supabase.co',
    api_key='your-service-role-key'
)

result = client.ask_question('What is RAG?')
print(result.answer)
```

---

## Odoo Backend Integration

### Installation

```bash
# 1. Install module
./scripts/odoo_install.sh ipai_ai_platform

# 2. Verify installation
./scripts/odoo_shell.sh "print('ipai_ai_platform' in env.registry._init_modules)"
```

### Configuration

Navigate to **Settings → Technical → System Parameters** and set:

| Key | Value | Purpose |
|-----|-------|---------|
| `ipai.supabase.url` | `https://spdtwktxdalcfigzeqrz.supabase.co` | Supabase project URL |
| `ipai.supabase.service_role_key` | `sbp_xxx...` | Service role key (backend auth) |
| `ipai.org.id` | `uuid-here` | Default organization UUID |
| `ipai.openai.api_key` | `sk-xxx...` | OpenAI API key (fallback) |

### Usage

#### Basic Question

```python
# Odoo Python shell
result = env['ai.client'].ask_question("What is RAG?")

print(result['answer'])
print(result['sources'])
print(result['confidence'])
```

#### With Context Filters

```python
result = env['ai.client'].ask_question(
    "How to setup billing?",
    context_filters={'category': 'billing'},
    max_chunks=10
)
```

#### Health Check

```python
health = env['ai.client'].health_check()
print(health)
# {
#     'configured': True,
#     'edge_function': False,
#     'openai_fallback': True,
#     'org_id': 'uuid-here',
#     'test_result': 'Using OpenAI fallback'
# }
```

### Integration Examples

#### CMS Section Generation

```python
# addons/ipai_cms/models/cms_section.py

class CmsSection(models.Model):
    _name = 'cms.section'

    def action_generate_with_ai(self):
        """Button action: Generate section content with AI"""
        for section in self:
            # Build context prompt
            prompt = f"Generate hero copy for: {section.title}"

            # Call AI
            result = self.env['ai.client'].ask_question(
                prompt,
                context_filters={'type': 'marketing'}
            )

            # Update section
            section.write({
                'content': result['answer'],
                'ai_generated': True
            })

        return True
```

#### Cron-Based Insights

```python
def _generate_daily_insights(self):
    """Cron job: Generate AI insights daily"""
    ai_client = self.env['ai.client']

    # Query recent data
    recent_data = self._fetch_analytics_data()

    # Generate insights
    prompt = f"Analyze this data and provide 3 key insights: {recent_data}"
    result = ai_client.ask_question(prompt)

    # Store insights
    self.env['analytics.insight'].create({
        'date': fields.Date.today(),
        'content': result['answer'],
        'confidence': result['confidence']
    })
```

---

## Frontend SDK (TypeScript)

### Installation

```bash
pnpm add @ipai/ai-sdk
```

### Configuration

```typescript
// lib/ai-client.ts
import { AIClient } from '@ipai/ai-sdk';

export const aiClient = new AIClient({
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL!,
  apiKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  defaultOrgId: process.env.NEXT_PUBLIC_ORG_ID,
  timeout: 30000,
  debug: process.env.NODE_ENV === 'development'
});
```

### Usage

#### React Hook

```typescript
// hooks/use-ai.ts
import { useState } from 'react';
import { aiClient } from '@/lib/ai-client';
import { AIError } from '@ipai/ai-sdk';

export function useAI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const askQuestion = async (question: string) => {
    setLoading(true);
    setError(null);

    try {
      const result = await aiClient.askQuestion({ question });
      return result;
    } catch (err) {
      if (err instanceof AIError) {
        setError(err.message);
      } else {
        setError('Unknown error occurred');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { askQuestion, loading, error };
}
```

#### Chat Component

```typescript
// components/chat-widget.tsx
'use client';

import { useState } from 'react';
import { useAI } from '@/hooks/use-ai';

export function ChatWidget() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const { askQuestion, loading, error } = useAI();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: question }]);

    try {
      // Get AI response
      const result = await askQuestion(question);

      // Add AI message
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: result.answer,
          sources: result.sources
        }
      ]);

      setQuestion('');
    } catch (err) {
      // Error already handled by useAI hook
    }
  };

  return (
    <div className="chat-widget">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role}>
            {msg.content}
            {msg.sources && (
              <ul>
                {msg.sources.map((s: any) => (
                  <li key={s.chunk_id}>{s.document_title}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <input
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
    </div>
  );
}
```

---

## Backend SDK (Python)

### Installation

```bash
pip install ipai-ai-sdk
```

### Configuration

```python
# config.py
import os
from ipai_ai_sdk import AIClient

ai_client = AIClient(
    supabase_url=os.environ['SUPABASE_URL'],
    api_key=os.environ['SUPABASE_SERVICE_ROLE_KEY'],
    default_org_id=os.environ.get('DEFAULT_ORG_ID'),
    timeout=30,
    debug=os.environ.get('DEBUG') == 'true'
)
```

### Usage

#### Flask API

```python
from flask import Flask, request, jsonify
from ipai_ai_sdk import AIError

app = Flask(__name__)

@app.route('/api/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        result = ai_client.ask_question(data['question'])

        return jsonify({
            'answer': result.answer,
            'sources': [
                {'title': s.document_title, 'similarity': s.similarity}
                for s in result.sources
            ],
            'confidence': result.confidence
        })

    except AIError as e:
        return jsonify({'error': str(e)}), 500
```

#### FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/api/ask")
async def ask(req: QuestionRequest):
    try:
        result = ai_client.ask_question(req.question)
        return {
            'answer': result.answer,
            'sources': result.sources,
            'confidence': result.confidence
        }
    except AIError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Authentication

### Frontend (Anon Key)

- Use **anon key** for browser applications
- RLS policies enforce org-scoped access
- User context from Supabase Auth session

```typescript
const client = new AIClient({
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL!,
  apiKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY! // ← anon key
});
```

### Backend (Service Role Key)

- Use **service role key** for server-side operations
- Bypasses RLS (use carefully)
- Required for Odoo backend integration

```python
client = AIClient(
    supabase_url=os.environ['SUPABASE_URL'],
    api_key=os.environ['SUPABASE_SERVICE_ROLE_KEY'] # ← service role
)
```

### Org Context

All AI operations are scoped to organizations:

- **Frontend**: Org context from user session
- **Backend**: Explicit `org_id` parameter or default from config
- **Odoo**: Configured via `ipai.org.id` system parameter

---

## Limits & Billing

### Free Tier

- **100 AI questions/month** per organization
- **5 context chunks** per question
- **30 second timeout**

### Pro Tier ($49/month)

- **5,000 AI questions/month**
- **10 context chunks** per question
- **60 second timeout**
- Priority support

### Enterprise (Custom)

- **Unlimited AI questions**
- **Custom context chunks**
- **Custom timeout**
- Dedicated support
- SLA guarantees

### Usage Tracking

All AI operations logged to `cms_artifacts` table (if exists):

```sql
SELECT
  COUNT(*) AS total_questions,
  SUM((metadata->>'tokens_used')::int) AS total_tokens
FROM cms_artifacts
WHERE artifact_type = 'ai_operation'
  AND org_id = 'your-org-uuid'
  AND created_at >= NOW() - INTERVAL '1 month';
```

---

## API Reference

### Edge Function: `/functions/v1/docs-ai-ask`

**Status**: NOT DEPLOYED (fallback to OpenAI API via Odoo)

**Request:**
```json
POST /functions/v1/docs-ai-ask
Authorization: Bearer <service_role_key>
Content-Type: application/json

{
  "question": "What is RAG?",
  "org_id": "uuid-here",
  "filters": { "category": "technical" },
  "max_chunks": 5
}
```

**Response:**
```json
{
  "answer": "RAG stands for Retrieval-Augmented Generation...",
  "sources": [
    {
      "chunk_id": "uuid",
      "document_title": "RAG Introduction",
      "similarity": 0.92,
      "content": "excerpt...",
      "metadata": { "category": "technical" }
    }
  ],
  "confidence": 0.89,
  "question_id": "uuid",
  "tokens_used": 450
}
```

**Error Codes:**
- `400` - Invalid request parameters
- `401` - Authentication failed
- `404` - Edge Function not found (fallback to OpenAI)
- `429` - Rate limit exceeded
- `500` - Server error

---

## Examples

### Example 1: Browser Chat Widget

```typescript
import { AIClient } from '@ipai/ai-sdk';

const client = new AIClient({
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL!,
  apiKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
});

async function handleChat(question: string) {
  const result = await client.askQuestion({ question });
  console.log(result.answer);
}
```

### Example 2: Odoo CMS Generation

```python
# Generate hero copy
result = env['ai.client'].ask_question(
    "Generate hero copy for Odoo expense automation module"
)

env['cms.section'].create({
    'title': 'Hero Section',
    'content': result['answer'],
    'ai_generated': True
})
```

### Example 3: Flask API

```python
@app.route('/api/ask', methods=['POST'])
def ask():
    result = ai_client.ask_question(request.json['question'])
    return jsonify({'answer': result.answer})
```

### Example 4: Batch Processing

```python
questions = ['Q1', 'Q2', 'Q3']

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(
        lambda q: ai_client.ask_question(q),
        questions
    ))
```

---

## Troubleshooting

### "Edge Function not found"

**Status**: EXPECTED (Edge Function not deployed)

**Solution**: Odoo backend automatically falls back to OpenAI API. No action required.

### "Authentication failed"

**Check**:
- Frontend: `NEXT_PUBLIC_SUPABASE_ANON_KEY` correct?
- Backend: `SUPABASE_SERVICE_ROLE_KEY` correct?
- Odoo: System parameter `ipai.supabase.service_role_key` set?

### "AI service unavailable"

**Check**:
- Odoo: Is `ipai.openai.api_key` system parameter set?
- Network: Can reach `api.openai.com`?
- Quota: OpenAI API quota exceeded?

### "Request timeout"

**Solution**: Increase timeout:
- TypeScript: `new AIClient({ timeout: 60000 })`
- Python: `AIClient(timeout=60)`
- Odoo: Uses 30s default (not configurable via UI)

### No audit trail logging

**Check**:
- Does `cms.artifact` model exist?
- Install `ipai_cms` module if needed

### Rate limit errors

**Solution**:
- Upgrade to Pro/Enterprise tier
- Implement caching on frontend
- Batch similar questions

---

## Support

- **Documentation**: https://insightpulseai.com/docs/platform/ai
- **GitHub**: https://github.com/Insightpulseai/odoo
- **Issues**: https://github.com/Insightpulseai/odoo/issues
- **Email**: business@insightpulseai.com

---

**Last Updated**: 2026-02-10
**Phase 5 Status**: COMPLETE (Odoo + SDKs + Docs)
**Next**: Deploy Edge Function for RAG capabilities
