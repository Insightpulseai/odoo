# AI Agents Settings Reference

Complete guide to configuring and managing AI agents in Odoo 19 CE using the IPAI AI platform.

## Overview

The IPAI AI platform provides native AI agent capabilities directly in Odoo through 8 integrated modules. AI agents can analyze data, answer questions, automate workflows, and provide intelligent assistance across all Odoo applications.

**Key Features:**
- **UI Panel Integration**: Quick access via Alt+Shift+F keyboard shortcut
- **Multi-Provider Support**: OpenAI, Claude (Anthropic), and local models
- **REST API Access**: Programmatic integration for external systems
- **Tool System**: Agents can execute Odoo operations and call external APIs
- **RAG Support**: Retrieval-augmented generation for context-aware responses
- **Conversation Management**: Persistent chat history and session management

**Access Locations:**
- UI Panel: Press `Alt+Shift+F` from any Odoo view
- Settings: Settings → Technical → AI Agents
- Developer Menu: Debug mode → View AI Agents

---

## Module Dependencies & Installation Order

The IPAI AI platform consists of 8 modules with specific dependencies. Install in this order:

| # | Module | Purpose | Dependencies |
|---|--------|---------|--------------|
| 1 | `ipai_ai_core` | Backend foundation, models, base classes | Base Odoo |
| 2 | `ipai_ai_fields` | Custom field types for AI data | ipai_ai_core |
| 3 | `ipai_ai_agent_builder` | Core agent framework, templates | ipai_ai_core, ipai_ai_fields |
| 4 | `ipai_ai_tools` | Agent tooling system, tool registry | ipai_ai_agent_builder |
| 5 | `ipai_ai_rag` | Retrieval-augmented generation | ipai_ai_core |
| 6 | `ipai_ai_livechat` | AI chatbot for live_chat module | ipai_ai_agent_builder, live_chat |
| 7 | `ipai_ai_automations` | Automated agent workflows, triggers | ipai_ai_agent_builder |
| 8 | `ipai_ai_agents_ui` | React + Fluent UI panel (Alt+Shift+F) | ipai_ai_agent_builder |

**Installation Commands:**

```bash
# Via Odoo Shell
./odoo-bin shell -d odoo_dev <<'EOF'
modules = [
    'ipai_ai_core',
    'ipai_ai_fields',
    'ipai_ai_agent_builder',
    'ipai_ai_tools',
    'ipai_ai_rag',
    'ipai_ai_livechat',
    'ipai_ai_automations',
    'ipai_ai_agents_ui'
]
for module_name in modules:
    module = env['ir.module.module'].search([('name', '=', module_name)])
    if module and module.state != 'installed':
        module.button_immediate_install()
        print(f"Installed: {module_name}")
EOF

# Via CLI (Docker)
docker exec -it ipai-odoo-dev odoo -d odoo_dev -u ipai_ai_core,ipai_ai_fields,ipai_ai_agent_builder,ipai_ai_tools,ipai_ai_rag,ipai_ai_livechat,ipai_ai_automations,ipai_ai_agents_ui --stop-after-init
```

---

## Configuration Parameters

### Provider Configuration (ir.config_parameter)

| Parameter Key | Purpose | Example Value | Required |
|---------------|---------|---------------|----------|
| `ai.provider.default` | Default AI provider | `openai`\|`claude`\|`local` | Yes |
| `ai.openai.api_key` | OpenAI API key | `sk-proj-...` | If using OpenAI |
| `ai.openai.org_id` | OpenAI organization ID | `org-...` | Optional |
| `ai.claude.api_key` | Claude API key | `sk-ant-api03-...` | If using Claude |
| `ai.model.default` | Default model | `gpt-4o`\|`claude-3-5-sonnet-20241022` | Yes |
| `ai.model.fallback` | Fallback model if primary fails | `gpt-3.5-turbo` | Optional |
| `ai.rate_limit.rpm` | Rate limit (requests/min) | `60` | Yes |
| `ai.rate_limit.tpm` | Rate limit (tokens/min) | `150000` | Yes |
| `ai.rate_limit.enabled` | Enable rate limiting | `True`\|`False` | Yes |
| `ai.token_budget.default` | Default token budget per request | `10000` | Yes |
| `ai.token_budget.max` | Maximum token budget allowed | `128000` | Yes |
| `ai.concurrency.max` | Max concurrent AI requests | `5` | Yes |
| `ai.timeout.default` | Request timeout (seconds) | `60` | Yes |
| `ai.retry.attempts` | Retry attempts on failure | `3` | Yes |
| `ai.retry.backoff` | Backoff multiplier for retries | `2.0` | Yes |
| `ai.logging.enabled` | Enable AI request logging | `True`\|`False` | Yes |
| `ai.logging.level` | Log level | `INFO`\|`DEBUG`\|`WARNING` | Yes |

