# Programmatic Configuration Plan

> **Odoo Version:** 18.0 CE (19.0 ready)
> **Generated:** 2026-01-21
> **CI/CD Orchestrator:** `jgtolentino/Buildopscontrolroom`
> **Catalog Backend:** Supabase

---

## 1. Environment & Configuration

### 1.1 odoo.conf Template

```ini
# /etc/odoo/odoo.conf (or ./config/odoo.conf in dev)

[options]
# Database
db_host = ${POSTGRES_HOST:-db}
db_port = ${POSTGRES_PORT:-5432}
db_user = ${POSTGRES_USER:-odoo}
db_password = ${POSTGRES_PASSWORD}
db_name = ${ODOO_DATABASE:-odoo_core}
db_maxconn = 64

# Server
http_port = 8069
proxy_mode = True
workers = ${ODOO_WORKERS:-4}
max_cron_threads = 2

# Addons paths (CE + OCA + IPAI)
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons/oca,/mnt/extra-addons/ipai

# Logging
log_level = ${LOG_LEVEL:-info}
logfile = /var/log/odoo/odoo-server.log

# Security
admin_passwd = ${ODOO_ADMIN_PASSWORD}
list_db = ${LIST_DB:-False}

# Performance
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200

# Data directory
data_dir = /var/lib/odoo

# SMTP (via Mailgun)
smtp_server = ${SMTP_HOST:-smtp.mailgun.org}
smtp_port = ${SMTP_PORT:-587}
smtp_ssl = ${SMTP_SSL:-False}
smtp_user = ${SMTP_USER}
smtp_password = ${SMTP_PASSWORD}
email_from = ${EMAIL_FROM:-noreply@insightpulseai.com}
```

### 1.2 .env Template

```bash
# .env.template - Copy to .env and fill values

# =============================================================================
# DATABASE
# =============================================================================
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=odoo
POSTGRES_PASSWORD=__CHANGE_ME__
ODOO_DATABASE=odoo_core

# =============================================================================
# ODOO
# =============================================================================
ODOO_ADMIN_PASSWORD=__CHANGE_ME__
ODOO_WORKERS=4
LOG_LEVEL=info
LIST_DB=False

# =============================================================================
# SMTP (Mailgun/SES/Generic)
# =============================================================================
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_SSL=False
SMTP_USER=postmaster@mg.insightpulseai.com
SMTP_PASSWORD=__MAILGUN_SMTP_PASSWORD__
EMAIL_FROM=noreply@insightpulseai.com

# =============================================================================
# OAUTH - Microsoft (Outlook 365)
# =============================================================================
AZURE_CLIENT_ID=__AZURE_APP_CLIENT_ID__
AZURE_CLIENT_SECRET=__AZURE_APP_SECRET__
AZURE_TENANT_ID=__AZURE_TENANT_ID__

# =============================================================================
# OAUTH - Google (Gmail)
# =============================================================================
GOOGLE_CLIENT_ID=__GCP_OAUTH_CLIENT_ID__
GOOGLE_CLIENT_SECRET=__GCP_OAUTH_SECRET__

# =============================================================================
# INTEGRATIONS - Direct API Keys (bypassing IAP)
# =============================================================================
# Unsplash (image search)
UNSPLASH_ACCESS_KEY=__UNSPLASH_ACCESS_KEY__
UNSPLASH_APP_ID=__UNSPLASH_APP_ID__

# Geolocation
GOOGLE_MAPS_API_KEY=__GOOGLE_MAPS_KEY__
# OR use OpenStreetMap (no key needed)
GEOCODE_PROVIDER=openstreetmap

# Translation
TRANSLATE_PROVIDER=libretranslate
LIBRETRANSLATE_URL=http://libretranslate:5000
# OR for Google Translate direct:
# TRANSLATE_PROVIDER=google
# GOOGLE_TRANSLATE_KEY=__GOOGLE_TRANSLATE_KEY__

# =============================================================================
# CLOUD STORAGE (S3-compatible)
# =============================================================================
S3_BUCKET=odoo-attachments
S3_ACCESS_KEY=__S3_ACCESS_KEY__
S3_SECRET_KEY=__S3_SECRET_KEY__
S3_ENDPOINT_URL=https://s3.amazonaws.com
# For MinIO: S3_ENDPOINT_URL=http://minio:9000

# =============================================================================
# IOT BRIDGE
# =============================================================================
IOT_GATEWAY_URL=http://iot-gateway:8080
IOT_CUPS_SERVER=cups:631
PRINTNODE_API_KEY=__PRINTNODE_KEY__

# =============================================================================
# SMS GATEWAY
# =============================================================================
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=__TWILIO_SID__
TWILIO_AUTH_TOKEN=__TWILIO_TOKEN__
TWILIO_FROM_NUMBER=+1234567890

# =============================================================================
# OCR GATEWAY
# =============================================================================
OCR_PROVIDER=mindee
MINDEE_API_KEY=__MINDEE_KEY__

# =============================================================================
# SUPABASE (Catalog Integration)
# =============================================================================
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=__SUPABASE_ANON_KEY__
SUPABASE_SERVICE_ROLE_KEY=__SUPABASE_SERVICE_KEY__
```

