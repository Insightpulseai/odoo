# -*- coding: utf-8 -*-
"""
IDP Controllers Package.

HTTP controllers for IDP endpoints:
- Health checks (livez, readyz, healthz)
- Extraction API
- Document processing API
"""
from . import health_controller, idp_api_controller
