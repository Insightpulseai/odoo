# EE/IAP to OCA/IPAI Replacement Mapping

> **Odoo Version:** 18.0 CE (19.0 ready)
> **Generated:** 2026-01-21
> **Master Module:** `ipai_enterprise_bridge`

---

## Replacement Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    EE/IAP Feature Request                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   1. Check Odoo CE Core       │
              │   (Already available?)        │
              └───────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ No                │ Yes → Use CE directly
                    ▼                   │
      ┌───────────────────────────────┐ │
      │   2. Check OCA 18.0 Addons    │ │
      │   (Vetted replacement?)       │ │
      └───────────────────────────────┘ │
                    │                   │
          ┌─────────┴─────────┐         │
          │ No                │ Yes → Install OCA module
          ▼                   │         │
┌───────────────────────────────┐       │
│   3. Use ipai_* Module        │       │
│   (Custom implementation)     │       │
└───────────────────────────────┘       │
          │                             │
          ▼                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              CE + OCA + IPAI Stack (No EE/IAP)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Settings Replacements

### 1.1 Multi-Company Inter-Company Rules

| Property | Value |
|----------|-------|
| **EE Setting** | Inter-Company Rules (auto-invoicing) |
| **EE Module** | `account_inter_company_rules` |
| **Why EE** | Automatic SO→PO creation between companies |

**Replacement Stack:**

| Layer | Module | Role |
|-------|--------|------|
| OCA | `account_invoice_inter_company` | Auto-create invoices between companies |
| OCA | `sale_order_inter_company` | Auto-create PO from SO |
| OCA | `purchase_order_inter_company` | Reverse direction |
| IPAI | `ipai_enterprise_bridge` | Unified settings UI |

**Data Model Mapping:**

```
EE: inter.company.rules → OCA: ir.config_parameter + module settings
EE: auto_generate_invoices → OCA: account_invoice_inter_company.auto_generate
```

**Configuration:**

```xml
<!-- data/inter_company_config.xml -->
<record id="param_inter_company_so" model="ir.config_parameter">
    <field name="key">sale_order_inter_company.auto_create</field>
    <field name="value">True</field>
</record>
```

---

### 1.2 IoT Box & Devices

| Property | Value |
|----------|-------|
| **EE Setting** | IoT Box, IoT Devices |
| **EE Module** | `iot`, `pos_iot`, `hw_*` |
| **Why EE** | Hardware integration layer |

**Replacement Stack:**

| Layer | Module | Role |
|-------|--------|------|
| OCA | `base_report_to_printer` | CUPS printer integration |
| OCA | `pingen` | Cloud printing service |
| OCA | `pos_printer_network` | Network receipt printers |
| IPAI | `ipai_iot_bridge` | Unified IoT gateway proxy |

**Data Model Mapping:**

```python
# ipai_iot_bridge/models/ipai_iot_device.py
class IpaiIotDevice(models.Model):
    _name = 'ipai.iot.device'
    _description = 'IPAI IoT Device (EE iot.device replacement)'

    name = fields.Char(required=True)
    device_type = fields.Selection([
        ('printer', 'Printer'),
        ('scale', 'Scale'),
        ('scanner', 'Barcode Scanner'),
        ('display', 'Customer Display'),
        ('payment', 'Payment Terminal'),
    ])
    connection_type = fields.Selection([
        ('usb', 'USB'),
        ('network', 'Network'),
        ('cups', 'CUPS'),
        ('printnode', 'PrintNode Cloud'),
    ])
    gateway_id = fields.Many2one('ipai.iot.gateway')
    ip_address = fields.Char()
    state = fields.Selection([
        ('draft', 'Not Connected'),
        ('connected', 'Connected'),
        ('error', 'Error'),
    ], default='draft')
```

**External Services:**

| Service | Purpose | Self-Hosted Option |
|---------|---------|-------------------|
| CUPS | Linux/Mac printing | ✓ Built-in |
| PrintNode | Cloud printing | ✓ Self-hosted API bridge |
| ESC/POS | Receipt printers | ✓ Direct network |

---

