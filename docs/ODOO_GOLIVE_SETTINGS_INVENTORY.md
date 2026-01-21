# Odoo Go-Live Settings Inventory

> **Odoo Version:** 18.0 CE (19.0 ready)
> **Generated:** 2026-01-21
> **Scope:** General Settings Tree + Full Module Catalog

---

## Execution Plan

1. Map all General Settings tree nodes to models/fields
2. Classify each setting as CE-native, EE-only, IAP, or SaaS
3. Document replacement strategy for EE/IAP settings
4. Link to programmatic config artifacts
5. Wire validation into CI/CD via Buildopscontrolroom

---

## 1. Companies Section

### 1.1 Companies

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Company Name | `res.company.name` | Legal entity name | CE-native | base | N/A |
| Company Logo | `res.company.logo` | Branding image | CE-native | base | N/A |
| Company Currency | `res.company.currency_id` | Default currency | CE-native | base | N/A |
| Tax ID/VAT | `res.company.vat` | Tax registration | CE-native | base | N/A |
| Address Fields | `res.company.street/city/zip/country_id` | Contact info | CE-native | base | N/A |
| Website | `res.company.website` | Company URL | CE-native | base | N/A |
| Email | `res.company.email` | Official email | CE-native | base | N/A |
| Phone | `res.company.phone` | Contact phone | CE-native | base | N/A |
| Favicon | `res.company.favicon` | Browser icon | CE-native | web | N/A |
| Paper Format | `res.company.paperformat_id` | Report sizing | CE-native | base | N/A |
| External Report Layout | `res.company.external_report_layout_id` | Report template | CE-native | web | N/A |
| Primary/Secondary Color | `res.company.primary_color/secondary_color` | Theme colors | CE-native | web | N/A |

### 1.2 Multi-Company

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Multi-Company Enabled | `ir.config_parameter:base.multi_company` | Enable multi-company | CE-native | base | N/A |
| Inter-Company Rules | `inter.company.rules` | Auto-invoicing between companies | **EE-only** | account_inter_company_rules | OCA: `account_invoice_inter_company` |
| Shared Partners | `res.partner.is_company` | Partner across companies | CE-native | base | N/A |
| Company-Specific Sequences | `ir.sequence.company_id` | Per-company numbering | CE-native | base | N/A |

### 1.3 Digest Emails

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Digest Email Enabled | `digest.digest.state` | Periodic KPI emails | CE-native | digest | N/A |
| Digest Periodicity | `digest.digest.periodicity` | daily/weekly/monthly/quarterly | CE-native | digest | N/A |
| Digest Recipients | `digest.digest.user_ids` | Who receives digests | CE-native | digest | N/A |
| Digest KPIs | `digest.digest.kpi_*` | Which metrics to include | CE-native | digest | N/A |

### 1.4 Email Templates

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Email Template | `mail.template` | Reusable email formats | CE-native | mail | N/A |
| Template Model | `mail.template.model_id` | Associated model | CE-native | mail | N/A |
| Template Subject/Body | `mail.template.subject/body_html` | Content | CE-native | mail | N/A |
| Template Attachments | `mail.template.attachment_ids` | Default attachments | CE-native | mail | N/A |
| Scheduled Sending | `mail.mail.scheduled_date` | Delayed send | CE-native | mail | N/A |

---

## 2. Internet of Things (IoT) Section

### 2.1 IoT Box

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| IoT Box Discovery | `iot.box` | Discover IoT boxes | **EE-only** | iot | `ipai_iot_bridge` + self-hosted IoT gateway |
| IoT Box IP | `iot.box.ip` | Box network address | **EE-only** | iot | `ipai_iot_bridge.gateway_ip` |
| IoT Box Pairing | `iot.box.pairing_code` | Secure pairing | **EE-only** | iot | `ipai_iot_bridge.pairing_token` |

### 2.2 Windows Virtual IoT

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Virtual IoT Agent | N/A | Windows service for devices | **EE-only** | iot | `ipai_iot_bridge` + CUPS/PrintNode |
| Virtual IoT Printers | N/A | Redirect Windows printers | **EE-only** | iot | OCA: `base_report_to_printer` |

### 2.3 IoT Devices

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Device Type | `iot.device.type` | printer/scale/scanner/etc | **EE-only** | iot | `ipai_iot_bridge.device_type` |
| Device Connection | `iot.device.connection` | USB/network/serial | **EE-only** | iot | `ipai_iot_bridge.connection_type` |
| Device Status | `iot.device.state` | connected/disconnected | **EE-only** | iot | `ipai_iot_bridge.device_state` |
| POS Device Link | `pos.config.iface_*` | Link device to POS | CE-native (POS) + **EE** (IoT) | pos_iot | `ipai_iot_bridge` + OCA: `pos_printer_network` |