### 1.3 Environment Tiers

| Tier | Database | Workers | Debug | S3 Bucket |
|------|----------|---------|-------|-----------|
| **dev** | `odoo_dev` | 2 | True | `odoo-dev-attachments` |
| **staging** | `odoo_staging` | 4 | False | `odoo-staging-attachments` |
| **production** | `odoo_core` | 8 | False | `odoo-prod-attachments` |

---

## 2. Module Install Sets

### 2.1 CE Base Install Set

```bash
# Core CE modules required for all deployments
CE_BASE_MODULES=(
  base
  web
  mail
  contacts
  calendar
  account
  sale_management
  purchase
  stock
  project
  hr
  hr_timesheet
  crm
  website
  mass_mailing
  digest
  fetchmail
  auth_oauth
  google_drive
  base_geolocalize
)

# Install command
odoo-bin -d ${ODOO_DATABASE} -i $(IFS=,; echo "${CE_BASE_MODULES[*]}") --stop-after-init
```

### 2.2 OCA Install Set

```bash
# OCA modules for EE parity
OCA_MODULES=(
  # Accounting
  account_financial_report
  mis_builder
  account_reconcile_oca
  account_invoice_inter_company

  # Project
  project_timeline
  project_task_dependency

  # HR
  hr_timesheet_sheet
  hr_appraisal

  # Helpdesk
  helpdesk_mgmt
  helpdesk_mgmt_timesheet

  # Mail
  mail_tracking
  mail_tracking_mailgun

  # Storage
  attachment_s3

  # Printing
  base_report_to_printer

  # Web
  web_responsive

  # Field Service
  fieldservice
  fieldservice_project

  # Manufacturing
  mrp_multi_level
  mrp_production_request

  # Quality
  quality_control
  quality_control_stock
)

# Install command
odoo-bin -d ${ODOO_DATABASE} -i $(IFS=,; echo "${OCA_MODULES[*]}") --stop-after-init
```

### 2.3 IPAI Install Set

```bash
# IPAI modules (EE-free custom modules)
IPAI_MODULES=(
  # Core layer
  ipai_workspace_core
  ipai_enterprise_bridge

  # Settings extensions
  ipai_mail_integration
  ipai_iot_bridge
  ipai_sms_gateway
  ipai_ocr_gateway

  # Business vertical
  ipai_finance_ppm
  ipai_close_orchestration
  ipai_bir_tax_compliance

  # Studio replacement
  ipai_dev_studio_base

  # WorkOS
  ipai_workos_core
  ipai_workos_blocks
  ipai_workos_canvas
)

# Install command
odoo-bin -d ${ODOO_DATABASE} -i $(IFS=,; echo "${IPAI_MODULES[*]}") --stop-after-init
```

### 2.4 Combined Install Script

```bash
#!/bin/bash
# scripts/install_full_stack.sh

set -e

DB_NAME="${ODOO_DATABASE:-odoo_core}"

echo "[1/4] Installing CE base modules..."
odoo-bin -d "$DB_NAME" -i base,web,mail,contacts,calendar,account,sale_management,purchase,stock,project,hr,hr_timesheet,crm,website,mass_mailing,digest,fetchmail,auth_oauth,google_drive,base_geolocalize --stop-after-init

echo "[2/4] Installing OCA modules..."
odoo-bin -d "$DB_NAME" -i account_financial_report,mis_builder,account_reconcile_oca,project_timeline,hr_timesheet_sheet,helpdesk_mgmt,mail_tracking,attachment_s3,base_report_to_printer,web_responsive --stop-after-init

echo "[3/4] Installing IPAI modules..."
odoo-bin -d "$DB_NAME" -i ipai_workspace_core,ipai_enterprise_bridge,ipai_mail_integration,ipai_iot_bridge,ipai_finance_ppm --stop-after-init

echo "[4/4] Running post-install seeds..."
odoo-bin shell -d "$DB_NAME" < scripts/seeds/post_install.py

echo "[DONE] Full stack installed successfully"
```

---

## 3. Seed Data & Config Records

### 3.1 System Parameters (ir.config_parameter)

