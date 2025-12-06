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
from . import test_parsers
from . import test_validation
from . import test_extraction
from . import test_health
from . import test_security
from . import test_document_flow
from . import test_http_endpoints
