# ipai-ai-sdk (Python)

**InsightPulseAI Platform SDK** - Python client for AI services

Phase 5B: SaaS Platform Kit - SDK Creation

## Installation

```bash
# pip
pip install ipai-ai-sdk

# poetry
poetry add ipai-ai-sdk

# Internal development (from monorepo)
pip install -e ./packages/ipai-ai-sdk-python
```

## Quick Start

```python
from ipai_ai_sdk import AIClient

# Initialize client
client = AIClient(
    supabase_url='https://spdtwktxdalcfigzeqrz.supabase.co',
    api_key='your-anon-key-or-service-role-key'
)

# Ask a question
result = client.ask_question('What is RAG?')

print(result.answer)
print(result.sources)
print(result.confidence)
```

## Configuration

### Backend (Python Service)

Use **service role key** for backend services:

```python
import os
from ipai_ai_sdk import AIClient

client = AIClient(
    supabase_url=os.environ['SUPABASE_URL'],
    api_key=os.environ['SUPABASE_SERVICE_ROLE_KEY'],
    default_org_id=os.environ.get('DEFAULT_ORG_ID'),
    timeout=30,  # Optional (default: 30s)
    debug=True   # Optional (default: False)
)
```

### Odoo Integration

From Odoo backend (already implemented in `ipai_ai_platform`):

```python
# System parameters configured via Odoo UI
result = env['ai.client'].ask_question("What is RAG?")
```

## API Reference

### `AIClient`

#### Constructor

```python
AIClient(
    supabase_url: str,          # Required
    api_key: str,               # Required
    default_org_id: str = None, # Optional
    timeout: int = 30,          # Optional (seconds)
    debug: bool = False         # Optional
)
```

#### Methods

##### `ask_question(question, org_id=None, filters=None, max_chunks=5)`

Ask a question to the AI service.

**Parameters:**
- `question` (str, required): Question text
- `org_id` (str, optional): Organization UUID (uses default if not provided)
- `filters` (dict, optional): Context filters (e.g., `{'category': 'billing'}`)
- `max_chunks` (int, optional): Max context chunks (default: 5)

**Returns:**
`AskQuestionResponse` object with:
- `answer` (str): Generated answer
- `sources` (List[ContextSource]): Context sources used
- `confidence` (float): Confidence score (0.0-1.0)
- `question_id` (str): Unique question ID
- `tokens_used` (int, optional): Tokens used (for billing)

**Example:**
```python
result = client.ask_question(
    'How to setup billing?',
    filters={'category': 'billing'},
    max_chunks=10
)
```

##### `health_check()`

Check AI service health and configuration.

**Returns:**
`HealthCheckResponse` object with:
- `configured` (bool): Config valid
- `edge_function` (bool): Edge Function reachable
- `openai_fallback` (bool): OpenAI fallback configured
- `org_id` (str, optional): Organization ID
- `test_result` (str, optional): Test result message
- `edge_function_status` (int/str, optional): HTTP status or error
- `error` (str, optional): Error details (if unhealthy)

**Example:**
```python
health = client.health_check()
if not health.edge_function:
    print(f"AI service unavailable: {health.test_result}")
```

### Error Handling

```python
from ipai_ai_sdk import AIClient, AIError, AIErrorCode

try:
    result = client.ask_question('test')
except AIError as error:
    print(f"AI Error [{error.code}]: {error.message}")

    # Check if retryable
    if error.is_retryable:
        print("Error is retryable, implementing backoff...")

    # Handle specific error types
    if error.code == AIErrorCode.AUTH_ERROR:
        print("Invalid API key")
    elif error.code == AIErrorCode.RATE_LIMIT_ERROR:
        print("Rate limit exceeded")
    elif error.code == AIErrorCode.SERVICE_UNAVAILABLE:
        print("Service temporarily unavailable")
```

**Error Codes:**
- `CONFIG_ERROR` - Configuration invalid
- `NETWORK_ERROR` - Network timeout/failure
- `AUTH_ERROR` - Authentication failed
- `RATE_LIMIT_ERROR` - Rate limit exceeded
- `SERVICE_UNAVAILABLE` - Edge Function unavailable
- `INVALID_REQUEST` - Invalid parameters
- `UNKNOWN_ERROR` - Unknown error

## Usage Examples

### Flask API

```python
from flask import Flask, request, jsonify
from ipai_ai_sdk import AIClient, AIError

app = Flask(__name__)
client = AIClient(
    supabase_url=os.environ['SUPABASE_URL'],
    api_key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
)

@app.route('/api/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        result = client.ask_question(data['question'])

        return jsonify({
            'answer': result.answer,
            'sources': [
                {
                    'title': s.document_title,
                    'similarity': s.similarity
                }
                for s in result.sources
            ],
            'confidence': result.confidence
        })

    except AIError as e:
        return jsonify({'error': str(e)}), 500
```

### FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ipai_ai_sdk import AIClient, AIError

app = FastAPI()
client = AIClient(
    supabase_url=os.environ['SUPABASE_URL'],
    api_key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/api/ask")
async def ask(req: QuestionRequest):
    try:
        result = client.ask_question(req.question)
        return {
            'answer': result.answer,
            'sources': result.sources,
            'confidence': result.confidence
        }
    except AIError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor
from ipai_ai_sdk import AIClient

client = AIClient(
    supabase_url=os.environ['SUPABASE_URL'],
    api_key=os.environ['SUPABASE_SERVICE_ROLE_KEY']
)

def process_question(question: str):
    try:
        return client.ask_question(question)
    except Exception as e:
        return {'error': str(e)}

questions = [
    'What is RAG?',
    'How to setup billing?',
    'What are the pricing plans?'
]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_question, questions))
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

Python SDK does NOT implement fallback (keeps client lightweight).

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black ipai_ai_sdk/
isort ipai_ai_sdk/

# Type checking
mypy ipai_ai_sdk/

# Coverage
pytest --cov=ipai_ai_sdk --cov-report=html
```

## Type Annotations

Full type annotation support for type checkers:

```python
from ipai_ai_sdk import (
    AIClient,
    AskQuestionResponse,
    ContextSource,
    HealthCheckResponse,
    AIError,
    AIErrorCode
)
```

## License

MIT

## Support

- Documentation: https://insightpulseai.com/docs/platform/ai
- GitHub: https://github.com/Insightpulseai/odoo
- Issues: https://github.com/Insightpulseai/odoo/issues