**Set Configuration:**

```python
# Via Odoo Shell
env['ir.config_parameter'].sudo().set_param('ai.provider.default', 'openai')
env['ir.config_parameter'].sudo().set_param('ai.openai.api_key', 'sk-proj-...')
env['ir.config_parameter'].sudo().set_param('ai.model.default', 'gpt-4o')
env['ir.config_parameter'].sudo().set_param('ai.rate_limit.rpm', '60')
env['ir.config_parameter'].sudo().set_param('ai.rate_limit.tpm', '150000')
env['ir.config_parameter'].sudo().set_param('ai.token_budget.default', '10000')
env['ir.config_parameter'].sudo().set_param('ai.concurrency.max', '5')

# Via SQL (direct database access)
INSERT INTO ir_config_parameter (key, value, create_date, write_date, create_uid, write_uid)
VALUES ('ai.provider.default', 'openai', NOW(), NOW(), 1, 1)
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();
```

**Get Configuration:**

```python
# Via Odoo Shell
provider = env['ir.config_parameter'].sudo().get_param('ai.provider.default')
api_key = env['ir.config_parameter'].sudo().get_param('ai.openai.api_key')
model = env['ir.config_parameter'].sudo().get_param('ai.model.default')
rpm = int(env['ir.config_parameter'].sudo().get_param('ai.rate_limit.rpm', '60'))
```

---

## Agent Configuration Model (ai.agent)

AI agents are defined in the `ai.agent` model with these key fields:

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `name` | Char | Agent display name | "Invoice Analyzer" |
| `technical_name` | Char | Unique technical identifier | "invoice_analyzer" |
| `model_id` | Many2one | Odoo model this agent operates on | `account.move` |
| `provider` | Selection | AI provider override | "openai"\|"claude"\|"local" |
| `model` | Char | AI model override | "gpt-4o" |
| `system_prompt` | Text | System instructions for agent | "You are an expert..." |
| `user_prompt_template` | Text | User prompt template | "Analyze invoice {invoice_id}" |
| `tool_ids` | Many2many | Tools available to agent | [(6, 0, [1, 2, 3])] |
| `temperature` | Float | Response randomness (0-2) | 0.7 |
| `max_tokens` | Integer | Max response tokens | 2000 |
| `top_p` | Float | Nucleus sampling (0-1) | 1.0 |
| `frequency_penalty` | Float | Penalty for repetition (-2 to 2) | 0.0 |
| `presence_penalty` | Float | Penalty for new topics (-2 to 2) | 0.0 |
| `conversation_history` | Boolean | Enable conversation history | True |
| `history_limit` | Integer | Max messages in history | 10 |
| `active` | Boolean | Agent is active | True |

**Create Agent:**

