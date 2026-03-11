# Azure Bot Service Contract

> Cross-boundary contract: Azure Bot Service + n8n + Supabase Identity

## Parties
- **Azure Bot Service** (F0 free tier): Bot registration + Teams channel
- **n8n** (self-hosted): Webhook endpoint, orchestration, response routing
- **Supabase**: Identity mapping (`kb.channel_identity_map`), RAG search
- **Odoo**: Business action execution via XML-RPC

## Data Flow
```
Teams User → Azure Bot Service → n8n /webhook/teams-bot-activity
  → Extract activity (user AAD ID, message text)
  → Forward to AI Agent Router
  → Identity resolution (Supabase kb.resolve_channel_user)
  → Intent classification → RAG / Navigation / Transaction
  → Response via Bot Framework REST API
```

## Security
- Bot Framework JWT token validated on every inbound request
- AAD Object ID used for identity mapping (not email or display name)
- Odoo XML-RPC calls use resolved Odoo user context
- n8n credentials stored in n8n credential store, not in workflow JSON

## Configuration
| Parameter | Location | Value |
|-----------|----------|-------|
| Bot Name | Azure | `ipai-openbrain-bot` |
| Messaging Endpoint | Azure | `https://n8n.insightpulseai.com/webhook/teams-bot-activity` |
| MicrosoftAppId | n8n credentials | From Azure Bot registration |
| MicrosoftAppPassword | n8n credentials | From Azure App registration |

## Lifecycle
- Created: 2026-03-10
- Owner: InsightPulse AI
- Review: Quarterly