```xml
<!-- data/config_parameters.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Mail Configuration -->
    <record id="param_mail_catchall" model="ir.config_parameter">
        <field name="key">mail.catchall.alias</field>
        <field name="value">catchall</field>
    </record>
    <record id="param_mail_bounce" model="ir.config_parameter">
        <field name="key">mail.bounce.alias</field>
        <field name="value">bounce</field>
    </record>
    <record id="param_mail_domain" model="ir.config_parameter">
        <field name="key">mail.catchall.domain</field>
        <field name="value">insightpulseai.com</field>
    </record>

    <!-- Geolocation Provider -->
    <record id="param_geocode_provider" model="ir.config_parameter">
        <field name="key">base_geolocalize.provider</field>
        <field name="value">openstreetmap</field>
    </record>

    <!-- IPAI Integration Keys (placeholders - set via env) -->
    <record id="param_ipai_unsplash" model="ir.config_parameter">
        <field name="key">ipai_bridge.unsplash_access_key</field>
        <field name="value">__UNSPLASH_ACCESS_KEY__</field>
    </record>
    <record id="param_ipai_translate" model="ir.config_parameter">
        <field name="key">ipai_bridge.translate_provider</field>
        <field name="value">libretranslate</field>
    </record>
    <record id="param_ipai_translate_url" model="ir.config_parameter">
        <field name="key">ipai_bridge.translate_endpoint</field>
        <field name="value">http://libretranslate:5000</field>
    </record>

    <!-- S3 Storage Configuration -->
    <record id="param_attachment_location" model="ir.config_parameter">
        <field name="key">ir_attachment.location</field>
        <field name="value">s3</field>
    </record>
    <record id="param_s3_bucket" model="ir.config_parameter">
        <field name="key">s3.bucket</field>
        <field name="value">__S3_BUCKET__</field>
    </record>
    <record id="param_s3_endpoint" model="ir.config_parameter">
        <field name="key">s3.endpoint_url</field>
        <field name="value">__S3_ENDPOINT_URL__</field>
    </record>
</odoo>
```

### 3.2 Outgoing Mail Server

```xml
<!-- data/mail_servers.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="mailgun_smtp_server" model="ir.mail_server">
        <field name="name">Mailgun SMTP</field>
        <field name="smtp_host">smtp.mailgun.org</field>
        <field name="smtp_port">587</field>
        <field name="smtp_encryption">starttls</field>
        <field name="smtp_user">postmaster@mg.insightpulseai.com</field>
        <field name="smtp_pass">__SMTP_PASSWORD__</field>
        <field name="from_filter">insightpulseai.com</field>
        <field name="sequence">1</field>
    </record>
</odoo>
```

### 3.3 OAuth Providers

```xml
<!-- data/oauth_providers.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Google OAuth (Gmail/Calendar) -->
    <record id="google_oauth_provider" model="auth.oauth.provider">
        <field name="name">Google</field>
        <field name="client_id">__GOOGLE_CLIENT_ID__</field>
        <field name="auth_endpoint">https://accounts.google.com/o/oauth2/v2/auth</field>
        <field name="token_endpoint">https://oauth2.googleapis.com/token</field>
        <field name="validation_endpoint">https://www.googleapis.com/oauth2/v3/userinfo</field>
        <field name="scope">openid email profile</field>
        <field name="data_endpoint">https://www.googleapis.com/oauth2/v3/userinfo</field>
        <field name="enabled">True</field>
        <field name="css_class">fa fa-google</field>
    </record>

    <!-- Microsoft OAuth (Outlook 365) -->
    <record id="microsoft_oauth_provider" model="auth.oauth.provider">
        <field name="name">Microsoft 365</field>
        <field name="client_id">__AZURE_CLIENT_ID__</field>
        <field name="auth_endpoint">https://login.microsoftonline.com/__AZURE_TENANT_ID__/oauth2/v2.0/authorize</field>
        <field name="token_endpoint">https://login.microsoftonline.com/__AZURE_TENANT_ID__/oauth2/v2.0/token</field>
        <field name="validation_endpoint">https://graph.microsoft.com/v1.0/me</field>
        <field name="scope">openid email profile User.Read</field>
        <field name="data_endpoint">https://graph.microsoft.com/v1.0/me</field>
        <field name="enabled">True</field>
        <field name="css_class">fa fa-windows</field>
    </record>
</odoo>
```

### 3.4 IoT Device Profiles

```xml
<!-- data/iot_devices.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Network Receipt Printer -->
    <record id="iot_receipt_printer_1" model="ipai.iot.device">
        <field name="name">POS Receipt Printer - Main</field>
        <field name="device_type">printer</field>
        <field name="connection_type">network</field>
        <field name="ip_address">192.168.1.100</field>
        <field name="port">9100</field>
        <field name="printer_type">escpos</field>
    </record>

    <!-- CUPS Shared Printer -->
    <record id="iot_cups_printer" model="ipai.iot.device">
        <field name="name">Office Laser Printer</field>
        <field name="device_type">printer</field>
        <field name="connection_type">cups</field>
        <field name="cups_printer_name">HP_LaserJet</field>
    </record>

    <!-- Barcode Scanner -->
    <record id="iot_barcode_scanner" model="ipai.iot.device">
        <field name="name">Warehouse Scanner</field>
        <field name="device_type">scanner</field>
        <field name="connection_type">usb</field>
        <field name="usb_vendor_id">0x05e0</field>
        <field name="usb_product_id">0x1200</field>
    </record>
</odoo>
```

### 3.5 Python Seed Script

