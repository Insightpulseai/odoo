# -*- coding: utf-8 -*-
"""
IPAI AI Audit Log Model.

Comprehensive audit trail for AI interactions.
"""
import hashlib
import json

from odoo import api, fields, models


class IpaiAiAuditLog(models.Model):
    """Audit log for AI requests and responses."""

    _name = "ipai.ai.audit.log"
    _description = "AI Audit Log"
    _order = "create_date desc"
    _rec_name = "display_name"

    # Basic info
    display_name = fields.Char(compute="_compute_display_name", store=True)
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        default=lambda self: self.env.uid,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
    )

    # Timing
    request_time = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
        index=True,
    )
    response_time = fields.Datetime()
    duration_ms = fields.Integer(
        string="Duration (ms)",
        compute="_compute_duration",
        store=True,
    )

    # AI request details
    provider = fields.Char(index=True)
    model = fields.Char(index=True)

    # Content (may be redacted)
    request_content = fields.Text()
    response_content = fields.Text()
    is_redacted = fields.Boolean(default=False)

    # Hashes for integrity/deduplication
    request_hash = fields.Char(index=True)
    response_hash = fields.Char()

    # Token usage
    prompt_tokens = fields.Integer()
    completion_tokens = fields.Integer()
    total_tokens = fields.Integer()

    # Status
    state = fields.Selection(
        [
            ("success", "Success"),
            ("error", "Error"),
            ("blocked", "Blocked by Governance"),
        ],
        default="success",
        required=True,
        index=True,
    )
    error_message = fields.Text()

    # Context
    source = fields.Char(
        help="Where the request originated (e.g., chatter, ask_ai, marketing)",
        index=True,
    )
    res_model = fields.Char(
        string="Related Model",
        index=True,
    )
    res_id = fields.Integer(
        string="Related Record",
    )

    # Governance
    governance_rule_id = fields.Many2one(
        "ipai.ai.governance.rule",
        string="Applied Governance Rule",
    )

    @api.depends("request_time", "user_id")
    def _compute_display_name(self):
        for log in self:
            user = log.user_id.name or "Unknown"
            time = (
                log.request_time.strftime("%Y-%m-%d %H:%M") if log.request_time else ""
            )
            log.display_name = f"{user} - {time}"

    @api.depends("request_time", "response_time")
    def _compute_duration(self):
        for log in self:
            if log.request_time and log.response_time:
                delta = log.response_time - log.request_time
                log.duration_ms = int(delta.total_seconds() * 1000)
            else:
                log.duration_ms = 0

    @api.model
    def log_request(self, request_data, response_data, **kwargs):
        """
        Create an audit log entry.

        Args:
            request_data: Dict with request details
            response_data: Dict with response details
            **kwargs: Additional fields (source, res_model, res_id, etc.)

        Returns:
            ipai.ai.audit.log record
        """
        # Prepare content (may need redaction)
        redaction_service = self.env["ipai.ai.redaction.service"]

        request_content = json.dumps(
            request_data.get("messages", []), ensure_ascii=False
        )
        response_content = response_data.get("response", "")

        # Check if redaction is needed
        is_redacted = False
        if self._should_redact():
            request_content, redacted_req = redaction_service.redact_text(
                request_content
            )
            response_content, redacted_resp = redaction_service.redact_text(
                response_content
            )
            is_redacted = redacted_req or redacted_resp

        # Generate hashes
        request_hash = self._hash_content(request_content)
        response_hash = self._hash_content(response_content)

        # Determine state
        state = "success" if response_data.get("success") else "error"

        vals = {
            "user_id": self.env.uid,
            "request_time": fields.Datetime.now(),
            "response_time": fields.Datetime.now(),
            "provider": response_data.get("provider", ""),
            "model": response_data.get("model", ""),
            "request_content": request_content,
            "response_content": response_content,
            "is_redacted": is_redacted,
            "request_hash": request_hash,
            "response_hash": response_hash,
            "total_tokens": response_data.get("tokens_used", 0),
            "state": state,
            "error_message": response_data.get("error", ""),
        }
        vals.update(kwargs)

        return self.sudo().create(vals)

    def _hash_content(self, content):
        """Generate SHA256 hash of content."""
        if not content:
            return ""
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    @api.model
    def _should_redact(self):
        """Check if redaction is enabled."""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ai_audit.enable_redaction", "True")
        ) == "True"

    @api.model
    def cleanup_old_logs(self, days=90):
        """
        Remove logs older than specified days.

        Called by scheduled action based on retention policy.
        """
        cutoff = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        old_logs = self.sudo().search([("request_time", "<", cutoff)])
        count = len(old_logs)
        old_logs.unlink()
        return count

    @api.model
    def get_usage_stats(self, user_id=None, days=30):
        """
        Get usage statistics.

        Args:
            user_id: Optional user ID filter
            days: Number of days to analyze

        Returns:
            dict with usage statistics
        """
        cutoff = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        domain = [("request_time", ">=", cutoff)]

        if user_id:
            domain.append(("user_id", "=", user_id))

        logs = self.search(domain)

        return {
            "total_requests": len(logs),
            "successful_requests": len(logs.filtered(lambda l: l.state == "success")),
            "failed_requests": len(logs.filtered(lambda l: l.state == "error")),
            "blocked_requests": len(logs.filtered(lambda l: l.state == "blocked")),
            "total_tokens": sum(logs.mapped("total_tokens")),
            "unique_users": len(set(logs.mapped("user_id").ids)),
            "by_provider": self._group_by_field(logs, "provider"),
            "by_model": self._group_by_field(logs, "model"),
            "by_source": self._group_by_field(logs, "source"),
        }

    def _group_by_field(self, logs, field):
        """Group logs by field and count."""
        result = {}
        for log in logs:
            key = getattr(log, field) or "unknown"
            result[key] = result.get(key, 0) + 1
        return result
