# -*- coding: utf-8 -*-
"""Azure Document Intelligence service for invoice/receipt extraction.

Replaces Odoo IAP document digitization.
Resource: docai-ipai-dev (Southeast Asia)
Auth: API key from Key Vault (MI-preferred path via ACA env var).
"""
import base64
import json
import logging
import time

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# DocAI API version
DOCAI_API_VERSION = "2024-11-30"

# Confidence thresholds
AUTO_CREATE_THRESHOLD = 0.90
REVIEW_THRESHOLD = 0.70


class DocIntelService(models.AbstractModel):
    _name = "ipai.doc.intel.service"
    _description = "Azure Document Intelligence Service"

    @api.model
    def _get_config(self):
        """Get DocAI configuration from ir.config_parameter."""
        ICP = self.env["ir.config_parameter"].sudo()
        endpoint = ICP.get_param("ipai_doc_intel.endpoint", "")
        api_key = ICP.get_param("ipai_doc_intel.api_key", "")
        if not endpoint or not api_key:
            raise UserError(
                "Document Intelligence not configured. "
                "Set ipai_doc_intel.endpoint and ipai_doc_intel.api_key "
                "in System Parameters."
            )
        return {"endpoint": endpoint.rstrip("/"), "api_key": api_key}

    @api.model
    def analyze_invoice(self, file_content, content_type="application/pdf"):
        """Analyze an invoice document and return extracted fields.

        Args:
            file_content: bytes of the PDF/image file
            content_type: MIME type (application/pdf, image/jpeg, image/png)

        Returns:
            dict with extracted fields + confidence scores
        """
        config = self._get_config()
        url = (
            f"{config['endpoint']}/documentintelligence/documentModels/"
            f"prebuilt-invoice:analyze?api-version={DOCAI_API_VERSION}"
        )
        headers = {
            "Ocp-Apim-Subscription-Key": config["api_key"],
            "Content-Type": content_type,
        }

        # Submit analysis
        _logger.info("Submitting invoice to Document Intelligence...")
        resp = requests.post(url, headers=headers, data=file_content, timeout=30)
        if resp.status_code != 202:
            raise UserError(
                f"Document Intelligence error: {resp.status_code} — {resp.text[:200]}"
            )

        # Get operation URL
        operation_url = resp.headers.get("Operation-Location")
        if not operation_url:
            raise UserError("No operation URL returned from Document Intelligence.")

        # Poll for result (max 60 seconds)
        poll_headers = {"Ocp-Apim-Subscription-Key": config["api_key"]}
        for _ in range(12):
            time.sleep(5)
            poll_resp = requests.get(operation_url, headers=poll_headers, timeout=15)
            result = poll_resp.json()
            status = result.get("status", "unknown")

            if status == "succeeded":
                return self._parse_invoice_result(result)
            elif status in ("failed", "canceled"):
                error_msg = result.get("error", {}).get("message", "Unknown error")
                raise UserError(f"Document Intelligence failed: {error_msg}")

        raise UserError("Document Intelligence timeout — analysis took >60 seconds.")

    @api.model
    def _parse_invoice_result(self, result):
        """Parse DocAI result into a clean field dict."""
        analyze_result = result.get("analyzeResult", {})
        documents = analyze_result.get("documents", [])
        if not documents:
            return {"fields": {}, "confidence": 0, "page_count": 0}

        doc = documents[0]
        raw_fields = doc.get("fields", {})
        parsed = {}

        # Map DocAI fields to Odoo-friendly names
        field_map = {
            "VendorName": "vendor_name",
            "VendorAddress": "vendor_address",
            "VendorTaxId": "vendor_tax_id",
            "CustomerName": "customer_name",
            "CustomerAddress": "customer_address",
            "CustomerId": "customer_id",
            "InvoiceId": "invoice_ref",
            "InvoiceDate": "invoice_date",
            "DueDate": "due_date",
            "PurchaseOrder": "purchase_order",
            "SubTotal": "subtotal",
            "TotalTax": "total_tax",
            "InvoiceTotal": "invoice_total",
            "AmountDue": "amount_due",
            "PreviousUnpaidBalance": "previous_balance",
        }

        confidences = []
        for docai_name, odoo_name in field_map.items():
            field = raw_fields.get(docai_name)
            if field:
                value = self._extract_field_value(field)
                confidence = field.get("confidence", 0)
                parsed[odoo_name] = {
                    "value": value,
                    "confidence": confidence,
                }
                confidences.append(confidence)

        # Extract line items
        items_field = raw_fields.get("Items")
        if items_field and items_field.get("type") == "array":
            items = []
            for item in items_field.get("valueArray", []):
                item_fields = item.get("valueObject", {})
                items.append({
                    "description": self._extract_field_value(
                        item_fields.get("Description", {})
                    ),
                    "quantity": self._extract_field_value(
                        item_fields.get("Quantity", {})
                    ),
                    "unit_price": self._extract_field_value(
                        item_fields.get("UnitPrice", {})
                    ),
                    "amount": self._extract_field_value(
                        item_fields.get("Amount", {})
                    ),
                    "tax": self._extract_field_value(
                        item_fields.get("Tax", {})
                    ),
                })
            parsed["line_items"] = items

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        page_count = len(analyze_result.get("pages", []))

        return {
            "fields": parsed,
            "avg_confidence": round(avg_confidence, 3),
            "page_count": page_count,
            "auto_create": avg_confidence >= AUTO_CREATE_THRESHOLD,
            "needs_review": avg_confidence < REVIEW_THRESHOLD,
        }

    @staticmethod
    def _extract_field_value(field):
        """Extract the value from a DocAI field based on its type."""
        if not field:
            return None
        field_type = field.get("type", "string")
        if field_type == "currency":
            currency = field.get("valueCurrency", {})
            return currency.get("amount")
        elif field_type == "date":
            return field.get("valueDate")
        elif field_type == "number":
            return field.get("valueNumber")
        elif field_type == "integer":
            return field.get("valueInteger")
        else:
            return field.get("valueString", field.get("content"))
