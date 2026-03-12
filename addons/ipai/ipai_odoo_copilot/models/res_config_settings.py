import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# ir.config_parameter keys — non-secret config only
_PARAM_PREFIX = "ipai_odoo_copilot"
_PARAMS = {
    "foundry_enabled": f"{_PARAM_PREFIX}.foundry_enabled",
    "foundry_endpoint": f"{_PARAM_PREFIX}.foundry_endpoint",
    "foundry_project": f"{_PARAM_PREFIX}.foundry_project",
    "foundry_agent_name": f"{_PARAM_PREFIX}.foundry_agent_name",
    "foundry_model": f"{_PARAM_PREFIX}.foundry_model",
    "search_connection": f"{_PARAM_PREFIX}.search_connection",
    "search_index": f"{_PARAM_PREFIX}.search_index",
    "memory_enabled": f"{_PARAM_PREFIX}.memory_enabled",
    "readonly_mode": f"{_PARAM_PREFIX}.readonly_mode",
    "draft_only_mode": f"{_PARAM_PREFIX}.draft_only_mode",
}


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # --- Azure Foundry Copilot settings ---

    ipai_copilot_foundry_enabled = fields.Boolean(
        string="Enable Azure Foundry Copilot",
        config_parameter=_PARAMS["foundry_enabled"],
        default=False,
    )
    ipai_copilot_foundry_endpoint = fields.Char(
        string="Foundry Endpoint",
        config_parameter=_PARAMS["foundry_endpoint"],
        help="Azure Foundry endpoint URL. Secrets must not be stored here.",
    )
    ipai_copilot_foundry_project = fields.Char(
        string="Foundry Project",
        config_parameter=_PARAMS["foundry_project"],
        default="data-intel-ph",
    )
    ipai_copilot_foundry_agent_name = fields.Char(
        string="Foundry Agent Name",
        config_parameter=_PARAMS["foundry_agent_name"],
        default="ipai-odoo-copilot-azure",
    )
    ipai_copilot_foundry_model = fields.Char(
        string="Model",
        config_parameter=_PARAMS["foundry_model"],
        default="gpt-4.1",
    )
    ipai_copilot_search_connection = fields.Char(
        string="Azure Search Connection",
        config_parameter=_PARAMS["search_connection"],
        help="Azure AI Search connection name for knowledge grounding.",
    )
    ipai_copilot_search_index = fields.Char(
        string="Azure Search Index",
        config_parameter=_PARAMS["search_index"],
        help="Azure AI Search index name for knowledge grounding.",
    )
    ipai_copilot_memory_enabled = fields.Boolean(
        string="Enable Foundry Memory",
        config_parameter=_PARAMS["memory_enabled"],
        default=False,
        help="Enable conversation memory in Azure Foundry. Off by default.",
    )
    ipai_copilot_readonly_mode = fields.Boolean(
        string="Read-Only Mode",
        config_parameter=_PARAMS["readonly_mode"],
        default=True,
        help="When enabled, copilot operates in read-only mode (no writes).",
    )
    ipai_copilot_draft_only_mode = fields.Boolean(
        string="Draft-Only Mode",
        config_parameter=_PARAMS["draft_only_mode"],
        default=True,
        help="When enabled, copilot generates drafts only (no direct publishing).",
    )

    # --- Actions ---

    def action_test_foundry_connection(self):
        """Validate Foundry config shape and report bounded status."""
        self.ensure_one()
        service = self.env["ipai.foundry.service"]
        result = service.test_connection()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Foundry Connection Test",
                "message": result.get("message", "Unknown result"),
                "type": result.get("status", "warning"),
                "sticky": False,
            },
        }

    def action_ensure_foundry_agent(self):
        """Bounded sync stub — logs intent, does not create resources."""
        self.ensure_one()
        service = self.env["ipai.foundry.service"]
        result = service.ensure_agent()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Foundry Agent Sync",
                "message": result.get("message", "Unknown result"),
                "type": result.get("status", "info"),
                "sticky": False,
            },
        }

    def action_open_foundry_portal(self):
        """Open Azure Foundry portal for the configured project."""
        self.ensure_one()
        icp = self.env["ir.config_parameter"].sudo()
        project = icp.get_param(
            _PARAMS["foundry_project"], "data-intel-ph"
        )
        # Assumption: Azure AI Foundry portal URL pattern
        url = f"https://ai.azure.com/project/{project}"
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
