"""
IPAI Outbox Event Model
For reliable event emission from Odoo to Supabase SSOT.
"""
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IpaiOutboxEvent(models.Model):
    _name = "ipai.outbox.event"
    _description = "Outbox Event for SSOT Mirroring"
    _order = "id asc"

    topic = fields.Char(
        string="Topic",
        required=True,
        index=True,
        help="Event topic (deployment, incident, mirror)",
    )
    action = fields.Char(
        string="Action",
        required=True,
        default="create",
        help="Event action (create, update, close)",
    )
    actor = fields.Char(
        string="Actor",
        help="Who/what triggered this event",
    )
    payload = fields.Text(
        string="Payload (JSON)",
        required=True,
        help="Event payload as JSON",
    )
    created_at = fields.Datetime(
        string="Created At",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    delivered_at = fields.Datetime(
        string="Delivered At",
        index=True,
        help="When the event was successfully delivered to SSOT",
    )
    attempts = fields.Integer(
        string="Attempts",
        default=0,
        help="Number of delivery attempts",
    )
    next_attempt_at = fields.Datetime(
        string="Next Attempt At",
        help="When to retry delivery",
    )
    last_error = fields.Text(
        string="Last Error",
        help="Last delivery error message",
    )
    locked_at = fields.Datetime(
        string="Locked At",
        help="When a worker locked this event",
    )
    locked_by = fields.Char(
        string="Locked By",
        help="Worker ID that locked this event",
    )

    @api.model
    def emit_event(self, topic: str, action: str, payload: dict, actor: str = None):
        """
        Emit an event to the outbox for delivery to SSOT.

        Args:
            topic: Event topic (deployment, incident, mirror)
            action: Event action (create, update, close)
            payload: Event payload as dict
            actor: Who triggered this event (optional)

        Returns:
            Created outbox event record
        """
        return self.create({
            "topic": topic,
            "action": action,
            "actor": actor or self.env.user.login,
            "payload": json.dumps(payload, ensure_ascii=False),
        })

    @api.model
    def emit_mirror_event(
        self,
        odoo_model: str,
        odoo_id: int,
        snapshot: dict,
        external_key: str = None
    ):
        """
        Emit a mirror event for an Odoo object snapshot.

        Args:
            odoo_model: Odoo model name (e.g., res.partner)
            odoo_id: Odoo record ID
            snapshot: Record data as dict
            external_key: Optional external key for mapping

        Returns:
            Created outbox event record
        """
        payload = {
            "mirror": {
                "odoo_model": odoo_model,
                "odoo_id": odoo_id,
                "external_key": external_key,
                "snapshot": snapshot,
            }
        }
        return self.emit_event("mirror", "sync", payload)

    @api.model
    def emit_deployment_event(
        self,
        system: str,
        environment: str,
        version: str,
        status: str,
        metadata: dict = None
    ):
        """
        Emit a deployment event.

        Args:
            system: System identifier
            environment: Environment (prod/dev/stage)
            version: Deployment version
            status: Deployment status
            metadata: Additional metadata

        Returns:
            Created outbox event record
        """
        payload = {
            "deployment": {
                "system": system,
                "environment": environment,
                "version": version,
                "status": status,
                "metadata": metadata or {},
            }
        }
        return self.emit_event("deployment", "create", payload)

    @api.model
    def emit_incident_event(
        self,
        system: str,
        environment: str,
        severity: str,
        title: str,
        status: str = "open",
        metadata: dict = None
    ):
        """
        Emit an incident event.

        Args:
            system: System identifier
            environment: Environment (prod/dev/stage)
            severity: Incident severity (sev1, sev2, sev3, sev4)
            title: Incident title
            status: Incident status (open, mitigated, closed)
            metadata: Additional metadata

        Returns:
            Created outbox event record
        """
        payload = {
            "incident": {
                "system": system,
                "environment": environment,
                "severity": severity,
                "title": title,
                "status": status,
                "metadata": metadata or {},
            }
        }
        return self.emit_event("incident", "create", payload)