### 1.3 Mail Plugins (Outlook/Gmail Sync)

| Property | Value |
|----------|-------|
| **EE Setting** | Outlook/Gmail Mail Plugins |
| **EE Module** | `mail_plugin`, `mail_plugin_outlook`, `mail_plugin_gmail` |
| **Why EE** | Browser extension + 2-way sync |

**Replacement Stack:**

| Layer | Module | Role |
|-------|--------|------|
| OCA | `mail_tracking` | Email open/click tracking |
| OCA | `mail_tracking_mailgun` | Mailgun webhook integration |
| IPAI | `ipai_mail_integration` | MS Graph / Gmail API connector |
| IPAI | `ipai_enterprise_bridge` | Unified mail settings |

**Data Model Mapping:**

```python
# ipai_mail_integration/models/mail_oauth_provider.py
class MailOAuthProvider(models.Model):
    _name = 'ipai.mail.oauth.provider'
    _description = 'Mail OAuth Provider (Gmail/Outlook)'

    name = fields.Char(required=True)
    provider_type = fields.Selection([
        ('google', 'Google (Gmail)'),
        ('microsoft', 'Microsoft (Outlook 365)'),
    ], required=True)
    client_id = fields.Char()
    # client_secret stored via ir.config_parameter for security
    tenant_id = fields.Char(help='Microsoft tenant ID')
    scope = fields.Text(default='Mail.Read Mail.Send Calendars.ReadWrite')
    state = fields.Selection([
        ('draft', 'Not Connected'),
        ('authorized', 'Authorized'),
        ('error', 'Error'),
    ])
```

**External Services:**

| Service | Purpose | Configuration |
|---------|---------|---------------|
| Microsoft Graph API | Outlook sync | Azure App Registration |
| Gmail API | Gmail sync | GCP OAuth Client |
| CalDAV | Calendar sync | Standard protocol |

---

### 1.4 Unsplash Integration

| Property | Value |
|----------|-------|
| **IAP Setting** | Unsplash Access Key |
| **IAP Module** | `web_unsplash` |
| **Why IAP** | Proxied through Odoo.com |

**Replacement Stack:**

| Layer | Module | Role |
|-------|--------|------|
| CE | `web_unsplash` | UI components (reuse) |
| IPAI | `ipai_enterprise_bridge` | Direct Unsplash API key |

**Configuration:**

```python
# res_config_settings.py
ipai_unsplash_access_key = fields.Char(
    string="Unsplash Access Key",
    config_parameter="ipai_bridge.unsplash_access_key",
    help="Direct Unsplash API key (bypass IAP)",
)
ipai_unsplash_app_id = fields.Char(
    string="Unsplash App ID",
    config_parameter="ipai_bridge.unsplash_app_id",
)
```

**Patch Required:**

```python
# controllers/main.py - patch web_unsplash to use direct key
from odoo.addons.web_unsplash.controllers.main import WebUnsplash

def _get_unsplash_access_key(self):
    """Override to use direct API key instead of IAP"""
    return self.env['ir.config_parameter'].sudo().get_param(
        'ipai_bridge.unsplash_access_key', ''
    )

WebUnsplash._get_unsplash_access_key = _get_unsplash_access_key
```

---

### 1.5 Geolocation (Geocoding)

| Property | Value |
|----------|-------|
| **IAP Setting** | Geocoding Provider |
| **IAP Module** | `base_geolocalize` (IAP mode) |
| **Why IAP** | Uses Odoo geocoding proxy |

**Replacement Stack:**

| Layer | Module | Role |
|-------|--------|------|
| CE | `base_geolocalize` | Core geocoding models |
| OCA | `base_geolocalize_openstreetmap` | OSM Nominatim provider |
| IPAI | `ipai_enterprise_bridge` | Fallback to Google with direct key |

**Configuration:**

```xml
<!-- data/geolocalize_config.xml -->
<record id="param_geocode_provider" model="ir.config_parameter">
    <field name="key">base_geolocalize.provider</field>
    <field name="value">openstreetmap</field>
</record>

<!-- For Google fallback (optional) -->
<record id="param_google_maps_key" model="ir.config_parameter">
    <field name="key">base_geolocalize.google_maps_api_key</field>
    <field name="value">__GOOGLE_MAPS_API_KEY__</field>
</record>
```

