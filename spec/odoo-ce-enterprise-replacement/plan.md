# Plan: Odoo CE Enterprise Replacement

## Phase 1: Foundation (ipai_enterprise_bridge)

### 1.1 Module Scaffold
```bash
# Create module structure
mrbob bobtemplates.odoo:addon
# Move to addons/ipai/ipai_enterprise_bridge/
```

### 1.2 Core Dependencies
```python
# __manifest__.py
{
    'name': 'IPAI Enterprise Bridge',
    'depends': [
        'base', 'mail', 'auth_oauth', 'fetchmail',
        'base_setup', 'web',
    ],
    'external_dependencies': {
        'python': ['requests', 'paho-mqtt'],
    },
}
```

### 1.3 Base Configuration Model
```python
# models/enterprise_bridge_config.py
class EnterpriseBridgeConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    # Email
    mail_provider = fields.Selection([
        ('mailgun', 'Mailgun'),
        ('smtp', 'Generic SMTP'),
        ('postfix', 'Local Postfix'),
    ])
    mailgun_api_key = fields.Char()
    mailgun_domain = fields.Char()

    # OAuth
    oauth_google_enabled = fields.Boolean()
    oauth_azure_enabled = fields.Boolean()

    # IoT
    iot_mqtt_broker = fields.Char()
    iot_mqtt_port = fields.Integer(default=1883)
```

## Phase 2: Email Integration

### 2.1 Outbound (Mailgun SMTP)
```python
# data/mail_server.xml
<record id="mailgun_smtp" model="ir.mail_server">
    <field name="name">Mailgun SMTP</field>
    <field name="smtp_host">smtp.mailgun.org</field>
    <field name="smtp_port">587</field>
    <field name="smtp_encryption">starttls</field>
    <field name="smtp_user" eval="env.get('MAILGUN_SMTP_USER', '')"/>
    <field name="smtp_pass" eval="env.get('MAILGUN_SMTP_PASSWORD', '')"/>
</record>
```

### 2.2 Inbound (Fetchmail)
```python
# data/fetchmail_server.xml
<record id="fetchmail_main" model="fetchmail.server">
    <field name="name">Main Inbox</field>
    <field name="server_type">imap</field>
    <field name="server">imap.mailgun.org</field>
    <field name="port">993</field>
    <field name="is_ssl">True</field>
    <field name="user" eval="env.get('MAIL_CATCHALL_USER', '')"/>
    <field name="password" eval="env.get('MAIL_CATCHALL_PASSWORD', '')"/>
</record>
```

### 2.3 DNS Configuration Script
```bash
#!/bin/bash
# scripts/mail_dns_setup.sh
DOMAIN="${MAILGUN_DOMAIN:-mg.example.com}"

# Verify DNS records
dig +short TXT "${DOMAIN}" | grep -q "v=spf1" || echo "SPF missing"
dig +short TXT "smtp._domainkey.${DOMAIN}" | grep -q "k=rsa" || echo "DKIM missing"
dig +short TXT "_dmarc.${DOMAIN}" | grep -q "v=DMARC1" || echo "DMARC missing"
```

## Phase 3: OAuth Integration

### 3.1 Google OAuth
```python
# data/oauth_google.xml
<record id="oauth_google" model="auth.oauth.provider">
    <field name="name">Google</field>
    <field name="client_id" eval="env.get('GOOGLE_CLIENT_ID', '')"/>
    <field name="auth_endpoint">https://accounts.google.com/o/oauth2/v2/auth</field>
    <field name="token_endpoint">https://oauth2.googleapis.com/token</field>
    <field name="scope">email profile openid</field>
    <field name="enabled">True</field>
</record>
```

### 3.2 Azure AD OAuth
```python
# data/oauth_azure.xml
<record id="oauth_azure" model="auth.oauth.provider">
    <field name="name">Microsoft 365</field>
    <field name="client_id" eval="env.get('AZURE_CLIENT_ID', '')"/>
    <field name="auth_endpoint">https://login.microsoftonline.com/common/oauth2/v2.0/authorize</field>
    <field name="token_endpoint">https://login.microsoftonline.com/common/oauth2/v2.0/token</field>
    <field name="scope">openid email profile User.Read</field>
    <field name="enabled">True</field>
</record>
```

## Phase 4: IoT Bridge

