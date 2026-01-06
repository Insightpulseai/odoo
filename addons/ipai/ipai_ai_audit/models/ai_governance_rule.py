# -*- coding: utf-8 -*-
"""
IPAI AI Governance Rule Model.

Define and enforce AI usage policies.
"""
from odoo import api, fields, models
from odoo.exceptions import UserError


class IpaiAiGovernanceRule(models.Model):
    """Governance rules for AI usage."""

    _name = "ipai.ai.governance.rule"
    _description = "AI Governance Rule"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Rule type
    rule_type = fields.Selection(
        [
            ("allow", "Allow"),
            ("deny", "Deny"),
            ("rate_limit", "Rate Limit"),
            ("require_approval", "Require Approval"),
        ],
        required=True,
        default="allow",
    )

    # Scope
    apply_to_all = fields.Boolean(
        string="Apply to All Users",
        default=True,
    )
    group_ids = fields.Many2many(
        "res.groups",
        string="Apply to Groups",
        help="Leave empty to apply to all users",
    )
    user_ids = fields.Many2many(
        "res.users",
        string="Apply to Users",
        help="Specific users this rule applies to",
    )

    # Conditions
    provider_filter = fields.Char(
        help="Provider name filter (empty = all providers)",
    )
    model_filter = fields.Char(
        help="Model name filter (empty = all models)",
    )
    source_filter = fields.Char(
        help="Source filter (e.g., 'chatter', 'ask_ai')",
    )

    # Rate limiting
    rate_limit_count = fields.Integer(
        string="Max Requests",
        default=100,
    )
    rate_limit_period = fields.Selection(
        [
            ("minute", "Per Minute"),
            ("hour", "Per Hour"),
            ("day", "Per Day"),
            ("month", "Per Month"),
        ],
        string="Rate Period",
        default="day",
    )

    # Token limits
    max_tokens_per_request = fields.Integer(
        default=0,
        help="Maximum tokens per request (0 = no limit)",
    )
    max_tokens_per_day = fields.Integer(
        default=0,
        help="Maximum tokens per day per user (0 = no limit)",
    )

    # Content restrictions
    block_patterns = fields.Text(
        help="Regex patterns to block (one per line)",
    )
    required_patterns = fields.Text(
        help="Regex patterns that must be present (one per line)",
    )

    # Logging
    log_all_requests = fields.Boolean(default=True)
    log_blocked_only = fields.Boolean(default=False)

    # Description
    description = fields.Text()

    _sql_constraints = [
        ("code_unique", "unique(code)", "Governance rule code must be unique."),
    ]

    @api.model
    def check_request(self, user, provider=None, model=None, source=None, content=None):
        """
        Check if a request is allowed by governance rules.

        Args:
            user: res.users record
            provider: AI provider name
            model: AI model name
            source: Request source
            content: Request content (for pattern matching)

        Returns:
            dict: {
                'allowed': bool,
                'rule': governance rule that matched (or None),
                'reason': str (if blocked),
            }
        """
        rules = self.search([("active", "=", True)], order="sequence")

        for rule in rules:
            # Check if rule applies to this user
            if not rule._applies_to_user(user):
                continue

            # Check filters
            if rule.provider_filter and provider and rule.provider_filter not in provider:
                continue
            if rule.model_filter and model and rule.model_filter not in model:
                continue
            if rule.source_filter and source and rule.source_filter not in source:
                continue

            # Apply rule
            if rule.rule_type == "deny":
                return {
                    "allowed": False,
                    "rule": rule,
                    "reason": f"Blocked by governance rule: {rule.name}",
                }

            if rule.rule_type == "rate_limit":
                if not rule._check_rate_limit(user):
                    return {
                        "allowed": False,
                        "rule": rule,
                        "reason": f"Rate limit exceeded: {rule.rate_limit_count} per {rule.rate_limit_period}",
                    }

            # Check content patterns
            if content and rule.block_patterns:
                import re
                for pattern in rule.block_patterns.split("\n"):
                    pattern = pattern.strip()
                    if pattern and re.search(pattern, content, re.IGNORECASE):
                        return {
                            "allowed": False,
                            "rule": rule,
                            "reason": f"Content blocked by pattern: {pattern}",
                        }

        # No blocking rules matched
        return {"allowed": True, "rule": None, "reason": None}

    def _applies_to_user(self, user):
        """Check if this rule applies to a user."""
        self.ensure_one()

        if self.apply_to_all:
            return True

        if self.user_ids and user in self.user_ids:
            return True

        if self.group_ids:
            user_groups = user.groups_id
            if any(g in user_groups for g in self.group_ids):
                return True

        return False

    def _check_rate_limit(self, user):
        """Check if user is within rate limit."""
        self.ensure_one()

        # Calculate time window
        now = fields.Datetime.now()
        if self.rate_limit_period == "minute":
            cutoff = fields.Datetime.subtract(now, minutes=1)
        elif self.rate_limit_period == "hour":
            cutoff = fields.Datetime.subtract(now, hours=1)
        elif self.rate_limit_period == "day":
            cutoff = fields.Datetime.subtract(now, days=1)
        else:  # month
            cutoff = fields.Datetime.subtract(now, days=30)

        # Count recent requests
        AuditLog = self.env["ipai.ai.audit.log"]
        count = AuditLog.search_count([
            ("user_id", "=", user.id),
            ("request_time", ">=", cutoff),
            ("state", "in", ["success", "error"]),  # Don't count blocked
        ])

        return count < self.rate_limit_count

    @api.model
    def get_user_limits(self, user=None):
        """Get effective limits for a user."""
        user = user or self.env.user
        rules = self.search([("active", "=", True)])

        limits = {
            "max_tokens_per_request": 0,
            "max_tokens_per_day": 0,
            "rate_limit_count": 0,
            "rate_limit_period": None,
        }

        for rule in rules:
            if rule._applies_to_user(user):
                if rule.max_tokens_per_request:
                    limits["max_tokens_per_request"] = max(
                        limits["max_tokens_per_request"],
                        rule.max_tokens_per_request,
                    )
                if rule.max_tokens_per_day:
                    limits["max_tokens_per_day"] = max(
                        limits["max_tokens_per_day"],
                        rule.max_tokens_per_day,
                    )
                if rule.rule_type == "rate_limit":
                    limits["rate_limit_count"] = rule.rate_limit_count
                    limits["rate_limit_period"] = rule.rate_limit_period

        return limits
