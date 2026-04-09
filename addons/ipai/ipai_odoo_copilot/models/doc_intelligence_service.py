# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import base64
import json
import logging
import time

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)

DOC_INTEL_TIMEOUT = 60
POLL_INTERVAL = 1.0
MAX_POLL_TIME = 120


class DocIntelligenceService(models.AbstractModel):
    """Bridge to Azure AI Document Intelligence for OCR/document extraction.

    Supports:
      - Receipt extraction → hr.expense draft
      - Invoice extraction → account.move (vendor bill) draft
      - General document read → text + layout

    Config parameters:
      - ipai_copilot.doc_intel_endpoint: Document Intelligence endpoint
      - ipai_copilot.doc_intel_key: API key
    """

    _name = "ipai.doc.intelligence.service"
    _description = "Azure Document Intelligence Bridge"

    # --- Settings ---

    def _get_doc_intel_settings(self):
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "endpoint": ICP.get_param("ipai_copilot.doc_intel_endpoint", ""),
            "api_key": ICP.get_param("ipai_copilot.doc_intel_key", ""),
            "api_version": "2024-11-30",
        }

    # --- Analyze Document ---

    @api.model
    def analyze_document(self, attachment_id, model_id="prebuilt-receipt"):
        """Analyze a document attachment using Azure Document Intelligence.

        Args:
            attachment_id: ir.attachment record ID
            model_id: Document Intelligence model to use:
                - prebuilt-receipt (expenses)
                - prebuilt-invoice (vendor bills)
                - prebuilt-read (general OCR)
                - prebuilt-layout (tables + structure)

        Returns:
            dict with extracted fields, or error
        """
        settings = self._get_doc_intel_settings()
        if not settings["endpoint"] or not settings["api_key"]:
            return {"status": "error", "message": "Document Intelligence not configured"}

        # Get attachment data
        attachment = self.env["ir.attachment"].sudo().browse(attachment_id)
        if not attachment.exists():
            return {"status": "error", "message": f"Attachment {attachment_id} not found"}

        file_data = base64.b64decode(attachment.datas)
        content_type = attachment.mimetype or "application/octet-stream"

        endpoint = settings["endpoint"].rstrip("/")
        api_key = settings["api_key"]
        api_version = settings["api_version"]

        # Submit analysis
        analyze_url = (
            f"{endpoint}/documentintelligence/documentModels/{model_id}:analyze"
            f"?api-version={api_version}"
        )
        headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Content-Type": content_type,
        }

        try:
            resp = requests.post(
                analyze_url,
                headers=headers,
                data=file_data,
                timeout=DOC_INTEL_TIMEOUT,
            )
            if resp.status_code != 202:
                return {
                    "status": "error",
                    "message": f"Analysis submission failed: {resp.status_code}",
                    "detail": resp.text[:200],
                }

            # Get operation URL from response headers
            operation_url = resp.headers.get("Operation-Location")
            if not operation_url:
                return {"status": "error", "message": "No operation URL in response"}

        except requests.RequestException as e:
            _logger.error("Document Intelligence submit error: %s", e)
            return {"status": "error", "message": str(e)}

        # Poll for result
        poll_headers = {"Ocp-Apim-Subscription-Key": api_key}
        deadline = time.time() + MAX_POLL_TIME

        while time.time() < deadline:
            time.sleep(POLL_INTERVAL)
            try:
                poll_resp = requests.get(
                    operation_url,
                    headers=poll_headers,
                    timeout=DOC_INTEL_TIMEOUT,
                )
                result = poll_resp.json()
                status = result.get("status")

                if status == "succeeded":
                    return {
                        "status": "success",
                        "model_id": model_id,
                        "result": result.get("analyzeResult", {}),
                    }
                elif status == "failed":
                    return {
                        "status": "error",
                        "message": "Analysis failed",
                        "detail": json.dumps(result.get("error", {})),
                    }
                # else: running/notStarted — continue polling
            except requests.RequestException as e:
                _logger.error("Document Intelligence poll error: %s", e)

        return {"status": "error", "message": "Analysis timed out"}

    # --- Receipt → Expense ---

    @api.model
    def extract_receipt_to_expense(self, attachment_id, employee_id=None):
        """Extract receipt data and create an hr.expense draft.

        Returns: dict with expense_id or error
        """
        result = self.analyze_document(attachment_id, "prebuilt-receipt")
        if result["status"] != "success":
            return result

        # Parse receipt fields
        documents = result["result"].get("documents", [])
        if not documents:
            return {"status": "error", "message": "No receipt detected"}

        receipt = documents[0].get("fields", {})
        merchant = receipt.get("MerchantName", {}).get("valueString", "Receipt")
        total = receipt.get("Total", {}).get("valueNumber", 0.0)
        date_str = receipt.get("TransactionDate", {}).get("valueDate")
        confidence = documents[0].get("confidence", 0.0)

        # Find employee
        if not employee_id:
            employee = self.env["hr.employee"].search(
                [("user_id", "=", self.env.uid)], limit=1
            )
            employee_id = employee.id if employee else None

        if not employee_id:
            return {"status": "error", "message": "No employee record found for current user"}

        # Find default expense product
        product = self.env["product.product"].search(
            [("can_be_expensed", "=", True)], limit=1
        )

        # Create expense draft
        vals = {
            "name": f"Receipt: {merchant}",
            "employee_id": employee_id,
            "total_amount_currency": total,
            "date": date_str or False,
            "product_id": product.id if product else False,
        }

        expense = self.env["hr.expense"].create(vals)

        # Attach the original document
        self.env["ir.attachment"].sudo().browse(attachment_id).write({
            "res_model": "hr.expense",
            "res_id": expense.id,
        })

        return {
            "status": "success",
            "expense_id": expense.id,
            "merchant": merchant,
            "total": total,
            "confidence": confidence,
            "needs_review": confidence < 0.85,
        }

    # --- Invoice → Vendor Bill ---

    @api.model
    def extract_invoice_to_bill(self, attachment_id):
        """Extract invoice data and create an account.move draft (vendor bill).

        Returns: dict with move_id or error
        """
        result = self.analyze_document(attachment_id, "prebuilt-invoice")
        if result["status"] != "success":
            return result

        documents = result["result"].get("documents", [])
        if not documents:
            return {"status": "error", "message": "No invoice detected"}

        invoice = documents[0].get("fields", {})
        vendor_name = invoice.get("VendorName", {}).get("valueString", "Unknown Vendor")
        invoice_total = invoice.get("InvoiceTotal", {}).get("valueNumber", 0.0)
        invoice_date = invoice.get("InvoiceDate", {}).get("valueDate")
        invoice_id_str = invoice.get("InvoiceId", {}).get("valueString", "")
        confidence = documents[0].get("confidence", 0.0)

        # Find or create vendor partner
        partner = self.env["res.partner"].search(
            [("name", "ilike", vendor_name)], limit=1
        )
        if not partner:
            partner = self.env["res.partner"].create({
                "name": vendor_name,
                "supplier_rank": 1,
            })

        # Create vendor bill draft
        move_vals = {
            "move_type": "in_invoice",
            "partner_id": partner.id,
            "invoice_date": invoice_date or False,
            "ref": invoice_id_str,
            "invoice_line_ids": [(0, 0, {
                "name": f"Invoice from {vendor_name}",
                "price_unit": invoice_total,
                "quantity": 1,
            })],
        }

        move = self.env["account.move"].create(move_vals)

        # Attach original document
        self.env["ir.attachment"].sudo().browse(attachment_id).write({
            "res_model": "account.move",
            "res_id": move.id,
        })

        return {
            "status": "success",
            "move_id": move.id,
            "vendor": vendor_name,
            "total": invoice_total,
            "confidence": confidence,
            "needs_review": confidence < 0.85,
        }
