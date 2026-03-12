import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# ir.config_parameter keys (shared with res_config_settings)
_PARAM_PREFIX = "ipai_odoo_copilot"


class FoundryService(models.AbstractModel):
    """Thin bounded service layer for Azure Foundry Copilot operations.

    This model provides bounded actions that validate configuration
    and log intent. It does NOT directly call Azure APIs in v1.
    Full SDK integration is a future slice.
    """

    _name = "ipai.foundry.service"
    _description = "Azure Foundry Copilot Service"

    def _get_config(self):
        """Read current Foundry config from ir.config_parameter."""
        icp = self.env["ir.config_parameter"].sudo()
        return {
            "enabled": icp.get_param(
                f"{_PARAM_PREFIX}.foundry_enabled", "False"
            ) == "True",
            "endpoint": icp.get_param(f"{_PARAM_PREFIX}.foundry_endpoint", ""),
            "project": icp.get_param(
                f"{_PARAM_PREFIX}.foundry_project", "data-intel-ph"
            ),
            "agent_name": icp.get_param(
                f"{_PARAM_PREFIX}.foundry_agent_name",
                "ipai-odoo-copilot-azure",
            ),
            "model": icp.get_param(f"{_PARAM_PREFIX}.foundry_model", "gpt-4.1"),
            "search_connection": icp.get_param(
                f"{_PARAM_PREFIX}.search_connection", ""
            ),
            "search_index": icp.get_param(f"{_PARAM_PREFIX}.search_index", ""),
            "memory_enabled": icp.get_param(
                f"{_PARAM_PREFIX}.memory_enabled", "False"
            ) == "True",
            "readonly_mode": icp.get_param(
                f"{_PARAM_PREFIX}.readonly_mode", "True"
            ) == "True",
            "draft_only_mode": icp.get_param(
                f"{_PARAM_PREFIX}.draft_only_mode", "True"
            ) == "True",
        }

    @api.model
    def test_connection(self):
        """Validate Foundry config shape. Does not call Azure APIs.

        Returns dict with 'status' ('success'|'warning'|'danger')
        and 'message'.
        """
        config = self._get_config()
        issues = []

        if not config["enabled"]:
            return {
                "status": "warning",
                "message": "Foundry Copilot is not enabled.",
            }

        if not config["endpoint"]:
            issues.append("Foundry endpoint is not configured.")
        if not config["project"]:
            issues.append("Foundry project is not configured.")
        if not config["agent_name"]:
            issues.append("Foundry agent name is not configured.")
        if not config["model"]:
            issues.append("Model is not configured.")

        if issues:
            _logger.warning(
                "Foundry connection test: config issues: %s",
                "; ".join(issues),
            )
            return {
                "status": "warning",
                "message": "Config issues: " + "; ".join(issues),
            }

        _logger.info(
            "Foundry connection test: config OK "
            "(endpoint=%s, project=%s, agent=%s, model=%s)",
            config["endpoint"],
            config["project"],
            config["agent_name"],
            config["model"],
        )
        return {
            "status": "success",
            "message": (
                f"Config OK — Agent: {config['agent_name']}, "
                f"Model: {config['model']}, "
                f"Project: {config['project']}. "
                "Note: this validates config shape only. "
                "Azure runtime connectivity requires managed identity wiring."
            ),
        }

    @api.model
    def ensure_agent(self):
        """Bounded sync stub. Logs intent but does not create Foundry resources.

        Full Azure SDK integration is a future slice. This action:
        1. Validates config shape
        2. Logs the sync intent
        3. Reports what would happen

        It does NOT call Azure Foundry APIs.
        """
        config = self._get_config()

        if not config["enabled"]:
            return {
                "status": "warning",
                "message": "Foundry Copilot is not enabled. Enable it first.",
            }

        _logger.info(
            "Foundry agent ensure (stub): would sync agent '%s' "
            "in project '%s' with model '%s'. "
            "Memory: %s, Read-only: %s, Draft-only: %s. "
            "This is a bounded stub — no Azure API calls made.",
            config["agent_name"],
            config["project"],
            config["model"],
            config["memory_enabled"],
            config["readonly_mode"],
            config["draft_only_mode"],
        )

        return {
            "status": "info",
            "message": (
                f"Sync intent logged for agent '{config['agent_name']}' "
                f"in project '{config['project']}'. "
                "This is a bounded stub — no Azure resources were created. "
                "Full SDK integration is a future slice."
            ),
        }
