{
    'name': 'IPAI Mailgun API',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Mailgun HTTP API integration to bypass SMTP port blocking',
    'description': """
        Mailgun HTTP API Email Integration
        ===================================

        Replaces SMTP-based email sending with Mailgun HTTP API to bypass
        DigitalOcean's outbound SMTP port blocking (ports 25/587/465).

        Features:
        ---------
        * HTTP API email sending (uses port 443)
        * Configurable via system parameters
        * Fallback to standard SMTP if API key not configured
        * Better monitoring and logging than SMTP
        * Compatible with all Odoo email workflows

        Configuration:
        --------------
        Set these system parameters in Settings > Technical > Parameters > System Parameters:

        * mailgun.api_key - Your Mailgun API key
        * mailgun.domain - Your Mailgun domain (default: mg.insightpulseai.net)
        * mailgun.use_api - Enable API mode (default: True)
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'data/system_parameters.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
