# AI Provider Router

Multi-provider LLM abstraction layer with automatic failover, retry logic, and structured output support.

## Features

- **Multi-Provider Support**: OpenAI, Google Gemini, Anthropic Claude, Ollama
- **Automatic Failover**: Seamless fallback to secondary/tertiary providers
- **Retry Logic**: Configurable retry attempts with exponential backoff
- **JSON Mode**: Structured JSON output for all providers
- **Secure Logging**: Automatic redaction of API keys in logs
- **Type Safety**: Full type hints and dataclass responses
- **100% Test Coverage**: Comprehensive unit tests

## Installation

```bash
cd infra/ai/provider_router
pip install -r requirements.txt
```

## Quick Start

```python
from provider_router import call_ai

# Simple usage
response = call_ai("What is 2+2?")
print(response.content)  # "4"
print(response.provider)  # "openai"
print(response.tokens_used)  # 12
print(response.latency_ms)  # 342

# With JSON mode
response = call_ai(
    "List 3 programming languages as JSON with a 'languages' array",
    json_mode=True
)
print(response.content)
# {"languages": ["Python", "JavaScript", "Go"]}

# With parameter overrides
response = call_ai(
    "Write a creative story",
    model="gpt-4o",
    temperature=0.9,
    max_tokens=500
)
```

## Configuration

### Environment Variables

```bash
# Primary provider selection
IPAI_AI_PROVIDER=openai  # Options: openai, gemini, anthropic, ollama

# Failover configuration
AI_PROVIDER_PRIMARY=openai
AI_PROVIDER_SECONDARY=gemini
AI_PROVIDER_TERTIARY=anthropic
AI_PROVIDER_RETRY_ATTEMPTS=3
AI_PROVIDER_RETRY_DELAY=2  # seconds

# OpenAI configuration
IPAI_LLM_API_KEY=sk-...
IPAI_LLM_BASE_URL=https://api.openai.com/v1  # Optional: for Azure OpenAI
IPAI_LLM_MODEL=gpt-4o-mini
IPAI_LLM_TEMPERATURE=0.2
IPAI_LLM_MAX_TOKENS=4096
IPAI_LLM_TIMEOUT=30

# Gemini configuration
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-flash
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# Anthropic configuration
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_BASE_URL=https://api.anthropic.com/v1

# Ollama configuration (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

### Provider Priority

The router tries providers in this order:

1. **Primary** (set via `AI_PROVIDER_PRIMARY` or `IPAI_AI_PROVIDER`)
2. **Secondary** (set via `AI_PROVIDER_SECONDARY`)
3. **Tertiary** (set via `AI_PROVIDER_TERTIARY`)

If all providers fail, an `AIError` exception is raised.

## Advanced Usage

### Using the Router Class

```python
from provider_router import ProviderRouter

router = ProviderRouter()

# Call with metadata tracking
response = router.call_ai(
    prompt="Analyze this text for sentiment",
    model="gpt-4o",
    meta={
        'user_id': '12345',
        'request_id': 'abc-def-ghi',
        'feature': 'sentiment_analysis'
    }
)

# Access metadata in response
print(response.metadata)
# {
#   'user_id': '12345',
#   'request_id': 'abc-def-ghi',
#   'feature': 'sentiment_analysis',
#   'finish_reason': 'stop',
#   'prompt_tokens': 15,
#   'completion_tokens': 42
# }
```

### JSON Mode for Structured Output

```python
from provider_router import call_ai
import json

# Request structured JSON response
response = call_ai(
    """Extract entities from this text:
    "John Smith works at Acme Corp in New York and can be reached at john@acme.com"

    Return JSON with keys: name, company, location, email
    """,
    json_mode=True
)

# Parse response
data = json.loads(response.content)
print(data)
# {
#   "name": "John Smith",
#   "company": "Acme Corp",
#   "location": "New York",
#   "email": "john@acme.com"
# }
```

### Error Handling

```python
from provider_router import call_ai, AIError

try:
    response = call_ai("Test prompt")
except AIError as e:
    print(f"Provider: {e.provider}")
    print(f"Error: {e}")
    print(f"Original: {e.original_error}")