```python
agent = env['ai.agent'].create({
    'name': 'Invoice Analyzer',
    'technical_name': 'invoice_analyzer',
    'model_id': env.ref('account.model_account_move').id,
    'provider': 'openai',
    'model': 'gpt-4o',
    'system_prompt': '''You are an expert invoice analyst. Your role is to:
- Extract key information from invoices (vendor, date, amount, line items)
- Validate invoice data for completeness and accuracy
- Flag potential issues or anomalies
- Suggest appropriate GL accounts for invoice lines

Always provide structured, actionable responses.''',
    'user_prompt_template': 'Analyze invoice {invoice_id} and extract all key details.',
    'tool_ids': [(6, 0, [
        env.ref('ipai_ai_tools.tool_read_invoice').id,
        env.ref('ipai_ai_tools.tool_validate_vendor').id,
        env.ref('ipai_ai_tools.tool_suggest_account').id
    ])],
    'temperature': 0.3,  # Lower for factual analysis
    'max_tokens': 2000,
    'conversation_history': True,
    'history_limit': 5,
    'active': True
})
```

---

## Access Methods

### Method 1: UI Panel (Alt+Shift+F)

The quickest way to interact with AI agents is via the integrated UI panel.

**Usage:**
1. Press `Alt+Shift+F` from any Odoo view
2. Select an agent from the dropdown menu
3. Type your question or request
4. Review agent response
5. Continue conversation or close panel

**Features:**
- Keyboard shortcut: `Alt+Shift+F`
- React + Fluent UI interface
- Conversation history per session
- Context awareness (current record/view)
- Copy/paste support

**Configuration:**

```javascript
// Panel configuration in ipai_ai_agents_ui module
{
  "keybinding": "Alt+Shift+F",
  "position": "right",
  "width": "400px",
  "theme": "fluent",
  "animations": true,
  "persistHistory": true
}
```

### Method 2: Odoo Shell (Programmatic)

For automation and testing, use the Odoo shell to interact with agents programmatically.

**List Available Agents:**

```python
# Get all active agents
agents = env['ai.agent'].search([('active', '=', True)])
for agent in agents:
    print(f"{agent.id}: {agent.name} ({agent.technical_name})")
    print(f"  Model: {agent.model_id.model}")
    print(f"  Provider: {agent.provider}")
    print(f"  Tools: {len(agent.tool_ids)}")
    print()

# Get agents for specific Odoo model
invoice_agents = env['ai.agent'].search([
    ('model_id.model', '=', 'account.move'),
    ('active', '=', True)
])
```

**Execute Agent:**

```python
# Execute agent with simple prompt
agent = env['ai.agent'].browse(1)
result = agent.execute_agent(
    prompt="What are the key details of invoice INV/2024/001?",
    context={'invoice_id': 123}
)

print(f"Response: {result['response']}")
print(f"Tokens used: {result['usage']['total_tokens']}")
print(f"Cost: ${result['cost']:.4f}")

# Execute agent with current record context
invoice = env['account.move'].browse(123)
result = agent.with_context(active_id=invoice.id).execute_agent(
    prompt="Analyze this invoice"
)

# Execute agent with conversation history
session_id = 'session-123'
result1 = agent.execute_agent(
    prompt="What is the total amount?",
    session_id=session_id
)
result2 = agent.execute_agent(
    prompt="Who is the vendor?",
    session_id=session_id  # Continues conversation
)
```

**Test Agent:**

```python
# Test agent with sample data
result = agent.test_agent(
    prompt="Extract vendor name and total amount",
    test_record_id=123
)

print(f"Test Result: {result['success']}")
print(f"Response: {result['response']}")
print(f"Validation: {result['validation']}")
```

### Method 3: REST API

For external integrations, use the REST API to interact with agents.

**Endpoint:** `POST /api/ai/chat`

**Authentication:** Bearer token or Odoo session

**Request:**

```bash
curl -X POST http://localhost:8069/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "agent_id": 1,
    "message": "What are my overdue invoices?",
    "session_id": "session-abc123",
    "context": {
      "user_id": 2,
      "company_id": 1
    }
  }'
```

**Response:**

```json
{
  "success": true,
  "response": "You have 3 overdue invoices:\n1. INV/2024/001 - $1,250 (7 days overdue)\n2. INV/2024/003 - $890 (3 days overdue)\n3. INV/2024/005 - $2,100 (14 days overdue)\n\nTotal overdue: $4,240",
  "session_id": "session-abc123",
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 120,
    "total_tokens": 270
  },
  "cost": 0.0054,
  "timestamp": "2024-02-10T12:34:56Z"
}
```

