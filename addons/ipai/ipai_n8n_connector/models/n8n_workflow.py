# -*- coding: utf-8 -*-
from odoo import api, fields, models


class N8nWorkflow(models.Model):
    """Cached n8n workflow information."""

    _name = "ipai.n8n.workflow"
    _description = "n8n Workflow"
    _order = "name"

    connector_id = fields.Many2one(
        "ipai.integration.connector",
        required=True,
        ondelete="cascade",
        domain="[('connector_type', '=', 'n8n')]",
    )

    # n8n IDs
    n8n_workflow_id = fields.Char(required=True, index=True)

    # Workflow info
    name = fields.Char(required=True)
    active_in_n8n = fields.Boolean(
        string="Active in n8n", help="Whether the workflow is active in n8n"
    )
    tags = fields.Char(help="Comma-separated tags")

    # Trigger info
    trigger_type = fields.Selection(
        [
            ("webhook", "Webhook"),
            ("schedule", "Schedule/Cron"),
            ("manual", "Manual"),
            ("event", "Event"),
        ]
    )
    webhook_path = fields.Char(help="Webhook path for triggering this workflow")

    # Execution tracking
    execution_ids = fields.One2many(
        "ipai.n8n.execution", "workflow_id", string="Executions"
    )
    last_execution_id = fields.Many2one(
        "ipai.n8n.execution", compute="_compute_last_execution", string="Last Execution"
    )
    execution_count = fields.Integer(compute="_compute_execution_count")

    # Sync status
    last_sync = fields.Datetime()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "workflow_uniq",
            "unique(connector_id, n8n_workflow_id)",
            "Workflow already exists for this connector!",
        ),
    ]

    def _compute_last_execution(self):
        for rec in self:
            rec.last_execution_id = rec.execution_ids[:1]

    def _compute_execution_count(self):
        for rec in self:
            rec.execution_count = len(rec.execution_ids)

    @api.model
    def sync_workflows(self, connector):
        """Sync workflows from n8n API."""
        from ..services.n8n_client import N8nClient

        client = N8nClient(connector)
        workflows = client.get_workflows()

        for wf in workflows:
            existing = self.search(
                [
                    ("connector_id", "=", connector.id),
                    ("n8n_workflow_id", "=", str(wf["id"])),
                ],
                limit=1,
            )

            # Determine trigger type
            trigger_type = "manual"
            webhook_path = None
            nodes = wf.get("nodes", [])
            for node in nodes:
                node_type = node.get("type", "")
                if "webhook" in node_type.lower():
                    trigger_type = "webhook"
                    # Try to extract webhook path
                    params = node.get("parameters", {})
                    webhook_path = params.get("path")
                    break
                elif "cron" in node_type.lower() or "schedule" in node_type.lower():
                    trigger_type = "schedule"
                    break

            vals = {
                "connector_id": connector.id,
                "n8n_workflow_id": str(wf["id"]),
                "name": wf.get("name", "Untitled"),
                "active_in_n8n": wf.get("active", False),
                "trigger_type": trigger_type,
                "webhook_path": webhook_path,
                "last_sync": fields.Datetime.now(),
            }

            if existing:
                existing.write(vals)
            else:
                self.create(vals)

        return True

    def action_trigger(self):
        """Manually trigger this workflow via webhook."""
        self.ensure_one()
        if not self.webhook_path:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Cannot Trigger",
                    "message": "This workflow does not have a webhook trigger.",
                    "type": "warning",
                },
            }

        from ..services.n8n_client import N8nClient

        client = N8nClient(self.connector_id)
        result = client.trigger_webhook(
            self.webhook_path,
            {
                "triggered_from": "odoo",
                "workflow_id": self.n8n_workflow_id,
            },
        )

        # Log execution
        self.env["ipai.n8n.execution"].create(
            {
                "workflow_id": self.id,
                "trigger_source": "odoo_manual",
                "status": "running" if result else "error",
            }
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Workflow Triggered",
                "message": f"Workflow '{self.name}' has been triggered.",
                "type": "success",
            },
        }
