# Configuration

## AI Agents

### Environment Variables

Set these in your `.env` file or container environment:

```bash
# LLM Provider (required)
IPAI_LLM_API_KEY=sk-your-api-key
IPAI_LLM_BASE_URL=https://api.openai.com/v1
IPAI_LLM_MODEL=gpt-4o-mini
IPAI_LLM_TEMPERATURE=0.2

# Supabase KB (required for RAG)
IPAI_SUPABASE_URL=https://your-project.supabase.co
IPAI_SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Embeddings (optional, for vector search)
IPAI_EMBEDDINGS_PROVIDER=openai
IPAI_EMBEDDINGS_MODEL=text-embedding-3-small
```

### Creating an Agent

1. Go to **AI → Configuration → Agents**
2. Click **Create**
3. Fill in:
   - **Name**: Display name (e.g., "Odoo Helper")
   - **System Prompt**: Instructions for the AI
   - **Sources**: Link knowledge sources
   - **Policy**: Read-only, Propose, or Execute

### Agent Policies

| Policy | Description |
|--------|-------------|
| Read Only | Agent can only answer questions |
| Propose | Agent can suggest actions (user approves) |
| Execute | Agent can execute read-only tools |

### Knowledge Sources

1. Go to **AI → Configuration → Sources**
2. Create sources for:
   - Documentation sites
   - GitHub repositories
   - PDF uploads
   - Custom databases

## Approvals

### Creating an Approval Type

1. Go to **Approvals → Configuration → Approval Types**
2. Click **Create**
3. Configure:
   - **Name**: Type name (e.g., "Purchase Approval")
   - **Model**: Which Odoo model requires approval
   - **Approval Type**: User, Group, or Manager
   - **Minimum Approvers**: Required approval count
   - **Auto-approve Amount**: Threshold for auto-approval

### Approval Type Options

| Type | Description |
|------|-------------|
| User | Specific users are approvers |
| Group | All users in a security group |
| Manager | Employee's management chain |

### Amount-based Auto-approval

```
auto_approve_amount = 500  # Requests ≤ $500 auto-approve
amount_field = amount_total  # Field containing the amount
```

### Security Groups

Assign users to groups:

- **Approvals / User**: Create requests, see own, approve assigned
- **Approvals / Manager**: Full access within company

## Multi-Company

### Company Isolation

All IPAI modules enforce company isolation via record rules:

```xml
<record id="rule_model_company" model="ir.rule">
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

### Switching Companies

Users can switch companies in the top-right menu. Data is filtered automatically.

## System Parameters

Some modules use system parameters for configuration:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ipai.ai_agents.default_agent` | Default agent ID | 1 |
| `ipai.approvals.notify_email` | Send email notifications | True |

Set via **Settings → Technical → System Parameters**.

## Scheduled Actions

### AI Agents

- **Cleanup Old Threads**: Removes threads older than 90 days (configurable)

### Approvals

- **Escalate Pending**: Escalates approvals pending > 48h
- **Notify Overdue**: Sends reminders for overdue approvals

Configure via **Settings → Technical → Automation → Scheduled Actions**.

## Integration

### REST API

All IPAI modules expose JSON-RPC endpoints:

```python
# AI Agents
POST /ipai_ai_agents/bootstrap
POST /ipai_ai_agents/ask
POST /ipai_ai_agents/feedback

# Approvals (via standard Odoo API)
POST /web/dataset/call_kw
```

### Webhooks

Configure outbound webhooks via n8n workflows for:
- New approval requests
- Approval status changes
- AI feedback events

## Troubleshooting

### AI Not Responding

1. Check `IPAI_LLM_API_KEY` is set
2. Verify Supabase connection
3. Check Odoo logs: `docker compose logs -f odoo-core`

### Approvals Not Triggering

1. Verify Approval Type is active
2. Check model matches exactly
3. Ensure user is in correct security group

### Performance Issues

1. Enable database indexes
2. Configure caching
3. Review scheduled action frequency
