# -*- coding: utf-8 -*-
"""
IDP Model Version.

Versioned prompt and model configurations for LLM extraction.
Enables A/B testing, rollback, and reproducibility.
"""
import hashlib
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IdpModelVersion(models.Model):
    """
    IDP Model Version Configuration.

    Stores versioned extraction configurations including:
    - LLM model selection
    - Prompt templates
    - JSON schemas for extraction
    - Post-processing rules

    Each extraction logs which version was used for reproducibility.
    Supports A/B testing and rollback via active flag.

    Attributes:
        _name: idp.model.version
        _description: IDP Model Version
    """

    _name = "idp.model.version"
    _description = "IDP Model Version"
    _order = "create_date desc"

    # Core identification
    name = fields.Char(
        string="Version Name",
        required=True,
        help="Human-readable version name (e.g., 'invoice-v2.1')",
    )
    version_code = fields.Char(
        string="Version Code",
        compute="_compute_version_code",
        store=True,
        help="Auto-generated version code based on content hash",
    )
    description = fields.Text(
        string="Description",
        help="What changed in this version",
    )

    # Document type targeting
    doc_type = fields.Selection(
        [
            ("invoice", "Invoice"),
            ("receipt", "Receipt"),
            ("purchase_order", "Purchase Order"),
            ("delivery_note", "Delivery Note"),
            ("all", "All Document Types"),
        ],
        string="Document Type",
        default="all",
        required=True,
    )

    # LLM configuration
    llm_model = fields.Selection(
        [
            ("claude-3-sonnet", "Claude 3 Sonnet"),
            ("claude-3-opus", "Claude 3 Opus"),
            ("claude-3-haiku", "Claude 3 Haiku"),
            ("gpt-4", "GPT-4"),
            ("gpt-4-turbo", "GPT-4 Turbo"),
            ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
        ],
        string="LLM Model",
        default="claude-3-sonnet",
        required=True,
    )
    temperature = fields.Float(
        string="Temperature",
        default=0.0,
        help="LLM temperature (0.0 = deterministic)",
    )
    max_tokens = fields.Integer(
        string="Max Tokens",
        default=4096,
    )

    # Prompt configuration
    system_prompt = fields.Text(
        string="System Prompt",
        required=True,
        default="""You are an enterprise-grade Intelligent Document Processing (IDP) extraction engine.

Your job:
1. Accept raw OCR text.
2. Identify the document type.
3. Extract only the fields defined in the target schema.
4. Normalize all values.
5. Return strictly valid JSON.
6. Assign a confidence score from 0.00 to 1.00.

Rules:
- Never hallucinate missing values.
- If a value is missing, return null.
- Dates must be ISO-8601 (YYYY-MM-DD).
- Currency must be ISO-4217 codes.
- Remove currency symbols from numeric fields.
- Line items must be arrays.
- Totals must be numeric, not formatted strings.
- All field names must match the schema exactly.
- Do not add extra commentary.

You must return:
{
  "doc_type": "...",
  "extracted_data": {...},
  "confidence": 0.00
}""",
    )
    extraction_prompt_template = fields.Text(
        string="Extraction Prompt Template",
        default="""Document OCR Text:
{{OCR_TEXT}}

Target Schema:
{{SCHEMA_JSON}}

Extract now.""",
        help="Template with {{OCR_TEXT}} and {{SCHEMA_JSON}} placeholders",
    )

    # Schema definition
    extraction_schema = fields.Text(
        string="Extraction Schema (JSON)",
        required=True,
        default="""{
  "vendor_name": "string|null",
  "vendor_address": "string|null",
  "invoice_number": "string|null",
  "invoice_date": "YYYY-MM-DD|null",
  "due_date": "YYYY-MM-DD|null",
  "currency": "ISO_4217|null",
  "line_items": [
    {
      "description": "string|null",
      "quantity": "number|null",
      "unit_price": "number|null",
      "amount": "number|null"
    }
  ],
  "subtotal": "number|null",
  "tax": "number|null",
  "total": "number|null"
}""",
    )

    # Post-processing rules (JSON)
    postprocessing_rules = fields.Text(
        string="Post-processing Rules (JSON)",
        default="[]",
        help="List of post-processing rules to apply after extraction",
    )

    # Validation rules reference
    validation_rule_ids = fields.Many2many(
        "idp.validation.rule",
        string="Validation Rules",
        help="Validation rules to apply to extractions using this version",
    )

    # Status and metrics
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Only active versions are used for processing",
    )
    is_default = fields.Boolean(
        string="Is Default",
        default=False,
        help="Default version for the document type",
    )

    # Usage statistics
    usage_count = fields.Integer(
        string="Usage Count",
        compute="_compute_usage_count",
    )
    success_rate = fields.Float(
        string="Success Rate (%)",
        compute="_compute_success_rate",
    )
    avg_confidence = fields.Float(
        string="Avg Confidence",
        compute="_compute_avg_confidence",
    )

    @api.depends("system_prompt", "extraction_prompt_template", "extraction_schema")
    def _compute_version_code(self):
        """Generate version code from content hash."""
        for record in self:
            content = (
                f"{record.system_prompt or ''}"
                f"{record.extraction_prompt_template or ''}"
                f"{record.extraction_schema or ''}"
            )
            hash_digest = hashlib.md5(content.encode()).hexdigest()[:8]
            record.version_code = f"{record.doc_type or 'all'}-{hash_digest}"

    def _compute_usage_count(self):
        """Count extractions using this version."""
        Extraction = self.env["idp.extraction"]
        for record in self:
            record.usage_count = Extraction.search_count(
                [("model_version_id", "=", record.id)]
            )

    def _compute_success_rate(self):
        """Calculate success rate for this version."""
        Extraction = self.env["idp.extraction"]
        for record in self:
            total = Extraction.search_count([("model_version_id", "=", record.id)])
            if total == 0:
                record.success_rate = 0.0
            else:
                success = Extraction.search_count(
                    [
                        ("model_version_id", "=", record.id),
                        ("validation_status", "=", "pass"),
                    ]
                )
                record.success_rate = (success / total) * 100

    def _compute_avg_confidence(self):
        """Calculate average confidence for this version."""
        self.env.cr.execute(
            """
            SELECT model_version_id, AVG(confidence)
            FROM idp_extraction
            WHERE model_version_id IN %s AND confidence > 0
            GROUP BY model_version_id
        """,
            (tuple(self.ids) or (0,),),
        )
        results = dict(self.env.cr.fetchall())
        for record in self:
            record.avg_confidence = results.get(record.id, 0.0)

    def get_schema_dict(self):
        """
        Parse and return the extraction schema as a dict.

        Returns:
            dict: Parsed JSON schema
        """
        self.ensure_one()
        try:
            return json.loads(self.extraction_schema)
        except json.JSONDecodeError:
            _logger.error(
                "Invalid JSON schema for model version %s",
                self.id,
            )
            return {}

    def render_prompt(self, ocr_text):
        """
        Render the extraction prompt with OCR text.

        Args:
            ocr_text: The raw OCR text to include

        Returns:
            str: Rendered prompt ready for LLM
        """
        self.ensure_one()
        prompt = self.extraction_prompt_template
        prompt = prompt.replace("{{OCR_TEXT}}", ocr_text or "")
        prompt = prompt.replace("{{SCHEMA_JSON}}", self.extraction_schema or "{}")
        return prompt

    @api.model
    def get_default_version(self, doc_type="all"):
        """
        Get the default active version for a document type.

        Args:
            doc_type: Document type to match

        Returns:
            idp.model.version or False
        """
        # First try to find a default for the specific doc_type
        version = self.search(
            [
                ("active", "=", True),
                ("is_default", "=", True),
                ("doc_type", "=", doc_type),
            ],
            limit=1,
        )
        if version:
            return version

        # Fall back to 'all' doc_type default
        version = self.search(
            [
                ("active", "=", True),
                ("is_default", "=", True),
                ("doc_type", "=", "all"),
            ],
            limit=1,
        )
        if version:
            return version

        # Last resort: any active version
        return self.search(
            [("active", "=", True)],
            order="create_date desc",
            limit=1,
        )

    def action_set_as_default(self):
        """Set this version as the default for its document type."""
        self.ensure_one()
        # Unset other defaults for same doc_type
        self.search(
            [
                ("doc_type", "in", [self.doc_type, "all"]),
                ("is_default", "=", True),
                ("id", "!=", self.id),
            ]
        ).write({"is_default": False})
        self.write({"is_default": True})
