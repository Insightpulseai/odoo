"""IPAI Tax Intelligence — Tax Validation Mixin.

Provides pre-posting tax validation behavior for account.move and
other document models. Creates tax exceptions for triggered rules.

Constitution Principle 7: MVP is explainable validation, not a full tax engine.
Constitution Principle 6: Draft-first — only validate draft documents.
Constitution Principle 4: No parallel ledger.
"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class TaxValidationMixin(models.AbstractModel):
    """Mixin that adds pre-posting tax validation to a document model.

    Inherit this mixin to enable rule-based tax validation:

        _inherit = ["tax.validation.mixin"]

    The mixin provides:
    - action_validate_taxes(): run all applicable rules, create exceptions
    - _get_applicable_rules(): fetch active rules for this document type
    """

    _name = "tax.validation.mixin"
    _description = "Tax Validation Mixin"

    # Subclasses must declare these fields or map their equivalents.
    # account.move already has move_type; expose a normalized applies_to value.

    def _get_validation_applies_to(self):
        """Return the applies_to key for rule filtering.

        Override in subclasses if the document type mapping differs.
        Default maps account.move move_type to the rule applies_to selection.
        """
        self.ensure_one()
        move_type = getattr(self, "move_type", None)
        if move_type in ("out_invoice", "out_refund", "out_receipt"):
            return "invoice"
        if move_type in ("in_invoice", "in_refund", "in_receipt"):
            return "bill"
        return "all"

    def _get_applicable_rules(self):
        """Return active tax validation rules applicable to this document.

        Filters by:
        - is_active = True
        - applies_to == this document's type OR applies_to == 'all'
        - country_id matches company country OR no country restriction
        """
        self.ensure_one()
        applies_to = self._get_validation_applies_to()
        company_country = self.env.company.country_id

        domain = [
            ("is_active", "=", True),
            "|",
            ("applies_to", "=", applies_to),
            ("applies_to", "=", "all"),
        ]
        rules = self.env["tax.validation.rule"].search(domain)

        # Further filter by country: rule has no country, or matches company country
        applicable = rules.filtered(
            lambda r: not r.country_id or r.country_id == company_country
        )
        return applicable.sorted("sequence")

    def action_validate_taxes(self):
        """Run all applicable tax validation rules against this document.

        Creates tax.exception records for each triggered rule.
        Returns a dict summarising how many exceptions were created.

        This is the entry point called before action_post().
        """
        self.ensure_one()
        rules = self._get_applicable_rules()
        exceptions_created = 0

        for rule in rules:
            triggered, rationale, inputs_summary, confidence = self._evaluate_rule(rule)
            if triggered:
                # Map rule type to exception type
                exc_type_map = {
                    "rate_check": "rate_mismatch",
                    "jurisdiction_match": "wrong_jurisdiction",
                    "exemption_verify": "missing_tax",
                    "withholding_check": "withholding_error",
                    "document_completeness": "missing_document",
                }
                exc_type = exc_type_map.get(rule.rule_type, "other")

                # Check for existing open exception from the same rule on same record
                existing = self.env["tax.exception"].search([
                    ("source_model", "=", self._name),
                    ("source_id", "=", self.id),
                    ("rule_id", "=", rule.id),
                    ("state", "in", ("detected", "under_review", "escalated")),
                ], limit=1)

                if not existing:
                    self.env["tax.exception"].create({
                        "source_model": self._name,
                        "source_id": self.id,
                        "rule_id": rule.id,
                        "exception_type": exc_type,
                        "state": "detected",
                        "rationale": rationale,
                        "inputs_summary": inputs_summary,
                        "confidence": confidence,
                    })
                    exceptions_created += 1
                    _logger.info(
                        "TaxIntelligence: Exception created for rule '%s' on %s#%s",
                        rule.name,
                        self._name,
                        self.id,
                    )

        return {
            "rules_evaluated": len(rules),
            "exceptions_created": exceptions_created,
        }

    def _evaluate_rule(self, rule):
        """Evaluate a single tax validation rule against this document.

        Returns a 4-tuple:
            (triggered: bool, rationale: str, inputs_summary: str, confidence: float)

        MVP implementation: performs deterministic checks based on rule_type.
        Override in subclasses to add domain-specific logic.
        """
        self.ensure_one()
        triggered = False
        rationale = ""
        inputs_summary = ""
        confidence = 1.0

        if rule.rule_type == "rate_check":
            triggered, rationale, inputs_summary, confidence = self._check_tax_rates(rule)
        elif rule.rule_type == "withholding_check":
            triggered, rationale, inputs_summary, confidence = self._check_withholding(rule)
        elif rule.rule_type == "document_completeness":
            triggered, rationale, inputs_summary, confidence = self._check_document_completeness(rule)
        # jurisdiction_match and exemption_verify are connector-owned (deferred)
        # They never trigger in MVP without an external connector.

        return triggered, rationale, inputs_summary, confidence

    def _check_tax_rates(self, rule):
        """Check that tax lines use expected rates from the applicable tax group."""
        lines = getattr(self, "invoice_line_ids", self.env["account.move.line"])
        if not lines:
            return False, "", "", 1.0

        # Check for lines with no taxes where taxes are expected
        lines_without_tax = lines.filtered(
            lambda l: not l.tax_ids and l.display_type not in ("line_section", "line_note")
        )
        if lines_without_tax:
            rationale = (
                f"Rule '{rule.name}': {len(lines_without_tax)} line(s) have no tax applied. "
                "All taxable lines should have applicable taxes configured."
            )
            inputs_summary = (
                f"Lines checked: {len(lines)}. "
                f"Lines without tax: {len(lines_without_tax)}. "
                f"Policy: {rule.policy_reference or 'N/A'}."
            )
            return True, rationale, inputs_summary, 0.95

        # If a specific tax group is configured, verify all taxes belong to it
        if rule.tax_group_id:
            mismatched = lines.filtered(
                lambda l: l.tax_ids and not any(
                    t.tax_group_id == rule.tax_group_id for t in l.tax_ids
                )
            )
            if mismatched:
                rationale = (
                    f"Rule '{rule.name}': {len(mismatched)} line(s) have taxes not in "
                    f"expected group '{rule.tax_group_id.name}'."
                )
                inputs_summary = (
                    f"Expected tax group: {rule.tax_group_id.name}. "
                    f"Lines with mismatched tax group: {len(mismatched)}."
                )
                return True, rationale, inputs_summary, 0.9

        return False, "", "", 1.0

    def _check_withholding(self, rule):
        """Check withholding tax presence for applicable vendor bills."""
        move_type = getattr(self, "move_type", "")
        if move_type not in ("in_invoice", "in_refund"):
            return False, "", "", 1.0

        lines = getattr(self, "invoice_line_ids", self.env["account.move.line"])
        # Look for withholding taxes: convention is tax group named with "Withholding"
        has_withholding = any(
            any("withhold" in (t.tax_group_id.name or "").lower() for t in l.tax_ids)
            for l in lines
            if l.display_type not in ("line_section", "line_note")
        )
        if not has_withholding and lines:
            rationale = (
                f"Rule '{rule.name}': No withholding tax found on vendor bill. "
                "BIR regulations require withholding tax on applicable vendor payments."
            )
            inputs_summary = (
                f"Document type: {move_type}. "
                f"Lines checked: {len(lines)}. "
                f"Withholding tax found: False. "
                f"Policy: {rule.policy_reference or 'N/A'}."
            )
            return True, rationale, inputs_summary, 0.85
        return False, "", "", 1.0

    def _check_document_completeness(self, rule):
        """Check that required supporting documents are attached."""
        # For MVP: check that at least one attachment exists for vendor bills
        move_type = getattr(self, "move_type", "")
        if move_type not in ("in_invoice", "in_refund"):
            return False, "", "", 1.0

        attachments = self.env["ir.attachment"].search_count([
            ("res_model", "=", self._name),
            ("res_id", "=", self.id),
        ])
        if attachments == 0:
            rationale = (
                f"Rule '{rule.name}': No supporting documents attached. "
                "Vendor bills require at least one attached document for BIR compliance."
            )
            inputs_summary = (
                f"Document type: {move_type}. Attachments found: 0. "
                f"Policy: {rule.policy_reference or 'N/A'}."
            )
            return True, rationale, inputs_summary, 1.0
        return False, "", "", 1.0

    @api.model
    def _get_open_exceptions(self, source_model, source_id):
        """Return open (blocking) exceptions for a source record."""
        return self.env["tax.exception"].search([
            ("source_model", "=", source_model),
            ("source_id", "=", source_id),
            ("state", "in", ("detected", "under_review", "escalated")),
            ("severity", "=", "blocking"),
        ])
