# Knowledge Item: Multi-Channel Ingress (Telegram/n8n)

## 1. Submission Envelope Pattern
Submissions from external channels (Telegram, WhatsApp, Email) must be normalized by an orchestrator (n8n) into a **Submission Envelope** before hitting the Odoo RPC.

### Envelope Fields
- `envelope_id`: UUID for the unique submission.
- `source_channel`: Origin (e.g., `telegram`).
- `source_message_id`: Original message ID for deduplication.
- `attachments`: The raw file payload.

## 2. Operational Gotchas
- **Telegram Webhook Limit**: A bot token supports only ONE webhook. Use separate tokens for Staging vs. Production bots to avoid broken delivery.
- **Binary Size**: n8n Webhook default limit is 16MB; ensure Odoo `ir.attachment` limits are aligned.
- **Deduplication**: Odoo must perform a `search([('source_message_id', '=', id)])` check before creating records to ensure idempotency.

## 3. Orchestration vs System of Record
- **n8n**: Transient state only. It moves data and handles protocol conversion.
- **Odoo**: Permanent state only. It owns the business lifecycle and accounting result.
