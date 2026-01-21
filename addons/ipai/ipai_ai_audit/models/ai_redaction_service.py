# -*- coding: utf-8 -*-
"""
IPAI AI Redaction Service.

Detect and redact sensitive information from AI requests/responses.
"""
import re

from odoo import api, fields, models


class IpaiAiRedactionService(models.AbstractModel):
    """Service for redacting sensitive information."""

    _name = "ipai.ai.redaction.service"
    _description = "AI Redaction Service"

    # Default redaction patterns
    DEFAULT_PATTERNS = [
        # Email addresses
        (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL]"),
        # Phone numbers (various formats)
        (
            r"\b(?:\+?63|0)?[\s.-]?(?:9\d{2}|2\d{1,2})[\s.-]?\d{3}[\s.-]?\d{4}\b",
            "[PHONE]",
        ),
        # Credit card numbers (simple pattern)
        (r"\b(?:\d{4}[\s-]?){3}\d{4}\b", "[CARD]"),
        # SSS/TIN numbers (Philippines)
        (r"\b\d{2}-\d{7}-\d\b", "[SSS]"),
        (r"\b\d{3}-\d{3}-\d{3}(?:-\d{3})?\b", "[TIN]"),
        # Passport numbers
        (r"\b[A-Z]{1,2}\d{6,9}\b", "[PASSPORT]"),
        # Bank account numbers (generic)
        (r"\b\d{10,18}\b", "[ACCOUNT]"),
        # IP addresses
        (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP]"),
        # API keys (common patterns)
        (r"\b(?:sk|pk|api|key)[-_]?[a-zA-Z0-9]{20,}\b", "[API_KEY]"),
        # Passwords in common formats
        (r"(?i)password[\s:=]+\S+", "[PASSWORD]"),
        (r"(?i)secret[\s:=]+\S+", "[SECRET]"),
    ]

    @api.model
    def get_patterns(self):
        """Get configured redaction patterns."""
        # Get custom patterns from config
        custom = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ai_audit.redaction_patterns", "")
        )

        patterns = list(self.DEFAULT_PATTERNS)

        if custom:
            for line in custom.split("\n"):
                line = line.strip()
                if line and "|" in line:
                    pattern, replacement = line.split("|", 1)
                    patterns.append((pattern.strip(), replacement.strip()))

        return patterns

    @api.model
    def redact_text(self, text):
        """
        Redact sensitive information from text.

        Args:
            text: Text to redact

        Returns:
            tuple: (redacted_text, was_redacted)
        """
        if not text:
            return text, False

        original = text
        patterns = self.get_patterns()

        for pattern, replacement in patterns:
            try:
                text = re.sub(pattern, replacement, text)
            except re.error:
                # Invalid regex, skip
                continue

        was_redacted = text != original
        return text, was_redacted

    @api.model
    def detect_sensitive(self, text):
        """
        Detect sensitive information without redacting.

        Args:
            text: Text to analyze

        Returns:
            list of dicts with detected sensitive data types
        """
        if not text:
            return []

        detected = []
        patterns = self.get_patterns()

        for pattern, label in patterns:
            try:
                matches = re.findall(pattern, text)
                if matches:
                    detected.append(
                        {
                            "type": label,
                            "count": len(matches),
                        }
                    )
            except re.error:
                continue

        return detected

    @api.model
    def add_custom_pattern(self, pattern, replacement):
        """
        Add a custom redaction pattern.

        Args:
            pattern: Regex pattern
            replacement: Replacement text

        Returns:
            bool: True if successfully added
        """
        # Validate pattern
        try:
            re.compile(pattern)
        except re.error:
            return False

        # Get existing patterns
        existing = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ai_audit.redaction_patterns", "")
        )

        # Add new pattern
        new_line = f"{pattern}|{replacement}"
        if existing:
            updated = existing + "\n" + new_line
        else:
            updated = new_line

        self.env["ir.config_parameter"].sudo().set_param(
            "ipai_ai_audit.redaction_patterns",
            updated,
        )

        return True

    @api.model
    def is_safe_to_log(self, text):
        """
        Check if text is safe to log without redaction.

        Args:
            text: Text to check

        Returns:
            bool: True if no sensitive data detected
        """
        detected = self.detect_sensitive(text)
        return len(detected) == 0
