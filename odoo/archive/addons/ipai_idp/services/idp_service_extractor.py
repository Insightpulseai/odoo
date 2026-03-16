# -*- coding: utf-8 -*-
"""
IDP LLM Extractor Service.

Handles LLM-based extraction from OCR text using versioned prompts.
"""
import json
import logging
import time

import requests
from odoo.exceptions import UserError

from odoo import api, models

_logger = logging.getLogger(__name__)


class IdpServiceExtractor(models.AbstractModel):
    """
    IDP LLM Extraction Service.

    Uses configured LLM backend to extract structured data from OCR text.
    Supports versioned prompts and schemas for reproducibility.

    Attributes:
        _name: idp.service.extractor
        _description: IDP LLM Extractor Service
    """

    _name = "idp.service.extractor"
    _description = "IDP LLM Extractor Service"

    @api.model
    def extract(self, document, ocr_result, model_version=None):
        """
        Extract structured data from OCR text using LLM.

        Args:
            document: idp.document record
            ocr_result: idp.document.ocr record with OCR text
            model_version: Optional specific model version to use

        Returns:
            idp.extraction record with extraction results
        """
        # Get model version
        if not model_version:
            model_version = self.env["idp.model.version"].get_default_version(
                document.doc_type or "all"
            )

        if not model_version:
            raise UserError("No active model version found for extraction.")

        params = self.env["ir.config_parameter"].sudo()
        llm_api_url = params.get_param("ipai_idp.llm_api_url")
        llm_api_key = params.get_param("ipai_idp.llm_api_key")

        if not llm_api_url:
            raise UserError("LLM API URL is not configured.")

        start_time = time.time()

        try:
            # Prepare prompts
            system_prompt = model_version.system_prompt
            user_prompt = model_version.render_prompt(ocr_result.raw_text)

            # Make LLM API call
            response = self._call_llm_api(
                llm_api_url,
                llm_api_key,
                model_version.llm_model,
                system_prompt,
                user_prompt,
                model_version.temperature,
                model_version.max_tokens,
            )

            processing_time = int((time.time() - start_time) * 1000)

            # Parse LLM response
            llm_data = self._parse_llm_response(response)

            # Create extraction record
            extraction = self.env["idp.extraction"].create(
                {
                    "document_id": document.id,
                    "ocr_id": ocr_result.id,
                    "model_version_id": model_version.id,
                    "extracted_json": json.dumps(
                        llm_data.get("extracted_data", {}), indent=2
                    ),
                    "raw_llm_response": response.get("raw_response", ""),
                    "confidence": llm_data.get("confidence", 0.0),
                    "processing_time_ms": processing_time,
                    "llm_model": model_version.llm_model,
                    "token_count": response.get("token_count", 0),
                }
            )

            # Update document type if extracted
            if llm_data.get("doc_type") and document.doc_type == "unknown":
                document.write({"doc_type": llm_data.get("doc_type")})

            _logger.info(
                "Extraction completed for document %s with confidence %.2f in %dms",
                document.id,
                llm_data.get("confidence", 0.0),
                processing_time,
            )

            return extraction

        except Exception as e:
            _logger.exception("LLM extraction error for document %s", document.id)
            raise UserError(f"LLM extraction failed: {str(e)}")

    @api.model
    def _call_llm_api(
        self,
        api_url,
        api_key,
        model,
        system_prompt,
        user_prompt,
        temperature,
        max_tokens,
    ):
        """
        Call the LLM API.

        Supports Claude (Anthropic) and OpenAI-compatible APIs.

        Args:
            api_url: API endpoint URL
            api_key: API key
            model: Model name
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Temperature setting
            max_tokens: Max tokens for response

        Returns:
            dict with response content and metadata
        """
        headers = {
            "Content-Type": "application/json",
        }

        # Determine API type based on URL or model
        is_anthropic = "anthropic" in api_url.lower() or model.startswith("claude")

        if is_anthropic:
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            }
        else:
            # OpenAI-compatible format
            headers["Authorization"] = f"Bearer {api_key}"
            payload = {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }

        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        # Extract content based on API type
        if is_anthropic:
            content = data.get("content", [{}])[0].get("text", "")
            token_count = data.get("usage", {}).get("input_tokens", 0) + data.get(
                "usage", {}
            ).get("output_tokens", 0)
        else:
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            token_count = data.get("usage", {}).get("total_tokens", 0)

        return {
            "content": content,
            "raw_response": json.dumps(data),
            "token_count": token_count,
        }

    @api.model
    def _parse_llm_response(self, response):
        """
        Parse LLM response content into structured data.

        Args:
            response: dict with 'content' key containing LLM output

        Returns:
            dict with parsed data
        """
        content = response.get("content", "")

        # Try to extract JSON from response
        try:
            # Look for JSON block in response
            if "```json" in content:
                json_start = content.index("```json") + 7
                json_end = content.index("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.index("```") + 3
                json_end = content.index("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # Try parsing entire content as JSON
                json_str = content.strip()

            data = json.loads(json_str)

            # Normalize response format
            if "extracted_data" not in data:
                # Assume entire response is the extracted data
                data = {
                    "doc_type": data.get("doc_type", "unknown"),
                    "extracted_data": data,
                    "confidence": data.get("confidence", 0.5),
                }

            return data

        except (json.JSONDecodeError, ValueError) as e:
            _logger.warning("Failed to parse LLM response as JSON: %s", e)
            return {
                "doc_type": "unknown",
                "extracted_data": {},
                "confidence": 0.0,
                "parse_error": str(e),
            }

    @api.model
    def extract_preview(self, ocr_text, doc_type="invoice", model_version=None):
        """
        Preview extraction without creating records.

        Useful for testing and API endpoints.

        Args:
            ocr_text: Raw OCR text
            doc_type: Document type
            model_version: Optional specific version

        Returns:
            dict with extraction results
        """
        if not model_version:
            model_version = self.env["idp.model.version"].get_default_version(doc_type)

        if not model_version:
            return {
                "error": "No active model version found",
                "doc_type": doc_type,
                "extracted_data": {},
                "confidence": 0.0,
            }

        params = self.env["ir.config_parameter"].sudo()
        llm_api_url = params.get_param("ipai_idp.llm_api_url")
        llm_api_key = params.get_param("ipai_idp.llm_api_key")

        if not llm_api_url:
            return {
                "error": "LLM API URL not configured",
                "doc_type": doc_type,
                "extracted_data": {},
                "confidence": 0.0,
            }

        start_time = time.time()

        try:
            system_prompt = model_version.system_prompt
            user_prompt = model_version.render_prompt(ocr_text)

            response = self._call_llm_api(
                llm_api_url,
                llm_api_key,
                model_version.llm_model,
                system_prompt,
                user_prompt,
                model_version.temperature,
                model_version.max_tokens,
            )

            processing_time = int((time.time() - start_time) * 1000)
            llm_data = self._parse_llm_response(response)

            return {
                "doc_type": llm_data.get("doc_type", doc_type),
                "extracted_data": llm_data.get("extracted_data", {}),
                "confidence": llm_data.get("confidence", 0.0),
                "processing_time_ms": processing_time,
                "model_version": model_version.name,
            }

        except Exception as e:
            _logger.exception("Preview extraction failed")
            return {
                "error": str(e),
                "doc_type": doc_type,
                "extracted_data": {},
                "confidence": 0.0,
            }

    @api.model
    def call_llm_raw(
        self,
        prompt,
        system_prompt="",
        model="claude-3-sonnet",
        temperature=0.0,
        max_tokens=4096,
    ):
        """
        Call LLM and return raw response text.

        Used by ADE LLM gateway for flexible prompt execution.

        Args:
            prompt: User prompt text
            system_prompt: Optional system prompt
            model: LLM model identifier
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            str: Raw LLM response content

        Raises:
            UserError: If LLM API is not configured or call fails
        """
        params = self.env["ir.config_parameter"].sudo()
        llm_api_url = params.get_param("ipai_idp.llm_api_url")
        llm_api_key = params.get_param("ipai_idp.llm_api_key")

        if not llm_api_url:
            raise UserError("LLM API URL is not configured.")

        try:
            response = self._call_llm_api(
                llm_api_url,
                llm_api_key,
                model,
                system_prompt or "",
                prompt,
                temperature,
                max_tokens,
            )
            return response.get("content", "")
        except Exception as e:
            _logger.exception("Raw LLM call failed")
            raise UserError(f"LLM call failed: {str(e)}")