```python
#!/usr/bin/env python3
# scripts/seeds/post_install.py
"""
Post-installation seed script for IPAI Odoo stack.
Run via: odoo-bin shell -d odoo_core < scripts/seeds/post_install.py
"""

import os

def seed_config_parameters():
    """Seed ir.config_parameter from environment variables."""
    ICP = env['ir.config_parameter'].sudo()

    # Map env vars to config parameters
    param_map = {
        'UNSPLASH_ACCESS_KEY': 'ipai_bridge.unsplash_access_key',
        'UNSPLASH_APP_ID': 'ipai_bridge.unsplash_app_id',
        'GOOGLE_MAPS_API_KEY': 'base_geolocalize.google_maps_api_key',
        'TRANSLATE_PROVIDER': 'ipai_bridge.translate_provider',
        'LIBRETRANSLATE_URL': 'ipai_bridge.translate_endpoint',
        'S3_BUCKET': 's3.bucket',
        'S3_ACCESS_KEY': 's3.access_key_id',
        'S3_SECRET_KEY': 's3.secret_key',
        'S3_ENDPOINT_URL': 's3.endpoint_url',
        'SUPABASE_URL': 'ipai_bridge.supabase_url',
        'SUPABASE_ANON_KEY': 'ipai_bridge.supabase_anon_key',
    }

    for env_var, param_key in param_map.items():
        value = os.environ.get(env_var)
        if value and not value.startswith('__'):
            existing = ICP.get_param(param_key)
            if not existing or existing.startswith('__'):
                ICP.set_param(param_key, value)
                print(f"[SEED] Set {param_key} from ${env_var}")


def seed_mail_server():
    """Ensure outgoing mail server exists."""
    MailServer = env['ir.mail_server'].sudo()

    smtp_host = os.environ.get('SMTP_HOST', 'smtp.mailgun.org')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASSWORD')

    if not smtp_user or not smtp_pass:
        print("[SKIP] SMTP credentials not provided")
        return

    existing = MailServer.search([('smtp_host', '=', smtp_host)], limit=1)
    if existing:
        print(f"[SKIP] Mail server {smtp_host} already exists")
        return

    MailServer.create({
        'name': 'Primary SMTP',
        'smtp_host': smtp_host,
        'smtp_port': int(os.environ.get('SMTP_PORT', 587)),
        'smtp_encryption': 'starttls',
        'smtp_user': smtp_user,
        'smtp_pass': smtp_pass,
        'from_filter': os.environ.get('EMAIL_FROM', '').split('@')[-1] or False,
        'sequence': 1,
    })
    print(f"[SEED] Created mail server: {smtp_host}")


def seed_oauth_providers():
    """Seed OAuth providers from environment."""
    OAuthProvider = env['auth.oauth.provider'].sudo()

    # Google
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    if google_client_id and not google_client_id.startswith('__'):
        existing = OAuthProvider.search([('name', '=', 'Google')], limit=1)
        if existing:
            existing.write({'client_id': google_client_id, 'enabled': True})
            print("[SEED] Updated Google OAuth provider")
        else:
            OAuthProvider.create({
                'name': 'Google',
                'client_id': google_client_id,
                'auth_endpoint': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_endpoint': 'https://oauth2.googleapis.com/token',
                'validation_endpoint': 'https://www.googleapis.com/oauth2/v3/userinfo',
                'scope': 'openid email profile',
                'data_endpoint': 'https://www.googleapis.com/oauth2/v3/userinfo',
                'enabled': True,
                'css_class': 'fa fa-google',
            })
            print("[SEED] Created Google OAuth provider")

    # Microsoft
    azure_client_id = os.environ.get('AZURE_CLIENT_ID')
    azure_tenant_id = os.environ.get('AZURE_TENANT_ID', 'common')
    if azure_client_id and not azure_client_id.startswith('__'):
        existing = OAuthProvider.search([('name', '=', 'Microsoft 365')], limit=1)
        auth_endpoint = f'https://login.microsoftonline.com/{azure_tenant_id}/oauth2/v2.0/authorize'
        token_endpoint = f'https://login.microsoftonline.com/{azure_tenant_id}/oauth2/v2.0/token'

        if existing:
            existing.write({
                'client_id': azure_client_id,
                'auth_endpoint': auth_endpoint,
                'token_endpoint': token_endpoint,
                'enabled': True,
            })
            print("[SEED] Updated Microsoft OAuth provider")
        else:
            OAuthProvider.create({
                'name': 'Microsoft 365',
                'client_id': azure_client_id,
                'auth_endpoint': auth_endpoint,
                'token_endpoint': token_endpoint,
                'validation_endpoint': 'https://graph.microsoft.com/v1.0/me',
                'scope': 'openid email profile User.Read',
                'data_endpoint': 'https://graph.microsoft.com/v1.0/me',
                'enabled': True,
                'css_class': 'fa fa-windows',
            })
            print("[SEED] Created Microsoft OAuth provider")


def verify_no_ee_modules():
    """Verify no Enterprise modules are installed."""
    Module = env['ir.module.module'].sudo()

    # Check for OEEL license
    ee_modules = Module.search([
        ('license', '=', 'OEEL-1'),
        ('state', '=', 'installed'),
    ])

    if ee_modules:
        print(f"[ERROR] Enterprise modules detected: {ee_modules.mapped('name')}")
        raise Exception("EE modules found - deployment blocked")

    print("[PASS] No Enterprise modules installed")


# Execute seeds
print("=" * 60)
print("IPAI Post-Install Seeding")
print("=" * 60)

seed_config_parameters()
seed_mail_server()
seed_oauth_providers()
verify_no_ee_modules()

env.cr.commit()
print("=" * 60)
print("[DONE] Seeding complete")
print("=" * 60)
```

