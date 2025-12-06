# -*- coding: utf-8 -*-
"""
IDP LLM Gateway.

Central gateway for resolving prompts and calling LLMs.
Maps prompt_ref identifiers to model version fields and handles rendering.
"""
import json
import logging
import re
from typing import Any, Dict

from odoo import api, models

_logger = logging.getLogger(__name__)

# Map prompt references to model version field names
PROMPT_FIELD_MAP = {
    # Classification
    "classify_document": "prompt_classify",
    # Invoice prompts
    "invoice_extraction": "prompt_extract",
    "invoice_correction": "prompt_correction",
    # Receipt prompts
    "receipt_extraction": "prompt_extract_receipt",
    "receipt_correction": "prompt_correction_receipt",
    # PO prompts
    "po_extraction": "prompt_extract_po",
    "po_correction": "prompt_correction_po",
}

# Default prompts when model version doesn't have a specific one
DEFAULT_PROMPTS = {
    "prompt_classify": """You are a document classifier. Analyze the OCR text and determine the document type.

Possible types: "invoice", "receipt", "purchase_order", "delivery_note", "other".

Return ONLY a JSON object with:
{
  "doc_type_pred": "<one of invoice|receipt|purchase_order|delivery_note|other>",
  "doc_type_confidence": <float between 0 and 1>
}

OCR_TEXT:
{{ ocr_text }}""",

    "prompt_extract": """You are an extraction engine for ACCOUNTS PAYABLE invoices.

Extract key invoice fields and return clean, machine-readable JSON.

Return JSON with this structure:
{
  "vendor_name": "string or null",
  "vendor_address": "string or null",
  "invoice_number": "string or null",
  "invoice_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "total_amount": number or null,
  "subtotal_amount": number or null,
  "tax_amount": number or null,
  "currency": "3-letter ISO or null",
  "po_number": "string or null",
  "line_items": [
    {"description": "string", "quantity": number, "unit_price": number, "line_total": number}
  ],
  "overall_confidence": number between 0 and 1
}

Guidelines:
- Use currency symbol context to guess currency if not explicit.
- Prefer totals labelled as "Total", "Invoice Total", or "Amount Due".
- If multiple totals exist, pick the final invoice total.

OCR_TEXT:
{{ ocr_text }}""",

    "prompt_correction": """You are a correction engine for extracted invoice data.

You are given:
1) Original OCR text
2) current_fields: JSON with current extracted fields
3) validation_errors: list of what is wrong

Your job:
- Fix only what is necessary to resolve validation_errors
- Keep all fields when possible; correct values rather than remove them
- If you cannot infer a field confidently, leave it as null

Return the same JSON structure as the extraction step.

OCR_TEXT:
{{ ocr_text }}

CURRENT_FIELDS:
{{ current_fields }}

VALIDATION_ERRORS:
{{ validation_errors }}""",

    "prompt_extract_receipt": """You are an extraction engine for retail RECEIPTS.

Extract key receipt fields and return clean, machine-readable JSON.

Return JSON with this structure:
{
  "merchant_name": "string or null",
  "merchant_address": "string or null",
  "receipt_number": "string or null",
  "transaction_date": "YYYY-MM-DD or null",
  "transaction_time": "HH:MM or null",
  "total_amount": number or null,
  "subtotal_amount": number or null,
  "tax_amount": number or null,
  "currency": "3-letter ISO or null",
  "payment_method": "cash|card|other or null",
  "card_last4": "string or null",
  "line_items": [
    {"description": "string", "quantity": number, "unit_price": number, "line_total": number}
  ],
  "overall_confidence": number between 0 and 1
}

OCR_TEXT:
{{ ocr_text }}""",

    "prompt_correction_receipt": """You are a correction engine for extracted receipt data.

You are given:
1) Original OCR text
2) current_fields: JSON with current extracted fields
3) validation_errors: list of what is wrong

Fix only what is necessary and return the corrected JSON.

OCR_TEXT:
{{ ocr_text }}

CURRENT_FIELDS:
{{ current_fields }}

VALIDATION_ERRORS:
{{ validation_errors }}""",

    "prompt_extract_po": """You are an extraction engine for PURCHASE ORDERS.

Extract key PO fields and return clean, machine-readable JSON.

Return JSON with this structure:
{
  "supplier_name": "string or null",
  "supplier_address": "string or null",
  "po_number": "string or null",
  "po_date": "YYYY-MM-DD or null",
  "requested_delivery_date": "YYYY-MM-DD or null",
  "total_amount": number or null,
  "subtotal_amount": number or null,
  "tax_amount": number or null,
  "currency": "3-letter ISO or null",
  "buyer_name": "string or null",
  "buyer_reference": "string or null",
  "line_items": [
    {"description": "string", "quantity": number, "unit_price": number, "line_total": number}
  ],
  "overall_confidence": number between 0 and 1
}

OCR_TEXT:
{{ ocr_text }}""",

    "prompt_correction_po": """You are a correction engine for extracted purchase order data.

You are given:
1) Original OCR text
2) current_fields: JSON with current extracted fields
3) validation_errors: list of what is wrong

Fix only what is necessary and return the corrected JSON.

OCR_TEXT:
{{ ocr_text }}

CURRENT_FIELDS:
{{ current_fields }}

VALIDATION_ERRORS:
{{ validation_errors }}""",
}