**List Agents Endpoint:** `GET /api/ai/agents`

```bash
curl -X GET http://localhost:8069/api/ai/agents \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**

```json
{
  "agents": [
    {
      "id": 1,
      "name": "Invoice Analyzer",
      "technical_name": "invoice_analyzer",
      "model": "account.move",
      "provider": "openai",
      "active": true
    },
    {
      "id": 2,
      "name": "Expense Assistant",
      "technical_name": "expense_assistant",
      "model": "hr.expense",
      "provider": "claude",
      "active": true
    }
  ]
}
```

---

## Common Operations

### Monitor Usage & Cost

```python
# Get usage stats for specific agent
agent = env['ai.agent'].browse(1)
usage_records = env['ai.usage'].search([
    ('agent_id', '=', agent.id),
    ('create_date', '>=', '2024-01-01')
])

total_tokens = sum(u.total_tokens for u in usage_records)
total_cost = sum(u.cost for u in usage_records)
total_requests = len(usage_records)

print(f"Agent: {agent.name}")
print(f"Total Requests: {total_requests}")
print(f"Total Tokens: {total_tokens:,}")
print(f"Total Cost: ${total_cost:.2f}")
print(f"Avg Tokens/Request: {total_tokens/total_requests if total_requests > 0 else 0:.0f}")
print(f"Avg Cost/Request: ${total_cost/total_requests if total_requests > 0 else 0:.4f}")

# Get usage by provider
openai_usage = env['ai.usage'].search([
    ('provider', '=', 'openai'),
    ('create_date', '>=', '2024-01-01')
])
claude_usage = env['ai.usage'].search([
    ('provider', '=', 'claude'),
    ('create_date', '>=', '2024-01-01')
])

print(f"\nOpenAI Usage: {sum(u.cost for u in openai_usage):.2f}")
print(f"Claude Usage: {sum(u.cost for u in claude_usage):.2f}")

# Get usage by date
from collections import defaultdict
usage_by_date = defaultdict(float)
for usage in env['ai.usage'].search([('create_date', '>=', '2024-01-01')]):
    date = usage.create_date.date()
    usage_by_date[date] += usage.cost

for date, cost in sorted(usage_by_date.items()):
    print(f"{date}: ${cost:.2f}")
```

### Manage Rate Limits

```python
# Check current rate limit status
rate_limiter = env['ai.rate_limiter'].get_current_limits()
print(f"Requests this minute: {rate_limiter['requests_current']}/{rate_limiter['requests_limit']}")
print(f"Tokens this minute: {rate_limiter['tokens_current']}/{rate_limiter['tokens_limit']}")
print(f"Time until reset: {rate_limiter['reset_seconds']}s")

# Adjust rate limits
env['ir.config_parameter'].sudo().set_param('ai.rate_limit.rpm', '100')
env['ir.config_parameter'].sudo().set_param('ai.rate_limit.tpm', '200000')

# Bypass rate limiting for specific operation (admin only)
agent = env['ai.agent'].browse(1)
result = agent.with_context(bypass_rate_limit=True).execute_agent(
    prompt="Emergency analysis required"
)
```

### Manage Conversation History

```python
# Get conversation history for session
session_id = 'session-123'
history = env['ai.conversation'].search([
    ('session_id', '=', session_id)
], order='create_date ASC')

for msg in history:
    print(f"[{msg.role}] {msg.content[:100]}...")

# Clear conversation history
env['ai.conversation'].search([
    ('session_id', '=', session_id)
]).unlink()

# Clear all old conversations (older than 30 days)
from datetime import datetime, timedelta
cutoff_date = datetime.now() - timedelta(days=30)
env['ai.conversation'].search([
    ('create_date', '<', cutoff_date)
]).unlink()

# Export conversation history
conversations = env['ai.conversation'].search([
    ('agent_id', '=', 1),
    ('create_date', '>=', '2024-01-01')
])
for conv in conversations:
    print(f"{conv.create_date}: [{conv.role}] {conv.content}")
