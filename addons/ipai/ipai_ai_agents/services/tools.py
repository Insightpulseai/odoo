# -*- coding: utf-8 -*-
"""
Read-only tool stubs to mirror Odoo 19-ish "standard agent" behavior.

These tools can be wired into an agent loop when actions are enabled.
By default, agents are read-only and can only:
- Open views/reports (navigation)
- Search and read records (with allowlist)
- Explain records (summarize)

Write operations require explicit approval flow.
"""
import logging
from typing import Any, Dict, List

_logger = logging.getLogger(__name__)


class ReadOnlyTools:
    """
    Read-only Odoo tools for AI agents.

    These mirror the behavior described for Odoo 19's "standard" Ask AI agent
    that can help users navigate but cannot modify data.
    """

    # Models allowed for search_read (add more as needed)
    ALLOWED_MODELS = [
        "res.partner",
        "res.users",
        "project.project",
        "project.task",
        "sale.order",
        "purchase.order",
        "account.move",
        "crm.lead",
        "hr.employee",
        "product.product",
        "product.template",
        "stock.picking",
    ]

    def __init__(self, env):
        self.env = env

    def open_action(self, xml_id: str) -> Dict[str, Any]:
        """
        Open a view/action by XML ID.

        This allows the agent to help users navigate to specific screens.

        Args:
            xml_id: External ID of the action (e.g., 'sale.action_orders')

        Returns:
            {ok: bool, action: dict, error: str}
        """
        try:
            action = self.env.ref(xml_id, raise_if_not_found=False)
            if not action:
                return {"ok": False, "error": f"Action '{xml_id}' not found"}

            # Return action definition for client to execute
            return {
                "ok": True,
                "action": action.read()[0] if hasattr(action, "read") else {"xml_id": xml_id},
            }
        except Exception as e:
            _logger.warning("open_action failed for %s: %s", xml_id, e)
            return {"ok": False, "error": str(e)}

    def search_read(
        self,
        model: str,
        domain: List = None,
        fields: List[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search and read records (allowlisted models only).

        Args:
            model: Model name (must be in ALLOWED_MODELS)
            domain: Search domain
            fields: Fields to read
            limit: Max records to return

        Returns:
            {ok: bool, records: list, error: str}
        """
        if model not in self.ALLOWED_MODELS:
            return {
                "ok": False,
                "error": f"Model '{model}' not in allowlist. Allowed: {self.ALLOWED_MODELS[:5]}..."
            }

        try:
            Model = self.env[model]
            domain = domain or []
            fields = fields or ["name", "display_name"]
            limit = min(limit, 100)  # Hard cap

            records = Model.search(domain, limit=limit)
            return {
                "ok": True,
                "records": records.read(fields),
                "count": len(records),
            }
        except Exception as e:
            _logger.warning("search_read failed for %s: %s", model, e)
            return {"ok": False, "error": str(e)}

    def explain_record(self, model: str, record_id: int) -> Dict[str, Any]:
        """
        Get a summary/explanation of a record.

        Args:
            model: Model name
            record_id: Record ID

        Returns:
            {ok: bool, summary: str, fields: dict, error: str}
        """
        if model not in self.ALLOWED_MODELS:
            return {
                "ok": False,
                "error": f"Model '{model}' not in allowlist"
            }

        try:
            record = self.env[model].browse(record_id)
            if not record.exists():
                return {"ok": False, "error": "Record not found"}

            # Read key fields
            fields_info = record.fields_get()
            readable_fields = [
                f for f in fields_info.keys()
                if fields_info[f].get("type") not in ("binary", "html")
                and not f.startswith("_")
            ][:20]

            data = record.read(readable_fields)[0] if record else {}

            # Build a simple summary
            name = data.get("name") or data.get("display_name") or f"Record #{record_id}"
            summary_parts = [f"**{name}** ({model})"]

            for field in ["state", "stage_id", "partner_id", "date", "create_date"]:
                if field in data and data[field]:
                    val = data[field]
                    if isinstance(val, (list, tuple)):
                        val = val[1] if len(val) > 1 else val[0]
                    summary_parts.append(f"- {field}: {val}")

            return {
                "ok": True,
                "summary": "\n".join(summary_parts),
                "fields": data,
            }
        except Exception as e:
            _logger.warning("explain_record failed for %s/%s: %s", model, record_id, e)
            return {"ok": False, "error": str(e)}

    def get_menu_items(self, parent_id: int = None, limit: int = 20) -> Dict[str, Any]:
        """
        List available menu items for navigation assistance.

        Args:
            parent_id: Parent menu ID (None for root menus)
            limit: Max items to return

        Returns:
            {ok: bool, menus: list, error: str}
        """
        try:
            Menu = self.env["ir.ui.menu"]
            domain = [("parent_id", "=", parent_id)]
            menus = Menu.search(domain, limit=limit)

            return {
                "ok": True,
                "menus": [{
                    "id": m.id,
                    "name": m.name,
                    "complete_name": m.complete_name,
                    "action": m.action.xml_id if m.action else None,
                } for m in menus],
            }
        except Exception as e:
            _logger.warning("get_menu_items failed: %s", e)
            return {"ok": False, "error": str(e)}


class ProposedAction:
    """
    Represents a proposed write action that requires approval.

    This enables "propose" mode where the agent can suggest changes
    but not execute them without user confirmation.
    """

    def __init__(self, action_type: str, model: str, record_id: int = None, vals: Dict = None):
        self.action_type = action_type  # 'create', 'write', 'unlink'
        self.model = model
        self.record_id = record_id
        self.vals = vals or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for storage/display."""
        return {
            "action_type": self.action_type,
            "model": self.model,
            "record_id": self.record_id,
            "vals": self.vals,
        }

    def describe(self) -> str:
        """Human-readable description of the proposed action."""
        if self.action_type == "create":
            return f"Create new {self.model} with: {self.vals}"
        elif self.action_type == "write":
            return f"Update {self.model}#{self.record_id} with: {self.vals}"
        elif self.action_type == "unlink":
            return f"Delete {self.model}#{self.record_id}"
        return f"Unknown action: {self.action_type}"