---

### 1.6 Google Translate

| Property | Value |
|----------|-------|
| **IAP Setting** | Translation Provider |
| **IAP Module** | `website_translate` |
| **Why IAP** | Proxied Google Translate |

**Replacement Stack:**

| Layer | Module | Role |
|-------|--------|------|
| IPAI | `ipai_enterprise_bridge` | LibreTranslate or direct Google API |

**External Services:**

| Service | Purpose | Self-Hosted |
|---------|---------|-------------|
| LibreTranslate | Open-source translation | ✓ Docker image |
| Google Translate API | Paid translation | Direct billing |
| DeepL API | Alternative translation | Direct billing |

**Configuration:**

```python
# res_config_settings.py
ipai_translate_provider = fields.Selection([
    ('none', 'Disabled'),
    ('libretranslate', 'LibreTranslate (Self-Hosted)'),
    ('google', 'Google Translate (Direct API)'),
    ('deepl', 'DeepL API'),
], string="Translation Provider", config_parameter="ipai_bridge.translate_provider")

ipai_translate_endpoint = fields.Char(
    string="Translation Endpoint",
    config_parameter="ipai_bridge.translate_endpoint",
    help="LibreTranslate URL or leave blank for cloud APIs",
)
ipai_translate_api_key = fields.Char(
    string="Translation API Key",
    config_parameter="ipai_bridge.translate_api_key",
)
```

---

### 1.7 Cloud Storage

| Property | Value |
|----------|-------|
| **EE Setting** | Cloud Storage (S3/Azure/GCS) |
| **EE Module** | `cloud_storage` |
| **Why EE** | Enterprise attachment offloading |

**Replacement Stack:**

| Layer | Module | Role |
|-------|--------|------|
| OCA | `attachment_s3` | S3-compatible storage |
| OCA | `attachment_azure` | Azure Blob storage |
| IPAI | `ipai_enterprise_bridge` | Unified storage settings |

**Data Model Mapping:**

```python
# Already in OCA, configure via:
# ir.config_parameter: ir_attachment.location = s3
# ir.config_parameter: s3.bucket = my-bucket
# ir.config_parameter: s3.access_key_id = AKIA...
# ir.config_parameter: s3.secret_key = ...
# ir.config_parameter: s3.endpoint_url = https://s3.amazonaws.com (or MinIO)
```

---

### 1.8 Mailjet API

| Property | Value |
|----------|-------|
| **IAP Setting** | Mailjet API Key/Secret |
| **IAP Module** | `mass_mailing_mailjet` |
| **Why IAP** | Proxied through Odoo.com |

**Replacement Stack:**

| Layer | Module | Role |
|-------|--------|------|
| CE | `mass_mailing` | Core mass mailing |
| IPAI | `ipai_mail_integration` | Direct Mailjet/Mailgun/SES |

**Configuration:**

```python
# Direct SMTP approach (recommended)
# ir.mail_server with Mailjet SMTP credentials

# Or API approach via ipai_mail_integration
ipai_mass_mailing_provider = fields.Selection([
    ('smtp', 'SMTP (Any Provider)'),
    ('mailgun', 'Mailgun API'),
    ('ses', 'AWS SES API'),
    ('sendgrid', 'SendGrid API'),
], config_parameter="ipai_bridge.mass_mailing_provider")
```

---

## 2. Module Replacements

### 2.1 Full EE Module Mapping

