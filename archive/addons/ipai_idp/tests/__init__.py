# -*- coding: utf-8 -*-
"""
IDP Tests Package.

Contains unit tests and integration tests for IDP module:
- test_parsers: Text parsing utility tests
- test_validation: Validation rule tests
- test_extraction: LLM extraction tests
- test_health: Health endpoint tests
- test_security: Access rights and record rules tests
- test_document_flow: State transition tests
- test_http_endpoints: HTTP controller tests
"""
from . import (
    test_document_flow,
    test_extraction,
    test_health,
    test_http_endpoints,
    test_parsers,
    test_security,
    test_validation,
)