class IdpLLMGateway(models.AbstractModel):
    """
    IDP LLM Prompt Gateway.

    Resolves prompt references to actual prompt templates from model versions,
    renders them with context variables, and calls the LLM.
    """

    _name = "idp.llm.gateway"
    _description = "IDP LLM Prompt Gateway"

    @api.model
    def run_prompt(self, prompt_ref: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve and execute a prompt.

        Args:
            prompt_ref: Reference to the prompt (e.g., 'invoice_extraction')
            context: Context variables for rendering, including:
                     - pipeline_id: Pipeline identifier
                     - ocr_text: OCR text
                     - current_fields: Current extracted fields (for correction)
                     - validation_errors: Validation errors (for correction)

        Returns:
            dict: Parsed JSON response from LLM

        Raises:
            ValueError: If prompt_ref is unknown or LLM response is invalid
        """
        pipeline_id = context.get("pipeline_id", "invoice_basic_v1")

        # Try to find model version by pipeline code
        ModelVersion = self.env["idp.model.version"]
        mv = ModelVersion.search([("version_code", "ilike", pipeline_id)], limit=1)

        if not mv:
            # Fall back to doc type matching from pipeline_id
            doc_type = self._extract_doc_type_from_pipeline(pipeline_id)
            mv = ModelVersion.get_default_version(doc_type)

        # Get the prompt template
        template = self._get_prompt_template(prompt_ref, mv)
        if not template:
            raise ValueError(f"Unknown prompt_ref: {prompt_ref}")

        # Render the template
        rendered_prompt = self._render_template(template, context)

        # Get LLM configuration from model version
        llm_model = mv.llm_model if mv else "claude-3-sonnet"
        temperature = mv.temperature if mv else 0.0
        max_tokens = mv.max_tokens if mv else 4096
        system_prompt = mv.system_prompt if mv else ""

        # Call the LLM
        raw_response = self._call_llm(
            rendered_prompt,
            system_prompt=system_prompt,
            model=llm_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Parse JSON response
        return self._parse_llm_response(raw_response)

    def _extract_doc_type_from_pipeline(self, pipeline_id: str) -> str:
        """Extract document type from pipeline ID."""
        if "invoice" in pipeline_id:
            return "invoice"
        elif "receipt" in pipeline_id:
            return "receipt"
        elif "po" in pipeline_id or "purchase" in pipeline_id:
            return "purchase_order"
        return "all"

    def _get_prompt_template(self, prompt_ref: str, mv) -> str:
        """
        Get prompt template from model version or defaults.

        Args:
            prompt_ref: Prompt reference
            mv: Model version record or None

        Returns:
            str: Prompt template
        """
        field_name = PROMPT_FIELD_MAP.get(prompt_ref)
        if not field_name:
            # Unknown prompt_ref
            return None

        # Try to get from model version
        if mv and hasattr(mv, field_name):
            template = getattr(mv, field_name)
            if template:
                return template

        # Fall back to defaults
        return DEFAULT_PROMPTS.get(field_name, "")

    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Render a template with context variables.

        Uses {{ var }} syntax for variable substitution.

        Args:
            template: Template string
            context: Context variables

        Returns:
            str: Rendered template
        """
        result = template

        for key, value in context.items():
            placeholder = "{{ " + key + " }}"

            # Convert complex types to JSON strings
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, ensure_ascii=False, indent=2)
            elif value is None:
                value_str = "null"
            else:
                value_str = str(value)

            result = result.replace(placeholder, value_str)

        return result

    def _call_llm(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "claude-3-sonnet",
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> str:
        """
        Call the LLM with the given prompt.

        Delegates to the extractor service's LLM client.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            model: LLM model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            str: Raw LLM response text
        """
        extractor = self.env["idp.service.extractor"]
        return extractor.call_llm_raw(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response as JSON.

        Handles various response formats including markdown code blocks.

        Args:
            response: Raw LLM response

        Returns:
            dict: Parsed JSON

        Raises:
            ValueError: If response cannot be parsed as JSON
        """
        if not response:
            return {}

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", response, re.DOTALL)
        if json_match:
            response = json_match.group(1).strip()

        # Try direct JSON parsing
        try:
            result = json.loads(response)
            if isinstance(result, dict):
                return result
            _logger.warning("LLM response is not a JSON object: %s", type(result))
            return {}
        except json.JSONDecodeError as e:
            _logger.warning("Failed to parse LLM response as JSON: %s", e)
            _logger.debug("Response was: %s", response[:500])
            return {}