| EE Module | Description | OCA Replacement | IPAI Module | Parity |
|-----------|-------------|-----------------|-------------|--------|
| `accountant` | Accountant dashboard | `account_financial_report`, `mis_builder` | - | 95% |
| `appointment` | Online scheduling | `calendar_ics` | `ipai_booking` | 60% |
| `cloud_storage` | S3/Azure attachments | `attachment_s3`, `attachment_azure` | - | 100% |
| `data_recycle` | Data cleanup | `auto_backup`, `database_cleanup` | - | 50% |
| `helpdesk` | Ticket management | `helpdesk_mgmt` | - | 85% |
| `hr_appraisal` | Performance reviews | `hr_appraisal` (OCA) | - | 85% |
| `industry_fsm` | Field service | `fieldservice`, `fieldservice_project` | - | 80% |
| `iot` | IoT integration | `base_report_to_printer` | `ipai_iot_bridge` | 70% |
| `knowledge` | Knowledge base | `knowledge` (OCA) | `ipai_workos_core` | 70% |
| `mail_plugin` | Browser extensions | `mail_tracking` | `ipai_mail_integration` | 60% |
| `marketing_automation` | Campaign automation | `mass_mailing_automation` | - | 60% |
| `marketing_card` | Business cards | - | `ipai_vcard` | 30% |
| `mrp_workorder` | Work orders | `mrp_multi_level`, `mrp_production_request` | - | 90% |
| `planning` | Resource planning | `project_timeline`, `project_task_dependency` | - | 75% |
| `pos_iot` | POS hardware | `pos_printer_network` | `ipai_iot_bridge` | 70% |
| `quality_control` | QC management | `quality_control`, `quality_control_stock` | - | 70% |
| `sale_amazon` | Amazon connector | - | n8n workflow | 40% |
| `sale_subscription` | Subscriptions | `sale_subscription` (OCA) | - | 80% |
| `sign` | e-Signatures | - | `ipai_docusign` | 50% |
| `social` | Social media | - | n8n workflows | 40% |
| `stock_barcode` | Barcode scanning | `stock_barcodes` | - | 70% |
| `timesheet_grid` | Timesheet grid | `hr_timesheet_sheet` | - | 90% |
| `voip` | VoIP integration | - | `ipai_voip` | 30% |
| `web_mobile` | Mobile app | `web_responsive` | - | 50% |
| `web_studio` | Low-code builder | - | `ipai_dev_studio_base` | 60% |

---

### 2.2 Critical Module Deep-Dives

#### 2.2.1 web_studio Replacement

**EE Capabilities:**
- Drag-and-drop view editor
- Custom field creation
- Automated actions builder
- Report designer

**IPAI Replacement:**

```python
# ipai_dev_studio_base provides:
# - Dynamic field creation via ir.model.fields wizard
# - View customization via ir.ui.view inheritance
# - Server actions builder
# - Report template editor

# Already implemented in addons/ipai/ipai_dev_studio_base/
```

**Limitations:**
- No visual drag-and-drop (code-based customization)
- Requires technical knowledge

---

#### 2.2.2 sign Replacement

**EE Capabilities:**
- In-app document signing
- PDF annotation
- Signature workflow
- Audit trail

**IPAI Replacement:**

```python
# ipai_docusign (to be created) or integrate with:
# - DocuSign API
# - HelloSign API
# - SignRequest (acquired by Box)

# Minimum viable: PDF upload + external signing link
class IpaiSignRequest(models.Model):
    _name = 'ipai.sign.request'

    document_id = fields.Many2one('ir.attachment')
    signer_ids = fields.Many2many('res.partner')
    provider = fields.Selection([
        ('docusign', 'DocuSign'),
        ('hellosign', 'HelloSign'),
    ])
    external_id = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('signed', 'Signed'),
        ('cancelled', 'Cancelled'),
    ])
```

---

#### 2.2.3 helpdesk Replacement

**EE Capabilities:**
- Ticket management
- SLA tracking
- Customer portal
- Timesheet integration

**OCA Replacement:** `helpdesk_mgmt` (OCA/helpdesk)

```bash
# Install OCA helpdesk
pip install odoo-addon-helpdesk_mgmt
odoo-bin -u helpdesk_mgmt -d odoo_core --stop-after-init
```

**Parity Notes:**
- Full ticket CRUD: ✓
- SLA tracking: ✓ (via custom fields)
- Portal: ✓
- Timesheet: ✓ (via `helpdesk_mgmt_timesheet`)

---

## 3. IAP Service Replacements

### 3.1 IAP Service Inventory

