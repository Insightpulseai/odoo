# -*- coding: utf-8 -*-
"""
OCR Gateway Service.

Abstract service for connecting to external OCR providers.
Handles receipt image processing and data extraction.
"""
import base64
import json
import logging
import uuid
from datetime import datetime

from odoo import api, models

_logger = logging.getLogger(__name__)


class IpaiOcrGatewayService(models.AbstractModel):
    """
    OCR Gateway Service.

    Provides methods to interact with external OCR services
    for receipt digitization. Supports multiple providers
    through configuration.

    Supported Providers:
    - mock: Simulated OCR for testing/development
    - azure: Azure Form Recognizer
    - google: Google Cloud Vision
    """

    _name = "ipai.ocr.gateway.service"
    _description = "IPAI OCR Gateway Service"

    @api.model
    def get_ocr_provider(self):
        """Get configured OCR provider from system parameters"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ocr_expense.provider", "mock")
        )

    @api.model
    def get_ocr_api_key(self):
        """Get OCR API key from system parameters"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ocr_expense.api_key", "")
        )

    @api.model
    def get_ocr_endpoint(self):
        """Get OCR API endpoint from system parameters"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ocr_expense.endpoint", "")
        )

    @api.model
    def process_receipt(self, expense):
        """
        Process a receipt image through OCR.

        Args:
            expense: hr.expense record with receipt_image field

        Returns:
            dict: {
                'success': bool,
                'transaction_id': str,
                'amount': float,
                'vendor': str,
                'date': str (YYYY-MM-DD),
                'confidence': float (0-100),
                'raw_text': str,
                'error': str (if failed)
            }
        """
        provider = self.get_ocr_provider()

        if provider == "mock":
            return self._process_mock(expense)
        elif provider == "azure":
            return self._process_azure(expense)
        elif provider == "google":
            return self._process_google(expense)
        else:
            return {
                "success": False,
                "error": f"Unknown OCR provider: {provider}",
            }

    @api.model
    def _process_mock(self, expense):
        """
        Mock OCR processing for development/testing.

        Returns simulated extraction data based on the image.
        Useful for testing the workflow without external API calls.
        """
        _logger.info("Processing receipt with mock OCR provider")

        # Generate a unique transaction ID
        transaction_id = f"MOCK-{uuid.uuid4().hex[:12].upper()}"

        # Simulate processing delay would happen in real service
        # For mock, we return immediate results

        # Generate mock data based on expense
        mock_amount = expense.total_amount_currency or 1250.00
        mock_vendor = "Sample Vendor Inc."
        mock_date = expense.date or datetime.now().date()

        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": mock_amount,
            "vendor": mock_vendor,
            "date": mock_date.isoformat() if hasattr(mock_date, "isoformat") else str(mock_date),
            "confidence": 87.5,
            "raw_text": f"""
SAMPLE RECEIPT
==============
{mock_vendor}
123 Business Street
Metro Manila, Philippines

Date: {mock_date}
Receipt #: {transaction_id}

Items:
- Service/Product    PHP {mock_amount:,.2f}

TOTAL: PHP {mock_amount:,.2f}

