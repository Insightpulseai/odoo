# -*- coding: utf-8 -*-
import logging
import os

import odoo
from werkzeug.exceptions import Forbidden

_logger = logging.getLogger(__name__)

ALLOWED_FDID = os.environ.get("AZURE_FRONTDOOR_ID")

# Paths exempt from FDID validation — Azure Container Apps liveness/readiness
# probes hit these directly without routing through Front Door.
EXEMPT_PATHS = frozenset({"/web/health", "/"})

_original_call = odoo.http.Root.__call__


def _secure_wsgi_call(self, environ, start_response):
    path = environ.get("PATH_INFO", "")

    # 1. Bypass for ACA health probes (no FDID header on internal probes)
    if path in EXEMPT_PATHS:
        return _original_call(self, environ, start_response)

    # 2. Skip when env var unset (local dev, devcontainer)
    if not ALLOWED_FDID:
        return _original_call(self, environ, start_response)

    # 3. Validate X-Azure-FDID (Werkzeug: HTTP_ prefix, hyphens → underscores)
    request_fdid = environ.get("HTTP_X_AZURE_FDID")
    if request_fdid != ALLOWED_FDID:
        _logger.warning(
            "Blocked direct access to %s — invalid FDID: %s", path, request_fdid
        )
        response = Forbidden(
            "Direct access blocked. Route traffic via Azure Front Door."
        )
        return response(environ, start_response)

    # 4. Authorized — proceed
    return _original_call(self, environ, start_response)


odoo.http.Root.__call__ = _secure_wsgi_call