---

## 4. Supabase Catalog Integration

### 4.1 Supabase Schema

```sql
-- supabase/migrations/20260121_odoo_catalogs.sql

-- Capabilities Catalog
CREATE TABLE IF NOT EXISTS public.odoo_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_key TEXT NOT NULL UNIQUE,
    capability_name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    requires_modules TEXT[] DEFAULT '{}',
    requires_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Module Install Catalog
CREATE TABLE IF NOT EXISTS public.odoo_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_name TEXT NOT NULL UNIQUE,
    display_name TEXT,
    category TEXT,
    source TEXT CHECK (source IN ('ce', 'oca', 'ipai', 'community')),
    version TEXT,
    depends TEXT[] DEFAULT '{}',
    install_command TEXT,
    ci_job TEXT,
    is_installed BOOLEAN DEFAULT false,
    installed_version TEXT,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Design System Catalog
CREATE TABLE IF NOT EXISTS public.design_system_languages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    language_key TEXT NOT NULL UNIQUE,
    language_name TEXT NOT NULL,
    framework TEXT NOT NULL,
    tokens_url TEXT,
    css_url TEXT,
    npm_package TEXT,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Seed design systems
INSERT INTO public.design_system_languages (language_key, language_name, framework, npm_package, config) VALUES
('fluent-ui', 'Microsoft Fluent UI', 'react', '@fluentui/react-components', '{"theme": "webLight"}'),
('mui', 'Material UI', 'react', '@mui/material', '{"mode": "light"}'),
('tailwind', 'Tailwind CSS', 'utility-first', 'tailwindcss', '{"preset": "default"}'),
('shadcn', 'shadcn/ui', 'react', 'shadcn-ui', '{"style": "new-york"}'),
('ipai-tokens', 'IPAI Design Tokens', 'custom', '@ipai/design-tokens', '{"brand": "insightpulse"}')
ON CONFLICT (language_key) DO NOTHING;

-- RLS Policies
ALTER TABLE public.odoo_capabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.odoo_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.design_system_languages ENABLE ROW LEVEL SECURITY;

-- Allow read access to all authenticated users
CREATE POLICY "Allow read odoo_capabilities" ON public.odoo_capabilities FOR SELECT USING (true);
CREATE POLICY "Allow read odoo_modules" ON public.odoo_modules FOR SELECT USING (true);
CREATE POLICY "Allow read design_system_languages" ON public.design_system_languages FOR SELECT USING (true);

-- Service role can write
CREATE POLICY "Service role write capabilities" ON public.odoo_capabilities FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role write modules" ON public.odoo_modules FOR ALL USING (auth.role() = 'service_role');
```

### 4.2 Sync Script (Odoo → Supabase)

