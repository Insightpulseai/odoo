# -*- coding: utf-8 -*-
"""
IDP Models Package.

Contains core models for document processing:
- idp_document: Main document records
- idp_document_ocr: OCR results
- idp_extraction: LLM extraction results
- idp_model_version: Versioned prompt/model configurations
- idp_review: Human review corrections
- res_config_settings: Configuration settings
"""
from . import idp_document
from . import idp_document_ocr
from . import idp_extraction
from . import idp_model_version
from . import idp_review
from . import idp_validation_rule
from . import res_config_settings
