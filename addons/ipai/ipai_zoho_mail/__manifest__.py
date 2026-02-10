# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'IPAI Zoho Mail Integration',
    'summary': 'Zoho Mail SMTP/IMAP configuration for insightpulseai.com',
    'description': """
IPAI Zoho Mail Integration
==========================

This module configures Odoo email settings for production use with Zoho Mail.

Features:
---------
* Outgoing SMTP server (smtp.zoho.com:587 STARTTLS)
* Incoming IMAP server (imap.zoho.com:993 SSL)
* System parameters for catchall domain and base URL
* Email aliases for sales, support, accounting

Configuration:
--------------
Before installing, ensure these environment variables are set:
* ZOHO_SMTP_PASSWORD - App password for noreply@insightpulseai.com
* ZOHO_IMAP_PASSWORD - App password for catchall@insightpulseai.com

DNS Requirements:
-----------------
* MX records pointing to mx.zoho.com, mx2.zoho.com, mx3.zoho.com
* SPF TXT record: v=spf1 include:zohomail.com ~all
* DKIM TXT record (configured in Zoho admin)
* DMARC TXT record for monitoring

Post-Installation:
------------------
1. Go to Settings → Technical → Email → Outgoing Mail Servers
2. Edit "Zoho SMTP (Prod)" and enter the SMTP password
3. Click "Test Connection" to verify
4. Go to Settings → Technical → Email → Incoming Mail Servers
5. Edit "Zoho IMAP (Prod)" and enter the IMAP password
6. Click "Fetch Mail" to verify
    """,
    'version': '19.0.1.0.0',
    'category': 'Mail',
    'author': 'InsightPulseAI',
    'website': 'https://insightpulseai.com',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'fetchmail',
    ],
    'data': [
        'data/config_params.xml',
        'data/mail_server.xml',
        'data/fetchmail_server.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
