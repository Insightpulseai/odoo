# -*- coding: utf-8 -*-
"""
IDP OCR Service.

Handles OCR processing for documents using configurable OCR engines.
"""
import logging
import time

import requests
from odoo.exceptions import UserError

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IdpServiceOcr(models.AbstractModel):
    """
    IDP OCR Processing Service.

    Provides OCR processing for documents using configurable backends.
    Supports multiple OCR engines with fallback capability.

    Attributes:
        _name: idp.service.ocr
        _description: IDP OCR Service
    """

    _name = "idp.service.ocr"
    _description = "IDP OCR Service"

    @api.model
    def process_document(self, document):
        """
        Process a document through OCR.

        Args:
            document: idp.document record

        Returns:
            idp.document.ocr record with OCR results
        """
        params = self.env["ir.config_parameter"].sudo()
        ocr_engine = params.get_param("ipai_idp.ocr_engine", "insightpulse")
        api_url = params.get_param("ipai_idp.ocr_api_url")
        api_key = params.get_param("ipai_idp.ocr_api_key")

        if not api_url:
            raise UserError("IDP OCR API URL is not configured.")

        start_time = time.time()
        ocr_result = None

        try:
            # Get file content
            if document.attachment_id:
                file_content = document.attachment_id.raw
                filename = document.attachment_id.name
                mimetype = document.attachment_id.mimetype
            else:
                raise UserError("No attachment found for document.")

            # Call OCR API
            files = {"file": (filename, file_content, mimetype)}
            headers = {}
            if api_key:
                headers["X-API-Key"] = api_key

            response = requests.post(
                api_url,
                files=files,
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            processing_time = int((time.time() - start_time) * 1000)

            # Create OCR result record
            ocr_result = self.env["idp.document.ocr"].create(
                {
                    "document_id": document.id,
                    "raw_text": data.get("text") or data.get("raw_text", ""),
                    "ocr_engine": ocr_engine,
                    "engine_version": data.get("version"),
                    "confidence": data.get("confidence", 0.0),
                    "bounding_boxes": str(data.get("boxes", [])),
                    "processing_time_ms": processing_time,
                    "pages_processed": data.get("pages", 1),
                    "status": "success",
                }
            )

            # Update document classification if provided
            if data.get("doc_type"):
                document.write(
                    {
                        "doc_type": data.get("doc_type"),
                        "doc_type_confidence": data.get("doc_type_confidence", 0.0),
                    }
                )

            _logger.info(
                "OCR completed for document %s: %d chars in %dms",
                document.id,
                len(data.get("text", "")),
                processing_time,
            )

        except requests.RequestException as e:
            processing_time = int((time.time() - start_time) * 1000)
            _logger.exception("OCR API error for document %s", document.id)

            # Create failed OCR record
            ocr_result = self.env["idp.document.ocr"].create(
                {
                    "document_id": document.id,
                    "ocr_engine": ocr_engine,
                    "processing_time_ms": processing_time,
                    "status": "failed",
                    "error_message": str(e),
                }
            )
            raise UserError(f"OCR processing failed: {str(e)}")

        return ocr_result

    @api.model
    def process_text_directly(self, text, document=None):
        """
        Create an OCR result from provided text (skip actual OCR).

        Useful for testing or when text is already available.

        Args:
            text: The raw text
            document: Optional idp.document record to link

        Returns:
            idp.document.ocr record
        """
        return self.env["idp.document.ocr"].create(
            {
                "document_id": document.id if document else False,
                "raw_text": text,
                "ocr_engine": "other",
                "confidence": 1.0,
                "status": "success",
            }
        )
