# -*- coding: utf-8 -*-
"""
IDP Validation Service.

Runs validation rules against extracted data.
"""
import json
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IdpServiceValidator(models.AbstractModel):
    """
    IDP Validation Service.

    Applies validation rules to extraction results.
    Supports error, warning, and info severity levels.

    Attributes:
        _name: idp.service.validator
        _description: IDP Validation Service
    """

    _name = "idp.service.validator"
    _description = "IDP Validation Service"

    @api.model
    def validate(self, extraction):
        """
        Validate an extraction against all applicable rules.

        Args:
            extraction: idp.extraction record

        Returns:
            dict: {
                'status': 'pass'|'fail'|'warning',
                'errors': list of error dicts,
                'warnings': list of warning dicts,
                'info': list of info dicts
            }
        """
        doc_type = extraction.doc_type or "all"
        rules = self.env["idp.validation.rule"].get_rules_for_doc_type(doc_type)

        # Parse extracted data
        data = extraction.get_extracted_data()

        errors = []
        warnings = []
        info = []

        for rule in rules:
            result = rule.validate(data)

            if not result["passed"]:
                entry = {
                    "rule": result.get("rule_name", rule.name),
                    "message": result.get("message", "Validation failed"),
                    "severity": result.get("severity", "error"),
                }

                if result["severity"] == "error":
                    errors.append(entry)
                elif result["severity"] == "warning":
                    warnings.append(entry)
                else:
                    info.append(entry)

        # Determine overall status
        if errors:
            status = "fail"
        elif warnings:
            status = "warning"
        else:
            status = "pass"

        result = {
            "status": status,
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "rules_applied": len(rules),
        }

        # Update extraction record
        extraction.write(
            {
                "validation_status": status,
                "validation_errors": json.dumps(errors + warnings),
            }
        )

        _logger.info(
            "Validation for extraction %s: %s (%d errors, %d warnings)",
            extraction.id,
            status,
            len(errors),
            len(warnings),
        )

        return result

    @api.model
    def validate_data(self, data, doc_type="all"):
        """
        Validate raw data dict without an extraction record.

        Useful for testing and previews.

        Args:
            data: dict of extracted data
            doc_type: Document type for rule selection

        Returns:
            dict with validation results
        """
        rules = self.env["idp.validation.rule"].get_rules_for_doc_type(doc_type)

        errors = []
        warnings = []
        info = []

        for rule in rules:
            result = rule.validate(data)

            if not result["passed"]:
                entry = {
                    "rule": result.get("rule_name", rule.name),
                    "message": result.get("message", "Validation failed"),
                    "severity": result.get("severity", "error"),
                }

                if result["severity"] == "error":
                    errors.append(entry)
                elif result["severity"] == "warning":
                    warnings.append(entry)
                else:
                    info.append(entry)

        if errors:
            status = "fail"
        elif warnings:
            status = "warning"
        else:
            status = "pass"

        return {
            "status": status,
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "rules_applied": len(rules),
        }

    @api.model
    def get_auto_approval_recommendation(self, extraction):
        """
        Determine if extraction should be auto-approved.

        Args:
            extraction: idp.extraction record

        Returns:
            dict: {
                'should_approve': bool,
                'reason': str,
                'confidence': float
            }
        """
        # Get thresholds from config
        params = self.env["ir.config_parameter"].sudo()
        min_confidence = float(
            params.get_param("ipai_idp.auto_approve_confidence", "0.90")
        )

        # Run validation if not already done
        if extraction.validation_status == "pending":
            self.validate(extraction)
            extraction.refresh()

        confidence = extraction.confidence or 0.0
        validation_status = extraction.validation_status

        # Decision logic
        if validation_status == "fail":
            return {
                "should_approve": False,
                "reason": "Validation errors present",
                "confidence": confidence,
            }

        if confidence < min_confidence:
            return {
                "should_approve": False,
                "reason": f"Confidence {confidence:.2f} below threshold {min_confidence}",
                "confidence": confidence,
            }

        if validation_status == "warning":
            # Could be approved but flagged
            return {
                "should_approve": True,
                "reason": "Approved with warnings",
                "confidence": confidence,
                "has_warnings": True,
            }

        return {
            "should_approve": True,
            "reason": "All criteria met",
            "confidence": confidence,
        }