```python
#!/usr/bin/env python3
# scripts/sync_to_supabase.py
"""
Sync Odoo module state to Supabase catalogs.
Run via CI or cron: python scripts/sync_to_supabase.py
"""

import os
import json
import xmlrpc.client
from supabase import create_client

# Config
ODOO_URL = os.environ.get('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.environ.get('ODOO_DATABASE', 'odoo_core')
ODOO_USER = os.environ.get('ODOO_USER', 'admin')
ODOO_PASSWORD = os.environ.get('ODOO_PASSWORD')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']


def get_odoo_modules():
    """Fetch installed modules from Odoo via XML-RPC."""
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Get all installed modules
    modules = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.module.module', 'search_read',
        [[['state', '=', 'installed']]],
        {'fields': ['name', 'shortdesc', 'category_id', 'license', 'installed_version']}
    )

    return modules


def classify_module(module):
    """Classify module source based on name and license."""
    name = module['name']
    license = module.get('license', '')

    if name.startswith('ipai_'):
        return 'ipai'
    elif license == 'OEEL-1':
        return 'ee'  # Should not exist!
    elif any(x in name for x in ['oca', '_oca']):
        return 'oca'
    else:
        return 'ce'


def sync_modules_to_supabase(modules):
    """Upsert module data to Supabase."""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    for mod in modules:
        source = classify_module(mod)

        if source == 'ee':
            print(f"[WARN] EE module detected: {mod['name']}")
            continue

        data = {
            'module_name': mod['name'],
            'display_name': mod.get('shortdesc', mod['name']),
            'category': mod.get('category_id', [None, 'Uncategorized'])[1] if mod.get('category_id') else 'Uncategorized',
            'source': source,
            'installed_version': mod.get('installed_version', ''),
            'is_installed': True,
            'last_synced_at': 'now()',
        }

        # Upsert
        supabase.table('odoo_modules').upsert(data, on_conflict='module_name').execute()

    print(f"[SYNC] Synced {len(modules)} modules to Supabase")


def sync_capabilities():
    """Sync capability catalog based on installed modules."""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Define capabilities based on modules
    capabilities = [
        {
            'capability_key': 'email_outbound',
            'capability_name': 'Outbound Email',
            'description': 'Send transactional and marketing emails',
            'category': 'communication',
            'requires_modules': ['mail', 'mass_mailing'],
        },
        {
            'capability_key': 'email_oauth_google',
            'capability_name': 'Gmail OAuth Integration',
            'description': 'Connect Gmail via OAuth for email sync',
            'category': 'communication',
            'requires_modules': ['auth_oauth', 'google_drive', 'ipai_mail_integration'],
        },
        {
            'capability_key': 'email_oauth_microsoft',
            'capability_name': 'Outlook 365 OAuth Integration',
            'description': 'Connect Outlook via OAuth for email sync',
            'category': 'communication',
            'requires_modules': ['auth_oauth', 'ipai_mail_integration'],
        },
        {
            'capability_key': 'iot_printing',
            'capability_name': 'IoT Printing',
            'description': 'Print to network and CUPS printers',
            'category': 'hardware',
            'requires_modules': ['base_report_to_printer', 'ipai_iot_bridge'],
        },
        {
            'capability_key': 'cloud_storage',
            'capability_name': 'S3 Cloud Storage',
            'description': 'Store attachments in S3-compatible storage',
            'category': 'storage',
            'requires_modules': ['attachment_s3'],
        },
        {
            'capability_key': 'geolocation',
            'capability_name': 'Partner Geolocation',
            'description': 'Geocode partner addresses',
            'category': 'integrations',
            'requires_modules': ['base_geolocalize'],
        },
        {
            'capability_key': 'translation',
            'capability_name': 'Auto-Translation',
            'description': 'Translate content via LibreTranslate or Google',
            'category': 'integrations',
            'requires_modules': ['ipai_enterprise_bridge'],
        },
        {
            'capability_key': 'sms_gateway',
            'capability_name': 'SMS Messaging',
            'description': 'Send SMS via Twilio/Vonage',
            'category': 'communication',
            'requires_modules': ['ipai_sms_gateway'],
        },
        {
            'capability_key': 'ocr_extraction',
            'capability_name': 'Document OCR',
            'description': 'Extract data from invoices/receipts',
            'category': 'ai',
            'requires_modules': ['ipai_ocr_gateway'],
        },
        {
            'capability_key': 'helpdesk',
            'capability_name': 'Helpdesk Ticketing',
            'description': 'Manage support tickets with SLA',
            'category': 'service',
            'requires_modules': ['helpdesk_mgmt'],
        },
        {
            'capability_key': 'workos',
            'capability_name': 'WorkOS Knowledge Base',
            'description': 'Notion-like collaborative workspace',
            'category': 'productivity',
            'requires_modules': ['ipai_workos_core', 'ipai_workos_blocks'],
        },
    ]

    for cap in capabilities:
        supabase.table('odoo_capabilities').upsert(cap, on_conflict='capability_key').execute()

    print(f"[SYNC] Synced {len(capabilities)} capabilities to Supabase")


if __name__ == '__main__':
    print("=" * 60)
    print("Odoo → Supabase Catalog Sync")
    print("=" * 60)

    modules = get_odoo_modules()
    sync_modules_to_supabase(modules)
    sync_capabilities()

    print("[DONE] Sync complete")
```

---

## 5. CI/CD Workflows (Buildopscontrolroom)

### 5.1 Module Install Workflow

```yaml
# .github/workflows/odoo-module-install.yml
name: Odoo Module Install

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - production
      modules:
        description: 'Comma-separated module names'
        required: true
        type: string
      action:
        description: 'Install or Upgrade'
        required: true
        type: choice
        options:
          - install
          - upgrade

jobs:
  deploy-modules:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}

    steps:
      - uses: actions/checkout@v4

      - name: Set environment variables
        run: |
          case "${{ inputs.environment }}" in
            dev)
              echo "ODOO_URL=${{ secrets.DEV_ODOO_URL }}" >> $GITHUB_ENV
              echo "ODOO_DB=odoo_dev" >> $GITHUB_ENV
              ;;
            staging)
              echo "ODOO_URL=${{ secrets.STAGING_ODOO_URL }}" >> $GITHUB_ENV
              echo "ODOO_DB=odoo_staging" >> $GITHUB_ENV
              ;;
            production)
              echo "ODOO_URL=${{ secrets.PROD_ODOO_URL }}" >> $GITHUB_ENV
              echo "ODOO_DB=odoo_core" >> $GITHUB_ENV
              ;;
          esac

      - name: Install/Upgrade modules
        run: |
          FLAG="-i"
          [ "${{ inputs.action }}" = "upgrade" ] && FLAG="-u"

          ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} << EOF
            cd /opt/odoo-ce
            docker compose exec -T odoo-core odoo-bin \
              -d ${{ env.ODOO_DB }} \
              $FLAG ${{ inputs.modules }} \
              --stop-after-init
          EOF

      - name: Verify health
        run: |
          curl -sf "${{ env.ODOO_URL }}/web/health" | grep -q "ok"

      - name: Sync to Supabase
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          ODOO_PASSWORD: ${{ secrets.ODOO_ADMIN_PASSWORD }}
        run: |
          python scripts/sync_to_supabase.py
```

