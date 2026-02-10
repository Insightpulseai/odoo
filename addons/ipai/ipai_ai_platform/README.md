# IPAI AI Platform Module

**Phase 5A: SaaS Platform Kit - AI × Odoo Integration**

Provides HTTP client for calling AI services from Odoo backend workflows.

## Features

- ✅ Supabase Edge Function integration (primary)
- ✅ OpenAI API fallback (when Edge Function unavailable)
- ✅ Multi-tenant organization scoping
- ✅ Audit trail logging (when cms.artifact exists)
- ✅ Configuration via system parameters
- ✅ Health check endpoint

## Installation

```bash
# 1. Install module
./scripts/odoo_install.sh ipai_ai_platform

# 2. Configure system parameters
# Navigate to: Settings → Technical → System Parameters
# Update these keys:
# - ipai.supabase.url = https://spdtwktxdalcfigzeqrz.supabase.co
# - ipai.supabase.service_role_key = <from ~/.zshrc SUPABASE_SERVICE_ROLE_KEY>
# - ipai.org.id = <UUID from organizations table>
# - ipai.openai.api_key = <OpenAI API key for fallback>
```

## Usage

### Basic Question

```python
# Python shell
result = env['ai.client'].ask_question("What is RAG?")
print(result['answer'])
print(result['sources'])
```

### With Context Filters

```python
result = env['ai.client'].ask_question(
    "How to setup billing?",
    context_filters={'category': 'billing'},
    max_chunks=10
)
```

### Health Check

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

## Architecture

### Fallback Strategy

```
Request → Try Edge Function (docs-ai-ask)
          ↓ (if unavailable)
          Fallback to OpenAI API
          ↓
          Return answer + sources
          ↓
          Log to cms.artifact (if exists)
```

### Configuration Priority

1. **Primary**: Supabase Edge Function (if `ipai.supabase.service_role_key` set)
2. **Fallback**: OpenAI API (if `ipai.openai.api_key` set)
3. **Error**: UserError if neither configured

## Verification

```bash
# 1. Module installed
./scripts/odoo_shell.sh "print('ipai_ai_platform' in env.registry._init_modules)"

# 2. Config parameters exist
./scripts/odoo_shell.sh "print(env['ir.config_parameter'].get_param('ipai.supabase.url'))"

# 3. Test AI client
./scripts/odoo_shell.sh "result = env['ai.client'].ask_question('Test query'); print(result)"

# 4. Health check
./scripts/odoo_shell.sh "health = env['ai.client'].health_check(); print(health)"
```

## Dependencies

- **Required**: `base` (Odoo core)
- **Optional**: `ipai_cms` (for audit trail logging)

## Security

- Service role key stored in system parameters (encrypted at rest)
- All AI operations logged with user context
- RLS policies applied at Supabase level (if Edge Function used)
- OpenAI API key never exposed to frontend

## Troubleshooting

### "Supabase URL not configured"
→ Set `ipai.supabase.url` in system parameters

### "AI service unavailable"
→ Check both `ipai.supabase.service_role_key` and `ipai.openai.api_key` are set

### "Edge Function unavailable, falling back"
→ Expected when `docs-ai-ask` Edge Function not deployed (fallback working correctly)

### Audit trail not working
→ Install `ipai_cms` module with `cms.artifact` model

## Next Steps

### Phase 5B: SDK Creation
- TypeScript SDK (`packages/ipai-ai-sdk/`)
- Python SDK (`packages/ipai-ai-sdk-python/`)
- Platform documentation (`docs/platform/ai.md`)

### Future Enhancements
- Usage tracking for billing limits
- Rate limiting per organization
- Streaming responses
- Batch operations