### 4.1 Device Registry Model
```python
# models/iot_device.py
class IotDevice(models.Model):
    _name = 'ipai.iot.device'

    name = fields.Char(required=True)
    device_type = fields.Selection([
        ('printer', 'Printer'),
        ('scale', 'Scale'),
        ('drawer', 'Cash Drawer'),
        ('display', 'Customer Display'),
        ('scanner', 'Barcode Scanner'),
    ])
    mqtt_topic = fields.Char()
    status = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ], default='offline')
    last_seen = fields.Datetime()
```

### 4.2 MQTT Bridge
```python
# models/iot_mqtt_bridge.py
import paho.mqtt.client as mqtt

class IotMqttBridge(models.AbstractModel):
    _name = 'ipai.iot.mqtt.bridge'

    def _connect_mqtt(self):
        config = self.env['ir.config_parameter'].sudo()
        broker = config.get_param('iot.mqtt.broker', 'localhost')
        port = int(config.get_param('iot.mqtt.port', 1883))

        client = mqtt.Client()
        client.connect(broker, port)
        return client

    def send_command(self, device, command):
        client = self._connect_mqtt()
        client.publish(device.mqtt_topic, json.dumps(command))
        client.disconnect()
```

## Phase 5: Multi-Company

### 5.1 Company Seeds
```xml
<!-- data/res_company.xml -->
<record id="company_tbwa" model="res.company">
    <field name="name">TBWA\SMP</field>
    <field name="email">info@tbwa-smp.com</field>
</record>
<record id="company_ipai" model="res.company">
    <field name="name">InsightPulseAI</field>
    <field name="email">info@insightpulseai.net</field>
    <field name="parent_id" ref="company_tbwa"/>
</record>
```

### 5.2 User Seeds
```xml
<!-- data/res_users.xml -->
<record id="user_admin_tbwa" model="res.users">
    <field name="name">TBWA Admin</field>
    <field name="login">admin@tbwa-smp.com</field>
    <field name="company_id" ref="company_tbwa"/>
    <field name="company_ids" eval="[(4, ref('company_tbwa')), (4, ref('company_ipai'))]"/>
</record>
```

## Phase 6: CI/CD Integration

### 6.1 Setup Script
```bash
#!/bin/bash
# scripts/setup_enterprise_bridge.sh
set -euo pipefail

DB="${1:-odoo_prod}"

# Install module
docker compose exec -T odoo odoo -d "$DB" -i ipai_enterprise_bridge --stop-after-init

# Apply config parameters
docker compose exec -T odoo odoo shell -d "$DB" <<'EOF'
env['ir.config_parameter'].sudo().set_param('mail.catchall.domain', os.getenv('MAIL_CATCHALL_DOMAIN', ''))
env['ir.config_parameter'].sudo().set_param('iot.mqtt.broker', os.getenv('IOT_MQTT_BROKER', 'localhost'))
env.cr.commit()
EOF

# Verify
./scripts/verify_enterprise_bridge.sh "$DB"
```

### 6.2 Verification Script
```bash
#!/bin/bash
# scripts/verify_enterprise_bridge.sh
set -euo pipefail

DB="${1:-odoo_prod}"

echo "Checking module installation..."
docker compose exec -T db psql -U odoo -d "$DB" -c "
SELECT name, state FROM ir_module_module
WHERE name = 'ipai_enterprise_bridge';"

echo "Checking mail server..."
docker compose exec -T db psql -U odoo -d "$DB" -c "
SELECT name, smtp_host FROM ir_mail_server WHERE active = true;"

echo "Checking OAuth providers..."
docker compose exec -T db psql -U odoo -d "$DB" -c "
SELECT name, enabled FROM auth_oauth_provider;"

echo "Checking IoT devices..."
docker compose exec -T db psql -U odoo -d "$DB" -c "
SELECT name, status FROM ipai_iot_device;" 2>/dev/null || echo "No IoT devices yet"
```

## Execution Order

1. Create `ipai_enterprise_bridge` module scaffold
2. Implement email layer (Mailgun SMTP + Fetchmail)
3. Implement OAuth layer (Google + Azure)
4. Implement IoT layer (MQTT bridge)
5. Implement multi-company seeds
6. Create CI/CD scripts
7. Run validation suite
8. Document parity matrix
