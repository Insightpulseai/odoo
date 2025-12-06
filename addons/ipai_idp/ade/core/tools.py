# -*- coding: utf-8 -*-
"""
ADE Tools - Adapters for IDP Services.

Provides a unified interface for the ADE orchestrator to call
underlying IDP services (LLM, OCR, parser, validator).
"""
import json
import logging
from typing import Any, Dict, Optional

_logger = logging.getLogger(__name__)


class ADETools:
    """
    Tool adapters for ADE orchestrator.

    Wraps Odoo IDP services to provide a clean interface for
    pipeline steps to call.
    """

    def __init__(self, env, pipeline_id: str = "invoice_basic_v1"):
        """
        Initialize ADE tools with Odoo environment.

        Args:
            env: Odoo environment (self.env from a model)
            pipeline_id: Current pipeline ID for prompt resolution
        """
        self.env = env
        self.pipeline_id = pipeline_id

    def call_llm(self, prompt_ref: str, **kwargs) -> Dict[str, Any]:
        """
        Call the LLM via the gateway with the given prompt reference.

        Args:
            prompt_ref: Reference to the prompt (e.g., 'invoice_extraction')
            **kwargs: Context variables for prompt rendering

        Returns:
            dict: Parsed JSON response from LLM
        """
        kwargs["pipeline_id"] = self.pipeline_id
        try:
            gateway = self.env["idp.llm.gateway"]
            result = gateway.run_prompt(prompt_ref, kwargs)
            return result
        except Exception as e:
            _logger.exception("LLM call failed for prompt_ref=%s", prompt_ref)
            raise

    def parse_field(self, parser: str, value: Any) -> Any:
        """
        Parse/normalize a field value using the parser service.

        Args:
            parser: Parser name (e.g., 'normalize_date', 'parse_amount')
            value: Value to parse

        Returns:
            Parsed/normalized value
        """
        if value is None:
            return None

        parser_service = self.env["idp.service.parser"]

        parser_map = {
            "normalize_date": parser_service.normalize_date,
            "parse_amount": lambda v: parser_service.parse_amount(str(v)),
            "detect_currency": parser_service.detect_currency,
        }

        parser_func = parser_map.get(parser)
        if not parser_func:
            _logger.warning("Unknown parser: %s", parser)
            return value

        try:
            result = parser_func(str(value))
            # Handle tuple returns from parse_amount
            if isinstance(result, tuple):
                return result[0]  # Return just the amount
            return result
        except Exception as e:
            _logger.warning("Parser %s failed for value %s: %s", parser, value, e)
            return value

    def validate(self, rule_set: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fields against a rule set.

        Args:
            rule_set: Name of the validation rule set (e.g., 'invoice_default')
            fields: Field values to validate

        Returns:
            dict: {'status': 'pass'|'fail'|'warning', 'errors': [...]}
        """
        try:
            validator = self.env["idp.service.validator"]
            # Map rule_set name to doc_type
            # e.g., "invoice_default" -> "invoice", "receipt_default" -> "receipt"
            doc_type = self._rule_set_to_doc_type(rule_set)
            result = validator.validate_data(fields, doc_type)
            return result
        except Exception as e:
            _logger.exception("Validation failed for rule_set=%s", rule_set)
            return {
                "status": "fail",
                "errors": [f"Validation error: {str(e)}"],
            }

    def _rule_set_to_doc_type(self, rule_set: str) -> str:
        """
        Map rule set name to document type.

        Args:
            rule_set: Rule set name (e.g., 'invoice_default')

        Returns:
            str: Document type for rule filtering
        """
        rule_set_lower = rule_set.lower()
        if "invoice" in rule_set_lower:
            return "invoice"
        elif "receipt" in rule_set_lower:
            return "receipt"
        elif "po" in rule_set_lower or "purchase" in rule_set_lower:
            return "purchase_order"
        elif "delivery" in rule_set_lower:
            return "delivery_note"
        return "all"

    def get_current_fields(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract current field values from state for correction prompts.

        Args:
            state: Current orchestrator state

        Returns:
            dict: Current extracted fields
        """
        # Filter out internal state variables
        internal_keys = {
            "ocr_text",
            "doc_id",
            "pipeline_id",
            "validation_status",
            "validation_errors",
            "final_status",
            "final_errors",
            "doc_type_pred",
            "doc_type_confidence",
        }
        return {k: v for k, v in state.items() if k not in internal_keys}