```

## Testing

```bash
# Run all tests
pytest test_router.py -v

# Run with coverage
pytest test_router.py --cov=router --cov-report=html

# Run specific test class
pytest test_router.py::TestProviderFailover -v
```

## Integration with Odoo

### As Odoo Module Service

```python
# In your Odoo module
from odoo import api, models
import sys
sys.path.append('/path/to/infra/ai/provider_router')
from provider_router import call_ai

class AIService(models.AbstractModel):
    _name = 'ipai.ai.service'
    _description = 'AI Service with Provider Router'

    @api.model
    def ask_ai(self, prompt, **kwargs):
        """Call AI with Odoo context"""
        try:
            response = call_ai(
                prompt=prompt,
                meta={
                    'user_id': self.env.user.id,
                    'company_id': self.env.company.id,
                    'model': self._name,
                }
                **kwargs
            )

            # Log to Odoo
            self.env['ipai.ai.audit'].create({
                'prompt': prompt,
                'response': response.content,
                'provider': response.provider,
                'model': response.model,
                'tokens_used': response.tokens_used,
                'latency_ms': response.latency_ms,
                'user_id': self.env.user.id,
            })

            return response.content

        except Exception as e:
            _logger.error(f"AI request failed: {e}")
            raise
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Application Layer                    │
│                   (call_ai convenience)                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    ProviderRouter                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Failover Logic: Primary → Secondary → Tertiary  │   │
│  │ Retry Logic: 3 attempts with 2s delay          │   │
│  │ Latency Tracking: Millisecond precision         │   │
│  └─────────────────────────────────────────────────┘   │
└──────────┬────────────┬────────────┬───────────┬────────┘
           │            │            │           │
           ▼            ▼            ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  OpenAI  │ │  Gemini  │ │Anthropic │ │  Ollama  │
    │   API    │ │   API    │ │   API    │ │  Local   │
    └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

## Security

### API Key Protection

- Never logs full API keys (automatic redaction)
- Environment variable-only configuration (no hardcoded secrets)
- Secure formatter prevents accidental exposure in logs

### Best Practices

1. **Use separate API keys per environment** (dev, staging, prod)
2. **Rotate keys quarterly** or after suspected exposure
3. **Monitor usage** via provider dashboards
4. **Set spend limits** in provider accounts
5. **Use least-privilege** service accounts

## Performance

### Latency Optimization

- Connection pooling (automatic in HTTP libraries)
- Request timeout enforcement (default: 30s)
- Retry with exponential backoff (prevents thundering herd)

### Cost Optimization

- Default to cheaper models (`gpt-4o-mini`, `gemini-1.5-flash`)
- Set appropriate `max_tokens` limits
- Use `temperature=0.2` for deterministic tasks (lower cost)
- Monitor token usage in `AIResponse.tokens_used`

## Troubleshooting

### "IPAI_LLM_API_KEY not set"

**Solution:** Set the environment variable:
```bash
export IPAI_LLM_API_KEY=sk-your-key-here
```

### "All providers failed"

**Possible causes:**
1. All API keys are invalid/expired
2. Network connectivity issues
3. Provider API outages
4. Rate limiting

**Solution:** Check logs for specific provider errors, verify API keys, check provider status pages.

### "Max retries exceeded"

**Possible causes:**
1. Persistent API errors
2. Network timeout
3. Invalid request format

**Solution:** Increase timeout, check request parameters, verify API key permissions.

### Import errors (openai, google-generativeai, anthropic)

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

## Changelog

### v1.0.0 (2026-01-09)
- Initial release
- Support for OpenAI, Gemini, Anthropic, Ollama
- Automatic failover and retry logic
- JSON mode support
- Comprehensive test coverage
- Secure logging with API key redaction

## License

AGPL-3.0 (OCA-compatible)

## Contributing

See repository CONTRIBUTING.md for guidelines.

## Support

- **Issues:** https://github.com/jgtolentino/odoo-ce/issues
- **Documentation:** docs/auth/EMAIL_AUTH_SETUP.md
- **Tests:** `pytest test_router.py -v`
