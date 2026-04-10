from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_knowledge_search_endpoint = fields.Char(
        string="Azure AI Search Endpoint",
        config_parameter="ipai_knowledge.azure_search_endpoint",
    )
    ipai_knowledge_openai_endpoint = fields.Char(
        string="Azure OpenAI Endpoint",
        config_parameter="ipai_knowledge.azure_openai_endpoint",
    )
    ipai_knowledge_openai_deployment = fields.Char(
        string="Azure OpenAI Deployment",
        config_parameter="ipai_knowledge.azure_openai_deployment",
    )
    ipai_knowledge_default_confidence = fields.Float(
        string="Default Confidence Threshold",
        config_parameter="ipai_knowledge.default_confidence_threshold",
        default=0.70,
    )