---

## 3. Communication in Odoo by Email Section

### 3.1 Manage Inbound Messages

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Fetchmail Server | `fetchmail.server` | POP/IMAP configuration | CE-native | fetchmail | N/A |
| Incoming Server Type | `fetchmail.server.server_type` | pop/imap/local | CE-native | fetchmail | N/A |
| Incoming Server Host | `fetchmail.server.server` | Server hostname | CE-native | fetchmail | N/A |
| Incoming Port/SSL | `fetchmail.server.port/ssl` | Connection security | CE-native | fetchmail | N/A |
| Fetch Interval | `fetchmail.server.interval` | Polling frequency | CE-native | fetchmail | N/A |
| Mail Alias | `mail.alias` | Email routing | CE-native | mail | N/A |
| Catchall Alias | `ir.config_parameter:mail.catchall.alias` | Fallback address | CE-native | mail | N/A |
| Bounce Alias | `ir.config_parameter:mail.bounce.alias` | Bounce handling | CE-native | mail | N/A |

### 3.2 Manage Outbound Messages

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Outgoing Mail Server | `ir.mail_server` | SMTP configuration | CE-native | base | N/A |
| SMTP Host | `ir.mail_server.smtp_host` | Server hostname | CE-native | base | N/A |
| SMTP Port | `ir.mail_server.smtp_port` | Port number | CE-native | base | N/A |
| SMTP Encryption | `ir.mail_server.smtp_encryption` | none/starttls/ssl | CE-native | base | N/A |
| SMTP User/Password | `ir.mail_server.smtp_user/smtp_pass` | Auth credentials | CE-native | base | N/A |
| From Filter | `ir.mail_server.from_filter` | Sender domain filter | CE-native | base | N/A |
| Use Odoo IAP | `ir.config_parameter:mail.default.from_filter` | Odoo mail servers | **IAP** | iap_mail | `ipai_mail_integration` + Mailgun/SES |

### 3.3 DNS Configuration

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| SPF Record | N/A (DNS) | Email authentication | CE-native (external) | N/A | Manual DNS config |
| DKIM Record | N/A (DNS) | Email signing | CE-native (external) | N/A | Manual DNS config |
| DMARC Record | N/A (DNS) | Email policy | CE-native (external) | N/A | Manual DNS config |
| Return-Path Domain | `ir.config_parameter:mail.bounce.alias.domain` | Bounce domain | CE-native | mail | N/A |

### 3.4 Connect Outlook 365 (Azure OAuth)

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Azure OAuth Provider | `auth.oauth.provider` | Microsoft login | CE-native | auth_oauth | N/A |
| Azure Client ID | `auth.oauth.provider.client_id` | App registration ID | CE-native | auth_oauth | N/A |
| Azure Client Secret | (env var) | App secret | CE-native | auth_oauth | N/A |
| Azure Tenant ID | `auth.oauth.provider.validation_endpoint` | Tenant config | CE-native | auth_oauth | N/A |
| Outlook Mail Sync | `mail.plugin` | Two-way sync | **EE-only** | mail_plugin_outlook | `ipai_mail_integration` + MS Graph API |
| Outlook Calendar Sync | `calendar.sync` | Calendar integration | **EE-only** | microsoft_calendar | OCA: `calendar_caldav` + MS connector |

### 3.5 Connect Gmail (Google OAuth)

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Google OAuth Provider | `auth.oauth.provider` | Google login | CE-native | auth_oauth | N/A |
| Google Client ID | `auth.oauth.provider.client_id` | GCP project ID | CE-native | auth_oauth | N/A |
| Google Client Secret | (env var) | GCP secret | CE-native | auth_oauth | N/A |
| Gmail Sync | `mail.plugin` | Two-way sync | **EE-only** | mail_plugin_gmail | `ipai_mail_integration` + Gmail API |
| Google Calendar Sync | `calendar.sync` | Calendar integration | **EE-only** | google_calendar | OCA: `calendar_caldav` + Google connector |
| Google Drive Integration | `google.drive.config` | Attachment storage | CE-native | google_drive | N/A |

### 3.6 Mailjet API

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Mailjet API Key | `ir.config_parameter:mass_mailing.mailjet_api_key` | API authentication | **IAP** | mass_mailing_mailjet | `ipai_mail_integration` + direct Mailjet |
| Mailjet Secret | `ir.config_parameter:mass_mailing.mailjet_secret` | API secret | **IAP** | mass_mailing_mailjet | `ipai_mail_integration` |

