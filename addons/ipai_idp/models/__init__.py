# -*- coding: utf-8 -*-
"""
IDP Models Package.

Contains core models for document processing:
- idp_document: Main document records
- idp_document_ocr: OCR results
- idp_extraction: LLM extraction results
- idp_model_version: Versioned prompt/model configurations
- idp_review: Human review corrections
- idp_validation_rule: Validation rules engine
- idp_llm_gateway: LLM prompt gateway for ADE
- idp_ade_trace: ADE execution audit trail
- res_config_settings: Configuration settings
"""
from . import (
    idp_ade_trace,
    idp_document,
    idp_document_ocr,
    idp_extraction,
    idp_llm_gateway,
    idp_model_version,
    idp_review,
    idp_validation_rule,
    res_config_settings,
)