```

---

## Troubleshooting

### Agent Not Responding

**Symptoms:** Agent doesn't respond or times out

**Diagnosis:**

```python
# 1. Check provider API key
api_key = env['ir.config_parameter'].sudo().get_param('ai.openai.api_key')
print(f"API Key configured: {'Yes' if api_key else 'No'}")
print(f"API Key prefix: {api_key[:15]}..." if api_key else "")

# 2. Check agent configuration
agent = env['ai.agent'].browse(1)
print(f"Agent active: {agent.active}")
print(f"Provider: {agent.provider}")
print(f"Model: {agent.model}")
print(f"System prompt length: {len(agent.system_prompt)} chars")

# 3. Check rate limits
rate_limiter = env['ai.rate_limiter'].get_current_limits()
if rate_limiter['requests_current'] >= rate_limiter['requests_limit']:
    print("RATE LIMIT EXCEEDED - Wait before retrying")

# 4. Check logs
tail -f /var/log/odoo/odoo.log | grep AI
```

**Solutions:**
1. Verify API key is set and valid
2. Check provider endpoint is accessible
3. Ensure rate limits not exceeded
4. Review agent system prompt for errors
5. Check timeout settings (increase if needed)

### High Token Usage

**Symptoms:** Unexpectedly high token consumption and costs

**Diagnosis:**

```python
# 1. Analyze token usage by agent
agents = env['ai.agent'].search([('active', '=', True)])
for agent in agents:
    usage = env['ai.usage'].search([('agent_id', '=', agent.id)])
    if usage:
        avg_tokens = sum(u.total_tokens for u in usage) / len(usage)
        print(f"{agent.name}: {avg_tokens:.0f} tokens/request")

# 2. Check conversation history settings
verbose_agents = env['ai.agent'].search([
    ('conversation_history', '=', True),
    ('history_limit', '>', 10)
])
print(f"Agents with high history limits: {len(verbose_agents)}")

# 3. Review large responses
large_responses = env['ai.usage'].search([
    ('completion_tokens', '>', 1000)
], limit=10, order='completion_tokens DESC')
for usage in large_responses:
    print(f"Agent: {usage.agent_id.name}, Tokens: {usage.completion_tokens}")
```

**Solutions:**
1. Reduce `history_limit` to 5 or fewer messages
2. Lower `max_tokens` parameter
3. Enable caching for RAG queries
4. Use more efficient prompts
5. Consider switching to cheaper model for simple queries

### Poor Response Quality

**Symptoms:** Agent responses are inaccurate or unhelpful

**Diagnosis:**

```python
# 1. Review system prompt
agent = env['ai.agent'].browse(1)
print(f"System Prompt:\n{agent.system_prompt}")

# 2. Check agent temperature
print(f"Temperature: {agent.temperature}")
# (0 = deterministic, 2 = very random)

# 3. Review recent responses
recent_usage = env['ai.usage'].search([
    ('agent_id', '=', agent.id)
], limit=5, order='create_date DESC')
for usage in recent_usage:
    print(f"Prompt: {usage.prompt[:100]}...")
    print(f"Response: {usage.response[:200]}...")
    print()
```

**Solutions:**
1. Refine system prompt with clearer instructions
2. Adjust temperature (lower for factual, higher for creative)
3. Add relevant tools to agent
4. Include examples in system prompt
5. Enable RAG for context-specific queries

### Tool Execution Failures

**Symptoms:** Agent reports tool execution errors

**Diagnosis:**

```python
# 1. Check tool configuration
agent = env['ai.agent'].browse(1)
print(f"Tools assigned: {len(agent.tool_ids)}")
for tool in agent.tool_ids:
    print(f"  - {tool.name} ({tool.technical_name})")
    print(f"    Active: {tool.active}")
    print(f"    Function: {tool.function_name}")

# 2. Test tool execution
tool = agent.tool_ids[0]
result = tool.test_execution()
print(f"Tool test result: {result}")

