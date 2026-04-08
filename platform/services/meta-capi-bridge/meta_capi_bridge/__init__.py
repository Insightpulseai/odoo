"""Meta Conversions API Bridge — Azure Function.

Receives canonical business events from Odoo (via webhook/queue)
and relays them to Meta Conversions API with idempotency,
retry, and dead-letter handling.

Architecture: Odoo → webhook → this function → Meta CAPI
Secrets: Azure Key Vault (kv-ipai-dev)
Direct Odoo-to-Meta calls: NEVER allowed
"""