| IAP Service | EE Module | Replacement | Cost Model |
|-------------|-----------|-------------|------------|
| Mail Servers | `iap_mail` | Mailgun/SES SMTP | Per-email |
| SMS | `sms`, `iap_sms` | Twilio/Vonage | Per-SMS |
| Snailmail | `snailmail` | Lob.com API | Per-letter |
| Partner Autocomplete | `partner_autocomplete` | Clearbit/Apollo | Per-lookup |
| OCR | `iap_extract` | Mindee/Google Vision | Per-document |
| Geocoding | `base_geolocalize` (IAP) | Google Maps/OSM | Per-request |
| Translation | `website_translate` | LibreTranslate/Google | Per-character |

### 3.2 SMS Gateway Replacement

```python
# ipai_sms_gateway already exists
# addons/ipai/ipai_sms_gateway/

# Supports:
# - Twilio
# - Vonage (Nexmo)
# - AWS SNS
# - Generic HTTP gateway
```

### 3.3 OCR Gateway Replacement

```python
# ipai_ocr_gateway already exists
# addons/ipai/ipai_ocr_gateway/

# Supports:
# - Mindee (invoices, receipts)
# - Google Cloud Vision
# - AWS Textract
# - Self-hosted Tesseract (basic)
```

---

## 4. Security & ACL Considerations

### 4.1 New Security Groups

```xml
<!-- security/security.xml -->
<record id="group_ipai_iot_admin" model="res.groups">
    <field name="name">IoT Administrator</field>
    <field name="category_id" ref="base.module_category_administration"/>
</record>

<record id="group_ipai_mail_admin" model="res.groups">
    <field name="name">Mail Integration Administrator</field>
    <field name="category_id" ref="base.module_category_administration"/>
</record>

<record id="group_ipai_storage_admin" model="res.groups">
    <field name="name">Cloud Storage Administrator</field>
    <field name="category_id" ref="base.module_category_administration"/>
</record>
```

### 4.2 Access Control

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_ipai_iot_device_admin,ipai.iot.device admin,model_ipai_iot_device,group_ipai_iot_admin,1,1,1,1
access_ipai_iot_device_user,ipai.iot.device user,model_ipai_iot_device,base.group_user,1,0,0,0
access_ipai_mail_oauth_admin,ipai.mail.oauth admin,model_ipai_mail_oauth_provider,group_ipai_mail_admin,1,1,1,1
```

---

## 5. Migration Notes

### 5.1 From EE to CE+OCA+IPAI

```bash
# 1. Backup database
pg_dump odoo_ee > backup_ee.sql

# 2. Export EE-specific data
psql odoo_ee -c "COPY (SELECT * FROM iot_device) TO '/tmp/iot_devices.csv' CSV HEADER;"
psql odoo_ee -c "COPY (SELECT * FROM cloud_storage_file) TO '/tmp/cloud_files.csv' CSV HEADER;"

# 3. Install CE + OCA + IPAI stack
odoo-bin -d odoo_ce -i ipai_enterprise_bridge,ipai_iot_bridge,ipai_mail_integration

# 4. Import migrated data
python scripts/migrate_ee_to_ipai.py --source backup_ee.sql --target odoo_ce

# 5. Verify no EE modules remain
odoo-bin shell -d odoo_ce -c "print(env['ir.module.module'].search([('license','=','OEEL-1')]).mapped('name'))"
```

### 5.2 Data Migration Scripts

See `scripts/migrate/` directory for:
- `migrate_iot_devices.py`
- `migrate_cloud_storage.py`
- `migrate_mail_plugins.py`
- `migrate_sign_requests.py`

---

## 6. Verification Checklist

```bash
# Run EE/IAP independence check
./scripts/validate_ee_iap_independence.sh

# Expected output:
# [PASS] No EE modules installed
# [PASS] No IAP endpoints configured
# [PASS] Email works via Mailgun
# [PASS] IoT devices reachable
# [PASS] Cloud storage functional
# [PASS] Translation service available
```

---

*See [PROGRAMMATIC_CONFIG_PLAN.md](./PROGRAMMATIC_CONFIG_PLAN.md) for implementation artifacts*