Thank you for your business!
            """.strip(),
        }

    @api.model
    def _process_azure(self, expense):
        """
        Process receipt using Azure Form Recognizer.

        Requires:
        - ipai_ocr_expense.api_key: Azure API key
        - ipai_ocr_expense.endpoint: Azure Form Recognizer endpoint
        """
        import requests

        api_key = self.get_ocr_api_key()
        endpoint = self.get_ocr_endpoint()

        if not api_key or not endpoint:
            return {
                "success": False,
                "error": "Azure OCR not configured. Set API key and endpoint.",
            }

        try:
            # Decode the image
            image_data = base64.b64decode(expense.receipt_image)

            # Call Azure Form Recognizer
            url = f"{endpoint}/formrecognizer/documentModels/prebuilt-receipt:analyze?api-version=2023-07-31"
            headers = {
                "Content-Type": "application/octet-stream",
                "Ocp-Apim-Subscription-Key": api_key,
            }

            response = requests.post(url, headers=headers, data=image_data, timeout=30)

            if response.status_code == 202:
                # Get operation location for async result
                operation_url = response.headers.get("Operation-Location")
                # In production, you'd poll this URL for results
                # For now, return pending status
                return {
                    "success": True,
                    "transaction_id": operation_url.split("/")[-1] if operation_url else "AZURE-PENDING",
                    "amount": 0.0,
                    "vendor": "",
                    "date": None,
                    "confidence": 0.0,
                    "raw_text": "Processing...",
                }
            else:
                return {
                    "success": False,
                    "error": f"Azure API error: {response.status_code}",
                }

        except Exception as e:
            _logger.error("Azure OCR error: %s", str(e))
            return {
                "success": False,
                "error": str(e),
            }

    @api.model
    def _process_google(self, expense):
        """
        Process receipt using Google Cloud Vision.

        Requires:
        - ipai_ocr_expense.api_key: Google Cloud API key
        """
        import requests

        api_key = self.get_ocr_api_key()

        if not api_key:
            return {
                "success": False,
                "error": "Google OCR not configured. Set API key.",
            }

        try:
            # Prepare the request
            url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"

            request_body = {
                "requests": [
                    {
                        "image": {"content": expense.receipt_image.decode() if isinstance(expense.receipt_image, bytes) else expense.receipt_image},
                        "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                    }
                ]
            }

            response = requests.post(url, json=request_body, timeout=30)
            result = response.json()

            if "responses" in result and result["responses"]:
                text_annotation = result["responses"][0].get("fullTextAnnotation", {})
                raw_text = text_annotation.get("text", "")

                # Parse extracted text for receipt data
                parsed = self._parse_receipt_text(raw_text)

                return {
                    "success": True,
                    "transaction_id": f"GCLOUD-{uuid.uuid4().hex[:12].upper()}",
                    "amount": parsed.get("amount", 0.0),
                    "vendor": parsed.get("vendor", ""),
                    "date": parsed.get("date"),
                    "confidence": parsed.get("confidence", 75.0),
                    "raw_text": raw_text,
                }
            else:
                return {
                    "success": False,
                    "error": "No text detected in image",
                }

        except Exception as e:
            _logger.error("Google OCR error: %s", str(e))
            return {
                "success": False,
                "error": str(e),
            }

    @api.model
    def _parse_receipt_text(self, raw_text):
        """
        Parse raw OCR text to extract receipt data.

        Basic extraction logic for common receipt formats.
        Can be enhanced with ML models for better accuracy.
        """
        import re

        result = {
            "amount": 0.0,
            "vendor": "",
            "date": None,
            "confidence": 50.0,
        }

        lines = raw_text.split("\n")

        # Try to extract vendor (usually first non-empty line)
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 3:
                result["vendor"] = line
                break

        # Try to extract amount (look for TOTAL patterns)
        amount_patterns = [
            r"TOTAL[:\s]*(?:PHP|₱)?\s*([\d,]+\.?\d*)",
            r"AMOUNT[:\s]*(?:PHP|₱)?\s*([\d,]+\.?\d*)",
            r"(?:PHP|₱)\s*([\d,]+\.?\d*)",
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(",", "")
                try:
                    result["amount"] = float(amount_str)
                    result["confidence"] += 20
                    break
                except ValueError:
                    pass

        # Try to extract date
        date_patterns = [
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{4}[/-]\d{1,2}[/-]\d{1,2})",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, raw_text)
            if match:
                date_str = match.group(1)
                # Try to parse date
                for fmt in ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y"]:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        result["date"] = parsed_date.date().isoformat()
                        result["confidence"] += 15
                        break
                    except ValueError:
                        continue
                if result["date"]:
                    break

        # Cap confidence at 100
        result["confidence"] = min(result["confidence"], 100.0)

        return result
