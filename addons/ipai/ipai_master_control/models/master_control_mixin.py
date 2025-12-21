# -*- coding: utf-8 -*-
"""
Master Control Mixin — Webhook Dispatcher

Provides a reusable mixin for emitting work items to the Master Control API.
"""
import json
import logging
from urllib.parse import urljoin

from odoo import api, models

_logger = logging.getLogger(__name__)

# Timeout for webhook requests (seconds)
WEBHOOK_TIMEOUT = 10


class MasterControlMixin(models.AbstractModel):
    """Mixin for emitting events to Master Control."""

    _name = "master.control.mixin"
    _description = "Master Control Webhook Mixin"

    @api.model
    def _get_master_control_config(self):
        """Get Master Control configuration from system parameters."""
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "webhook_url": ICP.get_param("master_control.webhook_url", ""),
            "tenant_id": ICP.get_param(
                "master_control.tenant_id",
                "00000000-0000-0000-0000-000000000001",
            ),
            "enabled": ICP.get_param("master_control.enabled", "true") == "true",
            "events": {
                "employee_hire": ICP.get_param(
                    "master_control.events.employee_hire", "true"
                )
                == "true",
                "employee_departure": ICP.get_param(
                    "master_control.events.employee_departure", "true"
                )
                == "true",
                "expense_submit": ICP.get_param(
                    "master_control.events.expense_submit", "true"
                )
                == "true",
                "purchase_large": ICP.get_param(
                    "master_control.events.purchase_large", "true"
                )
                == "true",
            },
        }

    @api.model
    def _emit_work_item(
        self,
        source: str,
        source_ref: str,
        title: str,
        lane: str,
        priority: int = 3,
        payload: dict = None,
        tags: list = None,
    ):
        """
        Emit a work item to Master Control.

        Args:
            source: Event source (e.g., 'odoo_event')
            source_ref: Unique reference (e.g., 'hr.employee:42:hire')
            title: Work item title
            lane: Routing lane (HR, IT, FIN, MGR)
            priority: 1-4 (1=critical, 4=low)
            payload: Additional context data
            tags: Optional list of tags
        """
        config = self._get_master_control_config()

        if not config["enabled"]:
            _logger.debug("Master Control disabled, skipping work item emission")
            return False

        if not config["webhook_url"]:
            _logger.warning(
                "Master Control webhook_url not configured, skipping emission"
            )
            return False

        work_item = {
            "tenant_id": config["tenant_id"],
            "source": source,
            "source_ref": source_ref,
            "title": title,
            "lane": lane,
            "priority": priority,
            "payload": payload or {},
            "tags": tags or [],
        }

        try:
            import requests

            url = urljoin(config["webhook_url"], "/v1/work-items")
            response = requests.post(
                url,
                json=work_item,
                headers={"Content-Type": "application/json"},
                timeout=WEBHOOK_TIMEOUT,
            )

            if response.ok:
                result = response.json()
                _logger.info(
                    "Master Control work item created: %s (source_ref=%s)",
                    result.get("work_item_id"),
                    source_ref,
                )
                return result
            else:
                _logger.error(
                    "Master Control webhook failed: %s %s",
                    response.status_code,
                    response.text,
                )
                return False

        except ImportError:
            _logger.error(
                "requests library not available, cannot emit to Master Control"
            )
            return False
        except Exception as e:
            _logger.exception("Master Control webhook error: %s", e)
            return False

    @api.model
    def _is_event_enabled(self, event_type: str) -> bool:
        """Check if a specific event type is enabled."""
        config = self._get_master_control_config()
        return config["enabled"] and config["events"].get(event_type, False)
