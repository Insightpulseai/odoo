# SHADOW ENTERPRISE: AI ENRICHMENT PROTOCOL
# ==========================================
# Automated Action: Trigger AI Enrichment
# Model: Contact (res.partner)
# Trigger: On Creation
# Action: Execute Python Code

import requests

# URL of your n8n Webhook
# IMPORTANT: Ensure this matches your n8n domain
webhook_url = "https://ipa.insightpulseai.net/webhook/enrich-contact"

# Payload to send to AI
payload = {
    "id": record.id,
    "name": record.name,
    "email": record.email or "",
    "website": record.website or ""
}

try:
    # Send to n8n (Timeout set to 1s to prevent blocking Odoo UI)
    response = requests.post(webhook_url, json=payload, timeout=1)

    # Optional: Log success (for debugging only, remove in production)
    if response.status_code == 200:
        env['ir.logging'].sudo().create({
            'name': 'AI Enrichment Success',
            'type': 'server',
            'level': 'info',
            'message': f'Contact {record.id} ({record.name}) sent for AI enrichment',
            'path': 'res.partner',
            'func': 'create',
            'line': '0'
        })
except requests.exceptions.Timeout:
    # Timeout is expected for async processing - not an error
    pass
except Exception as e:
    # Log failure silently; do not crash the user's creation process
    env['ir.logging'].sudo().create({
        'name': 'AI Enrichment Error',
        'type': 'server',
        'level': 'warning',
        'message': str(e),
        'path': 'res.partner',
        'func': 'create',
        'line': '0'
    })
