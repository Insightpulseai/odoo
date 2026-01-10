# IPAI AI Connectors

Inbound integration hub for the IPAI AI platform.

## Features

- Token-authenticated webhook endpoint
- Support for n8n, GitHub, Slack, and custom sources
- Event persistence with full audit trail
- Admin interface for viewing and managing events
- State machine for event processing (received → processing → processed/failed/ignored)

## Installation

1. Install the module in Odoo
2. Set the `IPAI_CONNECTORS_TOKEN` environment variable
3. Configure external systems to POST events to the endpoint

## Configuration

### Environment Variables

```bash
# Required: Shared secret token for webhook authentication
IPAI_CONNECTORS_TOKEN=your_secure_random_token
```

## API Endpoints

### POST /ipai_ai_connectors/event

Receive and store an integration event.

**Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "token": "your_secure_token",
    "source": "n8n",
    "event_type": "workflow.completed",
    "ref": "workflow_123",
    "payload": {
      "status": "success",
      "data": { ... }
    }
  },
  "id": 1
}
```

**Response (success):**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "ok": true,
    "event_id": 42
  },
  "id": 1
}
```

**Response (error):**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "ok": false,
    "error": "Invalid token"
  },
  "id": 1
}
```

### GET /ipai_ai_connectors/health

Health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "module": "ipai_ai_connectors",
  "version": "18.0.1.0.0"
}
```

## Supported Sources

| Source | Description |
|--------|-------------|
| `n8n` | n8n workflow automation |
| `github` | GitHub webhooks |
| `slack` | Slack events |
| `custom` | Any custom integration |

## Event States

| State | Description |
|-------|-------------|
| `received` | Event received, awaiting processing |
| `processing` | Event is being processed |
| `processed` | Event successfully processed |
| `failed` | Processing failed (see error_message) |
| `ignored` | Event marked as ignored |

## Usage with n8n

1. Create an HTTP Request node in n8n
2. Set method to POST
3. Set URL to `https://your-odoo.com/ipai_ai_connectors/event`
4. Set body type to JSON with:
   ```json
   {
     "jsonrpc": "2.0",
     "method": "call",
     "params": {
       "token": "{{ $env.IPAI_CONNECTORS_TOKEN }}",
       "source": "n8n",
       "event_type": "your_workflow_name",
       "ref": "{{ $json.id }}",
       "payload": {{ JSON.stringify($json) }}
     },
     "id": 1
   }
   ```

## Security

- Events are company-scoped via record rules
- Token must be kept secret
- CSRF is disabled for the webhook endpoint (external access)
- Failed authentication attempts are logged

## License

LGPL-3
