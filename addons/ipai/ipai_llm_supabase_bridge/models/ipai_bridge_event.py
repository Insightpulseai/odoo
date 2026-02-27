"""Outbox / dead-letter queue for Supabase webhook events."""

import json
import logging
import traceback

from odoo import api, fields, models

from .ipai_bridge_config import PARAM_PREFIX, _send_webhook

_logger = logging.getLogger(__name__)


class IpaiBridgeEvent(models.Model):
    """Immutable event log + outbox for Supabase webhook delivery."""

    _name = "ipai.bridge.event"
    _description = "IPAI Supabase Bridge Event"
    _order = "create_date desc"
    _rec_name = "event_type"

    event_type = fields.Selection(
        [
            ("tool.call", "Tool Call"),
            ("tool.result", "Tool Result"),
            ("thread.create", "Thread Created"),
            ("thread.message", "Thread Message"),
            ("thread.complete", "Thread Completed"),
            ("generation.start", "Generation Started"),
            ("generation.complete", "Generation Completed"),
            ("bridge.ping", "Bridge Ping"),
        ],
        required=True,
        index=True,
    )
    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("failed", "Failed"),
            ("dead", "Dead Letter"),
        ],
        default="pending",
        required=True,
        index=True,
    )
    payload = fields.Json(string="Event Payload")
    error_message = fields.Text(string="Last Error")
    attempts = fields.Integer(default=0)
    next_retry_at = fields.Datetime(string="Next Retry At")

    # Linkage to Odoo source records
    res_model = fields.Char(string="Source Model", index=True)
    res_id = fields.Integer(string="Source Record ID")
    odoo_db = fields.Char(string="Odoo Database")

    # Idempotency
    idempotency_key = fields.Char(
        string="Idempotency Key",
        index=True,
        help="Prevents duplicate delivery of the same event",
    )

    _sql_constraints = [
        (
            "idempotency_key_uniq",
            "UNIQUE(idempotency_key)",
            "Duplicate event idempotency key.",
        ),
    ]

    @api.model
    def _emit(self, event_type, payload, res_model=None, res_id=None,
              idempotency_key=None):
        """Create an event and attempt immediate delivery.

        This is the main entry point called by the llm_tool / llm_thread
        monkey-patches.
        """
        icp = self.env["ir.config_parameter"].sudo()
        enabled = icp.get_param(f"{PARAM_PREFIX}.enabled", "False") == "True"
        if not enabled:
            return self.browse()

        vals = {
            "event_type": event_type,
            "payload": payload,
            "res_model": res_model,
            "res_id": res_id or 0,
            "odoo_db": self.env.cr.dbname,
            "idempotency_key": idempotency_key,
        }
        event = self.sudo().create(vals)
        # Attempt immediate delivery (best-effort, non-blocking)
        event._try_send()
        return event

    def _try_send(self):
        """Attempt webhook delivery for a single event."""
        self.ensure_one()
        icp = self.env["ir.config_parameter"].sudo()
        url = icp.get_param(f"{PARAM_PREFIX}.webhook_url", "")
        secret = icp.get_param(f"{PARAM_PREFIX}.webhook_secret", "")
        max_retries = int(icp.get_param(f"{PARAM_PREFIX}.max_retries", "5"))

        if not url:
            return

        envelope = {
            "event_id": self.id,
            "event_type": self.event_type,
            "idempotency_key": self.idempotency_key,
            "odoo_db": self.odoo_db,
            "source_model": self.res_model,
            "source_id": self.res_id,
            "timestamp": fields.Datetime.now().isoformat(),
            "payload": self.payload,
        }

        try:
            _send_webhook(url, secret, envelope)
            self.write({"status": "sent", "attempts": self.attempts + 1})
        except Exception as exc:
            attempts = self.attempts + 1
            new_status = "dead" if attempts >= max_retries else "failed"
            backoff_base = int(
                icp.get_param(f"{PARAM_PREFIX}.retry_backoff_base", "60")
            )
            next_retry = None
            if new_status == "failed":
                delay_seconds = backoff_base * (2 ** (attempts - 1))
                next_retry = fields.Datetime.add(
                    fields.Datetime.now(), seconds=delay_seconds
                )
            self.write(
                {
                    "status": new_status,
                    "attempts": attempts,
                    "error_message": traceback.format_exc()[-500:],
                    "next_retry_at": next_retry,
                }
            )
            _logger.warning(
                "Bridge event %s delivery failed (attempt %d): %s",
                self.id,
                attempts,
                exc,
            )

    @api.model
    def _cron_retry_failed(self):
        """Cron job: retry failed events whose next_retry_at has passed."""
        events = self.sudo().search(
            [
                ("status", "=", "failed"),
                ("next_retry_at", "<=", fields.Datetime.now()),
            ],
            limit=200,
            order="next_retry_at asc",
        )
        _logger.info("Bridge retry cron: %d events to retry", len(events))
        for event in events:
            event._try_send()
            # Commit after each to avoid losing progress on timeout
            self.env.cr.commit()

    @api.model
    def _cron_flush_pending(self):
        """Cron job: batch-send any pending events that missed immediate delivery."""
        batch_size = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(f"{PARAM_PREFIX}.batch_size", "50")
        )
        events = self.sudo().search(
            [("status", "=", "pending")],
            limit=batch_size,
            order="create_date asc",
        )
        _logger.info("Bridge flush cron: %d pending events", len(events))
        for event in events:
            event._try_send()
            self.env.cr.commit()
