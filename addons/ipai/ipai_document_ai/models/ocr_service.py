import base64
import logging
import os
import time

import requests

from odoo import api, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiOcrService(models.AbstractModel):
    """OCR Service interface for document extraction."""

    _name = "ipai.ocr.service"
    _description = "IPAI OCR Service"

    @api.model
    def _get_config(self):
        """Get OCR service configuration from environment/params."""
        ICP = self.env["ir.config_parameter"].sudo()

        return {
            "base_url": os.getenv("OCR_BASE_URL")
            or ICP.get_param("ipai_document_ai.ocr_base_url", "http://ocr:8000"),
            "timeout": int(
                os.getenv("OCR_TIMEOUT_SECONDS")
                or ICP.get_param("ipai_document_ai.ocr_timeout", "60")
            ),
            "max_mb": int(
                os.getenv("OCR_MAX_MB")
                or ICP.get_param("ipai_document_ai.ocr_max_mb", "25")
            ),
            "retry_attempts": int(
                os.getenv("OCR_RETRY_ATTEMPTS")
                or ICP.get_param("ipai_document_ai.ocr_retry_attempts", "3")
            ),
            "retry_delay": int(
                os.getenv("OCR_RETRY_DELAY_SECONDS")
                or ICP.get_param("ipai_document_ai.ocr_retry_delay", "5")
            ),
        }

    @api.model
    def check_health(self):
        """Check OCR service health."""
        config = self._get_config()
        url = f"{config['base_url']}/health"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _logger.error(f"OCR health check failed: {e}")
            return {"status": "error", "message": str(e)}

    @api.model
    def extract_document(self, file_content_b64, filename, options=None):
        """
        Send document to OCR service for extraction.

        Args:
            file_content_b64: Base64 encoded file content
            filename: Original filename
            options: Optional extraction options dict

        Returns:
            dict: Extraction result with text, fields, confidence
        """
        config = self._get_config()

        # Decode base64 content
        try:
            file_content = base64.b64decode(file_content_b64)
        except Exception as e:
            raise UserError(_("Invalid file content: %s") % str(e))

        # Check file size
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > config["max_mb"]:
            raise UserError(
                _("File too large. Maximum size is %d MB.") % config["max_mb"]
            )

        url = f"{config['base_url']}/v1/ocr/extract"

        # Prepare multipart form data
        files = {"file": (filename, file_content)}
        data = {}
        if options:
            import json

            data["options"] = json.dumps(options)

        # Retry logic
        last_error = None
        for attempt in range(config["retry_attempts"]):
            try:
                _logger.info(
                    f"OCR extraction attempt {attempt + 1}/{config['retry_attempts']} "
                    f"for {filename}"
                )

                response = requests.post(
                    url,
                    files=files,
                    data=data,
                    timeout=config["timeout"],
                )
                response.raise_for_status()

                result = response.json()
                _logger.info(f"OCR extraction successful for {filename}")
                return result

            except requests.Timeout:
                last_error = (
                    _("OCR service timeout after %d seconds") % config["timeout"]
                )
                _logger.warning(f"OCR timeout on attempt {attempt + 1}: {last_error}")

            except requests.ConnectionError as e:
                last_error = _("Cannot connect to OCR service: %s") % str(e)
                _logger.warning(
                    f"OCR connection error on attempt {attempt + 1}: {last_error}"
                )

            except requests.HTTPError as e:
                # Don't retry on client errors (4xx)
                if e.response is not None and 400 <= e.response.status_code < 500:
                    raise UserError(_("OCR service rejected the request: %s") % str(e))
                last_error = _("OCR service error: %s") % str(e)
                _logger.warning(
                    f"OCR HTTP error on attempt {attempt + 1}: {last_error}"
                )

            except Exception as e:
                last_error = _("Unexpected OCR error: %s") % str(e)
                _logger.error(f"OCR unexpected error on attempt {attempt + 1}: {e}")

            # Wait before retry (except on last attempt)
            if attempt < config["retry_attempts"] - 1:
                delay = config["retry_delay"] * (attempt + 1)  # Exponential backoff
                _logger.info(f"Waiting {delay}s before retry...")
                time.sleep(delay)

        # All retries exhausted
        raise UserError(
            _("OCR extraction failed after %d attempts. Last error: %s")
            % (config["retry_attempts"], last_error)
        )

    @api.model
    def extract_document_async(self, file_content_b64, filename, options=None):
        """
        Send document to OCR service for async extraction.

        Args:
            file_content_b64: Base64 encoded file content
            filename: Original filename
            options: Optional extraction options dict

        Returns:
            str: Job ID for polling
        """
        config = self._get_config()

        # Decode base64 content
        try:
            file_content = base64.b64decode(file_content_b64)
        except Exception as e:
            raise UserError(_("Invalid file content: %s") % str(e))

        url = f"{config['base_url']}/v1/ocr/extract-async"

        files = {"file": (filename, file_content)}
        data = {}
        if options:
            import json

            data["options"] = json.dumps(options)

        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                timeout=30,  # Short timeout for job submission
            )
            response.raise_for_status()

            result = response.json()
            return result.get("job_id")

        except requests.RequestException as e:
            raise UserError(_("Failed to submit OCR job: %s") % str(e))

    @api.model
    def get_job_status(self, job_id):
        """
        Get status of async OCR job.

        Args:
            job_id: OCR job ID

        Returns:
            dict: Job status and result (if complete)
        """
        config = self._get_config()
        url = f"{config['base_url']}/v1/ocr/jobs/{job_id}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise UserError(_("Failed to get OCR job status: %s") % str(e))
