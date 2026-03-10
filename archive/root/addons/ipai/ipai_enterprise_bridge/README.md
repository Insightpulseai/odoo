# IPAI Enterprise Bridge

Replace Odoo Enterprise Edition (EE) and IAP features with self-hosted CE+OCA alternatives.

## Features

### Email (Non-IAP)
- Mailgun SMTP configuration
- Generic SMTP support
- Fetchmail integration
- DNS validation helpers

### OAuth (Non-EE)
- Google OAuth provider
- Azure AD OAuth provider
- Extensible provider framework

### IoT (Non-Subscription)
- Device registry model
- MQTT bridge for device communication
- WebSocket/HTTP alternatives
- Printer, scale, drawer, display support

## Installation

```bash
docker compose exec -T odoo odoo -d odoo_prod -i ipai_enterprise_bridge --stop-after-init
```

## Configuration

### Email (Mailgun)

Set environment variables:
```bash
MAILGUN_DOMAIN=mg.example.com
MAILGUN_SMTP_USER=postmaster@mg.example.com
MAILGUN_SMTP_PASSWORD=your-password
```

Then configure in Settings > General Settings > IPAI Enterprise Bridge.

### OAuth

1. Create OAuth app in Google Cloud Console / Azure Portal
2. Set client ID in Settings > General Settings > IPAI Enterprise Bridge
3. Enable the provider

### IoT

1. Deploy MQTT broker (Mosquitto recommended)
2. Configure broker host/port in Settings
3. Register devices in Enterprise Bridge > IoT Devices

## Dependencies

- `base`, `mail`, `auth_oauth`, `fetchmail`, `web`
- Python: `requests`, `paho-mqtt`

## License

LGPL-3.0
