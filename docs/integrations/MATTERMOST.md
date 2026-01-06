# Mattermost Integration

## Overview

Mattermost is our team chat platform, providing secure, self-hosted messaging for InsightPulse AI operations.

**Production URL:** https://chat.insightpulseai.net

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Mattermost Integration                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Odoo CE                          ipai-ops-stack                │
│   ┌────────────────────┐           ┌──────────────────────┐     │
│   │ ipai_integrations  │           │   Mattermost Server  │     │
│   │ - Connector config │◄─────────►│   (Docker)           │     │
│   │ - Webhooks         │   API v4  │                      │     │
│   │ - Bot accounts     │           │   PostgreSQL         │     │
│   │ - Audit logs       │           │   (shared)           │     │
│   └────────────────────┘           └──────────────────────┘     │
│   ┌────────────────────┐                                        │
│   │ ipai_mattermost_   │                                        │
│   │ connector          │                                        │
│   │ - API client       │                                        │
│   │ - Channel sync     │                                        │
│   │ - Message logs     │                                        │
│   └────────────────────┘                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Odoo Modules

### ipai_integrations

Central admin UI for all integrations:
- Connector configuration (URL, auth type)
- Webhook management (incoming/outgoing)
- Bot account management
- OAuth app management
- Audit logging

### ipai_mattermost_connector

Mattermost-specific functionality:
- API v4 client (`MattermostClient`)
- Channel synchronization
- Message posting from Odoo workflows
- Message logging

## Configuration

### 1. System Parameters

Set these in Odoo (Settings > Technical > Parameters > System Parameters):

| Key | Description |
|-----|-------------|
| `ipai_integrations.mattermost_url` | Base URL (default: https://chat.insightpulseai.net) |
| `ipai_mattermost.token_{connector_id}` | Bot/Personal access token |

### 2. Create Connector

1. Go to **Integrations > Configuration > Connectors**
2. Create new connector:
   - Name: Mattermost (InsightPulse AI)
   - Type: Mattermost
   - Base URL: https://chat.insightpulseai.net
   - Auth Type: Personal Access Token
3. Click **Test Connection**
4. If successful, click **Activate**

### 3. Configure Webhooks

#### Incoming Webhooks (Mattermost → Odoo)

1. In Mattermost: Integrations > Incoming Webhooks > Add
2. Copy the webhook URL
3. In Odoo: Integrations > Webhooks > Create
   - Direction: Incoming
   - Endpoint Path: /integrations/mattermost/webhook

#### Outgoing Webhooks (Odoo → Mattermost)

1. In Odoo: Integrations > Webhooks > Create
   - Direction: Outgoing
   - Target URL: Your Mattermost incoming webhook URL
   - Trigger Model: e.g., `project.task`
   - Trigger Events: On Create / On Update

### 4. Bot Configuration

1. In Mattermost: Integrations > Bot Accounts > Add
2. Copy the bot token
3. In Odoo: Integrations > Bots > Create
   - Connector: Mattermost
   - Bot Username: @odoo-bot
   - Bot Token: (paste token)
4. Configure slash commands if needed

## API Usage

### Post Message from Odoo

```python
connector = self.env["ipai.integration.connector"].search([
    ("connector_type", "=", "mattermost"),
    ("state", "=", "active"),
], limit=1)

if connector:
    connector.mm_post_message(
        channel_id="abc123",
        message="Hello from Odoo!",
        props={"card": {"title": "Task Update"}}
    )
```

### Sync Channels

```python
connector.action_test_connection()  # Verify connection
self.env["ipai.mattermost.channel"].sync_channels(connector)
```

## Webhooks

### Incoming Webhook Payload

Mattermost sends this format to Odoo:

```json
{
  "token": "verification_token",
  "team_id": "team_id",
  "team_domain": "team_name",
  "channel_id": "channel_id",
  "channel_name": "channel_name",
  "timestamp": 1234567890,
  "user_id": "user_id",
  "user_name": "username",
  "post_id": "post_id",
  "text": "message text",
  "trigger_word": "keyword"
}
```

### Outgoing Webhook Payload

Odoo sends this format to Mattermost:

```json
{
  "text": "Message text with **Markdown** support",
  "channel": "channel_name",
  "username": "Odoo Bot",
  "icon_url": "https://example.com/icon.png",
  "props": {
    "card": "Optional rich card content"
  }
}
```

## Troubleshooting

### Connection Failed

1. Verify Mattermost is running: `curl https://chat.insightpulseai.net/api/v4/system/ping`
2. Check token is valid and has correct permissions
3. Review audit logs in Odoo

### Messages Not Posting

1. Check bot has permission to post in channel
2. Verify channel ID is correct
3. Check rate limits haven't been exceeded

### Webhooks Not Firing

1. Verify webhook is enabled in both systems
2. Check signing secret matches
3. Review delivery logs in Odoo

## External Resources

- **Runtime Deployment:** `ipai-ops-stack` repository
- **Mattermost API Docs:** https://api.mattermost.com/
- **Channel:** #odoo-integrations on chat.insightpulseai.net