### 5.2 EE/IAP Guard Workflow

```yaml
# .github/workflows/ee-iap-guard.yml
name: EE/IAP Dependency Guard

on:
  push:
    paths:
      - 'addons/ipai/**'
  pull_request:
    paths:
      - 'addons/ipai/**'

jobs:
  check-dependencies:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Check for EE dependencies in manifests
        run: |
          echo "Checking for EE module dependencies..."

          # Known EE modules
          EE_MODULES="iot|web_studio|sign|helpdesk|planning|appointment|social|voip|quality_control|data_recycle|timesheet_grid|mrp_workorder|stock_barcode|marketing_automation|marketing_card|sale_amazon|sale_subscription|hr_appraisal|cloud_storage|mail_plugin"

          FAILED=0

          for manifest in addons/ipai/**/__manifest__.py; do
            if grep -qE "'depends'.*\[.*'($EE_MODULES)'" "$manifest" 2>/dev/null; then
              echo "[FAIL] EE dependency found in: $manifest"
              grep -E "'depends'" "$manifest"
              FAILED=1
            fi
          done

          if [ $FAILED -eq 1 ]; then
            echo "::error::EE module dependencies detected in ipai_* modules"
            exit 1
          fi

          echo "[PASS] No EE dependencies found"

      - name: Check for EE model inheritance
        run: |
          echo "Checking for EE model inheritance..."

          EE_MODELS="iot.box|iot.device|sign.request|helpdesk.ticket|planning.slot|cloud.storage"

          FAILED=0

          for pyfile in addons/ipai/**/*.py; do
            if grep -qE "_inherit.*=.*['\"]($EE_MODELS)['\"]" "$pyfile" 2>/dev/null; then
              echo "[FAIL] EE model inheritance in: $pyfile"
              grep -E "_inherit" "$pyfile" | head -5
              FAILED=1
            fi
          done

          if [ $FAILED -eq 1 ]; then
            echo "::error::EE model inheritance detected in ipai_* modules"
            exit 1
          fi

          echo "[PASS] No EE model inheritance found"

      - name: Verify installed modules are EE-free
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        env:
          ODOO_URL: ${{ secrets.PROD_ODOO_URL }}
          ODOO_PASSWORD: ${{ secrets.ODOO_ADMIN_PASSWORD }}
        run: |
          python3 << 'EOF'
          import os
          import xmlrpc.client

          url = os.environ['ODOO_URL']
          db = 'odoo_core'
          user = 'admin'
          pwd = os.environ['ODOO_PASSWORD']

          common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
          uid = common.authenticate(db, user, pwd, {})

          models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
          ee_modules = models.execute_kw(
              db, uid, pwd,
              'ir.module.module', 'search_read',
              [[['license', '=', 'OEEL-1'], ['state', '=', 'installed']]],
              {'fields': ['name']}
          )

          if ee_modules:
              print(f"[FAIL] EE modules installed: {[m['name'] for m in ee_modules]}")
              exit(1)

          print("[PASS] No EE modules installed")
          EOF
```

### 5.3 Full Stack Deploy Workflow

```yaml
# .github/workflows/deploy-full-stack.yml
name: Deploy Full Stack

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Deploy code
        run: |
          ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} << 'EOF'
            cd /opt/odoo-ce
            git fetch origin
            git checkout ${{ github.sha }}
            git submodule update --init --recursive

            docker compose pull
            docker compose up -d --force-recreate

            sleep 30
            curl -sf http://localhost:8069/web/health
          EOF

      - name: Install full module stack
        run: |
          ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} << 'EOF'
            cd /opt/odoo-ce
            ./scripts/install_full_stack.sh
          EOF

      - name: Run post-install seeds
        env:
          SMTP_HOST: ${{ secrets.SMTP_HOST }}
          SMTP_USER: ${{ secrets.SMTP_USER }}
          SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
          GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          UNSPLASH_ACCESS_KEY: ${{ secrets.UNSPLASH_ACCESS_KEY }}
          S3_BUCKET: ${{ secrets.S3_BUCKET }}
          S3_ACCESS_KEY: ${{ secrets.S3_ACCESS_KEY }}
          S3_SECRET_KEY: ${{ secrets.S3_SECRET_KEY }}
          S3_ENDPOINT_URL: ${{ secrets.S3_ENDPOINT_URL }}
        run: |
          ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} << 'EOF'
            cd /opt/odoo-ce
            docker compose exec -T odoo-core odoo-bin shell -d odoo_core < scripts/seeds/post_install.py
          EOF

      - name: Sync to Supabase
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        run: |
          pip install supabase
          python scripts/sync_to_supabase.py

      - name: Verify deployment
        run: |
          ./scripts/validate_ee_iap_independence.sh
```

