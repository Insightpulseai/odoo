# PRD: Odoo CE Enterprise Replacement

## Overview

Replace all Odoo Enterprise Edition (EE) and IAP-backed capabilities with a fully self-hosted CE + OCA + IPAI stack.

## Problem Statement

Odoo EE features require:
- Paid Enterprise subscription
- IAP credits for email, SMS, OCR, data enrichment
- IoT Box hardware subscription
- odoo.com account dependencies

These create vendor lock-in and recurring costs that can be eliminated with open-source alternatives.

## Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    IPAI Enterprise Bridge                        │
├─────────────────────────────────────────────────────────────────┤
│  Email Layer     │  Auth Layer      │  IoT Layer    │  AI Layer │
│  ─────────────   │  ────────────    │  ──────────   │  ──────── │
│  Mailgun SMTP    │  auth_oauth      │  MQTT Bridge  │  LangChain│
│  Fetchmail       │  auth_oauth_multi│  WebSocket    │  Ollama   │
│  mail.catchall   │  Keycloak OIDC   │  Device Reg   │  OCR API  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         OCA Modules                              │
├─────────────────────────────────────────────────────────────────┤
│  server-auth     │  server-tools    │  server-ux    │  web      │
│  account-*       │  hr-*            │  project-*    │  stock-*  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      Odoo 18 CE Core                             │
└─────────────────────────────────────────────────────────────────┘
```

## Feature Mapping

### 1. General Settings Replacement

| EE/IAP Feature | CE+OCA+IPAI Replacement |
|----------------|-------------------------|
| Odoo IAP Email | Mailgun SMTP + fetchmail |
| Odoo IAP SMS | Twilio + `sms_twilio` (OCA) |
| Data Enrichment | `partner_autocomplete_address` (OCA) + custom API |
| Document Digitization | PaddleOCR + `ipai_ocr_bridge` |
| IoT Box | `ipai_iot_bridge` + MQTT |
| Inter-Company | `account_invoice_inter_company` (OCA) |

### 2. Email Configuration

**Outbound (SMTP)**:
- Mailgun API or SMTP
- `ir.mail_server` records via XML seed
- DNS: SPF, DKIM, DMARC, tracking domain

**Inbound (Fetchmail)**:
- `fetchmail_incoming_log` (OCA)
- `mail.catchall.domain` parameter
- Alias routing via `mail.alias`

**OAuth**:
- `auth_oauth` for Google
- `auth_oauth_multi_token` (OCA) for Azure AD
- `ipai_oauth_azure` for Outlook 365

### 3. Authentication

| Provider | Module | Config |
|----------|--------|--------|
| Google | `auth_oauth` (CE) | `auth.oauth.provider` record |
| Azure AD | `auth_oauth_multi_token` (OCA) | OIDC config |
| Keycloak | `auth_oidc` (OCA) | OIDC endpoint |
| LDAP | `auth_ldap` (CE) | `res.company.ldap` |

### 4. IoT Replacement

**Architecture**:
```
Device → MQTT Broker → ipai_iot_bridge → Odoo
         (Mosquitto)    (WebSocket)      (Controller)
```

**Components**:
- `ipai_iot_bridge`: Device registry, status, commands
- `ipai_iot_pos`: POS hardware (printer, scale, drawer)
- `ipai_iot_mfg`: Manufacturing equipment

### 5. Multi-Company

**Modules**:
- `base_multi_company` (OCA)
- `account_invoice_inter_company` (OCA)
- `sale_order_inter_company` (OCA)
- `ipai_multi_company_config`: Shared config sync

**Seed Structure**:
```xml
<record id="company_tbwa" model="res.company">
    <field name="name">TBWA\SMP</field>
</record>
<record id="company_ipai" model="res.company">
    <field name="name">InsightPulseAI</field>
</record>
```

## Deliverables

1. **ipai_enterprise_bridge** module
2. **Configuration seeds** (XML/CSV)
3. **CI/CD scripts** for setup
4. **DNS automation** scripts
5. **Validation test suite**
6. **Parity matrix** (EE vs CE+OCA+IPAI)

## Acceptance Criteria

- [ ] Email send test passes (Mailgun)
- [ ] Email receive test passes (Fetchmail)
- [ ] OAuth Google login works
- [ ] OAuth Azure AD login works
- [ ] IoT device registration works
- [ ] Multi-company invoice works
- [ ] All config applied via CI (no manual UI steps)
- [ ] Zero EE modules in production DB
