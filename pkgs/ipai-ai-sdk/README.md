# @ipai/ai-sdk

**InsightPulseAI Platform SDK** - TypeScript/JavaScript client for AI services

Phase 5B: SaaS Platform Kit - SDK Creation

## Installation

```bash
# pnpm (recommended)
pnpm add @ipai/ai-sdk

# npm
npm install @ipai/ai-sdk

# yarn
yarn add @ipai/ai-sdk

# Internal development (from monorepo)
pnpm add file:./packages/ipai-ai-sdk
```

## Quick Start

```typescript
import { AIClient } from '@ipai/ai-sdk';

// Initialize client
const client = new AIClient({
  supabaseUrl: 'https://spdtwktxdalcfigzeqrz.supabase.co',
  apiKey: 'your-anon-key-or-service-role-key'
});

// Ask a question
const result = await client.askQuestion({
  question: 'What is RAG?'
});

console.log(result.answer);
console.log(result.sources);
console.log(result.confidence);
```

## Configuration

### Frontend (Browser)

Use **anon key** for frontend applications:

```typescript
const client = new AIClient({
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL!,
  apiKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  defaultOrgId: 'user-org-uuid', // Optional
  timeout: 30000, // Optional (default: 30s)
  debug: true // Optional (default: false)
});
```

### Backend (Node.js)

Use **service role key** for backend services:

```typescript
const client = new AIClient({
  supabaseUrl: process.env.SUPABASE_URL!,
  apiKey: process.env.SUPABASE_SERVICE_ROLE_KEY!,
  defaultOrgId: process.env.DEFAULT_ORG_ID
});
```

## API Reference

### `AIClient`

#### Constructor

```typescript
new AIClient(config: AIClientConfig)
```

**Config Options:**
- `supabaseUrl` (string, required): Supabase project URL
- `apiKey` (string, required): Anon key (frontend) or service role key (backend)
- `defaultOrgId` (string, optional): Default organization UUID
- `timeout` (number, optional): Request timeout in ms (default: 30000)
- `debug` (boolean, optional): Enable debug logging (default: false)

#### Methods

##### `askQuestion(params: AskQuestionParams): Promise<AskQuestionResponse>`

Ask a question to the AI service.

**Parameters:**
```typescript
{
  question: string;           // Question text (required)
  org_id?: string;            // Organization UUID (optional, uses default)
  filters?: Record<string, any>; // Context filters (optional)
  max_chunks?: number;        // Max context chunks (default: 5)
}
```

**Returns:**
```typescript
{
  answer: string;             // Generated answer
  sources: ContextSource[];   // Context sources used
  confidence: number;         // Confidence score (0.0-1.0)
  question_id: string;        // Unique question ID
  tokens_used?: number;       // Tokens used (for billing)
}
```

**Example:**
```typescript
const result = await client.askQuestion({
  question: 'How to setup billing?',
  filters: { category: 'billing' },
  max_chunks: 10
});
```

##### `healthCheck(): Promise<HealthCheckResponse>`

Check AI service health and configuration.

**Returns:**
```typescript
{
  configured: boolean;              // Config valid
  edge_function: boolean;           // Edge Function reachable
  openai_fallback: boolean;         // OpenAI fallback configured
  org_id?: string;                  // Organization ID
  test_result?: string;             // Test result message
  edge_function_status?: number | string; // HTTP status or error
  error?: string;                   // Error details (if unhealthy)
}
```

**Example:**
```typescript
const health = await client.healthCheck();
if (!health.edge_function) {
  console.warn('AI service unavailable:', health.test_result);
}
```

### Error Handling

```typescript
import { AIError, AIErrorCode } from '@ipai/ai-sdk';

try {
  const result = await client.askQuestion({ question: 'test' });
} catch (error) {
  if (error instanceof AIError) {
    console.error(`AI Error [${error.code}]:`, error.message);

    // Check if retryable
    if (error.isRetryable) {
      console.log('Error is retryable, implementing backoff...');
    }

    // Handle specific error types
    switch (error.code) {
      case AIErrorCode.AUTH_ERROR:
        console.error('Invalid API key');
        break;

      case AIErrorCode.RATE_LIMIT_ERROR:
        console.error('Rate limit exceeded');
        break;

      case AIErrorCode.SERVICE_UNAVAILABLE:
        console.error('Service temporarily unavailable');
        break;

      default:
        console.error('Unknown error:', error.message);
    }
  }
}
```

**Error Codes:**
- `CONFIG_ERROR` - Configuration invalid (missing URL/key)
- `NETWORK_ERROR` - Network timeout or connection failure
- `AUTH_ERROR` - Authentication failed (invalid API key)
- `RATE_LIMIT_ERROR` - Rate limit exceeded
- `SERVICE_UNAVAILABLE` - Edge Function unavailable
- `INVALID_REQUEST` - Invalid request parameters
- `UNKNOWN_ERROR` - Unknown error

## Usage Examples

### Browser Chat Widget

```typescript
import { AIClient } from '@ipai/ai-sdk';

const client = new AIClient({
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL!,
  apiKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
});

async function handleChatSubmit(question: string) {
  try {
    const result = await client.askQuestion({ question });

    // Display answer
    addMessageToUI({
      role: 'assistant',
      content: result.answer,
      sources: result.sources
    });

  } catch (error) {
    if (error instanceof AIError) {
      addErrorToUI(error.message);
    }
  }
}
```

### Server-Side Batch Processing

```typescript
import { AIClient } from '@ipai/ai-sdk';

const client = new AIClient({
  supabaseUrl: process.env.SUPABASE_URL!,
  apiKey: process.env.SUPABASE_SERVICE_ROLE_KEY!
});

async function batchProcess(questions: string[]) {
  const results = await Promise.all(
    questions.map(question =>
      client.askQuestion({ question })
        .catch(error => ({ error: error.message }))
    )
  );

  return results;
}
```

### React Hook

```typescript
import { useState } from 'react';
import { AIClient, AIError } from '@ipai/ai-sdk';

const client = new AIClient({
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL!,
  apiKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
});

export function useAI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const askQuestion = async (question: string) => {
    setLoading(true);
    setError(null);

    try {
      const result = await client.askQuestion({ question });
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

## Architecture

### Edge Function Integration

```
Request → SDK Client
          ↓
          Supabase Edge Function (docs-ai-ask)
          ↓
          RAG Pipeline (Embeddings + Vector Search)
          ↓
          OpenAI GPT-4 (Answer Generation)
          ↓
          Response → SDK Client
```

### Fallback Strategy (Odoo Backend)

When Edge Function unavailable, Odoo backend falls back to direct OpenAI API:

```
Odoo → ai.client → Edge Function (primary)
                ↓ (if unavailable)
                OpenAI API (fallback)
```

SDK does NOT implement fallback (keeps client lightweight).

## Development

```bash
# Install dependencies
pnpm install

# Build SDK
pnpm build

# Type checking
pnpm typecheck

# Run tests
pnpm test

# Watch mode
pnpm dev
```

## TypeScript Support

Full TypeScript support with type definitions:

```typescript
import type {
  AIClientConfig,
  AskQuestionParams,
  AskQuestionResponse,
  ContextSource,
  HealthCheckResponse
} from '@ipai/ai-sdk';
```

## License

MIT

## Support

- Documentation: https://insightpulseai.com/docs/platform/ai
- GitHub: https://github.com/Insightpulseai/odoo
- Issues: https://github.com/Insightpulseai/odoo/issues