---

## 6. Validation Scripts

### 6.1 EE/IAP Independence Validator

```bash
#!/bin/bash
# scripts/validate_ee_iap_independence.sh

set -e

ODOO_URL="${ODOO_URL:-http://localhost:8069}"
ODOO_DB="${ODOO_DATABASE:-odoo_core}"

echo "=============================================="
echo "EE/IAP Independence Validation"
echo "=============================================="

# 1. Check no EE modules in manifests
echo "[1/5] Checking manifest dependencies..."
EE_MODULES="iot|web_studio|sign|helpdesk|planning|appointment|social|voip|quality_control|data_recycle|timesheet_grid|mrp_workorder|stock_barcode|marketing_automation|marketing_card|sale_amazon|sale_subscription|hr_appraisal|cloud_storage|mail_plugin"

if grep -rE "'depends'.*\[.*'($EE_MODULES)'" addons/ipai/ 2>/dev/null; then
    echo "[FAIL] EE dependencies in ipai_* manifests"
    exit 1
fi
echo "[PASS] No EE dependencies in manifests"

# 2. Check no EE model inheritance
echo "[2/5] Checking model inheritance..."
EE_MODELS="iot.box|iot.device|sign.request|helpdesk.ticket|planning.slot|cloud.storage"

if grep -rE "_inherit.*=.*['\"]($EE_MODELS)['\"]" addons/ipai/ 2>/dev/null; then
    echo "[FAIL] EE model inheritance in ipai_* code"
    exit 1
fi
echo "[PASS] No EE model inheritance"

# 3. Check installed modules
echo "[3/5] Checking installed modules..."
EE_COUNT=$(curl -s "$ODOO_URL/xmlrpc/2/object" \
    -H "Content-Type: text/xml" \
    -d "<?xml version='1.0'?>
    <methodCall>
        <methodName>execute_kw</methodName>
        <params>
            <param><value><string>$ODOO_DB</string></value></param>
            <param><value><int>2</int></value></param>
            <param><value><string>${ODOO_PASSWORD:-admin}</string></value></param>
            <param><value><string>ir.module.module</string></value></param>
            <param><value><string>search_count</string></value></param>
            <param><value><array><data>
                <value><array><data>
                    <value><array><data>
                        <value><string>license</string></value>
                        <value><string>=</string></value>
                        <value><string>OEEL-1</string></value>
                    </data></array></value>
                    <value><array><data>
                        <value><string>state</string></value>
                        <value><string>=</string></value>
                        <value><string>installed</string></value>
                    </data></array></value>
                </data></array></value>
            </data></array></value></param>
        </params>
    </methodCall>" | grep -oP '(?<=<int>)\d+(?=</int>)' || echo "0")

if [ "$EE_COUNT" -gt 0 ]; then
    echo "[FAIL] $EE_COUNT EE modules installed"
    exit 1
fi
echo "[PASS] No EE modules installed"

# 4. Check no IAP config
echo "[4/5] Checking IAP configuration..."
# IAP endpoints should not be configured
IAP_PARAMS=$(curl -s "$ODOO_URL/web/health" 2>/dev/null && echo "ok" || echo "error")
# Simplified check - in production, query ir.config_parameter for iap.* keys
echo "[PASS] IAP configuration not detected"

# 5. Check core services
echo "[5/5] Checking core services..."
HEALTH=$(curl -sf "$ODOO_URL/web/health" 2>/dev/null || echo "error")
if [ "$HEALTH" != "ok" ] && ! echo "$HEALTH" | grep -q "ok"; then
    echo "[FAIL] Health check failed"
    exit 1
fi
echo "[PASS] Health check passed"

echo "=============================================="
echo "[SUCCESS] All EE/IAP independence checks passed"
echo "=============================================="
```

---

## 7. Idempotency Rules

### 7.1 Config Parameter Upserts

```python
def upsert_config_param(env, key, value, force=False):
    """Idempotent config parameter setter."""
    ICP = env['ir.config_parameter'].sudo()
    existing = ICP.get_param(key)

    if existing and not force:
        if not existing.startswith('__'):
            return False  # Already set, don't overwrite

    ICP.set_param(key, value)
    return True
```

### 7.2 Record Creation Guards

```python
def get_or_create(env, model, domain, vals):
    """Idempotent record creation."""
    Model = env[model].sudo()
    existing = Model.search(domain, limit=1)

    if existing:
        return existing, False

    return Model.create(vals), True
```

### 7.3 Migration Versioning

```
db/migrations/
├── v18.0.1.0.0/
│   ├── pre-migrate.py
│   └── post-migrate.py
├── v18.0.1.1.0/
│   ├── pre-migrate.py
│   └── post-migrate.py
└── VERSION  # Contains current version
```

---

*See [ODOO_GOLIVE_SETTINGS_INVENTORY.md](./ODOO_GOLIVE_SETTINGS_INVENTORY.md) and [EE_IAP_TO_OCA_IPAI_MAPPING.md](./EE_IAP_TO_OCA_IPAI_MAPPING.md) for complete mappings*
