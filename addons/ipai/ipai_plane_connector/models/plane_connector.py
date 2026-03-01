# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Plane connector AbstractModel — inherited by domain modules.

Provides ready-made helpers for:
- Obtaining a configured :class:`PlaneClient` instance.
- Verifying inbound webhook HMAC signatures.
- Deduplicating webhook deliveries via ``plane.webhook.delivery``.

Domain modules inherit this abstract model to gain Plane integration
without re-implementing auth, rate-limiting, or verification logic.
"""

import logging

from odoo import api, models
from odoo.exceptions import UserError

from ..utils.plane_client import PlaneClient
from ..utils.plane_webhook import verify_plane_signature

_logger = logging.getLogger(__name__)


class PlaneConnector(models.AbstractModel):
    _name = "ipai.plane.connector"
    _description = "Plane API Connector Base"

    # ------------------------------------------------------------------
    # Client factory
    # ------------------------------------------------------------------

    @api.model
    def _plane_client(self):
        """Return a :class:`PlaneClient` configured from system parameters.

        Required ir.config_parameter:
            plane.api_key — Plane API key.

        Optional ir.config_parameter:
            plane.base_url — Plane instance base URL
                             (default: https://api.plane.so).

        Raises:
            UserError: If ``plane.api_key`` is not set.
        """
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("plane.base_url", "https://api.plane.so")
        api_key = params.get_param("plane.api_key")
        if not api_key:
            raise UserError("Plane API key not configured (plane.api_key)")
        return PlaneClient(base_url=base_url, api_key=api_key)

    # ------------------------------------------------------------------
    # Workspace helper
    # ------------------------------------------------------------------

    @api.model
    def _plane_workspace_slug(self):
        """Return the configured Plane workspace slug."""
        return self.env["ir.config_parameter"].sudo().get_param(
            "plane.workspace_slug", "insightpulseai"
        )

    # ------------------------------------------------------------------
    # Webhook verification
    # ------------------------------------------------------------------

    @api.model
    def _plane_verify_webhook(self, headers, body):
        """Verify an inbound Plane webhook request.

        Args:
            headers (dict): HTTP request headers (must contain
                ``X-Plane-Signature``).
            body (str | bytes): Raw request body.

        Returns:
            bool: ``True`` if signature is valid.

        Raises:
            UserError: If ``plane.webhook_secret`` is not configured.
        """
        secret = self.env["ir.config_parameter"].sudo().get_param(
            "plane.webhook_secret"
        )
        if not secret:
            raise UserError("Plane webhook secret not configured")
        signature = headers.get("X-Plane-Signature", "")
        payload_bytes = (
            body if isinstance(body, bytes) else body.encode("utf-8")
        )
        return verify_plane_signature(secret, payload_bytes, signature)

    # ------------------------------------------------------------------
    # Delivery deduplication
    # ------------------------------------------------------------------

    @api.model
    def _plane_is_duplicate_delivery(self, delivery_id):
        """Check whether a webhook delivery has already been recorded.

        Args:
            delivery_id (str): The unique delivery identifier from the
                webhook headers.

        Returns:
            bool: ``True`` if a record with this ``delivery_id`` exists.
        """
        if not delivery_id:
            return False
        existing = self.env["plane.webhook.delivery"].sudo().search(
            [("delivery_id", "=", delivery_id)], limit=1,
        )
        return bool(existing)

    @api.model
    def _plane_record_delivery(self, delivery_id, event_type=None):
        """Create a ``plane.webhook.delivery`` record for deduplication.

        Args:
            delivery_id (str): Unique delivery identifier.
            event_type (str | None): Webhook event type (e.g.
                ``issue.created``).

        Returns:
            plane.webhook.delivery recordset.
        """
        return self.env["plane.webhook.delivery"].sudo().create({
            "delivery_id": delivery_id,
            "event_type": event_type,
        })

    # ------------------------------------------------------------------
    # Feature-flag check
    # ------------------------------------------------------------------

    @api.model
    def _plane_enabled(self):
        """Return ``True`` if all required Plane parameters are configured.

        Checks that ``plane.base_url``, ``plane.api_key``, and
        ``plane.workspace_slug`` are all set to non-empty values.
        """
        params = self.env["ir.config_parameter"].sudo()
        return bool(
            params.get_param("plane.base_url")
            and params.get_param("plane.api_key")
            and params.get_param("plane.workspace_slug")
        )