# 3. Check tool permissions
print(f"Tool requires admin: {tool.requires_admin}")
print(f"Tool groups: {tool.group_ids.mapped('name')}")
```

**Solutions:**
1. Verify tools are active and properly configured
2. Check user has required permissions for tools
3. Test tools independently before assigning to agent
4. Review tool function code for errors
5. Add error handling to tool functions

---

## Performance Optimization

### Enable RAG Caching

```python
# Enable RAG caching for faster repeated queries
env['ir.config_parameter'].sudo().set_param('ai.rag.cache.enabled', 'True')
env['ir.config_parameter'].sudo().set_param('ai.rag.cache.ttl', '3600')  # 1 hour

# Clear RAG cache
env['ai.rag.cache'].search([]).unlink()
```

### Batch Processing

```python
# Process multiple requests in batch
agent = env['ai.agent'].browse(1)
invoices = env['account.move'].search([('state', '=', 'draft')], limit=10)

results = []
for invoice in invoices:
    result = agent.with_context(active_id=invoice.id).execute_agent(
        prompt="Quick validation check"
    )
    results.append({
        'invoice_id': invoice.id,
        'invoice_name': invoice.name,
        'validation': result['response']
    })
    env.cr.commit()  # Commit after each to avoid long transactions
```

### Reduce Context Size

```python
# Trim context to essential fields only
invoice = env['account.move'].browse(123)
context_data = {
    'invoice_id': invoice.id,
    'invoice_number': invoice.name,
    'partner_name': invoice.partner_id.name,
    'amount_total': invoice.amount_total,
    'state': invoice.state
}
# Instead of passing entire invoice record
```

---

## Security & Compliance

### Data Privacy

```python
# Enable PII filtering
env['ir.config_parameter'].sudo().set_param('ai.privacy.pii_filter.enabled', 'True')

# Configure fields to redact
env['ir.config_parameter'].sudo().set_param('ai.privacy.redact_fields', 'email,phone,ssn,tax_id')

# Disable external provider (use local models only)
env['ir.config_parameter'].sudo().set_param('ai.provider.default', 'local')
```

### Audit Logging

```python
# Enable comprehensive audit logging
env['ir.config_parameter'].sudo().set_param('ai.audit.enabled', 'True')
env['ir.config_parameter'].sudo().set_param('ai.audit.log_prompts', 'True')
env['ir.config_parameter'].sudo().set_param('ai.audit.log_responses', 'True')

# Query audit logs
audit_logs = env['ai.audit.log'].search([
    ('create_date', '>=', '2024-01-01'),
    ('user_id', '=', env.user.id)
])
for log in audit_logs:
    print(f"{log.create_date}: {log.agent_id.name} - {log.action}")
```

### Access Control

```python
# Restrict agent access to specific user groups
agent = env['ai.agent'].browse(1)
agent.write({
    'group_ids': [(6, 0, [
        env.ref('base.group_user').id,
        env.ref('account.group_account_manager').id
    ])]
})

# Check user access
user = env.user
can_access = agent in env['ai.agent'].search([
    ('id', '=', agent.id),
    ('group_ids', 'in', user.groups_id.ids)
])
print(f"User can access agent: {can_access}")
```

---

## Further Reading

**Architecture Documentation:**
- `/docs/architecture/IPAI_AI_PLATFORM_ARCH.md` - AI platform architecture
- `/docs/architecture/ASK_AI_CONTRACT.md` - Ask AI feature contract

**Module Documentation:**
- `/addons/ipai/ipai_ai_agent_builder/README.md` - Agent builder module
- `/addons/ipai/ipai_ai_tools/README.md` - Tools system
- `/addons/ipai/ipai_ai_rag/README.md` - RAG implementation

**Related Settings:**
- `/docs/ai/ODOO_SETTINGS_REFERENCE.md` - General settings
- `/docs/ai/ODOO_SETTINGS_CHEATSHEET.md` - Quick commands

---

**Last Updated:** 2024-02-10
**Odoo Version:** 19.0 CE
**IPAI AI Platform Version:** 1.0
