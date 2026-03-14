# -*- coding: utf-8 -*-

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

PARAM_PREFIX = "ipai_odoo_copilot"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # --- Azure Foundry connection ---
    ipai_foundry_enabled = fields.Boolean(
        string="Enable Foundry Copilot",
        config_parameter=f"{PARAM_PREFIX}.foundry_enabled",
        default=False,
    )
    ipai_foundry_endpoint = fields.Char(
        string="Foundry Portal URL",
        config_parameter=f"{PARAM_PREFIX}.foundry_endpoint",
        help="Azure AI Foundry portal URL (e.g. https://ai.azure.com)",
    )
    ipai_foundry_api_endpoint = fields.Char(
        string="Foundry Project API Endpoint",
        config_parameter=f"{PARAM_PREFIX}.foundry_api_endpoint",
        default="https://data-intel-ph-resource.services.ai.azure.com"
                "/api/projects/data-intel-ph",
        help="Full Foundry project API endpoint including /api/projects/ path. "
             "Shape: https://<resource>.services.ai.azure.com/api/projects/<project>",
    )
    ipai_foundry_project = fields.Char(
        string="Foundry Project",
        config_parameter=f"{PARAM_PREFIX}.foundry_project",
        default="data-intel-ph",
        help="Azure Foundry project name",
    )
    ipai_foundry_agent_name = fields.Char(
        string="Foundry Agent Name",
        config_parameter=f"{PARAM_PREFIX}.foundry_agent_name",
        default="ipai-odoo-copilot-azure",
    )
    ipai_foundry_model = fields.Char(
        string="Model Deployment",
        config_parameter=f"{PARAM_PREFIX}.foundry_model",
        default="gpt-4.1",
        help="Model deployment name in Azure Foundry",
    )

    # --- Knowledge / Search ---
    ipai_foundry_search_connection = fields.Char(
        string="Search Connection",
        config_parameter=f"{PARAM_PREFIX}.foundry_search_connection",
        help="Azure AI Search connection name for knowledge grounding",
    )
    ipai_foundry_search_service = fields.Char(
        string="Search Service",
        config_parameter=f"{PARAM_PREFIX}.foundry_search_service",
        default="srch-ipai-dev",
        help="Azure AI Search service name",
    )
    ipai_foundry_search_index = fields.Char(
        string="Search Index",
        config_parameter=f"{PARAM_PREFIX}.foundry_search_index",
        help="Azure AI Search index name",
    )

    # --- Safety posture ---
    ipai_foundry_memory_enabled = fields.Boolean(
        string="Enable Agent Memory",
        config_parameter=f"{PARAM_PREFIX}.foundry_memory_enabled",
        default=False,
        help="Allow Foundry agent to retain conversation memory. "
             "Off by default for privacy.",
    )
    ipai_foundry_read_only_mode = fields.Boolean(
        string="Read-Only / Draft-Only Mode",
        config_parameter=f"{PARAM_PREFIX}.foundry_read_only_mode",
        default=True,
        help="When enabled, the agent cannot execute write operations. "
             "All mutations are surfaced as drafts for human approval.",
    )

    # --- Actions ---

    def action_test_foundry_connection(self):
        """Validate Foundry connectivity via real health probe."""
        service = self.env["ipai.foundry.service"]
        ok, message = service.test_connection()
        notif_type = "success" if ok else "warning"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Foundry Connection Test",
                "message": message,
                "type": notif_type,
                "sticky": False,
            },
        }

    def action_ensure_foundry_agent(self):
        """Verify the configured agent exists in Foundry (read-only)."""
        service = self.env["ipai.foundry.service"]
        ok, message = service.ensure_agent()
        notif_type = "success" if ok else "warning"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Foundry Agent Verification",
                "message": message,
                "type": notif_type,
                "sticky": False,
            },
        }

    def action_open_foundry_portal(self):
        """Open the Foundry portal URL in a new browser tab."""
        ICP = self.env["ir.config_parameter"].sudo()
        endpoint = ICP.get_param(
            f"{PARAM_PREFIX}.foundry_endpoint", ""
        )
        if not endpoint:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Foundry Portal",
                    "message": "No Foundry portal URL configured.",
                    "type": "warning",
                    "sticky": False,
                },
            }
        return {
            "type": "ir.actions.act_url",
            "url": endpoint,
            "target": "new",
        }