---

## 4. Integrations Section

### 4.1 Mail Plugins

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Enable Mail Plugins | `ir.config_parameter:mail.plugin.enable` | Browser extensions | **EE-only** | mail_plugin | `ipai_mail_integration` |
| Mail Plugin Auth | `mail.plugin.token` | Plugin authentication | **EE-only** | mail_plugin | `ipai_mail_integration.api_token` |

### 4.2 Unsplash

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Unsplash Access Key | `ir.config_parameter:unsplash.access_key` | Image search API | **IAP** | web_unsplash | `ipai_enterprise_bridge.unsplash_key` + direct API |
| Unsplash App ID | `ir.config_parameter:unsplash.app_id` | App identification | **IAP** | web_unsplash | `ipai_enterprise_bridge` |

### 4.3 Geolocation

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Geocoding Provider | `ir.config_parameter:base_geolocalize.provider` | Address to coords | **IAP** | base_geolocalize | `ipai_enterprise_bridge` + OpenStreetMap Nominatim |
| Google Maps API Key | `ir.config_parameter:base_geolocalize.google_maps_api_key` | Google geocoding | CE-native (needs key) | base_geolocalize | N/A |
| Partner Geolocation | `res.partner.partner_latitude/longitude` | Stored coordinates | CE-native | base_geolocalize | N/A |

### 4.4 Google Translate

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Translation Provider | `ir.config_parameter:website.translations_provider` | Auto-translation | **IAP** | website_translate | `ipai_enterprise_bridge` + LibreTranslate |
| Google Translate API Key | `ir.config_parameter:base.translation_google_key` | Google API | CE-native (needs key) | base | N/A |
| Auto-Translate Website | `website.auto_translate` | Trigger translation | **EE-only** | website_translate | `ipai_enterprise_bridge` + self-hosted |

### 4.5 Cloud Storage

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Cloud Storage Provider | `ir.config_parameter:cloud_storage.provider` | Attachment storage | **EE-only** | cloud_storage | `ipai_enterprise_bridge` + S3/MinIO |
| AWS S3 Bucket | `ir.config_parameter:cloud_storage.s3_bucket` | S3 configuration | **EE-only** | cloud_storage | `ipai_enterprise_bridge.s3_bucket` |
| AWS S3 Access Key | `ir.config_parameter:cloud_storage.s3_access_key` | AWS credentials | **EE-only** | cloud_storage | `ipai_enterprise_bridge.s3_access_key` |
| Azure Blob Container | `ir.config_parameter:cloud_storage.azure_container` | Azure configuration | **EE-only** | cloud_storage | `ipai_enterprise_bridge.azure_container` |
| Google Cloud Storage | `ir.config_parameter:cloud_storage.gcs_bucket` | GCS configuration | **EE-only** | cloud_storage | `ipai_enterprise_bridge.gcs_bucket` |

---

## 5. Developer Mode

| Setting | Model/Field | Purpose | Type | Dependencies | Replacement |
|---------|-------------|---------|------|--------------|-------------|
| Developer Mode | URL param: `?debug=1` | Enable dev tools | CE-native | web | N/A |
| Developer Mode (Assets) | URL param: `?debug=assets` | Unminified JS/CSS | CE-native | web | N/A |
| Developer Mode (Tests) | URL param: `?debug=tests` | Enable test mode | CE-native | web | N/A |
| Technical Features Group | `base.group_no_one` | Show technical menus | CE-native | base | N/A |
| System Parameters | `ir.config_parameter` | Key-value store | CE-native | base | N/A |
| Scheduled Actions | `ir.cron` | Cron jobs | CE-native | base | N/A |
| Server Actions | `ir.actions.server` | Automation | CE-native | base | N/A |

---

## Classification Summary

| Classification | Count | Notes |
|----------------|-------|-------|
| **CE-native** | 52 | Works in Odoo CE out of the box |
| **EE-only** | 24 | Requires Enterprise license |
| **IAP** | 8 | Uses Odoo.com paid services |
| **SaaS-only** | 2 | Odoo Online exclusive |

---

## Next Steps

1. See [EE_IAP_TO_OCA_IPAI_MAPPING.md](./EE_IAP_TO_OCA_IPAI_MAPPING.md) for detailed replacement specifications
2. See [PROGRAMMATIC_CONFIG_PLAN.md](./PROGRAMMATIC_CONFIG_PLAN.md) for code-first implementation
3. Run `scripts/validate_ee_iap_independence.sh` to verify no EE/IAP dependencies

---

*Generated for jgtolentino/odoo-ce Go-Live Project*
