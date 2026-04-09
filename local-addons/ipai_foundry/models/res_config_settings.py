from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ipai_foundry_endpoint = fields.Char(string="Foundry Endpoint", config_parameter='ipai.foundry_endpoint')
    
    # Azure App Registration (Odoo 18.0 Pattern)
    ipai_azure_tenant_id = fields.Char(string="Azure Tenant ID", config_parameter='ipai.azure_tenant_id')
    ipai_azure_client_id = fields.Char(string="Azure Client ID", config_parameter='ipai.azure_client_id')
    ipai_azure_client_secret = fields.Char(string="Azure Client Secret", config_parameter='ipai.azure_client_secret')
    
    ipai_doc_intel_endpoint = fields.Char(string="Document Intelligence Endpoint", config_parameter='ipai.doc_intel_endpoint')
